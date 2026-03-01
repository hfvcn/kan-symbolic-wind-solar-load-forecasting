# 项目架构/逻辑/现状说明（交接给“看不到代码”的分析 AI）

> 文档目的：让一个**无法访问本项目代码与文件系统**的 AI，仅凭本 Markdown 文档就能理解：
> 1) 系统做了什么、如何工作（架构与数据流）  
> 2) 当前实验结论与瓶颈（为什么“可解释性”和“性能”很难兼得）  
> 3) 在尽量贴合论文要求的前提下，下一步应如何改进（需要它提出可执行方案）

更新时间：2026-03-02  
项目路径（仅供本地开发者定位）：`/Users/vfch/Documents/project/graduation-design`

## 0.1 重要更新（2026-02-27）

为更贴合论文目标（在不靠平凡滞后解的情况下，让公式显式包含温度/GHI/风速等关键因素），系统新增了一个“Phase 1.5 派生数据集”能力：

- 新增 Modal 任务：`modal_jobs/derive_dataset.py`
  - 从既有 Phase 1 data_run 派生出新 data_run（无需重新下载原始数据）
  - 新增 targets：`net_load`、`delta_load`、`delta_net_load`
  - 新增工程物理代理特征（自动归一化并扩展 scaler_params）：`wind_speed_10m_m_s_cubed`、`ghi_day_w_m2`、`cdd_18c`、`hdd_18c`
  - 新增 `net_load_lag_{k}`（默认 k∈{1,12,48}）用于 net-load 持久性/残差建模
- 本地评估新增“持久性基线 + skill score”口径，并支持 `delta_*` 目标自动重建为绝对序列用于论文图表。

## 0.2 重要更新（2026-03-01）

本次已验证：采用“派生数据集 + Δ目标（残差/增量）”能让 KAN 在 5min 预测任务上**显著超过持久性基线**，并跑通“同步→重建→评估→出图”的本地闭环。

- 已同步的关键 run（均已在本地 `runs/` 可用）：
  - Phase 1.5 派生数据集（重建预测必选）：`2026-02-27_111856_3d590023`
  - Phase 2 KAN 训练（Δ负荷）：`2026-02-27_130143_635744ad`（target=`delta_load`）
  - Phase 2 KAN 训练（Δ净负荷）：`2026-02-27_163309_0420c80c`（target=`delta_net_load`）
- 本地已完成 Δ→绝对序列重建：
  - 为上述两个训练 run 生成 `artifacts/predictions_test_reconstructed.parquet` 与 `artifacts/eval_test_reconstructed.json`
- 重建后 test 指标（对比持久性基线）：
  - `delta_load→load`：RMSE ~82.85（persistence ~130.48，skill ~0.365）
  - `delta_net_load→net_load`：RMSE ~329.37（persistence ~494.18，skill ~0.333）
- 重要注意（公平性/预算差异）：上述两次 KAN 训练使用更大的训练预算（总 steps=2400，CPU 耗时约 3.4–3.5h），且稀疏正则相对放松；因此性能提升来源包含“任务重定义 + 训练预算/正则变化”，不等价于“同预算下 KAN 必然更优”。
- 解释性差距仍存在：上述两次 run 仍停留在 Phase 2（尚未做 Phase 3 符号提取）；并且 `feature_importance.csv` 显示 wind/GHI 特征在 `delta_load` run 中活跃边为 0；`delta_net_load` run 中 GHI/HDD 有进入但 wind 仍为 0。

## 0.3 重要更新（2026-03-01：论文目标倒推改进已落地）

为支撑后续的 S0–S3 论文路线（Phase3 交付物、多步 horizon、特征消融、结构化分解），项目新增/修正：

- **Phase 1.5 多步目标**：`modal_jobs/derive_dataset.py` 支持 `--horizon-steps`，可生成：
  - `delta_{load,net_load,wind,solar}_h{n}`（例如 `delta_net_load_h6`）
  - 并自动保证 `net_load_lag_{n}` 存在（用于重建与 persistence skill 评估）
- **评估口径修正**：`src/eval/runs.py` 的 persistence baseline 由固定 `shift(1)` 改为按 `target_col` 解析 `_h{n}` 后 `shift(n)`（skill/对比表对 h>1 正确）。
- **物理映射稳定性**：`src/eval/physics_mapping.py` 统一符号 assumptions（按变量名映射到 `real=True`），避免导数计算因符号对象不一致而退化为 0。
- **特征组细分（S2 消融）**：`src/data/features.py:get_feature_groups()` 新增 `solar_geom/solar_flag` 与 `meteo_*` 细分组，可做“GHI vs 太阳几何”替代关系消融。
- **结构化分解组合（S3）**：新增本地脚本 `scripts/combine_net_load_runs.py`，可将 load/wind/solar 三条子模型预测组合成一个 `phase=05-structured-combination` 的 net_load run，纳入统一评估。
- **论文导向 sweep driver**：新增 `scripts/thesis_sweep_driver.py`，集中编排 S0–S3（支持 `--dry-run/--execute`、detached、自动 sync、本地重建/组合/评估，并写 manifest）。

