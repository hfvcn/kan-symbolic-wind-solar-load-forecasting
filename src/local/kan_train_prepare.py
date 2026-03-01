from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.data.split import load_splits_from_parquet
from src.kan_sr.dataset import build_kan_dataset, pick_feature_columns
from src.local.kan_train_config import TrainConfig
from src.local.kan_train_core import move_dataset_to_device, torch_env_info


@dataclass(frozen=True)
class PreparedData:
    feature_cols: list[str]
    dataset: dict[str, Any]
    target_scaler: dict[str, float] | None


def downsample_train_df(train_df, *, max_train_rows: int | None):
    if max_train_rows is None or len(train_df) <= int(max_train_rows):
        return train_df
    return train_df.iloc[: int(max_train_rows)].copy()


def resolve_timestamp(processed_dir: Path, timestamp: str | None) -> str:
    if timestamp is not None:
        return str(timestamp)
    train_files = sorted(Path(processed_dir).glob("train_*.parquet"))
    if not train_files:
        raise FileNotFoundError(f"No train Parquet files found in {processed_dir}")
    return train_files[-1].stem.replace("train_", "")


def normalize_feature_settings(
    *,
    include_groups: list[str] | None,
    lag_series: list[str] | None,
    lag_steps: list[int] | None,
) -> tuple[list[str], list[str], list[int]]:
    groups = include_groups or ["meteorology", "solar", "cyclic"]
    series = lag_series or ["load", "wind", "solar"]
    steps = lag_steps or [1, 12, 48]
    return list(groups), list(series), [int(s) for s in steps]


def load_splits(
    *,
    processed_dir: Path,
    data_timestamp: str | None,
    max_train_rows: int | None,
) -> tuple[str, Any, Any, Any]:
    resolved_ts = resolve_timestamp(processed_dir, data_timestamp)
    train_df, val_df, test_df = load_splits_from_parquet(processed_dir, timestamp=resolved_ts)
    train_df = downsample_train_df(train_df, max_train_rows=max_train_rows)
    return resolved_ts, train_df, val_df, test_df


def pick_features(
    train_df,
    *,
    cfg: TrainConfig,
    include_base: bool,
    include_groups: list[str],
    lag_series: list[str],
    lag_steps: list[int],
) -> list[str]:
    return pick_feature_columns(
        train_df,
        target_col=str(cfg.target_col),
        include_base=bool(include_base),
        include_groups=include_groups,
        lag_steps=lag_steps,
        lag_series=lag_series,
    )


def prepare_data(
    *,
    train_df,
    val_df,
    cfg: TrainConfig,
    include_base: bool,
    include_groups: list[str],
    lag_series: list[str],
    lag_steps: list[int],
    device: str,
) -> PreparedData:
    feature_cols = pick_features(
        train_df,
        cfg=cfg,
        include_base=include_base,
        include_groups=include_groups,
        lag_series=lag_series,
        lag_steps=lag_steps,
    )
    dataset, ds_meta = build_kan_dataset(
        train_df,
        val_df,
        target_col=str(cfg.target_col),
        feature_cols=feature_cols,
        scale_target=True,
    )
    return PreparedData(
        feature_cols=feature_cols,
        dataset=move_dataset_to_device(dataset, device),
        target_scaler=ds_meta.get("target_scaler"),
    )


def build_model(*, in_dim: int, cfg: TrainConfig, device: str):
    from kan import KAN

    hidden_sizes = [int(x) for x in cfg.hidden_layers] if cfg.hidden_layers else [int(cfg.hidden_width)]
    if not hidden_sizes or any(h <= 0 for h in hidden_sizes):
        raise ValueError(f"hidden_layers must be positive ints, got: {cfg.hidden_layers}")
    width = [[int(in_dim), 0], *[[h, int(cfg.hidden_mult)] for h in hidden_sizes], [1, 0]]
    return KAN(
        width=width,
        grid=int(cfg.grid),
        k=int(cfg.k),
        mult_arity=int(cfg.mult_arity),
        grid_range=[float(cfg.grid_range_min), float(cfg.grid_range_max)],
        seed=int(cfg.seed),
        auto_save=False,
        device=device,
    )


def build_payload(
    *,
    run_id: str,
    kind: str | None,
    data_run_id: str,
    data_timestamp: str,
    cfg: TrainConfig,
    prepared: PreparedData,
    include_groups: list[str],
    include_base: bool,
    lag_series: list[str],
    lag_steps: list[int],
    max_train_rows: int | None,
    device: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "phase": "02-kan-training",
        "kind": str(kind or "kan"),
        "data_run_id": str(data_run_id),
        "data_timestamp": str(data_timestamp),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "cfg": asdict(cfg),
        "feature_cols": list(prepared.feature_cols),
        "target_scaler": prepared.target_scaler,
        "lag_steps": list(lag_steps),
        "lag_series": list(lag_series),
        "include_groups": list(include_groups),
        "include_base": bool(include_base),
        "max_train_rows": max_train_rows,
        "device": device,
        "env": torch_env_info(),
    }
