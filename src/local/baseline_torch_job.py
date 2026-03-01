from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from src.baselines.torch_models import MLPRegressor, count_trainable_params
from src.baselines.torch_training import train_mlp_regressor
from src.data.split import load_splits_from_parquet
from src.kan_sr.dataset import pick_feature_columns
from src.local.run_contract import ensure_run_dirs, utc_run_id, write_json


@dataclass(frozen=True)
class BaselineConfig:
    model_type: str = "mlp"  # mlp only (local)
    target_col: str = "load"
    epochs: int = 50
    lr: float = 1e-3
    batch_size: int = 512
    patience: int = 8


@dataclass(frozen=True)
class BaselineRunOptions:
    runs_root: Path
    data_timestamp: str | None = None
    run_id: str | None = None
    match_kan_run_id: str | None = None
    sync_kan_feature_cols: bool = False
    sync_kan_budget: bool = False
    lag_steps: list[int] | None = None
    max_train_rows: int | None = 200_000
    device_name: str | None = None


def _load_payload(runs_root: Path, run_id: str) -> dict[str, Any]:
    path = Path(runs_root) / str(run_id) / "payload.json"
    if not path.exists():
        raise FileNotFoundError(f"payload.json not found: {path}")
    return json.loads(path.read_text())


def _kan_total_steps(payload: dict[str, Any]) -> int:
    cfg = payload.get("cfg") or {}
    keys = ["warmup_steps", "sparsify_steps", "refine_steps"]
    missing = [k for k in keys if k not in cfg]
    if missing:
        raise ValueError(f"KAN payload cfg missing steps keys: {missing}")
    return int(cfg["warmup_steps"]) + int(cfg["sparsify_steps"]) + int(cfg["refine_steps"])


def _pick_device(device_name: str | None) -> str:
    import torch

    if device_name is None:
        return "cuda" if torch.cuda.is_available() else "cpu"
    dn = str(device_name).strip().lower()
    if dn not in {"cpu", "cuda"}:
        raise ValueError(f"device_name must be 'cpu' or 'cuda', got: {device_name!r}")
    if dn == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Requested CUDA device but torch.cuda.is_available() is False")
    return dn


def _downsample_train_df(train_df, *, max_train_rows: int | None):
    if max_train_rows is None or len(train_df) <= int(max_train_rows):
        return train_df
    return train_df.iloc[: int(max_train_rows)].copy()


def _resolve_timestamp(processed_dir: Path, *, data_timestamp: str | None) -> str:
    if data_timestamp is not None:
        return str(data_timestamp)
    train_files = sorted(processed_dir.glob("train_*.parquet"))
    if not train_files:
        raise FileNotFoundError(f"No train_*.parquet found under processed_dir: {processed_dir}")
    return train_files[-1].stem.replace("train_", "")


def _infer_feature_cols(
    train_df,
    *,
    cfg: BaselineConfig,
    kan_payload: dict[str, Any] | None,
    sync_kan_feature_cols: bool,
    lag_steps: list[int] | None,
) -> tuple[list[str], list[int]]:
    if sync_kan_feature_cols:
        if kan_payload is None:
            raise ValueError("sync_kan_feature_cols requires kan_payload")
        feature_cols = list(kan_payload.get("feature_cols") or [])
        if not feature_cols:
            raise ValueError("KAN payload missing feature_cols")
        missing = [c for c in feature_cols if c not in train_df.columns]
        if missing:
            raise ValueError(f"KAN feature cols missing from dataset: {missing[:10]}")
        steps = list(kan_payload.get("lag_steps") or [])
        return feature_cols, steps

    steps = lag_steps or [1, 12, 48]
    return pick_feature_columns(train_df, target_col=cfg.target_col, lag_steps=steps), list(steps)


def _save_predictions(*, out_path: Path, y_true: np.ndarray, y_pred: np.ndarray, index) -> None:
    import pandas as pd

    pd.DataFrame({"y_true": y_true.reshape(-1).astype("float64"), "y_pred": y_pred.reshape(-1).astype("float64")}, index=index).assign(
        residual=lambda d: d["y_pred"] - d["y_true"]
    ).to_parquet(out_path, compression="snappy")


