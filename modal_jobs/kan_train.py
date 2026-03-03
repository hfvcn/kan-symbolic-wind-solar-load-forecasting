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
      feature_importance_sparsify.csv
      eval_unpruned.json
      eval_sparsify.json
      eval_pruned.json
      prune_search.json
"""

from __future__ import annotations

import csv
import fnmatch
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


def _validate_required_feature_patterns(feature_cols: list[str], patterns: tuple[str, ...]) -> None:
    missing = [p for p in patterns if not any(fnmatch.fnmatch(c, p) for c in feature_cols)]
    if missing:
        raise ValueError(f"Required prune feature patterns did not match any feature columns: {missing}")


def _check_required_feature_patterns(
    feature_cols: list[str],
    active_edges_by_feature: dict[str, int],
    patterns: tuple[str, ...],
) -> dict[str, Any]:
    details: list[dict[str, Any]] = []
    ok = True
    for pat in patterns:
        matched = [c for c in feature_cols if fnmatch.fnmatch(c, pat)]
        active = [c for c in matched if int(active_edges_by_feature.get(c, 0)) > 0]
        pat_ok = len(active) > 0
        details.append({"pattern": pat, "matched": matched, "active": active, "ok": bool(pat_ok)})
        ok = ok and pat_ok
    missing = [d["pattern"] for d in details if not d["ok"]]
    return {"ok": bool(ok), "missing": missing, "details": details}


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
    prune_require_features: tuple[str, ...] = ()
    prune_require_strict: bool = False


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
    if cfg.prune_require_features:
        _validate_required_feature_patterns(feature_cols, cfg.prune_require_features)

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

    # Preflight: ensure dataset is finite.
    _write_json(
        artifacts_dir / "dataset_stats.json",
        {k: _tensor_stats(v) for k, v in dataset.items()},
    )
    _assert_finite_dataset(dataset)

    # Quick input range report
    x_np = train_df[feature_cols].to_numpy()
    out_of_range = float(np.mean((x_np < cfg.grid_range_min) | (x_np > cfg.grid_range_max)))
    _write_json(artifacts_dir / "input_range_report.json", {"grid_range": [cfg.grid_range_min, cfg.grid_range_max], "out_of_range_fraction": out_of_range})
    volume.commit()

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
    # Enable efficiency mode by disabling the symbolic branch during training.
    # This can speed up training by 5-10x without affecting spline learning.
    model.speed()

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

    # Eval after warmup (pre-sparsify)
    eval_unpruned = _evaluate(
        model,
        dataset["test_input"],
        dataset["test_label"],
        target_scaler=target_scaler,
    )
    _write_json(artifacts_dir / "eval_unpruned.json", eval_unpruned)

    # Stage B: sparsify
    # Re-enable save_act so that lamb (regularisation) is actually applied.
    # model.speed() disables save_act during warmup for performance, but
    # KAN.fit() silently sets lamb=0 when save_act is False.
    model.save_act = True
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

    # Eval after sparsify (pre-prune): this is the correct baseline for pruning
    # degradation, since pruning happens after sparsify.
    eval_sparsify = _evaluate(
        model,
        dataset["test_input"],
        dataset["test_label"],
        target_scaler=target_scaler,
    )
    _write_json(artifacts_dir / "eval_sparsify.json", eval_sparsify)

    # Feature importance before pruning (helps diagnose "prune killed feature")
    importance_sparsify = _compute_feature_importance(model, feature_cols)
    imp_sparsify_path = artifacts_dir / "feature_importance_sparsify.csv"
    with open(imp_sparsify_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["feature", "active_edges", "active_ratio"])
        w.writeheader()
        for row in importance_sparsify:
            w.writerow(row)

    volume.commit()

    # Prune search
    baseline_rmse = float(eval_sparsify["rmse"])
    prune_records: list[dict[str, Any]] = []

    candidates = [
        {"node_th": 0.01, "edge_th": 0.002},
        {"node_th": 0.01, "edge_th": 0.005},
        {"node_th": 0.01, "edge_th": 0.01},
        {"node_th": 0.01, "edge_th": 0.03},
        {"node_th": 0.01, "edge_th": 0.05},
        {"node_th": 0.01, "edge_th": 0.08},
        {"node_th": 0.02, "edge_th": 0.10},
        {"node_th": 0.02, "edge_th": 0.15},
        {"node_th": 0.03, "edge_th": 0.20},
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
            imp_pruned = _compute_feature_importance(pruned, feature_cols)
            active_edges = {r["feature"]: int(r["active_edges"]) for r in imp_pruned}
            required = (
                _check_required_feature_patterns(feature_cols, active_edges, cfg.prune_require_features)
                if cfg.prune_require_features
                else {"ok": True, "missing": [], "details": []}
            )
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
            "required": required,
        }
        prune_records.append(record)

    if not prune_records:
        raise RuntimeError("All prune candidates failed; see logs for details.")

    def _pick_sparse_then_rmse(records: list[dict[str, Any]]) -> dict[str, Any]:
        return max(records, key=lambda r: (float(r["sparsity"]["pruned_ratio"]), -float(r["eval_val"]["rmse"])))

    def _pick_rmse_then_sparse(records: list[dict[str, Any]]) -> dict[str, Any]:
        return min(records, key=lambda r: (float(r["eval_val"]["rmse"]), -float(r["sparsity"]["pruned_ratio"])))

    selection_pool = list(prune_records)
    required_filter_mode = "not_requested"
    if cfg.prune_require_features:
        required_ok = [r for r in prune_records if bool(r["required"]["ok"])]
        if required_ok:
            selection_pool = required_ok
            required_filter_mode = "filtered"
        else:
            required_filter_mode = "none_ok"

    if cfg.prune_require_features and required_filter_mode == "none_ok" and cfg.prune_require_strict:
        _write_json(
            artifacts_dir / "prune_search.json",
            {
                "baseline_eval": eval_sparsify,
                "baseline_rmse": baseline_rmse,
                "target_pruned_ratio": float(cfg.target_pruned_ratio),
                "max_rmse_degrade_ratio": float(cfg.max_rmse_degrade_ratio),
                "required_features": list(cfg.prune_require_features),
                "required_filter_mode": required_filter_mode,
                "selection_mode": "no_required_ok_strict",
                "records": prune_records,
            },
        )
        volume.commit()
        raise RuntimeError(
            "No prune candidate satisfied required feature patterns; see artifacts/prune_search.json for details."
        )

    good = [r for r in selection_pool if r["rmse_ok"] and r["sparse_ok"]]
    rmse_only = [r for r in selection_pool if r["rmse_ok"] and (not r["sparse_ok"])]
    sparse_only = [r for r in selection_pool if (not r["rmse_ok"]) and r["sparse_ok"]]

    selection_mode = ""
    if good:
        best = _pick_rmse_then_sparse(good)
        selection_mode = "both_ok"
    elif rmse_only:
        best = _pick_sparse_then_rmse(rmse_only)
        selection_mode = "rmse_ok_only"
    elif sparse_only:
        best = min(sparse_only, key=lambda r: float(r["eval_val"]["rmse"]))
        selection_mode = "sparse_ok_only"
    else:
        best = min(selection_pool, key=lambda r: float(r["eval_val"]["rmse"]))
        selection_mode = "min_rmse"

    if cfg.prune_require_features and required_filter_mode == "none_ok" and (not cfg.prune_require_strict):
        selection_mode = f"fallback_no_required_ok::{selection_mode}"

    _write_json(
        artifacts_dir / "prune_search.json",
        {
            "baseline_eval": eval_sparsify,
            "baseline_rmse": baseline_rmse,
            "target_pruned_ratio": float(cfg.target_pruned_ratio),
            "max_rmse_degrade_ratio": float(cfg.max_rmse_degrade_ratio),
            "required_features": list(cfg.prune_require_features),
            "required_filter_mode": required_filter_mode,
            "selection_mode": selection_mode,
            "records": prune_records,
        },
    )
    volume.commit()

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
            "lamb_l1": 0.0,
            "lamb_entropy": 0.0,
            "lamb_coef": 0.0,
            "lamb_coefdiff": 0.0,
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

    eval_pruned_final = best["eval_val"]
    prune_candidate_final = best["candidate"]
    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    payload["results"] = {
        "eval_unpruned": eval_unpruned,
        "eval_sparsify": eval_sparsify,
        "eval_pruned": eval_pruned_final,
        "sparsity": sparsity_final.as_dict(),
        "prune_candidate": prune_candidate_final,
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


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=6 * 3600, gpu="L4")
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
    grid_range_min: float = -5.0,
    grid_range_max: float = 5.0,
    grid: int = 5,
    k: int = 3,
    seed: int = 1,
    max_train_rows: int = 50_000,
    include_groups: str = "meteorology,solar,cyclic",
    lag_series: str = "load,wind,solar",
    lag_steps: str = "1,12,48",
    include_base: bool = True,
    warmup_steps: int = 200,
    sparsify_steps: int = 800,
    refine_steps: int = 200,
    warmup_lr: float = 0.01,
    sparsify_lr: float = 0.005,
    refine_lr: float = 0.5,
    sparsify_lamb: float = 0.01,
    sparsify_lamb_l1: float = 1.0,
    sparsify_lamb_entropy: float = 2.0,
    sparsify_lamb_coef: float = 0.0,
    sparsify_lamb_coefdiff: float = 0.0,
    target_pruned_ratio: float = 0.8,
    max_rmse_degrade_ratio: float = 1.1,
    prune_require_features: str = "",
    prune_require_strict: bool = False,
    hidden_mult: int = 0,
    mult_arity: int = 2,
    warmup_update_grid: bool = True,
    use_gpu: bool = False,
    submit_only: bool = False,
    run_id: Optional[str] = None,
    kind: Optional[str] = None,
) -> None:
    """
    Example:
      modal run modal_jobs/kan_train.py --data-run-id <phase1_run_id> --target load --hidden-width 10
      modal run modal_jobs/kan_train.py --data-run-id <phase1_run_id> --hidden-layers 32,32
      modal run modal_jobs/kan_train.py --data-run-id <phase1_run_id> --use-gpu
    """
    hidden_layers_tuple = _parse_hidden_layers(hidden_layers)
    cfg = TrainConfig(
        target_col=target,
        grid_range_min=float(grid_range_min),
        grid_range_max=float(grid_range_max),
        hidden_width=hidden_width,
        hidden_layers=hidden_layers_tuple,
        grid=int(grid),
        k=int(k),
        seed=int(seed),
        hidden_mult=hidden_mult,
        mult_arity=mult_arity,
        warmup_steps=warmup_steps,
        sparsify_steps=sparsify_steps,
        refine_steps=refine_steps,
        warmup_lr=float(warmup_lr),
        sparsify_lr=float(sparsify_lr),
        refine_lr=float(refine_lr),
        sparsify_lamb=sparsify_lamb,
        sparsify_lamb_l1=sparsify_lamb_l1,
        sparsify_lamb_entropy=sparsify_lamb_entropy,
        sparsify_lamb_coef=sparsify_lamb_coef,
        sparsify_lamb_coefdiff=sparsify_lamb_coefdiff,
        target_pruned_ratio=float(target_pruned_ratio),
        max_rmse_degrade_ratio=float(max_rmse_degrade_ratio),
        prune_require_features=tuple(_parse_csv_strs(prune_require_features)),
        prune_require_strict=bool(prune_require_strict),
    )

    include_groups_list = _parse_csv_strs(include_groups)
    lag_series_list = _parse_csv_strs(lag_series)
    lag_steps_list = _parse_csv_ints(lag_steps)
    max_train_rows_opt: Optional[int] = int(max_train_rows)
    if max_train_rows_opt <= 0:
        max_train_rows_opt = None

    fn = train_kan_gpu if use_gpu else train_kan_cpu
    if submit_only:
        call = fn.spawn(
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
        print(json.dumps({"run_id": run_id, "status": "submitted", "call": str(call)}, indent=2))
        return

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


def _is_noneish(s: str) -> bool:
    return (not str(s).strip()) or (str(s).strip().lower() in {"none", "null", "no"})


def _parse_hidden_layers(s: str) -> tuple[int, ...] | None:
    if _is_noneish(s):
        return None
    vals = tuple(int(x.strip()) for x in str(s).split(",") if x.strip())
    return vals or None


def _parse_csv_strs(s: str) -> list[str]:
    if _is_noneish(s):
        return []
    return [p.strip() for p in str(s).split(",") if p.strip()]


def _parse_csv_ints(s: str) -> list[int]:
    if _is_noneish(s):
        return []
    return [int(p.strip()) for p in str(s).split(",") if p.strip()]
