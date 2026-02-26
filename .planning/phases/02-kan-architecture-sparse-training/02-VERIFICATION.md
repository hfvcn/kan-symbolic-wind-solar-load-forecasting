---
phase: 02-kan-architecture-sparse-training
verified: 2026-02-26T06:21:29Z
status: verified
score: "Modal run complete; pruned_ratio=0.93; rmse_pruned <= rmse_unpruned"
evidence:
  - run_id: 2026-02-26_035935_74ef1f78
    data_run_id: 2026-02-26_032058_1957fda1
    target: load
    pruned_ratio: 0.93
    eval_unpruned_rmse: 5603.75600184078
    eval_pruned_rmse: 5156.14713718735
    artifacts:
      - runs/2026-02-26_035935_74ef1f78/checkpoint/model.pt
      - runs/2026-02-26_035935_74ef1f78/artifacts/sparsity.json
      - runs/2026-02-26_035935_74ef1f78/artifacts/eval_unpruned.json
      - runs/2026-02-26_035935_74ef1f78/artifacts/eval_pruned.json
      - runs/2026-02-26_035935_74ef1f78/artifacts/predictions_test.parquet
local_verification:
  - tests/test_kan_sr_smoke.py
notes:
  - "This verification run used a shortened step schedule; see runs/<id>/payload.json cfg.warmup_steps/sparsify_steps."
---

# Phase 02 Verification

## What is verified locally

- `tests/test_kan_sr_smoke.py` trains a tiny KAN end-to-end on synthetic data (TDD sanity).

## Verified via Modal (real data)

- `runs/2026-02-26_035935_74ef1f78/` is a completed Phase-2 run on PERFORM-derived Parquet splits:
  - Checkpoint: `checkpoint/model.pt`
  - Sparsity: `artifacts/sparsity.json` (`pruned_ratio=0.93`)
  - Metrics: `artifacts/eval_unpruned.json` (RMSE=5603.76), `artifacts/eval_pruned.json` (RMSE=5156.15)
  - Test predictions: `artifacts/predictions_test.parquet`
