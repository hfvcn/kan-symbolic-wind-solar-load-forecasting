from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class EdgeSparsity:
    total_edges: int
    pruned_edges: int

    @property
    def pruned_ratio(self) -> float:
        if self.total_edges == 0:
            return 0.0
        return self.pruned_edges / self.total_edges

    def as_dict(self) -> dict[str, float | int]:
        return {
            "total_edges": int(self.total_edges),
            "pruned_edges": int(self.pruned_edges),
            "pruned_ratio": float(self.pruned_ratio),
        }


def compute_edge_sparsity_from_state_dict(state_dict: dict[str, torch.Tensor]) -> EdgeSparsity:
    """
    Compute edge sparsity from KAN state_dict masks.

    KAN stores edge masks in keys like:
        act_fun.<layer>.mask  (float tensor with 0/1)
    """
    total = 0
    pruned = 0
    for k, v in state_dict.items():
        if not k.startswith("act_fun.") or not k.endswith(".mask"):
            continue
        total += int(v.numel())
        pruned += int((v == 0).sum().item())
    return EdgeSparsity(total_edges=total, pruned_edges=pruned)


def compute_edge_sparsity(model: torch.nn.Module) -> EdgeSparsity:
    return compute_edge_sparsity_from_state_dict(model.state_dict())

