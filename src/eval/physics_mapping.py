from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import sympy as sp

from src.kan_sr.sensitivity import compute_partials, summarize_derivative


@dataclass(frozen=True)
class PhysicsCheckResult:
    name: str
    passed: bool
    score: float
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": bool(self.passed), "score": float(self.score), "details": self.details}


def contains_integer_power(expr: sp.Expr, sym: sp.Symbol, power: int) -> bool:
    """
    Return True if `sym**power` (integer power) appears anywhere in `expr`.
    """
    if power == 1:
        return expr.has(sym)
    for node in sp.preorder_traversal(expr):
        if isinstance(node, sp.Pow):
            base, exp = node.args
            if base == sym and exp.is_integer and int(exp) == int(power):
                return True
    return False


def power_counts(expr: sp.Expr, sym: sp.Symbol, *, max_power: int = 6) -> dict[int, int]:
    """
    Count occurrences of `sym**k` for integer k in [2..max_power].
    """
    counts: dict[int, int] = {k: 0 for k in range(2, int(max_power) + 1)}
    for node in sp.preorder_traversal(expr):
        if isinstance(node, sp.Pow):
            base, exp = node.args
            if base == sym and exp.is_integer:
                k = int(exp)
                if 2 <= k <= max_power:
                    counts[k] += 1
    return {k: v for k, v in counts.items() if v > 0}


def derivative_summaries(
    expr: sp.Expr,
    *,
    feature_cols: list[str],
    x_df,
    var_names: list[str],
) -> dict[str, dict[str, Any]]:
    """
    Compute derivative summaries for selected variables on a DataFrame.

    Returns:
      {var_name: DerivativeSummary.as_dict()}
    """
    locals_map = {name: sp.Symbol(name) for name in feature_cols}
    vars_ = [locals_map[v] for v in var_names if v in locals_map]
    partials = compute_partials(expr, vars_)

    X = x_df[feature_cols].to_numpy(dtype=np.float64)
    args_arr = [X[:, i] for i in range(X.shape[1])]

    out: dict[str, dict[str, Any]] = {}
    for name, dexpr in partials.items():
        try:
            f = sp.lambdify(feature_cols, dexpr, modules="numpy")
            vals = np.asarray(f(*args_arr), dtype=np.float64).reshape(-1)
            out[name] = summarize_derivative(vals, var=name).as_dict()
        except Exception:  # noqa: BLE001 - robustness for complex formulas
            out[name] = summarize_derivative(np.asarray([], dtype=np.float64), var=name).as_dict()
    return out


