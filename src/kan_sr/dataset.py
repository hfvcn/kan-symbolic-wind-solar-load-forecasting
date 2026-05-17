from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd

from src.kan_sr.feature_scaling import fit_feature_scaler, transform_feature_matrix

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


DEFAULT_FEATURE_PROFILE = "default"
THESIS_26_FEATURE_PROFILE = "thesis_26"

FEATURE_PROFILE_EXCLUDED_COLUMNS: dict[str, tuple[str, ...]] = {
    DEFAULT_FEATURE_PROFILE: (),
    THESIS_26_FEATURE_PROFILE: (
        "wind_speed_hub_est",
        "ghi_temp_corr_w_m2",
    ),
    "load_no_month_cyclic": (
        "month_sin",
        "month_cos",
    ),
    "no_lag": (),
    "limited_lag": (),
    "reduced": (),
    "solar_core": (),
    "trend_core": (),
    "seasonal_core": (),
}


@dataclass(frozen=True)
class _ProfileConfig:
    """Override bundle applied by pick_feature_columns when a profile is active."""

    lag_steps: tuple[int, ...] | None = None  # None = use caller default
    include_base: bool | None = None          # None = use caller default
    include_groups: tuple[str, ...] | None = None  # None = use caller default
    fixed_features: tuple[str, ...] | None = None  # if set, return exactly these columns


FEATURE_PROFILE_CONFIG: dict[str, _ProfileConfig] = {
    DEFAULT_FEATURE_PROFILE: _ProfileConfig(),
    THESIS_26_FEATURE_PROFILE: _ProfileConfig(),
    "load_no_month_cyclic": _ProfileConfig(),
    "no_lag": _ProfileConfig(lag_steps=()),
    "limited_lag": _ProfileConfig(lag_steps=(1,)),
    "reduced": _ProfileConfig(
        fixed_features=(
            "temp_2m_c",
            "wind_speed_10m_m_s",
            "ghi_w_m2",
            "solar_altitude",
            "is_night",
            "cdd_18c",
            "hdd_18c",
        ),
    ),
    "solar_core": _ProfileConfig(
        fixed_features=(
            "ghi_w_m2",
            "solar_altitude",
            "is_night",
            "solar_lag_1",
        ),
    ),
    "trend_core": _ProfileConfig(
        fixed_features=(
            "temp_2m_c",
            "surface_pressure_hpa",
            "cdd_18c",
            "hdd_18c",
            "load_lag_12",
            "load_lag_24",
            "load_lag_48",
        ),
    ),
    "seasonal_core": _ProfileConfig(
        fixed_features=(
            "hour_sin",
            "hour_cos",
            "dow_sin",
            "dow_cos",
            "month_sin",
            "month_cos",
            "solar_altitude",
            "solar_azimuth",
            "is_night",
            "ghi_w_m2",
            "ghi_day_w_m2",
        ),
    ),
}


def normalize_feature_profile(feature_profile: str | None) -> str:
    name = str(feature_profile or DEFAULT_FEATURE_PROFILE).strip().lower()
    if name not in FEATURE_PROFILE_EXCLUDED_COLUMNS:
        raise ValueError(f"Unsupported feature_profile: {feature_profile!r}")
    return name


@dataclass(frozen=True)
class TargetScaler:
    mean: float
    std: float

    def transform(self, y: np.ndarray) -> np.ndarray:
        return (y - self.mean) / self.std

    def inverse_transform(self, y: np.ndarray) -> np.ndarray:
        return y * self.std + self.mean

    def as_dict(self) -> dict[str, float]:
        return {"mean": float(self.mean), "std": float(self.std)}


def fit_target_scaler(y: np.ndarray, eps: float = 1e-8) -> TargetScaler:
    mean = float(np.mean(y))
    std = float(np.std(y))
    if std < eps:
        std = eps
    return TargetScaler(mean=mean, std=std)


def _to_float32_tensor(x: np.ndarray) -> torch.Tensor:
    import torch

    return torch.tensor(x.astype(np.float32), dtype=torch.float32)


