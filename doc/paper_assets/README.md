# Paper Assets (Generated)

本目录用于存放**可直接用于论文写作**的表格与图像（由脚本生成）。

## 已验证的关键 run_id（2026-02-26）

- Phase 1 (data)
  - ERCOT: `2026-02-26_032058_1957fda1`
  - MISO: `2026-02-26_052312_f85bed5b`
- Phase 2 (KAN train)
  - Load (used by symbolic + transfer): `2026-02-26_035935_74ef1f78`
  - Load (best preliminary, ablation no_l1): `2026-02-26_055200_958b3949`
  - MultKAN (hidden_mult=2): `2026-02-26_070523_c05a4c19`
  - Solar (night hard-constraint verified): `2026-02-26_064925_a74e5d63`
- Phase 3 (KAN symbolic)
  - Original (weak): `2026-02-26_041718_5579aeeb`
  - Improved sweep (from `2026-02-26_055200_958b3949`): `2026-02-26_090620_1fc7d27a` (better), `2026-02-26_091400_ba9fd48c`
- Phase 4 (baselines)
  - MLP: `2026-02-26_043102_777fac2d`
  - LSTM: `2026-02-26_043230_b2b5c68f`
  - PySR: `2026-02-26_045336_77244377`
  - PySR (seeded cross-validation): `2026-02-26_064508_3e631069`
- Phase 5 (ablations)
  - full: `2026-02-26_053425_2e4bc623`
  - no_entropy: `2026-02-26_054408_f605ac11`
  - no_l1: `2026-02-26_055200_958b3949`
  - no_magnitude: `2026-02-26_060024_d6250f56`
- Phase 8 (transfer eval): `transfer_2026-02-26_052920`

建议工作流：

1. 在 Modal 上跑完实验（KAN 训练 / 符号提取 / PySR / baselines）
   - 可选：先跑 Phase 1.5 派生数据集（`net_load` / `delta_load` / `delta_net_load` + 物理代理特征）：
     - `modal run modal_jobs/derive_dataset.py --source-data-run-id <data_run_id> --add-physics-proxies`
2. 使用 `scripts/sync_from_modal.sh latest` 或指定 `run_id` 同步到本地 `runs/`
3. 若目标为 `delta_*`，先重建为绝对序列（用于论文图表与对比表口径）：
   - `python3 scripts/reconstruct_predictions.py --run runs/<id>`
4. 运行评估与绘图脚本，将产物输出到本目录：
   - `python3 scripts/evaluate_runs.py --run runs/<id1> --run runs/<id2> ...`
   - `python3 scripts/plot_pareto_frontier.py --pysr-run runs/<pysr_id> --kan-symbolic-run runs/<sym_id>`
   - `python3 scripts/make_thesis_figures.py --run runs/<id>`
   - `python3 scripts/sensitivity_analysis.py --symbolic-run runs/<sym_id>`
   - `python3 scripts/physics_mapping.py --symbolic-run runs/<sym_id>`
   - `python3 scripts/transfer_eval.py --train-run runs/<kan_train_id> --target-data-run runs/<target_iso_data_id>`
   - `python3 scripts/build_asset_index.py`

更省事的方式：直接用单文件驱动脚本 `scripts/experiment_driver.py`（集中调参 + 触发 Modal + 同步 + 本地评估/绘图 + 资产索引）。

## 一键重生成（本地）

在 `runs/` 已包含上述 run_id 的前提下：

```bash
# 评估表 + Pareto + seasonal + transfer gap
python3 scripts/evaluate_runs.py \
  --run runs/2026-02-26_035935_74ef1f78 \
  --run runs/2026-02-26_041718_5579aeeb \
  --run runs/2026-02-26_043102_777fac2d \
  --run runs/2026-02-26_043230_b2b5c68f \
  --run runs/2026-02-26_045336_77244377 \
  --run runs/2026-02-26_064508_3e631069 \
  --run runs/transfer_2026-02-26_052920 \
  --run runs/2026-02-26_053425_2e4bc623 \
  --run runs/2026-02-26_054408_f605ac11 \
  --run runs/2026-02-26_055200_958b3949 \
  --run runs/2026-02-26_060024_d6250f56

# 消融报告
python3 scripts/ablation_report.py \
  --kan-run runs/2026-02-26_053425_2e4bc623 \
  --kan-run runs/2026-02-26_054408_f605ac11 \
  --kan-run runs/2026-02-26_055200_958b3949 \
  --kan-run runs/2026-02-26_060024_d6250f56

# 解释性报告（symbolic）
python3 scripts/sensitivity_analysis.py --symbolic-run runs/2026-02-26_041718_5579aeeb
python3 scripts/physics_mapping.py --symbolic-run runs/2026-02-26_041718_5579aeeb
python3 scripts/compare_kan_pysr.py --pysr-run runs/2026-02-26_064508_3e631069 --symbolic-run runs/2026-02-26_041718_5579aeeb

# 图表（按需）
python3 scripts/make_thesis_figures.py --run runs/2026-02-26_035935_74ef1f78
python3 scripts/make_thesis_figures.py --run runs/2026-02-26_041718_5579aeeb
python3 scripts/make_thesis_figures.py --run runs/2026-02-26_045336_77244377
python3 scripts/make_thesis_figures.py --run runs/2026-02-26_064508_3e631069
python3 scripts/make_thesis_figures.py --run runs/transfer_2026-02-26_052920

# 资产索引
python3 scripts/build_asset_index.py
```

注意：
- `runs/` 目录默认不提交到 Git；`doc/paper_assets/` 可提交（取决于你的开源要求与学校规范）。
