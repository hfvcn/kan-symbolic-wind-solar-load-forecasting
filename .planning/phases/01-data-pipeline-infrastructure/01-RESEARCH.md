# Phase 1: Data Pipeline & Infrastructure - Research

**Researched:** 2026-02-25
**Domain:** ARPA-E PERFORM HDF5 data ingestion, time series preprocessing, Modal cloud infrastructure
**Confidence:** HIGH

## Summary

Phase 1 establishes the foundational data pipeline for the KAN-SR wind-solar load forecasting project. The ARPA-E PERFORM dataset provides 5-minute resolution time-coincident wind, solar, and load data for ERCOT (2017-2018) in HDF5 format, hosted on AWS S3 with anonymous access. The pipeline must download this data, align timestamps to UTC, handle missing values via spline interpolation, engineer multi-modal features (meteorological, astronomical, cyclic time encoding, autoregressive lags), apply Z-score normalization, and perform strictly chronological train/val/test splitting with lag-window gaps to prevent data leakage.

The infrastructure layer uses Modal for cloud compute with Modal Volumes for persistent artifact storage. The project already has a working smoke test demonstrating Volume roundtrip, retry logic, and parallel fanout. The data pipeline must follow the established artifact contract: write to `/vol/runs/<run_id>/`, use `payload.json` for metadata, `metrics.csv` for logs, and commit periodically.

**Primary recommendation:** Build an idempotent, checkpoint-capable data pipeline using h5py + s3fs for HDF5 access, pandas for preprocessing, scikit-learn for normalization and splitting, and pvlib for solar angle calculations. Store processed tensors as Parquet files on Modal Volume with JSON metadata. Design each processing step to be resumable by checking for existing outputs before re-running.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Missing Data - Short-term (<1 hour):** Follow ARPA-E PERFORM dataset conventions; Claude decides interpolation method based on data characteristics
- **Missing Data - Long-term (>6 hours):** Claude decides handling strategy (removal, neighbor interpolation, etc.)
- **Data Quality Logging:** Generate detailed logs recording all missing data locations and treatments for thesis documentation
- **Outliers:** Preserve original data without modification; mark in logs for later decision
- **Autoregressive Lag Window:** t-1 to t-48 (4 hours at 5-minute resolution = 48 time steps)
- **Normalization Strategy:** Z-score standardization for all features
- **Cyclic Time Features:** Sin/cos trigonometric encoding for hour, weekday, and month
- **Meteorological Variables:** Claude selects based on actual dataset availability
- **Pipeline Idempotency:** Re-runnable; skip completed steps on re-execution
- **Error Recovery:** Rollback on failure, clean partial outputs, retry on next run
- **Logging Detail:** Minimal runtime output (progress bar + summary); detailed report on completion
- **Checkpointing:** Save intermediate results after each processing step
- **Storage:** Modal Volume only (no S3); simplified architecture
- **File Formats:** Parquet for feature data, JSON for metadata
- **Versioning:** Timestamp-based naming (data_20250225_143000.parquet)
- **Local Sync:** Auto-sync to local `runs/` directory for debugging

### Claude's Discretion

- Specific interpolation algorithm selection
- Meteorological variable selection (based on dataset contents)
- Long-term missing data handling strategy
- Progress bar and report styling

### Deferred Ideas (OUT OF SCOPE)

