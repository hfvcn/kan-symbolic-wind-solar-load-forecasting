# 项目架构/逻辑/现状说明（V3，全仓审查版，交接给“看不到代码”的分析 AI）

> 目的：让一个**无法访问本项目代码与文件系统**的 AI，仅凭本文就能理解：
> 1) 项目做了什么、如何工作（数据流/训练流/评估流/资产输出）  
> 2) 截止当前（2026-03-05）的**实验事实**与关键瓶颈（尤其 multi-horizon 的 wind/solar 现象）  
> 3) 本次对代码与文档的**审查结果**（可复现性、口径一致性、风险点、已具备的工具链）  

更新时间：2026-03-05  
仓库路径（本地定位）：`/Users/vfch/Documents/project/graduation-design`  
审查基准：Git HEAD `aa1ddfd`（并结合本地已同步的 `runs/` 与 `doc/paper_assets/` 产物）

---

## 1. 一句话概括（对论文目标对齐）

本项目用 **KAN（稀疏化/剪枝）→ 符号提取（Symbolic）→ 物理映射/敏感性分析 → 论文资产（图表/表格）** 的闭环流程，在 PERFORM 的 5min 时序数据上做 **多步预测（multi-horizon）**，并把“物理变量能否进入稀疏结构/解析公式”作为核心证据链（不仅追求最低 RMSE）。

---

## 2. 论文要求（工程化后的验收口径）

原始要求（来自 README 的课题描述）：在风光耦合负荷预测中，通过符号回归发现风速/光照/温度/历史负荷等因素的内在数学关系，兼顾精度与可解释性。

工程验收口径（建议用于论文“方法/实验”章节的统一语义）：

1) **预测有效**：在不泄漏、不作弊的设置下，至少在关键 horizon 上显著优于 persistence baseline（报告 RMSE/WAPE + skill）。  
2) **可解释可复算**：输出可读公式（LaTeX/SymPy），并能在 test 上复算指标（`formula_eval_test.json` / `predictions_test.parquet`）。  
3) **关键因子显式出现**：最终公式（或结构化分解后的子公式）中应显式包含并可解释地依赖：  
   - 历史项（lag）  
   - 温度 / 辐照（GHI）/ 风速（或物理代理，如 `v^3`、hub-height）  
   - 风光耦合相关的结构（例如净负荷 `net_load = load - wind - solar` 的分解叙事）

> 研究难点（项目主矛盾）：在 5min 高频预测中，滞后项（尤其 `*_lag_1`）通常极强，容易把外生气象因子“挤出”稀疏结构与最终解析公式。

---

## 3. 代码组织（模块职责与入口）

### 3.1 顶层目录（你需要知道的最少集合）

- `modal_jobs/`：云端 Modal 任务入口（Phase 1/1.5/2/3/4）。  
  - `data_pipeline.py`：Phase 1 数据管道  
  - `derive_dataset.py`：Phase 1.5 派生数据集（delta/net_load/multi-horizon/物理代理特征）  
  - `kan_train.py`：Phase 2 KAN 训练（warmup→sparsify→refine→prune）  
  - `kan_symbolic.py`：Phase 3 符号提取（per-edge 拟合→拼接公式→评估）  
  - `baseline_torch.py` / `pysr_baseline.py`：Phase 4 基线

- `src/`：可复用的核心库（Modal 与本地脚本共同依赖）。  
  - `src/data/`：下载、清洗、特征工程、切分、归一化、派生目标  
  - `src/local/`：本地等价流程（可不经 Modal 直接在本机生成 run；注意与 Modal 的配置字段存在轻微漂移，见“审查结果”）  
  - `src/kan_sr/`：KAN 稀疏度/剪枝、符号提取、指标、可分性、敏感性  
  - `src/eval/`：run 汇总口径（含 persistence/skill）、物理映射符号统一  
  - `src/thesis_sweep/`：论文导向 sweep 计划器（S0–S4），驱动批量实验并写 manifest

