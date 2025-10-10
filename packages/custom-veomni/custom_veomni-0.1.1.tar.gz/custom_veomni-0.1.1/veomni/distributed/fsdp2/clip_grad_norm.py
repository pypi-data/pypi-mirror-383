import math
from typing import List

import torch
import torch.distributed as dist
from torch.distributed._tensor import DTensor

from ...utils.device import get_device_type
from ...utils.logging import get_logger
from ..parallel_state import get_parallel_state


logger = get_logger(__name__)


def clip_grad_norm(
    model, max_norm: float, norm_type: float = 2.0, error_if_nonfinite: bool = False, foreach: bool | None = None
) -> torch.Tensor:
    # EP-aware path (FSDP2 + EP): maintain mathematical parity with FSDP1 clipper
    if hasattr(model, "_ep_param_groups"):
        return ep_fsdp2_clip_grad_norm(
            model,
            max_norm,
            norm_type=norm_type,
            error_if_nonfinite=error_if_nonfinite,
            foreach=foreach,
        )

    # FSDP2 without EP: still need distributed reductions across the FSDP group
    ps = get_parallel_state()
    fsdp_group = ps.fsdp_group
    try:
        world_size = dist.get_world_size(fsdp_group) if fsdp_group is not None else 1
    except Exception:
        world_size = 1

    if world_size == 1:
        # Default path (single-rank)
        return torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm,
            norm_type=norm_type,
            error_if_nonfinite=error_if_nonfinite,
            foreach=foreach,
        )

    return _fsdp2_reduce_and_clip(
        params=[p for p in model.parameters() if p.grad is not None],
        max_norm=max_norm,
        norm_type=norm_type,
        foreach=foreach,
        error_if_nonfinite=error_if_nonfinite,
        reduce_groups=[("fsdp", fsdp_group)],
    )


@torch.no_grad()
def ep_fsdp2_clip_grad_norm(
    model, max_norm: float, norm_type: float = 2.0, error_if_nonfinite: bool = False, foreach: bool | None = None
) -> torch.Tensor:
    """
    EP-aware gradient clipping for composable FSDP2 with reductions mirroring FSDP1:

    - Compute local norms for non-EP and EP parameter groups separately.
    - For finite p: sum p-th powers across the appropriate groups, then take 1/p.
      • non-EP: all-reduce over FSDP group.
      • EP: all-reduce over EP-FSDP group, then over EP group.
    - For inf-norm: take elementwise MAX with the same reduction groups (MAX).
    - Use a single global clip coefficient for both groups.
    """

    ps = get_parallel_state()
    fsdp_group = ps.fsdp_group
    ep_group = ps.ep_group if ps.ep_enabled else None
    # For EP params sharded by FSDP2 along hidden dimension
    ep_fsdp_group = None
    if ps.ep_enabled and ps.ep_fsdp_device_mesh is not None:
        ep_fsdp_group = ps.ep_fsdp_device_mesh["ep_fsdp"].get_group()

    # Build param groups (filter out params without grads)
    ep_params: List[torch.nn.Parameter] = [p for p in model._ep_param_groups.get("ep", []) if p.grad is not None]
    non_ep_params: List[torch.nn.Parameter] = [
        p for p in model._ep_param_groups.get("non_ep", []) if p.grad is not None
    ]

    # Match FSDP1 gradient averaging for EP params by dividing grads by ep_size
    if ps.ep_enabled and ps.ep_size > 1 and ep_params:
        scale = 1.0 / float(ps.ep_size)
        for q in ep_params:
            if q.grad is not None:
                q.grad.detach().mul_(scale)

    # Compute and reduce non-EP
    non_ep_total = _fsdp2_reduce_group(
        params=non_ep_params,
        norm_type=norm_type,
        reduce_groups=[("fsdp", fsdp_group)],
    )

    # Compute and reduce EP: first across ep_fsdp, then across ep
    ep_total = _fsdp2_reduce_group(
        params=ep_params,
        norm_type=norm_type,
        reduce_groups=[("ep_fsdp", ep_fsdp_group), ("ep", ep_group)],
    )

    if math.isinf(norm_type):
        total_norm = torch.maximum(non_ep_total, ep_total)
    else:
        total_norm = (non_ep_total + ep_total) ** (1.0 / float(norm_type))

    # Apply the same clip coefficient to both groups
    torch.nn.utils.clip_grads_with_norm_(ep_params, max_norm, total_norm, foreach=foreach)
    torch.nn.utils.clip_grads_with_norm_(non_ep_params, max_norm, total_norm, foreach=foreach)

    return total_norm


def _local_pth_sum(params: List[torch.nn.Parameter], p: float) -> torch.Tensor:
    dev = None
    acc = None
    for q in params:
        g = q.grad
        if g is None:
            continue
        if isinstance(g, DTensor):
            g_local = g.to_local()
        else:
            g_local = g
        if dev is None:
            dev = g_local.device
            acc = torch.tensor(0.0, device=dev, dtype=torch.float32)
        # compute in FP32 for stability
        gn = torch.norm(g_local.detach().to(torch.float32), p=p)
        acc = acc + (gn**p)
    if acc is None:
        # no grads; choose a reasonable device
        dev = torch.device(get_device_type())
        acc = torch.tensor(0.0, device=dev, dtype=torch.float32)
    return acc


def _local_max(params: List[torch.nn.Parameter]) -> torch.Tensor:
    dev = None
    mx = None
    for q in params:
        g = q.grad
        if g is None:
            continue
        if isinstance(g, DTensor):
            g_local = g.to_local()
        else:
            g_local = g
        if dev is None:
            dev = g_local.device
            mx = torch.tensor(0.0, device=dev, dtype=torch.float32)
        gn = torch.max(torch.abs(g_local.detach().to(torch.float32)))
        mx = torch.maximum(mx, gn)
    if mx is None:
        dev = torch.device(get_device_type())
        mx = torch.tensor(0.0, device=dev, dtype=torch.float32)
    return mx


def _fsdp2_reduce_group(
    params: List[torch.nn.Parameter],
    norm_type: float,
    reduce_groups: List[tuple[str, dist.ProcessGroup | None]],
) -> torch.Tensor:
    """Compute local group statistic and reduce over provided groups.

    For finite p, returns the globally-reduced sum of p-th powers (not the final norm).
    For inf, returns the globally-reduced max.
    """
    if math.isinf(norm_type):
        val = _local_max(params)
        for _, group in reduce_groups:
            if group is not None:
                dist.all_reduce(val, op=dist.ReduceOp.MAX, group=group)
        return val
    else:
        p = float(norm_type)
        val = _local_pth_sum(params, p)
        for _, group in reduce_groups:
            if group is not None:
                dist.all_reduce(val, op=dist.ReduceOp.SUM, group=group)
        return val


def _fsdp2_reduce_and_clip(
    params: List[torch.nn.Parameter],
    max_norm: float,
    norm_type: float,
    foreach: bool | None,
    error_if_nonfinite: bool,
    reduce_groups: List[tuple[str, dist.ProcessGroup | None]],
) -> torch.Tensor:
    if math.isinf(norm_type):
        total_norm = _fsdp2_reduce_group(params, norm_type, reduce_groups)
    else:
        total_p = _fsdp2_reduce_group(params, norm_type, reduce_groups)
        total_norm = total_p ** (1.0 / float(norm_type))

    torch.nn.utils.clip_grads_with_norm_(params, max_norm, total_norm, foreach=foreach)
    return total_norm
