# graduation-design
*注意：本课题要求在Github中开源代码。
在能源领域，准确预测风力和光伏发电的耦合负荷对于电网的稳定运行和智能调度至关重要。与区块链风险检测类似，负荷预测模型也需要高度的可解释性，以便电力工程师理解和信任预测结果。本课题将符号回归应用于风光耦合负荷预测，旨在发现影响负荷变化的潜在物理规律和关键因素（如风速、光照强度、温度、历史负荷等）之间的内在数学关系。通过生成可解释的数学模型，本研究不仅追求预测精度，更致力于揭示能源系统的运行机理，为可再生能源的高效消纳提供理论依据。

## Modal 运行产物同步到本地

本项目的训练/基线/评估通常在 Modal 上运行，运行产物先落到 Modal Volume（持久化存储），再同步到本地 `runs/` 目录（不提交到 Git）。

详细约定见：`.planning/MODAL.md`

## 数据管道（Phase 1）

数据管道会从 ARPA-E PERFORM 下载 ERCOT 风/光/负荷实际值，并完成：
- 缺失值处理（短缺失三次样条插值 + 质量报告）
- 气象代理特征（Open-Meteo 历史档案：温度 / GHI / 风速 / 气压；cache-first 保存到 `raw/open_meteo_hourly.parquet`）
- 周期性时间编码 + 太阳高度角/方位角
- 48 步滞后特征（t-1..t-48）
- 按时间顺序切分 + 48 步 gap 防泄漏 + Z-score（仅拟合 train）

```bash
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/data_pipeline.py --year 2018 --iso ERCOT
```

## 派生数据集（Phase 1.5，可选但强烈推荐）

5min 负荷预测里 `load_lag_1`（持久性/persistence）往往压倒性强，导致符号公式退化为“纯自回归”。为更贴合论文目标（让温度/GHI/风速等物理因子显式进入关系式），本项目提供派生数据集构建任务：

- 定义：`net_load = load - wind - solar`（耦合负荷/净负荷）
- 残差/变化量建模：`delta_load = load - load_lag_1`，`delta_net_load = net_load - net_load_lag_1`
- 工程物理代理特征（自动归一化并写入 scaler_params）：
  - `wind_speed_10m_m_s_cubed`、`ghi_day_w_m2`、`cdd_18c`、`hdd_18c`

```bash
# 从已有 Phase-1 data_run 派生出一个新 data_run（不重新下载原始数据）
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/derive_dataset.py \
  --source-data-run-id <data_run_id> \
  --add-physics-proxies \
  --net-load-lag-steps 1,12,48 \
  --degree-base-c 18
```

### Modal 功能自检（Smoke Test）

```bash
# 运行一次 CPU + Volume + 重试 + fanout 的自检
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/smoke_test.py

# 可选：如果你的账号有 GPU 权限，额外跑 GPU 探测
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/smoke_test.py --with-gpu
```

```bash
# 1) 查看远端 runs 列表
/Users/vfch/Documents/project/graduation-design/scripts/sync_from_modal.sh ls

# 2) 同步最新一次 run 到本地 /Users/vfch/Documents/project/graduation-design/runs/
/Users/vfch/Documents/project/graduation-design/scripts/sync_from_modal.sh latest

# 3) 同步指定 run（run_id 为远端目录名）
/Users/vfch/Documents/project/graduation-design/scripts/sync_from_modal.sh 2026-02-25_001
```

## 训练与符号提取（Phase 2-3）

```bash
# Phase 2: KAN 训练（输出 checkpoint/model.pt + predictions_test.parquet）
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id <data_run_id> --target load

# Phase 3: 符号提取（输出 formula.sympy.txt / formula.tex / predictions_test.parquet）
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id <kan_train_run_id>
```

若训练/符号提取的目标是 `delta_load` / `delta_net_load`，可在本地将 test 预测重建回绝对序列（便于论文图表对比）：

```bash
python3 /Users/vfch/Documents/project/graduation-design/scripts/reconstruct_predictions.py --run runs/<run_id>
```

同步到本地后（`runs/<id>`），可生成论文图表：

```bash
python3 /Users/vfch/Documents/project/graduation-design/scripts/make_thesis_figures.py --run runs/<id>
python3 /Users/vfch/Documents/project/graduation-design/scripts/sensitivity_analysis.py --symbolic-run runs/<sym_id>
python3 /Users/vfch/Documents/project/graduation-design/scripts/physics_mapping.py --symbolic-run runs/<sym_id>
```

## 基线实验（Phase 4）

```bash
# Torch 基线（MLP / LSTM）
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/baseline_torch.py --data-run-id <data_run_id> --model-type mlp --target load
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/baseline_torch.py --data-run-id <data_run_id> --model-type lstm --target load

# PySR 基线（可选：seed_from_symbolic_run 用于交叉验证）
modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/pysr_baseline.py --data-run-id <data_run_id> --target load
```

## 评估与论文资产（Phase 5-8）

```bash
# 对比表 + Pareto 简图 + seasonal breakdown + transfer gap（如包含 transfer run）
python3 /Users/vfch/Documents/project/graduation-design/scripts/evaluate_runs.py --run runs/<id1> --run runs/<id2> ...

# PySR 方程集 vs KAN symbolic 点（复杂度 vs RMSE）
python3 /Users/vfch/Documents/project/graduation-design/scripts/plot_pareto_frontier.py --pysr-run runs/<pysr_id> --kan-symbolic-run runs/<sym_id>

# 跨 ISO 迁移评估（本地生成 runs/transfer_*）
python3 /Users/vfch/Documents/project/graduation-design/scripts/transfer_eval.py --train-run runs/<kan_train_id> --target-data-run runs/<target_iso_data_id>

# 生成论文资产索引（ASSET_INDEX.md）
python3 /Users/vfch/Documents/project/graduation-design/scripts/build_asset_index.py
```

## 一键实验驱动（推荐）

为了方便频繁调参与重复跑实验，本仓库提供单文件集成脚本 `scripts/experiment_driver.py`：

1) 打开脚本顶部 `CONFIG` 区域，集中修改：
- 数据 run_id（或是否重跑 Phase 1）
- （可选）是否先跑 Phase 1.5 派生数据集（`RUN_DERIVED_DATASET`）
- KAN 训练 sweep（超参数 / 特征选择）
- KAN 符号提取 sweep（r2_threshold / lib / sample_rows 等）
- 是否跑 baselines / 是否自动生成论文图表与索引

2) 运行：

```bash
# 只打印将执行的命令（不真的跑 Modal）
python3 scripts/experiment_driver.py --dry-run

# 真正执行：Modal 训练/符号提取 -> 同步 runs/ -> 本地评估与绘图 -> 生成 ASSET_INDEX
python3 scripts/experiment_driver.py --execute
```