- `scripts/`：本地工具与论文资产生成。  
  - 同步：`sync_from_modal.sh`  
  - 重建：`reconstruct_predictions.py`（delta→abs）  
  - 评估：`evaluate_runs.py`（comparison 表、seasonal、pareto 等）  
  - 绘图：`make_thesis_figures.py`、`plot_pareto_frontier.py`  
  - 诊断：`diagnose_solar_bounds.py`、`summarize_solar_ablation.py`  
  - 一键驱动：`experiment_driver.py`、`thesis_sweep_driver.py`

- `doc/`：论文资产与阶段性结论沉淀（`doc/paper_assets/`、`doc/thesis_sweeps/` 等）。  
- `tests/`：单元测试（使用 `unittest`，可通过 `python3 -m unittest discover ...` 运行）。

---

## 4. 运行位置与存储契约（最关键的可复现约定）

### 4.1 Modal vs 本地

- **Modal（推荐）**：跑训练/符号提取/基线；产物写入 Modal Volume。  
- **本地**：将远端 run 同步到本地 `runs/`，再做评估、重建、绘图、生成论文资产。

### 4.2 Run 目录结构（契约）

远端：`/vol/runs/<run_id>/...`  
本地：`runs/<run_id>/...`（默认不提交 Git）

每个 run 目录的关键文件（按 phase 可能不同）：

- `payload.json`：run 元信息（phase/kind/超参/数据 run_id/特征列等）  
- `processed/`：Phase 1/1.5 输出的 `{train,val,test}_<timestamp>.parquet`  
- `checkpoint/model.pt`：Phase 2 训练的模型权重（用于 Phase 3 符号提取）  
- `artifacts/`（常见）：  
  - `predictions_test.parquet`：test 集预测（通常是 delta 口径）  
  - `predictions_test_reconstructed.parquet`：若目标是 `delta_*`，在本地重建回绝对序列后的预测（论文图表/公平对比强烈推荐用它）  
  - `eval_{unpruned,sparsify,pruned}.json`、`sparsity.json`、`feature_importance*.csv`  
  - Phase 3：`formula.sympy.txt` / `formula.tex` / `formula_metrics.json` / `formula_eval_test.json`

> **口径提醒（很重要）**：  
> `src/eval/runs.py` 的汇总会优先读取 `predictions_test_reconstructed.parquet`（若存在），否则退回 `predictions_test.parquet`。因此要保证“abs(test) 与 persistence 的可比性”，delta 目标请先做重建。

---

## 5. 端到端数据流（从原始数据到论文资产）

### 5.1 Phase 1：数据管道（`modal_jobs/data_pipeline.py`）

输入：PERFORM（ARPA-E）S3 的 ERCOT/MISO 风/光/负荷实际值 HDF5  
处理：缺失插值 + 质量报告 + Open-Meteo 历史档案代理气象 + 周期编码 + 太阳几何 + lag 特征 + 时间切分（含 gap 防泄漏）+ Z-score（仅拟合 train）  
输出：`runs/<data_run_id>/processed/{train,val,test}_<ts>.parquet` + `runs/<data_run_id>/artifacts/scaler_params.json`

### 5.2 Phase 1.5：派生数据集（`modal_jobs/derive_dataset.py`）

目的：缓解 5min 任务“persistence 主导 → 物理量进不去结构/公式”的结构性问题。  
核心派生：

- `net_load = load - wind - solar`  
- 多步差分目标：`delta_{wind,solar,load,net_load}_h{n}`（例如 `delta_solar_h288`）  
- 确保重建所需 lag：`net_load_lag_{n}` 等  
- 物理代理特征（会扩展 scaler_params）：`wind_speed_10m_m_s_cubed`、`ghi_day_w_m2`、`cdd_18c`、`hdd_18c`、`wind_speed_hub_est`、`ghi_temp_corr_w_m2`

### 5.3 Phase 2：KAN 训练（`modal_jobs/kan_train.py`）

