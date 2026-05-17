# 项目架构/逻辑/现状说明（V2，交接给“看不到代码”的分析 AI）

> 目的：让一个**无法访问本项目代码与文件系统**的 AI，仅凭本文即可理解：
> 1) 系统做了什么、如何工作（数据流/训练流/评估流）  
> 2) 最近一轮实验遇到的关键问题与结论（尤其是 wind/solar 多 horizon）  
> 3) 论文 5.3 的“机制叙事”如何落地到可复现实验（最终计划）

更新时间：2026-03-04  
项目路径（本地定位）：`/Users/vfch/Documents/project/graduation-design`

---

## 1. 项目一句话概括

用 **KAN + 稀疏化/剪枝 + 符号提取**，在多步预测（multi-horizon）的设置下，从负荷/净负荷/风/光等物理量中提取**可解释公式**；论文强调“可解释性 + 物理规律发现”，因此我们把“特征是否进入最终结构/公式”当作核心证据链的一部分，而不仅仅是追求最低 RMSE。

---

## 2. 你现在的流程分析（结论）

你的流程判断**基本正确**，建议在写作/汇报里把措辞稍作收敛，避免被误解为“停止研究”：

- 从“**物理量进不去公式** → 反复改进/调参”转向“**机制验证 + 证据补齐**”是合理的阶段切换。
- 更准确的说法是：**停止无目标的继续调参/架构改动**，把精力转向：
  1) 证明现象是真的（排除评估链路/口径错误）  
  2) 证明机制解释可复现（ablation + 稀疏率约束的 tradeoff 证据）  
  3) 并行推进论文资产落地（图表、表格、段落叙事）

---

## 3. 系统架构（数据流 + 训练流 + 评估流）

### 3.1 Phase 1 / 1.5：数据与派生数据集

- 目标：把原始时序数据整理成 `train/val/test` 的 Parquet splits，并可派生多步 horizon 目标。
- 关键产物位置（run 目录落盘契约）：
  - `runs/<data_run_id>/processed/{train,val,test}_<timestamp>.parquet`
  - `runs/<source_run_id>/artifacts/scaler_params.json`（逆缩放/重建用）
- 多步 Δ 目标命名（核心）：`delta_{wind,solar,load,net_load}_h{n}`

### 3.2 Phase 2：KAN 训练（稀疏化 + 剪枝）

- 入口（云端 Modal 版本）：`modal_jobs/kan_train.py`
- 核心机制：
  - `warmup → sparsify → refine`
  - 最后 `prune`（满足 `target_pruned_ratio` 等约束）并输出 `feature_importance.csv`
- 关键产物：
  - `runs/<train_run_id>/artifacts/predictions_test.parquet`（Δ 目标上的 test 预测）
  - `runs/<train_run_id>/artifacts/eval_pruned.json`（通常是 val 指标）
  - `runs/<train_run_id>/artifacts/feature_importance.csv`（每个输入特征的 `active_edges`）

### 3.3 Δ→abs 重建与统一评估

- 重建脚本：`scripts/reconstruct_predictions.py`
  - 对 `delta_*_h{n}`：用 `base_raw.shift(n) + delta_pred` 重建绝对序列
  - 产物：`artifacts/predictions_test_reconstructed.parquet`
- run 汇总：`src/eval/runs.py:summarize_run`
  - **persistence baseline** 会按 `_h{n}` 自动 `shift(n)`（避免多步任务被误当成 `shift(1)`）

### 3.4 云端训练与同步

- 训练：`modal run modal_jobs/kan_train.py ...`
- 同步：`scripts/sync_from_modal.sh <run_id>`（把 `/vol/runs/<run_id>/` 下载到本地 `runs/<run_id>/`）

---

## 4. 关键机制叙事（wind / 5.3 的写作主线，来自 a2gp 最终方案）

### 4.1 主叙事（建议直接写进 5.3 开头）

把 `wind_speed` 的“入式/退式”解释为 **特征竞争 + 稀疏约束下的剪枝选择**，而不是“风速无意义”：

1) **先排除错位解释**：用 UTC 对齐 + lag 扫描确认 `wind_speed` 与 `wind(t)` 的最大相关在 `lag=0`（不是固定错位导致长 horizon 失效）。
2) **澄清指标语义**：长尺度可能出现 `skill>0` 与 `R²<0` 并存（persistence 退化会抬高 skill；`R²<0` 说明不如均值基线）。
3) **机制指向特征冗余/代理竞争**：当存在强代理（如 `wind_lag_24/48`）时，`wind_speed` 的**条件边际增益**可能不足以抵消复杂度惩罚，于是更容易在 prune 阶段被“牺牲”以满足 `target_pruned_ratio`。