## 0.4 重要更新（2026-03-01：T4 全流程闭环）

已在 **Modal(T4)** 上跑通 “KAN 训练 → 基线对齐训练 → Phase3 符号提取 → 同步到本地 → Δ→绝对值重建 → 论文资产输出” 的完整闭环。

- 本次全流程关键 run（均已同步到本地 `runs/`）：
  - Phase 1.5 派生数据集（含多步 horizon）：`2026_03_01_142726_9ab14f0b__derived_h1_6_12_24`
  - Phase 2 KAN（T4）：`2026-03-01_151000_kan_nobase_nogrid_gpu`（target=`delta_net_load_h6`，`include_base=false`，`warmup_update_grid=false`）
  - Phase 4 baseline（T4，MLP）：`2026-03-01_155600_baseline_mlp_match_kan151000`（**同步 KAN 特征列 + 同步 KAN optimizer updates 预算 + 参数量对齐**）
  - Phase 3 符号提取（T4，strict 库）：`2026-03-01_160200_sym_strict_r2_0_995__kan151000`
- test 指标（见本地论文资产：`doc/paper_assets/fullflow_t4_kan151000_20260301_230545/comparison_table.csv`）：
  - KAN：RMSE=1413.51，persistence RMSE=2585.66，skill=0.453（≈45% RMSE 改善）；重建口径 WAPE≈5.26%（persistence≈9.49%）
  - baseline MLP：RMSE=1474.38，skill=0.430；参数量=1485；预算同步后 epochs=13（optimizer updates≈1274，KAN steps=1200）
  - 符号公式（strict）：RMSE=2388.46，skill=0.076；产物包含 `formula.tex / formula.sympy.txt / formula_eval_test.json`，可在 test 上复算

**是否要替换为引用论文的数据集？（kan-citate：国网 2019–2020，15min 风电/光伏出力预测）**
- 不建议把主线数据集整体替换：引用论文的任务对象是 **WP/PV 出力预测**，而本项目主线是 **耦合负荷/净负荷预测（load/net_load）**，研究对象不同。
- 更可行的写法：主线继续使用 PERFORM（保证“耦合负荷/净负荷”叙事一致）；把引用论文作为架构/训练策略的参考来源。若未来能合法获得其数据，可作为附录/外部验证实验，而非替换主线。

**从引用论文（kan-citate）中已借鉴并落地的点：**
- **多步预测（multi-step）目标与数据口径**  
  - 论文主线强调短期预测的多步设置；本项目已新增 Phase 1.5 派生数据集支持 `--horizon-steps`，生成 `delta_*_h{n}` 与 `net_load_h{n}`（例如 `delta_net_load_h6`）。  
  - 评估口径同步：persistence baseline 与 skill 按 `_h{n}` 自动用 `shift(n)`，避免把多步任务错当单步（`shift(1)`）造成“虚假提升”。  

- **多尺度（multi-scale）思想的“可符号化等价实现”**  
  - 论文用多尺度卷积核抽取不同时间尺度的模式（MCKAN/CKAN）；本项目为了保持可解释与可符号化，采用更直接的工程等价物：  
    - 用多尺度 lag 子集（如 12/24/48）表达多时间尺度依赖；  
    - 配合 horizon sweep（h=6/12/24）让外生因素在更长预测步长下更有机会进入稀疏结构。  
  - 这条路线的好处：输入变量仍是“可命名的物理量/滞后量”，符号提取时不会被卷积/池化的潜表示遮蔽。  

- **更深的 KAN（Deep-KAN）作为可控对照变量**  
  - 论文模型通过更复杂的结构提升拟合能力；本项目在不破坏 Phase3 符号提取前提下，引入 `hidden_layers`（深层 KAN）作为可控开关，用于实验回答：  
    - “加深是否提升精度？”  
    - “加深是否让符号提取更难/更不稳定？”  

- **“自动化搜索”的工程替代（可复现 sweep）**  
  - 论文用 CQALA 做超参自动优化；本项目目前没有实现该元启发式算法，但已经落地可复现 sweep 驱动：`scripts/thesis_sweep_driver.py`，能系统化跑 S0–S3 并输出 manifest + 论文资产，用于后续把“搜索过程”写成可复现实验。  

- **数值稳定性：用“评估侧稳定化”替代“全链路改 Min-Max”**  
  - 论文强调把特征统一缩放到 [0,1]（Min-Max）以提高稳定性；本项目主线仍用 Z-score，但已在 Phase3 公式评估侧落地更局部的稳定化：  
    - `safe_exp(x)=exp(clip(x,-c,c))`（medium 库）  
    - 输入按训练集分位数裁剪（`--eval-clip-quantiles low,high`）  
  - 该做法不改变 Phase1/Phase2 训练口径，但能把“符号库可用性/稳定性”作为可控变量写进论文实验（S0）。  


**未直接照搬的点（原因：与本项目论文目标冲突或成本过高）：**
- 论文的 **MCKAN（多尺度卷积 KAN）/EAA 注意力/CQALA 超参优化** 会引入更强的潜表示与复杂训练流程，虽可能提升精度，但会显著降低“公式显式包含关键物理因子”的可控性；当前项目先以“可符号化可复算”为第一优先级。

