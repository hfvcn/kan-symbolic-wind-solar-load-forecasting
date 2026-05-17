from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.kan_sr.metrics import mae, r2, rmse

FORMULA_COMBINED_SYMPY = "formula_combined.sympy.txt"
FORMULA_COMBINED_TEX = "formula_combined.tex"
FORMULA_COMBINED_METRICS = "formula_combined_metrics.json"
FORMULA_EVAL_TEST = "formula_eval_test.json"
FORMULA_PREDICTIONS = "predictions_test_formula.parquet"


@dataclass(frozen=True)
class LoadedComponentRun:
    label: str
    run_dir: Path
    payload: dict[str, Any]
    target_col: str | None
    horizon_steps: int
    frame: pd.DataFrame


@dataclass(frozen=True)
class LoadedFormulaRun:
    component: LoadedComponentRun
    expr: Any
    metrics: dict[str, Any]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))


def infer_target_col(payload: dict[str, Any]) -> str | None:
    if payload.get("target_col"):
        return str(payload["target_col"])
    cfg = payload.get("cfg")
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg["target_col"])
    return None


def infer_horizon_steps(target_col: str | None) -> int:
    if not target_col or "_h" not in str(target_col):
        return 1
    try:
        return max(1, int(str(target_col).rsplit("_h", 1)[1]))
    except Exception:
        return 1


def pick_predictions_path(run_dir: Path) -> Path:
    artifacts = run_dir / "artifacts"
    for name in ("predictions_test_reconstructed.parquet", "predictions_test.parquet"):
        path = artifacts / name
        if path.exists():
            return path
    raise FileNotFoundError(f"predictions file not found under: {artifacts}")


def load_component_run(run_dir: Path, *, label: str) -> LoadedComponentRun:
    payload_path = run_dir / "payload.json"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found: {payload_path}")
    payload = read_json(payload_path)
    pred_df = pd.read_parquet(pick_predictions_path(run_dir))
    if "y_true" not in pred_df.columns or "y_pred" not in pred_df.columns:
        raise ValueError(f"Invalid predictions file for {run_dir.name}: missing y_true/y_pred")
    target_col = infer_target_col(payload)
    renamed = pred_df[["y_true", "y_pred"]].rename(columns={"y_true": f"{label}_true", "y_pred": f"{label}_pred"})
    return LoadedComponentRun(
        label=label,
        run_dir=run_dir,
        payload=payload,
        target_col=target_col,
        horizon_steps=infer_horizon_steps(target_col),
        frame=renamed,
    )


def load_formula_run(run_dir: Path, *, label: str) -> LoadedFormulaRun:
    sp = _require_sympy()
    component = load_component_run(run_dir, label=label)
    artifacts = run_dir / "artifacts"
    formula_path = artifacts / "formula_reconstructed.sympy.txt"
    if not formula_path.exists():
        raise FileNotFoundError(f"formula_reconstructed.sympy.txt not found: {formula_path}")
    metrics_path = artifacts / "formula_metrics.json"
    metrics = read_json(metrics_path) if metrics_path.exists() else {}
    return LoadedFormulaRun(component=component, expr=sp.sympify(formula_path.read_text().strip()), metrics=metrics)


def require_complete_formula_runs(formula_runs: dict[str, str]) -> dict[str, Path] | None:
    cleaned = {key: str(value).strip() for key, value in formula_runs.items() if str(value).strip()}
    if not cleaned:
        return None
    missing = [key for key in ("load", "wind", "solar") if key not in cleaned]
    if missing:
        raise ValueError(f"Incomplete formula run set; missing: {', '.join(missing)}")
    return {key: Path(cleaned[key]) for key in ("load", "wind", "solar")}


def _require_sympy():
    try:
        import sympy as sp
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("sympy is required when combining formula artifacts") from exc
    return sp


def _compute_formula_complexity(expr: Any) -> dict[str, Any]:
    sp = _require_sympy()

    def depth(node: Any) -> int:
        if not getattr(node, "args", None):
            return 1
        return 1 + max(depth(child) for child in node.args)

    nodes = list(sp.preorder_traversal(expr))
    func_nodes = [node for node in nodes if isinstance(node, sp.Function)]
    sym_nodes = [node for node in nodes if isinstance(node, sp.Symbol)]
    num_nodes = [node for node in nodes if isinstance(node, sp.Number)]
    return {
        "node_count": int(len(nodes)),
        "function_count": int(len(func_nodes)),
        "symbol_count": int(len(set(sym_nodes))),
        "number_count": int(len(num_nodes)),
        "tree_depth": int(depth(expr)),
    }


def ensure_same_horizon(components: list[LoadedComponentRun]) -> int:
    horizons = {comp.horizon_steps for comp in components}
    if len(horizons) != 1:
        detail = ", ".join(f"{comp.label}={comp.target_col!r}" for comp in components)
        raise ValueError(f"Horizon mismatch across component runs: {detail}")
    return next(iter(horizons))


def join_component_frames(components: list[LoadedComponentRun]) -> pd.DataFrame:
    joined = components[0].frame.copy()
    for component in components[1:]:
        joined = joined.join(component.frame, how="inner")
    joined = joined.dropna(subset=list(joined.columns))
    if joined.empty:
        raise ValueError("No overlapping finite rows between component runs")
    return joined


