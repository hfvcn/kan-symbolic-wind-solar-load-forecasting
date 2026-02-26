"""
Centralized configuration for the KAN-SR project.

Contains paths, ERCOT location parameters, data pipeline settings,
and helper functions for run directory management.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

# =============================================================================
# Modal Volume Configuration
# =============================================================================

VOLUME_MOUNT: str = "/vol"
"""Mount point for Modal Volume in cloud containers."""

DEFAULT_VOLUME_NAME: str = os.environ.get("KAN_SR_VOLUME", "kan-sr")
"""Volume name, overridable via environment."""


# =============================================================================
# ERCOT Location Parameters
# =============================================================================

ERCOT_LATITUDE: float = 31.0
"""ERCOT system centroid latitude (degrees) for solar calculations."""

ERCOT_LONGITUDE: float = -100.0
"""ERCOT system centroid longitude (degrees) for solar calculations."""

DEFAULT_ISO: str = "ERCOT"
"""Default ISO/market for PERFORM data loading."""

ISO_CENTROIDS: dict[str, tuple[float, float]] = {
    "ERCOT": (31.0, -100.0),
    "MISO": (43.0, -90.0),
    "NYISO": (43.0, -75.0),
    "SPP": (36.0, -97.0),
}
"""Approximate ISO centroid coordinates for solar position & meteorology proxies."""


def get_iso_centroid(iso: str) -> tuple[float, float]:
    iso_u = iso.upper()
    if iso_u in ISO_CENTROIDS:
        return ISO_CENTROIDS[iso_u]
    # Fallback to ERCOT centroid if unknown; keep pipeline runnable.
    return ISO_CENTROIDS[DEFAULT_ISO]


# =============================================================================
# S3 Data Source Configuration
# =============================================================================

S3_BUCKET: str = "arpa-e-perform"
"""ARPA-E PERFORM public S3 bucket (anonymous access)."""

S3_PATH_TEMPLATES: dict[str, str] = {
    "wind": "{iso}/{year}/Wind/Actuals/BA_level/BA_wind_actuals_{year}.h5",
    "solar": "{iso}/{year}/Solar/Actuals/BA_level/BA_solar_actuals_{year}.h5",
    "load": "{iso}/{year}/Load/Actuals/BA_level/BA_load_actuals_{year}.h5",
}
"""S3 path templates for wind, solar, and load actuals. Format with year."""


def get_s3_path(data_type: str, year: int, iso: str = DEFAULT_ISO) -> str:
    """
    Construct full S3 path for a data type and year.

    Args:
        data_type: One of 'wind', 'solar', 'load'.
        year: Data year (e.g., 2018).
        iso: ISO/market folder name (default: ERCOT).

    Returns:
        Full S3 URI (s3://arpa-e-perform/...).

    Raises:
        ValueError: If data_type is not recognized.
    """
    if data_type not in S3_PATH_TEMPLATES:
        raise ValueError(f"Unknown data_type: {data_type}. Must be one of {list(S3_PATH_TEMPLATES.keys())}")
    path = S3_PATH_TEMPLATES[data_type].format(iso=iso.upper(), year=year)
    return f"s3://{S3_BUCKET}/{path}"


# =============================================================================
# Data Pipeline Parameters
# =============================================================================

DEFAULT_YEAR: int = 2018
"""Primary data year for ERCOT analysis."""

RESOLUTION_MINUTES: int = 5
"""Native data resolution in minutes (5-minute intervals)."""

LAG_WINDOW: int = 48
"""Autoregressive lag window size. 48 steps = 4 hours at 5-min resolution."""

TRAIN_RATIO: float = 0.7
"""Training set fraction of total data."""

VAL_RATIO: float = 0.15
"""Validation set fraction of total data. Test = 1 - TRAIN - VAL = 0.15."""


# =============================================================================
# Run Directory Helpers
# =============================================================================

def generate_run_id() -> str:
    """
    Generate a unique run ID with timestamp and UUID.

    Format: YYYY-MM-DD_HHMMSS_<8hex>

    Returns:
        Unique run identifier string.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


def get_run_dir(run_id: str, volume_mount: str = VOLUME_MOUNT) -> Path:
    """
    Get the base directory for a run.

    Args:
        run_id: Unique run identifier.
        volume_mount: Modal Volume mount point.

    Returns:
        Path to the run's base directory.
    """
    return Path(volume_mount) / "runs" / run_id


def get_raw_dir(run_id: str, volume_mount: str = VOLUME_MOUNT) -> Path:
    """
    Get the raw data directory for a run.

    Args:
        run_id: Unique run identifier.
        volume_mount: Modal Volume mount point.

    Returns:
        Path to the run's raw data directory.
    """
    return get_run_dir(run_id, volume_mount) / "raw"


def get_processed_dir(run_id: str, volume_mount: str = VOLUME_MOUNT) -> Path:
    """
    Get the processed data directory for a run.

    Args:
        run_id: Unique run identifier.
        volume_mount: Modal Volume mount point.

    Returns:
        Path to the run's processed data directory.
    """
    return get_run_dir(run_id, volume_mount) / "processed"


def get_artifacts_dir(run_id: str, volume_mount: str = VOLUME_MOUNT) -> Path:
    """
    Get the artifacts directory for a run.

    Args:
        run_id: Unique run identifier.
        volume_mount: Modal Volume mount point.

    Returns:
        Path to the run's artifacts directory.
    """
    return get_run_dir(run_id, volume_mount) / "artifacts"


def init_run_dirs(run_id: str, volume_mount: str = VOLUME_MOUNT) -> dict[str, Path]:
    """
    Initialize all directories for a new run.

    Creates: raw/, processed/, artifacts/, checkpoint/ subdirectories.

    Args:
        run_id: Unique run identifier.
        volume_mount: Modal Volume mount point.

    Returns:
        Dict mapping directory names to their Paths.
    """
    dirs = {
        "base": get_run_dir(run_id, volume_mount),
        "raw": get_raw_dir(run_id, volume_mount),
        "processed": get_processed_dir(run_id, volume_mount),
        "artifacts": get_artifacts_dir(run_id, volume_mount),
        "checkpoint": get_run_dir(run_id, volume_mount) / "checkpoint",
    }

    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    return dirs
