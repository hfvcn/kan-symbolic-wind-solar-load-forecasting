"""
Symbolic extraction (Phase 3) as a Modal job.

Inputs:
  - Phase 2 run_id (KAN training) containing checkpoint/model.pt
  - Phase 1 scaler params (resolved via payload.data_run_id)

Outputs:
  /vol/runs/<run_id>/artifacts/
    edge_symbolic_report.csv
    formula.sympy.txt
    formula.tex
    formula_metrics.json
    formula_eval_test.json
"""

from __future__ import annotations

import csv
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


APP_NAME = "kan-sr-symbolic"
DEFAULT_VOLUME_NAME = os.environ.get("KAN_SR_VOLUME", "kan-sr")
VOLUME_MOUNT = "/vol"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(DEFAULT_VOLUME_NAME, create_if_missing=True)

# Include local source tree in Modal containers so `import src.*` works.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "numpy>=1.24",
        "pandas>=2.0",
        "pyarrow>=14.0",
        "scikit-learn>=1.3",
        "torch>=2.1",
        "pykan==0.2.8",
        "pyyaml>=6.0",
        "tqdm>=4.66",
        "matplotlib>=3.8",
        "sympy>=1.13.3",
    )
    .env({"PYTHONPATH": "/root/project"})
    .add_local_dir(SRC_DIR, remote_path="/root/project/src")
)


def _utc_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)


def _load_scaler_for_features(scaler_params: dict[str, Any], feature_cols: list[str]) -> dict[str, Any]:
    names = scaler_params["feature_names"]
    mean = scaler_params["mean"]
    scale = scaler_params["scale"]
    idx = {n: i for i, n in enumerate(names)}

    means: list[float] = []
    stds: list[float] = []
    missing: list[str] = []
    for c in feature_cols:
        if c not in idx:
            missing.append(c)
            means.append(0.0)
            stds.append(1.0)
        else:
            i = idx[c]
            means.append(float(mean[i]))
            stds.append(float(scale[i]))

    if missing:
        logger.warning(f"Some feature cols missing from scaler_params (using mean=0,std=1): {missing[:10]}")

    return {"mean": means, "std": stds, "missing": missing}