def build_net_load_frame(joined: pd.DataFrame) -> pd.DataFrame:
    y_true = joined["load_true"] - joined["wind_true"] - joined["solar_true"]
    y_pred = joined["load_pred"] - joined["wind_pred"] - joined["solar_pred"]
    return pd.DataFrame({"y_true": y_true, "y_pred": y_pred, "residual": y_pred - y_true}, index=joined.index)


def compute_eval_metrics(pred_df: pd.DataFrame) -> dict[str, Any]:
    y_true = pred_df["y_true"].to_numpy(dtype=np.float64)
    y_pred = pred_df["y_pred"].to_numpy(dtype=np.float64)
    finite = np.isfinite(y_true) & np.isfinite(y_pred)
    if int(np.sum(finite)) == 0:
        raise ValueError("No finite rows available for evaluation")
    yt = y_true[finite]
    yp = y_pred[finite]
    return {
        "rmse": float(rmse(yt, yp)),
        "mae": float(mae(yt, yp)),
        "r2": float(r2(yt, yp)),
        "n": int(len(yt)),
    }


def compute_persistence_metrics(pred_df: pd.DataFrame, *, horizon_steps: int) -> dict[str, float | None]:
    if horizon_steps < 1:
        raise ValueError(f"horizon_steps must be >= 1, got {horizon_steps}")
    df = pred_df[["y_true", "y_pred"]].copy()
    df["y_base"] = df["y_true"].shift(int(horizon_steps))
    y_true = df["y_true"].to_numpy(dtype=np.float64)
    y_pred = df["y_pred"].to_numpy(dtype=np.float64)
    y_base = df["y_base"].to_numpy(dtype=np.float64)
    finite = np.isfinite(y_true) & np.isfinite(y_pred) & np.isfinite(y_base)
    if int(np.sum(finite)) == 0:
        return {"rmse_persistence": None, "skill_score": None}
    yt = y_true[finite]
    yp = y_pred[finite]
    yb = y_base[finite]
    persistence_rmse = float(rmse(yt, yb))
    skill_score = None
    if persistence_rmse > 0 and np.isfinite(persistence_rmse):
        skill_score = float(1.0 - (float(rmse(yt, yp)) / persistence_rmse))
    return {"rmse_persistence": persistence_rmse, "skill_score": skill_score}


def combine_prediction_components(*, load: LoadedComponentRun, wind: LoadedComponentRun, solar: LoadedComponentRun) -> tuple[pd.DataFrame, dict[str, Any], int]:
    horizon = ensure_same_horizon([load, wind, solar])
    pred_df = build_net_load_frame(join_component_frames([load, wind, solar]))
    return pred_df, compute_eval_metrics(pred_df), horizon


def combine_formula_components(*, load: LoadedFormulaRun, wind: LoadedFormulaRun, solar: LoadedFormulaRun) -> dict[str, Any]:
    sp = _require_sympy()
    pred_df, metrics, horizon = combine_prediction_components(
        load=load.component,
        wind=wind.component,
        solar=solar.component,
    )
    expr = load.expr - wind.expr - solar.expr
    return {
        "expr": expr,
        "tex": sp.latex(expr),
        "pred_df": pred_df,
        "metrics": metrics,
        "complexity": _compute_formula_complexity(expr),
        "horizon_steps": horizon,
        "targets": {item.component.label: item.component.target_col for item in (load, wind, solar)},
    }


def build_formula_comparison_rows(run_dirs: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        payload_path = run_dir / "payload.json"
        artifacts = run_dir / "artifacts"
        if not payload_path.exists() or not (artifacts / FORMULA_EVAL_TEST).exists():
            continue
        payload = read_json(payload_path)
        if str(payload.get("phase")) != "05-structured-combination":
            continue
        pred_path = artifacts / FORMULA_PREDICTIONS
        if not pred_path.exists():
            raise FileNotFoundError(f"Missing formula predictions for combo run: {pred_path}")
        pred_df = pd.read_parquet(pred_path)
        target_col = infer_target_col(payload)
        skill = compute_persistence_metrics(pred_df, horizon_steps=infer_horizon_steps(target_col))
        eval_metrics = read_json(artifacts / FORMULA_EVAL_TEST)
        complexity_payload = read_json(artifacts / FORMULA_COMBINED_METRICS) if (artifacts / FORMULA_COMBINED_METRICS).exists() else {}
        rows.append(
            {
                "run_id": f"{payload.get('run_id', run_dir.name)}__formula",
                "phase": "05-structured-combination",
                "kind": "s3_composite_formula",
                "target_col": target_col,
                "rmse": float(eval_metrics["rmse"]),
                "mae": float(eval_metrics["mae"]),
                "r2": float(eval_metrics["r2"]),
                "rmse_persistence": skill["rmse_persistence"],
                "skill_score": skill["skill_score"],
                "complexity": complexity_payload.get("node_count"),
                "complexity_name": "sympy_node_count" if complexity_payload.get("node_count") is not None else None,
                "physical_score": None,
                "param_count": None,
                "compute_time_s": None,
                "path": str(run_dir),
            }
        )
    return rows
