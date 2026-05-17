from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.kan_sr.dataset import fit_target_scaler
from src.kan_sr.metrics import mae, r2, rmse


@dataclass(frozen=True)
class TorchTrainResult:
    best_val_rmse: float
    val_metrics: dict[str, float]
    test_metrics: dict[str, float]
    target_scaler: dict[str, float]


def _append_metrics_row(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            w.writeheader()
        w.writerow(row)


def _eval_model(model: nn.Module, x: torch.Tensor, y: torch.Tensor, scaler: dict[str, float]) -> dict[str, float]:
    model.eval()
    with torch.no_grad():
        pred = model(x).detach().cpu().numpy().reshape(-1)
    y_true = y.detach().cpu().numpy().reshape(-1)

    mean = float(scaler["mean"])
    std = float(scaler["std"])
    pred = pred * std + mean
    y_true = y_true * std + mean
    return {"rmse": rmse(y_true, pred), "mae": mae(y_true, pred), "r2": r2(y_true, pred)}


def train_mlp_regressor(
    *,
    model: nn.Module,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    device: str,
    metrics_path: Path,
    lr: float = 1e-3,
    batch_size: int = 512,
    epochs: int = 50,
    patience: int = 8,
    log_every: int = 50,
) -> TorchTrainResult:
    scaler = fit_target_scaler(y_train).as_dict()
    y_train_s = (y_train - scaler["mean"]) / scaler["std"]
    y_val_s = (y_val - scaler["mean"]) / scaler["std"]
    y_test_s = (y_test - scaler["mean"]) / scaler["std"]

    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    train_ds = TensorDataset(torch.tensor(x_train, dtype=torch.float32), torch.tensor(y_train_s, dtype=torch.float32))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    x_val_t = torch.tensor(x_val, dtype=torch.float32).to(device)
    y_val_t = torch.tensor(y_val_s, dtype=torch.float32).to(device)
    x_test_t = torch.tensor(x_test, dtype=torch.float32).to(device)
    y_test_t = torch.tensor(y_test_s, dtype=torch.float32).to(device)

    best_state = None
    best_val = math.inf
    bad = 0
    early_stop = int(patience) > 0
    log_every_s = int(log_every)
    if log_every_s <= 0:
        raise ValueError("log_every must be positive")

    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach().cpu().item()))

        val_metrics = _eval_model(model, x_val_t, y_val_t, scaler)
        if epoch == 1 or epoch == epochs or (epoch % log_every_s == 0):
            print(
                (
                    f"[torch_train] device={device} epoch={epoch}/{epochs} "
                    f"train_loss={float(np.mean(losses)) if losses else float('nan'):.6g} "
                    f"val_rmse={float(val_metrics['rmse']):.6g} "
                    f"val_r2={float(val_metrics['r2']):.6g}"
                ),
                flush=True,
            )
        _append_metrics_row(
            metrics_path,
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "epoch": epoch,
                "train_loss": float(np.mean(losses)) if losses else float("nan"),
                **{f"val_{k}": float(v) for k, v in val_metrics.items()},
            },
        )

        if val_metrics["rmse"] < best_val:
            best_val = float(val_metrics["rmse"])
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            bad = 0
        elif early_stop:
            bad += 1
            if bad >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state, strict=True)

    val_metrics = _eval_model(model, x_val_t, y_val_t, scaler)
    test_metrics = _eval_model(model, x_test_t, y_test_t, scaler)
    return TorchTrainResult(
        best_val_rmse=float(best_val),
        val_metrics={k: float(v) for k, v in val_metrics.items()},
        test_metrics={k: float(v) for k, v in test_metrics.items()},
        target_scaler=scaler,
    )


def make_lstm_sequences(
    x: np.ndarray,
    y: np.ndarray,
    *,
    seq_len: int,
) -> tuple[np.ndarray, np.ndarray]:
    if seq_len <= 1:
        raise ValueError("seq_len must be > 1")
    if len(x) != len(y):
        raise ValueError("x and y must have same length")
    if len(x) < seq_len:
        raise ValueError("not enough rows for seq_len")

    xs = []
    ys = []
    for t in range(seq_len - 1, len(x)):
        xs.append(x[t - seq_len + 1 : t + 1])
        ys.append(y[t])
    return np.stack(xs, axis=0), np.stack(ys, axis=0)
