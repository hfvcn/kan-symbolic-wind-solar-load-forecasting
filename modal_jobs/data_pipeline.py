"""
End-to-end data pipeline Modal job for KAN-SR project.

This module implements a fully idempotent data pipeline that:
1. Downloads ERCOT actuals from ARPA-E PERFORM S3
2. Preprocesses with interpolation and quality logging
3. Engineers features (cyclic, solar, lag)
4. Splits chronologically with gap and normalizes
5. Saves ML-ready Parquet artifacts

The pipeline uses step markers for idempotency: any step can fail and
re-running resumes from the last completed step. Failed steps clean up
partial outputs before re-raising to ensure clean retry.

References:
    - Modal Volume: kan-sr (configurable via KAN_SR_VOLUME env)
    - Storage contract: .planning/MODAL.md
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

# Configure module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


# =============================================================================
# Modal App Configuration
# =============================================================================

APP_NAME = "kan-sr-data-pipeline"
DEFAULT_VOLUME_NAME = os.environ.get("KAN_SR_VOLUME", "kan-sr")
VOLUME_MOUNT = "/vol"

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(DEFAULT_VOLUME_NAME, create_if_missing=True)

# Include local source tree in Modal containers so `import src.*` works.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

# Image with all data pipeline dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "h5py>=3.10",
        "s3fs>=2024.2.0",
        "pandas>=2.0",
        "numpy>=1.24",
        "scikit-learn>=1.3",
        "pvlib>=0.10.0",
        "pyarrow>=14.0",
        "tqdm>=4.66",
        "rich>=13.0",
    )
    .env({"PYTHONPATH": "/root/project"})
    .add_local_dir(SRC_DIR, remote_path="/root/project/src")
)


# =============================================================================
# Checkpointing Helpers
# =============================================================================


def _utc_run_id() -> str:
    """Generate unique run ID with UTC timestamp and UUID."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


def step_complete(run_dir: str | Path, step_name: str) -> bool:
    """Check if a step has been marked as complete."""
    marker = Path(run_dir) / f".step_{step_name}_done"
    return marker.exists()


