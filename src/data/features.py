"""
Feature engineering for ARPA-E PERFORM time series forecasting.

This module implements feature generation for energy forecasting models:
- Cyclic time encoding (hour, day of week, month) using sin/cos
- Solar position features (altitude, azimuth) using pvlib
- Autoregressive lag features (t-1 to t-48)

Feature Groups:
    - Cyclic: Captures periodic patterns without discontinuities
    - Solar: Physical astronomical features for solar generation
    - Meteorology: Temperature / irradiance / wind speed / pressure proxies (see meteorology.py)
    - Lag: Autoregressive features capturing recent temporal dynamics

References:
    - pvlib solar position: https://pvlib-python.readthedocs.io/
    - Cyclic encoding: sin/cos transformation preserves distance metric
    - ERCOT coordinates from src.config
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from pvlib.location import Location

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def encode_cyclic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode cyclic time features using sin/cos transformation.

    Transforms hour, day of week, and month into continuous cyclic features
    using sine/cosine encoding. This preserves the circular nature of time
    (e.g., hour 23 is close to hour 0) unlike linear encoding.

    Args:
        df: DataFrame with DatetimeIndex.

    Returns:
        DataFrame with added cyclic feature columns:
            - hour_sin, hour_cos (period=24)
            - dow_sin, dow_cos (period=7, day of week)
            - month_sin, month_cos (period=12)

    Formula:
        sin_feature = sin(2 * pi * value / period)
        cos_feature = cos(2 * pi * value / period)

    Example:
        >>> df_with_cyclic = encode_cyclic_features(df)
        >>> df_with_cyclic[['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos']].head()
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must have DatetimeIndex")

    df_out = df.copy()

    # Hour encoding (period=24)
    hour = df_out.index.hour + df_out.index.minute / 60  # Include fractional hour
    df_out["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    df_out["hour_cos"] = np.cos(2 * np.pi * hour / 24)

    # Day of week encoding (period=7)
    dow = df_out.index.dayofweek  # Monday=0, Sunday=6
    df_out["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    df_out["dow_cos"] = np.cos(2 * np.pi * dow / 7)

    # Month encoding (period=12)
    # Use day of year for smoother transition within months
    day_of_year = df_out.index.dayofyear
    df_out["month_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    df_out["month_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)

    logger.info("Added cyclic features: hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos")
    return df_out


def add_solar_features(
    df: pd.DataFrame,
    latitude: float | None = None,
    longitude: float | None = None,
) -> pd.DataFrame:
    """
    Add solar position features using pvlib.

    Calculates solar altitude (elevation) and azimuth for each timestamp
    based on geographic coordinates. Useful for solar generation forecasting.

    Args:
        df: DataFrame with DatetimeIndex (must be timezone-aware).
        latitude: Latitude in degrees. Defaults to ERCOT_LATITUDE from config.
        longitude: Longitude in degrees. Defaults to ERCOT_LONGITUDE from config.

    Returns:
        DataFrame with added columns:
            - solar_altitude: Sun elevation angle in degrees (0=horizon, 90=zenith)
            - solar_azimuth: Sun compass bearing in degrees (0=North, 90=East)
            - is_night: Boolean flag (True when solar_altitude < 0)

    Note:
        Index must be timezone-aware for accurate solar position calculation.
        PERFORM data uses UTC timestamps.

    Example:
        >>> df_with_solar = add_solar_features(df, latitude=31.0, longitude=-100.0)
        >>> df_with_solar[df_with_solar['is_night']].count()  # Night hours
    """
    import pvlib

    # Load defaults from config if not provided
    if latitude is None or longitude is None:
        from src.config import ERCOT_LATITUDE, ERCOT_LONGITUDE
        latitude = latitude or ERCOT_LATITUDE
        longitude = longitude or ERCOT_LONGITUDE

    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must have DatetimeIndex")

    df_out = df.copy()

    # Ensure timezone-aware
    if df_out.index.tz is None:
        logger.warning("Index has no timezone, assuming UTC")
        df_out.index = df_out.index.tz_localize("UTC")

    # Create pvlib Location
    location = pvlib.location.Location(latitude, longitude)

    # Calculate solar position
    logger.info(f"Calculating solar position for lat={latitude}, lon={longitude}")
    solar_position = location.get_solarposition(df_out.index)

    # Add features
    df_out["solar_altitude"] = solar_position["elevation"].values
    df_out["solar_azimuth"] = solar_position["azimuth"].values
    df_out["is_night"] = df_out["solar_altitude"] < 0

    # Log statistics
    night_count = df_out["is_night"].sum()
    day_count = len(df_out) - night_count
    logger.info(f"Added solar features: {day_count} day timestamps, {night_count} night timestamps")

    return df_out


def add_lag_features(
    df: pd.DataFrame,
    target_cols: list[str],
    lags: list[int] | None = None,
) -> pd.DataFrame:
    """
    Add autoregressive lag features for specified columns.

    Creates lagged versions of target columns for capturing temporal dynamics.
    Default lags span t-1 to t-48 (4 hours at 5-minute resolution).

    Args:
        df: DataFrame with time series data.
        target_cols: List of column names to create lag features for.
        lags: List of lag values (positive integers). Default: [1, 2, ..., 48].

    Returns:
        DataFrame with added lag columns named: {col}_lag_{n}

    Note:
        Lag features create NaN in the first `max(lags)` rows. These should
        be dropped AFTER train/val/test splitting to prevent data leakage.

    Example:
        >>> df_with_lags = add_lag_features(df, target_cols=['load'], lags=[1, 12, 48])
        >>> df_with_lags[['load', 'load_lag_1', 'load_lag_12', 'load_lag_48']].head(50)
    """
    if lags is None:
        # Default: t-1 to t-48 (4 hours at 5-minute resolution)
        lags = list(range(1, 49))

    df_out = df.copy()

    # Validate target columns exist
    missing_cols = [col for col in target_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Target columns not found: {missing_cols}")

    # Create lag features
    total_lags = 0
    for col in target_cols:
        for lag in lags:
            lag_col_name = f"{col}_lag_{lag}"
            df_out[lag_col_name] = df_out[col].shift(lag)
            total_lags += 1

    logger.info(f"Added {total_lags} lag features for {len(target_cols)} columns (lags: {min(lags)}-{max(lags)})")

    return df_out


def add_all_features(
    df: pd.DataFrame,
    target_cols: list[str],
    latitude: float | None = None,
    longitude: float | None = None,
    lags: list[int] | None = None,
) -> pd.DataFrame:
    """
    Convenience function to add all feature types in sequence.

    Combines cyclic, solar, and lag features into a single call.

    Args:
        df: DataFrame with DatetimeIndex and time series data.
        target_cols: Columns for lag feature creation.
        latitude: Latitude for solar calculations (default: ERCOT_LATITUDE).
        longitude: Longitude for solar calculations (default: ERCOT_LONGITUDE).
        lags: Lag values (default: 1-48).

    Returns:
        DataFrame with all feature groups added.

    Example:
        >>> df_full = add_all_features(df, target_cols=['load', 'wind', 'solar'])
    """
    logger.info("Adding all feature groups...")

    # Apply feature transformations in sequence
    df_out = encode_cyclic_features(df)
    df_out = add_solar_features(df_out, latitude=latitude, longitude=longitude)
    df_out = add_lag_features(df_out, target_cols=target_cols, lags=lags)

    original_cols = len(df.columns)
    final_cols = len(df_out.columns)
    logger.info(f"Feature engineering complete: {original_cols} -> {final_cols} columns (+{final_cols - original_cols})")

    return df_out


def get_feature_groups() -> dict[str, list[str]]:
    """
    Return dictionary mapping feature group names to column patterns.

    Useful for feature selection, documentation, and model interpretability.

    Returns:
        Dict with keys:
            - "cyclic": Cyclic time encoding columns
            - "solar": Solar position columns (union)
            - "solar_geom": Solar geometry columns (alt/azimuth)
            - "solar_flag": Solar flags (e.g., is_night)
            - "meteorology": Meteorological proxy columns (union)
            - "meteo_temp": Temperature columns
            - "meteo_wind": Wind proxy columns
            - "meteo_pressure": Pressure proxy columns
            - "meteo_irradiance": Irradiance proxy columns
            - "meteo_degree": Degree (CDD/HDD) proxy columns
            - "lag_pattern": Regex pattern for lag columns

    Example:
        >>> groups = get_feature_groups()
        >>> cyclic_cols = [c for c in df.columns if c in groups['cyclic']]
        >>> lag_cols = [c for c in df.columns if 'lag_' in c]
    """
    solar_geom = ["solar_altitude", "solar_azimuth"]
    solar_flag = ["is_night"]
    meteo_temp = ["temp_2m_c"]
    meteo_wind = ["wind_speed_10m_m_s", "wind_speed_10m_m_s_cubed", "wind_speed_hub_est"]
    meteo_pressure = ["surface_pressure_hpa"]
    meteo_irradiance = ["ghi_w_m2", "ghi_day_w_m2", "ghi_temp_corr_w_m2"]
    meteo_degree = ["cdd_18c", "hdd_18c"]

    return {
        "cyclic": [
            "hour_sin",
            "hour_cos",
            "dow_sin",
            "dow_cos",
            "month_sin",
            "month_cos",
        ],
        # Fine-grained groups for ablation studies (GHI vs solar geometry, etc.)
        "solar_geom": solar_geom,
        "solar_flag": solar_flag,
        "solar": [*solar_geom, *solar_flag],
        "meteo_temp": meteo_temp,
        "meteo_wind": meteo_wind,
        "meteo_pressure": meteo_pressure,
        "meteo_irradiance": meteo_irradiance,
        "meteo_degree": meteo_degree,
        "meteorology": [
            *meteo_temp,
            *meteo_wind,
            *meteo_pressure,
            *meteo_irradiance,
            *meteo_degree,
        ],
        "lag_pattern": r".*_lag_\d+$",  # Regex pattern for matching lag columns
    }


def filter_feature_columns(
    df: pd.DataFrame,
    include_groups: list[str] | None = None,
    exclude_groups: list[str] | None = None,
) -> list[str]:
    """
    Filter DataFrame columns by feature group.

    Helper function for selecting subsets of features for model training
    or analysis.

    Args:
        df: DataFrame with feature columns.
        include_groups: Groups to include. If None, include all.
        exclude_groups: Groups to exclude. Applied after include.

    Returns:
        List of column names matching the filter criteria.

    Example:
        >>> # Get only cyclic and solar features
        >>> cols = filter_feature_columns(df, include_groups=['cyclic', 'solar'])
        >>> X = df[cols]
    """
    import re

    groups = get_feature_groups()
    all_columns = list(df.columns)

    if include_groups is None:
        include_groups = list(groups.keys())

    included_cols: set[str] = set()

    for group in include_groups:
        if group not in groups:
            logger.warning(f"Unknown feature group: {group}")
            continue

        group_def = groups[group]

        if isinstance(group_def, list):
            # Direct column names
            for col in group_def:
                if col in all_columns:
                    included_cols.add(col)
        elif isinstance(group_def, str):
            # Regex pattern
            pattern = re.compile(group_def)
            for col in all_columns:
                if pattern.match(col):
                    included_cols.add(col)

    # Apply exclusions
    if exclude_groups:
        for group in exclude_groups:
            if group not in groups:
                continue

            group_def = groups[group]

            if isinstance(group_def, list):
                for col in group_def:
                    included_cols.discard(col)
            elif isinstance(group_def, str):
                pattern = re.compile(group_def)
                included_cols = {col for col in included_cols if not pattern.match(col)}

    # Preserve original column order
    return [col for col in all_columns if col in included_cols]
