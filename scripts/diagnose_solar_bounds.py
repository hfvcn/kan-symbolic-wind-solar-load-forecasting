#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.split import inverse_transform
from src.kan_sr.metrics import r2 as r2_fn
from src.kan_sr.metrics import rmse as rmse_fn


_DELTA_SOLAR_RE = re.compile(r"^delta_solar(?:_h(\d+))?$")


@dataclass(frozen=True)
class TrainSolarStats:
    solar_p99: float
    solar_max: float
    delta_q01: float
    delta_q99: float


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
    m = _DELTA_SOLAR_RE.match(str(target_col))
    if m is None:
        raise ValueError(f"Expected delta_solar target_col, got: {target_col!r}")
    h = int(m.group(1) or "1")
    if h < 1:
        raise ValueError(f"Invalid horizon in target_col: {target_col!r}")
    return h


def _as_run_dir(arg: str) -> Path:
    p = Path(arg)
    if p.exists():
        return p
    return REPO_ROOT / "runs" / arg


def _quantiles(x: np.ndarray, qs: tuple[float, ...]) -> dict[str, float]:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    x = x[np.isfinite(x)]
    if x.size == 0:
        raise ValueError("No finite samples for quantiles")
    return {f"p{int(q * 100):02d}": float(np.quantile(x, q)) for q in qs}


def _stats(x: np.ndarray) -> dict[str, Any]:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    x = x[np.isfinite(x)]
    if x.size == 0:
        raise ValueError("No finite samples for stats")
    out: dict[str, Any] = {
        "n": int(x.size),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
        "mean": float(np.mean(x)),
        "std": float(np.std(x, ddof=0)),
    }
    out.update(_quantiles(x, qs=(0.01, 0.05, 0.5, 0.95, 0.99)))
    return out