def _resolve_kan_sync(
    *,
    runs_root: Path,
    data_run_id: str,
    cfg: BaselineConfig,
    match_kan_run_id: str | None,
    sync_kan_feature_cols: bool,
    sync_kan_budget: bool,
    max_train_rows: int | None,
) -> tuple[dict[str, Any] | None, BaselineConfig, int | None]:
    if not (sync_kan_feature_cols or sync_kan_budget):
        return None, cfg, max_train_rows
    if match_kan_run_id is None:
        raise ValueError("sync_kan_feature_cols/sync_kan_budget requires match_kan_run_id")

    kan_payload = _load_payload(Path(runs_root), match_kan_run_id)
    if str(kan_payload.get("data_run_id")) != str(data_run_id):
        raise ValueError(f"KAN data_run_id mismatch: baseline={data_run_id} kan={kan_payload.get('data_run_id')}")
    kan_target = (kan_payload.get("cfg") or {}).get("target_col")
    if kan_target is not None and str(kan_target) != str(cfg.target_col):
        raise ValueError(f"KAN target_col mismatch: baseline={cfg.target_col} kan={kan_target}")

    cfg2 = cfg
    max_rows2 = max_train_rows
    if sync_kan_budget:
        kan_max = kan_payload.get("max_train_rows")
        max_rows2 = int(kan_max) if kan_max is not None else None
    return kan_payload, cfg2, max_rows2


