"""
Data preprocessing for ARPA-E PERFORM time series.

This module provides interpolation for missing values and data quality logging
for thesis-grade documentation of data cleaning operations.

Methodology:
    - Short gaps (< 1 hour): Cubic spline interpolation preserves smoothness
    - Long gaps (> 6 hours): Logged for appropriate handling (drop/neighbor/keep)
    - Outliers: Marked but NOT modified (preserves raw signal characteristics)

The quality report provides complete traceability for thesis documentation.

References:
    - PERFORM data has 5-minute resolution (288 points/day)
    - ERCOT zones may have occasional missing values from sensor/transmission issues
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def find_missing_gaps(
    df: pd.DataFrame,
    resolution_minutes: int = 5,
) -> list[dict[str, Any]]:
    """
    Scan each column for consecutive NaN blocks and record gap details.

    Identifies all gaps in the DataFrame and returns structured information
    for logging and decision-making about interpolation strategies.

    Args:
        df: DataFrame with DatetimeIndex to scan for missing values.
        resolution_minutes: Expected time resolution in minutes (default: 5).

    Returns:
        List of gap dictionaries, each containing:
            - column: Column name where gap occurred
            - start_time: Start timestamp of the gap
            - end_time: End timestamp of the gap
            - gap_size: Number of consecutive missing steps
            - gap_hours: Duration of gap in hours

    Example:
        >>> gaps = find_missing_gaps(df, resolution_minutes=5)
        >>> for gap in gaps:
        ...     print(f"{gap['column']}: {gap['gap_size']} steps ({gap['gap_hours']:.2f} hours)")
    """
    gaps: list[dict[str, Any]] = []

    for column in df.columns:
        series = df[column]
        is_nan = series.isna()

        if not is_nan.any():
            continue

        # Find consecutive NaN blocks using diff to detect transitions
        nan_groups = (is_nan != is_nan.shift()).cumsum()

        # Group by consecutive blocks where is_nan is True
        for group_id in nan_groups[is_nan].unique():
            mask = (nan_groups == group_id) & is_nan
            gap_indices = df.index[mask]

            if len(gap_indices) == 0:
                continue

            gap_size = len(gap_indices)
            gap_hours = gap_size * resolution_minutes / 60

            gap_info = {
                "column": column,
                "start_time": str(gap_indices[0]),
                "end_time": str(gap_indices[-1]),
                "gap_size": gap_size,
                "gap_hours": gap_hours,
            }
            gaps.append(gap_info)
            logger.debug(f"Gap found: {column} at {gap_info['start_time']} ({gap_size} steps)")

    logger.info(f"Found {len(gaps)} gaps across {len(df.columns)} columns")
    return gaps


def interpolate_missing(
    df: pd.DataFrame,
    max_gap_hours: float = 1.0,
    resolution_minutes: int = 5,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Interpolate short gaps using cubic spline method.

    Short gaps (default: < 1 hour) are filled using cubic spline interpolation,
    which provides smooth transitions that preserve signal characteristics.
    Longer gaps are left as NaN for explicit handling by the caller.

    Args:
        df: DataFrame with DatetimeIndex and numeric columns.
        max_gap_hours: Maximum gap duration to interpolate (hours). Default: 1.0.
        resolution_minutes: Data resolution in minutes. Default: 5.

    Returns:
        Tuple of (interpolated_df, gap_log):
            - interpolated_df: DataFrame with short gaps filled
            - gap_log: Dict with gap analysis and interpolation statistics

    Methodology:
        - Uses pandas interpolate(method='spline', order=3) for cubic spline
        - limit parameter restricts interpolation to gaps <= max_gap_hours
        - limit_direction='both' handles gaps at series boundaries

    Example:
        >>> df_clean, log = interpolate_missing(df, max_gap_hours=1.0)
        >>> print(f"Interpolated {log['gaps_interpolated']} gaps")
    """
    # Calculate maximum consecutive steps to interpolate
    max_consecutive = int(max_gap_hours * 60 / resolution_minutes)
    logger.info(f"Max interpolation: {max_gap_hours} hours = {max_consecutive} steps")

    # Find all gaps before interpolation
    gaps_before = find_missing_gaps(df, resolution_minutes)

    # Count missing values before
    missing_before = df.isna().sum().to_dict()
    total_missing_before = df.isna().sum().sum()

    # Create a copy for interpolation
    df_interpolated = df.copy()

    # Apply cubic spline interpolation with limit
    # Note: spline interpolation requires at least 4 points, so we fall back to linear
    # for very short series or columns with too few valid points
    for column in df_interpolated.columns:
        valid_count = df_interpolated[column].notna().sum()
        if valid_count >= 4:
            try:
                df_interpolated[column] = df_interpolated[column].interpolate(
                    method="spline",
                    order=3,
                    limit=max_consecutive,
                    limit_direction="both",
                )
            except Exception as e:
                # Fall back to linear if spline fails
                logger.warning(f"Spline interpolation failed for {column}, using linear: {e}")
                df_interpolated[column] = df_interpolated[column].interpolate(
                    method="linear",
                    limit=max_consecutive,
                    limit_direction="both",
                )
        elif valid_count > 0:
            # Not enough points for spline, use linear
            df_interpolated[column] = df_interpolated[column].interpolate(
                method="linear",
                limit=max_consecutive,
                limit_direction="both",
            )

    # Find remaining gaps after interpolation
    gaps_after = find_missing_gaps(df_interpolated, resolution_minutes)

    # Count missing values after
    missing_after = df_interpolated.isna().sum().to_dict()
    total_missing_after = df_interpolated.isna().sum().sum()

    # Categorize gaps
    short_gaps = [g for g in gaps_before if g["gap_hours"] <= max_gap_hours]
    long_gaps = [g for g in gaps_before if g["gap_hours"] > max_gap_hours]

    # Build gap log
    gap_log: dict[str, Any] = {
        "parameters": {
            "max_gap_hours": max_gap_hours,
            "resolution_minutes": resolution_minutes,
            "max_consecutive_steps": max_consecutive,
        },
        "summary": {
            "total_missing_before": int(total_missing_before),
            "total_missing_after": int(total_missing_after),
            "values_interpolated": int(total_missing_before - total_missing_after),
            "gaps_found": len(gaps_before),
            "gaps_interpolated": len(short_gaps),
            "gaps_remaining": len(gaps_after),
        },
        "gaps_by_column_before": {k: int(v) for k, v in missing_before.items()},
        "gaps_by_column_after": {k: int(v) for k, v in missing_after.items()},
        "short_gaps": short_gaps,
        "long_gaps": long_gaps,
    }

    logger.info(
        f"Interpolation complete: {gap_log['summary']['values_interpolated']} values filled, "
        f"{gap_log['summary']['gaps_remaining']} gaps remaining"
    )

    return df_interpolated, gap_log


