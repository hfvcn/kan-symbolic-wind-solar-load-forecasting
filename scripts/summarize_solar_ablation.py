#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.kan_sr.metrics import r2 as r2_fn
from src.kan_sr.metrics import rmse as rmse_fn


_DELTA_SOLAR_RE = re.compile(r"^delta_solar(?:_h(\d+))?$")
_HORIZON_RE = re.compile(r"_h(\d+)$")


@dataclass(frozen=True)
class SolarAblationRow:
    run_id: str
    kind: str
    target_col: str
    horizon_steps: int
    abs_test_rmse: float
    abs_test_r2: float
    abs_test_rmse_persist: float
    abs_test_skill: float | None
    delta_test_rmse: float
    delta_test_r2: float
    delta_val_rmse: float
    delta_val_r2: float
    ghi_edges: int


OUTPUT_FIELDS = [
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
    "ghi_edges",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _infer_target_col(payload: dict[str, Any]) -> str:
    if payload.get("target_col"):
        return str(payload["target_col"])
    cfg = payload.get("cfg")
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg["target_col"])
    raise ValueError("Could not infer target_col from payload.json")


def _infer_horizon_steps(target_col: str) -> int:
    m = _HORIZON_RE.search(str(target_col))
    if not m:
        return 1
    h = int(m.group(1))
    if h < 1:
        raise ValueError(f"Invalid horizon in target_col: {target_col!r}")
    return h


def _require_delta_solar(target_col: str) -> None:
    if _DELTA_SOLAR_RE.match(str(target_col)) is None:
        raise ValueError(f"Expected delta_solar target_col, got: {target_col!r}")


def _rmse_r2(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float]:
    yt = np.asarray(y_true, dtype=np.float64).reshape(-1)
    yp = np.asarray(y_pred, dtype=np.float64).reshape(-1)
    mask = np.isfinite(yt) & np.isfinite(yp)
    if int(np.sum(mask)) == 0:
        raise ValueError("No finite samples to evaluate")
    return (float(rmse_fn(yt[mask], yp[mask])), float(r2_fn(yt[mask], yp[mask])))


def _abs_metrics_from_reconstructed(pred_df: pd.DataFrame, *, horizon_steps: int) -> tuple[float, float, float, float | None]:
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

    yt = y_true[mask]
    yp = y_pred[mask]
    yb = y_base[mask]

    rm = float(rmse_fn(yt, yp))
    rb = float(rmse_fn(yt, yb))
    skill = float(1.0 - (rm / rb)) if rb > 0 and np.isfinite(rb) else None
    return (rm, float(r2_fn(yt, yp)), rb, skill)


def _ghi_edges(feature_importance_csv: Path) -> int:
    if not feature_importance_csv.exists():
        raise FileNotFoundError(f"feature_importance.csv not found: {feature_importance_csv}")
    df = pd.read_csv(feature_importance_csv)
    if "feature" not in df.columns or "active_edges" not in df.columns:
        raise ValueError(f"Invalid feature_importance.csv schema: {feature_importance_csv}")
    ghi_df = df[df["feature"].astype(str).str.startswith("ghi_")]
    if len(ghi_df) == 0:
        return 0
    return int(np.sum(ghi_df["active_edges"].to_numpy(dtype=np.int64)))


def _as_run_dir(arg: str) -> Path:
    p = Path(arg)
    if p.exists():
        return p
    return REPO_ROOT / "runs" / arg


def summarize_run(run_dir: Path, *, require_abs: bool) -> SolarAblationRow:
    payload_path = run_dir / "payload.json"
    artifacts = run_dir / "artifacts"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found: {payload_path}")
    payload = _read_json(payload_path)

    run_id = str(payload.get("run_id") or run_dir.name)
    kind = str(payload.get("kind") or payload.get("phase") or "unknown")
    target_col = _infer_target_col(payload)
    _require_delta_solar(target_col)
    horizon_steps = _infer_horizon_steps(target_col)

    pred_delta_path = artifacts / "predictions_test.parquet"
    if not pred_delta_path.exists():
        raise FileNotFoundError(f"predictions_test.parquet not found: {pred_delta_path}")
    pred_delta = pd.read_parquet(pred_delta_path)
    delta_test_rmse, delta_test_r2 = _rmse_r2(pred_delta["y_true"], pred_delta["y_pred"])

    eval_val_path = artifacts / "eval_pruned.json"
    if not eval_val_path.exists():
        raise FileNotFoundError(f"eval_pruned.json not found: {eval_val_path}")
    eval_val = _read_json(eval_val_path)
    delta_val_rmse = float(eval_val["rmse"])
    delta_val_r2 = float(eval_val["r2"])

    pred_abs_path = artifacts / "predictions_test_reconstructed.parquet"
    if require_abs and not pred_abs_path.exists():
        raise FileNotFoundError(
            f"predictions_test_reconstructed.parquet not found: {pred_abs_path}. "
            "Run scripts/reconstruct_predictions.py --run <run_dir> first."
        )

    abs_test_rmse = abs_test_r2 = abs_test_rmse_persist = 0.0
    abs_test_skill: float | None = None
    if pred_abs_path.exists():
        pred_abs = pd.read_parquet(pred_abs_path)
        abs_test_rmse, abs_test_r2, abs_test_rmse_persist, abs_test_skill = _abs_metrics_from_reconstructed(
            pred_abs, horizon_steps=horizon_steps
        )

    ghi_edges = _ghi_edges(artifacts / "feature_importance.csv")

    return SolarAblationRow(
        run_id=run_id,
        kind=kind,
        target_col=target_col,
        horizon_steps=int(horizon_steps),
        abs_test_rmse=float(abs_test_rmse),
        abs_test_r2=float(abs_test_r2),
        abs_test_rmse_persist=float(abs_test_rmse_persist),
        abs_test_skill=abs_test_skill,
        delta_test_rmse=float(delta_test_rmse),
        delta_test_r2=float(delta_test_r2),
        delta_val_rmse=float(delta_val_rmse),
        delta_val_r2=float(delta_val_r2),
        ghi_edges=int(ghi_edges),
    )


def _write_csv(rows: Iterable[SolarAblationRow]) -> None:
    w = csv.DictWriter(sys.stdout, fieldnames=OUTPUT_FIELDS)
    w.writeheader()
    for row in rows:
        w.writerow({k: getattr(row, k) for k in OUTPUT_FIELDS})


def main() -> None:
    ap = argparse.ArgumentParser(description="Summarize solar ablation runs (abs(test) + delta(test/val) + ghi_edges).")
    ap.add_argument("--run", action="append", required=True, help="Run id or path to local run dir (repeatable).")
    ap.add_argument(
        "--require-abs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require predictions_test_reconstructed.parquet to exist (default: true).",
    )
    args = ap.parse_args()

    rows: list[SolarAblationRow] = []
    for arg in args.run:
        run_dir = _as_run_dir(str(arg))
        if not run_dir.exists():
            raise FileNotFoundError(f"Run dir not found: {run_dir}")
        rows.append(summarize_run(run_dir, require_abs=bool(args.require_abs)))

    _write_csv(rows)


if __name__ == "__main__":
    main()

