#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _utc_run_id(prefix: str = "transfer") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{prefix}_{ts}"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))


def _param_count(state_dict: dict) -> int:
    import torch

    n = 0
    for v in state_dict.values():
        if isinstance(v, torch.Tensor):
            n += int(v.numel())
    return int(n)


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross-ISO transfer evaluation for a trained KAN run (Phase 8).")
    ap.add_argument("--train-run", required=True, help="Path to synced Phase-2 training run directory (runs/<id>).")
    ap.add_argument("--target-data-run", required=True, help="Path to synced Phase-1 data run directory for target ISO (runs/<id>).")
    ap.add_argument("--target-timestamp", default=None, help="Processed Parquet timestamp to use (default: latest).")
    ap.add_argument("--out-run-id", default=None, help="Output run_id under runs/ (default: auto).")
    ap.add_argument("--out-runs-dir", default="runs", help="Local runs/ directory.")
    ap.add_argument("--max-test-rows", type=int, default=None, help="Optionally truncate test rows for quick iteration.")
    args = ap.parse_args()

    started_at = datetime.now(timezone.utc)

    import torch
    from kan import KAN

    from src.data.split import inverse_transform, load_splits_from_parquet, transform
    from src.kan_sr.metrics import mae, r2, rmse

    train_run = Path(args.train_run)
    target_data_run = Path(args.target_data_run)

    ckpt_path = train_run / "checkpoint" / "model.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"KAN checkpoint not found: {ckpt_path}")

    try:
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    except TypeError:
        ckpt = torch.load(ckpt_path, map_location="cpu")
    payload = ckpt.get("payload", {}) or {}
    cfg = payload.get("cfg", {}) or {}
    feature_cols = ckpt.get("feature_cols") or payload.get("feature_cols")
    if not feature_cols:
        raise ValueError("checkpoint missing feature_cols")

    target_col = str(cfg.get("target_col", payload.get("target_col", "load")))
    target_scaler = ckpt.get("target_scaler") or payload.get("target_scaler")

    source_data_run_id = str(payload.get("data_run_id", ""))
    source_data_timestamp = payload.get("data_timestamp")
    if not source_data_run_id:
        raise ValueError("training payload missing data_run_id")

    # Load target ISO processed splits (z-scored by its own scaler).
    _train_df_t, _val_df_t, test_df_t = load_splits_from_parquet(target_data_run / "processed", timestamp=args.target_timestamp)
    if args.max_test_rows is not None and len(test_df_t) > int(args.max_test_rows):
        test_df_t = test_df_t.iloc[: int(args.max_test_rows)].copy()

    if target_col not in test_df_t.columns:
        raise ValueError(f"target column not found in target test split: {target_col}")

    # Load scalers: target ISO (to invert) and source ISO (to re-apply).
    target_scaler_params_path = target_data_run / "artifacts" / "scaler_params.json"
    if not target_scaler_params_path.exists():
        raise FileNotFoundError(f"target scaler_params.json not found: {target_scaler_params_path}")
    target_scaler_params = json.loads(target_scaler_params_path.read_text())

    # Resolve relative to train_run's parent for typical layout (runs/<id>/...).
    source_scaler_params_path = train_run.parent / source_data_run_id / "artifacts" / "scaler_params.json"
    if not source_scaler_params_path.exists():
        raise FileNotFoundError(f"source scaler_params.json not found for training data run: {source_scaler_params_path}")
    source_scaler_params = json.loads(source_scaler_params_path.read_text())

    # Convert target features back to original scale, then apply *source* scaler to match training feature space.
    x_target_orig = inverse_transform(test_df_t[feature_cols], target_scaler_params)

    # Some features (e.g., boolean flags like `is_night`) are not normalized by
    # Phase-1 scaler_params (because `normalize_features()` only normalizes numeric
    # columns). Only require *numeric* features to exist in the source scaler.
    source_feature_names = set(source_scaler_params.get("feature_names", []))
    numeric_feature_cols = [
        c
        for c in feature_cols
        if c in x_target_orig.columns and pd.api.types.is_numeric_dtype(x_target_orig[c]) and not pd.api.types.is_bool_dtype(x_target_orig[c])
    ]
    missing_in_source = [c for c in numeric_feature_cols if c not in source_feature_names]
    if missing_in_source:
        raise ValueError(
            "Some numeric feature_cols missing from source scaler_params.feature_names "
            f"(cannot apply training scaler): {missing_in_source[:10]}"
        )

    x_target_scaled_as_source = transform(x_target_orig, source_scaler_params)

    # Rebuild model with training cfg and load weights.
    in_dim = len(feature_cols)
    hidden_width = int(cfg.get("hidden_width", 10))
    hidden_mult = int(cfg.get("hidden_mult", 0))
    mult_arity = int(cfg.get("mult_arity", 2))
    grid = int(cfg.get("grid", 5))
    k = int(cfg.get("k", 3))
    grid_range_min = float(cfg.get("grid_range_min", -5.0))
    grid_range_max = float(cfg.get("grid_range_max", 5.0))

    model_width = ckpt.get("model_width") or payload.get("model_width")
    if model_width:
        width = [[int(a), int(b)] for a, b in model_width]
    else:
        sd = ckpt.get("model_state", {})
        inferred_hidden = None
        if "node_bias_0" in sd:
            inferred_hidden = int(sd["node_bias_0"].shape[0])
        elif "act_fun.0.mask" in sd:
            inferred_hidden = int(sd["act_fun.0.mask"].shape[1])
        width = [[in_dim, 0], [int(inferred_hidden or hidden_width), int(hidden_mult)], [1, 0]]

    model = KAN(
        width=width,
        grid=grid,
        k=k,
        mult_arity=mult_arity,
        grid_range=[grid_range_min, grid_range_max],
        seed=int(cfg.get("seed", 1)),
        auto_save=False,
        device="cpu",
    )
    model.load_state_dict(ckpt["model_state"], strict=True)

    X = torch.tensor(x_target_scaled_as_source.to_numpy(dtype=np.float32))
    with torch.no_grad():
        pred_norm = model(X).detach().cpu().numpy().reshape(-1)

    if target_scaler is not None:
        pred = pred_norm * float(target_scaler["std"]) + float(target_scaler["mean"])
    else:
        pred = pred_norm

    y_true = test_df_t[target_col].to_numpy(dtype=np.float64).reshape(-1)

    # Hard constraint (PIKAN): nighttime PV must be 0 (for solar target).
    if target_col == "solar" and "is_night" in x_target_orig.columns:
        night_mask = x_target_orig["is_night"].to_numpy(dtype=np.float64) > 0.5
        pred = pred.copy()
        pred[night_mask] = 0.0

    metrics = {"rmse": rmse(y_true, pred), "mae": mae(y_true, pred), "r2": r2(y_true, pred), "n": int(len(y_true))}

    out_run_id = args.out_run_id or _utc_run_id(prefix="transfer")
    out_run_dir = Path(args.out_runs_dir) / out_run_id
    artifacts_dir = out_run_dir / "artifacts"
    ckpt_dir = out_run_dir / "checkpoint"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    out_payload = {
        "run_id": out_run_id,
        "phase": "08-transfer-eval",
        "kind": "kan_transfer",
        "train_run_id": train_run.name,
        "source_data_run_id": source_data_run_id,
        "source_data_timestamp": source_data_timestamp,
        "target_data_run_id": target_data_run.name,
        "target_data_timestamp": args.target_timestamp,
        "target_col": target_col,
        "feature_cols": list(feature_cols),
        "cfg": cfg,
        "model_param_count": _param_count(ckpt.get("model_state", {})),
        "started_at": started_at.isoformat(),
    }
    _write_json(out_run_dir / "payload.json", out_payload)

    pred_df = pd.DataFrame({"y_true": y_true, "y_pred": pred, "residual": pred - y_true}, index=test_df_t.index)
    pred_df.to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")
    _write_json(artifacts_dir / "eval_test.json", metrics)

    out_payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    out_payload["eval_test"] = metrics
    _write_json(out_run_dir / "payload.json", out_payload)

    print(json.dumps({"out_run_id": out_run_id, "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
