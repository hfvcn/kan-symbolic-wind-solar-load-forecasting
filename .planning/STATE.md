# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24)

**Core value:** From data, extract human-understandable physical formulas -- not just accurate predictions, but transparent logic that grid engineers can read, verify, and trust.
**Current focus:** Post-v1 optimization — (1) keep all knobs in `scripts/experiment_driver.py`, (2) mitigate 5min persistence dominance via delta/residual and net-load targets, (3) improve symbolic formula quality so key physical factors (temp/GHI/wind) appear and pass physics checks.

## Current Position

Phase: Post-v1 optimization
Plan: Extend the pipeline with a derived-dataset stage (delta/net-load + engineered features), add persistence/skill evaluation, and regenerate thesis assets as optimization runs accumulate.
Status: v1 roadmap remains verified; additional optimization runs are being added and indexed.
Last activity: 2026-02-27 -- Added `modal_jobs/derive_dataset.py` (net_load/delta targets + engineered proxy features), added delta-run reconstruction + persistence/skill metrics in evaluation, extended physics mapping for net-load, and integrated these into `scripts/experiment_driver.py`.

Progress:
- Implementation: [██████████] 18/18 plans code complete
- Verification: 8 phases verified (see per-phase VERIFICATION.md)

Verified runs (synced locally):
- Phase 1 (data): `2026-02-26_032058_1957fda1` (ERCOT), `2026-02-26_052312_f85bed5b` (MISO)
- Phase 2 (KAN train): `2026-02-26_035935_74ef1f78`
- Phase 3 (KAN symbolic): `2026-02-26_041718_5579aeeb`
- Optimization (KAN symbolic sweep from `2026-02-26_055200_958b3949`): `2026-02-26_090620_1fc7d27a`, `2026-02-26_091400_ba9fd48c`
- Phase 4 (baselines): `2026-02-26_043102_777fac2d` (MLP), `2026-02-26_043230_b2b5c68f` (LSTM), `2026-02-26_045336_77244377` (PySR)
- Phase 7 (seeded PySR): `2026-02-26_064508_3e631069`
- Phase 6 (solar hard constraint): `2026-02-26_064925_a74e5d63`
- Phase 5 (ablations): `2026-02-26_053425_2e4bc623`, `2026-02-26_054408_f605ac11`, `2026-02-26_055200_958b3949`, `2026-02-26_060024_d6250f56`
- Phase 8 (transfer): `transfer_2026-02-26_052920`

## Performance Metrics

This repo does not track execution time automatically. Use `.planning/ROADMAP.md` plan checkboxes and per-phase `*-VERIFICATION.md` for status.

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Roadmap: 8 phases derived from 19 requirements at comprehensive depth
- Roadmap: Phase 4 (baselines) can run in parallel with Phases 2-3 since it only needs the data pipeline
- Plan 01-01: Used pathlib.Path for run directory helpers (cross-platform compatibility)
- Plan 01-01: Apply HDF5 scale_factor attribute when present (PERFORM convention)
- Plan 01-02: Spline order=3 for cubic interpolation (smoothest interpolation)
- Plan 01-02: Day-of-year for month encoding (smoother transitions within months)
- Plan 01-02: Outliers marked with 3-sigma threshold but NOT modified (preserves raw signal)
- Plan 01-03: Z-score normalization excludes target column (load) to preserve prediction scale
- Plan 01-03: 48-step gap between splits matches LAG_WINDOW to prevent lag feature leakage
- Phase 01 audit: Add meteorology proxy features (Open-Meteo, cache-first) and update data submodule exports; Phase 1 verification now 5/5
- Phase 02: Chunked `KAN.fit()` training to guarantee periodic checkpoints + Volume commits; default feature set uses compact lag subset (1,12,48) for interpretability; prune candidate search targets 80% sparsity with <=10% RMSE degradation
- Phase 03: Symbolic extraction uses per-edge `suggest_symbolic()` + SymPy `symbolic_formula()` with input/output de-normalization for thesis-ready equations
- Phase 04: Baselines run as isolated Modal jobs; Torch baselines optionally match KAN parameter count via checkpoint state_dict estimate
- Phase 05: Local evaluation reads synced run artifacts and generates thesis-ready tables/plots under doc/paper_assets
- Phase 06: Physics-informed hooks added (MultKAN, separability detection, and nighttime PV hard constraint at inference/export)
- Phase 07: Added sensitivity analysis + physics mapping reports + PySR cross-validation via KAN seed features
- Phase 03/07: Symbolic formulas produced with input/output normalizers expect ORIGINAL-scale inputs; evaluation/derivatives must inverse-transform feature columns
- Phase 08: Added cross-ISO transfer evaluation tooling + forward scaler transform + publication-quality visualization suite + ASSET_INDEX generator

### Pending Todos

None yet.

### Blockers/Concerns

- Research flag: Phase 2 sparsification hyperparameters have no direct pykan precedent on noisy energy data
- Research flag: Phase 3 symbolic extraction on real-world noisy time series is genuinely novel territory
- Research flag: Phase 6 PIKAN constraint formulation for zone-level data needs real runs to quantify impact (ablation)
- Remaining execution: none (consolidation only)

## Session Continuity

Last session: 2026-02-26
Stopped at: Consolidation (evaluation refresh + asset index + final test suite)
Resume file: .planning/ROADMAP.md
