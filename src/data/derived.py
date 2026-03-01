from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


def compute_net_load(load: pd.Series, wind: pd.Series, solar: pd.Series) -> pd.Series:
    """
    Compute net load as a *definition* (not a discovered relationship):

        net_load = load - wind - solar
    """
    return load.astype(np.float64) - wind.astype(np.float64) - solar.astype(np.float64)


def compute_delta(current: pd.Series, previous: pd.Series) -> pd.Series:
    """Compute a difference series: current - previous."""
    return current.astype(np.float64) - previous.astype(np.float64)


def normalize_horizon_steps(
    steps: list[int] | None,
    *,
    max_steps: int = 48,
    include_1: bool = True,
) -> list[int]:
    """
    Normalize a list of horizon steps:
      - de-duplicate and sort
      - validate 1 <= step <= max_steps
      - optionally ensure step=1 is included (backward-compatible defaults)
    """
    if max_steps <= 0:
        raise ValueError("max_steps must be positive")

    raw = [] if steps is None else list(steps)
    out = sorted({int(s) for s in raw})
    if include_1 and 1 not in out:
        out = [1, *out]

    bad = [s for s in out if s < 1 or s > int(max_steps)]
    if bad:
        raise ValueError(f"horizon_steps out of range (1..{max_steps}): {bad}")
    return out


@dataclass(frozen=True)
class ZScoreStats:
    mean: float
    std: float

    def as_tuple(self) -> tuple[float, float]:
        return (float(self.mean), float(self.std))


def fit_zscore(x: pd.Series, *, eps: float = 1e-8) -> ZScoreStats:
    x = pd.to_numeric(x, errors="coerce").astype(np.float64)
    mean = float(np.nanmean(x.to_numpy(dtype=np.float64)))
    std = float(np.nanstd(x.to_numpy(dtype=np.float64)))
    if not np.isfinite(std) or std < eps:
        std = eps
    if not np.isfinite(mean):
        mean = 0.0
    return ZScoreStats(mean=mean, std=std)


def apply_zscore(x: pd.Series, stats: ZScoreStats) -> pd.Series:
    x = pd.to_numeric(x, errors="coerce").astype(np.float64)
    return (x - float(stats.mean)) / float(stats.std)


def add_degree_features(
    df: pd.DataFrame,
    *,
    temp_col: str = "temp_2m_c",
    base_c: float = 18.0,
    cooling_col: str = "cdd_18c",
    heating_col: str = "hdd_18c",
) -> pd.DataFrame:
    """
    Add "degree" proxies frequently used in load studies:

      - cdd_18c = max(0, temp - 18°C)
      - hdd_18c = max(0, 18°C - temp)

    Note: Although often aggregated as degree-days/hours, at 5-min resolution
    these are instantaneous proxies for heating/cooling demand pressure.
    """
    if temp_col not in df.columns:
        raise ValueError(f"temp_col not found: {temp_col}")
    t = pd.to_numeric(df[temp_col], errors="coerce").astype(np.float64)
    out = df.copy()
    out[cooling_col] = np.maximum(0.0, t - float(base_c))
    out[heating_col] = np.maximum(0.0, float(base_c) - t)
    return out


def add_wind_cubic_feature(
    df: pd.DataFrame,
    *,
    wind_col: str = "wind_speed_10m_m_s",
    out_col: str = "wind_speed_10m_m_s_cubed",
) -> pd.DataFrame:
    """
    Add a simple wind-power proxy feature v^3 (Betz-law-inspired).
    """
    if wind_col not in df.columns:
        raise ValueError(f"wind_col not found: {wind_col}")
    v = pd.to_numeric(df[wind_col], errors="coerce").astype(np.float64)
    out = df.copy()
    out[out_col] = v**3
    return out


def add_daylight_ghi_feature(
    df: pd.DataFrame,
    *,
    ghi_col: str = "ghi_w_m2",
    is_night_col: str = "is_night",
    out_col: str = "ghi_day_w_m2",
) -> pd.DataFrame:
    """
    Add a daylight-gated irradiance feature:

        ghi_day = ghi * (1 - is_night)
    """
    if ghi_col not in df.columns:
        raise ValueError(f"ghi_col not found: {ghi_col}")
    if is_night_col not in df.columns:
        raise ValueError(f"is_night_col not found: {is_night_col}")
    ghi = pd.to_numeric(df[ghi_col], errors="coerce").astype(np.float64)
    night = df[is_night_col].astype(bool)
    out = df.copy()
    out[out_col] = ghi * (~night).astype(np.float64)
    return out


def extend_scaler_params(
    scaler_params: dict[str, Any],
    new_stats: dict[str, ZScoreStats],
) -> dict[str, Any]:
    """
    Extend a `scaler_params.json` dict (as produced by src.data.split.save_scaler_params)
    with additional normalized feature columns.
    """
    feature_names = list(scaler_params.get("feature_names", []))
    mean = list(scaler_params.get("mean", []))
    scale = list(scaler_params.get("scale", []))

    out = dict(scaler_params)
    out["feature_names"] = feature_names
    out["mean"] = mean
    out["scale"] = scale

    existing = set(feature_names)
    for name, stats in new_stats.items():
        if name in existing:
            continue
        feature_names.append(str(name))
        mean.append(float(stats.mean))
        scale.append(float(stats.std))

    return out
