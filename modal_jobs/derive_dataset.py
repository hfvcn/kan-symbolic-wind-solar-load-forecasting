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
    rolling_origin_index: int = -1,
    rolling_origin_step_steps: int = 0,
) -> dict[str, Any]:
    import pandas as pd

    from src.data.derived import (
        add_daylight_ghi_feature,
        add_degree_features,
        add_ghi_temp_corrected_feature,
        add_wind_cubic_feature,
        add_wind_hub_feature,
        compute_delta,
        compute_net_load,
        normalize_horizon_steps,
    )
    from src.data.derived_source import load_source_split_bundle
    from src.data.split import inverse_transform, normalize_features, save_splits_to_parquet
    from src.config import MAX_HORIZON_STEPS

    run_id = run_id or _utc_run_id()
    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    processed_dir = run_dir / "processed"
    artifacts_dir = run_dir / "artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    source_bundle = load_source_split_bundle(
        runs_root=Path(VOLUME_MOUNT) / "runs",
        source_data_run_id=str(source_data_run_id),
        source_timestamp=source_timestamp,
        rolling_origin_index=None if int(rolling_origin_index) < 0 else int(rolling_origin_index),
        rolling_origin_step_steps=None if int(rolling_origin_step_steps) <= 0 else int(rolling_origin_step_steps),
    )
    train_df = source_bundle.train_df
    val_df = source_bundle.val_df
    test_df = source_bundle.test_df
    scaler_params = source_bundle.scaler_params
    resolved_source_ts = source_bundle.source_timestamp

    horizons = normalize_horizon_steps(horizon_steps, max_steps=MAX_HORIZON_STEPS, include_1=True)

    def source_raw(df: pd.DataFrame) -> pd.DataFrame:
        # Recover all source features to a single raw-space contract before creating
        # derived targets/features. Otherwise a downstream target-role switch can mix
        # a previously excluded raw target column with already-normalized predictors.
        return inverse_transform(df, scaler_params)

    train_df = source_raw(train_df)
    val_df = source_raw(val_df)
    test_df = source_raw(test_df)

    net_steps = sorted({*horizons, *(net_load_lag_steps or [1, 12, 48])})

    def add_targets(df: pd.DataFrame) -> pd.DataFrame:
        cols = [c for c in ["load", "wind", "solar"] if c in df.columns]
        if len(cols) != 3:
            missing = sorted(set(["load", "wind", "solar"]) - set(cols))
            raise ValueError(f"Missing required base columns in processed split: {missing}")
        out = df.copy()
        out["net_load"] = compute_net_load(out["load"], out["wind"], out["solar"])
        for h in horizons:
            out[f"delta_load_h{h}"] = compute_delta(out["load"], out["load"].shift(h))
            out[f"delta_wind_h{h}"] = compute_delta(out["wind"], out["wind"].shift(h))
            out[f"delta_solar_h{h}"] = compute_delta(out["solar"], out["solar"].shift(h))
            out[f"delta_net_load_h{h}"] = compute_delta(out["net_load"], out["net_load"].shift(h))
            if add_absolute_targets:
                out[f"wind_h{h}"] = out["wind"]
                out[f"solar_h{h}"] = out["solar"]
                out[f"net_load_h{h}"] = out["net_load"]
        out["delta_load"] = out["delta_load_h1"]
        out["delta_net_load"] = out["delta_net_load_h1"]
        return out

    train_df2 = add_targets(train_df)
    val_df2 = add_targets(val_df)
    test_df2 = add_targets(test_df)

    # Optional: derived lag features for net_load (small subset, raw here; the final
    # normalize_features pass handles train-only standardization consistently).
    def add_net_load_lags(df: pd.DataFrame) -> pd.DataFrame:
        if "net_load" not in df.columns:
            raise ValueError("Missing required column for net_load lags: net_load")
        out = df.copy()
        for k in net_steps:
            out[f"net_load_lag_{k}"] = out["net_load"].shift(int(k))
        return out

    # Optional: physics proxy features (raw here; the final normalize_features pass
    # handles train-only standardization consistently).
    def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if not add_physics_proxies:
            return out

        required = ["temp_2m_c", "wind_speed_10m_m_s", "ghi_w_m2", "is_night"]
        missing = [c for c in required if c not in out.columns]
        if missing:
            raise ValueError(f"Missing required meteo/solar columns for engineered features: {missing}")

        work = pd.DataFrame(index=out.index)
        work["temp_2m_c"] = out["temp_2m_c"]
        work["wind_speed_10m_m_s"] = out["wind_speed_10m_m_s"]
        work["ghi_w_m2"] = out["ghi_w_m2"]
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
        for col in engineered_cols:
            out[col] = work[col]
        return out

    train_df3 = add_net_load_lags(train_df2)
    val_df3 = add_net_load_lags(val_df2)
    test_df3 = add_net_load_lags(test_df2)

    # Remove initial rows where shift-based targets/lags are undefined (avoids cross-split leakage).
    nan_cols = ["delta_load", "delta_net_load"]
    for h in horizons:
        nan_cols += [f"delta_load_h{h}", f"delta_net_load_h{h}", f"delta_wind_h{h}", f"delta_solar_h{h}"]
    nan_cols += [f"net_load_lag_{k}" for k in net_steps]
    train_df3 = train_df3.dropna(subset=nan_cols).copy()
    val_df3 = val_df3.dropna(subset=nan_cols).copy()
    test_df3 = test_df3.dropna(subset=nan_cols).copy()

    train_df4 = add_engineered_features(train_df3)
    val_df4 = add_engineered_features(val_df3)
    test_df4 = add_engineered_features(test_df3)

    target_cols = ["net_load", "delta_load", "delta_net_load"]
    for h in horizons:
        target_cols.extend([f"delta_load_h{h}", f"delta_net_load_h{h}", f"delta_wind_h{h}", f"delta_solar_h{h}"])
        if add_absolute_targets:
            target_cols.extend([f"wind_h{h}", f"solar_h{h}", f"net_load_h{h}"])

    train_df5, val_df5, test_df5, scaler_params2 = normalize_features(
        train_df4,
        val_df4,
        test_df4,
        exclude_cols=sorted(set(target_cols)),
    )
    _write_json(artifacts_dir / "scaler_params.json", scaler_params2)
    _write_json(artifacts_dir / "split_manifest.json", source_bundle.split_manifest)

    # Save derived splits to parquet
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    paths = save_splits_to_parquet(train_df5, val_df5, test_df5, processed_dir, timestamp)

    engineered_cols = ["wind_speed_10m_m_s_cubed", "ghi_day_w_m2", "cdd_18c", "hdd_18c"]
    if add_hub_wind:
        engineered_cols.append("wind_speed_hub_est")
    if add_temp_ghi:
        engineered_cols.append("ghi_temp_corr_w_m2")

    out_payload = {
        "run_id": run_id,
        "phase": "01.5-derived-dataset",
        "status": "completed",
        "source_data_run_id": source_data_run_id,
        "source_timestamp": resolved_source_ts,
        "degree_base_c": float(degree_base_c),
        "horizon_steps": list(horizons),
        "net_load_lag_steps": list(net_steps),
        "add_physics_proxies": bool(add_physics_proxies),
        "add_hub_wind": bool(add_hub_wind),
        "add_temp_ghi": bool(add_temp_ghi),
        "add_absolute_targets": bool(add_absolute_targets),
        "timestamp": timestamp,
        "rows": {"train": int(len(train_df5)), "val": int(len(val_df5)), "test": int(len(test_df5))},
        "added_columns": {
            "targets": sorted(set(target_cols)),
            "net_load_lags": [f"net_load_lag_{k}" for k in net_steps],
            "engineered_features": engineered_cols,
        },
        "paths": paths,
        "artifacts_dir": str(artifacts_dir),
        "source_split": source_bundle.split_manifest,
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
    rolling_origin_index: int = -1,
    rolling_origin_step_steps: int = 0,
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
        rolling_origin_index=int(rolling_origin_index),
        rolling_origin_step_steps=int(rolling_origin_step_steps),
    )
    print(json.dumps(result, indent=2))