def _build_payload(
    *,
    run_id: str,
    cfg: BaselineConfig,
    data_run_id: str,
    data_timestamp: str | None,
    feature_cols: list[str],
    lag_steps: list[int],
    match_kan_run_id: str | None,
    sync_kan_feature_cols: bool,
    sync_kan_budget: bool,
    max_train_rows: int | None,
    device: str,
    budget_sync: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "phase": "04-baselines-torch",
        "cfg": asdict(cfg),
        "data_run_id": str(data_run_id),
        "data_timestamp": data_timestamp,
        "feature_cols": list(feature_cols),
        "lag_steps": list(lag_steps),
        "match_kan_run_id": match_kan_run_id,
        "sync_kan_feature_cols": bool(sync_kan_feature_cols),
        "sync_kan_budget": bool(sync_kan_budget),
        "max_train_rows": max_train_rows,
        "device": device,
        "budget_sync": budget_sync,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def _train_and_persist_mlp(
    *,
    dirs,
    payload: dict[str, Any],
    train_df,
    val_df,
    test_df,
    feature_cols: list[str],
    target_col: str,
    cfg: BaselineConfig,
    device: str,
) -> dict[str, Any]:
    import torch

    x_train = train_df[feature_cols].to_numpy(dtype=np.float32)
    y_train = train_df[[target_col]].to_numpy(dtype=np.float32)
    x_val = val_df[feature_cols].to_numpy(dtype=np.float32)
    y_val = val_df[[target_col]].to_numpy(dtype=np.float32)
    x_test = test_df[feature_cols].to_numpy(dtype=np.float32)
    y_test = test_df[[target_col]].to_numpy(dtype=np.float32)

    model = MLPRegressor(input_dim=len(feature_cols), hidden_dim=64, dropout=0.1)
    payload = dict(payload)
    payload["model_param_count"] = int(count_trainable_params(model))

    result = train_mlp_regressor(
        model=model,
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        x_test=x_test,
        y_test=y_test,
        device=device,
        metrics_path=Path(dirs.run_dir) / "metrics.csv",
        lr=float(cfg.lr),
        batch_size=int(cfg.batch_size),
        epochs=int(cfg.epochs),
        patience=int(cfg.patience),
    )

    torch.save({"model_state": model.state_dict(), "payload": payload}, Path(dirs.checkpoint_dir) / "model.pt")
    write_json(Path(dirs.artifacts_dir) / "eval_test.json", result.test_metrics)
    write_json(Path(dirs.artifacts_dir) / "target_scaler.json", result.target_scaler)

    mean = float(result.target_scaler["mean"])
    std = float(result.target_scaler["std"])
    with torch.no_grad():
        pred_norm = model(torch.tensor(x_test, dtype=torch.float32).to(device)).detach().cpu().numpy().reshape(-1)
    _save_predictions(out_path=Path(dirs.artifacts_dir) / "predictions_test.parquet", y_true=y_test.reshape(-1), y_pred=pred_norm * std + mean, index=test_df.index)
    return payload


def run_baseline_local(
    data_run_id: str,
    *,
    opts: BaselineRunOptions,
    cfg: BaselineConfig = BaselineConfig(),
) -> dict[str, Any]:
    if str(cfg.model_type).strip().lower() != "mlp":
        raise ValueError("Local baseline_torch currently supports model_type='mlp' only")

    processed_dir = Path(opts.runs_root) / str(data_run_id) / "processed"
    train_df, val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=opts.data_timestamp)
    resolved_ts = _resolve_timestamp(processed_dir, data_timestamp=opts.data_timestamp)

    kan_payload, cfg2, max_rows2 = _resolve_kan_sync(runs_root=Path(opts.runs_root), data_run_id=str(data_run_id), cfg=cfg, match_kan_run_id=opts.match_kan_run_id, sync_kan_feature_cols=bool(opts.sync_kan_feature_cols), sync_kan_budget=bool(opts.sync_kan_budget), max_train_rows=opts.max_train_rows)
    train_df = _downsample_train_df(train_df, max_train_rows=max_rows2)

    budget_sync = None
    if bool(opts.sync_kan_budget):
        if kan_payload is None:
            raise ValueError("sync_kan_budget requires kan_payload")
        kan_steps = int(_kan_total_steps(kan_payload))
        bs = int(cfg2.batch_size)
        if bs <= 0:
            raise ValueError(f"batch_size must be positive, got: {cfg2.batch_size}")
        batches_per_epoch = int(math.ceil(len(train_df) / bs))
        if batches_per_epoch <= 0:
            raise ValueError(f"Invalid batches_per_epoch computed: n_train={len(train_df)} batch_size={bs}")
        epochs = int(math.ceil(float(kan_steps) / float(batches_per_epoch)))
        cfg2 = replace(cfg2, epochs=epochs)
        budget_sync = {
            "kan_total_steps": kan_steps,
            "batches_per_epoch": batches_per_epoch,
            "epochs": int(cfg2.epochs),
            "optimizer_updates_target": kan_steps,
            "optimizer_updates_planned": int(cfg2.epochs) * batches_per_epoch,
        }

    feature_cols, lag_steps_out = _infer_feature_cols(train_df, cfg=cfg2, kan_payload=kan_payload, sync_kan_feature_cols=bool(opts.sync_kan_feature_cols), lag_steps=opts.lag_steps)
    device = _pick_device(opts.device_name)

    rid = opts.run_id or utc_run_id()
    dirs = ensure_run_dirs(Path(opts.runs_root), rid)
    payload = _build_payload(run_id=rid, cfg=cfg2, data_run_id=str(data_run_id), data_timestamp=resolved_ts, feature_cols=feature_cols, lag_steps=lag_steps_out, match_kan_run_id=opts.match_kan_run_id, sync_kan_feature_cols=bool(opts.sync_kan_feature_cols), sync_kan_budget=bool(opts.sync_kan_budget), max_train_rows=max_rows2, device=device, budget_sync=budget_sync)
    write_json(Path(dirs.run_dir) / "payload.json", payload)

    payload2 = _train_and_persist_mlp(dirs=dirs, payload=payload, train_df=train_df, val_df=val_df, test_df=test_df, feature_cols=feature_cols, target_col=str(cfg2.target_col), cfg=cfg2, device=device)
    payload2["completed_at"] = datetime.now(timezone.utc).isoformat()
    write_json(Path(dirs.run_dir) / "payload.json", payload2)
    return payload2
