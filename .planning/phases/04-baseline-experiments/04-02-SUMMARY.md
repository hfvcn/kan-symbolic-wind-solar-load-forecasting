---
phase: 04-baseline-experiments
plan: 02
completed: 2026-02-25
status: complete
---

# Phase 04 Plan 02 Summary: Torch Baselines (MLP/LSTM)

- 新增 `modal_jobs/baseline_torch.py`：
  - `--model-type mlp|lstm`
  - 输出 `payload.json / metrics.csv / checkpoint/model.pt / artifacts/eval_test.json`
  - 可选 `--match-kan-run-id`：从 KAN checkpoint 估算参数量并匹配 baseline hidden size
- 新增 `src/baselines/torch_models.py`（MLPRegressor / LSTMRegressor）
- 新增 `src/baselines/torch_training.py`（MLP trainer + LSTM 序列构建）