def handle_long_gaps(
    df: pd.DataFrame,
    gap_log: dict[str, Any],
    strategy: str = "drop",
) -> pd.DataFrame:
    """
    Handle remaining NaN values after interpolation.

    Provides multiple strategies for dealing with gaps that were too long
    to interpolate, typically caused by extended sensor outages.

    Args:
        df: DataFrame with potential remaining NaN values.
        gap_log: Gap log from interpolate_missing() for context.
        strategy: How to handle remaining NaN values:
            - "drop": Remove rows containing any NaN (default)
            - "neighbor": Fill with nearest valid value
            - "keep_nan": Leave NaN for later handling

    Returns:
        DataFrame with long gaps handled according to strategy.

    Example:
        >>> df_clean = handle_long_gaps(df, gap_log, strategy="drop")
        >>> assert not df_clean.isna().any().any()
    """
    rows_before = len(df)
    nan_count_before = df.isna().sum().sum()

    if nan_count_before == 0:
        logger.info("No remaining NaN values to handle")
        return df

    df_handled = df.copy()

    if strategy == "drop":
        # Drop rows with any NaN
        df_handled = df_handled.dropna()
        rows_dropped = rows_before - len(df_handled)
        logger.info(f"Dropped {rows_dropped} rows with NaN (strategy='drop')")

    elif strategy == "neighbor":
        # Forward fill then backward fill to use nearest valid value
        df_handled = df_handled.ffill().bfill()
        logger.info(f"Filled {nan_count_before} NaN values with nearest neighbor (strategy='neighbor')")

    elif strategy == "keep_nan":
        # Leave NaN for caller to handle
        logger.info(f"Keeping {nan_count_before} NaN values (strategy='keep_nan')")

    else:
        raise ValueError(f"Unknown strategy: {strategy}. Must be one of: drop, neighbor, keep_nan")

    return df_handled


