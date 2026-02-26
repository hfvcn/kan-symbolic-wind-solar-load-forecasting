---
phase: 07-interpretability-validation
plan: 01
completed: 2026-02-26
status: code-complete
---

# Phase 07 Summary 01: Sensitivity Analysis (Partial Derivatives)

## What shipped

- Added unit tests for derivative computation and summary stats: `tests/test_sensitivity.py`
- Improved sensitivity script to be thesis-ready:
  - Auto-selects correct input space (normalized vs original) via RMSE probe
  - Writes meta JSON + summary CSV + histogram/box/scatter plots
  - Output goes to `doc/paper_assets/` (safe to commit)
  - Script: `scripts/sensitivity_analysis.py`

## Notes

- Real PERFORM experiments are still required to interpret derivative magnitudes and signs meaningfully (Phase 7 verification).

