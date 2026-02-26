---
phase: 07-interpretability-validation
plan: 03
completed: 2026-02-26
status: code-complete
---

# Phase 07 Summary 03: PySR Cross-Validation (KAN Seeds)

## What shipped

- Seed feature extraction + evaluation utilities: `src/eval/seed_features.py`
- Unit tests: `tests/test_seed_features.py`
- Extended PySR baseline job for seeded cross-validation:
  - `modal_jobs/pysr_baseline.py` supports `seed_from_symbolic_run` and appends seed features as extra variables
  - Optionally inverts z-score to fit PySR in original units (`use_original_features=True` by default)
  - Writes `runs/<pysr_run>/artifacts/seed_features.json` when seeds are used
- Local comparison report generator: `scripts/compare_kan_pysr.py`

## Notes

- This approach is robust and reproducible without relying on internal PySR “initial population” hooks.

