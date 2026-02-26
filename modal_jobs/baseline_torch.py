"""
Torch baselines (Phase 4): MLP + LSTM.

Outputs:
  /vol/runs/<run_id>/
    payload.json
    metrics.csv
    checkpoint/model.pt
    artifacts/eval_test.json
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import modal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


APP_NAME = "kan-sr-baselines-torch"
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
        "scikit-learn>=1.3",
        "pyarrow>=14.0",
        "torch>=2.1",
        "tqdm>=4.66",
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


def _estimate_kan_param_count_from_checkpoint(ckpt_path: Path) -> int:
    import torch

    try:
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    except TypeError:
        ckpt = torch.load(ckpt_path, map_location="cpu")
    state = ckpt["model_state"]
    total = 0
    for k, v in state.items():
        if k.endswith(".mask"):
            continue
        if hasattr(v, "numel"):
            total += int(v.numel())
    return int(total)


def _pick_mlp_hidden_for_param_target(input_dim: int, target_params: int) -> int:
    # params ~= input_dim*h + h (bias) + h*1 + 1
    denom = input_dim + 2
    h = max(4, int(round((target_params - 1) / max(1, denom))))
    return h


def _pick_lstm_hidden_for_param_target(input_dim: int, target_params: int, max_h: int = 512) -> int:
    # One-layer LSTM params: 4*(D*H + H*H + H) + (H*1 + 1)
    best_h = 16
    best_diff = float("inf")
    for h in range(8, max_h + 1, 4):
        params = 4 * (input_dim * h + h * h + h) + (h + 1)
        diff = abs(params - target_params)
        if diff < best_diff:
            best_diff = diff
            best_h = h
    return int(best_h)


@dataclass(frozen=True)
class BaselineConfig:
    model_type: str = "mlp"  # mlp | lstm
    target_col: str = "load"
    seq_len: int = 48
    epochs: int = 50


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=6 * 3600)
def run_baseline(
    data_run_id: str,
    *,
    data_timestamp: str | None = None,
    run_id: str | None = None,
    cfg: BaselineConfig = BaselineConfig(),
    match_kan_run_id: str | None = None,
    lag_steps: list[int] | None = None,
    max_train_rows: int | None = 200_000,
) -> dict[str, Any]:
    import numpy as np
    import torch

    from src.baselines.torch_models import LSTMRegressor, MLPRegressor
    from src.baselines.torch_training import make_lstm_sequences, train_mlp_regressor
    from src.data.split import load_splits_from_parquet
    from src.kan_sr.dataset import pick_feature_columns

    run_id = run_id or _utc_run_id()
    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    ckpt_dir = run_dir / "checkpoint"
    artifacts_dir = run_dir / "artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = run_dir / "metrics.csv"
    payload_path = run_dir / "payload.json"

    processed_dir = Path(VOLUME_MOUNT) / "runs" / data_run_id / "processed"
    train_df, val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=data_timestamp)

    if max_train_rows is not None and len(train_df) > max_train_rows:
        train_df = train_df.iloc[:max_train_rows].copy()
        logger.info(f"Downsampled train_df to first {max_train_rows} rows for baseline speed")

    lag_steps = lag_steps or [1, 12, 48]
    feature_cols = pick_feature_columns(train_df, target_col=cfg.target_col, lag_steps=lag_steps)

    # Parameter matching (optional)
    target_param_count = None
    if match_kan_run_id is not None:
        kan_ckpt = Path(VOLUME_MOUNT) / "runs" / match_kan_run_id / "checkpoint" / "model.pt"
        if kan_ckpt.exists():
            target_param_count = _estimate_kan_param_count_from_checkpoint(kan_ckpt)
            logger.info(f"Matching baseline params to KAN checkpoint param count: {target_param_count}")
        else:
            logger.warning(f"KAN checkpoint not found for param matching: {kan_ckpt}")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    X_train = train_df[feature_cols].to_numpy(dtype=np.float32)
    y_train = train_df[[cfg.target_col]].to_numpy(dtype=np.float32)
    X_val = val_df[feature_cols].to_numpy(dtype=np.float32)
    y_val = val_df[[cfg.target_col]].to_numpy(dtype=np.float32)
    X_test = test_df[feature_cols].to_numpy(dtype=np.float32)
    y_test = test_df[[cfg.target_col]].to_numpy(dtype=np.float32)

    payload = {
        "run_id": run_id,
        "phase": "04-baselines-torch",
        "cfg": asdict(cfg),
        "data_run_id": data_run_id,
        "data_timestamp": data_timestamp,
        "feature_cols": feature_cols,
        "lag_steps": list(lag_steps),
        "match_kan_run_id": match_kan_run_id,
        "target_param_count": target_param_count,
        "device": device,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(payload_path, payload)
    volume.commit()

    if cfg.model_type == "mlp":
        hidden = 64
        if target_param_count is not None:
            hidden = _pick_mlp_hidden_for_param_target(len(feature_cols), target_param_count)

        model = MLPRegressor(input_dim=len(feature_cols), hidden_dim=hidden, dropout=0.1)
        payload["model_hidden_dim"] = int(hidden)
        payload["model_param_count"] = int(sum(p.numel() for p in model.parameters() if p.requires_grad))
        result = train_mlp_regressor(
            model=model,
            x_train=X_train,
            y_train=y_train,
            x_val=X_val,
            y_val=y_val,
            x_test=X_test,
            y_test=y_test,
            device=device,
            metrics_path=metrics_path,
            epochs=cfg.epochs,
        )

        torch.save({"model_state": model.state_dict(), "payload": payload}, ckpt_dir / "model.pt")
        _write_json(artifacts_dir / "eval_test.json", result.test_metrics)
        _write_json(artifacts_dir / "target_scaler.json", result.target_scaler)

        # Save test predictions for downstream evaluation/plots
        mean = float(result.target_scaler["mean"])
        std = float(result.target_scaler["std"])
        with torch.no_grad():
            pred_norm = model(torch.tensor(X_test, dtype=torch.float32).to(device)).detach().cpu().numpy().reshape(-1)
        pred = pred_norm * std + mean
        y_true = y_test.reshape(-1).astype("float64")

        # Hard constraint (PIKAN): nighttime PV must be 0 (for solar target).
        if cfg.target_col == "solar" and "is_night" in test_df.columns:
            try:
                from src.data.split import inverse_transform

                scaler_params = json.loads(
                    (Path(VOLUME_MOUNT) / "runs" / data_run_id / "artifacts" / "scaler_params.json").read_text()
                )
                is_night_orig = inverse_transform(test_df[["is_night"]], scaler_params)["is_night"].to_numpy(dtype=np.float64)
                pred = pred.copy()
                pred[is_night_orig > 0.5] = 0.0
            except Exception:  # noqa: BLE001
                pass
        import pandas as pd

        pd.DataFrame(
            {"y_true": y_true, "y_pred": pred, "residual": pred - y_true},
            index=test_df.index,
        ).to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")

    elif cfg.model_type == "lstm":
        # Build sequences from non-lag features for a clean baseline.
        seq_cols = [c for c in feature_cols if "_lag_" not in c]
        if not seq_cols:
            raise ValueError("No sequence features selected (all selected features are lag columns)")

        X_train_s, y_train_s = make_lstm_sequences(train_df[seq_cols].to_numpy(dtype=np.float32), y_train, seq_len=cfg.seq_len)
        X_val_s, y_val_s = make_lstm_sequences(val_df[seq_cols].to_numpy(dtype=np.float32), y_val, seq_len=cfg.seq_len)
        X_test_s, y_test_s = make_lstm_sequences(test_df[seq_cols].to_numpy(dtype=np.float32), y_test, seq_len=cfg.seq_len)

        hidden = 64
        if target_param_count is not None:
            hidden = _pick_lstm_hidden_for_param_target(len(seq_cols), target_param_count)

        model = LSTMRegressor(input_dim=len(seq_cols), hidden_size=hidden, num_layers=1, dropout=0.0)
        payload["model_hidden_dim"] = int(hidden)
        payload["model_param_count"] = int(sum(p.numel() for p in model.parameters() if p.requires_grad))
        # Reuse the MLP trainer with flattened batches is not correct; do a simple training loop inline.
        from src.kan_sr.dataset import fit_target_scaler
        from src.kan_sr.metrics import mae, r2, rmse
        import csv

        scaler = fit_target_scaler(y_train_s).as_dict()
        y_train_n = (y_train_s - scaler["mean"]) / scaler["std"]
        y_val_n = (y_val_s - scaler["mean"]) / scaler["std"]
        y_test_n = (y_test_s - scaler["mean"]) / scaler["std"]

        model = model.to(device)
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss_fn = torch.nn.MSELoss()

        def eval_np(xb: np.ndarray, yb: np.ndarray) -> dict[str, float]:
            model.eval()
            with torch.no_grad():
                pred = model(torch.tensor(xb, dtype=torch.float32).to(device)).detach().cpu().numpy().reshape(-1)
            true = yb.reshape(-1)
            pred = pred * scaler["std"] + scaler["mean"]
            true = true * scaler["std"] + scaler["mean"]
            return {"rmse": rmse(true, pred), "mae": mae(true, pred), "r2": r2(true, pred)}

        # Simple epoch loop
        best_state = None
        best_val = float("inf")
        patience = 8
        bad = 0

        for epoch in range(1, cfg.epochs + 1):
            model.train()
            # mini-batch
            idx = np.random.permutation(len(X_train_s))
            for start in range(0, len(idx), 256):
                sl = idx[start : start + 256]
                xb = torch.tensor(X_train_s[sl], dtype=torch.float32).to(device)
                yb = torch.tensor(y_train_n[sl], dtype=torch.float32).to(device)
                opt.zero_grad()
                pred = model(xb)
                loss = loss_fn(pred, yb)
                loss.backward()
                opt.step()

            val_metrics = eval_np(X_val_s, y_val_n)
            # write metrics
            is_new = not metrics_path.exists()
            with open(metrics_path, "a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["ts", "epoch", "val_rmse", "val_mae", "val_r2"])
                if is_new:
                    w.writeheader()
                w.writerow(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "epoch": epoch,
                        "val_rmse": float(val_metrics["rmse"]),
                        "val_mae": float(val_metrics["mae"]),
                        "val_r2": float(val_metrics["r2"]),
                    }
                )

            if val_metrics["rmse"] < best_val:
                best_val = float(val_metrics["rmse"])
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                bad = 0
            else:
                bad += 1
                if bad >= patience:
                    break

        if best_state is not None:
            model.load_state_dict(best_state, strict=True)

        test_metrics = eval_np(X_test_s, y_test_n)
        torch.save({"model_state": model.state_dict(), "payload": payload}, ckpt_dir / "model.pt")
        _write_json(artifacts_dir / "eval_test.json", test_metrics)
        _write_json(artifacts_dir / "target_scaler.json", scaler)

        # Save test predictions (aligned to sequence end timestamps)
        with torch.no_grad():
            pred_norm = model(torch.tensor(X_test_s, dtype=torch.float32).to(device)).detach().cpu().numpy().reshape(-1)
        pred = pred_norm * scaler["std"] + scaler["mean"]
        y_true = y_test_s.reshape(-1).astype("float64")
        import pandas as pd

        ts_index = test_df.index[cfg.seq_len - 1 :]
        if cfg.target_col == "solar" and "is_night" in test_df.columns:
            try:
                from src.data.split import inverse_transform

                scaler_params = json.loads(
                    (Path(VOLUME_MOUNT) / "runs" / data_run_id / "artifacts" / "scaler_params.json").read_text()
                )
                is_night_orig = inverse_transform(test_df[["is_night"]], scaler_params)["is_night"].to_numpy(dtype=np.float64)
                night_mask = is_night_orig[cfg.seq_len - 1 :] > 0.5
                pred = pred.copy()
                pred[night_mask] = 0.0
            except Exception:  # noqa: BLE001
                pass
        pd.DataFrame(
            {"y_true": y_true, "y_pred": pred, "residual": pred - y_true},
            index=ts_index,
        ).to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")

    else:
        raise ValueError(f"Unknown model_type: {cfg.model_type}")

    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    _write_json(payload_path, payload)
    volume.commit()

    return {"run_id": run_id, "status": "completed", "model_type": cfg.model_type, "artifacts_dir": str(artifacts_dir)}


@app.local_entrypoint()
def main(
    data_run_id: str,
    model_type: str = "mlp",
    target: str = "load",
    match_kan_run_id: Optional[str] = None,
) -> None:
    cfg = BaselineConfig(model_type=model_type, target_col=target)
    result = run_baseline.remote(data_run_id, cfg=cfg, match_kan_run_id=match_kan_run_id)
    print(json.dumps(result, indent=2))
