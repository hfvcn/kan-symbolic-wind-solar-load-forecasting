"""
KAN training + sparsification (Phase 2) as a Modal job.

Outputs (per MODAL.md contract) to:
  /vol/runs/<run_id>/
    payload.json
    metrics.csv
    checkpoint/model.pt
    artifacts/
      sparsity.json
      feature_importance.csv
      eval_unpruned.json
      eval_pruned.json
"""

from __future__ import annotations

import csv
import json
import logging
import os
import time
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


APP_NAME = "kan-sr-train-kan"
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
        # core
        "numpy>=1.24",
        "pandas>=2.0",
        "scikit-learn>=1.3",
        "pyarrow>=14.0",
        # KAN
        "torch>=2.1",
        "pykan==0.2.8",
        "pyyaml>=6.0",
        "tqdm>=4.66",
        "matplotlib>=3.8",
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


def _append_metrics_row(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            w.writeheader()
        w.writerow(row)


def _load_processed_splits(processed_dir: Path, timestamp: Optional[str] = None) -> tuple[Any, Any, Any, str]:
    from src.data.split import load_splits_from_parquet

    train, val, test = load_splits_from_parquet(processed_dir, timestamp=timestamp)
    if timestamp is None:
        # load_splits_from_parquet logs and infers; re-derive for payload
        train_files = sorted(processed_dir.glob("train_*.parquet"))
        inferred = train_files[-1].stem.replace("train_", "")
        return train, val, test, inferred
    return train, val, test, timestamp


def _evaluate(model: Any, x, y_true, *, target_scaler: Optional[dict[str, float]] = None) -> dict[str, float]:
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


def _torch_env_info() -> dict[str, Any]:
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
    try:
        info["cudnn_version"] = torch.backends.cudnn.version()
    except Exception:  # noqa: BLE001
        info["cudnn_version"] = None

    if torch.cuda.is_available():
        try:
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
            info["cuda_capability"] = list(torch.cuda.get_device_capability(0))
        except Exception:  # noqa: BLE001
            pass

    return info


def _tensor_stats(t, *, sample: int = 8192) -> dict[str, Any]:
    import torch

    if not isinstance(t, torch.Tensor):
        return {"type": str(type(t))}
    x = t
    if x.numel() > sample:
        x = x.flatten()[:sample]
    x = x.detach()
    finite = torch.isfinite(x)
    finite_frac = float(finite.to(torch.float32).mean().cpu().item()) if x.numel() else 1.0
    out: dict[str, Any] = {
        "shape": list(t.shape),
        "dtype": str(t.dtype),
        "device": str(t.device),
        "numel": int(t.numel()),
        "finite_frac_sample": finite_frac,
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


def _assert_finite_dataset(dataset: dict[str, Any]) -> None:
    import torch

    for k, v in dataset.items():
        if not isinstance(v, torch.Tensor):
            continue
        if not torch.isfinite(v).all().item():
            raise ValueError(f"Non-finite values found in dataset tensor: {k}")


def _compute_feature_importance(model: Any, feature_cols: list[str]) -> list[dict[str, Any]]:
    """
    Simple importance proxy: active edges from input -> first hidden layer.
    """
    import torch

    sd = model.state_dict()
    mask = None
    for k, v in sd.items():
        if k == "act_fun.0.mask":
            mask = v
            break
    if mask is None:
        return []
    # mask shape: [in_dim, hidden_dim]
    active = (mask != 0).to(torch.int32)
    per_feature = active.sum(dim=1).cpu().numpy().tolist()
    total_hidden = int(active.shape[1])

    rows: list[dict[str, Any]] = []
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


@dataclass(frozen=True)
class TrainConfig:
    target_col: str = "load"
    grid_range_min: float = -5.0
    grid_range_max: float = 5.0
    hidden_width: int = 10
    hidden_layers: tuple[int, ...] | None = None
    grid: int = 5
    k: int = 3
    seed: int = 1
    hidden_mult: int = 0
    mult_arity: int = 2

    # training schedule
    warmup_steps: int = 200
    sparsify_steps: int = 800
    refine_steps: int = 200

    warmup_lr: float = 0.01
    sparsify_lr: float = 0.005
    refine_lr: float = 0.5  # LBFGS default in KAN

    # regularization (KAN.fit args)
    sparsify_lamb: float = 0.01
    sparsify_lamb_l1: float = 1.0
    sparsify_lamb_entropy: float = 2.0
    sparsify_lamb_coef: float = 0.0
    sparsify_lamb_coefdiff: float = 0.0

    # pruning targets
    target_pruned_ratio: float = 0.8
    max_rmse_degrade_ratio: float = 1.1  # within 10%


def _move_dataset_to_device(dataset: dict[str, Any], device: str) -> dict[str, Any]:
    import torch

    out: dict[str, Any] = {}
    for k, v in dataset.items():
        if isinstance(v, torch.Tensor):
            out[k] = v.to(device)
        else:
            out[k] = v
    return out


def _fit_in_chunks(
    model: Any,
    dataset: dict[str, Any],
    *,
    stage: str,
    total_steps: int,
    chunk_steps: int,
    metrics_path: Path,
    fit_kwargs: dict[str, Any],
    save_ckpt_path: Path,
    vol: modal.Volume,
) -> None:
    """
    Run `KAN.fit()` in chunks so we can checkpoint + commit regularly.
    """
    import math
    import time

    import torch

    if total_steps <= 0:
        return
    if chunk_steps <= 0:
        raise ValueError("chunk_steps must be positive")

    done = 0
    while done < total_steps:
        steps = min(chunk_steps, total_steps - done)
        # Ensure log is never 0 (KAN.fit divides by log)
        fit_kwargs_chunk = dict(fit_kwargs)
        fit_kwargs_chunk["steps"] = steps
        fit_kwargs_chunk["log"] = max(1, steps // 5)

        t0 = time.time()
        hist = model.fit(dataset, **fit_kwargs_chunk)
        dt_s = float(time.time() - t0)

        last_metrics: tuple[float, float, float] | None = None
        for i, (tl, vl, reg) in enumerate(zip(hist["train_loss"], hist["test_loss"], hist["reg"])):
            tl_f = float(tl)
            vl_f = float(vl)
            reg_f = float(reg)
            last_metrics = (tl_f, vl_f, reg_f)
            if not (math.isfinite(tl_f) and math.isfinite(vl_f) and math.isfinite(reg_f)):
                torch.save({"model_state": model.state_dict()}, save_ckpt_path.with_name(f"model_{stage}_nonfinite.pt"))
                vol.commit()
                raise RuntimeError(
                    f"Non-finite metrics detected during {stage}: step={done+i} train_loss={tl_f} val_loss={vl_f} reg={reg_f}"
                )
            _append_metrics_row(
                metrics_path,
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "stage": stage,
                    "step": done + i,
                    "train_loss": tl_f,
                    "val_loss": vl_f,
                    "reg": reg_f,
                },
            )

        done += steps

        # Always write a "latest" checkpoint for the stage, plus a step-stamped snapshot.
        torch.save({"model_state": model.state_dict()}, save_ckpt_path)
        snap_path = save_ckpt_path.with_name(f"{save_ckpt_path.stem}_step{done}.pt")
        torch.save({"model_state": model.state_dict()}, snap_path)
        vol.commit()

        if last_metrics is not None:
            tl_f, vl_f, reg_f = last_metrics
            print(
                (
                    f"[kan_fit] stage={stage} done={done}/{total_steps} "
                    f"chunk_steps={steps} chunk_s={dt_s:.1f} "
                    f"train_loss={tl_f:.6g} val_loss={vl_f:.6g} reg={reg_f:.6g}"
                ),
                flush=True,
            )

def _train_kan_impl(
    data_run_id: str,
    *,
    device_name: str,
    data_timestamp: Optional[str] = None,
    run_id: Optional[str] = None,
    kind: Optional[str] = None,
    cfg: TrainConfig = TrainConfig(),
    include_base: bool = True,
    include_groups: Optional[list[str]] = None,
    lag_series: Optional[list[str]] = None,
    lag_steps: Optional[list[int]] = None,
    max_train_rows: Optional[int] = 50_000,
    warmup_update_grid: bool = True,
) -> dict[str, Any]:
    """
    Train a KAN model and prune to high sparsity.

    Args:
        data_run_id: Phase 1 run_id that contains processed Parquet splits.
        device_name: "cpu" or "cuda".
        data_timestamp: Optional timestamp for processed Parquet versioning.
        run_id: Optional fixed run id for resuming.
        kind: Optional run label to store in payload.json (e.g., ablation tag).
        cfg: Training hyperparameters.
        include_base: Whether to include base (non-target) cols among (load, wind, solar).
        include_groups: Feature group names (from src.data.features.get_feature_groups).
        lag_series: Series to generate lag features for (e.g., load, wind, solar).
        lag_steps: Lag feature subset (default [1,12,48]).
        max_train_rows: Optional cap for quick iteration / smoke training.
    """
    import numpy as np
    import pandas as pd
    import torch
    from kan import KAN

    from src.kan_sr.dataset import build_kan_dataset, pick_feature_columns
    from src.kan_sr.prune import prune_kan_model
    from src.kan_sr.sparsity import compute_edge_sparsity

    if device_name not in {"cpu", "cuda"}:
        raise ValueError(f"device_name must be 'cpu' or 'cuda', got: {device_name}")
    if device_name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Requested CUDA device but torch.cuda.is_available() is False")

    run_id = run_id or _utc_run_id()
    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    checkpoint_dir = run_dir / "checkpoint"
    artifacts_dir = run_dir / "artifacts"

    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = run_dir / "metrics.csv"
    payload_path = run_dir / "payload.json"

    data_processed_dir = Path(VOLUME_MOUNT) / "runs" / data_run_id / "processed"
    if not data_processed_dir.exists():
        raise FileNotFoundError(f"Processed dir not found: {data_processed_dir}")

    train_df, val_df, test_df, resolved_ts = _load_processed_splits(data_processed_dir, timestamp=data_timestamp)

    if max_train_rows is not None and len(train_df) > max_train_rows:
        train_df = train_df.iloc[:max_train_rows].copy()
        logger.info(f"Downsampled train_df to first {max_train_rows} rows for iteration")

    if include_groups is None:
        include_groups = ["meteorology", "solar", "cyclic"]
    if lag_series is None:
        lag_series = ["load", "wind", "solar"]
    if lag_steps is None:
        lag_steps = [1, 12, 48]
    feature_cols = pick_feature_columns(
        train_df,
        target_col=cfg.target_col,
        include_base=include_base,
        include_groups=include_groups,
        lag_steps=lag_steps,
        lag_series=lag_series,
    )

    dataset, ds_meta = build_kan_dataset(train_df, val_df, target_col=cfg.target_col, feature_cols=feature_cols, scale_target=True)
    target_scaler = ds_meta.get("target_scaler")

    def hidden_sizes() -> list[int]:
        if cfg.hidden_layers:
            hs = [int(x) for x in cfg.hidden_layers]
            if not hs or any(h <= 0 for h in hs):
                raise ValueError(f"hidden_layers must be positive ints, got: {cfg.hidden_layers}")
            return hs
        return [int(cfg.hidden_width)]

    # Build model
    in_dim = len(feature_cols)
    width = [[in_dim, 0], *[[h, int(cfg.hidden_mult)] for h in hidden_sizes()], [1, 0]]
    model = KAN(
        width=width,
        grid=cfg.grid,
        k=cfg.k,
        mult_arity=cfg.mult_arity,
        grid_range=[cfg.grid_range_min, cfg.grid_range_max],
        seed=cfg.seed,
        auto_save=False,
        device=device_name,
    )
    dataset = _move_dataset_to_device(dataset, device_name)

    # Persist payload
    payload = {
        "run_id": run_id,
        "phase": "02-kan-training",
        "kind": str(kind or "kan"),
        "data_run_id": data_run_id,
        "data_timestamp": resolved_ts,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "cfg": asdict(cfg),
        "feature_cols": feature_cols,
        "target_scaler": target_scaler,
        "lag_steps": list(lag_steps),
        "lag_series": list(lag_series),
        "include_groups": list(include_groups),
        "include_base": bool(include_base),
        "max_train_rows": max_train_rows,
        "device": device_name,
        "env": _torch_env_info(),
    }
    _write_json(payload_path, payload)
    volume.commit()

    # Preflight: ensure dataset/model forward are finite (fail fast with artifacts).
    _write_json(
        artifacts_dir / "dataset_stats.json",
        {k: _tensor_stats(v) for k, v in dataset.items()},
    )
    _assert_finite_dataset(dataset)
    with torch.no_grad():
        y0 = model(dataset["train_input"][: min(512, dataset["train_input"].shape[0])])
        if not torch.isfinite(y0).all().item():
            _write_json(artifacts_dir / "preflight_output_stats.json", {"y0": _tensor_stats(y0)})
            volume.commit()
            raise RuntimeError("Model forward produced non-finite values at initialization")

    # Quick input range report
    x_np = train_df[feature_cols].to_numpy()
    out_of_range = float(np.mean((x_np < cfg.grid_range_min) | (x_np > cfg.grid_range_max)))
    _write_json(artifacts_dir / "input_range_report.json", {"grid_range": [cfg.grid_range_min, cfg.grid_range_max], "out_of_range_fraction": out_of_range})

    # Stage A: warmup (fit) with chunked checkpointing
    _fit_in_chunks(
        model,
        dataset,
        stage="warmup",
        total_steps=cfg.warmup_steps,
        chunk_steps=max(50, cfg.warmup_steps // 4),
        metrics_path=metrics_path,
        fit_kwargs={
            "opt": "Adam",
            "lr": cfg.warmup_lr,
            "lamb": 0.0,
            "update_grid": bool(warmup_update_grid),
            "grid_update_num": 10,
            "stop_grid_update_step": cfg.warmup_steps,
        },
        save_ckpt_path=checkpoint_dir / "model_warmup.pt",
        vol=volume,
    )

    # Eval unpruned on val
    eval_unpruned = _evaluate(
        model,
        dataset["test_input"],
        dataset["test_label"],
        target_scaler=target_scaler,
    )
    _write_json(artifacts_dir / "eval_unpruned.json", eval_unpruned)

    # Stage B: sparsify
    _fit_in_chunks(
        model,
        dataset,
        stage="sparsify",
        total_steps=cfg.sparsify_steps,
        chunk_steps=max(100, cfg.sparsify_steps // 6),
        metrics_path=metrics_path,
        fit_kwargs={
            "opt": "Adam",
            "lr": cfg.sparsify_lr,
            "lamb": cfg.sparsify_lamb,
            "lamb_l1": cfg.sparsify_lamb_l1,
            "lamb_entropy": cfg.sparsify_lamb_entropy,
            "lamb_coef": cfg.sparsify_lamb_coef,
            "lamb_coefdiff": cfg.sparsify_lamb_coefdiff,
            "update_grid": False,
        },
        save_ckpt_path=checkpoint_dir / "model_sparsify.pt",
        vol=volume,
    )

    # Prune search
    baseline_rmse = float(eval_unpruned["rmse"])
    best: Optional[dict[str, Any]] = None

    candidates = [
        {"node_th": 0.01, "edge_th": 0.01},
        {"node_th": 0.01, "edge_th": 0.03},
        {"node_th": 0.01, "edge_th": 0.05},
        {"node_th": 0.01, "edge_th": 0.08},
        {"node_th": 0.02, "edge_th": 0.10},
    ]

    state_before_prune = {k: v.clone() for k, v in model.state_dict().items()}

    # Ensure internal activations exist for pruning
    _ = model(dataset["train_input"])

    for cand in candidates:
        model.load_state_dict(state_before_prune, strict=True)
        try:
            pruned = prune_kan_model(
                model,
                dataset["train_input"],
                node_th=cand["node_th"],
                edge_th=cand["edge_th"],
            )
            sparsity = compute_edge_sparsity(pruned)
            eval_pruned = _evaluate(pruned, dataset["test_input"], dataset["test_label"], target_scaler=target_scaler)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Prune candidate failed (node_th={cand['node_th']} edge_th={cand['edge_th']}): {e}")
            continue

        rmse_ok = float(eval_pruned["rmse"]) <= baseline_rmse * cfg.max_rmse_degrade_ratio
        sparse_ok = sparsity.pruned_ratio >= cfg.target_pruned_ratio

        record = {
            "candidate": cand,
            "sparsity": sparsity.as_dict(),
            "eval_val": eval_pruned,
            "rmse_ok": bool(rmse_ok),
            "sparse_ok": bool(sparse_ok),
        }
        if best is None:
            best = record
        else:
            # Prefer satisfying both constraints; then higher sparsity; then lower rmse.
            best_good = best["rmse_ok"] and best["sparse_ok"]
            rec_good = rmse_ok and sparse_ok
            if rec_good and not best_good:
                best = record
            elif rec_good and best_good:
                if record["sparsity"]["pruned_ratio"] > best["sparsity"]["pruned_ratio"]:
                    best = record
                elif record["sparsity"]["pruned_ratio"] == best["sparsity"]["pruned_ratio"] and record["eval_val"]["rmse"] < best["eval_val"]["rmse"]:
                    best = record
            elif (not rec_good) and (not best_good):
                # If neither meets constraints, keep one with higher sparsity first, then rmse.
                if record["sparsity"]["pruned_ratio"] > best["sparsity"]["pruned_ratio"]:
                    best = record
                elif record["sparsity"]["pruned_ratio"] == best["sparsity"]["pruned_ratio"] and record["eval_val"]["rmse"] < best["eval_val"]["rmse"]:
                    best = record

    assert best is not None

    # Apply best prune permanently
    model.load_state_dict(state_before_prune, strict=True)
    model = prune_kan_model(
        model,
        dataset["train_input"],
        node_th=best["candidate"]["node_th"],
        edge_th=best["candidate"]["edge_th"],
    )
    sparsity_final = compute_edge_sparsity(model)

    _write_json(artifacts_dir / "sparsity.json", {"best_candidate": best["candidate"], **sparsity_final.as_dict()})
    _write_json(artifacts_dir / "eval_pruned.json", best["eval_val"])

    # Optional refine after pruning (LBFGS)
    _fit_in_chunks(
        model,
        dataset,
        stage="refine",
        total_steps=cfg.refine_steps,
        chunk_steps=max(50, cfg.refine_steps // 4),
        metrics_path=metrics_path,
        fit_kwargs={
            "opt": "LBFGS",
            "lr": cfg.refine_lr,
            "lamb": 0.0,
            "update_grid": False,
        },
        save_ckpt_path=checkpoint_dir / "model_refine.pt",
        vol=volume,
    )

    # Feature importance CSV
    importance = _compute_feature_importance(model, feature_cols)
    imp_path = artifacts_dir / "feature_importance.csv"
    with open(imp_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["feature", "active_edges", "active_ratio"])
        w.writeheader()
        for row in importance:
            w.writerow(row)

    # Persist the *effective* (post-prune) architecture for downstream jobs.
    model_width = [[int(a), int(b)] for a, b in getattr(model, "width", [])]
    if model_width:
        payload["model_width"] = model_width
        payload.setdefault("cfg", {})
        payload["cfg"]["hidden_width_final"] = int(model_width[1][0]) if len(model_width) > 1 else None
        payload["cfg"]["hidden_mult_final"] = int(model_width[1][1]) if len(model_width) > 1 else None

    # Final checkpoint
    ckpt = {
        "model_state": model.state_dict(),
        "payload": payload,
        "feature_cols": feature_cols,
        "target_scaler": target_scaler,
        "best_prune": best["candidate"],
        "sparsity": sparsity_final.as_dict(),
        "model_width": model_width,
    }
    torch.save(ckpt, checkpoint_dir / "model.pt")

    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    payload["results"] = {
        "eval_unpruned": eval_unpruned,
        "eval_pruned": best["eval_val"],
        "sparsity": sparsity_final.as_dict(),
        "prune_candidate": best["candidate"],
    }
    _write_json(payload_path, payload)

    # Save test predictions for downstream evaluation/plots
    x_test = torch.tensor(test_df[feature_cols].to_numpy(dtype=np.float32)).to(device_name)
    with torch.no_grad():
        pred_norm = model(x_test).detach().cpu().numpy().reshape(-1)

    y_true = test_df[cfg.target_col].to_numpy(dtype=np.float64).reshape(-1)
    if target_scaler is not None:
        pred = pred_norm * float(target_scaler["std"]) + float(target_scaler["mean"])
    else:
        pred = pred_norm

    # Hard constraint (PIKAN): nighttime PV must be 0 (for solar target).
    if cfg.target_col == "solar" and "is_night" in test_df.columns:
        from src.data.split import inverse_transform

        scaler_path = Path(VOLUME_MOUNT) / "runs" / data_run_id / "artifacts" / "scaler_params.json"
        if not scaler_path.exists():
            raise FileNotFoundError(f"scaler_params.json not found for solar nighttime constraint: {scaler_path}")
        scaler_params = json.loads(scaler_path.read_text())

        is_night_orig = inverse_transform(test_df[["is_night"]], scaler_params)["is_night"].to_numpy(dtype=np.float64)
        night_mask = is_night_orig > 0.5
        pred = pred.copy()
        pred[night_mask] = 0.0

    pred_df = pd.DataFrame({"y_true": y_true, "y_pred": pred, "residual": pred - y_true}, index=test_df.index)
    pred_df.to_parquet(artifacts_dir / "predictions_test.parquet", compression="snappy")
    volume.commit()

    return {
        "run_id": run_id,
        "status": "completed",
        "data_run_id": data_run_id,
        "data_timestamp": resolved_ts,
        "eval_unpruned": eval_unpruned,
        "eval_pruned": best["eval_val"],
        "sparsity": sparsity_final.as_dict(),
        "checkpoint": str(checkpoint_dir / "model.pt"),
    }


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=6 * 3600)
def train_kan_cpu(
    data_run_id: str,
    *,
    data_timestamp: Optional[str] = None,
    run_id: Optional[str] = None,
    kind: Optional[str] = None,
    cfg: TrainConfig = TrainConfig(),
    include_base: bool = True,
    include_groups: Optional[list[str]] = None,
    lag_series: Optional[list[str]] = None,
    lag_steps: Optional[list[int]] = None,
    max_train_rows: Optional[int] = 50_000,
    warmup_update_grid: bool = True,
) -> dict[str, Any]:
    return _train_kan_impl(
        data_run_id,
        device_name="cpu",
        data_timestamp=data_timestamp,
        run_id=run_id,
        kind=kind,
        cfg=cfg,
        include_base=include_base,
        include_groups=include_groups,
        lag_series=lag_series,
        lag_steps=lag_steps,
        max_train_rows=max_train_rows,
        warmup_update_grid=bool(warmup_update_grid),
    )


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=6 * 3600, gpu="T4")
def train_kan_gpu(
    data_run_id: str,
    *,
    data_timestamp: Optional[str] = None,
    run_id: Optional[str] = None,
    kind: Optional[str] = None,
    cfg: TrainConfig = TrainConfig(),
    include_base: bool = True,
    include_groups: Optional[list[str]] = None,
    lag_series: Optional[list[str]] = None,
    lag_steps: Optional[list[int]] = None,
    max_train_rows: Optional[int] = 50_000,
    warmup_update_grid: bool = True,
) -> dict[str, Any]:
    return _train_kan_impl(
        data_run_id,
        device_name="cuda",
        data_timestamp=data_timestamp,
        run_id=run_id,
        kind=kind,
        cfg=cfg,
        include_base=include_base,
        include_groups=include_groups,
        lag_series=lag_series,
        lag_steps=lag_steps,
        max_train_rows=max_train_rows,
        warmup_update_grid=bool(warmup_update_grid),
    )


@app.local_entrypoint()
def main(
    data_run_id: str,
    data_timestamp: Optional[str] = None,
    target: str = "load",
    hidden_width: int = 10,
    hidden_layers: str = "",
    max_train_rows: int = 50_000,
    include_groups: str = "meteorology,solar,cyclic",
    lag_series: str = "load,wind,solar",
    lag_steps: str = "1,12,48",
    include_base: bool = True,
    warmup_steps: int = 200,
    sparsify_steps: int = 800,
    refine_steps: int = 200,
    sparsify_lamb: float = 0.01,
    sparsify_lamb_l1: float = 1.0,
    sparsify_lamb_entropy: float = 2.0,
    sparsify_lamb_coef: float = 0.0,
    sparsify_lamb_coefdiff: float = 0.0,
    hidden_mult: int = 0,
    mult_arity: int = 2,
    warmup_update_grid: bool = True,
    use_gpu: bool = False,
    run_id: Optional[str] = None,
    kind: Optional[str] = None,
) -> None:
    """
    Example:
      modal run modal_jobs/kan_train.py --data-run-id <phase1_run_id> --target load --hidden-width 10
      modal run modal_jobs/kan_train.py --data-run-id <phase1_run_id> --hidden-layers 32,32
      modal run modal_jobs/kan_train.py --data-run-id <phase1_run_id> --use-gpu
    """
    hidden_layers_s = str(hidden_layers).strip()
    hidden_layers_tuple = None
    if hidden_layers_s and hidden_layers_s.lower() not in {"none", "null", "no"}:
        hidden_layers_tuple = tuple(int(x.strip()) for x in hidden_layers_s.split(",") if x.strip())
    cfg = TrainConfig(
        target_col=target,
        hidden_width=hidden_width,
        hidden_layers=hidden_layers_tuple,
        hidden_mult=hidden_mult,
        mult_arity=mult_arity,
        warmup_steps=warmup_steps,
        sparsify_steps=sparsify_steps,
        refine_steps=refine_steps,
        sparsify_lamb=sparsify_lamb,
        sparsify_lamb_l1=sparsify_lamb_l1,
        sparsify_lamb_entropy=sparsify_lamb_entropy,
        sparsify_lamb_coef=sparsify_lamb_coef,
        sparsify_lamb_coefdiff=sparsify_lamb_coefdiff,
    )
    include_groups_s = str(include_groups).strip()
    if include_groups_s.lower() in {"none", "null", "no"}:
        include_groups_list = []
    else:
        include_groups_list = [s.strip() for s in include_groups_s.split(",") if s.strip()]

    lag_series_s = str(lag_series).strip()
    if lag_series_s.lower() in {"none", "null", "no"}:
        lag_series_list = []
    else:
        lag_series_list = [s.strip() for s in lag_series_s.split(",") if s.strip()]

    lag_steps_s = str(lag_steps).strip()
    if lag_steps_s.lower() in {"none", "null", "no"}:
        lag_steps_list = []
    else:
        lag_steps_list = [int(s.strip()) for s in lag_steps_s.split(",") if s.strip()]
    max_train_rows_opt: Optional[int] = int(max_train_rows)
    if max_train_rows_opt <= 0:
        max_train_rows_opt = None

    fn = train_kan_gpu if use_gpu else train_kan_cpu
    result = fn.remote(
        data_run_id,
        data_timestamp=data_timestamp,
        run_id=run_id,
        kind=kind,
        cfg=cfg,
        include_base=include_base,
        include_groups=include_groups_list,
        lag_series=lag_series_list,
        lag_steps=lag_steps_list,
        max_train_rows=max_train_rows_opt,
        warmup_update_grid=bool(warmup_update_grid),
    )
    print(json.dumps(result, indent=2))