def generate_quality_report(
    df_original: pd.DataFrame,
    df_processed: pd.DataFrame,
    gap_log: dict[str, Any],
    output_path: str | Path,
) -> str:
    """
    Generate detailed JSON quality report for thesis documentation.

    Creates a comprehensive data quality report documenting all transformations
    applied during preprocessing, suitable for academic documentation.

    Args:
        df_original: Original DataFrame before any preprocessing.
        df_processed: Final DataFrame after all preprocessing.
        gap_log: Gap log from interpolate_missing().
        output_path: Path to write JSON report.

    Returns:
        Path to the generated report (as string).

    Report Contents:
        - Timestamp and metadata
        - Missing value statistics (before/after per column)
        - Gap details with treatment applied
        - Outlier analysis (values > 3 std, marked NOT modified)
        - Summary statistics

    Example:
        >>> report_path = generate_quality_report(df_orig, df_clean, gap_log, "quality.json")
        >>> with open(report_path) as f:
        ...     report = json.load(f)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Basic statistics
    report: dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "original_shape": {
            "rows": len(df_original),
            "columns": len(df_original.columns),
        },
        "processed_shape": {
            "rows": len(df_processed),
            "columns": len(df_processed.columns),
        },
        "rows_removed": len(df_original) - len(df_processed),
        "time_range": {
            "start": str(df_original.index.min()) if len(df_original) > 0 else None,
            "end": str(df_original.index.max()) if len(df_original) > 0 else None,
        },
    }

    # Missing value analysis
    missing_original: dict[str, int] = df_original.isna().sum().to_dict()
    missing_processed: dict[str, int] = df_processed.isna().sum().to_dict()

    report["missing_values"] = {
        "original": {k: int(v) for k, v in missing_original.items()},
        "processed": {k: int(v) for k, v in missing_processed.items()},
        "total_original": int(sum(missing_original.values())),
        "total_processed": int(sum(missing_processed.values())),
    }

    # Gap analysis from interpolation
    report["gap_analysis"] = gap_log

    # Outlier analysis (mark but do NOT modify per user decision)
    outliers: dict[str, list[dict[str, Any]]] = {}
    for column in df_processed.select_dtypes(include=[np.number]).columns:
        series = df_processed[column].dropna()
        if len(series) == 0:
            continue

        mean = series.mean()
        std = series.std()

        if std == 0:
            continue

        # Find values > 3 standard deviations from mean
        outlier_mask = np.abs(series - mean) > 3 * std
        outlier_indices = series[outlier_mask].index

        if len(outlier_indices) > 0:
            column_outliers = []
            for idx in outlier_indices:
                column_outliers.append({
                    "timestamp": str(idx),
                    "value": float(series[idx]),
                    "z_score": float((series[idx] - mean) / std),
                    "treatment": "marked_not_modified",
                })
            outliers[column] = column_outliers
            logger.debug(f"Found {len(column_outliers)} outliers in {column}")

    report["outliers"] = {
        "method": "3_sigma",
        "treatment": "marked_not_modified",
        "by_column": outliers,
        "total_count": sum(len(v) for v in outliers.values()),
    }

    # Summary statistics for processed data
    numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
    summary_stats: dict[str, dict[str, float]] = {}

    for column in numeric_cols:
        col_data = df_processed[column].dropna()
        if len(col_data) > 0:
            summary_stats[column] = {
                "mean": float(col_data.mean()),
                "std": float(col_data.std()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "median": float(col_data.median()),
                "count": int(len(col_data)),
            }

    report["summary_statistics"] = summary_stats

    # Write report
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"Quality report written to: {output_path}")
    return str(output_path)


def validate_no_nan_inf(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame contains no NaN or Inf values.

    Final validation step before using data for model training.
    Raises ValueError with details if invalid values are found.

    Args:
        df: DataFrame to validate.

    Returns:
        True if DataFrame is clean (no NaN or Inf).

    Raises:
        ValueError: If NaN or Inf values are found, with detailed message
            specifying which columns and how many invalid values.

    Example:
        >>> validate_no_nan_inf(df_clean)  # Returns True or raises ValueError
        True
    """
    nan_counts = df.isna().sum()
    nan_columns = nan_counts[nan_counts > 0]

    inf_counts = pd.Series(0, index=df.columns)
    for column in df.select_dtypes(include=[np.number]).columns:
        inf_counts[column] = np.isinf(df[column]).sum()
    inf_columns = inf_counts[inf_counts > 0]

    errors = []

    if len(nan_columns) > 0:
        nan_details = ", ".join([f"{col}={count}" for col, count in nan_columns.items()])
        errors.append(f"NaN values found: {nan_details}")

    if len(inf_columns) > 0:
        inf_details = ", ".join([f"{col}={count}" for col, count in inf_columns.items()])
        errors.append(f"Inf values found: {inf_details}")

    if errors:
        error_msg = "; ".join(errors)
        raise ValueError(f"DataFrame validation failed: {error_msg}")

    logger.info("Validation passed: no NaN or Inf values")
    return True