## 0.5 当前情况与面临问题（给讨论 AI 的摘要）

### 当前情况（已落地/可复现）

1) **端到端闭环已跑通（GPU T4）**  
   - 已完成：Phase2(KAN) → Phase4(baseline) → Phase3(symbolic) → sync → 本地重建与论文资产导出  
   - 论文资产：`doc/paper_assets/fullflow_t4_kan151000_20260301_230545/`

2) **KAN 已在 30min ahead（h=6）上显著超过 persistence**  
   - KAN：RMSE=1413.51，persistence=2585.66，skill=0.453（WAPE≈5.26%）  
   - baseline(MLP, 预算/特征/参数对齐)：RMSE=1474.38，skill=0.430

3) **对比公平性已工程化**  
   - baseline 支持：同步 KAN 特征列、同步 KAN 的 optimizer updates 预算、对齐参数量（避免“KAN 特调训练长度”造成优势解释争议）

4) **本地非 Modal 版本已具备**  
   - `scripts/local_fullflow.py` 支持 derive-dataset / kan-train / kan-symbolic / baseline-mlp（落盘契约与 `runs/<id>/...` 一致）

5) **已完成一次“论文导向 sweep session”（S0+S3）并产出资产**  
   - session：`2026-03-02_s0s3_t4_nogrid`  
   - manifest：`doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`  
   - 论文资产：`doc/paper_assets/thesis_sweep_2026-03-02_s0s3_t4_nogrid/`（含 `comparison_table.csv`、季节/昼夜切片表、Pareto 图）  
   - 结构化分解组合产物：本地 run `2026_03_02_s0s3_t4_nogrid__s3_combo_net_load`（`phase=05-structured-combination`）  

### 面临问题（论文交付与研究瓶颈）

P1) **Phase3 符号公式精度明显低于 KAN 本体**  
- strict 库公式 RMSE=2388.46（skill=0.076） vs KAN RMSE=1413.51（skill=0.453）  
- 已在 S0 中验证：medium(lib 含 exp) 通过 safe-exp + 输入分位裁剪可稳定运行；并出现“更接近 KAN”的候选（例如 teacher 的 `r2_threshold=0.99` 时 RMSE≈1999）。  
- 但整体仍存在显著 gap：符号公式仍明显弱于 KAN，本质问题可能是“库表达能力/结构约束”与 KAN spline 的 mismatch，需要进一步的符号库设计或结构约束策略。  
- 工程注意：  
  - KAN 训练在部分目标上启用 warmup grid update 可能触发 NaN（因此本 session 使用 `--no-warmup-update-grid` 对齐 teacher 的稳定配置）。  
  - Phase3 的 `--eval-clip-quantiles` 需要数值型输入；特征里若包含 bool（如 `is_night`）需在 inverse_transform 后显式转为 float 再做 quantile（已修复）。  

P2) **“关键物理因子进入关系式”仍不稳定**  
- 当前最强 KAN 的 `feature_importance.csv` 显示：`wind_speed_10m_m_s / ghi_w_m2 / temp_2m_c` 等外生物理因子活跃边为 0  
- Phase3 strict 公式也主要由 `wind_lag_* / solar_lag_*` 与 `solar_altitude/is_night/hour_sin/cos` 构成  
- S3（结构化分解）已工程化并跑通，但当前用 strict 库对三条子模型提取出的符号公式精度仍偏低（尤其 wind/solar 子任务），导致“子公式可解释”与“子公式可用”尚未同时满足。  
- 若论文要求最终公式显式包含 wind/GHI/temp，仍需要继续推进 **S2（替代关系消融）** 与/或对 S3 的符号提取策略做定向增强（例如更贴近物理的库、对 `is_night` 的 gating、对子任务单独调阈值/库）。  

P3) **KAN “剪枝/稀疏化”与“符号化”之间存在张力**  
- 稀疏化/剪枝有助于简化结构，但会让符号拟合更敏感；同时 KAN 的边函数若过于复杂，符号库受限时只能粗拟合 → 公式精度掉  
- Phase2 中 `artifacts/eval_pruned.json` 可能出现与最终 test 指标不一致的情况（因为 refine 后未重新写回 eval_pruned），论文对外报告应以 `predictions_test(_reconstructed).parquet` 的复算为准

P4) **任务定义与论文叙事需要统一**  
- kan-citate 的任务是 WP/PV 出力预测（国网 15min），本项目主线是 PERFORM 的耦合负荷/净负荷预测（5min、可做 h=6/12/24）  
- 因此不宜“直接换数据集”，更合理是：沿用 PERFORM 主线，并解释为何选择 `net_load`/多步 horizon 让外生物理因子更有解释空间

---

## 1. 论文要求（以此为最高目标）

论文要求原文（来自项目 README / 用户描述）：

