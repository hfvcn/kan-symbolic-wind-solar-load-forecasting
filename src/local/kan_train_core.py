from __future__ import annotations

import csv
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def pick_device(device_name: str) -> str:
    import torch

    dn = str(device_name).strip().lower()
    if dn not in {"cpu", "cuda"}:
        raise ValueError(f"device_name must be 'cpu' or 'cuda', got: {device_name!r}")
    if dn == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Requested CUDA device but torch.cuda.is_available() is False")
    return dn


def torch_env_info() -> dict[str, Any]:
    import platform
    import sys

    import torch

    info: dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch_version": str(torch.__version__),
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "torch_cuda_version": str(torch.version.cuda) if torch.version.cuda is not None else None,
    }
    if torch.cuda.is_available():
        info["cuda_device_name"] = torch.cuda.get_device_name(0)
        info["cuda_capability"] = list(torch.cuda.get_device_capability(0))
    return info


def append_metrics_row(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            w.writeheader()
        w.writerow(row)


def move_dataset_to_device(dataset: dict[str, Any], device: str) -> dict[str, Any]:
    import torch

    out: dict[str, Any] = {}
    for k, v in dataset.items():
        out[k] = v.to(device) if isinstance(v, torch.Tensor) else v
    return out


def tensor_stats(t, *, sample: int = 8192) -> dict[str, Any]:
    import torch

    if not isinstance(t, torch.Tensor):
        return {"type": str(type(t))}

    x = t.flatten()
    if x.numel() > int(sample):
        x = x[: int(sample)]
    finite = torch.isfinite(x)

    out: dict[str, Any] = {
        "shape": list(t.shape),
        "dtype": str(t.dtype),
        "device": str(t.device),
        "numel": int(t.numel()),
        "finite_frac_sample": float(finite.to(torch.float32).mean().cpu().item()) if x.numel() else 1.0,
    }
    if finite.any():
        xf = x[finite]
        out.update(
            {
                "min_sample": float(xf.min().cpu().item()),
                "max_sample": float(xf.max().cpu().item()),
                "mean_sample": float(xf.mean().cpu().item()),
                "std_sample": float(xf.std(unbiased=False).cpu().item()),
            }
        )
    return out


def assert_finite_dataset(dataset: dict[str, Any]) -> None:
    import torch

    for k, v in dataset.items():
        if isinstance(v, torch.Tensor) and not torch.isfinite(v).all().item():
            raise ValueError(f"Non-finite values found in dataset tensor: {k}")


def evaluate(model: Any, x, y_true, *, target_scaler: Optional[dict[str, float]]) -> dict[str, float]:
    import numpy as np
    import torch

    from src.kan_sr.metrics import mae, r2, rmse

    with torch.no_grad():
        pred = model(x).detach().cpu().numpy()
    y_true_np = y_true.detach().cpu().numpy()

    if target_scaler is not None:
        mean = float(target_scaler["mean"])
        std = float(target_scaler["std"])
        pred = pred * std + mean
        y_true_np = y_true_np * std + mean

    return {
        "rmse": rmse(y_true_np, pred),
        "mae": mae(y_true_np, pred),
        "r2": r2(y_true_np, pred),
    }


def fit_in_chunks(
    model: Any,
    dataset: dict[str, Any],
    *,
    stage: str,
    total_steps: int,
    chunk_steps: int,
    metrics_path: Path,
    fit_kwargs: dict[str, Any],
    save_ckpt_path: Path,
) -> None:
    import torch

    if int(total_steps) <= 0:
        return
    if int(chunk_steps) <= 0:
        raise ValueError("chunk_steps must be positive")

    done = 0
    while done < int(total_steps):
        steps = min(int(chunk_steps), int(total_steps) - done)
        fit_kwargs_chunk = dict(fit_kwargs)
        fit_kwargs_chunk["steps"] = int(steps)
        fit_kwargs_chunk["log"] = max(1, int(steps) // 5)

        hist = model.fit(dataset, **fit_kwargs_chunk)
        for i, (tl, vl, reg) in enumerate(zip(hist["train_loss"], hist["test_loss"], hist["reg"])):
            tl_f = float(tl)
            vl_f = float(vl)
            reg_f = float(reg)
            if not (math.isfinite(tl_f) and math.isfinite(vl_f) and math.isfinite(reg_f)):
                torch.save({"model_state": model.state_dict()}, save_ckpt_path.with_name(f"model_{stage}_nonfinite.pt"))
                raise RuntimeError(f"Non-finite metrics during {stage}: step={done+i} train={tl_f} val={vl_f} reg={reg_f}")
            append_metrics_row(
                metrics_path,
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "stage": stage,
                    "step": int(done + i),
                    "train_loss": tl_f,
                    "val_loss": vl_f,
                    "reg": reg_f,
                },
            )

        done += int(steps)
        torch.save({"model_state": model.state_dict()}, save_ckpt_path)
        torch.save({"model_state": model.state_dict()}, save_ckpt_path.with_name(f"{save_ckpt_path.stem}_step{done}.pt"))


def compute_feature_importance(model: Any, feature_cols: list[str]) -> list[dict[str, Any]]:
    import torch

    mask = model.state_dict().get("act_fun.0.mask")
    if mask is None:
        return []

    active = (mask != 0).to(torch.int32)
    per_feature = active.sum(dim=1).cpu().numpy().tolist()
    total_hidden = int(active.shape[1])

    rows = []
    for name, cnt in zip(feature_cols, per_feature):
        rows.append(
            {
                "feature": name,
                "active_edges": int(cnt),
                "active_ratio": float(cnt) / float(total_hidden) if total_hidden else 0.0,
            }
        )
    rows.sort(key=lambda r: (r["active_edges"], r["active_ratio"]), reverse=True)
    return rows