None -- discussion stayed within phase scope

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-01 | Acquire wind/solar/load synchronized data from ARPA-E PERFORM (ERCOT, HDF5, 5-min resolution) | h5py + s3fs anonymous access pattern; HDF5 structure documented with meta/time_index/actuals keys |
| DATA-02 | Data preprocessing pipeline (UTC timestamp alignment, spline interpolation, Z-score normalization, cyclic time encoding) | pandas interpolate() with scipy spline methods; sklearn StandardScaler; sin/cos encoding formula |
| DATA-03 | Multi-modal feature engineering (meteorological, astronomical, cyclic, autoregressive lags) | pvlib solar position; cyclic encoding formula; pandas shift() for lag features; TimeSeriesSplit with gap |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| h5py | >=3.10 | Read ARPA-E PERFORM HDF5 files | Standard Python HDF5 interface; required for .h5 format |
| s3fs | >=2024.2.0 | Anonymous S3 access for ARPA-E data | Enables direct streaming from `s3://arpa-e-perform/` without credentials |
| pandas | >=2.0 | Time series manipulation, DataFrame operations | Industry standard; integrates with all other tools |
| numpy | >=1.24 | Array operations, mathematical functions | Foundation of scientific Python; JAX-compatible arrays |
| scikit-learn | >=1.3 | StandardScaler, TimeSeriesSplit, metrics | Standard preprocessing and splitting tools |
| pvlib | >=0.10.0 | Solar position calculations (altitude, azimuth) | NREL SPA algorithm; validated against USNO ephemeris |
| pyarrow | >=14.0 | Parquet file I/O with compression | Required for pandas Parquet support; efficient columnar storage |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| modal | >=0.60 | Cloud compute and persistent volumes | All cloud operations; already validated in smoke_test.py |
| tqdm | >=4.66 | Progress bars for long operations | User-facing progress during download and preprocessing |
| rich | >=13.0 | Console output formatting, tables | Detailed reports and structured logging |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pvlib | pysolar | pysolar is simpler but pvlib has more features and better validation; pvlib preferred for energy domain |
| pandas | polars | Polars is faster but pandas has better h5py/HDF5 integration and ecosystem compatibility |
| pyarrow | fastparquet | PyArrow is more feature-complete; fastparquet slightly faster for simple cases |
| StandardScaler | MinMaxScaler | Z-score handles outliers better; user explicitly chose Z-score normalization |

**Installation:**
```bash
pip install h5py s3fs pandas numpy scikit-learn pvlib pyarrow tqdm rich
```

## Architecture Patterns

### Recommended Project Structure
```
graduation-design/
|-- modal_jobs/
|   |-- smoke_test.py           # Already exists - infrastructure validation
|   |-- data_pipeline.py        # NEW: Main data pipeline Modal job
|-- src/
|   |-- __init__.py
|   |-- data/
|   |   |-- __init__.py
|   |   |-- download.py         # S3 download + caching
|   |   |-- preprocess.py       # Cleaning, interpolation
|   |   |-- features.py         # Feature engineering
|   |   |-- split.py            # Chronological train/val/test
|   |-- config.py               # Paths, hyperparameters
|-- runs/                       # Local sync of Modal artifacts (gitignored)
|-- scripts/
|   |-- sync_from_modal.sh      # Already exists
```

### Pattern 1: Idempotent Step Pattern
**What:** Each processing step checks for existing outputs before running
**When to use:** All pipeline steps to enable resume after failure

```python
# Source: Project CONTEXT.md requirements
def step_download(run_dir: str, config: dict) -> str:
    """Download HDF5 if not already cached."""
    output_path = f"{run_dir}/raw/ercot_2018.h5"
    if os.path.exists(output_path):
        logger.info(f"Skipping download - exists: {output_path}")
        return output_path

    # Perform download...
    return output_path
```

### Pattern 2: Modal Volume Artifact Contract
**What:** Consistent artifact structure across all runs
**When to use:** All Modal jobs writing results

```python
# Source: Project MODAL.md
def init_run(volume_mount: str = "/vol") -> dict:
    """Initialize run directory with standard structure."""
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S") + f"_{uuid.uuid4().hex[:8]}"
    run_dir = f"{volume_mount}/runs/{run_id}"
    os.makedirs(f"{run_dir}/raw", exist_ok=True)
    os.makedirs(f"{run_dir}/processed", exist_ok=True)
    os.makedirs(f"{run_dir}/artifacts", exist_ok=True)

    payload = {
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "phase": "data-pipeline",
        "config": {...}
    }
    with open(f"{run_dir}/payload.json", "w") as f:
        json.dump(payload, f, indent=2)

    return {"run_id": run_id, "run_dir": run_dir}
```

### Pattern 3: Time Series Chronological Split with Gap
**What:** Split data respecting temporal order with gap for lag features
**When to use:** Train/val/test splitting for autoregressive models

