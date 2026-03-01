from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    phase: str
    kind: str
    target_col: str | None
    rmse: float | None
    mae: float | None
    r2: float | None
    rmse_persistence: float | None
    skill_score: float | None
    complexity: float | None
    complexity_name: str | None
    physical_score: float | None
    param_count: int | None
    compute_time_s: float | None
    path: Path

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "phase": self.phase,
            "kind": self.kind,
            "target_col": self.target_col,
            "rmse": self.rmse,
            "mae": self.mae,
            "r2": self.r2,
            "rmse_persistence": self.rmse_persistence,
            "skill_score": self.skill_score,
            "complexity": self.complexity,
            "complexity_name": self.complexity_name,
            "physical_score": self.physical_score,
            "param_count": self.param_count,
            "compute_time_s": self.compute_time_s,
            "path": str(self.path),
        }


def _infer_target_col(payload: dict[str, Any]) -> str | None:
    if payload.get("target_col"):
        return str(payload.get("target_col"))
    cfg = payload.get("cfg")
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg.get("target_col"))
    return None


def _pick_predictions_path(artifacts_dir: Path) -> Path | None:
    for name in ["predictions_test_reconstructed.parquet", "predictions_test.parquet"]:
        p = artifacts_dir / name
        if p.exists():
            return p
    return None


_HORIZON_RE = re.compile(r"_h(\d+)$")


def _infer_horizon_steps(target_col: str | None) -> int:
    if not target_col:
        return 1
    m = _HORIZON_RE.search(str(target_col))
    if not m:
        return 1
    h = int(m.group(1))
    return h if h >= 1 else 1


def _metrics_from_predictions(pred_df: pd.DataFrame, *, horizon_steps: int) -> dict[str, float] | None:
    import numpy as np

    from src.kan_sr.metrics import mae as mae_fn
    from src.kan_sr.metrics import r2 as r2_fn
    from src.kan_sr.metrics import rmse as rmse_fn

    if "y_true" not in pred_df.columns or "y_pred" not in pred_df.columns:
        return None

    if int(horizon_steps) < 1:
        raise ValueError(f"horizon_steps must be >= 1, got: {horizon_steps}")

    df = pred_df.copy()
    df["y_base"] = df["y_true"].shift(int(horizon_steps))
    y_true = df["y_true"].to_numpy(dtype="float64")
    y_pred = df["y_pred"].to_numpy(dtype="float64")
    y_base = df["y_base"].to_numpy(dtype="float64")

    mask = np.isfinite(y_true) & np.isfinite(y_pred) & np.isfinite(y_base)
    if int(np.sum(mask)) == 0:
        return None

    yt = y_true[mask]
    yp = y_pred[mask]
    yb = y_base[mask]

    rm = float(rmse_fn(yt, yp))
    rb = float(rmse_fn(yt, yb))
    skill = None
    if rb > 0 and np.isfinite(rb):
        skill = float(1.0 - (rm / rb))

    return {
        "rmse": rm,
        "mae": float(mae_fn(yt, yp)),
        "r2": float(r2_fn(yt, yp)),
        "rmse_persistence": rb,
        "skill_score": skill,
    }


