from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainConfig:
    target_col: str = "load"
    grid_range_min: float = -5.0
    grid_range_max: float = 5.0
    scale_features: bool = False
    hidden_width: int = 10
    hidden_layers: tuple[int, ...] | None = None
    grid: int = 5
    k: int = 3
    seed: int = 1
    hidden_mult: int = 0
    mult_arity: int = 2

    warmup_steps: int = 200
    sparsify_steps: int = 800
    refine_steps: int = 200

    warmup_lr: float = 0.01
    sparsify_lr: float = 0.005
    refine_lr: float = 0.5

    sparsify_lamb: float = 0.01
    sparsify_lamb_l1: float = 1.0
    sparsify_lamb_entropy: float = 2.0
    sparsify_lamb_coef: float = 0.0
    sparsify_lamb_coefdiff: float = 0.0

    target_pruned_ratio: float = 0.8
    max_rmse_degrade_ratio: float = 1.1
    prune_candidate_profile: str = "default"

DEFAULT_PRUNE_CANDIDATES: tuple[dict[str, float], ...] = (
    {"node_th": 0.01, "edge_th": 0.002},
    {"node_th": 0.01, "edge_th": 0.005},
    {"node_th": 0.01, "edge_th": 0.01},
    {"node_th": 0.01, "edge_th": 0.03},
    {"node_th": 0.01, "edge_th": 0.05},
    {"node_th": 0.01, "edge_th": 0.08},
    {"node_th": 0.02, "edge_th": 0.10},
    {"node_th": 0.02, "edge_th": 0.15},
    {"node_th": 0.03, "edge_th": 0.20},
)

GENTLE_PRUNE_CANDIDATES: tuple[dict[str, float], ...] = (
    {"node_th": 0.0, "edge_th": 0.0},
    {"node_th": 0.0, "edge_th": 0.0001},
    {"node_th": 0.0, "edge_th": 0.0005},
    {"node_th": 0.0, "edge_th": 0.001},
    {"node_th": 0.005, "edge_th": 0.001},
    {"node_th": 0.005, "edge_th": 0.002},
    {"node_th": 0.01, "edge_th": 0.002},
    {"node_th": 0.01, "edge_th": 0.005},
    {"node_th": 0.02, "edge_th": 0.01},
)


def prune_candidates_for_profile(profile: str) -> tuple[dict[str, float], ...]:
    name = str(profile).strip().lower() or "default"
    if name == "default":
        return DEFAULT_PRUNE_CANDIDATES
    if name == "gentle":
        return GENTLE_PRUNE_CANDIDATES
    raise ValueError(f"Unsupported prune_candidate_profile: {profile!r}")
