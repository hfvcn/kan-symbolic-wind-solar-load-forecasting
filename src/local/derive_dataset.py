from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.derived import (
    ZScoreStats,
    add_daylight_ghi_feature,
    add_degree_features,
    add_ghi_temp_corrected_feature,
    add_wind_cubic_feature,
    add_wind_hub_feature,
    apply_zscore,
    compute_delta,
    compute_net_load,
    extend_scaler_params,
    fit_zscore,
    normalize_horizon_steps,
)
from src.data.split import inverse_transform, load_splits_from_parquet, save_splits_to_parquet
from src.config import MAX_HORIZON_STEPS
from src.local.run_contract import ensure_run_dirs, utc_run_id, write_json


@dataclass(frozen=True)
class DeriveDatasetConfig:
    degree_base_c: float = 18.0
    horizon_steps: list[int] | None = None
    net_load_lag_steps: list[int] | None = None
    add_physics_proxies: bool = True
    add_hub_wind: bool = True       # hub-height wind speed (power-law extrapolation)
    add_temp_ghi: bool = True       # temperature-corrected GHI
    add_absolute_targets: bool = True  # add wind_h{n} / solar_h{n} / net_load_h{n}


def _load_scaler_params(runs_root: Path, data_run_id: str) -> dict[str, Any]:
    path = Path(runs_root) / str(data_run_id) / "artifacts" / "scaler_params.json"
    if not path.exists():
        raise FileNotFoundError(f"scaler_params.json not found: {path}")
    return json.loads(path.read_text())