流程：`warmup → sparsify → refine → prune_search → prune`  
关键产物：`checkpoint/model.pt`、`feature_importance.csv`（每个输入特征的 `active_edges`）、`eval_pruned.json`、`predictions_test.parquet`

> 可控点：`include_groups`（特征组）与 `lag_series/lag_steps`（代理强度），以及 `sparsify_*` 正则与 `target_pruned_ratio`。  
> Modal 版本支持 `prune_require_features`（按通配符强制某些特征在 prune 后仍保留 active edge）。

### 5.4 Phase 3：符号提取（`modal_jobs/kan_symbolic.py`）

方法：对每条 KAN edge 拟合符号库函数（lib 可控），满足阈值后固定，再拼接为整体 SymPy 表达式并评估。  
关键产物：`formula.sympy.txt` / `formula.tex` / `formula_eval_test.json` / `edge_symbolic_report.csv`  
数值稳定性工具：`safe_exp_clip`、`eval_clip_quantiles`（用于避免 exp 等算子导致的溢出）。

### 5.5 Phase 4：基线（`modal_jobs/baseline_torch.py` / `modal_jobs/pysr_baseline.py`）

目的：证明“不是只有 KAN 才能做得好”，并为论文提供公平对照。  
Torch baseline 支持对齐：同步 KAN 特征列 + 同步训练预算（optimizer updates）+ 参数量对齐。

### 5.6 Phase 5+：本地评估与论文资产（`scripts/*.py`）

- delta→abs 重建：`scripts/reconstruct_predictions.py`  
- 统一对比表/季节分解/Pareto：`scripts/evaluate_runs.py`  
- 图表：`scripts/make_thesis_figures.py`  
- 资产索引：`scripts/build_asset_index.py` 生成 `doc/paper_assets/ASSET_INDEX.md`

---

## 6. 截止 2026-03-05 的“实验事实”（从产物反推，非推测）

### 6.1 全流程闭环（T4 fullflow 已跑通）

在 `doc/paper_assets/fullflow_t4_kan151000_20260301_230545/comparison_table.csv` 中可复现：

- KAN（`2026-03-01_151000_kan_nobase_nogrid_gpu`，`delta_net_load_h6`）：RMSE=1413.51，persistence RMSE=2585.66，skill=0.453  
- baseline MLP（`2026-03-01_155600_baseline_mlp_match_kan151000`）：RMSE=1474.38，skill=0.430（预算/特征对齐）  
- strict 符号公式（`2026-03-01_160200_sym_strict_r2_0_995__kan151000`）：RMSE=2388.46，skill=0.076  

结论（事实层）：**符号提取链路已可用且可复算，但公式精度显著弱于 teacher（KAN）**。

### 6.2 Solar multi-horizon：GHI “有信息但会被剪枝轨迹影响”（已用 ablation 坐实）

汇总表：`doc/solar_ablation_summary_20260304.csv`（abs(test) + persistence + ghi_edges）  
核心现象：

- `h=72`：`both` 最好且 `ghi_edges` 最高（GHI 在稀疏结构中稳定保留，性能显著提升）。  
- `h=576`：`meteo-only` 最好且 `ghi_edges>0`（长尺度更偏气象驱动）。  
- `h=144`：`both` 失败且 `ghi_edges=0`（典型“竞争 + 稀疏/剪枝选择轨迹敏感”反例）。  

> 论文可用表述：外生量的“入式/退式”更像**稀疏约束下的结构选择**，而非“外生量无意义”。

### 6.3 Solar 长 horizon 反例：`delta_solar_h288` 的 test 外推崩坏（已诊断）

诊断输出：对 run `2026-03-04_101610_37271ac2` 运行 `scripts/diagnose_solar_bounds.py` 可复现：

