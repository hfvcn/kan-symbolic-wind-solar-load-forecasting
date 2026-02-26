"""
Meteorological feature generation for ARPA-E PERFORM forecasting.

PERFORM BA-level actuals (wind/solar/load) do not include raw meteorological
sensor inputs (e.g., temperature, irradiance, wind speed, pressure). To support
thesis requirements and physics-informed constraints, this module fetches
meteorological proxy features from Open-Meteo's historical archive API and
aligns them to the PERFORM 5-minute time index.

Design goals:
    - Deterministic columns with explicit units in names
    - Optional, cache-first behavior (Parquet) for reproducibility
    - Safe alignment to 5-minute index with no NaN/Inf in outputs

Columns added (default):
    - temp_2m_c: air temperature at 2m (°C)
    - wind_speed_10m_m_s: wind speed at 10m (m/s)
    - surface_pressure_hpa: surface pressure (hPa)
    - ghi_w_m2: shortwave radiation / GHI proxy (W/m^2)
"""

from __future__ import annotations

import json
import logging
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from src.config import ERCOT_LATITUDE, ERCOT_LONGITUDE, RESOLUTION_MINUTES

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Open-Meteo hourly variables we request by default.
# Units in API responses (as of 2026-02): °C, km/h, hPa, W/m²
DEFAULT_OPEN_METEO_HOURLY_VARS: tuple[str, ...] = (
    "temperature_2m",
    "wind_speed_10m",
    "surface_pressure",
    "shortwave_radiation",
)


@dataclass(frozen=True)
class OpenMeteoRequest:
    latitude: float
    longitude: float
    start_date: date
    end_date: date
    hourly_vars: tuple[str, ...] = DEFAULT_OPEN_METEO_HOURLY_VARS
    timezone: str = "UTC"


def _build_open_meteo_archive_url(req: OpenMeteoRequest) -> str:
    hourly = ",".join(req.hourly_vars)
    params = {
        "latitude": req.latitude,
        "longitude": req.longitude,
        "start_date": req.start_date.isoformat(),
        "end_date": req.end_date.isoformat(),
        "hourly": hourly,
        "timezone": req.timezone,
    }
    return f"{OPEN_METEO_ARCHIVE_URL}?{urllib.parse.urlencode(params)}"


def _fetch_json(url: str, timeout_s: int = 60) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_open_meteo_with_retry(
    req: OpenMeteoRequest,
    retries: int = 3,
    backoff_s: float = 1.0,
) -> dict[str, Any]:
    url = _build_open_meteo_archive_url(req)
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            logger.info(
                "Fetching Open-Meteo hourly: "
                f"{req.start_date.isoformat()}..{req.end_date.isoformat()} "
                f"vars={','.join(req.hourly_vars)}"
            )
            return _fetch_json(url)
        except Exception as e:  # noqa: BLE001 - boundary to external network
            last_err = e
            if attempt >= retries:
                break
            sleep_s = backoff_s * (2**attempt)
            logger.warning(f"Open-Meteo request failed (attempt {attempt + 1}/{retries + 1}): {e}. Retrying in {sleep_s:.1f}s")
            time.sleep(sleep_s)
    assert last_err is not None
    raise RuntimeError(f"Open-Meteo request failed after {retries + 1} attempts: {last_err}") from last_err


def _open_meteo_hourly_json_to_df(payload: dict[str, Any]) -> pd.DataFrame:
    if "hourly" not in payload or "time" not in payload["hourly"]:
        raise ValueError("Invalid Open-Meteo payload: missing hourly.time")

    hourly = payload["hourly"]
    times = pd.to_datetime(hourly["time"])
    if isinstance(times, pd.DatetimeIndex) and times.tz is None:
        # Payload timezone is requested as UTC; localize for downstream joins.
        times = times.tz_localize("UTC")

    data: dict[str, Iterable[float]] = {}
    for var in DEFAULT_OPEN_METEO_HOURLY_VARS:
        if var not in hourly:
            raise ValueError(f"Open-Meteo payload missing hourly variable: {var}")
        data[var] = hourly[var]

    df = pd.DataFrame(data, index=times).sort_index()

    # Convert to stable, unit-explicit feature names.
    out = pd.DataFrame(index=df.index)
    out["temp_2m_c"] = pd.to_numeric(df["temperature_2m"], errors="coerce")
    out["surface_pressure_hpa"] = pd.to_numeric(df["surface_pressure"], errors="coerce")
    out["ghi_w_m2"] = pd.to_numeric(df["shortwave_radiation"], errors="coerce")

    # wind_speed_10m is km/h -> m/s
    wind_km_h = pd.to_numeric(df["wind_speed_10m"], errors="coerce")
    out["wind_speed_10m_m_s"] = wind_km_h / 3.6

    return out


