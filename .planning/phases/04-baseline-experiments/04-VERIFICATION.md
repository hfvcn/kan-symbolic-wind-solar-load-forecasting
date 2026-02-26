---
phase: 04-baseline-experiments
verified: 2026-02-26T06:21:29Z
status: verified
score: "Modal baselines complete (MLP/LSTM/PySR) on the same Phase-1 dataset"
evidence:
  - run_id: 2026-02-26_043102_777fac2d
    kind: mlp
    data_run_id: 2026-02-26_032058_1957fda1
    target: load
    eval_test_rmse: 175.67892435624188
    artifacts:
      - runs/2026-02-26_043102_777fac2d/artifacts/eval_test.json
      - runs/2026-02-26_043102_777fac2d/artifacts/predictions_test.parquet
  - run_id: 2026-02-26_043230_b2b5c68f
    kind: lstm
    data_run_id: 2026-02-26_032058_1957fda1
    target: load
    eval_test_rmse: 5107.989657653282
    artifacts:
      - runs/2026-02-26_043230_b2b5c68f/artifacts/eval_test.json
      - runs/2026-02-26_043230_b2b5c68f/artifacts/predictions_test.parquet
  - run_id: 2026-02-26_045336_77244377
    kind: pysr
    data_run_id: 2026-02-26_032058_1957fda1
    target: load
    eval_test_rmse: 127.59631641493024
    artifacts:
      - runs/2026-02-26_045336_77244377/artifacts/equations.csv
      - runs/2026-02-26_045336_77244377/artifacts/best_equation.txt
      - runs/2026-02-26_045336_77244377/artifacts/eval_test.json
      - runs/2026-02-26_045336_77244377/artifacts/predictions_test.parquet
---

# Phase 04 Verification

本阶段已在 Modal 上完成真实基线实验并同步到本地 `runs/`：

- Torch baselines:
  - `runs/2026-02-26_043102_777fac2d/` (MLP)
  - `runs/2026-02-26_043230_b2b5c68f/` (LSTM)
- PySR baseline:
  - `runs/2026-02-26_045336_77244377/`