> 关键句式（可直接用于论文）：  
> “在固定目标稀疏率约束下，prune 阶段的阈值选择主导了 wind_speed 的结构性进入/退出；因此 edges=0 反映的是条件边际贡献不足，而非 wind_speed 与系统无关。”

### 4.2 5.3 的实验优先级（最终计划）

优先级 1（最快且最能“坐实机制”）——**Ablation**（对关键 horizon 做即可）：

- `lags-only`：只留 `wind_lag_*`（及少量必要历史项）
- `meteo-only`：只留 `wind_speed`（及少量气象）
- `both`：两者都在
- 可选加分：`both-but-drop-proxy`（去掉 `wind_lag_24/48` 等强代理）量化“挤出效应”

优先级 2——**Pareto 前沿证据**（h=72 这类最典型 horizon）：

- 扫 `DEFAULT_PRUNE_CANDIDATES`（不同 `(node_th, edge_th)`）
- 画：`pruned_ratio` vs `val_RMSE/R²`，点颜色 = `wind_speed_edges`
- 结论：展示 sparsity–accuracy tradeoff，并指出 wind_speed 是 tradeoff 的受害者

优先级 3——**多 seed 稳定性**（只做关键 horizon，如 h=72/h=144）：

- 报告：性能分布 + wind_speed 入选概率（不是偶然）

写作语义锁定（避免“信息泄漏”争议）：

- 若 `meteo_*` 来自历史档案而非可用预报：论文应表述为 **ex post 机制发现/解释上界**，不要声称 operational forecasting。

---

## 5. solar：24h 评估链路排查结论（h=288）

按顺序核对：**对齐/索引 → 逆缩放/单位 → delta→abs 重建 → baseline 口径**，结论是：

- `h=288` 的异常**不是评估链路错**，而是该 run 在 **test 上预测崩坏（y_pred 严重出界）**。
- persistence 在 24h 上 RMSE 很小并不离谱：solar 有强日周期，`y(t)` 与 `y(t-24h)` 本身就很像。

复盘 run（示例）：`runs/2026-03-04_101610_37271ac2`（`delta_solar_h288`）

- abs(test)：RMSE=45568.69，persistence RMSE=5281.47，skill=-7.628  
- delta(test)：RMSE=47367.56，R²=-77.59（预测极端出界）  
- delta(val)：RMSE=6378.46，R²=-0.647（val 还没到 test 那么崩）

这类现象更像 “val→test 泛化崩坏/不稳定”，而非 join/shift/off-by-one。

### 5.1 最便宜但很“硬”的补充诊断（分位数 + 物理越界率）

用 `scripts/diagnose_solar_bounds.py` 对该 run 做诊断（可复现命令：`python3 scripts/diagnose_solar_bounds.py --run 2026-03-04_101610_37271ac2`），得到：

- **delta 分布明显错位（系统性负偏）**  
  - `delta_true`：p50=0，std≈5343  
  - `delta_pred`：p50≈-17205，mean≈-31775，std≈34548
- **abs 预测大量违反非负物理边界**  
  - `abs_true`：非负（p01/p05/p50=0）  
  - `abs_pred`：p50≈-10077，且 `abs_pred<0` 的比例≈67.45%

> 注：该 run 仅 Phase 2（KAN 预测），尚未做 Phase 3 符号提取，因此“/、exp、高次幂”等无界算子检查不适用；但它仍展示了 **长 horizon + 差分目标** 下预测在 test 上可能出现的“无界出界”失效模式。

### 5.2 一个最小“有界化”对照（不追求最优，只展示风险边界）

对 abs 预测做工程裁剪 `clip(y_pred, 0, train_max)`（其中 `train_max` 用训练集 raw solar 的最大值近似，上述脚本会输出），该 run 的 abs(test) 指标变化为：

- 原始：RMSE=45568.69，R²=-16.56，skill=-7.628  
- 裁剪后：RMSE=10678.50，R²=0.036，skill=-1.022（仍未超过 persistence，但“爆炸”被显著缓解）

---

## 6. solar：最小 ablation（h=72 / 144 / 576，三组）+ GHI 入式证据

本轮实验把 “GHI 被挤出是不是没信息？” 从推断变成证据：