```python
# Source: scikit-learn TimeSeriesSplit documentation
def chronological_split(df: pd.DataFrame,
                        train_ratio: float = 0.7,
                        val_ratio: float = 0.15,
                        gap_steps: int = 48) -> tuple:
    """
    Split time series data chronologically with lag-window gap.

    Args:
        df: DataFrame sorted by time index
        train_ratio: Fraction for training
        val_ratio: Fraction for validation (test = 1 - train - val)
        gap_steps: Gap between splits (48 = 4 hours at 5-min resolution)
    """
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    # Apply gaps to prevent lag feature leakage
    train = df.iloc[:train_end]
    val = df.iloc[train_end + gap_steps:val_end]
    test = df.iloc[val_end + gap_steps:]

    return train, val, test
```

### Pattern 4: Cyclic Time Feature Encoding
**What:** Encode periodic time features using sin/cos to preserve cyclical relationships
**When to use:** Hour of day, day of week, month of year features

```python
# Source: Feature-Engine CyclicalFeatures documentation
def encode_cyclic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add sin/cos encoded time features."""
    # Hour of day (period = 24)
    df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)

    # Day of week (period = 7)
    df['dow_sin'] = np.sin(2 * np.pi * df.index.dayofweek / 7)
    df['dow_cos'] = np.cos(2 * np.pi * df.index.dayofweek / 7)

    # Month of year (period = 12)
    df['month_sin'] = np.sin(2 * np.pi * df.index.month / 12)
    df['month_cos'] = np.cos(2 * np.pi * df.index.month / 12)

    return df
```

### Anti-Patterns to Avoid

- **Random train/test split on time series:** Using `train_test_split(shuffle=True)` causes data leakage. Always use chronological splits with `shuffle=False` or `TimeSeriesSplit`.
- **Creating lag features before splitting:** Lag features at split boundaries will leak future information. Create lags after splitting, or use gaps equal to max lag window.
- **Writing to container local disk instead of Volume mount:** Data written to `/tmp/` or other local paths is lost when container terminates. Always write to the Volume mount path (e.g., `/vol/`).
- **Forgetting volume.commit():** Changes to Modal Volumes are only persisted after `volume.commit()`. Call periodically and at end of processing.
- **Backfilling missing values:** Using future data to fill past gaps. Always use forward-fill or interpolation methods that only use past values.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Missing value interpolation | Custom interpolation logic | `pandas.DataFrame.interpolate(method='spline', order=3)` | Wraps scipy.interpolate.UnivariateSpline; handles edge cases |
| Solar angle calculation | Manual ephemeris math | `pvlib.solarposition.get_solarposition()` | NREL SPA algorithm validated against USNO; handles refraction |
| Feature normalization | Manual Z-score computation | `sklearn.preprocessing.StandardScaler` | Handles partial_fit for streaming; stores mean/std for inverse |
| Time series splitting | Manual index slicing | `sklearn.model_selection.TimeSeriesSplit` with `gap` parameter | Handles cross-validation folds properly; built-in gap support |
| Cyclic encoding | Manual sin/cos formulas | `feature_engine.creation.CyclicalFeatures` or pattern above | Consistent API; handles multiple features |
| S3 anonymous access | Manual boto3 config | `s3fs.S3FileSystem(anon=True)` | Clean abstraction; handles credential-free access |
| HDF5 reading | Raw file parsing | `h5py.File` context manager | Standard interface; handles chunking and compression |
| Parquet I/O | Custom serialization | `pandas.DataFrame.to_parquet(engine='pyarrow')` | Columnar storage; efficient compression; column pruning |

**Key insight:** Time series preprocessing has subtle edge cases (boundary effects in interpolation, timezone handling, lag feature leakage) that standard libraries handle correctly. Custom implementations frequently introduce bugs that are hard to detect until model evaluation.

## Common Pitfalls

### Pitfall 1: Data Leakage via Lag Features at Split Boundaries
**What goes wrong:** Lag features (e.g., `P(t-48)`) at the start of validation/test sets use values from the training set, leaking information.
**Why it happens:** Lag features are computed on the full dataset before splitting, or splits don't account for the lag window.
**How to avoid:** Insert a gap between splits equal to the maximum lag window (48 steps = 4 hours). Drop the first 48 rows of val/test sets, or compute lag features after splitting.
**Warning signs:** Test accuracy suspiciously close to training accuracy; model performance degrades sharply on truly new data.

