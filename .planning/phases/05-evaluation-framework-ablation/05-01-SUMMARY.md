---
phase: 05-evaluation-framework-ablation
plan: 01
completed: 2026-02-25
status: complete
---

# Phase 05 Plan 01 Summary: Evaluation Framework

- 新增 `src/eval/runs.py`：
  - `summarize_run()`：从 payload + artifacts 提取统一指标
  - `build_comparison_table()`：生成对比表并标注 pareto_optimal
  - `seasonal_breakdown()`：按 DJF/MAM/JJA/SON 统计指标
- 新增 `scripts/evaluate_runs.py`：
  - 输出 `doc/paper_assets/comparison_table.csv`
  - 输出 `doc/paper_assets/pareto_rmse_vs_complexity.png`
  - 对每个 run 若存在 `predictions_test.parquet`，输出 seasonal CSV
- 统一产物：为 Phase 2/3/4 的 Modal 作业补充写出 `artifacts/predictions_test.parquet`

