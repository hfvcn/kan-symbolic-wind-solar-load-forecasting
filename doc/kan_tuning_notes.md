# KAN 物理因子调参经验（定位阶段）

> 最后更新：2026-03-03  
> 目标：**物理特征最终出现在符号公式里**，且公式精度可用。  
> 当前阶段：研究定位（优先跑 Phase2 来快速判断“物理特征是否保留 + 剪枝后精度上限”）。

---

## 0. 核心结论（截至当前）

- **物理特征已经能“进入”稀疏结构**：以 `feature_importance.csv` 中 `active_edges > 0` 为准（见第 5 节）。
- **Solar（`solar_h6` / 无 lag）当前最强候选（精度优先）**：`tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug`  
  - `R²(pruned)=0.8905`，且 `temp_2m_c` / `ghi_*` / `solar_altitude` 都存活  
  - `sparsity.total_edges=56`，`active_edges_total = total_edges - pruned_edges = 28`（已落在 Phase3 的“20~30 边舒适区”）
- **Solar（`solar_h6` / 无 lag）新增候选（少边且物理量不丢）**：`todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug`  
  - `R²(pruned)=0.8745`，`active_edges_total=24`，且 `temp_2m_c` / `ghi_*` / `solar_altitude` 都存活（更贴近 Phase3 复杂度目标）
- **Solar（更少边，符号提取更轻）**：`tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug`  
  - `R²(pruned)=0.8764`，`active_edges_total=18`，且 `temp_2m_c` 存活
- **Solar 的“少边但丢温度”仍存在**：`tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug` 能把 `total_edges` 压到 28（`active_edges_total=10`）且 `R²(pruned)=0.8078`，但 `temp_2m_c=0`。
- **Wind（`wind_h6` / 无 lag）结论更新**：在纯物理场景里，`wind_speed_*` **可以进入**（例如 `tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug` 的 `wind_speed_10m_m_s(_cubed)` 均有 `active_edges>0`），但当前 `R²(pruned)` 仍偏低（约 0.15）。
- **Wind 额外调参（tune9/tune10）效果不佳**：多数配置出现 `R²(pruned)<0` 或风速特征被剪到 0，Wind 更像是“结构/seed 敏感 + 物理特征解释力不足”的组合问题（见第 5.2 节）。
- **关键诊断点**：Wind 的主要问题更像是 **sparsify 阶段就开始崩/退化**（`eval_sparsify.json` 会直接暴露），而不只是 prune 选错阈值。
- **实现侧更新（用于减少“温度/风速被剪没”的伪失败）**：`modal_jobs/kan_train.py` 已支持 `--prune-require-features`（支持 `ghi_*` 通配符）把“关键物理特征存活”纳入 prune 候选过滤；并修复了一个 `min_rmse` 分支会绕过过滤的选择 bug；同时 refine 阶段显式置零各类正则项，避免 refine 意外改动 mask。

---

## 1. 为什么定位阶段先不跑符号提取（Phase3）

- Phase3 的符号拟合时间与“需要拟合的边数”强相关；**不剪枝/不够稀疏会导致 Phase3 极慢甚至不可用**。
- 因此定位阶段先用 Phase2 的输出作为筛选器：
  - `eval_pruned.json`：剪枝后精度（**可视为公式精度上限**）
  - `feature_importance.csv`：目标物理变量是否进入稀疏结构
  - `sparsity.json`：活跃边规模（影响 Phase3 可行性）

---

## 2. 快速评估指标（如何判断“物理量有没有保留下来”）

在每个 run 目录：

- 物理特征是否进入：`runs/<run_id>/artifacts/feature_importance.csv`
  - 判定口径：目标物理列 `active_edges > 0` 即认为“进入稀疏结构”（未来才有机会出现在符号公式里）。
- 剪枝后精度上限：`runs/<run_id>/artifacts/eval_pruned.json`
  - Phase3 公式一般只会持平或变差（因为是对剪枝后的网络做符号近似）。
- 可提取复杂度：`runs/<run_id>/artifacts/sparsity.json`
  - 关注 `total_edges` 与 `pruned_edges`，并计算：`active_edges_total = total_edges - pruned_edges`（更接近 Phase3 的真实拟合负担）。

### 2.1 新增的定位产物（强烈建议看）

为了解决“到底是 sparsify 把物理量剪没了，还是 prune 选错候选导致物理量消失”的问题，`modal_jobs/kan_train.py` 增加了 3 个诊断产物：

- `eval_sparsify.json`：sparsify 后、prune 前的测试集评估（**prune 的正确基线**）。
- `feature_importance_sparsify.csv`：sparsify 后的输入边活跃情况（用于判定“物理量是否在 prune 前就已死掉”）。
- `prune_search.json`：记录所有 prune candidates 的阈值、sparsity、eval 以及最终选择模式（`selection_mode`）。