> 在能源领域，准确预测风力和光伏发电的耦合负荷对于电网的稳定运行和智能调度至关重要。与区块链风险检测类似，负荷预测模型也需要高度的可解释性，以便电力工程师理解和信任预测结果。本课题将符号回归应用于风光耦合负荷预测，旨在发现影响负荷变化的潜在物理规律和关键因素（如风速、光照强度、温度、历史负荷等）之间的内在数学关系。通过生成可解释的数学模型，本研究不仅追求预测精度，更致力于揭示能源系统的运行机理，为可再生能源的高效消纳提供理论依据。

**从工程角度拆解为 3 个同时成立的目标：**
1) **预测精度**：至少在合理的预测设置下（不泄漏、不作弊）能达到可用 RMSE / R²  
2) **可解释模型**：输出可读的解析公式（LaTeX/SymPy），并能在测试集上复算指标  
3) **关键因素进入关系式**：公式或分解后的子公式应明确包含（或能证明显著依赖）  
   - 历史负荷（滞后）  
   - 温度 / 光照（GHI）/ 风速（或其代理）  
   - 以及与风光耦合相关的因素（至少在叙事上能自洽：为何风/光会影响“耦合负荷/净负荷”）

> 本项目当前最大的研究难点：在 5min 高频预测任务里，`load_lag_1`（上一时刻负荷）往往**压倒性强**，导致最优公式只依赖历史负荷，外生物理因子（温度/风速/GHI）成为“微小修正项”甚至完全消失。

---

## 2. 系统总体架构（哪里运行、产物怎么流）

### 2.1 运行位置

- **Modal（云端）**：跑耗时的训练/符号提取/基线（PyTorch / Julia(PySR)）  
  - 所有远端产物写入 Modal Volume（持久化存储）
- **本地（Mac）**：同步 run 产物到本地 `runs/`，再做评估、绘图、生成论文资产

### 2.2 存储契约（非常重要）

- 远端 Volume 内固定写入路径：`/vol/runs/<run_id>/...`  
- 本地同步后固定落盘：`runs/<run_id>/...`（该目录默认不提交 Git）

每个 run 目录至少包含：
- `payload.json`：该 run 的元信息（超参、数据版本、时间戳、特征列等）
- `artifacts/`：预测结果、符号公式、评估指标、可解释性报告、图片等
- （训练类）`checkpoint/`：模型权重（可复现/可继续训练）

> 更完整约定见 `.planning/MODAL.md`（本交接文档已把关键点复述在此）。

### 2.3 端到端数据流（文字版）

1) Phase 1 数据管道（Modal）  
   原始 HDF5 → 清洗/插值/质量报告 → 特征工程（含滞后特征）→ 按时间切分 train/val/test → Z-score（只拟合 train）  
   输出：`runs/<data_run_id>/processed/{train,val,test}_<timestamp>.parquet` + `scaler_params.json`

2) Phase 2 训练（Modal）  
   读取 processed splits → 选取特征列 → 训练 KAN（含稀疏正则）→ 剪枝→（可选）精修  
   输出：`runs/<train_run_id>/checkpoint/model.pt` + `artifacts/predictions_test.parquet` + 稀疏度/特征重要性等

3) Phase 3 符号提取（Modal）  
   读取 KAN checkpoint → per-edge symbolic matching → 拼接成整体 SymPy 表达式 → 输出 LaTeX/SymPy/复杂度/测试集指标  
   输出：`runs/<sym_run_id>/artifacts/formula.sympy.txt`、`formula.tex`、`formula_eval_test.json`、`predictions_test.parquet`

4) Phase 4 基线（Modal）  
   - Torch：MLP/LSTM  
   - PySR：符号回归（Julia）

5) Phase 5–8 本地评估与论文资产（Local）  
   读取多个 `runs/<id>` → 生成对比表、Pareto 图、消融图、transfer gap、敏感性分析、物理映射报告、论文图像索引

### 2.4 端到端数据流（Mermaid）

```mermaid
flowchart LR
  A["Modal: Phase1 data_pipeline\n(raw->processed splits + scaler_params)"] -->|data_run_id| B["Modal: Phase2 KAN train\n(checkpoint + predictions_test)"]
  B -->|train_run_id| C["Modal: Phase3 KAN symbolic\n(formula + predictions_test)"]
  A --> D["Modal: Phase4 baselines\n(MLP/LSTM/PySR)"]

  B --> E["Local: sync runs/<id>"]
  C --> E
  D --> E
  E --> F["Local: evaluation + plots\n(doc/paper_assets/*)"]
```

---

## 3. 代码组织（让看不到代码的 AI 也能理解模块职责）

### 3.1 顶层目录

- `modal_jobs/`：所有 Modal 任务入口（数据/训练/符号提取/基线）  
- `src/`：核心算法与工具库（数据处理、KAN 训练工具、符号构建、评估等；包含 `src/local/` 的“非 Modal”本地流水线实现）  
- `scripts/`：本地脚本（同步、评估、绘图、解释性报告、实验驱动；包含 `scripts/local_fullflow.py` 与 `scripts/thesis_sweep_driver.py`）  
- `runs/`：同步的实验产物（不提交 Git）  
- `doc/paper_assets/`：可直接用于论文写作的表格与图片（可提交 Git，视学校/开源要求）  
- `doc/optimization/`：post-v1 优化会话日志/manifest（本地生成）  
- `tests/`：单元测试（TDD 保障改动不破坏闭环）  
- `.planning/`：路线图、Modal 契约、阶段验证记录

