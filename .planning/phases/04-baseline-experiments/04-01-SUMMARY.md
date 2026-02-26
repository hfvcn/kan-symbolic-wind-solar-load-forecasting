---
phase: 04-baseline-experiments
plan: 01
completed: 2026-02-25
status: complete
---

# Phase 04 Plan 01 Summary: PySR Baseline

- 新增 `modal_jobs/pysr_baseline.py`（Julia 隔离作业）：
  - 输出 `artifacts/equations.csv`（PySR 的方程表/帕累托候选）
  - 输出 `artifacts/best_equation.txt`
  - 输出 `artifacts/eval_test.json`（RMSE/MAE/R²）

## Notes

- PySR 在 Modal 上运行时可能需要首次下载 Julia 运行时/依赖；属于一次性成本。

