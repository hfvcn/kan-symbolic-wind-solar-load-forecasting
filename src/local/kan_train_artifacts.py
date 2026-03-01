from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import numpy as np

from src.local.kan_train_core import assert_finite_dataset, tensor_stats
from src.local.run_contract import write_json


def preflight(model, dataset: dict[str, Any], *, artifacts_dir: Path) -> None:
    import torch

    write_json(Path(artifacts_dir) / "dataset_stats.json", {k: tensor_stats(v) for k, v in dataset.items()})
    assert_finite_dataset(dataset)

    with torch.no_grad():
        x0 = dataset["train_input"][: min(512, dataset["train_input"].shape[0])]
        y0 = model(x0)
        if not torch.isfinite(y0).all().item():
            write_json(Path(artifacts_dir) / "preflight_output_stats.json", {"y0": tensor_stats(y0)})
            raise RuntimeError("Model forward produced non-finite values at initialization")


def write_feature_importance_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["feature", "active_edges", "active_ratio"])
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_checkpoint(
    *,
    ckpt_path: Path,
    model,
    payload: dict[str, Any],
    feature_cols: list[str],
    target_scaler: dict[str, float] | None,
    best_prune: dict[str, float],
    sparsity: dict[str, float | int],
    model_width: list[list[int]],
) -> None:
    import torch

    ckpt = {
        "model_state": model.state_dict(),
        "payload": payload,
        "feature_cols": feature_cols,
        "target_scaler": target_scaler,
        "best_prune": best_prune,
        "sparsity": sparsity,
        "model_width": model_width,
    }
    torch.save(ckpt, ckpt_path)


def save_test_predictions(
    *,
    out_path: Path,
    model,
    test_df,
    feature_cols: list[str],
    target_col: str,
    target_scaler: dict[str, float] | None,
    device: str,
) -> None:
    import pandas as pd
    import torch

    x_test = torch.tensor(test_df[feature_cols].to_numpy(dtype=np.float32)).to(device)
    with torch.no_grad():
        pred_norm = model(x_test).detach().cpu().numpy().reshape(-1)

    y_true = test_df[str(target_col)].to_numpy(dtype=np.float64).reshape(-1)
    if target_scaler is not None:
        pred = pred_norm * float(target_scaler["std"]) + float(target_scaler["mean"])
    else:
        pred = pred_norm
    pd.DataFrame({"y_true": y_true, "y_pred": pred, "residual": pred - y_true}, index=test_df.index).to_parquet(out_path, compression="snappy")