def analyze_physics(
    expr: sp.Expr,
    *,
    feature_cols: list[str],
    x_df,
    target_col: str,
) -> dict[str, Any]:
    """
    Heuristic physics mapping + consistency scoring (Phase 7).

    This is intentionally lightweight and explainable; it does not claim
    scientific proof, but provides thesis-ready evidence and checks.
    """
    target = str(target_col)
    base_target = target[len("delta_") :] if target.startswith("delta_") else target
    locals_map = {name: sp.Symbol(name) for name in feature_cols}

    checks: list[PhysicsCheckResult] = []

    def _check(name: str, passed: bool, score: float, details: dict[str, Any]) -> None:
        checks.append(PhysicsCheckResult(name=name, passed=bool(passed), score=float(score), details=details))

    # Wind: look for v^3 and monotone increasing w.r.t wind speed.
    if base_target == "wind":
        vname = "wind_speed_10m_m_s"
        v3name = "wind_speed_10m_m_s_cubed"
        has_v3 = False
        power_detail: dict[str, Any] = {"var": vname, "power_counts": {}}
        if vname in locals_map:
            v = locals_map[vname]
            has_v3 = contains_integer_power(expr, v, 3)
            power_detail = {"var": vname, "power_counts": power_counts(expr, v)}
        if (not has_v3) and (v3name in locals_map):
            # If an engineered v^3 proxy exists and appears in the expression, treat as satisfying the cubic-term check.
            if bool(expr.has(locals_map[v3name])):
                has_v3 = True
                power_detail = {"var": v3name, "power_counts": {3: 1}}

        if vname in locals_map or v3name in locals_map:
            _check(
                name="wind_speed_cubic_term",
                passed=has_v3,
                score=1.0 if has_v3 else 0.0,
                details=power_detail,
            )

        # Monotonicity check (prefer raw wind speed if present; fallback to v^3 proxy).
        wind_var = vname if vname in locals_map else (v3name if v3name in locals_map else None)
        if wind_var is not None:
            summ = derivative_summaries(expr, feature_cols=feature_cols, x_df=x_df, var_names=[wind_var]).get(wind_var, {})
            pct_pos = float(summ.get("pct_positive", 0.0))
            _check(
                name="wind_speed_monotone_increasing",
                passed=pct_pos >= 0.7,
                score=min(1.0, pct_pos / 0.7) if np.isfinite(pct_pos) else 0.0,
                details={"var": wind_var, "derivative_summary": summ, "present_in_expr": bool(expr.has(locals_map[wind_var]))},
            )

    # Solar: irradiance should be non-decreasing; temperature often decreases efficiency.
    if base_target == "solar":
        gname = "ghi_w_m2"
        tname = "temp_2m_c"

        if gname in locals_map:
            summ = derivative_summaries(expr, feature_cols=feature_cols, x_df=x_df, var_names=[gname]).get(gname, {})
            pct_pos = float(summ.get("pct_positive", 0.0))
            _check(
                name="ghi_monotone_increasing",
                passed=pct_pos >= 0.7,
                score=min(1.0, pct_pos / 0.7) if np.isfinite(pct_pos) else 0.0,
                details={"var": gname, "derivative_summary": summ, "present_in_expr": bool(expr.has(locals_map[gname]))},
            )

        if tname in locals_map:
            summ = derivative_summaries(expr, feature_cols=feature_cols, x_df=x_df, var_names=[tname]).get(tname, {})
            pct_neg = float(summ.get("pct_negative", 0.0))
            _check(
                name="temp_efficiency_decreasing",
                passed=pct_neg >= 0.6,
                score=min(1.0, pct_neg / 0.6) if np.isfinite(pct_neg) else 0.0,
                details={"var": tname, "derivative_summary": summ, "present_in_expr": bool(expr.has(locals_map[tname]))},
            )

    # Load: temperature sensitivity should not be pathological; cyclic features matter.
    if base_target == "load":
        tname = "temp_2m_c"
        if tname in locals_map:
            summ = derivative_summaries(expr, feature_cols=feature_cols, x_df=x_df, var_names=[tname]).get(tname, {})
            # We don't assume a sign (heating vs cooling), but we expect sensitivity to exist.
            mean_abs = float(abs(summ.get("mean", 0.0))) if summ else 0.0
            _check(
                name="temp_sensitivity_present",
                passed=np.isfinite(mean_abs) and mean_abs > 0.0,
                score=1.0 if np.isfinite(mean_abs) and mean_abs > 0.0 else 0.0,
                details={"var": tname, "derivative_summary": summ},
            )

    # Net load: higher irradiance / higher wind should *reduce* net load (more RE generation).
    if base_target == "net_load":
        wind_vars = ["wind_speed_10m_m_s_cubed", "wind_speed_10m_m_s"]
        ghi_vars = ["ghi_day_w_m2", "ghi_w_m2"]

        def _best_present(candidates: list[str]) -> str | None:
            for v in candidates:
                if v in locals_map:
                    return v
            return None

        wv = _best_present(wind_vars)
        gv = _best_present(ghi_vars)

        if wv is not None:
            summ = derivative_summaries(expr, feature_cols=feature_cols, x_df=x_df, var_names=[wv]).get(wv, {})
            pct_neg = float(summ.get("pct_negative", 0.0))
            _check(
                name="wind_proxy_monotone_decreasing",
                passed=pct_neg >= 0.7,
                score=min(1.0, pct_neg / 0.7) if np.isfinite(pct_neg) else 0.0,
                details={"var": wv, "derivative_summary": summ, "present_in_expr": bool(expr.has(locals_map[wv]))},
            )

        if gv is not None:
            summ = derivative_summaries(expr, feature_cols=feature_cols, x_df=x_df, var_names=[gv]).get(gv, {})
            pct_neg = float(summ.get("pct_negative", 0.0))
            _check(
                name="ghi_proxy_monotone_decreasing",
                passed=pct_neg >= 0.7,
                score=min(1.0, pct_neg / 0.7) if np.isfinite(pct_neg) else 0.0,
                details={"var": gv, "derivative_summary": summ, "present_in_expr": bool(expr.has(locals_map[gv]))},
            )

    score = float(np.mean([c.score for c in checks])) if checks else float("nan")
    return {
        "target_col": target,
        "base_target_col": base_target,
        "n_checks": int(len(checks)),
        "score": score,
        "checks": [c.as_dict() for c in checks],
    }