### Pitfall 2: Silent HDF5 Data Corruption from Scale Factors
**What goes wrong:** ARPA-E PERFORM HDF5 files store power values as integers with scale factors in attributes. Reading raw values without applying scale factor gives meaningless numbers.
**Why it happens:** Scale factors are stored in HDF5 attributes, not the main data arrays.
**How to avoid:** Always read and apply scale factors: `actual_mw = raw_value * scale_factor`. Check attribute names in the PERFORM documentation.
**Warning signs:** Power values are in unexpected ranges (thousands instead of MW); data doesn't match PERFORM documentation examples.

### Pitfall 3: Timezone Confusion Between Local and UTC
**What goes wrong:** ERCOT operates in US Central Time but PERFORM data is stored in UTC. Mixing timezones corrupts solar angle calculations and diurnal patterns.
**Why it happens:** Solar angle calculations require location-aware local time, but data is UTC.
**How to avoid:** Keep all data in UTC internally. Pass UTC timestamps to pvlib with explicit timezone. Apply timezone conversion only for display.
**Warning signs:** Sunrise/sunset times don't match expected local times; solar features show 6-hour offsets.

### Pitfall 4: Modal Volume Write Without Commit
**What goes wrong:** Data written to Volume mount path is not persisted; subsequent jobs or manual inspection shows empty directories.
**Why it happens:** Modal Volumes require explicit `volume.commit()` to persist changes. Background commits happen "every few seconds" but are not immediate.
**How to avoid:** Call `volume.commit()` after each major write operation and at job completion. Add commit calls in finally blocks or atexit handlers.
**Warning signs:** Files exist during job execution but are missing when accessed from another job or via `modal volume ls`.

### Pitfall 5: Memory Exhaustion on Full Dataset Load
**What goes wrong:** Loading full 2-year ERCOT dataset into memory at once exhausts container RAM, causing OOM crashes.
**Why it happens:** 5-minute resolution = 105K rows/year with many features. Multiple copies during preprocessing multiply memory usage.
**How to avoid:** Process year-by-year or month-by-month. Use chunked reading from HDF5. Write intermediate results to Parquet immediately after processing. Release DataFrames with `del df; gc.collect()`.
**Warning signs:** Job exits with signal 9 (SIGKILL); no error traceback; "Killed" message in logs.

### Pitfall 6: Interpolation Extrapolating Beyond Data Bounds
**What goes wrong:** Spline interpolation at data boundaries produces wild extrapolations instead of sensible values.
**Why it happens:** Splines are only defined within the data range; extrapolation is mathematically undefined.
**How to avoid:** Use `fill_value='extrapolate'` with caution or clip to boundary values. For long gaps (>6 hours per user decision), consider dropping rather than interpolating.
**Warning signs:** Interpolated values are negative (physically impossible for power); spline produces oscillations at boundaries.

## Code Examples

### HDF5 Data Access from S3 (DATA-01)
```python
# Source: PERFORM-Forecasts/documentation ERCOT_demo.md
import h5py
import pandas as pd
import s3fs

def load_wind_actuals(year: int = 2018) -> pd.DataFrame:
    """Load ERCOT wind actuals from ARPA-E PERFORM S3."""
    s3_path = f's3://arpa-e-perform/ERCOT/{year}/Wind/Actuals/BA_level/BA_wind_actuals_{year}.h5'
    fs = s3fs.S3FileSystem(anon=True)

    with fs.open(s3_path, 'rb') as s3_file:
        with h5py.File(s3_file, 'r') as f:
            # Read metadata
            meta = pd.DataFrame(f['meta'][...])

            # Read time index (stored as bytes, convert to datetime)
            time_index = pd.to_datetime(f['time_index'][...].astype(str))

            # Read actuals (may need scale_factor from attributes)
            actuals = f['actuals'][...]

            # Build DataFrame
            df = pd.DataFrame(actuals, index=time_index, columns=meta['name'].values)
            df.index = df.index.tz_localize('UTC')

    return df
```