def mark_step_complete(run_dir: str | Path, step_name: str, vol: modal.Volume) -> None:
    """Mark a step as complete and commit to volume."""
    marker = Path(run_dir) / f".step_{step_name}_done"
    marker.parent.mkdir(parents=True, exist_ok=True)

    with open(marker, "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())

    vol.commit()
    logger.info(f"Step '{step_name}' marked complete")


def cleanup_partial_output(output_path: str | Path) -> None:
    """Remove partial output file or directory on step failure."""
    output_path = Path(output_path)

    if output_path.is_file():
        output_path.unlink()
        logger.warning(f"Cleaned up partial file: {output_path}")
    elif output_path.is_dir():
        shutil.rmtree(output_path)
        logger.warning(f"Cleaned up partial directory: {output_path}")


def init_run_directories(run_dir: Path) -> dict[str, Path]:
    """Initialize all directories for a new run."""
    dirs = {
        "base": run_dir,
        "raw": run_dir / "raw",
        "processed": run_dir / "processed",
        "artifacts": run_dir / "artifacts",
        "reports": run_dir / "reports",
    }

    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    return dirs


# =============================================================================
# Pipeline Steps
# =============================================================================


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=1800)
def step_download(run_id: str, year: int = 2018, iso: str = "ERCOT") -> dict[str, Any]:
    """
    Step 1: Download ERCOT actuals from ARPA-E PERFORM S3.

    Downloads wind, solar, and load HDF5 files to {run_dir}/raw/.
    Idempotent: skips if step already complete.
    Error recovery: cleans up raw/ on failure, re-raises.
    """
    import sys

    sys.path.insert(0, "/vol")  # Ensure local imports work

    from src.data.download import download_iso_actuals

    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    raw_dir = run_dir / "raw"

    # Check idempotency
    if step_complete(run_dir, "download"):
        logger.info("Step 'download' already complete, skipping")
        # Return cached paths
        return {
            "run_id": run_id,
            "step": "download",
            "status": "skipped",
            "paths": {
                "wind": str(raw_dir / f"wind_actuals_{year}.h5"),
                "solar": str(raw_dir / f"solar_actuals_{year}.h5"),
                "load": str(raw_dir / f"load_actuals_{year}.h5"),
            },
        }

    # Initialize directories
    init_run_directories(run_dir)

    try:
        logger.info(f"Downloading {iso} actuals for year {year}")
        paths = download_iso_actuals(run_dir, year=year, iso=iso)

        # Commit volume and mark complete
        volume.commit()
        mark_step_complete(run_dir, "download", volume)

        return {
            "run_id": run_id,
            "step": "download",
            "status": "completed",
            "year": year,
            "iso": iso,
            "paths": paths,
        }

    except Exception as e:
        logger.error(f"Download failed: {e}")
        cleanup_partial_output(raw_dir)
        raise


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=1800)
def step_preprocess(run_id: str, year: int = 2018, iso: str = "ERCOT") -> dict[str, Any]:
    """
    Step 2: Preprocess raw data with interpolation and quality logging.

    Loads HDF5 files, interpolates short gaps, generates quality report.
    Saves cleaned data as intermediate Parquet.
    Error recovery: cleans up intermediate files on failure.
    """
    import pandas as pd

    import sys

    sys.path.insert(0, "/vol")

    from src.data.download import load_hdf5_to_dataframe
    from src.data.preprocess import (
        generate_quality_report,
        handle_long_gaps,
        interpolate_missing,
    )

    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    raw_dir = run_dir / "raw"
    reports_dir = run_dir / "reports"
    intermediate_path = run_dir / "intermediate_cleaned.parquet"

    # Check idempotency
    if step_complete(run_dir, "preprocess"):
        logger.info("Step 'preprocess' already complete, skipping")
        return {
            "run_id": run_id,
            "step": "preprocess",
            "status": "skipped",
            "intermediate_path": str(intermediate_path),
        }

    reports_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load raw HDF5 files
        logger.info("Loading raw HDF5 files...")
        dfs = {}
        for data_type in ["wind", "solar", "load"]:
            h5_path = raw_dir / f"{data_type}_actuals_{year}.h5"
            dfs[data_type] = load_hdf5_to_dataframe(
                h5_path,
                year=year,
                default_column_name=iso.upper(),
            )

        # Combine into single DataFrame (ISO-level aggregates)
        # Each dataframe has BA columns; use ISO total column when present, otherwise fallback to first.
        logger.info("Combining data types into unified DataFrame...")
        combined = pd.DataFrame(index=dfs["load"].index)

        for data_type, df in dfs.items():
            iso_u = iso.upper()
            if iso_u in df.columns:
                combined[data_type] = df[iso_u]
            else:
                combined[data_type] = df.iloc[:, 0]

        # Store original for quality report
        df_original = combined.copy()

        # Interpolate short gaps
        logger.info("Interpolating missing values...")
        df_interpolated, gap_log = interpolate_missing(combined, max_gap_hours=1.0)

        # Handle remaining gaps (drop rows with NaN)
        df_clean = handle_long_gaps(df_interpolated, gap_log, strategy="drop")

        # Generate quality report
        report_path = reports_dir / "quality_report.json"
        generate_quality_report(df_original, df_clean, gap_log, report_path)

        # Save intermediate Parquet
        df_clean.to_parquet(intermediate_path, compression="snappy")
        logger.info(f"Saved intermediate cleaned data: {intermediate_path}")

        # Commit and mark complete
        volume.commit()
        mark_step_complete(run_dir, "preprocess", volume)

        return {
            "run_id": run_id,
            "step": "preprocess",
            "status": "completed",
            "rows_original": len(df_original),
            "rows_cleaned": len(df_clean),
            "intermediate_path": str(intermediate_path),
            "report_path": str(report_path),
        }

    except Exception as e:
        logger.error(f"Preprocess failed: {e}")
        cleanup_partial_output(intermediate_path)
        cleanup_partial_output(reports_dir / "quality_report.json")
        raise


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=1800)
def step_features(run_id: str, iso: str = "ERCOT", target_cols: list[str] | None = None) -> dict[str, Any]:
    """
    Step 3: Apply feature engineering to cleaned data.

    Adds cyclic time encoding, solar position features, and lag features.
    Saves featured data as intermediate Parquet.
    Error recovery: cleans up intermediate files on failure.
    """
    import pandas as pd

    import sys

    sys.path.insert(0, "/vol")

    from src.data.features import add_all_features
    from src.data.meteorology import add_open_meteo_meteorology_features
    from src.config import get_iso_centroid

    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    intermediate_cleaned = run_dir / "intermediate_cleaned.parquet"
    intermediate_featured = run_dir / "intermediate_featured.parquet"
    met_cache = run_dir / "raw" / "open_meteo_hourly.parquet"

    if target_cols is None:
        target_cols = ["load", "wind", "solar"]

    # Check idempotency
    if step_complete(run_dir, "features"):
        logger.info("Step 'features' already complete, skipping")
        return {
            "run_id": run_id,
            "step": "features",
            "status": "skipped",
            "intermediate_path": str(intermediate_featured),
        }

    try:
        # Load cleaned data
        logger.info("Loading cleaned intermediate data...")
        df = pd.read_parquet(intermediate_cleaned)

        # Add meteorological proxy features (cache-first)
        logger.info("Adding meteorology features (Open-Meteo archive, cache-first)...")
        lat, lon = get_iso_centroid(iso)
        df = add_open_meteo_meteorology_features(
            df,
            latitude=lat,
            longitude=lon,
            cache_path=met_cache,
            allow_network=True,
            allow_missing=True,
        )

        # Apply all features
        logger.info("Applying feature engineering...")
        df_featured = add_all_features(df, target_cols=target_cols, latitude=lat, longitude=lon)

        # Save intermediate Parquet
        df_featured.to_parquet(intermediate_featured, compression="snappy")
        logger.info(f"Saved featured data: {intermediate_featured}")

        # Commit and mark complete
        volume.commit()
        mark_step_complete(run_dir, "features", volume)

        return {
            "run_id": run_id,
            "step": "features",
            "status": "completed",
            "rows": len(df_featured),
            "columns": len(df_featured.columns),
            "intermediate_path": str(intermediate_featured),
        }

    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        cleanup_partial_output(intermediate_featured)
        raise


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=1800)
def step_split_normalize(run_id: str, target_col: str = "load") -> dict[str, Any]:
    """
    Step 4: Split data chronologically and normalize features.

    Applies chronological split with gap, drops initial lag rows,
    normalizes using Z-score (fit on train only), saves final Parquet splits.
    Error recovery: cleans up processed/ and artifacts/ on failure.
    """
    import pandas as pd

    import sys

    sys.path.insert(0, "/vol")

    from src.data.split import (
        chronological_split,
        drop_initial_lag_rows,
        normalize_features,
        save_scaler_params,
        save_splits_to_parquet,
    )

    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id
    intermediate_featured = run_dir / "intermediate_featured.parquet"
    processed_dir = run_dir / "processed"
    artifacts_dir = run_dir / "artifacts"

    # Check idempotency
    if step_complete(run_dir, "split_normalize"):
        logger.info("Step 'split_normalize' already complete, skipping")
        return {
            "run_id": run_id,
            "step": "split_normalize",
            "status": "skipped",
            "processed_dir": str(processed_dir),
            "artifacts_dir": str(artifacts_dir),
        }

    processed_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load featured data
        logger.info("Loading featured intermediate data...")
        df = pd.read_parquet(intermediate_featured)

        # Chronological split with gap
        logger.info("Applying chronological split with 48-step gap...")
        train, val, test = chronological_split(df)

        # Drop initial lag rows from each split
        logger.info("Dropping initial lag rows...")
        train = drop_initial_lag_rows(train)
        val = drop_initial_lag_rows(val)
        test = drop_initial_lag_rows(test)

        # Normalize features (exclude target column)
        logger.info(f"Normalizing features (excluding target: {target_col})...")
        train_scaled, val_scaled, test_scaled, scaler_params = normalize_features(
            train, val, test, exclude_cols=[target_col]
        )

        # Save scaler parameters
        scaler_path = artifacts_dir / "scaler_params.json"
        save_scaler_params(scaler_params, scaler_path)

        # Save splits to Parquet with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        paths = save_splits_to_parquet(train_scaled, val_scaled, test_scaled, processed_dir, timestamp)

        # Commit and mark complete
        volume.commit()
        mark_step_complete(run_dir, "split_normalize", volume)

        return {
            "run_id": run_id,
            "step": "split_normalize",
            "status": "completed",
            "train_rows": len(train_scaled),
            "val_rows": len(val_scaled),
            "test_rows": len(test_scaled),
            "target_col": target_col,
            "paths": paths,
            "scaler_path": str(scaler_path),
        }

    except Exception as e:
        logger.error(f"Split/normalize failed: {e}")
        cleanup_partial_output(processed_dir)
        cleanup_partial_output(artifacts_dir)
        raise


