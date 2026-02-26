---
phase: 06-physics-informed-enhancements
plan: 02
completed: 2026-02-25
status: complete
---

# Phase 06 Plan 02 Summary: Nighttime PV=0

- 在以下作业的 `predictions_test.parquet` 导出逻辑中加入 nighttime PV 硬约束（target=solar）：
  - `modal_jobs/kan_train.py`
  - `modal_jobs/kan_symbolic.py`
  - `modal_jobs/baseline_torch.py`
  - `modal_jobs/pysr_baseline.py`

