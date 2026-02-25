"""
ARPA-E PERFORM data download and HDF5 loading utilities.

This module provides idempotent download from AWS S3 (anonymous access)
and DataFrame loading for ERCOT wind, solar, and load actuals.

HDF5 Structure (ARPA-E PERFORM):
    /meta         - Metadata dataset with column names (zone/BA identifiers)
    /time_index   - Timestamps stored as bytes (e.g., b'2018-01-01 00:00:00')
    /actuals      - Actual power values (may require scale_factor from attrs)

The actuals dataset may have a 'scale_factor' attribute. If present, raw
values should be multiplied by this factor to get MW values.

References:
    - https://github.com/PERFORM-Forecasts/documentation
    - https://registry.opendata.aws/arpa-e-perform/
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import h5py
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    import s3fs

from src.config import (
    DEFAULT_YEAR,
    get_raw_dir,
    get_s3_path,
)

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def _get_s3_filesystem() -> "s3fs.S3FileSystem":
    """
    Create an S3FileSystem with anonymous access.

    Returns:
        s3fs.S3FileSystem configured for credential-free access.
    """
    import s3fs

    return s3fs.S3FileSystem(anon=True)


def download_perform_file(s3_path: str, local_path: str, force: bool = False) -> str:
    """
    Download a file from ARPA-E PERFORM S3 bucket to local path.

    Implements idempotent caching: if local_path exists and force=False,
    skips download and returns the existing path.

    Args:
        s3_path: Full S3 URI (e.g., 's3://arpa-e-perform/ERCOT/2018/...').
        local_path: Destination path on local filesystem or Volume.
        force: If True, re-download even if file exists.

    Returns:
        The local_path where the file is stored.

    Raises:
        FileNotFoundError: If S3 file does not exist.
        IOError: If download fails.

    Example:
        >>> path = download_perform_file(
        ...     's3://arpa-e-perform/ERCOT/2018/Wind/Actuals/BA_level/BA_wind_actuals_2018.h5',
        ...     '/vol/runs/my-run/raw/wind_actuals_2018.h5'
        ... )
    """
    local_path_obj = Path(local_path)

    # Idempotent: skip if cached
    if local_path_obj.exists() and not force:
        logger.info(f"Skipping download (cached): {local_path}")
        return str(local_path_obj)

    # Ensure parent directory exists
    local_path_obj.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading: {s3_path}")
    logger.info(f"        to: {local_path}")

    fs = _get_s3_filesystem()

    try:
        # Check if S3 file exists
        if not fs.exists(s3_path):
            raise FileNotFoundError(f"S3 file not found: {s3_path}")

        # Get file size for progress reporting
        file_info = fs.info(s3_path)
        file_size_mb = file_info.get("size", 0) / (1024 * 1024)
        logger.info(f"File size: {file_size_mb:.1f} MB")

        # Download file
        # Use fs.get() for simple download (handles streaming internally)
        fs.get(s3_path, str(local_path_obj))

        logger.info(f"Download complete: {local_path}")

    except Exception as e:
        # Clean up partial download on failure
        if local_path_obj.exists():
            local_path_obj.unlink()
        raise IOError(f"Failed to download {s3_path}: {e}") from e

    return str(local_path_obj)


def download_ercot_actuals(
    run_dir: str | Path,
    year: int = DEFAULT_YEAR,
    data_types: list[str] | None = None,
) -> dict[str, str]:
    """
    Download ERCOT actuals data for specified types and year.

    Downloads wind, solar, and/or load HDF5 files from ARPA-E PERFORM S3.
    Files are cached in {run_dir}/raw/ with idempotent behavior.

    Args:
        run_dir: Base directory for the run (e.g., '/vol/runs/2025-02-25_120000_abc12345').
        year: Data year (default: 2018).
        data_types: List of types to download. Default: ['wind', 'solar', 'load'].

    Returns:
        Dict mapping data type to local file path.
        Example: {'wind': '/vol/runs/.../raw/wind_actuals_2018.h5', ...}

    Example:
        >>> paths = download_ercot_actuals('/vol/runs/my-run', year=2018)
        >>> paths['wind']
        '/vol/runs/my-run/raw/wind_actuals_2018.h5'
    """
    if data_types is None:
        data_types = ["wind", "solar", "load"]

    run_dir_path = Path(run_dir)
    raw_dir = run_dir_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, str] = {}

    for data_type in data_types:
        s3_path = get_s3_path(data_type, year)
        local_filename = f"{data_type}_actuals_{year}.h5"
        local_path = raw_dir / local_filename

        downloaded_path = download_perform_file(s3_path, str(local_path))
        result[data_type] = downloaded_path
        logger.info(f"Cached {data_type} actuals: {downloaded_path}")

    return result


def load_hdf5_to_dataframe(
    file_path: str | Path,
    dataset_key: str = "actuals",
) -> pd.DataFrame:
    """
    Load ARPA-E PERFORM HDF5 file into a pandas DataFrame.

    Reads the HDF5 structure expected from PERFORM:
    - /meta: contains column names (zone/BA identifiers)
    - /time_index: timestamps as bytes
    - /actuals (or specified dataset_key): power values

    If a 'scale_factor' attribute is present on the data dataset,
    values are multiplied by it to get MW.

    Args:
        file_path: Path to the HDF5 file.
        dataset_key: Name of the data dataset (default: 'actuals').

    Returns:
        DataFrame with UTC-localized DatetimeIndex and columns from meta.

    Raises:
        FileNotFoundError: If file does not exist.
        KeyError: If expected datasets are missing.

    Example:
        >>> df = load_hdf5_to_dataframe('/vol/runs/.../raw/wind_actuals_2018.h5')
        >>> df.index  # UTC DatetimeIndex
        >>> df.columns  # Zone/BA names from meta
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"HDF5 file not found: {file_path}")

    logger.info(f"Loading HDF5: {file_path}")

    with h5py.File(file_path, "r") as f:
        # Read time index (stored as bytes, need to decode)
        time_index_raw = f["time_index"][...]

        # Handle bytes -> string conversion
        if time_index_raw.dtype.kind == "S":  # Byte string
            time_index_str = time_index_raw.astype(str)
        elif time_index_raw.dtype.kind == "O":  # Object (Python bytes)
            time_index_str = np.array([t.decode("utf-8") if isinstance(t, bytes) else str(t) for t in time_index_raw])
        else:
            time_index_str = time_index_raw.astype(str)

        # Parse to datetime with UTC localization
        time_index = pd.to_datetime(time_index_str)
        time_index = time_index.tz_localize("UTC")

        # Read metadata for column names
        meta = f["meta"][...]

        # Extract column names - meta structure may vary
        # Common patterns: structured array with 'name' field or simple string array
        if meta.dtype.names is not None and "name" in meta.dtype.names:
            # Structured array with 'name' field
            column_names = meta["name"]
        else:
            # Simple array - use as-is
            column_names = meta

        # Decode if bytes
        if hasattr(column_names[0], "decode"):
            column_names = [c.decode("utf-8") for c in column_names]
        elif isinstance(column_names[0], bytes):
            column_names = [c.decode("utf-8") for c in column_names]
        else:
            column_names = [str(c) for c in column_names]

        # Read actual data
        if dataset_key not in f:
            raise KeyError(f"Dataset '{dataset_key}' not found in {file_path}. Available: {list(f.keys())}")

        data_dataset = f[dataset_key]
        data = data_dataset[...]

        # Check for scale_factor attribute
        scale_factor = data_dataset.attrs.get("scale_factor", None)
        if scale_factor is not None:
            logger.info(f"Applying scale_factor: {scale_factor}")
            data = data * scale_factor
        else:
            logger.debug("No scale_factor attribute found (using raw values)")

    # Build DataFrame
    df = pd.DataFrame(data, index=time_index, columns=column_names)
    df.index.name = "timestamp"

    logger.info(f"Loaded DataFrame: {len(df)} rows x {len(df.columns)} columns")
    logger.info(f"Time range: {df.index.min()} to {df.index.max()}")

    return df


