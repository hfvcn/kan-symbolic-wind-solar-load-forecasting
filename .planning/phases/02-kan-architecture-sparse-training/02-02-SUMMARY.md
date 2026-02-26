---
phase: 02-kan-architecture-sparse-training
plan: 02
completed: 2026-02-25
status: complete
---

# Phase 02 Plan 02 Summary: Sparsification + Pruning

- 在 `modal_jobs/kan_train.py` 中加入 composite regularization 参数与 sparsify 阶段
- 增加剪枝阈值候选搜索（node_th/edge_th），优先满足：
  - pruned_ratio ≥ 0.8
  - pruned 后 RMSE ≤ baseline * 1.1
- 输出：
  - `artifacts/eval_unpruned.json`
  - `artifacts/eval_pruned.json`
  - `artifacts/sparsity.json`
  - `artifacts/feature_importance.csv`
- 剪枝后增加 refine（LBFGS）阶段并持续 checkpoint

## Verification

- 合成数据 smoke test 可运行，保证 prune/sparsity 统计基础结构可用
- 真实数据的 80%+ 稀疏目标需在 Modal 上用实际数据与超参数进一步验证（后续阶段会通过实验迭代达标）