def _rmse_r2(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    yt = np.asarray(y_true, dtype=np.float64).reshape(-1)
    yp = np.asarray(y_pred, dtype=np.float64).reshape(-1)
    mask = np.isfinite(yt) & np.isfinite(yp)
    if int(np.sum(mask)) == 0:
        raise ValueError("No finite samples to evaluate")
    yt = yt[mask]
    yp = yp[mask]
    return {"rmse": float(rmse_fn(yt, yp)), "r2": float(r2_fn(yt, yp))}


def _train_solar_stats_for_run(run_dir: Path, *, horizon_steps: int) -> TrainSolarStats:
    payload = _read_json(run_dir / "payload.json")
    data_run_id = str(payload["data_run_id"])
    data_ts = str(payload["data_timestamp"])

    data_run_dir = REPO_ROOT / "runs" / data_run_id
    data_payload_path = data_run_dir / "payload.json"
    if not data_payload_path.exists():
        raise FileNotFoundError(f"data_run payload.json not found: {data_payload_path}")
    data_payload = _read_json(data_payload_path)

    source_run_id = str(data_payload.get("source_data_run_id") or data_run_id)
    source_ts = str(data_payload.get("source_timestamp") or data_ts)
    source_dir = REPO_ROOT / "runs" / source_run_id

    scaler_path = source_dir / "artifacts" / "scaler_params.json"
    processed_dir = source_dir / "processed"
    train_path = processed_dir / f"train_{source_ts}.parquet"
    if not scaler_path.exists():
        raise FileNotFoundError(f"scaler_params.json not found: {scaler_path}")
    if not train_path.exists():
        raise FileNotFoundError(f"train parquet not found: {train_path}")

    scaler_params = json.loads(scaler_path.read_text())
    train_df = pd.read_parquet(train_path)
    solar_raw = inverse_transform(train_df[["solar"]], scaler_params)["solar"].to_numpy(dtype=np.float64)

    solar_p99 = float(np.nanquantile(solar_raw, 0.99))
    solar_max = float(np.nanmax(solar_raw))

    delta = pd.Series(solar_raw).diff(periods=horizon_steps).to_numpy(dtype=np.float64)
    delta_q01 = float(np.nanquantile(delta, 0.01))
    delta_q99 = float(np.nanquantile(delta, 0.99))

    return TrainSolarStats(solar_p99=solar_p99, solar_max=solar_max, delta_q01=delta_q01, delta_q99=delta_q99)


def diagnose(run_dir: Path, *, require_abs: bool) -> dict[str, Any]:
    payload_path = run_dir / "payload.json"
    artifacts = run_dir / "artifacts"
    if not payload_path.exists():
        raise FileNotFoundError(f"payload.json not found: {payload_path}")
    payload = _read_json(payload_path)

    target_col = _infer_target_col(payload)
    horizon_steps = _infer_horizon_steps(target_col)

    pred_delta_path = artifacts / "predictions_test.parquet"
    if not pred_delta_path.exists():
        raise FileNotFoundError(f"predictions_test.parquet not found: {pred_delta_path}")
    pred_delta = pd.read_parquet(pred_delta_path)
    delta_true = pred_delta["y_true"].to_numpy(dtype=np.float64)
    delta_pred = pred_delta["y_pred"].to_numpy(dtype=np.float64)

    pred_abs_path = artifacts / "predictions_test_reconstructed.parquet"
    if require_abs and not pred_abs_path.exists():
        raise FileNotFoundError(
            f"predictions_test_reconstructed.parquet not found: {pred_abs_path}. "
            "Run scripts/reconstruct_predictions.py --run <run_dir> first."
        )

    out: dict[str, Any] = {
        "run_id": str(payload.get("run_id") or run_dir.name),
        "kind": str(payload.get("kind") or "unknown"),
        "target_col": target_col,
        "horizon_steps": int(horizon_steps),
        "delta_true": _stats(delta_true),
        "delta_pred": _stats(delta_pred),
        "delta_test": _rmse_r2(delta_true, delta_pred),
    }

    train_stats = _train_solar_stats_for_run(run_dir, horizon_steps=horizon_steps)
    out["train_solar_raw"] = {
        "solar_p99": train_stats.solar_p99,
        "solar_max": train_stats.solar_max,
        "delta_q01": train_stats.delta_q01,
        "delta_q99": train_stats.delta_q99,
    }

    # Delta: clip to training q01/q99 (cheap boundedness check)
    delta_pred_clip = np.clip(delta_pred, train_stats.delta_q01, train_stats.delta_q99)
    out["delta_test_clip_train_q01_q99"] = _rmse_r2(delta_true, delta_pred_clip)

    if pred_abs_path.exists():
        pred_abs = pd.read_parquet(pred_abs_path)
        abs_true = pred_abs["y_true"].to_numpy(dtype=np.float64)
        abs_pred = pred_abs["y_pred"].to_numpy(dtype=np.float64)
        out["abs_true"] = _stats(abs_true)
        out["abs_pred"] = _stats(abs_pred)

        abs_pred_f = abs_pred[np.isfinite(abs_pred)]
        out["abs_pred_out_of_bounds"] = {
            "neg_ratio": float(np.mean(abs_pred_f < 0.0)) if abs_pred_f.size else 0.0,
            "above_train_p99_ratio": float(np.mean(abs_pred_f > train_stats.solar_p99)) if abs_pred_f.size else 0.0,
            "above_train_max_ratio": float(np.mean(abs_pred_f > train_stats.solar_max)) if abs_pred_f.size else 0.0,
        }

        # Abs: evaluate with persistence baseline (shift(h)) and show clip-to-[0,train_max].
        df = pred_abs.copy()
        df["y_base"] = df["y_true"].shift(int(horizon_steps))
        y_base = df["y_base"].to_numpy(dtype=np.float64)
        mask = np.isfinite(abs_true) & np.isfinite(abs_pred) & np.isfinite(y_base)
        if int(np.sum(mask)) == 0:
            raise ValueError("No finite samples to evaluate abs(test) with persistence baseline")
        yt = abs_true[mask]
        yp = abs_pred[mask]
        yb = y_base[mask]

        rmse_abs = float(rmse_fn(yt, yp))
        rmse_persist = float(rmse_fn(yt, yb))
        skill = float(1.0 - (rmse_abs / rmse_persist)) if rmse_persist > 0 and np.isfinite(rmse_persist) else None
        out["abs_test"] = {"rmse": rmse_abs, "r2": float(r2_fn(yt, yp)), "rmse_persist": rmse_persist, "skill": skill, "n_eval": int(np.sum(mask))}

        yp_clip = np.clip(yp, 0.0, train_stats.solar_max)
        rmse_abs_clip = float(rmse_fn(yt, yp_clip))
        skill_clip = float(1.0 - (rmse_abs_clip / rmse_persist)) if rmse_persist > 0 and np.isfinite(rmse_persist) else None
        out["abs_test_clip_0_train_max"] = {
            "rmse": rmse_abs_clip,
            "r2": float(r2_fn(yt, yp_clip)),
            "rmse_persist": rmse_persist,
            "skill": skill_clip,
            "train_max": train_stats.solar_max,
            "n_eval": int(np.sum(mask)),
        }

    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Diagnose delta_solar runs for out-of-bounds / extrapolation failure modes.")
    ap.add_argument("--run", action="append", required=True, help="Run id or path to local run dir (repeatable).")
    ap.add_argument(
        "--require-abs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require predictions_test_reconstructed.parquet to exist (default: true).",
    )
    args = ap.parse_args()

    for arg in args.run:
        run_dir = _as_run_dir(str(arg))
        if not run_dir.exists():
            raise FileNotFoundError(f"Run dir not found: {run_dir}")
        report = diagnose(run_dir, require_abs=bool(args.require_abs))
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