def fetch_open_meteo_hourly(
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
    *,
    hourly_vars: tuple[str, ...] = DEFAULT_OPEN_METEO_HOURLY_VARS,
    timezone: str = "UTC",
    chunk_days: int = 31,
) -> pd.DataFrame:
    """
    Fetch Open-Meteo hourly meteorology as a DataFrame (UTC index).

    To reduce the risk of API limits, requests are chunked by `chunk_days`
    and concatenated.
    """
    if chunk_days <= 0:
        raise ValueError("chunk_days must be positive")

    req_start = start_date
    parts: list[pd.DataFrame] = []

    while req_start <= end_date:
        req_end = min(end_date, req_start + timedelta(days=chunk_days - 1))
        req = OpenMeteoRequest(
            latitude=latitude,
            longitude=longitude,
            start_date=req_start,
            end_date=req_end,
            hourly_vars=hourly_vars,
            timezone=timezone,
        )
        payload = _fetch_open_meteo_with_retry(req)
        parts.append(_open_meteo_hourly_json_to_df(payload))
        req_start = req_end + timedelta(days=1)

    df = pd.concat(parts).sort_index()
    df = df[~df.index.duplicated(keep="first")]
    return df


def align_hourly_to_index(
    met_hourly: pd.DataFrame,
    target_index: pd.DatetimeIndex,
    *,
    resolution_minutes: int = RESOLUTION_MINUTES,
) -> pd.DataFrame:
    """
    Align hourly meteorology to a target 5-minute DatetimeIndex (UTC).

    Returns a DataFrame indexed exactly by `target_index`, with NaN/Inf
    removed via interpolation + ffill/bfill.
    """
    if not isinstance(target_index, pd.DatetimeIndex):
        raise TypeError("target_index must be a pandas DatetimeIndex")
    if target_index.tz is None:
        raise ValueError("target_index must be timezone-aware (UTC recommended)")
    if met_hourly.index.tz is None:
        met_hourly = met_hourly.copy()
        met_hourly.index = met_hourly.index.tz_localize("UTC")

    met_hourly = met_hourly.sort_index()
    met_hourly = met_hourly.tz_convert(target_index.tz)

    freq = f"{resolution_minutes}min"
    met_5m = met_hourly.resample(freq).interpolate(method="time")
    met_5m = met_5m.reindex(target_index)

    # Fill any remaining NaN around edges or gaps.
    met_5m = met_5m.interpolate(method="time").ffill().bfill()

    # Guard against inf from bad conversions.
    met_5m = met_5m.replace([np.inf, -np.inf], np.nan).ffill().bfill()

    return met_5m


def add_open_meteo_meteorology_features(
    df: pd.DataFrame,
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    cache_path: str | Path | None = None,
    force_refresh: bool = False,
    allow_network: bool = True,
    allow_missing: bool = True,
) -> pd.DataFrame:
    """
    Add Open-Meteo meteorology features to a PERFORM time series DataFrame.

    Behavior:
        - If cache_path exists and force_refresh=False: load cached hourly data
        - Else if allow_network=True: fetch from Open-Meteo and optionally cache
        - Else: skip or raise depending on allow_missing
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must have DatetimeIndex")
    if df.index.tz is None:
        raise ValueError("DataFrame index must be timezone-aware (UTC recommended)")

    latitude = ERCOT_LATITUDE if latitude is None else latitude
    longitude = ERCOT_LONGITUDE if longitude is None else longitude

    start_date = df.index.min().date()
    end_date = df.index.max().date()

    cache_path_obj = Path(cache_path) if cache_path is not None else None

    met_hourly: pd.DataFrame | None = None
    if cache_path_obj is not None and cache_path_obj.exists() and not force_refresh:
        logger.info(f"Loading cached meteorology: {cache_path_obj}")
        met_hourly = pd.read_parquet(cache_path_obj)
        if not isinstance(met_hourly.index, pd.DatetimeIndex):
            raise ValueError("Cached meteorology parquet must have DatetimeIndex")
        if met_hourly.index.tz is None:
            met_hourly.index = met_hourly.index.tz_localize("UTC")

    if met_hourly is None:
        if not allow_network:
            msg = "Meteorology fetch disabled (allow_network=False) and no cache available"
            if allow_missing:
                logger.warning(msg + "; skipping meteorology features")
                return df
            raise RuntimeError(msg)

        try:
            met_hourly = fetch_open_meteo_hourly(
                latitude=latitude,
                longitude=longitude,
                start_date=start_date,
                end_date=end_date,
            )
            if cache_path_obj is not None:
                cache_path_obj.parent.mkdir(parents=True, exist_ok=True)
                met_hourly.to_parquet(cache_path_obj, compression="snappy")
                logger.info(f"Cached meteorology to: {cache_path_obj}")
        except Exception as e:  # noqa: BLE001 - boundary to external network
            msg = f"Failed to fetch Open-Meteo meteorology: {e}"
            if allow_missing:
                logger.warning(msg + "; skipping meteorology features")
                return df
            raise RuntimeError(msg) from e

    met_aligned = align_hourly_to_index(met_hourly, df.index)
    df_out = df.join(met_aligned, how="left")

    # Final safety: ensure no NaN/Inf introduced
    met_cols = met_aligned.columns.tolist()
    bad = df_out[met_cols].isna().any().any() or np.isinf(df_out[met_cols].to_numpy()).any()
    if bad:
        # Shouldn't happen due to align_hourly_to_index fill logic, but keep it safe.
        df_out[met_cols] = df_out[met_cols].replace([np.inf, -np.inf], np.nan).interpolate("time").ffill().bfill()

    logger.info(f"Added meteorology features: {', '.join(met_cols)}")
    return df_out