---

## 3. 当前可调参数与默认值（TrainConfig）

默认值来自 `modal_jobs/kan_train.py::TrainConfig`（便于调参时心里有数）：

- 结构容量
  - `hidden_width=10`：当 `hidden_layers=None` 时生效（单隐藏层宽度）
  - `hidden_layers=None`：多层结构（例如 `32,32` 或 `32,16,8`）；**一旦设置，会覆盖 `hidden_width` 的作用**
  - `grid=5`：每条边 spline 的 grid 分段数
  - `k=3`：spline 阶数（或局部基函数阶数）
  - `hidden_mult=0`：乘法单元相关（非 0 时结构更激进，稳定性也更敏感）
  - `mult_arity=2`：乘法单元 arity
- 稀疏化与训练日程
  - `warmup_steps=200`, `sparsify_steps=800`, `refine_steps=200`
  - `warmup_lr=0.01`, `sparsify_lr=0.005`, `refine_lr=0.5`（已可通过 CLI 传入：`--warmup-lr/--sparsify-lr/--refine-lr`）
  - `sparsify_lamb=0.01`：稀疏正则强度（更大更稀疏，但更可能把物理量剪掉）
  - `sparsify_lamb_entropy=2.0`：熵项权重（影响稀疏化形态）
- 剪枝约束（控制“剪到多稀/允许退化多少”）
  - `target_pruned_ratio=0.8`
  - `max_rmse_degrade_ratio=1.1`（允许 RMSE 退化 ≤10%）
  - `prune_require_features=()`：prune 候选过滤用的“必须保留特征”模式（支持通配符，例如 `ghi_*`）
  - `prune_require_strict=False`：若没有任何 prune candidate 满足 `prune_require_features`，是否直接失败（默认 false，会在 `prune_search.json` 标注 fallback）
- 可复现
  - `seed=1`（当前所有调参对比尽量固定 seed，避免“靠换 seed 跑通”）

补充（不在 TrainConfig 内，但同样重要的 CLI 开关）：

- `--no-warmup-update-grid`：禁用 warmup 的 `update_grid`（用于避免某些配置下 step0 NaN；定位阶段优先可复现）。
- `--max-train-rows`：训练集下采样上限（定位阶段可用来加速，论文最终结果建议回到 full/固定上限）。
- `--prune-require-features` / `--prune-require-strict`：把“关键物理特征必须存活”写进 prune 候选选择过程（定位阶段用于减少伪失败）。

---

## 4. 数据一致性（本轮调参对比的前提）

本轮 solar 相关调参多数基于同一份 derived 数据（便于横向比较）：

- `data_run_id`: `2026_03_02_physics_s3_t4__derived_h1_6_12_24`
- `data_timestamp`: `2026-03-02_054521`

---

## 5. 已跑实验摘要（重点 run）

说明：
- R² 取自 `payload.json -> results`（与 `artifacts/eval_*.json` 一致）。
- “物理特征存活”来自对应 `feature_importance.csv` 的 `active_edges > 0`。

### 5.1 Solar（S4 pure solar，无 lag）调参结果

