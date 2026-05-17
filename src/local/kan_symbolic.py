from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from src.data.split import inverse_transform, load_splits_from_parquet
from src.eval.physics_mapping import analyze_physics
from src.eval.symbolic_formula import compute_eval_clip_bounds, evaluate_symbolic_split
from src.kan_sr.feature_scaling import compose_affine_normalizers, transform_feature_frame
from src.kan_sr.symbolic import (
    DEFAULT_SYMBOLIC_LIB,
    build_symbolic_formula,
    extract_symbolic_edges,
    prime_symbolic_activations,
    sympy_complexity,
)
from src.local.run_contract import ensure_run_dirs, utc_run_id, write_json


@dataclass(frozen=True)
class SymbolicConfig:
    r2_threshold: float = 0.999
    weight_simple: float = 0.9
    fix_below_threshold_to_zero: bool = False
    sample_rows: int = 20_000
    lib: list[str] | None = None
    safe_exp_clip: float | None = None
    eval_clip_quantiles: tuple[float, float] | None = None
    device_name: str = "cpu"  # cpu | cuda


def _load_scaler_params(runs_root: Path, data_run_id: str) -> dict[str, Any]:
    path = Path(runs_root) / str(data_run_id) / "artifacts" / "scaler_params.json"
    if not path.exists():
        raise FileNotFoundError(f"scaler_params.json not found: {path}")
    return json.loads(path.read_text())


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
            continue
        i = idx[c]
        means.append(float(mean[i]))
        stds.append(float(scale[i]))

    return {"mean": means, "std": stds, "missing": missing}


def _infer_model_width(in_dim: int, ckpt: dict[str, Any], *, fallback_hidden_width: int, hidden_mult: int) -> list[list[int]]:
    model_width = ckpt.get("model_width") or (ckpt.get("payload") or {}).get("model_width")
    if model_width:
        return [[int(a), int(b)] for a, b in model_width]

    sd = ckpt.get("model_state", {})
    inferred_hidden = None
    if "node_bias_0" in sd:
        inferred_hidden = int(sd["node_bias_0"].shape[0])
    elif "act_fun.0.mask" in sd:
        inferred_hidden = int(sd["act_fun.0.mask"].shape[1])
    return [[int(in_dim), 0], [int(inferred_hidden or fallback_hidden_width), int(hidden_mult)], [1, 0]]


def _pick_device(device_name: str) -> str:
    import torch

    dn = str(device_name).strip().lower()
    if dn not in {"cpu", "cuda"}:
        raise ValueError(f"device_name must be 'cpu' or 'cuda', got: {device_name!r}")
    if dn == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Requested CUDA device but torch.cuda.is_available() is False")
    return dn


def _load_ckpt(path: Path) -> dict[str, Any]:
    import torch

    if not Path(path).exists():
        raise FileNotFoundError(f"Phase 2 checkpoint not found: {path}")
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def _build_kan_model(*, feature_cols: list[str], train_cfg: dict[str, Any], ckpt: dict[str, Any], device: str):
    from kan import KAN

    in_dim = len(feature_cols)
    hidden_width = int(train_cfg.get("hidden_width", 10))
    hidden_mult = int(train_cfg.get("hidden_mult", 0))
    width = _infer_model_width(in_dim, ckpt, fallback_hidden_width=hidden_width, hidden_mult=hidden_mult)

    model = KAN(
        width=width,
        grid=int(train_cfg.get("grid", 5)),
        k=int(train_cfg.get("k", 3)),
        mult_arity=int(train_cfg.get("mult_arity", 2)),
        grid_range=[float(train_cfg.get("grid_range_min", -5.0)), float(train_cfg.get("grid_range_max", 5.0))],
        seed=int(train_cfg.get("seed", 1)),
        auto_save=False,
        device=device,
    )
    model.load_state_dict(ckpt["model_state"], strict=True)
    return model


def _save_artifacts(
    *,
    artifacts_dir: Path,
    edge_fits,
    expr,
    formula_complexity: dict[str, Any],
    physics_report: dict[str, Any] | None,
    eval_val_metrics: dict[str, float] | None,
    eval_test_metrics: dict[str, float] | None,
    test_pred_df,
) -> None:
    import pandas as pd
    import sympy as sp

    pd.DataFrame([e.as_dict() for e in edge_fits]).to_csv(Path(artifacts_dir) / "edge_symbolic_report.csv", index=False)
    (Path(artifacts_dir) / "formula.sympy.txt").write_text(str(expr))
    (Path(artifacts_dir) / "formula.tex").write_text(sp.latex(expr))
    write_json(Path(artifacts_dir) / "formula_metrics.json", formula_complexity)
    if physics_report is not None:
        write_json(Path(artifacts_dir) / "physics_mapping.json", physics_report)
    if eval_val_metrics is not None:
        write_json(Path(artifacts_dir) / "formula_eval_val.json", eval_val_metrics)
    if eval_test_metrics is not None:
        write_json(Path(artifacts_dir) / "formula_eval_test.json", eval_test_metrics)
    test_pred_df.to_parquet(Path(artifacts_dir) / "predictions_test.parquet", compression="snappy")


