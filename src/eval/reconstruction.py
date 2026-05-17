from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.data.derived import compute_net_load
from src.data.split import inverse_transform
from src.kan_sr.metrics import mae, r2, rmse

DELTA_RECON_PREDICTIONS = "predictions_test_reconstructed.parquet"
DELTA_RECON_EVAL = "eval_test_reconstructed.json"
DELTA_RECON_FORMULA = "formula_reconstructed.sympy.txt"
DELTA_RECON_FORMULA_TEX = "formula_reconstructed.tex"

_DELTA_TARGET_RE = re.compile(r"^delta_(load|net_load|wind|solar)(?:_h(\d+))?$")


@dataclass(frozen=True)
class DeltaReconSpec:
    base: str
    horizon_steps: int
    lag_col: str


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def infer_target_col(payload: dict[str, Any]) -> str | None:
    if payload.get("target_col"):
        return str(payload["target_col"])
    cfg = payload.get("cfg") or {}
    if isinstance(cfg, dict) and cfg.get("target_col"):
        return str(cfg["target_col"])
    return None


def infer_data_ref(payload: dict[str, Any]) -> tuple[str | None, str | None]:
    data_run_id = payload.get("data_run_id")
    data_timestamp = payload.get("data_timestamp")
    return (str(data_run_id) if data_run_id else None, str(data_timestamp) if data_timestamp else None)


def delta_reconstruction_spec(target_col: str) -> DeltaReconSpec | None:
    match = _DELTA_TARGET_RE.match(str(target_col))
    if not match:
        return None
    base = str(match.group(1))
    horizon = int(match.group(2) or "1")
    if horizon < 1:
        raise ValueError(f"Invalid horizon in target_col: {target_col!r}")
    return DeltaReconSpec(base=base, horizon_steps=horizon, lag_col=f"{base}_lag_{horizon}")


def load_processed_split(processed_dir: Path, *, split: str, timestamp: str) -> pd.DataFrame:
    parquet_path = processed_dir / f"{split}_{timestamp}.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Split file not found: {parquet_path}")
    return pd.read_parquet(parquet_path)


def _resolve_source_data_ref(data_run_dir: Path, *, fallback_timestamp: str) -> tuple[str, str]:
    payload_path = data_run_dir / "payload.json"
    if not payload_path.exists():
        return (data_run_dir.name, str(fallback_timestamp))
    payload = read_json(payload_path)
    source_run_id = payload.get("source_data_run_id")
    source_timestamp = payload.get("source_timestamp")
    if source_run_id and source_timestamp:
        return (str(source_run_id), str(source_timestamp))
    return (data_run_dir.name, str(fallback_timestamp))


def resolve_reconstruction_source(data_run_dir: Path, *, data_timestamp: str) -> tuple[str, str]:
    aligned_test = data_run_dir / "processed" / f"test_{data_timestamp}.parquet"
    aligned_scaler = data_run_dir / "artifacts" / "scaler_params.json"
    if aligned_test.exists() and aligned_scaler.exists():
        return (data_run_dir.name, str(data_timestamp))
    return _resolve_source_data_ref(data_run_dir, fallback_timestamp=data_timestamp)


def base_raw_series(test_df: pd.DataFrame, *, base: str, scaler_params: dict[str, Any]) -> pd.Series:
    if base == "net_load":
        required = ["load", "wind", "solar"]
        missing = [col for col in required if col not in test_df.columns]
        if missing:
            raise ValueError(f"Missing columns for net_load reconstruction: {missing}")
        base_df = inverse_transform(test_df[required], scaler_params)
        return compute_net_load(base_df["load"], base_df["wind"], base_df["solar"]).astype(np.float64)
    if base not in test_df.columns:
        raise ValueError(f"Missing base column for reconstruction: {base}")
    return inverse_transform(test_df[[base]], scaler_params)[base].astype(np.float64)


