from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import sympy as sp


@dataclass(frozen=True)
class DerivativeSummary:
    var: str
    mean: float
    median: float
    min: float
    max: float
    pct_positive: float
    pct_negative: float
    n: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "var": self.var,
            "mean": float(self.mean),
            "median": float(self.median),
            "min": float(self.min),
            "max": float(self.max),
            "pct_positive": float(self.pct_positive),
            "pct_negative": float(self.pct_negative),
            "n": int(self.n),
        }


def compute_partials(expr: sp.Expr, vars_: list[sp.Symbol], *, simplify: bool = False) -> dict[str, sp.Expr]:
    if simplify:
        return {v.name: sp.simplify(sp.diff(expr, v)) for v in vars_}
    return {v.name: sp.diff(expr, v) for v in vars_}


def summarize_derivative(values: np.ndarray, *, var: str) -> DerivativeSummary:
    v = np.asarray(values, dtype=np.float64)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return DerivativeSummary(var=var, mean=float("nan"), median=float("nan"), min=float("nan"), max=float("nan"), pct_positive=0.0, pct_negative=0.0, n=0)
    return DerivativeSummary(
        var=var,
        mean=float(np.mean(v)),
        median=float(np.median(v)),
        min=float(np.min(v)),
        max=float(np.max(v)),
        pct_positive=float(np.mean(v > 0.0)),
        pct_negative=float(np.mean(v < 0.0)),
        n=int(len(v)),
    )