| run_id | 关键结构 | (l,entropy) | R²(unpruned) | R²(sparsify) | R²(pruned) | total_edges | active_edges_total | 物理特征存活（摘要） |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug` | `hw=50,g=5,k=3` | (0.0015,3.0) | 0.9010 | 0.8869 | **0.8905** | 56 | **28** | `solar_altitude`,`ghi_*`,`temp_2m_c` |
| `tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug` | `hw=60,g=5,k=3` | (0.001,3.0) | 0.9012 | 0.7724 | **0.8764** | 56 | 18 | `solar_altitude`,`ghi_*`,`temp_2m_c` |
| `tune9_20260303_solar_hw60_g5_k3_l001_e3_pr090_rm105_nwug` | `hw=60,g=5,k=3` | (0.001,3.0) | 0.9012 | 0.7750 | 0.8601 | 56 | 18 | `solar_altitude`,`ghi_*`,`temp_2m_c` |
| `tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug` | `hw=60,g=5,k=3` | (0.002,2.0) | 0.9012 | 0.7912 | 0.8078 | 28 | 10 | `solar_altitude`,`ghi_*`（`temp_2m_c=0`） |
| `tune9_20260303_solar_hw60_g5_k3_l002_e4_pr085_rm105_nwug` | `hw=60,g=5,k=3` | (0.002,4.0) | 0.9012 | 0.8015 | 0.7967 | 28 | 8 | `solar_altitude`,`ghi_temp_corr_w_m2`（`temp_2m_c=0`） |
| `tune9_20260303_solar_hw60_g5_k3_l002_e3_pr085_rm105_nwug` | `hw=60,g=5,k=3` | (0.002,3.0) | 0.9012 | 0.7484 | 0.7663 | 28 | 6 | `solar_altitude`,`ghi_temp_corr_w_m2`（`temp_2m_c=0`） |
| `tune6_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug` | `hw=80,g=5,k=3` | (0.001,1.0) | 0.8853 | 0.7948 | 0.8073 | 84 | 16 | `solar_altitude`,`ghi_*`,`temp_2m_c` |
| `tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug` | `hw=30+hm10,g=5,k=3` | (0.001,2.0) | 0.9030 | 0.7368 | 0.6893 | 122 | 77 | 物理量存活，但边数大且精度下降（乘法节点未带来“少边高精度”） |

#### 5.1.1 todo.md 批次（2026-03-03）新增 Solar runs（只列关键点）

| run_id | (l,entropy) | R²(pruned) | active_edges_total | 备注 |
|---|---:|---:|---:|---|
| `todoS1_20260303_solar_hw50_g5_k3_l0014_e3_pr085_rm105_req_nwug` | (0.0014,3.0) | 0.8879 | 28 | 精度接近当前 best，但边数未明显下降 |
| `todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug` | (0.0020,4.0) | 0.8745 | **24** | **少边且 temp/ghi/altitude 均存活**（Phase3 更友好） |

补充说明：
- 这批 run 都启用了 `--prune-require-features 'temp_2m_c,solar_altitude,ghi_*'`，用于减少“prune 选择把物理量剪没”的伪失败。
- `target_pruned_ratio=0.85` 在 Solar 上经常无法在 `max_rmse_degrade_ratio=1.05` 的约束下达成，因此 `selection_mode` 常见为 `rmse_ok_only`（实际边数仍以 `active_edges_total` 为准判断 Phase3 可行性）。

**观察到的规律（经验性，不保证普适）**：
- `hw=15` 在 unpruned 很高，但 **pruned 会崩**：说明“小容量 + 稀疏/剪枝”会把有效结构剪没。
- grid 过小（`g=3`）或过大（`g=10`）都不如 `g=5`：`g=3` 甚至出现剪枝后 R² 为负。
- 更“可提取”（edges 更少）的结构（例如 `hl=32,32` 只剩 19 条边）确实更干净，但可能把关键物理量剪掉，只剩少数代理特征。

### 5.2 Wind（纯物理 `wind_h6`，无 lag）结果

| run_id | 关键结构 | (l,entropy) | R²(unpruned) | R²(sparsify) | R²(pruned) | wind 相关特征存活（摘要） |
|---|---:|---:|---:|---:|---:|---|
| `tune6_20260303_wind_pure_windonly_hw30_g5_k3_l001_e2_nwug` | `hw=30,g=5,k=3` | (0.001,2.0) | 0.3165 | -43.9312 | -0.1609 | sparsify 阶段崩；prune 后仍未恢复 |
| `tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0005_e2_nwug` | `hw=30,g=5,k=3` | (0.0005,2.0) | 0.3165 | -0.9803 | 0.0209 | `wind_speed_10m_m_s`,`v^3` 存活（弱） |
| `tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug` | `hw=30,g=5,k=3` | (0.0002,2.0) | 0.3165 | -2.0135 | **0.1471** | `wind_speed_10m_m_s`,`v^3`,`wind_speed_hub_est` 均存活 |

#### 5.2.1 todo.md Wind “稳定性补丁包”尝试（2026-03-03）

| run_id | 关键配置 | R²(unpruned) | R²(pruned) | active_edges_total | 现象 |
|---|---|---:|---:|---:|---|
| `todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug` | `warmup=600, lr=0.01, cyclic+wind` | -89.15 | -27.62 | 31 | **明显发散/爆**（RMSE 极大） |
| `todoW2_20260303_wind_full_hw50_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug` | `warmup=600, lr=0.01, cyclic+wind+temp+pressure` | -6.21 | -0.50 | 71 | 稳定性好一些，但精度仍为负 |
| `todoW3_20260303_wind_windonly_nocyc_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug` | `warmup=600, lr=0.01, wind-only` | -0.03 | -0.16 | **9** | 不发散但精度低（结构很干净） |

**结论（面向下一轮 Wind 调参）**：
- “延长 warmup”不是直接加步数就行：在当前默认 `warmup_lr=0.01` 下，`warmup_steps=600` 在 Wind 上非常容易不稳定（尤其带 `cyclic` 时）。
- 因此下一轮如果继续探索长 warmup，需要同步降低 `warmup_lr`（已在 `modal_jobs/kan_train.py` CLI 暴露 `--warmup-lr/--sparsify-lr/--refine-lr` 便于直接扫参）。

**解读**：
- Wind 纯物理下：降低 `sparsify_lamb` 能显著提高“风速物理量存活概率”，但 `eval_sparsify` 仍经常显著退化，提示需要从 sparsify 训练稳定性本身入手（而不仅是换 prune 阈值）。
- `tune9/tune10` 的额外尝试（更宽网络、改 grid/k、加入气压/温度组）大多带来 **R² 变负或风速特征归零**，当前阶段不建议继续在纯物理 `wind_h6` 上堆结构容量；更像需要改变建模策略（见第 7.2）。

---

## 6. 离论文闭环还差什么（量化口径）

当前阶段已经满足：
- Phase2：存在候选 run 同时满足 “物理特征存活” + “剪枝后精度较高”（例如 pruned R²≈0.85）。

已经具备可直接送 Phase3 的 Solar 候选（从“更易提取”到“精度更强”）：
- `tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug`：`active_edges_total=18`，`R²(pruned)=0.8764`
- `todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug`：`active_edges_total=24`，`R²(pruned)=0.8745`
- `tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug`：`active_edges_total=28`，`R²(pruned)=0.8905`

论文闭环还缺的关键检查点（需要 Phase3）：
- **公式中确实出现目标物理变量名**（例如 solar: `solar_altitude/ghi_*/temp_2m_c`；wind: `wind_*`）
- **公式精度可用**：`formula_eval_test.json` 不显著低于 `eval_pruned.json`（退化幅度可接受）
- **公式复杂度可控**：活跃边/符号表达式复杂度在可解释范围内（否则难以写入论文并复现）

---

## 7. 下一步调参优化建议

为了进一步提高 Phase2 的表现并为 Phase3（符号提取）铺路，建议尝试以下方向：

### 7.1 Solar 场景：突破“高精度必然多边”的瓶颈
当前最强候选（`tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug`）的 `active_edges_total=18` 已经接近 Phase3 的“可提取区间”，但仍希望进一步压缩到更干净的结构同时不丢温度项：
- **`l=0.0015,e=3.0,hw=50` 是当前最好折中**：`tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug` 在 `active_edges_total=28` 时仍能达到 `R²(pruned)=0.8905` 且温度存活。
- **先用 (l,entropy) 做微调**：`l=0.002,e=2.0` 能显著压缩边数，但会丢 `temp_2m_c`；可尝试 `l=0.0015` 或保持 `l=0.002` 但提高熵项（例如 `e=3.0`）来观察温度是否回归且边数仍较小。
- **乘法节点（`hidden_mult`）目前证据不支持**：`tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug` 没有出现“少边高精度”的收益，反而边数显著上升；除非后续发现更合适的配套正则，否则不建议优先投入。
- **折中的网络拓扑**：尝试浅漏斗型网络（如 `hl=32,8` 或 `hl=48,16`），配合较温和的稀疏化参数。

### 7.2 Wind 场景：解决“模型偷懒依赖 Lag”的问题
在含 lag 的数据中，网络发现仅靠滞后风电功率就能降低 Loss，从而把相对较弱的“风速”等物理特征剪掉了（自回归遮蔽效应）。
- **纯物理底噪测试（高优）**：跑一版完全不带 lag 的纯物理特征局（`s4_pure_wind`）。确认在没有捷径时，模型能否从风速/温度/气压中学出有效映射。
- **收紧剪枝退化容忍度**：将 `max_rmse_degrade_ratio` 从 1.1 收紧到 `1.01` 或 `1.02`，逼迫算法保留所有能带来边缘性能提升的特征（包括被视为弱特征的物理量）。
 - **现状**：已验证纯物理局里“风速能进结构”，但精度明显不足；而含 lag 的局里精度可用但风速容易被遮蔽（active_edges=0）。论文闭环要么接受“风速进入但精度一般”的结论，要么需要引入显式的建模约束（例如对 wind_speed 特征做特征级保活/惩罚差分）。

### 7.3 Phase3 符号回归的准备
- **定义 Target Edges**：为 PySR 找到“20~30条边左右的帕累托最优线”。
- **强剪枝压力测试**：在目前的 Best Run (`hw=80`) 基础上，直接跑几组修改了剪枝目标的实验（如设定 `target_pruned_ratio=0.90` 或 `0.95`）。如果在剩下 25 条边时 R² 依然能维持在 0.75+，这才是送进 Phase3 的“天选局”。

---