def load_all_actuals(
    run_dir: str | Path,
    year: int = DEFAULT_YEAR,
    data_types: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Download (if needed) and load all ERCOT actuals into DataFrames.

    Convenience function that combines download_ercot_actuals() and
    load_hdf5_to_dataframe() for all specified data types.

    Args:
        run_dir: Base directory for the run.
        year: Data year (default: 2018).
        data_types: List of types to load. Default: ['wind', 'solar', 'load'].

    Returns:
        Dict mapping data type to DataFrame.
        Example: {'wind': DataFrame, 'solar': DataFrame, 'load': DataFrame}

    Example:
        >>> dfs = load_all_actuals('/vol/runs/my-run', year=2018)
        >>> dfs['wind'].head()
        >>> dfs['load']['ERCOT'].describe()
    """
    if data_types is None:
        data_types = ["wind", "solar", "load"]

    # First, ensure all files are downloaded
    file_paths = download_ercot_actuals(run_dir, year=year, data_types=data_types)

    # Then load each into a DataFrame
    result: dict[str, pd.DataFrame] = {}

    for data_type in data_types:
        file_path = file_paths[data_type]
        df = load_hdf5_to_dataframe(file_path)
        result[data_type] = df
        logger.info(f"Loaded {data_type}: {len(df)} rows, {list(df.columns)}")

    return result
