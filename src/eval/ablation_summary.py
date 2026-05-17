from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, TextIO

import numpy as np
import pandas as pd

from src.kan_sr.metrics import r2 as r2_fn
from src.kan_sr.metrics import rmse as rmse_fn

_HORIZON_RE = re.compile(r"_h(\d+)$")

BASE_OUTPUT_FIELDS = [
    "run_id",
    "kind",
    "target_col",
    "horizon_steps",
    "abs_test_rmse",
    "abs_test_r2",
    "abs_test_rmse_persist",
    "abs_test_skill",
    "delta_test_rmse",
    "delta_test_r2",
    "delta_val_rmse",
    "delta_val_r2",
]


@dataclass(frozen=True)
class AblationSummaryConfig:
    target_prefix: str
    edge_field_name: str
    feature_prefixes: tuple[str, ...]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def infer_target_col(payload: dict[str, Any]) -> str:
    if payload.get("target_col"):
        return str(payload["target_col"])
    cfg = payload.get("cfg")
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg["target_col"])
    raise ValueError("Could not infer target_col from payload.json")


def infer_horizon_steps(target_col: str) -> int:
    match = _HORIZON_RE.search(str(target_col))
    if not match:
        return 1
    horizon_steps = int(match.group(1))
    if horizon_steps < 1:
        raise ValueError(f"Invalid horizon in target_col: {target_col!r}")
    return horizon_steps


def require_target_prefix(target_col: str, *, prefix: str) -> None:
    if not str(target_col).startswith(prefix):
        raise ValueError(f"Expected target_col with prefix {prefix!r}, got: {target_col!r}")


def rmse_r2(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float]:
    y_true_arr = np.asarray(y_true, dtype=np.float64).reshape(-1)
    y_pred_arr = np.asarray(y_pred, dtype=np.float64).reshape(-1)
    mask = np.isfinite(y_true_arr) & np.isfinite(y_pred_arr)
    if int(np.sum(mask)) == 0:
        raise ValueError("No finite samples to evaluate")
    return (
        float(rmse_fn(y_true_arr[mask], y_pred_arr[mask])),
        float(r2_fn(y_true_arr[mask], y_pred_arr[mask])),
    )


def abs_metrics_from_reconstructed(
    pred_df: pd.DataFrame,
    *,
    horizon_steps: int,
) -> tuple[float, float, float, float | None]:
    if "y_true" not in pred_df.columns or "y_pred" not in pred_df.columns:
        raise ValueError("Reconstructed predictions missing y_true/y_pred")

    df = pred_df.copy()
    df["y_base"] = df["y_true"].shift(int(horizon_steps))
    y_true = df["y_true"].to_numpy(dtype=np.float64)
    y_pred = df["y_pred"].to_numpy(dtype=np.float64)
    y_base = df["y_base"].to_numpy(dtype=np.float64)

    mask = np.isfinite(y_true) & np.isfinite(y_pred) & np.isfinite(y_base)
    if int(np.sum(mask)) == 0:
        raise ValueError("No finite samples to evaluate abs(test) with persistence baseline")

    y_true_eval = y_true[mask]
    y_pred_eval = y_pred[mask]
    y_base_eval = y_base[mask]
    rmse = float(rmse_fn(y_true_eval, y_pred_eval))
    rmse_persist = float(rmse_fn(y_true_eval, y_base_eval))
    skill = None
    if rmse_persist > 0 and np.isfinite(rmse_persist):
        skill = float(1.0 - (rmse / rmse_persist))
    return (rmse, float(r2_fn(y_true_eval, y_pred_eval)), rmse_persist, skill)


def count_active_edges(feature_importance_csv: Path, *, feature_prefixes: tuple[str, ...]) -> int:
    if not feature_importance_csv.exists():
        raise FileNotFoundError(f"feature_importance.csv not found: {feature_importance_csv}")
    df = pd.read_csv(feature_importance_csv)
    if "feature" not in df.columns or "active_edges" not in df.columns:
        raise ValueError(f"Invalid feature_importance.csv schema: {feature_importance_csv}")
    feature_series = df["feature"].astype(str)
    mask = feature_series.apply(lambda name: name.startswith(feature_prefixes))
    if int(mask.sum()) == 0:
        return 0
    return int(df.loc[mask, "active_edges"].to_numpy(dtype=np.int64).sum())


def as_run_dir(arg: str, *, repo_root: Path) -> Path:
    path = Path(arg)
    if path.exists():
        return path
    return repo_root / "runs" / arg


def summarize_run(
    run_dir: Path,
    *,
    config: AblationSummaryConfig,
    require_abs: bool,
) -> dict[str, Any]:
    payload_path = run_dir / "payload.json"
    artifacts_dir = run_dir / "artifacts"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found: {payload_path}")

    payload = read_json(payload_path)
    run_id = str(payload.get("run_id") or run_dir.name)
    kind = str(payload.get("kind") or payload.get("phase") or "unknown")
    target_col = infer_target_col(payload)
    require_target_prefix(target_col, prefix=config.target_prefix)
    horizon_steps = infer_horizon_steps(target_col)

    pred_delta_path = artifacts_dir / "predictions_test.parquet"
    if not pred_delta_path.exists():
        raise FileNotFoundError(f"predictions_test.parquet not found: {pred_delta_path}")
    pred_delta_df = pd.read_parquet(pred_delta_path)
    delta_test_rmse, delta_test_r2 = rmse_r2(pred_delta_df["y_true"], pred_delta_df["y_pred"])

    eval_val_path = artifacts_dir / "eval_pruned.json"
    if not eval_val_path.exists():
        raise FileNotFoundError(f"eval_pruned.json not found: {eval_val_path}")
    eval_val = read_json(eval_val_path)

    pred_abs_path = artifacts_dir / "predictions_test_reconstructed.parquet"
    if require_abs and not pred_abs_path.exists():
        raise FileNotFoundError(
            f"predictions_test_reconstructed.parquet not found: {pred_abs_path}. "
            "Run scripts/reconstruct_predictions.py --run <run_dir> first."
        )

    abs_test_rmse = 0.0
    abs_test_r2 = 0.0
    abs_test_rmse_persist = 0.0
    abs_test_skill: float | None = None
    if pred_abs_path.exists():
        pred_abs_df = pd.read_parquet(pred_abs_path)
        (
            abs_test_rmse,
            abs_test_r2,
            abs_test_rmse_persist,
            abs_test_skill,
        ) = abs_metrics_from_reconstructed(pred_abs_df, horizon_steps=horizon_steps)

    return {
        "run_id": run_id,
        "kind": kind,
        "target_col": target_col,
        "horizon_steps": int(horizon_steps),
        "abs_test_rmse": float(abs_test_rmse),
        "abs_test_r2": float(abs_test_r2),
        "abs_test_rmse_persist": float(abs_test_rmse_persist),
        "abs_test_skill": abs_test_skill,
        "delta_test_rmse": float(delta_test_rmse),
        "delta_test_r2": float(delta_test_r2),
        "delta_val_rmse": float(eval_val["rmse"]),
        "delta_val_r2": float(eval_val["r2"]),
        config.edge_field_name: int(
            count_active_edges(
                artifacts_dir / "feature_importance.csv",
                feature_prefixes=config.feature_prefixes,
            )
        ),
    }


def write_csv(
    rows: Iterable[dict[str, Any]],
    *,
    edge_field_name: str,
    output: TextIO,
) -> None:
    fieldnames = [*BASE_OUTPUT_FIELDS, edge_field_name]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key) for key in fieldnames})