---

## 4. 数据管道（Phase 1）——“耦合负荷”数据如何构造

### 4.1 数据来源与时间分辨率

- 数据源：ARPA-E PERFORM（风、光、负荷实际值）  
- 时间分辨率：5 分钟（全年约 105,120 条）

### 4.2 清洗与缺失处理

- 短缺失：三次样条插值（cubic spline）  
- 产出质量报告：缺失率、插值点数量、异常值（3-sigma 标记但不改值）等

### 4.3 特征工程（核心）

系统刻意把特征分为多组，便于可解释性分析与控制：

1) **气象代理（Open-Meteo 历史档案，hourly → 5min 重采样插值）**  
   - `temp_2m_c`（温度）  
   - `ghi_w_m2`（全局水平辐照度 GHI，光照强度 proxy）  
   - `wind_speed_10m_m_s`（10m 风速）  
   - `surface_pressure_hpa`（气压）

2) **天文太阳位置（pvlib）**  
   - `solar_altitude`、`solar_azimuth`、`is_night`

3) **周期编码（sin/cos）**  
   - `hour_sin/cos`、`dow_sin/cos`、`month_sin/cos`

4) **自回归滞后特征（t-1..t-48）**  
   - 为 `load/wind/solar` 都生成 `*_lag_k`（k=1..48，5min 步长 → 覆盖 4 小时）

> 研究意义：滞后项表达“系统惯性/记忆效应”；气象/太阳位置表达“外生物理驱动”；周期编码表达“人类活动周期”。

### 4.4 切分与防泄漏

- 按时间顺序切分 train/val/test  
- 在 train/val 与 val/test 之间插入 48-step gap（防止滞后特征跨边界泄漏）  
- 切分后，每个 split 再丢弃最前 48 行（去掉 lag 造成的 NaN）

### 4.5 归一化

- 对所有数值特征做 Z-score，但**不归一化 target**（例如 load）  
- 仅在 train 上拟合 scaler，并保存参数到 `scaler_params.json`

### 4.6 一个已验证的数据 run（可复现实验基准）

数据管道 run（ERCOT 2018, target=load）：`2026-02-26_032058_1957fda1`
- 原始行数：105,120  
- 特征后列数：160  
- 切分后：train/val/test = 73,536 / 15,672 / 15,672  
（这些信息写在该 run 的 `payload.json` 内）

---

## 5. 模型与训练（Phase 2）——KAN 稀疏训练 + 剪枝

### 5.1 KAN 训练的核心理念

KAN（Kolmogorov–Arnold Network）把每条边看作一元函数（样条 B-spline），天然更利于符号化与解释。

本项目训练目标不是单纯最小化误差，而是：
- 在误差可接受的情况下，让网络变得**极稀疏**（大部分边剪掉）
- 让剩余边更容易被符号库拟合成解析函数

### 5.2 训练流程（分阶段）

典型训练包含 3 段（每段都会周期性写 checkpoint 并 commit 到 Volume）：
1) warmup：主要拟合、更新 grid  
2) sparsify：加入复合正则（幅度/L1/熵等）逼迫边权归零  
3) refine：剪枝后用 LBFGS 精修（可选）

随后进行剪枝候选搜索（不同 node/edge 阈值），挑选：
- 稀疏度 ≥ target_pruned_ratio（默认 0.8）
- pruned 后 RMSE 不超过 unpruned 的一定比例（默认 1.1 倍）

### 5.3 Phase 2 输出

典型输出文件：
- `checkpoint/model.pt`：包含模型 state + payload + feature_cols + target_scaler + 最佳剪枝阈值
- `artifacts/predictions_test.parquet`：对 test split 的预测（用于统一评估口径）
- `artifacts/feature_importance.csv`：从稀疏结构统计“哪些特征仍有活跃边”
- `artifacts/sparsity.json`：剪枝比例（复杂度 proxy）
- `artifacts/eval_unpruned.json`、`artifacts/eval_pruned.json`：训练期监控指标（注意：基于 val split）

### 5.4 频繁调参点（已暴露为 CLI）

为方便实验迭代，本项目已将“经常改的部分”暴露到 `kan_train` 的 CLI：
- 训练超参：steps / lambdas / hidden_width / hidden_mult / mult_arity / use_gpu / max_train_rows
- 特征选择：`include_groups`、`lag_series`、`lag_steps`、`include_base`

关键点：可以用 `lag_series=none` 或移除 `load` 来抑制“历史负荷滞后项压制一切”的问题。

---

## 6. 符号提取（Phase 3）——从稀疏 KAN 变成可读公式

### 6.1 方法概述

- 对每条未剪掉的边，调用 `suggest_symbolic()` 在一个符号库中寻找最拟合的一元函数  
- 依据 `r2_threshold` 决定是否“固定”该边为符号函数  
- 把所有边组合成最终的 SymPy 表达式，并用 scaler 参数做**输入/输出反归一化**，使公式直接对应原始量纲

