---
phase: 07-interpretability-validation
plan: 02
completed: 2026-02-26
status: code-complete
---

# Phase 07 Summary 02: Physics Mapping & Validation

## What shipped

- Implemented heuristic physics mapping + consistency scoring: `src/eval/physics_mapping.py`
- Added unit tests for wind cubic detection and monotonicity sanity: `tests/test_physics_mapping.py`
- Added report generator:
  - `scripts/physics_mapping.py` writes:
    - `doc/paper_assets/physics_mapping_<run>.json`
    - `doc/paper_assets/physics_mapping_<run>.md`
    - plus attaches `runs/<symbolic_run>/artifacts/physics_mapping.json|md` for downstream aggregation
- Integrated physical consistency score into comparison table:
  - `src/eval/runs.py` now reads `artifacts/physics_mapping.json` when present (kan_symbolic runs)

## Notes

- Mapping is heuristic evidence for thesis narrative, not a proof of causal physics.