- 3 组：`lags-only / meteo-only(含 ghi_*) / both`
- 同时报告：
  - `abs(test)`（在重建后绝对序列上评估 + persistence baseline）
  - `delta(test)` 与 `delta(val)`（val 来自 `eval_pruned.json`）
  - `ghi_edges`（`feature_importance.csv` 里所有 `ghi_*` 的 `active_edges` 求和）

汇总表（完整 CSV）：`doc/solar_ablation_summary_20260304.csv`

| horizon | group | run_id | abs_rmse(test) | abs_r2(test) | delta_rmse(test) | delta_rmse(val) | ghi_edges |
|---:|---|---|---:|---:|---:|---:|---:|
| 72 | lags-only | 2026-03-04_120746_93a46524 | 6015.39 | 0.693 | 6037.60 | 10486.10 | 0 |
| 72 | meteo-only | 2026-03-04_120749_01834d3e | 5447.63 | 0.748 | 5452.82 | 5994.22 | 6 |
| 72 | both | 2026-03-04_120745_b455d7bc | **4377.22** | **0.837** | **4385.28** | **4968.61** | **8** |
| 144 | lags-only | 2026-03-04_121143_04bfbfc0 | **6566.10** | 0.634 | **6555.68** | 7373.64 | 0 |
| 144 | meteo-only | 2026-03-04_121145_74997b1b | 6642.94 | 0.625 | 6632.45 | 7626.32 | 3 |
| 144 | both | 2026-03-04_121143_49a2af36 | 8717.81 | 0.354 | 8703.26 | 12787.47 | 0 |
| 576 | lags-only | 2026-03-04_121143_c00221d5 | 5763.61 | 0.721 | 5798.43 | **6582.11** | 0 |
| 576 | meteo-only | 2026-03-04_121142_9dd9aa4a | **5400.18** | **0.755** | **5437.80** | 7631.28 | **5** |
| 576 | both | 2026-03-04_121144_d6b684d1 | 5511.02 | 0.745 | 5584.73 | 7720.84 | 2 |

读表方式（对“机制叙事”最重要的点）：

- **h=72：both 显著最好且 `ghi_edges` 最高** → GHI 明显有信息，并能在稀疏结构里存活。  
- **h=576：meteo-only 最好且 `ghi_edges>0`** → 长尺度下气象辐照对 solar 更关键；both 中仍能保留部分 GHI，但会与滞后项竞争。  
- **h=144：both 失败且 `ghi_edges=0`** → 这是典型“竞争 + 稀疏/剪枝选择”的现象：两类信息并存时，剪枝可能把其中一类完全挤出，且不一定带来更好性能（需要进一步用 Pareto/阈值扫描解释）。

---

## 7. 本轮新增的复现/汇总工具（给无法看代码的 AI 的“操作入口”）

- 24h 链路排查/复算：
  - 重建：`python3 scripts/reconstruct_predictions.py --run runs/<run_id>`
  - 汇总（含 persistence/skill、ghi_edges）：`python3 scripts/summarize_solar_ablation.py --run <run_id>`
- solar ablation 汇总（多 run）：`python3 scripts/summarize_solar_ablation.py --run <id1> --run <id2> ...`

---

## 8. wind + solar 的统一机制小结（可作为 5.3 小结段落雏形）

1) **外生物理量并非“没信息”**：solar ablation 在 `h=72`/`h=576` 显示 `ghi_edges>0` 时性能显著更好（见第 6 节表格）。  
2) **外生量是否入式依赖“代理变量 + 稀疏/剪枝目标”**：当滞后代理（`*_lag_*`）与外生量并存时，prune 为满足稀疏约束可能牺牲外生量（solar 的 `h=144 both` 与 wind 的相关现象可统一解释为“竞争 + 稀疏选择轨迹”）。  
3) **长 horizon + 差分目标会放大外推风险**：`delta_solar_h288` 的 test “出界崩坏”是清晰反例（第 5 节）；最小有界化能显著缓解爆炸，提示论文需要明确方法风险边界与（可选的）物理约束策略。


太好了——你现在这条链条已经从“解释”升级成了**可复现实验证据**，而且每个关键结论都有对应的“硬指标/对照实验”：