def summarize_run(run_dir: str | Path) -> RunSummary:
    run_dir = Path(run_dir)
    payload_path = run_dir / "payload.json"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found in: {run_dir}")

    payload = _read_json(payload_path)
    run_id = payload.get("run_id", run_dir.name)
    phase = payload.get("phase") or "unknown"

    started_at = _parse_dt(payload.get("started_at"))
    completed_at = _parse_dt(payload.get("completed_at"))
    compute_time_s = None
    if started_at and completed_at:
        compute_time_s = (completed_at - started_at).total_seconds()

    artifacts = run_dir / "artifacts"
    kind = "unknown"
    rmse = mae = r2 = None
    rmse_persistence = None
    skill_score = None
    complexity = None
    complexity_name = None
    physical_score = None
    param_count = payload.get("model_param_count")
    target_col = _infer_target_col(payload)
    horizon_steps = _infer_horizon_steps(target_col)

    # Phase 2 KAN training
    if phase == "02-kan-training":
        kind = payload.get("kind", "kan")
        pred_path = _pick_predictions_path(artifacts)
        eval_path = artifacts / "eval_pruned.json"
        sparsity_path = artifacts / "sparsity.json"
        if pred_path is not None:
            pred_df = pd.read_parquet(pred_path)
            m = _metrics_from_predictions(pred_df, horizon_steps=horizon_steps)
            if m is not None:
                rmse = float(m["rmse"])
                mae = float(m["mae"])
                r2 = float(m["r2"])
                rmse_persistence = float(m["rmse_persistence"])
                skill_score = float(m["skill_score"]) if m.get("skill_score") is not None else None
        if rmse is None and eval_path.exists():
            m = _read_json(eval_path)
            rmse, mae, r2 = float(m.get("rmse")), float(m.get("mae")), float(m.get("r2"))
        if sparsity_path.exists():
            s = _read_json(sparsity_path)
            complexity = float(s.get("pruned_ratio")) if s.get("pruned_ratio") is not None else None
            complexity_name = "edge_pruned_ratio"

    # Phase 3 symbolic extraction
    elif payload.get("train_run_id") and (artifacts / "formula_eval_test.json").exists():
        if phase == "unknown":
            phase = "03-symbolic-extraction"
        kind = "kan_symbolic"
        pred_path = _pick_predictions_path(artifacts)
        if pred_path is not None:
            pred_df = pd.read_parquet(pred_path)
            m = _metrics_from_predictions(pred_df, horizon_steps=horizon_steps)
            if m is not None:
                rmse = float(m["rmse"])
                mae = float(m["mae"])
                r2 = float(m["r2"])
                rmse_persistence = float(m["rmse_persistence"])
                skill_score = float(m["skill_score"]) if m.get("skill_score") is not None else None
        if rmse is None:
            m = _read_json(artifacts / "formula_eval_test.json")
            rmse, mae, r2 = float(m.get("rmse")), float(m.get("mae")), float(m.get("r2"))
        cpath = artifacts / "formula_metrics.json"
        if cpath.exists():
            c = _read_json(cpath)
            complexity = float(c.get("node_count")) if c.get("node_count") is not None else None
            complexity_name = "sympy_node_count"
        ppath = artifacts / "physics_mapping.json"
        if ppath.exists():
            p = _read_json(ppath)
            if p.get("score") is not None:
                physical_score = float(p.get("score"))

    # Torch baselines
    elif phase == "04-baselines-torch":
        kind = payload.get("cfg", {}).get("model_type", "torch")
        eval_path = artifacts / "eval_test.json"
        if eval_path.exists():
            m = _read_json(eval_path)
            rmse, mae, r2 = float(m.get("rmse")), float(m.get("mae")), float(m.get("r2"))
        pred_path = _pick_predictions_path(artifacts)
        if pred_path is not None:
            pred_df = pd.read_parquet(pred_path)
            mm = _metrics_from_predictions(pred_df, horizon_steps=horizon_steps)
            if mm is not None:
                rmse = float(mm["rmse"])
                mae = float(mm["mae"])
                r2 = float(mm["r2"])
                rmse_persistence = float(mm["rmse_persistence"])
                skill_score = float(mm["skill_score"]) if mm.get("skill_score") is not None else None
        if param_count is not None:
            complexity = float(param_count)
            complexity_name = "param_count"

    # PySR
    elif phase == "04-baselines-pysr":
        kind = "pysr_seeded" if payload.get("seed_from_symbolic_run") else "pysr"
        eval_path = artifacts / "eval_test.json"
        if eval_path.exists():
            m = _read_json(eval_path)
            rmse, mae, r2 = float(m.get("rmse")), float(m.get("mae")), float(m.get("r2"))
        pred_path = _pick_predictions_path(artifacts)
        if pred_path is not None:
            pred_df = pd.read_parquet(pred_path)
            mm = _metrics_from_predictions(pred_df, horizon_steps=horizon_steps)
            if mm is not None:
                rmse_persistence = float(mm["rmse_persistence"])
                skill_score = float(mm["skill_score"]) if mm.get("skill_score") is not None else None
        eq_path = artifacts / "equations.csv"
        if eq_path.exists():
            df = pd.read_csv(eq_path)
            # Heuristic: prefer 'complexity' column if present
            if "complexity" in df.columns and len(df) > 0:
                complexity = float(df["complexity"].min())
                complexity_name = "pysr_complexity_min"

    # Structured combination (local)
    elif phase == "05-structured-combination":
        kind = payload.get("kind", "structured_combo")
        eval_path = artifacts / "eval_test.json"
        if eval_path.exists():
            m = _read_json(eval_path)
            rmse, mae, r2 = float(m.get("rmse")), float(m.get("mae")), float(m.get("r2"))
        pred_path = _pick_predictions_path(artifacts)
        if pred_path is not None:
            pred_df = pd.read_parquet(pred_path)
            mm = _metrics_from_predictions(pred_df, horizon_steps=horizon_steps)
            if mm is not None:
                rmse_persistence = float(mm["rmse_persistence"])
                skill_score = float(mm["skill_score"]) if mm.get("skill_score") is not None else None

    # Phase 8 transfer evaluation (local)
    elif phase == "08-transfer-eval":
        kind = payload.get("kind", "transfer")
        eval_path = artifacts / "eval_test.json"
        if eval_path.exists():
            m = _read_json(eval_path)
            rmse, mae, r2 = float(m.get("rmse")), float(m.get("mae")), float(m.get("r2"))
        if param_count is not None:
            complexity = float(param_count)
            complexity_name = "param_count"

    return RunSummary(
        run_id=str(run_id),
        phase=str(phase),
        kind=str(kind),
        target_col=target_col,
        rmse=rmse,
        mae=mae,
        r2=r2,
        rmse_persistence=rmse_persistence,
        skill_score=skill_score,
        complexity=complexity,
        complexity_name=complexity_name,
        physical_score=physical_score,
        param_count=int(param_count) if param_count is not None else None,
        compute_time_s=compute_time_s,
        path=run_dir,
    )


