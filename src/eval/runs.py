from __future__ import annotations

import json
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
    rmse: float | None
    mae: float | None
    r2: float | None
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
            "rmse": self.rmse,
            "mae": self.mae,
            "r2": self.r2,
            "complexity": self.complexity,
            "complexity_name": self.complexity_name,
            "physical_score": self.physical_score,
            "param_count": self.param_count,
            "compute_time_s": self.compute_time_s,
            "path": str(self.path),
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
    complexity = None
    complexity_name = None
    physical_score = None
    param_count = payload.get("model_param_count")

    # Phase 2 KAN training
    if phase == "02-kan-training":
        kind = payload.get("kind", "kan")
        pred_path = artifacts / "predictions_test.parquet"
        eval_path = artifacts / "eval_pruned.json"
        sparsity_path = artifacts / "sparsity.json"
        if pred_path.exists():
            try:
                from src.kan_sr.metrics import mae as mae_fn
                from src.kan_sr.metrics import r2 as r2_fn
                from src.kan_sr.metrics import rmse as rmse_fn

                pred_df = pd.read_parquet(pred_path).dropna(subset=["y_true", "y_pred"])
                if len(pred_df) > 0:
                    y_true = pred_df["y_true"].to_numpy(dtype="float64")
                    y_pred = pred_df["y_pred"].to_numpy(dtype="float64")
                    rmse = float(rmse_fn(y_true, y_pred))
                    mae = float(mae_fn(y_true, y_pred))
                    r2 = float(r2_fn(y_true, y_pred))
            except Exception:
                pass
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
        eq_path = artifacts / "equations.csv"
        if eq_path.exists():
            df = pd.read_csv(eq_path)
            # Heuristic: prefer 'complexity' column if present
            if "complexity" in df.columns and len(df) > 0:
                complexity = float(df["complexity"].min())
                complexity_name = "pysr_complexity_min"

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
        rmse=rmse,
        mae=mae,
        r2=r2,
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