def _extract_symbolic_impl(
    train_run_id: str,
    *,
    run_id: str | None,
    r2_threshold: float,
    weight_simple: float,
    fix_below_threshold_to_zero: bool,
    sample_rows: int,
    lib: list[str] | None,
    device_name: str,
) -> dict[str, Any]:
    import numpy as np
    import pandas as pd
    import sympy as sp
    import torch
    from kan import KAN

    from src.data.split import load_splits_from_parquet
    from src.kan_sr.metrics import mae, r2, rmse
    from src.kan_sr.separability import detect_separability
    from src.kan_sr.symbolic import (
        DEFAULT_SYMBOLIC_LIB,
        build_symbolic_formula,
        evaluate_symbolic_formula,
        extract_symbolic_edges,
        sympy_complexity,
    )

    device_s = str(device_name).strip().lower()
    if device_s not in {"cpu", "cuda"}:
        raise ValueError(f"device_name must be 'cpu' or 'cuda', got: {device_name!r}")
    if device_s == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Requested CUDA device but torch.cuda.is_available() is False")

    run_id = run_id or _utc_run_id()
    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    artifacts_dir = run_dir / "artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Load Phase 2 checkpoint
    ckpt_path = Path(VOLUME_MOUNT) / "runs" / train_run_id / "checkpoint" / "model.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Phase 2 checkpoint not found: {ckpt_path}")

    try:
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    except TypeError:
        ckpt = torch.load(ckpt_path, map_location="cpu")
    payload = ckpt.get("payload", {})
    feature_cols = ckpt["feature_cols"]
    target_scaler = ckpt.get("target_scaler")
    cfg = payload.get("cfg", {})

    data_run_id = payload["data_run_id"]
    data_timestamp = payload["data_timestamp"]

    # Load Phase 1 scaler params for input de-normalization in formula
    scaler_path = Path(VOLUME_MOUNT) / "runs" / data_run_id / "artifacts" / "scaler_params.json"
    scaler_params = json.loads(Path(scaler_path).read_text())
    input_norm = _load_scaler_for_features(scaler_params, feature_cols)
    output_norm = None
    if target_scaler is not None:
        output_norm = {"mean": [float(target_scaler["mean"])], "std": [float(target_scaler["std"])]}

    # Rebuild model and load weights
    in_dim = len(feature_cols)
    hidden_width = int(cfg.get("hidden_width", 10))
    hidden_mult = int(cfg.get("hidden_mult", 0))
    mult_arity = int(cfg.get("mult_arity", 2))
    grid = int(cfg.get("grid", 5))
    k = int(cfg.get("k", 3))
    grid_range_min = float(cfg.get("grid_range_min", -5.0))
    grid_range_max = float(cfg.get("grid_range_max", 5.0))

    # Prefer effective (post-prune) width stored by Phase 2; otherwise infer from state_dict.
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
        device=device_s,
    )
    model.load_state_dict(ckpt["model_state"], strict=True)

    # Load Phase 1 test split for evaluation, and train split for activation sampling.
    processed_dir = Path(VOLUME_MOUNT) / "runs" / data_run_id / "processed"
    train_df, _val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=data_timestamp)

    if sample_rows is not None and len(train_df) > sample_rows:
        train_df = train_df.sample(n=sample_rows, random_state=1).sort_index()

    # Populate internal activations for symbolic fitting.
    x_sample = torch.tensor(train_df[feature_cols].to_numpy(dtype=np.float32), device=device_s)
    _ = model(x_sample)

    # Per-edge suggestions + optional fixing.
    edge_fits = extract_symbolic_edges(
        model,
        lib=lib or DEFAULT_SYMBOLIC_LIB,
        r2_threshold=r2_threshold,
        weight_simple=weight_simple,
        fix_below_threshold_to_zero=fix_below_threshold_to_zero,
    )

    # Build final formula (SymPy) with de-normalization.
    expr = build_symbolic_formula(
        model,
        feature_cols=feature_cols,
        input_normalizer=input_norm,
        output_normalizer=output_norm,
    )

    # Evaluate extracted formula on *original-scale* inputs.
    # Note: `build_symbolic_formula(..., input_normalizer=...)` produces a formula
    # that expects unnormalized feature values (same names as feature_cols).
    from src.data.split import inverse_transform

    test_x_orig = inverse_transform(test_df[feature_cols], scaler_params)
    pred = evaluate_symbolic_formula(expr, feature_cols=feature_cols, x_df=test_x_orig)

    # Hard constraint (PIKAN): nighttime PV must be 0 (for solar target).
    if payload["cfg"]["target_col"] == "solar" and "is_night" in test_df.columns:
        try:
            is_night_orig = inverse_transform(test_df[["is_night"]], scaler_params)["is_night"].to_numpy(dtype=np.float64)
            pred = pred.copy()
            pred[is_night_orig > 0.5] = 0.0
        except Exception:  # noqa: BLE001
            pass

    y_true = test_df[payload["cfg"]["target_col"]].to_numpy(dtype=np.float64)

    mask = np.isfinite(pred)
    pred = pred[mask]
    y_true = y_true[mask]

    eval_metrics = {"rmse": rmse(y_true, pred), "mae": mae(y_true, pred), "r2": r2(y_true, pred), "n_eval": int(len(y_true))}

    # Save artifacts
    report_path = artifacts_dir / "edge_symbolic_report.csv"
    with open(report_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(edge_fits[0].as_dict().keys()) if edge_fits else ["layer", "i", "j"])
        w.writeheader()
        for fit in edge_fits:
            w.writerow(fit.as_dict())

    (artifacts_dir / "formula.sympy.txt").write_text(str(expr))
    (artifacts_dir / "formula.tex").write_text(sp.latex(expr))
    _write_json(artifacts_dir / "formula_metrics.json", sympy_complexity(expr))
    _write_json(artifacts_dir / "formula_eval_test.json", eval_metrics)
    _write_json(artifacts_dir / "separability.json", detect_separability(expr).as_dict())

    # Save full test prediction series (including NaN where evaluation is invalid)
    pred_full = evaluate_symbolic_formula(expr, feature_cols=feature_cols, x_df=test_x_orig)
    if payload["cfg"]["target_col"] == "solar" and "is_night" in test_df.columns:
        try:
            is_night_orig = inverse_transform(test_df[["is_night"]], scaler_params)["is_night"].to_numpy(dtype=np.float64)
            pred_full = pred_full.copy()
            pred_full[is_night_orig > 0.5] = 0.0
        except Exception:  # noqa: BLE001
            pass
    pred_df = pd.DataFrame(
        {
            "y_true": test_df[payload["cfg"]["target_col"]].to_numpy(dtype=np.float64),
            "y_pred": pred_full,
        },
        index=test_df.index,
    )
    pred_df["residual"] = pred_df["y_pred"] - pred_df["y_true"]
    pred_df.to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")

    out_payload = {
        "run_id": run_id,
        "status": "completed",
        "train_run_id": train_run_id,
        "data_run_id": data_run_id,
        "data_timestamp": data_timestamp,
        "r2_threshold": float(r2_threshold),
        "weight_simple": float(weight_simple),
        "fix_below_threshold_to_zero": bool(fix_below_threshold_to_zero),
        "sample_rows": int(sample_rows),
        "lib": list(lib or DEFAULT_SYMBOLIC_LIB),
        "eval_test": eval_metrics,
        "feature_cols": feature_cols,
        "target_col": payload["cfg"]["target_col"],
        "device": device_s,
        "artifacts_dir": str(artifacts_dir),
    }
    _write_json(run_dir / "payload.json", out_payload)
    volume.commit()
    return out_payload


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=2 * 3600)
def extract_symbolic(
    train_run_id: str,
    *,
    run_id: str | None = None,
    r2_threshold: float = 0.99,
    weight_simple: float = 0.9,
    fix_below_threshold_to_zero: bool = False,
    sample_rows: int = 10_000,
    lib: list[str] | None = None,
) -> dict[str, Any]:
    return _extract_symbolic_impl(
        train_run_id,
        run_id=run_id,
        r2_threshold=r2_threshold,
        weight_simple=weight_simple,
        fix_below_threshold_to_zero=fix_below_threshold_to_zero,
        sample_rows=sample_rows,
        lib=lib,
        device_name="cpu",
    )


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=2 * 3600, gpu="T4")
def extract_symbolic_gpu(
    train_run_id: str,
    *,
    run_id: str | None = None,
    r2_threshold: float = 0.99,
    weight_simple: float = 0.9,
    fix_below_threshold_to_zero: bool = False,
    sample_rows: int = 10_000,
    lib: list[str] | None = None,
) -> dict[str, Any]:
    return _extract_symbolic_impl(
        train_run_id,
        run_id=run_id,
        r2_threshold=r2_threshold,
        weight_simple=weight_simple,
        fix_below_threshold_to_zero=fix_below_threshold_to_zero,
        sample_rows=sample_rows,
        lib=lib,
        device_name="cuda",
    )


@app.local_entrypoint()
def main(
    train_run_id: str,
    run_id: str = "",
    r2_threshold: float = 0.99,
    weight_simple: float = 0.9,
    fix_below_threshold_to_zero: bool = False,
    sample_rows: int = 10_000,
    lib: str = "default",
    use_gpu: bool = False,
) -> None:
    lib_list = None
    lib_s = str(lib).strip().lower()
    if lib_s not in {"", "default"}:
        lib_list = [s.strip() for s in str(lib).split(",") if s.strip()]
    run_id_opt = run_id.strip() or None
    fn = extract_symbolic_gpu if use_gpu else extract_symbolic
    result = fn.remote(
        train_run_id,
        run_id=run_id_opt,
        r2_threshold=r2_threshold,
        weight_simple=weight_simple,
        fix_below_threshold_to_zero=fix_below_threshold_to_zero,
        sample_rows=sample_rows,
        lib=lib_list,
    )
    print(json.dumps(result, indent=2))
