from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.kan_sr.feature_scaling import transform_feature_frame
from src.kan_sr.sparsity import compute_edge_sparsity
from src.local.kan_train_artifacts import preflight, save_test_predictions, write_checkpoint, write_feature_importance_csv
from src.local.kan_train_config import TrainConfig
from src.local.kan_train_core import compute_feature_importance, evaluate, fit_in_chunks, pick_device
from src.local.kan_train_prepare import (
    PreparedData,
    build_model,
    build_payload,
    load_splits,
    normalize_feature_settings,
    prepare_data,
)
from src.local.kan_train_prune import apply_prune, search_best_prune
from src.local.run_contract import ensure_run_dirs, mark_payload_completed, utc_run_id, write_json


@dataclass(frozen=True)
class KanTrainContext:
    run_id: str
    device: str
    dirs: Any
    prepared: PreparedData
    model: Any
    payload: dict[str, Any]
    test_df: Any


def _init_context(
    *,
    runs_root: Path,
    data_run_id: str,
    data_timestamp: str | None,
    device_name: str,
    run_id: str | None,
    kind: str | None,
    cfg: TrainConfig,
    include_base: bool,
    include_groups: list[str] | None,
    lag_series: list[str] | None,
    lag_steps: list[int] | None,
    max_train_rows: int | None,
    feature_profile: str = "default",
) -> KanTrainContext:
    import torch

    device = pick_device(device_name)
    rid = run_id or utc_run_id()
    dirs = ensure_run_dirs(Path(runs_root), rid)

    processed_dir = Path(runs_root) / str(data_run_id) / "processed"
    if not processed_dir.exists():
        raise FileNotFoundError(f"Processed dir not found: {processed_dir}")

    resolved_ts, train_df, val_df, test_df = load_splits(processed_dir=processed_dir, data_timestamp=data_timestamp, max_train_rows=max_train_rows)
    groups, series, steps = normalize_feature_settings(include_groups=include_groups, lag_series=lag_series, lag_steps=lag_steps)
    prepared = prepare_data(
        train_df=train_df,
        val_df=val_df,
        cfg=cfg,
        include_base=include_base,
        include_groups=groups,
        lag_series=series,
        lag_steps=steps,
        feature_profile=str(feature_profile),
        device=device,
    )
    model = build_model(in_dim=len(prepared.feature_cols), cfg=cfg, device=device)

    payload = build_payload(
        run_id=rid,
        kind=kind,
        data_run_id=str(data_run_id),
        data_timestamp=resolved_ts,
        cfg=cfg,
        prepared=prepared,
        include_groups=groups,
        include_base=include_base,
        lag_series=series,
        lag_steps=steps,
        feature_profile=str(feature_profile),
        max_train_rows=max_train_rows,
        device=device,
    )
    write_json(Path(dirs.run_dir) / "payload.json", payload)
    preflight(model, prepared.dataset, artifacts_dir=Path(dirs.artifacts_dir))
    with torch.no_grad():
        _ = model(prepared.dataset["train_input"][:1])

    return KanTrainContext(run_id=rid, device=device, dirs=dirs, prepared=prepared, model=model, payload=payload, test_df=test_df)