### Missing Value Interpolation (DATA-02)
```python
# Source: pandas interpolate() documentation
def interpolate_missing(df: pd.DataFrame,
                        max_gap_hours: float = 1.0,
                        resolution_minutes: int = 5) -> tuple[pd.DataFrame, dict]:
    """
    Interpolate missing values using cubic spline for short gaps.

    Returns:
        df: DataFrame with interpolated values
        log: Dict with gap statistics for thesis documentation
    """
    max_consecutive = int(max_gap_hours * 60 / resolution_minutes)  # 12 for 1 hour

    # Log missing data locations before interpolation
    missing_log = {
        "total_missing": df.isna().sum().to_dict(),
        "missing_locations": []
    }

    # Find consecutive missing blocks
    for col in df.columns:
        mask = df[col].isna()
        groups = mask.ne(mask.shift()).cumsum()
        for group_id, group_data in df[mask].groupby(groups[mask]):
            gap_size = len(group_data)
            if gap_size > 0:
                missing_log["missing_locations"].append({
                    "column": col,
                    "start": str(group_data.index[0]),
                    "end": str(group_data.index[-1]),
                    "gap_size": gap_size,
                    "treatment": "interpolate" if gap_size <= max_consecutive else "drop"
                })

    # Interpolate short gaps with cubic spline
    df_interp = df.interpolate(
        method='spline',
        order=3,
        limit=max_consecutive,
        limit_direction='forward'
    )

    return df_interp, missing_log
```

### Solar Position Features (DATA-03)
```python
# Source: pvlib solarposition documentation
import pvlib

def add_solar_features(df: pd.DataFrame,
                       latitude: float = 31.0,  # ERCOT centroid
                       longitude: float = -100.0) -> pd.DataFrame:
    """Add solar position features (altitude, azimuth)."""

    location = pvlib.location.Location(latitude, longitude, tz='UTC')

    # Get solar position for all timestamps
    solar_pos = location.get_solarposition(df.index)

    # Add to DataFrame
    df['solar_altitude'] = solar_pos['elevation']  # Degrees above horizon
    df['solar_azimuth'] = solar_pos['azimuth']     # Degrees east of north

    # Add night flag (solar altitude < 0)
    df['is_night'] = (df['solar_altitude'] < 0).astype(int)

    return df
```

### Autoregressive Lag Features (DATA-03)
```python
# Source: scikit-learn lagged features example
def add_lag_features(df: pd.DataFrame,
                     target_cols: list[str],
                     lags: list[int] = None) -> pd.DataFrame:
    """
    Add lagged versions of target columns.

    Args:
        df: DataFrame with time series data
        target_cols: Columns to create lags for
        lags: List of lag steps (default: 1-48 for 4 hours at 5-min)
    """
    if lags is None:
        lags = list(range(1, 49))  # t-1 to t-48

    for col in target_cols:
        for lag in lags:
            df[f'{col}_lag_{lag}'] = df[col].shift(lag)

    # Drop rows with NaN from lag creation (first 48 rows)
    n_drop = max(lags)
    df = df.iloc[n_drop:].copy()

    return df
```

### Z-Score Normalization with Scaler Persistence (DATA-02)
```python
# Source: scikit-learn StandardScaler documentation
import json
from sklearn.preprocessing import StandardScaler

def normalize_features(train_df: pd.DataFrame,
                       val_df: pd.DataFrame,
                       test_df: pd.DataFrame,
                       save_path: str) -> tuple:
    """
    Fit StandardScaler on train, transform all splits.
    Save scaler parameters for later inverse transform.
    """
    feature_cols = [c for c in train_df.columns if c not in ['target']]

    scaler = StandardScaler()

    # Fit on training data only (prevent data leakage)
    train_scaled = train_df.copy()
    train_scaled[feature_cols] = scaler.fit_transform(train_df[feature_cols])

    # Transform validation and test
    val_scaled = val_df.copy()
    val_scaled[feature_cols] = scaler.transform(val_df[feature_cols])

    test_scaled = test_df.copy()
    test_scaled[feature_cols] = scaler.transform(test_df[feature_cols])

    # Save scaler parameters as JSON for reproducibility
    scaler_params = {
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "feature_names": feature_cols
    }
    with open(save_path, 'w') as f:
        json.dump(scaler_params, f, indent=2)

    return train_scaled, val_scaled, test_scaled
```