- `delta_pred` 出现系统性负偏（p50≈-17205，mean≈-31775）且方差爆炸（std≈34548 vs true std≈5343）。  
- 重建到绝对值后 `abs_pred<0` 比例≈67.45%（违反 solar 非负物理边界）。  
- abs(test) RMSE=45568.69，persistence RMSE=5281.47，skill=-7.628。  
- 最小“物理裁剪”对照（`clip(y_pred, 0, train_max)`）可将 RMSE 降到 10678.50、R²≈0.036，但 skill 仍为负（风险缓解≠性能超越）。

结论（事实层）：**长 horizon + 差分目标会放大无界外推风险**；需要在建模/符号库/约束层面对“越界”给出论文可解释的处理（否则反例会很刺眼）。

### 6.4 结构化分解（S3）能力已具备并产出可评估 run

示例：`2026-03-01_105353_fullflow_t4_1e551b__s3_combo_net_load_h6`（Phase=`05-structured-combination`）  
该 run 的 `payload.json` 中记录 `eval_test.rmse=1520.18`（目标 `net_load_h6`）。  

结论（事实层）：**“先预测 load/wind/solar 再组合 net_load” 的工程管线已打通**，可作为论文里“保证物理因子显式出现”的可交付路线之一（子公式是否足够准仍需进一步实验支撑）。

---

## 7. 全仓审查结果（代码/流程/可复现性）

### 7.1 通过项（当前做得好的）

1) **存储契约清晰**：run 目录结构稳定，`payload.json` 能反推配置与数据来源。  
2) **评估口径已补齐 multi-horizon**：persistence baseline 会按 `_h{n}` 自动 shift(n)，skill 可比。  
3) **论文资产链路成熟**：`doc/paper_assets/` + `ASSET_INDEX.md` 能把“run→图表/表格”串起来。  
4) **诊断工具到位**：solar bounds 诊断、ablation 汇总让“机制叙事”从推断变成证据。  
5) **测试可运行**：`python3 -m unittest discover -s tests -p 'test_*.py'`（本次审查环境下 41 tests / 14s 通过）。

### 7.2 风险点/不一致（需要在论文落地前显式处理）

1) **Modal vs 本地（`src/local/*`）配置/Schema 存在轻微漂移**  
   - 例如 Modal 训练支持 `prune_require_features`、`warmup_update_grid` 等字段，而本地 `TrainConfig` 未包含；不同来源的 run `payload.json` 字段不完全一致。  
   - 风险：做“批量汇总/筛选”时容易被字段缺失误导；论文复现实验建议优先使用 Modal 产物，或在落地阶段统一 schema。

2) **delta vs abs 口径需要强制一致**  
   - 若缺少 `predictions_test_reconstructed.parquet`，汇总可能落回 delta(test) 指标，导致与 abs(test) 混用。  
   - 建议：把“重建→评估→出图”作为固定 checklist（见 `doc/todo.md` 的落地计划）。

3) **长 horizon 的物理越界是“可被审稿人抓住的反例”**  
   - 已有明确证据（6.3）。论文中应把它定位为“失效模式与风险边界”，并给出最小缓解策略与后续改进方向（算子安全化/物理约束/有界投影等）。

4) **日志噪声（非致命）**  
   - 本地跑测试与绘图时出现 matplotlib/pyparsing deprecation warning、SymPy 的 tensor→float warning（不影响结果，但会污染日志）。  

---

## 8. 与 v1/v2 的关系（你现在应该读哪份）

- v1（`doc/PROJECT_ARCHITECTURE_STATUS_FOR_AI.md`）：更偏“全系统交接 + Phase 1.5/全流程闭环”与架构细节。  
- v2（`doc/PROJECT_ARCHITECTURE_STATUS_FOR_AI_v2.md`）：更偏“wind/solar multi-horizon 机制叙事与写作计划”。  
- v3（本文件）：在**全仓审查**基础上，把“架构事实 + 关键实验事实 + 审查发现”统一到一份可直接用于论文落地的状态快照；具体后续任务拆解见 `doc/todo.md`。