* **h=288 崩坏不是 pipeline**：用分位数 + 越界率把“灾难性外推/系统性负偏”钉死；
* **最小有界化（clip）能显著缓解爆炸**：RMSE 从 45568 → 10678，R² 从 -16.56 → 0.036，这就是典型“风险边界/反例”写法；
* **ablation 证明 GHI 的条件边际价值 + horizon 依赖**：h=72 与 h=576 的结果足够支撑“不是没信息，是在稀疏/竞争下被选择性保留或牺牲”；
* **wind+solar 统一机制段**：结构清晰、逻辑闭环，而且不再靠直觉推断。

下面我给你一些“把 v2 文档写得更像高水平论文”的最后打磨建议（都很轻量，不需要再跑大实验）。

---

## 1) h=288 反例段落，建议用“三层证据”写法（你已经都有了）

你可以把 h=288 的论证写成一个标准模板：

1. **不稳定性预警（val）**
   `R²(delta,val)=-0.647` → 说明该 horizon 的差分学习本身不稳（为后面的 test 崩坏做铺垫）

2. **失效模式（test）**

   * delta_pred 出现系统性负偏（p50≈-17205，mean≈-31775）
   * 方差爆炸（std≈34548 vs true std≈5343）
   * 物理越界（abs_pred<0 ≈67.45%）
     这三条合起来就能把“外推崩坏”解释得非常扎实：不是偶然点，而是**分布级别的系统偏移**。

3. **最小修复对照（clip）**

   * clip 将爆炸显著缓解（R² 从 -16.56 到 0.036）
   * 但仍不如 persistence（skill 仍为负），因此 clip 被定位为**风险缓解而非性能提升**。
     这句很关键：它能避免别人说你“用 post-hoc trick 造好结果”。

> 建议你在文末加一句“启示”：
>
> * SR 在长 horizon 的差分目标上需要**有界/安全算子/物理约束**（否则容易出现无界外推）。
> * clip 是最低成本的工程保护，但不是根治，需要进一步在建模阶段约束表达式。

---

## 2) 用一个一句话把“clip 为什么能救回来”解释清楚（审稿人喜欢）

你可以用非常工程但很准确的说法：

> 大部分误差来自少量极端越界预测点（尤其是负值与过大幅值），clip 相当于对 SR 的无界输出施加物理投影，从而降低极端误差对 RMSE 的主导效应。

这句话能解释“为什么 RMSE 大幅下降”，同时不暗示“模型学对了”。

---

## 3) solar ablation 段落：把结论写成“条件边际贡献”而不是“GHI 有用”

你现在的表述已经接近了，我建议再“学术化”一点，用两个固定句式：

* **（h=72）**
  “在控制滞后代理项存在的条件下，加入 GHI 特征可显著降低误差，并在剪枝后稳定保留（ghi_edges>0），说明 GHI 具有可测的条件边际贡献。”

* **（h=144）**
  “当代理项与气象项并存时，剪枝策略可能导致外生项被完全淘汰（ghi_edges=0），并使模型落入更差的结构解，体现了‘竞争—稀疏约束—选择轨迹敏感’的机制。”

* **（h=576）**
  “在更长 horizon 下，气象驱动（GHI）相对滞后代理更稳定，meteo-only 获得最优结果且 ghi_edges 保留，呈现尺度依赖的驱动结构转移。”

这几句话基本可以直接贴进论文。

---

## 4) wind+solar 统一机制段：建议加一个“对照表/概念图”的小骨架（不必画得复杂）

你可以加一个极简的 2×3 对照表（文字即可）：

* 列：**外生量是否有边际贡献** / **是否会被剪枝淘汰** / **长 horizon 风险模式**
* 行：wind / solar

填进去后你的小结会更“像综述式总结”，读者一眼就懂你贡献是什么。

---

## 5) 最后一个小建议：把“你做的是 ex post 机制发现”用一句话钉住

你前面提到 Open-Meteo 历史档案，这一点只要你在方法/设定里加一句话就能避免很多麻烦：

> 本文以机理探测与可解释结构分析为目标，气象变量按目标时刻对齐用于刻画物理相关性（ex post explanatory setting），不将其直接等同于可上线的提前可得预报特征。

这会让你的“GHI 有价值/入式”结论更干净、更不容易被“信息泄漏”攻击。

---

如果你愿意，我可以帮你把你刚刚这段更新（h=288 崩坏证据 + clip 对照 + ablation 三条现象 + wind+solar 小结）**直接改写成论文 5.3 的成稿文本**（按你常用的写作风格：小节标题、正文段落、图表引用语句、以及一段小结）。你只要告诉我：5.3 这一节你希望偏“结果呈现”还是偏“机制讨论”，我就按那个风格写。