def build_kan_dataset(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    *,
    target_col: str,
    feature_cols: list[str],
    scale_features: bool = False,
    scale_target: bool = True,
) -> tuple[dict[str, torch.Tensor], dict[str, Any]]:
    """
    Build a dataset dict compatible with `kan.KAN.fit()`.

    KAN expects a dict containing:
        - train_input, train_label
        - test_input, test_label

    Here we map validation split to KAN's "test_*" fields for training-time monitoring.
    """
    if target_col not in train_df.columns:
        raise ValueError(f"target_col not in train_df: {target_col}")
    if target_col not in val_df.columns:
        raise ValueError(f"target_col not in val_df: {target_col}")
    if not feature_cols:
        raise ValueError("feature_cols must be non-empty")

    missing = [c for c in feature_cols if c not in train_df.columns or c not in val_df.columns]
    if missing:
        raise ValueError(f"feature columns missing from dataframes: {missing}")

    x_train = train_df[feature_cols].to_numpy()
    y_train = train_df[[target_col]].to_numpy()

    x_val = val_df[feature_cols].to_numpy()
    y_val = val_df[[target_col]].to_numpy()

    meta: dict[str, Any] = {
        "target_col": target_col,
        "feature_cols": list(feature_cols),
        "scale_features": bool(scale_features),
        "scale_target": bool(scale_target),
    }

    if scale_features:
        feature_scaler = fit_feature_scaler(x_train)
        x_train = transform_feature_matrix(x_train, feature_scaler)
        x_val = transform_feature_matrix(x_val, feature_scaler)
        meta["feature_scaler"] = feature_scaler

    if scale_target:
        scaler = fit_target_scaler(y_train)
        y_train = scaler.transform(y_train)
        y_val = scaler.transform(y_val)
        meta["target_scaler"] = scaler.as_dict()
        logger.info(f"Target scaled for training: mean={scaler.mean:.4f}, std={scaler.std:.4f}")

    dataset = {
        "train_input": _to_float32_tensor(x_train),
        "train_label": _to_float32_tensor(y_train),
        "test_input": _to_float32_tensor(x_val),
        "test_label": _to_float32_tensor(y_val),
    }

    return dataset, meta


def pick_feature_columns(
    df: pd.DataFrame,
    *,
    target_col: str,
    include_base: bool = True,
    include_groups: Iterable[str] = ("meteorology", "solar", "cyclic"),
    lag_steps: Iterable[int] = (1, 12, 48),
    lag_series: Iterable[str] = ("load", "wind", "solar"),
    feature_profile: str = DEFAULT_FEATURE_PROFILE,
) -> list[str]:
    """
    Select a compact, thesis-friendly feature set.

    Default behavior keeps interpretability manageable:
      - Base cols: wind/solar (and load if target != load)
      - Groups: meteorology, solar-position, cyclic encoding
      - Sparse lag subset: (1, 12, 48) for each series in lag_series
    """
    from src.data.features import get_feature_groups

    profile_name = normalize_feature_profile(feature_profile)
    cfg = FEATURE_PROFILE_CONFIG.get(profile_name, _ProfileConfig())

    # --- "reduced" (or any profile with fixed_features) returns exactly those columns ---
    if cfg.fixed_features is not None:
        out = [c for c in cfg.fixed_features if c in df.columns and c != target_col]
        if not out:
            raise ValueError(
                f"No feature columns selected for profile {profile_name!r} "
                "(fixed_features not found in dataframe)"
            )
        return out

    # --- Apply config overrides, falling back to caller-supplied defaults ---
    eff_include_base = cfg.include_base if cfg.include_base is not None else include_base
    eff_include_groups = cfg.include_groups if cfg.include_groups is not None else include_groups
    eff_lag_steps = cfg.lag_steps if cfg.lag_steps is not None else lag_steps

    groups = get_feature_groups()
    cols: list[str] = []

    if eff_include_base:
        for base_col in ("load", "wind", "solar"):
            if base_col == target_col:
                continue
            if base_col in df.columns:
                cols.append(base_col)

    for g in eff_include_groups:
        for c in groups.get(g, []):
            if c in df.columns and c != target_col:
                cols.append(c)

    lag_steps_list = sorted({int(s) for s in eff_lag_steps})
    for series in lag_series:
        for step in lag_steps_list:
            name = f"{series}_lag_{step}"
            if name in df.columns and name != target_col:
                cols.append(name)

    # De-duplicate preserving order
    seen: set[str] = set()
    out: list[str] = []
    for c in cols:
        if c not in seen:
            seen.add(c)
            out.append(c)

    excluded = set(FEATURE_PROFILE_EXCLUDED_COLUMNS[profile_name])
    if excluded:
        out = [c for c in out if c not in excluded]

    if not out:
        raise ValueError("No feature columns selected (check include_groups / lag_steps / schema)")

    return out