def reconstruct_delta_run(
    run_dir: Path,
    *,
    runs_root: Path,
    target_col: str,
    data_run_id: str,
    data_timestamp: str,
) -> bool:
    pred_path = run_dir / "artifacts" / "predictions_test.parquet"
    if not pred_path.exists():
        return False
    recon = delta_reconstruction_spec(target_col)
    if recon is None:
        return False

    data_run_dir = runs_root / data_run_id
    source_run_id, source_timestamp = resolve_reconstruction_source(data_run_dir, data_timestamp=data_timestamp)
    source_run_dir = runs_root / source_run_id
    processed_dir = source_run_dir / "processed"
    scaler_path = source_run_dir / "artifacts" / "scaler_params.json"
    if not processed_dir.exists():
        raise FileNotFoundError(f"Processed dir not found for reconstruction: {processed_dir}")
    if not scaler_path.exists():
        raise FileNotFoundError(f"scaler_params.json not found for reconstruction: {scaler_path}")

    test_df = load_processed_split(processed_dir, split="test", timestamp=source_timestamp)
    scaler_params = read_json(scaler_path)
    base_raw = base_raw_series(test_df, base=recon.base, scaler_params=scaler_params)
    lag_raw = base_raw.shift(recon.horizon_steps)

    pred_df = pd.read_parquet(pred_path)
    if "y_true" not in pred_df.columns or "y_pred" not in pred_df.columns:
        raise ValueError(f"Invalid predictions file (missing y_true/y_pred): {pred_path}")
    joined = pred_df[["y_true", "y_pred"]].join(lag_raw.rename("_base_lag"), how="left")
    if joined.empty:
        raise ValueError(f"No overlapping index between predictions and processed test split for {run_dir.name}")
    if not np.isfinite(joined["_base_lag"].to_numpy(dtype=np.float64)).any():
        raise ValueError(f"Reconstruction base lag is all-NaN for {run_dir.name} (target={target_col})")

    out_df = pd.DataFrame(index=joined.index)
    out_df["y_true"] = joined["_base_lag"] + joined["y_true"].astype(np.float64)
    out_df["y_pred"] = joined["_base_lag"] + joined["y_pred"].astype(np.float64)
    out_df["residual"] = out_df["y_pred"] - out_df["y_true"]
    out_df.to_parquet(run_dir / "artifacts" / DELTA_RECON_PREDICTIONS, compression="snappy")

    finite = np.isfinite(out_df["y_true"].to_numpy(dtype=np.float64)) & np.isfinite(out_df["y_pred"].to_numpy(dtype=np.float64))
    eval_payload: dict[str, Any] = {
        "reconstructed_from": target_col,
        "reconstructed_target": recon.base,
        "base_run_id": source_run_id,
        "base_timestamp": source_timestamp,
        "horizon_steps": int(recon.horizon_steps),
    }
    if int(np.sum(finite)) > 0:
        y_true = out_df["y_true"].to_numpy(dtype=np.float64)[finite]
        y_pred = out_df["y_pred"].to_numpy(dtype=np.float64)[finite]
        eval_payload.update({"rmse": float(rmse(y_true, y_pred)), "mae": float(mae(y_true, y_pred)), "r2": float(r2(y_true, y_pred)), "n_eval": int(len(y_true))})
    (run_dir / "artifacts" / DELTA_RECON_EVAL).write_text(json.dumps(eval_payload, indent=2))

    formula_path = run_dir / "artifacts" / "formula.sympy.txt"
    if formula_path.exists():
        import sympy as sp

        expr_delta = sp.sympify(formula_path.read_text().strip())
        expr_full = sp.Symbol(recon.lag_col) + expr_delta
        (run_dir / "artifacts" / DELTA_RECON_FORMULA).write_text(str(expr_full))
        (run_dir / "artifacts" / DELTA_RECON_FORMULA_TEX).write_text(sp.latex(expr_full))
    return True