### 6.2 符号库（可控）

默认库大致包括：
- 多项式：`x, x^2, x^3, x^4`
- 三角：`sin, cos`
- 非线性：`exp, gaussian, abs`

已支持在 CLI 里用 `--lib` 传入逗号分隔列表，从而禁止 `exp/gaussian` 以提升可解释性（代价是拟合能力下降）。

### 6.3 Phase 3 输出

典型输出文件：
- `artifacts/formula.sympy.txt`：一行 SymPy 表达式（可复算）
- `artifacts/formula.tex`：LaTeX（论文可直接贴）
- `artifacts/formula_metrics.json`：复杂度（node_count / tree_depth 等）
- `artifacts/formula_eval_test.json`：公式在 test 上的 RMSE/MAE/R²
- `artifacts/predictions_test.parquet`：公式预测结果

---

## 7. 基线（Phase 4）——用于论证“不是只有 KAN 才能做到”

已实现并验证的基线：
- Torch：`MLP`、`LSTM`
- PySR：直接符号回归（Julia），支持 seeded（用 KAN symbolic 提供候选特征/形式）

重要事实（对论文叙事很关键）：
- 在 **5 分钟预测**任务里，只要允许 `load_lag_1`，简单模型就能做到接近“复制上一时刻”，RMSE 会非常低。  
  这会导致：性能对比上 PySR/MLP 很强，但公式也会非常“自回归化”，物理外生因子难出头。

---

## 8. 评估、可解释性报告与论文资产（Phase 5–8，本地）

本地脚本会生成一套“可直接写进论文”的资产（目录 `doc/paper_assets/`），核心包括：
- `comparison_table.csv`：多 run 指标对比（rmse/mae/r2/complexity/physical_score/compute_time 等）
- `pareto_rmse_vs_complexity.png`：精度-复杂度散点
- `ablation_table.csv` + ablation 图：正则项消融
- `transfer_gaps.csv`：跨 ISO 迁移差距（若跑过 transfer_eval）
- `physics_mapping_*.md/json`：物理映射报告（目前对 load 仅做“温度敏感性存在”检查）
- `sensitivity_*`：敏感性分析（对温度/风速/GHI 等变量的导数分布与散点）
- `figures/`：预测曲线、残差分布、公式渲染图等
- `ASSET_INDEX.md`：把所有资产索引成可快速引用的清单

补充说明（容易踩坑）：
- 对 `delta_*` 目标：需要先运行 `scripts/reconstruct_predictions.py` 生成“绝对值口径”的预测；评估脚本会优先读取 `predictions_test_reconstructed.parquet`。
- `scripts/evaluate_runs.py` 会按传入的 `--run` 列表生成对比表；如果只传少量 run，会覆盖 `comparison_table.csv` 为该子集。若要长期保留“全量对比”，需要把所有 run 一并传入，或另存一份全量表（例如 `comparison_table_all_runs.csv`）。
-（环境兼容性）在受限环境里若 Matplotlib 无法写入 `~/.matplotlib`，可先设置 `MPLCONFIGDIR` 到可写目录再运行绘图脚本。

> 注意：`physics_mapping.json` 是本地脚本写入的，会被 `sync_from_modal.sh` 重新同步覆盖；因此每次重新 sync 之后，若需要 `physical_score` 进入对比表，需要重新跑 physics_mapping 脚本。

---

## 9. 一键实验驱动（重要：方便后续 AI 给“可执行调参方案”）

为便于频繁调参，本项目把“调参 + Modal 调用 + 同步 + 本地评估/绘图/索引”集成到脚本入口：

- **论文导向（S0–S3，推荐）**：`scripts/thesis_sweep_driver.py`
  - dry-run：`python3 scripts/thesis_sweep_driver.py --source-data-run-id <phase1_id> --dry-run`
  - 真跑（含 GPU T4）：`python3 scripts/thesis_sweep_driver.py --source-data-run-id <phase1_id> --execute --use-gpu`
  - 后台提交（不自动 sync，本地稍后手动同步）：`python3 scripts/thesis_sweep_driver.py --source-data-run-id <phase1_id> --execute --use-gpu --detached-remote`
- **通用实验（legacy）**：`scripts/experiment_driver.py`

使用方式：
1) 编辑脚本顶部 `CONFIG`（数据 run_id、KAN sweep、symbolic sweep、是否跑 baselines 等）
2) 先 dry-run 看命令：
   - `python3 scripts/experiment_driver.py --dry-run`
3) 真跑：
   - `python3 scripts/experiment_driver.py --execute`

每次运行会写入：
- `doc/optimization/<session_id>/manifest.json`：run_id 列表 + 超参 + 指标快照
- `doc/optimization/<session_id>/run_log.md`：可读日志

---

## 10. 同步脚本（`sync_from_modal.sh`）近期变更说明

原因：Modal CLI 在下载目录时，可能出现“嵌套路径”差异，导致本地出现：
- `runs/<id>/<id>/payload.json`（重复嵌套）
- 或下载到 `runs/` 根目录导致结构混乱

