from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedCmd:
    name: str
    run_id: str
    cmd: list[str]


@dataclass(frozen=True)
class SymbolicLibPlan:
    name: str
    lib: str
    r2_thresholds: tuple[float, ...]
    safe_exp_clip: float | None = None
    eval_clip_quantiles: tuple[float, float] | None = None