def _warmup_and_sparsify(
    ctx: KanTrainContext, *, cfg: TrainConfig, warmup_update_grid: bool
) -> tuple[dict[str, float], dict[str, float], Path]:
    metrics_path = Path(ctx.dirs.run_dir) / "metrics.csv"
    fit_in_chunks(
        ctx.model,
        ctx.prepared.dataset,
        stage="warmup",
        total_steps=int(cfg.warmup_steps),
        chunk_steps=max(50, int(cfg.warmup_steps) // 4),
        metrics_path=metrics_path,
        fit_kwargs={
            "opt": "Adam",
            "lr": float(cfg.warmup_lr),
            "lamb": 0.0,
            "update_grid": bool(warmup_update_grid),
            "grid_update_num": 10,
            "stop_grid_update_step": int(cfg.warmup_steps),
        },
        save_ckpt_path=Path(ctx.dirs.checkpoint_dir) / "model_warmup.pt",
    )

    eval_unpruned = evaluate(ctx.model, ctx.prepared.dataset["test_input"], ctx.prepared.dataset["test_label"], target_scaler=ctx.prepared.target_scaler)
    write_json(Path(ctx.dirs.artifacts_dir) / "eval_unpruned.json", eval_unpruned)

    fit_in_chunks(
        ctx.model,
        ctx.prepared.dataset,
        stage="sparsify",
        total_steps=int(cfg.sparsify_steps),
        chunk_steps=max(100, int(cfg.sparsify_steps) // 6),
        metrics_path=metrics_path,
        fit_kwargs={
            "opt": "Adam",
            "lr": float(cfg.sparsify_lr),
            "lamb": float(cfg.sparsify_lamb),
            "lamb_l1": float(cfg.sparsify_lamb_l1),
            "lamb_entropy": float(cfg.sparsify_lamb_entropy),
            "lamb_coef": float(cfg.sparsify_lamb_coef),
            "lamb_coefdiff": float(cfg.sparsify_lamb_coefdiff),
            "update_grid": False,
        },
        save_ckpt_path=Path(ctx.dirs.checkpoint_dir) / "model_sparsify.pt",
    )
    eval_sparsify = evaluate(ctx.model, ctx.prepared.dataset["test_input"], ctx.prepared.dataset["test_label"], target_scaler=ctx.prepared.target_scaler)
    write_json(Path(ctx.dirs.artifacts_dir) / "eval_sparsify.json", eval_sparsify)
    write_feature_importance_csv(
        Path(ctx.dirs.artifacts_dir) / "feature_importance_sparsify.csv",
        compute_feature_importance(ctx.model, ctx.prepared.feature_cols),
    )
    return eval_unpruned, eval_sparsify, metrics_path


def _prune_and_refine(
    ctx: KanTrainContext,
    *,
    cfg: TrainConfig,
    metrics_path: Path,
    eval_sparsify: dict[str, float],
) -> tuple[Any, Any, dict[str, float | int], list[list[int]]]:
    best = search_best_prune(
        ctx.model,
        ctx.prepared.dataset,
        target_scaler=ctx.prepared.target_scaler,
        baseline_rmse=float(eval_sparsify["rmse"]),
        cfg=cfg,
    )
    model = apply_prune(ctx.model, ctx.prepared.dataset, record=best)
    sparsity_final = compute_edge_sparsity(model).as_dict()
    write_json(Path(ctx.dirs.artifacts_dir) / "sparsity.json", {"best_candidate": best.candidate, **sparsity_final})

    fit_in_chunks(
        model,
        ctx.prepared.dataset,
        stage="refine",
        total_steps=int(cfg.refine_steps),
        chunk_steps=max(50, int(cfg.refine_steps) // 4),
        metrics_path=metrics_path,
        fit_kwargs={"opt": "LBFGS", "lr": float(cfg.refine_lr), "lamb": 0.0, "update_grid": False},
        save_ckpt_path=Path(ctx.dirs.checkpoint_dir) / "model_refine.pt",
    )
    write_feature_importance_csv(Path(ctx.dirs.artifacts_dir) / "feature_importance.csv", compute_feature_importance(model, ctx.prepared.feature_cols))
    model_width = [[int(a), int(b)] for a, b in getattr(model, "width", [])]
    return model, best, sparsity_final, model_width


def _write_final_pruned_eval(ctx: KanTrainContext, *, model) -> dict[str, float]:
    eval_pruned = evaluate(
        model,
        ctx.prepared.dataset["test_input"],
        ctx.prepared.dataset["test_label"],
        target_scaler=ctx.prepared.target_scaler,
    )
    write_json(Path(ctx.dirs.artifacts_dir) / "eval_pruned.json", eval_pruned)
    write_json(Path(ctx.dirs.artifacts_dir) / "eval_val.json", eval_pruned)
    return eval_pruned


def _write_final_test_eval(ctx: KanTrainContext, *, model) -> dict[str, float]:
    import numpy as np
    import torch

    from src.kan_sr.metrics import mae, r2, rmse

    target_col = str((ctx.payload.get("cfg") or {}).get("target_col") or "load")
    x_test_np = transform_feature_frame(ctx.test_df, ctx.prepared.feature_cols, ctx.prepared.feature_scaler)
    x_test = torch.tensor(x_test_np).to(ctx.device)
    with torch.no_grad():
        pred = model(x_test).detach().cpu().numpy().reshape(-1)

    y_true = ctx.test_df[target_col].to_numpy(dtype=np.float64).reshape(-1)
    if ctx.prepared.target_scaler is not None:
        pred = pred * float(ctx.prepared.target_scaler["std"]) + float(ctx.prepared.target_scaler["mean"])

    metrics = {
        "rmse": rmse(y_true, pred),
        "mae": mae(y_true, pred),
        "r2": r2(y_true, pred),
    }
    write_json(Path(ctx.dirs.artifacts_dir) / "eval_test.json", metrics)
    return metrics


def _finalize(
    ctx: KanTrainContext,
    *,
    model,
    best,
    eval_unpruned: dict[str, float],
    eval_sparsify: dict[str, float],
    sparsity: dict[str, float | int],
    model_width: list[list[int]],
) -> dict[str, Any]:
    eval_val = _write_final_pruned_eval(ctx, model=model)
    eval_test = _write_final_test_eval(ctx, model=model)
    payload = dict(ctx.payload)
    payload["model_width"] = model_width
    results = {
        "eval_unpruned": eval_unpruned,
        "eval_sparsify": eval_sparsify,
        "eval_pruned": eval_val,
        "eval_val": eval_val,
        "eval_test": eval_test,
        "sparsity": sparsity,
        "prune_candidate": best.candidate,
    }

    write_checkpoint(
        ckpt_path=Path(ctx.dirs.checkpoint_dir) / "model.pt",
        model=model,
        payload=payload,
        feature_cols=ctx.prepared.feature_cols,
        feature_scaler=ctx.prepared.feature_scaler,
        target_scaler=ctx.prepared.target_scaler,
        best_prune=best.candidate,
        sparsity=sparsity,
        model_width=model_width,
    )
    target_col = str((ctx.payload.get("cfg") or {}).get("target_col") or "load")
    save_test_predictions(
        out_path=Path(ctx.dirs.artifacts_dir) / "predictions_test.parquet",
        model=model,
        test_df=ctx.test_df,
        feature_cols=ctx.prepared.feature_cols,
        feature_scaler=ctx.prepared.feature_scaler,
        target_col=target_col,
        target_scaler=ctx.prepared.target_scaler,
        device=ctx.device,
    )
    final_payload = mark_payload_completed(payload, results=results)
    write_json(Path(ctx.dirs.run_dir) / "payload.json", final_payload)
    return {
        "run_id": ctx.run_id,
        "status": str(final_payload["status"]),
        "finished_at": str(final_payload["finished_at"]),
        "checkpoint": str(Path(ctx.dirs.checkpoint_dir) / "model.pt"),
    }


def train_kan_local(
    data_run_id: str,
    *,
    runs_root: Path,
    device_name: str = "cpu",
    data_timestamp: str | None = None,
    run_id: str | None = None,
    kind: str | None = None,
    cfg: TrainConfig = TrainConfig(),
    include_base: bool = True,
    include_groups: list[str] | None = None,
    lag_series: list[str] | None = None,
    lag_steps: list[int] | None = None,
    feature_profile: str = "default",
    max_train_rows: int | None = 50_000,
    warmup_update_grid: bool = True,
) -> dict[str, Any]:
    ctx = _init_context(
        runs_root=runs_root,
        data_run_id=data_run_id,
        data_timestamp=data_timestamp,
        device_name=device_name,
        run_id=run_id,
        kind=kind,
        cfg=cfg,
        include_base=include_base,
        include_groups=include_groups,
        lag_series=lag_series,
        lag_steps=lag_steps,
        feature_profile=feature_profile,
        max_train_rows=max_train_rows,
    )
    eval_unpruned, eval_sparsify, metrics_path = _warmup_and_sparsify(ctx, cfg=cfg, warmup_update_grid=warmup_update_grid)
    model, best, sparsity, model_width = _prune_and_refine(ctx, cfg=cfg, metrics_path=metrics_path, eval_sparsify=eval_sparsify)
    return _finalize(
        ctx,
        model=model,
        best=best,
        eval_unpruned=eval_unpruned,
        eval_sparsify=eval_sparsify,
        sparsity=sparsity,
        model_width=model_width,
    )
