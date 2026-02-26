"""
Chronological data splitting and normalization for time series forecasting.

This module provides strict temporal splitting (no shuffle) with gap between splits
to prevent lag feature leakage, Z-score normalization fitted on training data only,
and Parquet I/O with timestamp versioning for reproducibility.

Methodology:
    - Chronological split ensures no future data leakage
    - Gap of 48 steps (4 hours at 5-min resolution) between splits prevents lag feature contamination
    - StandardScaler fit on train only prevents data leakage via normalization
    - Scaler parameters saved to JSON for inverse transform during evaluation

References:
    - Split ratios from src.config (TRAIN_RATIO, VAL_RATIO)
    - LAG_WINDOW from src.config for gap sizing
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.config import LAG_WINDOW, TRAIN_RATIO, VAL_RATIO

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def chronological_split(
    df: pd.DataFrame,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    gap_steps: int = LAG_WINDOW,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split DataFrame chronologically with gaps between splits.

    Performs strict temporal splitting without shuffling. A gap is inserted
    between train/val and val/test to prevent lag feature leakage.

    Args:
        df: DataFrame with DatetimeIndex, must be sorted chronologically.
        train_ratio: Fraction of data for training (default: from config).
        val_ratio: Fraction of data for validation (default: from config).
        gap_steps: Number of timesteps to skip between splits (default: LAG_WINDOW).

    Returns:
        Tuple of (train, val, test) DataFrames.

    Raises:
        ValueError: If DataFrame is not sorted by DatetimeIndex.

    Example:
        >>> train, val, test = chronological_split(df, train_ratio=0.7, val_ratio=0.15)
        >>> print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame must have DatetimeIndex")

    # Verify chronological ordering
    if not df.index.is_monotonic_increasing:
        raise ValueError("DataFrame index must be sorted in ascending order (chronological)")

    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    # Split with gaps to prevent lag feature leakage
    train = df.iloc[:train_end]
    val = df.iloc[train_end + gap_steps : val_end]
    test = df.iloc[val_end + gap_steps :]

    # Log split information
    logger.info(f"Chronological split: {n} total rows")
    logger.info(f"  Train: {len(train)} rows ({len(train)/n*100:.1f}%) - {train.index.min()} to {train.index.max()}")
    logger.info(f"  Val:   {len(val)} rows ({len(val)/n*100:.1f}%) - {val.index.min()} to {val.index.max()}")
    logger.info(f"  Test:  {len(test)} rows ({len(test)/n*100:.1f}%) - {test.index.min()} to {test.index.max()}")
    logger.info(f"  Gap:   {gap_steps} steps between each split")

    return train, val, test


def drop_initial_lag_rows(df: pd.DataFrame, n_lags: int = LAG_WINDOW) -> pd.DataFrame:
    """
    Drop first n_lags rows that have NaN from lag feature creation.

    Lag features create NaN values in the first n_lags rows of the DataFrame.
    This function removes those rows after splitting to prevent data leakage.

    Args:
        df: DataFrame with potential NaN from lag features.
        n_lags: Number of initial rows to drop (default: LAG_WINDOW from config).

    Returns:
        DataFrame with first n_lags rows removed.

    Example:
        >>> train_clean = drop_initial_lag_rows(train, n_lags=48)
    """
    rows_before = len(df)
    df_clean = df.iloc[n_lags:]

    logger.info(f"Dropped first {n_lags} lag rows: {rows_before} -> {len(df_clean)} rows")
    return df_clean


def normalize_features(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    exclude_cols: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """
    Normalize features using Z-score (StandardScaler) fit on train only.

    Fits StandardScaler on training data only to prevent data leakage,
    then transforms all splits (train, val, test) using the fitted scaler.

    Args:
        train: Training DataFrame.
        val: Validation DataFrame.
        test: Test DataFrame.
        exclude_cols: Columns to exclude from normalization (e.g., target columns).
            Defaults to None (normalize all numeric columns).

    Returns:
        Tuple of (train_scaled, val_scaled, test_scaled, scaler_params):
            - train_scaled: Normalized training data
            - val_scaled: Normalized validation data
            - test_scaled: Normalized test data
            - scaler_params: Dict with mean, scale, feature_names for inverse transform

    Example:
        >>> train_s, val_s, test_s, params = normalize_features(train, val, test, exclude_cols=['load'])
        >>> save_scaler_params(params, 'scaler.json')
    """
    exclude_cols = exclude_cols or []

    # Identify columns to normalize (numeric, not excluded)
    numeric_cols = train.select_dtypes(include=[np.number]).columns.tolist()
    normalize_cols = [col for col in numeric_cols if col not in exclude_cols]

    logger.info(f"Normalizing {len(normalize_cols)} columns (excluding {len(exclude_cols)} target columns)")

    # Create copies to avoid modifying originals
    train_scaled = train.copy()
    val_scaled = val.copy()
    test_scaled = test.copy()

    if not normalize_cols:
        logger.warning("No columns to normalize after exclusions")
        scaler_params: dict[str, Any] = {
            "mean": [],
            "scale": [],
            "feature_names": [],
            "excluded_cols": exclude_cols,
        }
        return train_scaled, val_scaled, test_scaled, scaler_params

    # Fit scaler on train only
    scaler = StandardScaler()
    scaler.fit(train[normalize_cols])

    # Transform all splits
    train_scaled[normalize_cols] = scaler.transform(train[normalize_cols])
    val_scaled[normalize_cols] = scaler.transform(val[normalize_cols])
    test_scaled[normalize_cols] = scaler.transform(test[normalize_cols])

    # Build scaler params dict for reproducibility
    scaler_params = {
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "feature_names": normalize_cols,
        "excluded_cols": exclude_cols,
    }

    logger.info("Z-score normalization complete (fit on train only)")
    logger.info(f"  Features normalized: {len(normalize_cols)}")
    logger.info(f"  Mean range: [{min(scaler.mean_):.4f}, {max(scaler.mean_):.4f}]")
    logger.info(f"  Scale range: [{min(scaler.scale_):.4f}, {max(scaler.scale_):.4f}]")

    return train_scaled, val_scaled, test_scaled, scaler_params


def save_scaler_params(scaler_params: dict[str, Any], output_path: str | Path) -> str:
    """
    Save scaler parameters to JSON for reproducibility and inverse transform.

    Writes scaler parameters with metadata including creation timestamp
    and sklearn version for complete reproducibility.

    Args:
        scaler_params: Dict containing mean, scale, feature_names from normalize_features().
        output_path: Path to write JSON file.

    Returns:
        Path to the created file (as string).

    Example:
        >>> path = save_scaler_params(params, '/vol/runs/run123/artifacts/scaler.json')
    """
    import sklearn

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add metadata
    full_params = {
        **scaler_params,
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "sklearn_version": sklearn.__version__,
        },
    }

    with open(output_path, "w") as f:
        json.dump(full_params, f, indent=2)

    logger.info(f"Scaler parameters saved to: {output_path}")
    return str(output_path)


def load_scaler_params(params_path: str | Path) -> dict[str, Any]:
    """
    Load scaler parameters from JSON file.

    Args:
        params_path: Path to scaler parameters JSON file.

    Returns:
        Dict with mean, scale, feature_names for inverse transform.

    Example:
        >>> params = load_scaler_params('/vol/runs/run123/artifacts/scaler.json')
        >>> scaler = StandardScaler()
        >>> scaler.mean_ = np.array(params['mean'])
        >>> scaler.scale_ = np.array(params['scale'])
    """
    params_path = Path(params_path)

    with open(params_path) as f:
        params = json.load(f)

    logger.info(f"Loaded scaler parameters from: {params_path}")
    return params


def save_splits_to_parquet(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
    output_dir: str | Path,
    timestamp: str | None = None,
) -> dict[str, str]:
    """
    Save train/val/test splits to Parquet with timestamp versioning.

    Saves each split as {split}_{timestamp}.parquet with snappy compression,
    and creates corresponding metadata JSON files.

    Args:
        train: Training DataFrame.
        val: Validation DataFrame.
        test: Test DataFrame.
        output_dir: Directory to save Parquet files.
        timestamp: Version timestamp. If None, generates from current UTC time.

    Returns:
        Dict mapping split name -> parquet path.

    Example:
        >>> paths = save_splits_to_parquet(train, val, test, '/vol/runs/run123/processed/')
        >>> print(paths['train'])  # '/vol/runs/run123/processed/train_2026-02-25_123456.parquet'
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")

    splits = {"train": train, "val": val, "test": test}
    paths: dict[str, str] = {}

    for split_name, df in splits.items():
        # Save Parquet with snappy compression
        parquet_path = output_dir / f"{split_name}_{timestamp}.parquet"
        df.to_parquet(parquet_path, compression="snappy")

        # Save metadata JSON
        meta_path = output_dir / f"{split_name}_{timestamp}_meta.json"
        meta = {
            "split": split_name,
            "timestamp": timestamp,
            "rows": len(df),
            "columns": list(df.columns),
            "date_range": {
                "start": str(df.index.min()) if len(df) > 0 else None,
                "end": str(df.index.max()) if len(df) > 0 else None,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        paths[split_name] = str(parquet_path)
        logger.info(f"Saved {split_name}: {parquet_path} ({len(df)} rows)")

    return paths


def load_splits_from_parquet(
    output_dir: str | Path,
    timestamp: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load train/val/test splits from Parquet files.

    If timestamp is not provided, finds the latest version by filename sort.

    Args:
        output_dir: Directory containing Parquet files.
        timestamp: Version timestamp to load. If None, loads latest.

    Returns:
        Tuple of (train, val, test) DataFrames.

    Raises:
        FileNotFoundError: If no matching Parquet files found.

    Example:
        >>> train, val, test = load_splits_from_parquet('/vol/runs/run123/processed/')
    """
    output_dir = Path(output_dir)

    if timestamp is None:
        # Find latest timestamp by sorting train files
        train_files = sorted(output_dir.glob("train_*.parquet"))
        if not train_files:
            raise FileNotFoundError(f"No train Parquet files found in {output_dir}")

        # Extract timestamp from latest file
        latest_file = train_files[-1]
        # Filename format: train_YYYY-MM-DD_HHMMSS.parquet
        timestamp = latest_file.stem.replace("train_", "")
        logger.info(f"Loading latest timestamp: {timestamp}")

    # Load each split
    splits: dict[str, pd.DataFrame] = {}
    for split_name in ["train", "val", "test"]:
        parquet_path = output_dir / f"{split_name}_{timestamp}.parquet"

        if not parquet_path.exists():
            raise FileNotFoundError(f"Split file not found: {parquet_path}")

        splits[split_name] = pd.read_parquet(parquet_path)
        logger.info(f"Loaded {split_name}: {parquet_path} ({len(splits[split_name])} rows)")

    return splits["train"], splits["val"], splits["test"]


def inverse_transform(
    df: pd.DataFrame,
    scaler_params: dict[str, Any],
) -> pd.DataFrame:
    """
    Apply inverse Z-score transform using saved scaler parameters.

    Useful for converting model predictions back to original scale
    for interpretability and reporting.

    Args:
        df: Normalized DataFrame to inverse transform.
        scaler_params: Dict with mean, scale, feature_names from save_scaler_params().

    Returns:
        DataFrame with values in original scale.

    Example:
        >>> params = load_scaler_params('scaler.json')
        >>> predictions_original = inverse_transform(predictions_normalized, params)
    """
    df_inverse = df.copy()

    mean = np.array(scaler_params["mean"])
    scale = np.array(scaler_params["scale"])
    feature_names = scaler_params["feature_names"]

    # Only transform columns that were normalized
    cols_to_transform = [col for col in feature_names if col in df.columns]

    if cols_to_transform:
        # Create mapping from feature name to index in scaler arrays
        feature_idx = {name: i for i, name in enumerate(feature_names)}

        for col in cols_to_transform:
            idx = feature_idx[col]
            df_inverse[col] = df[col] * scale[idx] + mean[idx]

        logger.info(f"Inverse transformed {len(cols_to_transform)} columns")

    return df_inverse


def transform(
    df: pd.DataFrame,
    scaler_params: dict[str, Any],
) -> pd.DataFrame:
    """
    Apply forward Z-score transform using saved scaler parameters.

    This is the counterpart to `inverse_transform` and is useful for cross-ISO
    evaluation where we want to apply a *training* scaler to a different region's
    original-scale features.
    """
    df_scaled = df.copy()

    mean = np.array(scaler_params["mean"])
    scale = np.array(scaler_params["scale"])
    feature_names = scaler_params["feature_names"]

    cols_to_transform = [col for col in feature_names if col in df.columns]
    if cols_to_transform:
        feature_idx = {name: i for i, name in enumerate(feature_names)}
        for col in cols_to_transform:
            idx = feature_idx[col]
            df_scaled[col] = (df[col] - mean[idx]) / scale[idx]
        logger.info(f"Transformed {len(cols_to_transform)} columns to Z-score using saved params")

    return df_scaled