def _build_payload(
    *,
    run_id: str,
    train_run_id: str,
    data_run_id: str,
    data_timestamp: str,
    target_col: str,
    cfg: SymbolicConfig,
    feature_cols: list[str],
    eval_val_metrics: dict[str, float],
    eval_test_metrics: dict[str, float],
    complexity: dict[str, Any],
    physics_mapping_score: float | None,
) -> dict[str, Any]:
    return {
        "run_id": str(run_id),
        "phase": "03-symbolic",
        "status": "completed",
        "train_run_id": str(train_run_id),
        "data_run_id": str(data_run_id),
        "data_timestamp": str(data_timestamp),
        "target_col": str(target_col),
        "cfg": asdict(cfg),
        "feature_cols": list(feature_cols),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "results": {
            "eval_val": dict(eval_val_metrics),
            "eval_test": dict(eval_test_metrics),
            "complexity": dict(complexity),
        },
        "physics_mapping_score": physics_mapping_score,
    }


def extract_symbolic_local(
    train_run_id: str,
    *,
    runs_root: Path,
    run_id: str | None = None,
    cfg: SymbolicConfig = SymbolicConfig(),
) -> dict[str, Any]:
    import torch

    device_s = _pick_device(cfg.device_name)
    run_id = run_id or utc_run_id()
    dirs = ensure_run_dirs(Path(runs_root), run_id)

    ckpt_path = Path(runs_root) / str(train_run_id) / "checkpoint" / "model.pt"
    ckpt = _load_ckpt(ckpt_path)

    payload = ckpt.get("payload", {})
    feature_cols = list(ckpt["feature_cols"])
    feature_scaler = ckpt.get("feature_scaler")
    target_scaler = ckpt.get("target_scaler")
    train_cfg = payload.get("cfg", {})

    data_run_id = payload["data_run_id"]
    data_timestamp = payload["data_timestamp"]
    target_col = str(train_cfg.get("target_col") or payload.get("target_col") or "load")

    scaler_params = _load_scaler_params(Path(runs_root), str(data_run_id))
    input_norm = compose_affine_normalizers(_load_scaler_for_features(scaler_params, feature_cols), feature_scaler)
    output_norm = {"mean": [float(target_scaler["mean"])], "std": [float(target_scaler["std"])]} if target_scaler is not None else None

    model = _build_kan_model(feature_cols=feature_cols, train_cfg=train_cfg, ckpt=ckpt, device=device_s)

    processed_dir = Path(runs_root) / str(data_run_id) / "processed"
    train_df, val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=str(data_timestamp))
    if cfg.sample_rows is not None and len(train_df) > int(cfg.sample_rows):
        train_df = train_df.sample(n=int(cfg.sample_rows), random_state=1).sort_index()

    x_sample_np = transform_feature_frame(train_df, feature_cols, feature_scaler)
    x_sample = torch.tensor(x_sample_np, device=device_s)
    model, x_sample = prime_symbolic_activations(model, x_sample, device_name=device_s, torch_mod=torch)

    edge_fits = extract_symbolic_edges(model, lib=cfg.lib or DEFAULT_SYMBOLIC_LIB, r2_threshold=float(cfg.r2_threshold), weight_simple=float(cfg.weight_simple), fix_below_threshold_to_zero=bool(cfg.fix_below_threshold_to_zero))
    expr = build_symbolic_formula(model, feature_cols=feature_cols, input_normalizer=input_norm, output_normalizer=output_norm)

    clip_bounds = compute_eval_clip_bounds(
        train_df=train_df,
        feature_cols=feature_cols,
        scaler_params=scaler_params,
        eval_clip_quantiles=cfg.eval_clip_quantiles,
    )
    if clip_bounds is not None:
        write_json(
            Path(dirs.artifacts_dir) / "eval_input_clip.json",
            {
                "quantiles": [float(cfg.eval_clip_quantiles[0]), float(cfg.eval_clip_quantiles[1])],
                "bounds": {
                    col: {"low": float(bounds[0]), "high": float(bounds[1])}
                    for col, bounds in clip_bounds.items()
                },
            },
        )

    try:
        val_eval = evaluate_symbolic_split(
            split_name="val",
            expr=expr,
            split_df=val_df,
            feature_cols=feature_cols,
            scaler_params=scaler_params,
            target_col=target_col,
            safe_exp_clip=cfg.safe_exp_clip,
            clip_bounds=clip_bounds,
        )
        test_eval = evaluate_symbolic_split(
            split_name="test",
            expr=expr,
            split_df=test_df,
            feature_cols=feature_cols,
            scaler_params=scaler_params,
            target_col=target_col,
            safe_exp_clip=cfg.safe_exp_clip,
            clip_bounds=clip_bounds,
        )
    except RuntimeError as exc:
        write_json(Path(dirs.artifacts_dir) / "formula_eval_nonfinite.json", {"error": str(exc)})
        raise
    complexity = sympy_complexity(expr)
    x_test_orig = inverse_transform(test_df[feature_cols], scaler_params).astype(np.float64)
    physics_report = analyze_physics(
        expr,
        feature_cols=feature_cols,
        x_df=x_test_orig,
        target_col=target_col,
    )

    _save_artifacts(
        artifacts_dir=dirs.artifacts_dir,
        edge_fits=edge_fits,
        expr=expr,
        formula_complexity=complexity,
        physics_report=physics_report,
        eval_val_metrics=val_eval.metrics,
        eval_test_metrics=test_eval.metrics,
        test_pred_df=test_eval.predictions,
    )
    out_payload = _build_payload(
        run_id=run_id,
        train_run_id=str(train_run_id),
        data_run_id=str(data_run_id),
        data_timestamp=str(data_timestamp),
        target_col=target_col,
        cfg=cfg,
        feature_cols=feature_cols,
        eval_val_metrics=val_eval.metrics,
        eval_test_metrics=test_eval.metrics,
        complexity=complexity,
        physics_mapping_score=float(physics_report.get("score")) if physics_report.get("score") is not None else None,
    )
    write_json(dirs.run_dir / "payload.json", out_payload)
    return out_payload