def _require_cols(df: pd.DataFrame, cols: list[str], *, context: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {context}: {missing}")


def _resolve_processed_timestamp(processed_dir: Path, timestamp: str | None) -> str:
    if timestamp:
        return str(timestamp)
    train_files = sorted(Path(processed_dir).glob("train_*.parquet"))
    if not train_files:
        raise FileNotFoundError(f"No train parquet files found in: {processed_dir}")
    return train_files[-1].stem.replace("train_", "")


def _base_raw(df: pd.DataFrame, *, scaler_params: dict[str, Any]) -> pd.DataFrame:
    return inverse_transform(df[["load", "wind", "solar"]], scaler_params)

def add_targets(df: pd.DataFrame, *, horizons: list[int], scaler_params: dict[str, Any], add_absolute: bool = False) -> pd.DataFrame:
    b = _base_raw(df, scaler_params=scaler_params)
    out = df.copy()
    out["net_load"] = compute_net_load(b["load"], b["wind"], b["solar"])
    for h in horizons:
        out[f"delta_load_h{h}"] = compute_delta(b["load"], b["load"].shift(h))
        out[f"delta_wind_h{h}"] = compute_delta(b["wind"], b["wind"].shift(h))
        out[f"delta_solar_h{h}"] = compute_delta(b["solar"], b["solar"].shift(h))
        out[f"delta_net_load_h{h}"] = compute_delta(out["net_load"], out["net_load"].shift(h))
        # Absolute-level targets: actual generation at time t (i.e. t-h lagged = current, non-differenced)
        if add_absolute:
            out[f"wind_h{h}"] = b["wind"]          # wind power at t (MW)
            out[f"solar_h{h}"] = b["solar"]        # solar power at t (MW)
            out[f"net_load_h{h}"] = out["net_load"] # net load at t (MW)
    out["delta_load"] = out["delta_load_h1"]
    out["delta_net_load"] = out["delta_net_load_h1"]
    return out


def add_net_load_lags(
    df: pd.DataFrame,
    *,
    net_steps: list[int],
    stats: dict[str, ZScoreStats] | None,
) -> tuple[pd.DataFrame, dict[str, ZScoreStats]]:
    if "net_load" not in df.columns:
        raise ValueError("Missing required column for net_load lags: net_load")
    out = df.copy()
    new_stats: dict[str, ZScoreStats] = {}
    for k in net_steps:
        raw = out["net_load"].shift(int(k))
        name = f"net_load_lag_{k}"
        s = stats[name] if stats and name in stats else fit_zscore(raw)
        new_stats[name] = s
        out[name] = apply_zscore(raw, s)
    return out, new_stats


def add_engineered_features(
    df: pd.DataFrame,
    *,
    scaler_params: dict[str, Any],
    cfg: DeriveDatasetConfig,
    stats: dict[str, ZScoreStats] | None,
) -> tuple[pd.DataFrame, dict[str, ZScoreStats]]:
    if not bool(cfg.add_physics_proxies):
        return df.copy(), {}

    required = ["temp_2m_c", "wind_speed_10m_m_s", "ghi_w_m2", "is_night"]
    _require_cols(df, required, context="engineered feature inputs")

    met_raw = inverse_transform(df[["temp_2m_c", "wind_speed_10m_m_s", "ghi_w_m2"]], scaler_params)
    work = pd.DataFrame(index=df.index)
    work["temp_2m_c"] = met_raw["temp_2m_c"]
    work["wind_speed_10m_m_s"] = met_raw["wind_speed_10m_m_s"]
    work["ghi_w_m2"] = met_raw["ghi_w_m2"]
    work["is_night"] = df["is_night"].astype(bool)
    work = add_wind_cubic_feature(work)
    work = add_daylight_ghi_feature(work)
    work = add_degree_features(work, base_c=float(cfg.degree_base_c))
    # New physical features
    if bool(cfg.add_hub_wind):
        work = add_wind_hub_feature(work)          # v_hub = v_10m * (100/10)^0.14
    if bool(cfg.add_temp_ghi):
        work = add_ghi_temp_corrected_feature(work)  # ghi * (1 - 0.004*(T-25)) * daytime

    out = df.copy()
    engineered_cols = ["wind_speed_10m_m_s_cubed", "ghi_day_w_m2", "cdd_18c", "hdd_18c"]
    if bool(cfg.add_hub_wind):
        engineered_cols.append("wind_speed_hub_est")
    if bool(cfg.add_temp_ghi):
        engineered_cols.append("ghi_temp_corr_w_m2")
    new_stats: dict[str, ZScoreStats] = {}
    for col in engineered_cols:
        raw = work[col]
        s = stats[col] if stats and col in stats else fit_zscore(raw)
        new_stats[col] = s
        out[col] = apply_zscore(raw, s)
    return out, new_stats


def _target_cols(horizons: list[int]) -> list[str]:
    cols: list[str] = ["net_load", "delta_load", "delta_net_load"]
    for h in horizons:
        cols.extend([f"delta_load_h{h}", f"delta_net_load_h{h}", f"delta_wind_h{h}", f"delta_solar_h{h}"])
    return cols


def _build_payload(
    *,
    run_id: str,
    source_data_run_id: str,
    source_timestamp: str | None,
    cfg: DeriveDatasetConfig,
    horizons: list[int],
    net_steps: list[int],
    timestamp: str,
    train_rows: int,
    val_rows: int,
    test_rows: int,
    engineered_feature_cols: list[str],
    paths: dict[str, str],
    artifacts_dir: Path,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "phase": "01.5-derived-dataset",
        "status": "completed",
        "source_data_run_id": str(source_data_run_id),
        "source_timestamp": source_timestamp,
        "cfg": asdict(cfg),
        "horizon_steps": list(horizons),
        "net_load_lag_steps": list(net_steps),
        "timestamp": timestamp,
        "rows": {"train": int(train_rows), "val": int(val_rows), "test": int(test_rows)},
        "added_columns": {
            "targets": sorted(set(_target_cols(horizons))),
            "net_load_lags": [f"net_load_lag_{k}" for k in net_steps],
            "engineered_features": sorted(list(engineered_feature_cols)),
        },
        "paths": paths,
        "artifacts_dir": str(artifacts_dir),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def derive_dataset_local(
    source_data_run_id: str,
    *,
    runs_root: Path,
    source_timestamp: str | None = None,
    run_id: str | None = None,
    cfg: DeriveDatasetConfig = DeriveDatasetConfig(),
) -> dict[str, Any]:
    run_id = run_id or utc_run_id()
    dirs = ensure_run_dirs(Path(runs_root), run_id)

    src_processed = Path(runs_root) / str(source_data_run_id) / "processed"
    if not src_processed.exists():
        raise FileNotFoundError(f"Source processed dir not found: {src_processed}")

    scaler_params = _load_scaler_params(Path(runs_root), str(source_data_run_id))
    resolved_source_ts = _resolve_processed_timestamp(src_processed, source_timestamp)
    train_df, val_df, test_df = load_splits_from_parquet(src_processed, timestamp=resolved_source_ts)

    horizons = normalize_horizon_steps(cfg.horizon_steps, max_steps=MAX_HORIZON_STEPS, include_1=True)
    net_steps = sorted({*horizons, *(cfg.net_load_lag_steps or [1, 12, 48])})

    _require_cols(train_df, ["load", "wind", "solar"], context="processed splits")
    _require_cols(val_df, ["load", "wind", "solar"], context="processed splits")
    _require_cols(test_df, ["load", "wind", "solar"], context="processed splits")

    train_df2 = add_targets(train_df, horizons=horizons, scaler_params=scaler_params, add_absolute=bool(cfg.add_absolute_targets))
    val_df2 = add_targets(val_df, horizons=horizons, scaler_params=scaler_params, add_absolute=bool(cfg.add_absolute_targets))
    test_df2 = add_targets(test_df, horizons=horizons, scaler_params=scaler_params, add_absolute=bool(cfg.add_absolute_targets))

    train_df3, nl_stats = add_net_load_lags(train_df2, net_steps=net_steps, stats=None)
    val_df3, _ = add_net_load_lags(val_df2, net_steps=net_steps, stats=nl_stats)
    test_df3, _ = add_net_load_lags(test_df2, net_steps=net_steps, stats=nl_stats)

    # Remove initial rows where shift-based targets/lags are undefined (avoids cross-split leakage).
    nan_cols = ["delta_load", "delta_net_load"]
    for h in horizons:
        nan_cols += [f"delta_load_h{h}", f"delta_net_load_h{h}", f"delta_wind_h{h}", f"delta_solar_h{h}"]
    nan_cols += [f"net_load_lag_{k}" for k in net_steps]
    train_df3 = train_df3.dropna(subset=nan_cols).copy()
    val_df3 = val_df3.dropna(subset=nan_cols).copy()
    test_df3 = test_df3.dropna(subset=nan_cols).copy()

    train_df4, eng_stats = add_engineered_features(train_df3, scaler_params=scaler_params, cfg=cfg, stats=None)
    val_df4, _ = add_engineered_features(val_df3, scaler_params=scaler_params, cfg=cfg, stats=eng_stats)
    test_df4, _ = add_engineered_features(test_df3, scaler_params=scaler_params, cfg=cfg, stats=eng_stats)

    merged_stats: dict[str, ZScoreStats] = {**nl_stats, **eng_stats}
    scaler_params2 = extend_scaler_params(scaler_params, merged_stats)
    write_json(dirs.artifacts_dir / "scaler_params.json", scaler_params2)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    paths = save_splits_to_parquet(train_df4, val_df4, test_df4, dirs.processed_dir, timestamp)

    payload = _build_payload(run_id=run_id, source_data_run_id=str(source_data_run_id), source_timestamp=resolved_source_ts, cfg=cfg, horizons=horizons, net_steps=net_steps, timestamp=timestamp, train_rows=len(train_df4), val_rows=len(val_df4), test_rows=len(test_df4), engineered_feature_cols=list(eng_stats.keys()), paths=paths, artifacts_dir=dirs.artifacts_dir)
    write_json(dirs.run_dir / "payload.json", payload)
    return payload
