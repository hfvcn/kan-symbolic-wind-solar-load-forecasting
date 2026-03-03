"""
Derived dataset builder (Phase 1.5) as a Modal job.

This job takes an existing Phase-1 `data_run_id` (processed splits + scaler_params)
and produces a new data run with extra target columns + engineered features
for delta/net-load/horizon experiments.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


APP_NAME = "kan-sr-derive-dataset"
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
        "numpy>=1.24",
        "pandas>=2.0",
        "pyarrow>=14.0",
        "scikit-learn>=1.3",
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


def _parse_csv_ints(s: str, *, name: str) -> list[int]:
    raw = [p.strip() for p in str(s).split(",") if p.strip()]
    out: list[int] = []
    for p in raw:
        try:
            out.append(int(p))
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Invalid int in {name}: {p!r}") from e
    return out


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=1800)
def derive_dataset(
    source_data_run_id: str,
    *,
    source_timestamp: str | None = None,
    run_id: str | None = None,
    degree_base_c: float = 18.0,
    horizon_steps: list[int] | None = None,
    net_load_lag_steps: list[int] | None = None,
    add_physics_proxies: bool = True,
    add_hub_wind: bool = True,
    add_temp_ghi: bool = True,
    add_absolute_targets: bool = True,
) -> dict[str, Any]:
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

    run_id = run_id or _utc_run_id()
    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    processed_dir = run_dir / "processed"
    artifacts_dir = run_dir / "artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    src_run_dir = Path(VOLUME_MOUNT) / "runs" / source_data_run_id
    src_processed = src_run_dir / "processed"
    if not src_processed.exists():
        raise FileNotFoundError(f"Source processed dir not found: {src_processed}")

    scaler_path = src_run_dir / "artifacts" / "scaler_params.json"
    if not scaler_path.exists():
        raise FileNotFoundError(f"Source scaler_params.json not found: {scaler_path}")
    scaler_params = json.loads(scaler_path.read_text())

    train_df, val_df, test_df = load_splits_from_parquet(src_processed, timestamp=source_timestamp)

    horizons = normalize_horizon_steps(horizon_steps, max_steps=48, include_1=True)

    # Base series (may be normalized or raw depending on source run); inverse_transform
    # makes this robust by only touching columns present in scaler_params.feature_names.
    def base_raw(df: pd.DataFrame) -> pd.DataFrame:
        cols = [c for c in ["load", "wind", "solar"] if c in df.columns]
        if len(cols) != 3:
            missing = sorted(set(["load", "wind", "solar"]) - set(cols))
            raise ValueError(f"Missing required base columns in processed split: {missing}")
        return inverse_transform(df[cols], scaler_params)

    def lag_raw(df: pd.DataFrame, steps: list[int]) -> pd.DataFrame:
        cols: list[str] = []
        for series in ("load", "wind", "solar"):
            for k in steps:
                name = f"{series}_lag_{k}"
                if name not in df.columns:
                    raise ValueError(f"Missing required lag column in processed split: {name}")
                cols.append(name)
        return inverse_transform(df[cols], scaler_params)

    net_steps = sorted({*horizons, *(net_load_lag_steps or [1, 12, 48])})

    def add_targets(df: pd.DataFrame) -> pd.DataFrame:
        b = base_raw(df)
        lags = lag_raw(df, steps=horizons)
        out = df.copy()
        out["net_load"] = compute_net_load(b["load"], b["wind"], b["solar"])
        for h in horizons:
            out[f"delta_load_h{h}"] = compute_delta(b["load"], lags[f"load_lag_{h}"])
            out[f"delta_wind_h{h}"] = compute_delta(b["wind"], lags[f"wind_lag_{h}"])
            out[f"delta_solar_h{h}"] = compute_delta(b["solar"], lags[f"solar_lag_{h}"])
            nl_lag_h = compute_net_load(lags[f"load_lag_{h}"], lags[f"wind_lag_{h}"], lags[f"solar_lag_{h}"])
            out[f"delta_net_load_h{h}"] = compute_delta(out["net_load"], nl_lag_h)
            if add_absolute_targets:
                out[f"wind_h{h}"] = b["wind"]
                out[f"solar_h{h}"] = b["solar"]
                out[f"net_load_h{h}"] = out["net_load"]
        out["delta_load"] = out["delta_load_h1"]
        out["delta_net_load"] = out["delta_net_load_h1"]
        return out

    train_df2 = add_targets(train_df)
    val_df2 = add_targets(val_df)
    test_df2 = add_targets(test_df)

    # Optional: derived lag features for net_load (small subset, normalized).
    def add_net_load_lags(df: pd.DataFrame, *, stats: dict[str, ZScoreStats] | None = None) -> tuple[pd.DataFrame, dict[str, ZScoreStats]]:
        lags = lag_raw(df, steps=net_steps)

        raw_cols: dict[str, pd.Series] = {}
        for k in net_steps:
            nl = compute_net_load(lags[f"load_lag_{k}"], lags[f"wind_lag_{k}"], lags[f"solar_lag_{k}"])
            raw_cols[f"net_load_lag_{k}"] = nl

        out = df.copy()
        new_stats: dict[str, ZScoreStats] = {}
        for name, raw in raw_cols.items():
            s = stats[name] if stats and name in stats else fit_zscore(raw)
            new_stats[name] = s
            out[name] = apply_zscore(raw, s)

        # Keep raw net_load itself (target) untouched.
        return out, new_stats

    # Optional: physics proxy features (normalized).
    def add_engineered_features(
        df: pd.DataFrame,
        *,
        stats: dict[str, ZScoreStats] | None = None,
    ) -> tuple[pd.DataFrame, dict[str, ZScoreStats]]:
        out = df.copy()
        if not add_physics_proxies:
            return out, {}

        required = ["temp_2m_c", "wind_speed_10m_m_s", "ghi_w_m2", "is_night"]
        missing = [c for c in required if c not in out.columns]
        if missing:
            raise ValueError(f"Missing required meteo/solar columns for engineered features: {missing}")

        met_raw = inverse_transform(out[["temp_2m_c", "wind_speed_10m_m_s", "ghi_w_m2"]], scaler_params)
        work = pd.DataFrame(index=out.index)
        work["temp_2m_c"] = met_raw["temp_2m_c"]
        work["wind_speed_10m_m_s"] = met_raw["wind_speed_10m_m_s"]
        work["ghi_w_m2"] = met_raw["ghi_w_m2"]
        work["is_night"] = out["is_night"].astype(bool)

        work = add_wind_cubic_feature(work)
        work = add_daylight_ghi_feature(work)
        work = add_degree_features(work, base_c=float(degree_base_c))
        if add_hub_wind:
            work = add_wind_hub_feature(work)
        if add_temp_ghi:
            work = add_ghi_temp_corrected_feature(work)

        engineered_cols = ["wind_speed_10m_m_s_cubed", "ghi_day_w_m2", "cdd_18c", "hdd_18c"]
        if add_hub_wind:
            engineered_cols.append("wind_speed_hub_est")
        if add_temp_ghi:
            engineered_cols.append("ghi_temp_corr_w_m2")
        new_stats: dict[str, ZScoreStats] = {}
        for col in engineered_cols:
            raw = work[col]
            s = stats[col] if stats and col in stats else fit_zscore(raw)
            new_stats[col] = s
            out[col] = apply_zscore(raw, s)
        return out, new_stats

    # Fit stats on train for new normalized features; apply consistently to val/test.
    train_df3, nl_stats = add_net_load_lags(train_df2, stats=None)
    val_df3, _ = add_net_load_lags(val_df2, stats=nl_stats)
    test_df3, _ = add_net_load_lags(test_df2, stats=nl_stats)

    train_df4, eng_stats = add_engineered_features(train_df3, stats=None)
    val_df4, _ = add_engineered_features(val_df3, stats=eng_stats)
    test_df4, _ = add_engineered_features(test_df3, stats=eng_stats)

    # Extend scaler params with new normalized feature cols.
    merged_stats: dict[str, ZScoreStats] = {**nl_stats, **eng_stats}
    scaler_params2 = extend_scaler_params(scaler_params, merged_stats)
    _write_json(artifacts_dir / "scaler_params.json", scaler_params2)

    # Save derived splits to parquet
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    paths = save_splits_to_parquet(train_df4, val_df4, test_df4, processed_dir, timestamp)

    target_cols = ["net_load", "delta_load", "delta_net_load"]
    for h in horizons:
        target_cols.extend([f"delta_load_h{h}", f"delta_net_load_h{h}", f"delta_wind_h{h}", f"delta_solar_h{h}"])
        if add_absolute_targets:
            target_cols.extend([f"wind_h{h}", f"solar_h{h}", f"net_load_h{h}"])

    out_payload = {
        "run_id": run_id,
        "phase": "01.5-derived-dataset",
        "status": "completed",
        "source_data_run_id": source_data_run_id,
        "source_timestamp": source_timestamp,
        "degree_base_c": float(degree_base_c),
        "horizon_steps": list(horizons),
        "net_load_lag_steps": list(net_steps),
        "add_physics_proxies": bool(add_physics_proxies),
        "add_hub_wind": bool(add_hub_wind),
        "add_temp_ghi": bool(add_temp_ghi),
        "add_absolute_targets": bool(add_absolute_targets),
        "timestamp": timestamp,
        "rows": {"train": int(len(train_df4)), "val": int(len(val_df4)), "test": int(len(test_df4))},
        "added_columns": {
            "targets": sorted(set(target_cols)),
            "net_load_lags": [f"net_load_lag_{k}" for k in net_steps],
            "engineered_features": list(eng_stats.keys()),
        },
        "paths": paths,
        "artifacts_dir": str(artifacts_dir),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(run_dir / "payload.json", out_payload)
    volume.commit()
    logger.info(f"Derived dataset created: {run_id} (from {source_data_run_id})")
    return out_payload


@app.local_entrypoint()
def main(
    source_data_run_id: str,
    source_timestamp: str = "",
    run_id: str = "",
    degree_base_c: float = 18.0,
    horizon_steps: str = "1",
    net_load_lag_steps: str = "1,12,48",
    add_physics_proxies: bool = True,
    add_hub_wind: bool = True,
    add_temp_ghi: bool = True,
    add_absolute_targets: bool = True,
) -> None:
    run_id_opt = run_id.strip() or None
    ts_opt = source_timestamp.strip() or None
    horizons = _parse_csv_ints(horizon_steps, name="horizon_steps")
    steps = _parse_csv_ints(net_load_lag_steps, name="net_load_lag_steps")
    result = derive_dataset.remote(
        source_data_run_id,
        source_timestamp=ts_opt,
        run_id=run_id_opt,
        degree_base_c=float(degree_base_c),
        horizon_steps=horizons,
        net_load_lag_steps=steps,
        add_physics_proxies=bool(add_physics_proxies),
        add_hub_wind=bool(add_hub_wind),
        add_temp_ghi=bool(add_temp_ghi),
        add_absolute_targets=bool(add_absolute_targets),
    )
    print(json.dumps(result, indent=2))