当前脚本采取更稳健策略：
1) 先下载到临时目录  
2) 通过定位 `payload.json` 判断真实 run 根目录  
3) 再把内容复制到 `runs/<run_id>/`  

这保证：只要远端遵守 `/vol/runs/<run_id>/...` 契约，本地同步结构就稳定一致。

---

## 11. 已验证的关键 run（现状与“遇到的情况”）

> 下面列出关键结论：**性能很强的模型通常被历史负荷滞后项主导**；  
> 强行去掉滞后项能让温度/太阳角度进入公式，但性能大幅下降。

### 11.1 数据 run

- Phase 1（ERCOT 2018, target=load）：`2026-02-26_032058_1957fda1`
  - 105,120 行；特征后 160 列；切分后 73,536 / 15,672 / 15,672
- Phase 1.5（派生数据集：net_load + delta targets + 物理代理特征）：`2026-02-27_111856_3d590023`
  - source：`2026-02-26_032058_1957fda1`
  - 新增 targets：`net_load`、`delta_load`、`delta_net_load`
  - 新增特征：`wind_speed_10m_m_s_cubed`、`ghi_day_w_m2`、`cdd_18c`、`hdd_18c` 等
- Phase 1.5（派生数据集：**多步 horizon**）：`2026_03_01_142726_9ab14f0b__derived_h1_6_12_24`
  - source：`2026-02-26_032058_1957fda1`
  - 生成 targets：`delta_{load,net_load,wind,solar}_h{1,6,12,24}` 与 `net_load_h{1,6,12,24}`（用于 S1 horizon sweep / S3 结构化分解）

### 11.2 预测性能（test）概览（部分关键 run）

（说明：均为 test split 指标；若是 symbolic run，则为公式在 test 上的指标）

| run_id | 类型 | target | 关键设置 | RMSE | R² | 备注 |
|---|---|---|---|---:|---:|---|
| `2026-03-01_151000_kan_nobase_nogrid_gpu` | KAN train（T4） | `delta_net_load_h6→net_load_h6`（重建口径） | `lag_steps=[12,24,48]`，`include_base=false`，`warmup_update_grid=false` | 1413.51 | 0.99107 | **skill=0.453**；persistence RMSE=2585.66；论文资产已生成 |
| `2026-03-01_155600_baseline_mlp_match_kan151000` | Torch MLP（T4） | `delta_net_load_h6→net_load_h6`（重建口径） | **同步 KAN 特征列 + 同步 optimizer updates 预算 + 参数量对齐** | 1474.38 | 0.99029 | skill=0.430；param≈1485；epochs=13 |
| `2026-03-01_160200_sym_strict_r2_0_995__kan151000` | KAN symbolic（T4） | `delta_net_load_h6→net_load_h6`（重建口径） | strict lib，`r2_threshold=0.995` | 2388.46 | 0.97452 | skill=0.076；输出 `formula.tex`/`formula_eval_test.json` |
| `2026-02-27_130143_635744ad` | KAN train | `delta_load→load`（重建口径） | `lag_steps=[12,24,48]`，`include_base=false` | ~82.85 | ~0.99968 | **skill~0.365**；耗时~3.5h（CPU）；wind/GHI 特征活跃边为 0 |
| `2026-02-27_163309_0420c80c` | KAN train | `delta_net_load→net_load`（重建口径） | `lag_steps=[12,24,48]`，`include_base=false` | ~329.37 | ~0.99952 | **skill~0.333**；耗时~3.4h（CPU）；GHI/HDD 进入但 wind 活跃边为 0 |
| `2026-02-26_043102_777fac2d` | Torch MLP | load | 含 `load_lag_1` | ~175.7 | ~0.9986 | 5min 预测几乎可复制上一时刻 |
| `2026-02-26_045336_77244377` | PySR | load | 含 `load_lag_1` | ~127.6 | ~0.9992 | 公式非常简单但强依赖历史负荷 |
| `2026-02-26_055200_958b3949` | KAN train | load | 消融 no_l1（仍含 lag） | ~1050.1 | ~0.9484 | KAN 明显落后于简单基线 |
| `2026-02-26_090620_1fc7d27a` | KAN symbolic | load | 从 `055200` 提取 | ~1861.0 | ~0.8380 | 性能下降；公式仍主要由 load lag 组成 |
| `2026-02-26_122629_b5a495b4` | KAN train | load | **去掉所有 lag**（外生-only） | ~5555.4 | ~-0.4431 | 性能崩溃，但利于“物理因子进公式” |
| `2026-02-26_130651_18ca3f58` | KAN symbolic | load | 外生-only + 禁 exp/gaussian | ~5641.6 | ~-0.4883 | 公式含 `temp_2m_c`/`solar_altitude`，物理映射得分 1 |

> 物理映射报告（本地生成，供论文引用）：`doc/paper_assets/physics_mapping_<run_id>.md/json`

### 11.3 当前“遇到的情况”（问题陈述）

