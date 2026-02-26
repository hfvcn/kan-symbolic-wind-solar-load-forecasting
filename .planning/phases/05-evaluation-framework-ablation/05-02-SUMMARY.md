---
phase: 05-evaluation-framework-ablation
plan: 02
completed: 2026-02-25
status: complete
---

# Phase 05 Plan 02 Summary: Ablation Hooks + Pareto Frontier

- `modal_jobs/kan_train.py` CLI 增加 lamb 相关覆盖参数，支持消融矩阵运行
- `modal_jobs/pysr_baseline.py` 为 equations.csv 增加 test_rmse/test_mae/test_r2（可直接画 Pareto）
- 新增 `scripts/plot_pareto_frontier.py`：在同一平面绘制 PySR 方程集与 KAN-SR symbolic 点