def build_comparison_table(run_dirs: list[str | Path]) -> pd.DataFrame:
    rows = [summarize_run(p).as_dict() for p in run_dirs]
    df = pd.DataFrame(rows)

    # Pareto optimality on (rmse, complexity) for rows where both are present.
    df["pareto_optimal"] = False
    valid = df.dropna(subset=["rmse", "complexity"]).copy()
    if len(valid) > 0:
        pareto = []
        for i, a in valid.iterrows():
            dominated = False
            for j, b in valid.iterrows():
                if i == j:
                    continue
                if (b["rmse"] <= a["rmse"]) and (b["complexity"] <= a["complexity"]) and (
                    (b["rmse"] < a["rmse"]) or (b["complexity"] < a["complexity"])
                ):
                    dominated = True
                    break
            pareto.append(not dominated)
        df.loc[valid.index, "pareto_optimal"] = pareto

    # Sort: by rmse then complexity (if available)
    if "rmse" in df.columns:
        df = df.sort_values(by=["rmse", "complexity"], ascending=[True, True], na_position="last")
    return df


def seasonal_breakdown(pred_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-season metrics from a prediction DataFrame.

    Expects:
      - DatetimeIndex
      - columns: y_true, y_pred
    """
    from src.kan_sr.metrics import mae, r2, rmse

    if not isinstance(pred_df.index, pd.DatetimeIndex):
        raise TypeError("pred_df must have a DatetimeIndex for seasonal breakdown")

    def season(month: int) -> str:
        if month in (12, 1, 2):
            return "DJF"
        if month in (3, 4, 5):
            return "MAM"
        if month in (6, 7, 8):
            return "JJA"
        return "SON"

    df = pred_df.copy()
    df = df.dropna(subset=["y_true", "y_pred"])
    df["season"] = [season(m) for m in df.index.month]

    rows: list[dict[str, Any]] = []
    for s, g in df.groupby("season"):
        y_true = g["y_true"].to_numpy(dtype="float64")
        y_pred = g["y_pred"].to_numpy(dtype="float64")
        rows.append(
            {
                "season": s,
                "n": int(len(g)),
                "rmse": rmse(y_true, y_pred),
                "mae": mae(y_true, y_pred),
                "r2": r2(y_true, y_pred),
            }
        )

    out = pd.DataFrame(rows).sort_values("season")
    return out


def day_night_breakdown(pred_df: pd.DataFrame, *, is_night) -> pd.DataFrame:
    """
    Compute day/night metrics from predictions, using an externally-provided is_night series.

    Expects:
      - pred_df index matches is_night index (at least on overlap)
      - columns: y_true, y_pred
    """
    from src.kan_sr.metrics import mae, r2, rmse

    if "y_true" not in pred_df.columns or "y_pred" not in pred_df.columns:
        raise ValueError("pred_df must contain y_true/y_pred")

    df = pred_df[["y_true", "y_pred"]].copy()
    df = df.dropna(subset=["y_true", "y_pred"])
    if not hasattr(is_night, "reindex"):
        raise TypeError("is_night must be a pandas Series-like object")
    night = is_night.reindex(df.index)
    night = night.dropna()
    df = df.loc[night.index].copy()
    df["is_night"] = night.astype(bool)

    rows: list[dict[str, Any]] = []
    for label, mask in [("day", False), ("night", True)]:
        g = df[df["is_night"] == bool(mask)]
        if len(g) == 0:
            continue
        y_true = g["y_true"].to_numpy(dtype="float64")
        y_pred = g["y_pred"].to_numpy(dtype="float64")
        rows.append({"segment": label, "n": int(len(g)), "rmse": rmse(y_true, y_pred), "mae": mae(y_true, y_pred), "r2": r2(y_true, y_pred)})

    return pd.DataFrame(rows)
