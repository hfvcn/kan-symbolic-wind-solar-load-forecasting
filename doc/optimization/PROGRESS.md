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