1) **强自回归支配**：允许 `load_lag_1` 时，所有强模型（MLP/PySR/部分 KAN）都会主要依赖它 → 精度极高，但“风速/光照/温度”很难进入最终公式（或只作为很小的修正项，容易被剪枝/符号化忽略）。  
2) **外生-only 可解释但不准**：去掉所有 lag 后，温度/太阳高度角等会进入公式，甚至能通过“温度敏感性存在”的检查，但预测性能显著下降（R² 变负）。  
3) **KAN 与基线的关系已发生变化**：在原始 `load` 目标下，KAN 仍明显落后于 PySR/MLP；但在 Phase 1.5 派生数据集上改用 `delta_*`（尤其是 `delta_net_load_h6`）后，KAN 能稳定超过持久性基线（skill≈0.45）。同时，本项目已实现“公平对比”机制：baseline 可同步 KAN 的特征列、训练行数与 optimizer updates 预算，并对齐参数量（见 `baseline_torch.py --sync-kan-*` 的 payload 记录）。  
4) **耦合负荷定义需明确**：论文提“风光耦合负荷”，但目前实验目标主要是 `load`；如果“耦合负荷”更接近净负荷 `net_load = load - wind - solar` 或某种耦合形式，则需要在数据定义/目标函数上做调整，才能让风/光因子在数学关系中自然出现。  
5) **关键物理因子仍可能被稀疏化剪掉**：即使已提供 wind/GHI/温度及其工程代理特征，当前最强的 `delta_net_load_h6` KAN run（`2026-03-01_151000_...`）在 `feature_importance.csv` 中仍把 `wind_speed_10m_m_s / ghi_w_m2 / temp_2m_c` 剪到 0，而主要依赖 `wind_lag_* / solar_lag_*` 与 `solar_altitude / is_night / hour_sin/cos`。Phase 3 提取出的 strict 公式也基本只包含这些变量。这意味着：若论文硬要求“风速、光照强度、温度、历史负荷”在最终数学关系里**显式出现**，仍需要通过 S2（替代关系消融/强制使用 GHI）或 S3（结构化分解：先用风速/GHI 预测出力，再组合到 net_load）来达标。  

---

## 12. 交给分析 AI 的“任务说明”（让它给下一步方案）

请基于上述架构与现状，输出一个**可执行的改进方案**，要求：

1) **贴合论文要求**：解释清楚如何让关键因素（风速/光照/温度/历史负荷）进入可解释数学关系中，并能在 test 上验证  
2) **兼顾性能**：不能只为了可解释而让 R² 长期为负；需要给出“性能与可解释性的折中策略”  
3) **可落地**：最好以 `scripts/thesis_sweep_driver.py`（论文导向 S0–S3）或 `scripts/experiment_driver.py`（通用）为入口，给出 2–4 组建议 sweep（包括特征选择与训练/符号提取参数）  
4) **避免“显而易见的作弊/平凡解”**：例如把 `net_load = load - wind - solar` 直接当作“发现的规律”应明确其学术意义有限；若使用，也应说明它在论文中的定位（定义 vs 发现）。  
5) **建议补充的评估**：例如改变预测 horizon（1h ahead）、做残差建模、分解模型（baseline + correction）、或扩展物理映射检查（不仅温度，还应检查 GHI/风速敏感性）等。

可选但加分：
- 给出“论文叙事结构”的建议：如何把“高精度基线”和“KAN-SR 物理发现”组合成一篇可信的毕业论文。

---

## 13. 本地复现（给开发者，不给外部 AI）

单测：
- `python3 -m unittest discover -s tests -p 'test_*.py'`

一键实验：
- `python3 scripts/thesis_sweep_driver.py --source-data-run-id <phase1_id> --dry-run`
- `python3 scripts/thesis_sweep_driver.py --source-data-run-id <phase1_id> --execute --use-gpu`
- `python3 scripts/experiment_driver.py --dry-run`
- `python3 scripts/experiment_driver.py --execute`

本地（非 Modal）全流程入口：
- `python3 scripts/local_fullflow.py --help`

论文资产重生成：
- 参考 `doc/paper_assets/README.md`
-（本次 2026-03-01 验证的最小闭环：T4 fullflow）同步→重建→评估→出图：
  - `scripts/sync_from_modal.sh 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24`
  - `scripts/sync_from_modal.sh 2026-03-01_151000_kan_nobase_nogrid_gpu`
  - `scripts/sync_from_modal.sh 2026-03-01_155600_baseline_mlp_match_kan151000`
  - `scripts/sync_from_modal.sh 2026-03-01_160200_sym_strict_r2_0_995__kan151000`
  - `python3 scripts/reconstruct_predictions.py --run runs/2026-03-01_151000_kan_nobase_nogrid_gpu --run runs/2026-03-01_155600_baseline_mlp_match_kan151000 --run runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000`
  - `python3 scripts/evaluate_runs.py --run runs/2026-03-01_151000_kan_nobase_nogrid_gpu --run runs/2026-03-01_155600_baseline_mlp_match_kan151000 --run runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000 --out-dir doc/paper_assets/<your_session_dir>`