# =============================================================================
# Pipeline Orchestrator
# =============================================================================


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=7200)
def run_pipeline(
    year: int = 2018,
    iso: str = "ERCOT",
    target_col: str = "load",
    force: bool = False,
) -> dict[str, Any]:
    """
    Orchestrate full data pipeline execution.

    Runs all steps in sequence. Each step checks its own completion marker
    for idempotency. If force=True, clears all markers and re-runs from scratch.

    Args:
        year: Data year to process (default: 2018).
        target_col: Target column for prediction (default: "load").
        force: If True, ignore existing markers and re-run all steps.

    Returns:
        Dict with run summary including paths to all artifacts.
    """
    run_id = _utc_run_id()
    run_dir = Path(VOLUME_MOUNT) / "runs" / run_id

    logger.info(f"Starting pipeline run: {run_id}")
    logger.info(f"  Year: {year}, Target: {target_col}, Force: {force}")

    # Initialize directories
    init_run_directories(run_dir)

    # Save run payload (metadata)
    payload = {
        "run_id": run_id,
        "year": year,
        "iso": iso,
        "target_col": target_col,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "force": force,
    }
    payload_path = run_dir / "payload.json"
    with open(payload_path, "w") as f:
        json.dump(payload, f, indent=2)
    volume.commit()

    # If force, clear all step markers
    if force:
        logger.info("Force mode: clearing all step markers")
        for marker in run_dir.glob(".step_*_done"):
            marker.unlink()
        volume.commit()

    # Run steps in sequence
    results: dict[str, Any] = {"run_id": run_id}

    # Step 1: Download
    results["download"] = step_download.remote(run_id, year=year, iso=iso)

    # Step 2: Preprocess
    results["preprocess"] = step_preprocess.remote(run_id, year=year, iso=iso)

    # Step 3: Features
    results["features"] = step_features.remote(run_id, iso=iso, target_cols=[target_col, "wind", "solar"])

    # Step 4: Split and normalize
    results["split_normalize"] = step_split_normalize.remote(run_id, target_col=target_col)

    # Record completion
    completed_at = datetime.now(timezone.utc).isoformat()
    payload["completed_at"] = completed_at
    payload["results"] = results

    with open(payload_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    volume.commit()

    logger.info(f"Pipeline complete: {run_id}")

    return {
        "run_id": run_id,
        "status": "completed",
        "year": year,
        "target_col": target_col,
        "started_at": payload["started_at"],
        "completed_at": completed_at,
        "processed_dir": str(run_dir / "processed"),
        "artifacts_dir": str(run_dir / "artifacts"),
        "reports_dir": str(run_dir / "reports"),
    }


# =============================================================================
# Local Entrypoint
# =============================================================================


@app.local_entrypoint()
def main(year: int = 2018, iso: str = "ERCOT", target: str = "load", force: bool = False) -> None:
    """
    Run the full data pipeline and sync artifacts locally.

    Usage:
        modal run modal_jobs/data_pipeline.py
        modal run modal_jobs/data_pipeline.py --year 2019 --iso MISO --target wind
        modal run modal_jobs/data_pipeline.py --force

    After completion, artifacts are synced to local runs/{run_id}/ directory.
    """
    import subprocess

    print(f"[pipeline] Starting data pipeline")
    print(f"[pipeline] Volume: {DEFAULT_VOLUME_NAME}")
    print(f"[pipeline] ISO: {iso}")
    print(f"[pipeline] Year: {year}, Target: {target}, Force: {force}")

    # Run pipeline
    result = run_pipeline.remote(year=year, iso=iso, target_col=target, force=force)
    print(json.dumps(result, indent=2))

    # Auto-sync artifacts to local runs/ directory
    run_id = result["run_id"]
    local_runs_base = Path("runs")
    local_runs_base.mkdir(parents=True, exist_ok=True)

    print(f"\n[sync] Syncing artifacts to: {local_runs_base}/{run_id}")

    # NOTE: `modal volume get` treats directory-vs-file differently. Always add a trailing slash
    # to reliably sync directories.
    volume_run_path = f"/runs/{run_id}/"
    try:
        subprocess.run(
            ["modal", "volume", "get", DEFAULT_VOLUME_NAME, volume_run_path, str(local_runs_base), "--force"],
            check=True,
        )
        print("[sync] Synced full run directory")
    except subprocess.CalledProcessError as e:
        print(f"[sync] Warning: Failed to sync run directory: {e}")

    print(f"\n[pipeline] COMPLETE")
    print(f"[pipeline] Artifacts synced to: {local_runs_base}/{run_id}")
