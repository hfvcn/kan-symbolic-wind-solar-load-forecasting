#!/usr/bin/env python3
from __future__ import annotations

"""
Reconstruct base-series predictions for delta/residual targets.

Motivation:
  For delta targets (e.g., delta_load), the model predicts a *change*:
      delta_load_t = load_t - load_{t-1}
  For paper/reporting we often want the reconstructed absolute series:
      load_pred_t = load_{t-1} + delta_pred_t

This script writes:
  - runs/<run_id>/artifacts/predictions_test_reconstructed.parquet
  - runs/<run_id>/artifacts/eval_test_reconstructed.json
  - (optional) runs/<run_id>/artifacts/formula_reconstructed.{sympy.txt,tex}
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.split import inverse_transform
from src.kan_sr.metrics import mae, r2, rmse


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _infer_target_col(payload: dict[str, Any]) -> str | None:
    if "target_col" in payload and payload.get("target_col"):
        return str(payload["target_col"])
    cfg = payload.get("cfg") or {}
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg["target_col"])
    return None


def _infer_data_ref(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    data_run_id = payload.get("data_run_id")
    data_ts = payload.get("data_timestamp")
    return (str(data_run_id) if data_run_id else None, str(data_ts) if data_ts else None)


def _reconstruct_delta_run(run_dir: Path, *, target_col: str, data_run_id: str, data_timestamp: str) -> bool:
    artifacts = run_dir / "artifacts"
    pred_path = artifacts / "predictions_test.parquet"
    if not pred_path.exists():
        return False

    if target_col == "delta_load":
        base_name = "load"
        lag_col = "load_lag_1"
    elif target_col == "delta_net_load":
        base_name = "net_load"
        lag_col = "net_load_lag_1"
    else:
        return False

    data_run = REPO_ROOT / "runs" / data_run_id
    test_path = data_run / "processed" / f"test_{data_timestamp}.parquet"
    scaler_path = data_run / "artifacts" / "scaler_params.json"
    if not test_path.exists():
        raise FileNotFoundError(f"Processed test split not found for reconstruction: {test_path}")
    if not scaler_path.exists():
        raise FileNotFoundError(f"scaler_params.json not found for reconstruction: {scaler_path}")

    test_df = pd.read_parquet(test_path)
    if lag_col not in test_df.columns:
        raise ValueError(f"Required lag column missing for reconstruction: {lag_col} (in {test_path})")

    scaler_params = json.loads(scaler_path.read_text())
    lag_raw = inverse_transform(test_df[[lag_col]], scaler_params)[lag_col].astype(np.float64)

    pred_df = pd.read_parquet(pred_path)
    if "y_true" not in pred_df.columns or "y_pred" not in pred_df.columns:
        raise ValueError(f"Invalid predictions file (missing y_true/y_pred): {pred_path}")

    # Align on index (symbolic predictions may include NaN; keep full index for plots).
    joined = pred_df[["y_true", "y_pred"]].join(lag_raw.rename("_base_lag"), how="inner")
    if len(joined) == 0:
        raise ValueError(f"No overlapping index between predictions and processed test split for {run_dir.name}")

    y_true_base = joined["_base_lag"] + joined["y_true"].astype(np.float64)
    y_pred_base = joined["_base_lag"] + joined["y_pred"].astype(np.float64)

    out_df = pd.DataFrame({"y_true": y_true_base, "y_pred": y_pred_base}, index=joined.index)
    out_df["residual"] = out_df["y_pred"] - out_df["y_true"]

    out_path = artifacts / "predictions_test_reconstructed.parquet"
    out_df.to_parquet(out_path, compression="snappy")

    # Metrics on finite subset.
    finite = np.isfinite(out_df["y_true"].to_numpy(dtype=np.float64)) & np.isfinite(out_df["y_pred"].to_numpy(dtype=np.float64))
    m: dict[str, Any] = {"reconstructed_from": target_col, "reconstructed_target": base_name}
    if int(np.sum(finite)) > 0:
        y_t = out_df["y_true"].to_numpy(dtype=np.float64)[finite]
        y_p = out_df["y_pred"].to_numpy(dtype=np.float64)[finite]
        m.update({"rmse": float(rmse(y_t, y_p)), "mae": float(mae(y_t, y_p)), "r2": float(r2(y_t, y_p)), "n_eval": int(len(y_t))})
    (artifacts / "eval_test_reconstructed.json").write_text(json.dumps(m, indent=2))

    # Optional: formula reconstruction for symbolic runs
    sym_path = artifacts / "formula.sympy.txt"
    if sym_path.exists():
        try:
            import sympy as sp

            expr_delta = sp.sympify(sym_path.read_text().strip())
            base_sym = sp.Symbol(lag_col)
            expr_full = base_sym + expr_delta
            (artifacts / "formula_reconstructed.sympy.txt").write_text(str(expr_full))
            (artifacts / "formula_reconstructed.tex").write_text(sp.latex(expr_full))
        except Exception:
            pass

    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Reconstruct base-series predictions for delta targets.")
    ap.add_argument("--run", action="append", required=True, help="Path to a synced run directory (repeatable).")
    args = ap.parse_args()

    ok = 0
    skipped = 0
    for run_path in args.run:
        run_dir = Path(run_path)
        payload_path = run_dir / "payload.json"
        if not payload_path.exists():
            skipped += 1
            continue
        payload = _safe_read_json(payload_path)
        target_col = _infer_target_col(payload)
        data_run_id, data_ts = _infer_data_ref(payload)
        if not target_col or not data_run_id or not data_ts:
            skipped += 1
            continue
        if target_col not in {"delta_load", "delta_net_load"}:
            skipped += 1
            continue
        try:
            did = _reconstruct_delta_run(run_dir, target_col=target_col, data_run_id=data_run_id, data_timestamp=data_ts)
            ok += int(bool(did))
        except Exception as e:
            print(f"[WARN] Reconstruction failed for {run_dir}: {e}")
            continue

    print(f"[reconstruct] done: ok={ok} skipped={skipped}")


if __name__ == "__main__":
    main()

