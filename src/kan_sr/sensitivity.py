from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import sympy as sp

BASELINE_MEAN = "mean"


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


def _mean_baseline(x_df, feature_cols: list[str]) -> dict[str, float]:
    return {col: float(np.asarray(x_df[col], dtype=np.float64).mean()) for col in feature_cols}


def feature_sensitivity(
    expr: sp.Expr,
    *,
    feature_cols: list[str],
    x_df,
    baseline: str = BASELINE_MEAN,
    input_clip: dict[str, tuple[float, float]] | None = None,
    safe_exp_clip: float | None = None,
) -> dict[str, dict[str, Any]]:
    if baseline != BASELINE_MEAN:
        raise ValueError(f"Unsupported baseline strategy: {baseline!r}")

    from src.kan_sr.symbolic import evaluate_symbolic_formula

    baseline_values = _mean_baseline(x_df, feature_cols)
    base_pred = evaluate_symbolic_formula(
        expr,
        feature_cols=feature_cols,
        x_df=x_df,
        input_clip=input_clip,
        safe_exp_clip=safe_exp_clip,
    )

    out: dict[str, dict[str, Any]] = {}
    for col in feature_cols:
        ablated_df = x_df.loc[:, feature_cols].copy()
        ablated_df[col] = baseline_values[col]
        ablated_pred = evaluate_symbolic_formula(
            expr,
            feature_cols=feature_cols,
            x_df=ablated_df,
            input_clip=input_clip,
            safe_exp_clip=safe_exp_clip,
        )
        delta = np.abs(np.asarray(base_pred, dtype=np.float64) - np.asarray(ablated_pred, dtype=np.float64))
        finite = delta[np.isfinite(delta)]
        if len(finite) == 0:
            raise ValueError(f"No finite sensitivity values for feature: {col}")
        out[col] = {
            "baseline_strategy": baseline,
            "baseline_value": float(baseline_values[col]),
            "mean_abs_delta": float(np.mean(finite)),
            "median_abs_delta": float(np.median(finite)),
            "max_abs_delta": float(np.max(finite)),
            "n": int(len(finite)),
        }
    return out
