#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.kan_sr.metrics import mae, r2, rmse


def _utc_run_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{prefix}_{ts}_{uuid.uuid4().hex[:8]}"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _infer_target_col(payload: dict[str, Any]) -> str | None:
    if payload.get("target_col"):
        return str(payload.get("target_col"))
    cfg = payload.get("cfg")
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg.get("target_col"))
    return None


def _infer_horizon_steps(target_col: str | None) -> int:
    if not target_col:
        return 1
    s = str(target_col)
    if "_h" not in s:
        return 1
    try:
        return max(1, int(s.rsplit("_h", 1)[1]))
    except Exception:
        return 1


def _pick_predictions_path(run_dir: Path) -> Path:
    artifacts = run_dir / "artifacts"
    for name in ["predictions_test_reconstructed.parquet", "predictions_test.parquet"]:
        p = artifacts / name
        if p.exists():
            return p
    raise FileNotFoundError(f"predictions file not found under: {artifacts}")


def _load_pred(run_dir: Path, *, label: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    payload_path = run_dir / "payload.json"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found: {payload_path}")
    payload = _safe_read_json(payload_path)
    pred_path = _pick_predictions_path(run_dir)
    pred_df = pd.read_parquet(pred_path)
    if "y_true" not in pred_df.columns or "y_pred" not in pred_df.columns:
        raise ValueError(f"Invalid predictions file (missing y_true/y_pred): {pred_path}")
    out = pred_df[["y_true", "y_pred"]].copy()
    out = out.rename(columns={"y_true": f"{label}_true", "y_pred": f"{label}_pred"})
    return out, payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Combine load/wind/solar prediction runs into a net_load prediction run.")
    ap.add_argument("--load-run", required=True, help="Path to synced load(run) directory.")
    ap.add_argument("--wind-run", required=True, help="Path to synced wind(run) directory.")
    ap.add_argument("--solar-run", required=True, help="Path to synced solar(run) directory.")
    ap.add_argument("--out-run-id", default="", help="Output run_id under runs/ (default: auto).")
    ap.add_argument("--out-runs-dir", default="runs", help="Local runs/ directory.")
    args = ap.parse_args()

    started_at = datetime.now(timezone.utc)

    load_dir = Path(args.load_run)
    wind_dir = Path(args.wind_run)
    solar_dir = Path(args.solar_run)

    load_df, load_payload = _load_pred(load_dir, label="load")
    wind_df, wind_payload = _load_pred(wind_dir, label="wind")
    solar_df, solar_payload = _load_pred(solar_dir, label="solar")

    load_target = _infer_target_col(load_payload)
    wind_target = _infer_target_col(wind_payload)
    solar_target = _infer_target_col(solar_payload)
    horizon = _infer_horizon_steps(load_target)
    if _infer_horizon_steps(wind_target) != horizon or _infer_horizon_steps(solar_target) != horizon:
        raise ValueError(f"Horizon mismatch: load={load_target!r}, wind={wind_target!r}, solar={solar_target!r}")

    joined = load_df.join(wind_df, how="inner").join(solar_df, how="inner")
    joined = joined.dropna(subset=list(joined.columns))
    if len(joined) == 0:
        raise ValueError("No overlapping finite rows between component prediction runs")

    y_true = joined["load_true"] - joined["wind_true"] - joined["solar_true"]
    y_pred = joined["load_pred"] - joined["wind_pred"] - joined["solar_pred"]
    y_true_arr = y_true.to_numpy(dtype=np.float64)
    y_pred_arr = y_pred.to_numpy(dtype=np.float64)

    metrics = {"rmse": float(rmse(y_true_arr, y_pred_arr)), "mae": float(mae(y_true_arr, y_pred_arr)), "r2": float(r2(y_true_arr, y_pred_arr)), "n": int(len(joined))}

    out_run_id = args.out_run_id.strip() or _utc_run_id(prefix="combo_net_load")
    out_run_dir = Path(args.out_runs_dir) / out_run_id
    artifacts_dir = out_run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    pred_out = pd.DataFrame({"y_true": y_true, "y_pred": y_pred, "residual": y_pred - y_true}, index=joined.index)
    pred_out.to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")
    _write_json(artifacts_dir / "eval_test.json", metrics)

    out_payload: dict[str, Any] = {
        "run_id": out_run_id,
        "phase": "05-structured-combination",
        "kind": "net_load_from_components",
        "target_col": f"net_load_h{horizon}" if horizon != 1 else "net_load",
        "component_runs": {"load": load_dir.name, "wind": wind_dir.name, "solar": solar_dir.name},
        "component_targets": {"load": load_target, "wind": wind_target, "solar": solar_target},
        "started_at": started_at.isoformat(),
    }
    out_payload["eval_test"] = metrics
    out_payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    _write_json(out_run_dir / "payload.json", out_payload)

    print(json.dumps({"out_run_id": out_run_id, "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()