### Parquet Output with Metadata (Storage)
```python
# Source: pandas to_parquet documentation
def save_processed_data(df: pd.DataFrame,
                        output_dir: str,
                        split_name: str,
                        metadata: dict) -> str:
    """Save processed DataFrame as Parquet with JSON metadata."""
    import json
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parquet_path = f"{output_dir}/{split_name}_{timestamp}.parquet"
    meta_path = f"{output_dir}/{split_name}_{timestamp}_meta.json"

    # Save Parquet with snappy compression
    df.to_parquet(parquet_path, engine='pyarrow', compression='snappy')

    # Save metadata
    metadata.update({
        "parquet_file": parquet_path,
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "columns": df.columns.tolist(),
        "created_at": datetime.now().isoformat()
    })
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return parquet_path
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CSV file storage | Parquet with columnar compression | 2020+ | 10x faster reads; 5x smaller files; column selection |
| Manual timezone handling | pandas tz-aware DatetimeIndex | pandas 2.0 (2023) | Eliminates timezone conversion bugs |
| Custom S3 credential management | s3fs anonymous access | Stable | Simplified public data access |
| Colab persistent storage | Modal Volumes | 2024-2025 | More reliable; no session timeouts; better artifact management |
| mean() for missing values | Spline interpolation | Always better | Preserves time series dynamics |

**Deprecated/outdated:**
- `pandas.read_hdf()` for remote HDF5: Does not support S3; use h5py + s3fs instead
- `fastparquet` engine: PyArrow is now the default and more feature-complete
- Modal Volumes v1: v2 has no file count limits and better concurrent write support (Oct 2025)

## Open Questions

1. **Exact HDF5 attribute names for scale factors**
   - What we know: PERFORM data uses scale factors stored as attributes
   - What's unclear: Exact attribute key names may vary by file type (wind vs solar vs load)
   - Recommendation: Inspect actual HDF5 file attributes on first download; document in code comments

2. **ERCOT location for solar angle calculation**
   - What we know: ERCOT spans a large geographic area (~31N, -100W approximate centroid)
   - What's unclear: Whether to use system-level centroid or per-zone coordinates
   - Recommendation: Use system-level centroid for initial implementation; refine if solar features underperform

3. **Optimal long-gap handling strategy**
   - What we know: User decision allows Claude discretion for gaps >6 hours
   - What's unclear: Frequency and distribution of long gaps in actual data
   - Recommendation: First run: log gap statistics without handling; second run: implement strategy based on data exploration

## Sources

### Primary (HIGH confidence)
- [PERFORM-Forecasts/documentation GitHub](https://github.com/PERFORM-Forecasts/documentation) - HDF5 structure, S3 paths, Python examples
- [ARPA-E PERFORM AWS Registry](https://registry.opendata.aws/arpa-e-perform/) - Data access patterns
- [pandas interpolate() documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html) - Interpolation methods
- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) - Gap parameter documentation
- [pvlib solarposition](https://pvlib-python.readthedocs.io/en/stable/reference/solarposition.html) - Solar angle calculations
- [Modal Volumes documentation](https://modal.com/docs/guide/volumes) - Volume patterns, commit/reload
- [pandas to_parquet](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html) - Parquet I/O

### Secondary (MEDIUM confidence)
- [Feature-Engine CyclicalFeatures](https://feature-engine.trainindata.com/en/latest/user_guide/creation/CyclicalFeatures.html) - Cyclic encoding formula
- [scikit-learn lagged features example](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html) - Lag feature patterns
- [NREL PERFORM Phase I Technical Report](https://docs.nrel.gov/docs/fy23osti/79498.pdf) - Dataset structure details

### Tertiary (LOW confidence - needs validation)
- HDF5 scale_factor attribute names: Requires inspection of actual files
- Modal Volume v2 concurrent write limits: Documentation states "hundreds" but exact limits not specified

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries are well-documented, widely used, and verified against official docs
- Architecture patterns: HIGH - patterns derived from project context (MODAL.md, smoke_test.py) and official Modal docs
- Pitfalls: HIGH - pitfalls compiled from project PITFALLS.md research and verified against official documentation
- Code examples: HIGH - all examples verified against official library documentation

**Research date:** 2026-02-25
**Valid until:** 2026-03-25 (30 days - stable domain)
