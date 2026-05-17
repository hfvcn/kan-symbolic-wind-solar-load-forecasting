# Optimization Progress (Post-v1)

This folder tracks **post-v1** improvements beyond the verified roadmap in `.planning/ROADMAP.md`.

## 2026-02-26

### What changed

- Added a single-file experiment orchestrator: `scripts/experiment_driver.py`
  - Centralizes hyperparameters, Modal calls, syncing, and local evaluation/plots.
  - Writes per-run session artifacts under `doc/optimization/<session_id>/`.
- Exposed tuning knobs for:
  - KAN training: `modal_jobs/kan_train.py` (feature selection + lag controls + max_train_rows + `--data-run-id` style CLI)
  - Symbolic extraction: `modal_jobs/kan_symbolic.py` (`--train-run-id`, `--sample-rows`, `--lib`)
- Evaluation consistency fix:
  - `src/eval/runs.py` now prefers **TEST** metrics from `artifacts/predictions_test.parquet` for Phase 2 KAN runs (falls back to `eval_pruned.json` only if predictions are absent).
- Unit tests updated/added (all pass via `python3 -m unittest discover -s tests -p 'test_*.py'`).

### New optimization runs

Symbolic sweep on the best preliminary KAN train run `2026-02-26_055200_958b3949`:

- `2026-02-26_090620_1fc7d27a` (default lib, `r2_threshold=0.95`, `sample_rows=20000`)
  - `rmse=1861.0`, `r2=0.838` (test)
- `2026-02-26_091400_ba9fd48c` (no exp/gaussian, `r2_threshold=0.90`, `sample_rows=20000`)
  - `rmse=2608.9`, `r2=0.682` (test)

Local assets regenerated into `doc/paper_assets/` (figures + physics mapping + sensitivity + ASSET_INDEX).

### Remaining gap (paper narrative)

- The improved symbolic formulas are **still dominated by autoregressive load lags** (e.g., `load_lag_1`, `load_lag_12`), so `physics_mapping` still scores `0.0` for load-temperature sensitivity.

### Next optimization ideas (planned)

- Train KAN with **restricted lag features** to encourage physical factors:
  - Exclude `load` from `lag_series` (keep `wind,solar` only), or use only `load_lag_48` (daily/periodic) instead of `load_lag_1`.
  - Reduce feature set to `meteorology,solar,cyclic` for symbolic runs.
- Run symbolic sweeps on those trained models and compare:
  - `formula_eval_test.json` metrics
  - `physics_mapping.json` score and derivative sign statistics

## 2026-02-27

### What changed (advice-driven, paper-aligned)

- Added a derived dataset job: `modal_jobs/derive_dataset.py`
  - Builds a new Phase-1.5 data run from an existing Phase-1 run (no re-download).
  - Adds new **targets**: `net_load`, `delta_load`, `delta_net_load`.
  - Adds **engineered proxy features** (normalized + appended to `scaler_params.json`):
    - `wind_speed_10m_m_s_cubed` (wind power proxy)
    - `ghi_day_w_m2` (daylight-gated irradiance)
    - `cdd_18c`, `hdd_18c` (cooling/heating degree proxies)
  - Adds normalized `net_load_lag_{k}` features (default k in {1,12,48}) to enable net-load persistence/residual modeling.
- Added local post-processing for delta targets:
  - `scripts/reconstruct_predictions.py` writes `predictions_test_reconstructed.parquet` and `eval_test_reconstructed.json` for `delta_*` runs (so tables/plots reflect reconstructed absolute series).
  - `scripts/make_thesis_figures.py` now prefers reconstructed predictions and `formula_reconstructed.tex` when present.
- Evaluation improvements:
  - `src/eval/runs.py` now computes **persistence baseline RMSE** and **skill_score** (`1 - RMSE_model/RMSE_persist`) from prediction artifacts.
  - `scripts/evaluate_runs.py` uses reconstructed predictions for seasonal breakdown when available.
- Physics mapping upgrades:
  - `src/eval/physics_mapping.py` now supports `net_load` and `delta_*` targets (checks GHI/wind monotone decreasing for net load).
- Experiment integration:
  - `scripts/experiment_driver.py` can optionally run Phase-1.5 derived dataset creation and automatically runs reconstruction before local evaluation/plots.

### Tests

- Added `tests/test_derived_features.py`.
- Updated `tests/test_physics_mapping.py` (net-load checks).
- Updated `tests/test_run_summarizer_inference.py` (reconstructed predictions preference + skill_score).
