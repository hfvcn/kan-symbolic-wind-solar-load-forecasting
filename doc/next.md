## 注意:实验代码通过modal运行
# 当前需要保留的记录

## 1. 目前已确认的遗漏问题

1. 当前中期报告和中期答辩 PPT 的主要问题，不是没有结论，而是**过程链被压缩得太厉害**。现在留下来的 mostly 是“结果链”，缺了“项目是怎么一步步收敛到这些结论的”。
2. 当前版本里最容易被压掉的关键信息有：
   - 不是一开始就直接得到“负荷影响/捷径竞争”这个解释，中间其实经历过“先怀疑调参问题，再多轮排除”的过程。
   - direct 路线下公式负荷主导退化之后，之所以转向 focused/component teacher，是因为需要验证“并不是所有物理量都进不去公式”。
   - solar 是稳定正例，wind 是边界反例，这两个角色必须同时出现，故事才完整。
   - wind 的关键结论不是“训练失败”，而是“更难以被简洁、稳定、泛化良好的原始风速项显式保留”。
   - wind 的 horizon 结论可以写成“先增强、后减弱”或“非单调”；但“其他物理量持续下降/单调下降”目前证据不足，不能写强。
3. 当前更稳妥的边界表述应保留：
   - 当前系统不是经典蒸馏，而是 `KAN teacher + symbolic extraction`。
   - `KAN > PySR` 需要限定到**当前主实验设置**，不能写成全程都如此。
   - 当前流程存在切分前插值/补值带来的非严格无泄漏问题，机制性结论要控制强度。

## 2. 我现在口述的项目推进记录原文

> 1：精度优化  
> 2：公式提取，发现公式中没有物理因素加入  
> 3：初步判断为参数调整太随意所致，进行多轮不同情况的调参，物理因素进入效果依旧不佳，重新判断为受到负荷影响  
> 4：隔离负荷重新实验，除了风力因素外效果正常  
> 5：进一步探究风力为何不同，发现可能是由于风力本身物理特性所致（周期性）  
> 6：带着这个怀疑进行不同时长的实验，发现风力效果先升后降，其他物理因素持续下降

## 3. 之前文件里已经写下的推进记录原文

### 3.1 `doc/项目现状系统核查_20260314.md`

#### 3.1.1 实验过程演化说明（修正版）

> 这部分用于说明当前项目是如何从“预测性能比较”逐步转向“物理量能否进入公式”的。  
>   
> 1. 项目早期的重点首先是比较不同方法的预测能力，但需要区分“历史探索期”和“当前主实验期”。历史探索期确实存在个别早期 `load` 目标 run 中 `PySR > KAN` 的情况；不过那一批 KAN 仍属于小模型、弱配置、未形成后期 canonical 设置的阶段，不能直接代表当前主线结论。进入后期 canonical matched `delta_net_load_h6` 主实验后，KAN teacher 已经明确优于直接 PySR，因此当前真正的瓶颈不再是“KAN 能不能赢过 PySR”，而是“高精度 teacher 能不能转化成物理上可信的符号公式”。  
>   
> 2. 正是在这个背景下，项目后续路线才从单纯比较预测精度，转向以 `KAN teacher + symbolic extraction` 为核心的解释链路。这里并不是传统意义上的“教师-学生蒸馏训练”，而是先训练高精度 KAN teacher，再对其进行后验符号提取。转向的直接原因不是为了继续刷预测指标，而是观察到 direct 路线下最终公式过度依赖负荷自身，物理量的进入频率、结构显著性和符号可辨识性都偏低，甚至常常完全进不了最终公式。  
>   
> 3. 在后续大量调参与 focused teacher / component teacher 设计之后，可以看到这个问题并不是“整个链路都无法让物理量进公式”。以 solar、GHI、temperature 为代表的物理量，在多条 focused 路线中已经能够较稳定地进入最终公式，说明当前方法在一般意义上具备把物理信息显式化的能力。  
>   
> 4. 真正持续异常的是 wind。即使在多次调参、特征调整和 teacher 设计之后，wind 在不少设置里仍然表现为：要么原始风速项进不去公式，要么只以 `wind_lag_*`、代理变量或替代表达的形式间接出现，而不是以简洁、稳定的原始风速项显式保留。因此，当前更合理的解释不是“训练失败”，而是 wind 在当前任务与时间尺度下具有更低的符号可辨识性。换句话说，wind 的信息可能并非不存在，而是更容易被历史项或其他变量吸收；而符号提取本身又带有简洁性偏置，因此 raw wind term 更容易被抛弃。  
>   
> 5. 后续 long-horizon 实验进一步支持了这种解释。现有证据更适合写成：wind 在不同 horizon 下呈现出较明显的非单调行为，中等 horizon 更容易显现出可辨识结构，整体上更接近“先增强、后减弱”；而其他物理量目前并不支持同样强的稳定非单调叙事。更稳妥的说法是，其他物理量在更长 horizon 下整体会变得更不稳定，部分量表现出减弱趋势，但不宜简单概括为严格单调下降。  
>   
> 6. 因此，当前项目的实验过程可以概括为：先确认后期 canonical 设置下 KAN teacher 在预测层面优于直接 PySR；随后发现 direct 公式被负荷主导，解释层存在物理量入式不足的问题；再通过 focused teacher 与 component teacher 的连续实验验证“并不是所有物理量都进不去”，最终把问题收敛到 wind 的低符号可辨识性及其 horizon 依赖性上。这个过程本身就是论文讨论部分的重要材料。

#### 3.1.2 关于 horizon 依赖性的原文限制

> `wind 先增后降` 可以作为中等强度结论。  
> `其他变量逐渐下降` 目前证据不足，不宜写成正式主结论。

#### 3.1.3 当前最值得保住的主线

> 1. 当前 direct net-load 路线确实存在负荷主导退化  
> 2. focused teacher / component teacher 的确能让真实物理因子进入解释层  
> 3. solar 已经提供了较强的稳定正例  
> 4. wind 提供的是更有研究意味的反例与边界：它可能有价值，但不容易被简单、稳定、泛化良好的符号表达显式保留

### 3.2 `doc/开题报告草稿.md`

#### 3.2.1 研究思路

> 本课题的研究思路经历了一个从“预测精度比较”到“物理量可辨识性分析”的演化过程。项目早期的重点是比较KAN与PySR等方法的预测能力；在确认KAN教师在当前标准对齐主实验设置下优于对齐版PySR后，发现真正的瓶颈不是“KAN能不能赢”，而是“高精度教师能不能转化成物理上可信的符号公式”。进一步实验发现直接路线存在负荷主导退化，由此转向分量聚焦教师设计，并发现太阳能与风电在符号可辨识性上的系统差异。后续研究将围绕“变量可辨识性、替代表达与符号简洁性偏置”展开，而不仅仅是模型精度对比。

#### 3.2.2 已写进开题草稿的几条关键记录

> 在当前已完成的多组直接路线试验中，直接对净负荷提取公式时反复观察到符号提取运行坍缩为仅含 `load` 项的极简公式，物理量全部被丢弃。这一现象促使后续研究进一步引入分量聚焦教师作为改进方向。  
>   
> 在分量聚焦教师设置下，与太阳能分量相关的物理量在已完成的符号提取运行中均进入了公式，初步呈现出较稳定的保留趋势。风电则更为复杂：在一条路线下原始风速未进入但预测技能分数为正（主要通过滞后项代理），在另一条路线下原始风速进入但预测技能分数为负，初步提示“显式进入”与“泛化效果”并非简单对应关系。  
>   
> 在已完成的多步长实验中，风电的预测技能分数和风速边数呈非单调变化，初步提示中等预测步长更容易显现可用结构。但太阳能在长预测步长下的结果也较复杂，目前不支持简单的单调叙事。

### 3.3 `doc/tmp/cco46.md`

#### 3.3.1 论文定位与叙事主线原文

> “我们发现，在净负荷预测任务中，直接做符号提取会退化为负荷主导 → 于是设计了 focused/component teacher → solar 物理量可以稳定进入公式（正例）→ wind 则不行（反例）→ 进一步分析发现 wind 的低可辨识性与 horizon 有非单调关系 → 这说明符号可解释性不仅取决于变量本身的信息量，还受替代表达、时间尺度和符号简洁性偏置的共同影响。”

## 4. 当前可直接采用的稳妥版本

1. 项目推进过程最稳的写法，不是“调了很多参数终于找到正确参数”，而是：
   - 先做精度比较；
   - 再发现 direct 路线公式负荷主导；
   - 再用 focused/component teacher 证明不是所有物理量都进不去；
   - 最后把问题收敛到 wind 的低符号可辨识性和 horizon 非单调。
2. 现在口述版本里的这句话需要降强度：
   - “其他物理因素持续下降”
   - 目前应改成：“其他物理量在更长 horizon 下整体更不稳定，部分量表现出减弱趋势，但不宜概括为严格单调下降。”
3. 现在口述版本里的这句话也需要降强度：
   - “风力为何不同，发现可能是由于风力本身物理特性所致（周期性）”
   - 目前更稳的说法应是：“wind 的低可辨识性更可能受时间尺度、变量替代性与符号简洁性偏置共同影响。”

## 5. 论文收口前必须补的后续工作

> **状态标注（更新于 2026-04-17）**：这一节最初记录的是“工程产物生成 + 论文口径收口”的联动缺口。现在 `S3` 的净负荷总公式已经真实生成、落盘并完成 test 复算：正式 run 为 `paperref_20260306_121725_v2__s3_combo_net_load`，正式比较表为 `doc/thesis_sweeps/paperref_20260306_121725_v2/paper_assets/comparison_table.csv`。相关主表、图表与正文口径也已完成回写，因此本节主闭环现已完成；剩余只保留一个后续增强项：`wind/solar` 更深的 symbolic 提取留作独立后处理，不再作为当前 `next` 清单的前置条件。

### 5.1 这轮已经补齐的最大缺口

1. 当前最强结果依然不是“direct net-load 直接导出一条同时含风速/光照/温度/历史负荷的总公式”，而是：
   - direct 路线会坍缩为 `load` 主导公式；
   - S2 证明物理量消失的主要原因是 lag shortcut competition；
   - S3 能把 load / wind / solar 三个子任务的关键物理量稳定保留在局部公式中，并保持组合预测精度。
2. `s3_combo_net_load` 已不再只有 `predictions_test.parquet` 与 `eval_test.json`。当前正式产物还包括：
   - `formula_combined.sympy.txt`
   - `formula_combined.tex`
   - `formula_combined_metrics.json`
   - `formula_eval_test.json`
   - `predictions_test_formula.parquet`
3. 这意味着当前已经同时具备：
   - “三条局部公式 + 一个组合后的净负荷预测器”
   - “由三条局部公式显式组合得到的一条净负荷总公式”
4. 因此当前后续工作的重点，不再是“把总公式生出来”，而是把它正确写入主表、图表和正文口径，并明确呈现它相对组合预测器的 transfer gap。
5. 当前阶段如果继续遗漏的，不是工程产物本身，而是：
   - 主表是否把 `S3 composite formula` 单列出来；
   - 图表是否把 `predictor` 与 `formula` 分对象展示；
   - 正文是否仍在把 `S3` 的局部公式可解释性和组合预测精度混写成同一个对象。

### 5.2 工程上已经补齐的产物

1. `scripts/combine_net_load_runs.py` 已扩展为不仅组合三个子任务的预测值，也能读取三个子任务 symbolic run 的 `formula_reconstructed.sympy.txt`。
2. 组合阶段已显式构造：
   - `F_net = F_load - F_wind - F_solar`
3. 组合 run 已新增并落盘以下产物：
   - `formula_combined.sympy.txt`
   - `formula_combined.tex`
   - `formula_eval_test.json`
   - `predictions_test_formula.parquet`
4. 组合公式评估已经直接对 test 集逐点计算，并已进入正式比较表。
5. 这一步保持了 Debug-First：若组合公式数值评估异常，会显式报错而不是静默降级。当前 `paperref` 正式 run 成功完成，无额外溢出/裁剪 fallback。

### 5.3 主叙事与补充交付的关系

1. 当前论文主叙事仍不应改回“为了满足课题要求而强行追一条总公式”的写法。更稳的主线仍然是：
   - direct 公式坍缩是失败案例；
   - S2 是机制验证；
   - S3 是建设性解决方案。
2. 课题原始要求中“最终给出净负荷公式”这一项，仍应作为对现有主叙事的补充交付（closure），而不是反过来支配全文结构。
3. 因此当前收口策略应是：
   - 主贡献继续强调“为什么 direct 路线失败、为什么 S3 能恢复可辨识性”；
   - 额外交付明确写出“由三条局部公式显式组合得到净负荷总公式，并已完成 test 复算”。
4. 现在可以把 `paperref_20260306_121725_v2__s3_combo_net_load__formula` 写成“由三条局部公式结构化组合得到的净负荷总公式”；但仍必须与 `paperref_20260306_121725_v2__s3_combo_net_load` 这个组合预测器分对象叙述，不能混成一个结果。
5. `KAN > PySR`、`wind 先增后降`、`其他物理量下降` 等表述仍需保持现有的边界强度，不因收口需要而过度泛化。

### 5.4 当前论文里已经有的比较，和现在新增的比较

1. 当前论文里原本就已经明确包含“公式 vs KAN”的比较，不是完全空白：
   - 方法上已经定义了 `TGR = RMSE_symbolic / RMSE_teacher`；
   - direct 主结果里已经有 `KAN教师` vs `strict symbolic` 的数值比较；
   - S3 子任务层面已经有 load / wind / solar 各自的 TGR。
2. 当前已经补齐此前真正缺失的那一组比较：
   - `S3 composite formula` vs `S3 composite predictor`
   - 对应正式落盘位置：`doc/thesis_sweeps/paperref_20260306_121725_v2/paper_assets/comparison_table.csv`
3. 当前 `paperref` 正式数值是：
   - `S3 composite predictor`：RMSE `1254.6153`，MAE `821.8361`，R2 `0.9929838`，skill `0.5153250`
   - `S3 composite formula`：RMSE `2644.3554`，MAE `1706.3551`，R2 `0.9688310`，skill `-0.0214366`，complexity `310`
4. 这说明当前已经可以把 `s3_combo_net_load__formula` 称为“最终净负荷总公式”，但不能把它写成“最终净负荷最优结果”：
   - 公式对象已存在；
   - 但它相对组合预测器仍存在明显 transfer gap。
5. 后续性能排查已把这条改进真正落回正式 `paperref` run：structured combo pipeline 现在按真实 test 指标自动选择更优 predictor / formula candidate，而不再固定绑定单一路径。2026-04-18 已通过显式 refresh 流程把 detached symbolic session 与外部 best symbolic run 并入正式 `paper_assets`；当前 `S3 composite formula` 实际采用的局部公式来源为：
   - `load`：`s3_formula_grid_20260417__sym_medium_r2_0_98_paperref_20260306_121725_v2_s3_comp_load_delta_h6`
   - `wind`：`symbolic_cpu24h_detached_v2_20260418__sym_medium_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6`
   - `solar`：`paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6`
   但这轮 refresh 完成后，`S3 composite predictor` 与 `S3 composite formula` 的最终净负荷 test 指标并未继续提升，因此论文口径应写成“候选池与公式来源已刷新并显式化”，而不是“最终 S3 数值再次改善”。
6. 进一步的 `wind/solar` full-grid symbolic 深挖已作为后处理完成一轮，并已纳入正式 `comparison_table.csv`；当前剩余工作不再是“把任务跑完”，而是是否还要继续做更激进的 symbolic 扩展搜索。

### 5.5 论文主表与图表的补齐情况

1. 当前主表里已经有：
   - `direct KAN`
   - `matched MLP`
   - `direct symbolic`
2. 主结果源表现在已经补齐 `S3 composite formula` 这一行；正式来源就是：
   - `doc/thesis_sweeps/paperref_20260306_121725_v2/paper_assets/comparison_table.csv`
3. 这行结果当前已按正式口径报告：
   - RMSE / MAE / R2 / skill
   - complexity = `310`（`sympy_node_count`）
   - 公式来源说明（由 load / wind / solar 三个局部公式结构化组合）
4. 图表上已经补出四对象对比资产：
   - `direct KAN` vs `direct symbolic` vs `S3 composite predictor` vs `S3 composite formula`
5. 当前正式结果已经明确表明：`S3 composite formula` 的 RMSE 相对 `S3 composite predictor` 增加 `1389.7401`，比例约 `2.1077x`。这一差距仍应保留，并解释为“局部公式组合后的 transfer gap”，而不是只展示更好看的 predictor 结果。

### 5.6 答辩与中期汇报阶段的表达边界

1. 现在可以展示并强调：
   - direct 路线为何失败；
   - S2 如何证明失败原因；
   - S3 如何在保持精度的同时恢复关键物理量；
   - 当前论文里已经有公式与 KAN 的直接比较（direct symbolic vs direct KAN，以及各子任务 TGR）；
   - 由三条局部公式结构化组合得到的净负荷总公式已经生成，并已完成 test 复算。
2. 当前仍不能直接说：
   - “已经拿到最终净负荷单条公式，并且它优于组合预测器”
   - “S3 的局部公式可解释性和组合预测精度是同一个结果对象”
3. 当前更稳的说法是：
   - “已经拿到由三条局部公式结构化组合得到的净负荷总公式，并完成了 test 复算；但该总公式相对组合预测器仍存在明显 transfer gap，因此论文与答辩中必须并列呈现 predictor 与 formula 两个对象。”

## 6. 新版 KAN 性能优化导致的叙事偏移问题（2026-04-22 记录）

> **背景**：2026-04-19 在 Codex 协助下以"让 KAN 超过 LSTM"为目标优化 KAN 配置，结果 KAN 性能大幅提升，但同时发现优化后的 KAN 与论文初稿的核心叙事产生冲突。

### 6.1 发生了什么

在 Codex session `rollout-2026-04-19T12-13-32` 中，以"让 KAN 超过 LSTM"为目标，Codex 自主做了以下改动：
1. 新建 `src/kan_sr/feature_scaling.py`，给所有输入做 z-score 标准化
2. `include_base` 从 `False` 改为 `True`（加入 load/wind/solar 当前值）
3. `hidden_width` 从 `10` 改为 `32`
4. `sparsify_lamb` 从 `0.01` 降到 `0.0005`（20× 更弱）
5. `sparsify_lamb_entropy` 从 `2.0` 降到 `0.5`（4× 更弱）
6. `target_pruned_ratio` 从 `0.8` 降到 `0.0`（完全不要求剪枝）
7. `max_rmse_degrade_ratio` 从 `1.1` 降到 `1.01`
8. prune profile 从 `default`（起步 edge_th=0.01）改为 `gentle`（起步 0.0001）
9. 用户要求后加入 `lag_step=1`（1 小时短期 lag）

### 6.2 新版 vs 旧版的完整差异表

| 配置项 | 旧版 KAN | 新版 KAN | 影响 |
|--------|---------|---------|------|
| `include_base` | `False` | `True` | 旧版无 load/wind/solar 当前值，新版多了 5 个特征 |
| feature scaling | 无 | z-score | load ~40000 vs wind_speed ~5，不 scale 梯度被 load 主导 |
| 特征数 | 26 | 31（canonical）/ 34（lag1） | 新版多了 base 列 + 新工程特征 + lag_1 |
| `lag_steps` | [12, 24, 48] | [12, 24, 48]（canonical）/ [1, 12, 24, 48]（lag1） | lag1 版有 1 小时短期 lag |
| `hidden_width` | 10 | 32 | 3.2× 容量 |
| `sparsify_lamb` | 0.01 | 0.0005 | 20× 更弱的稀疏惩罚 |
| `sparsify_lamb_entropy` | 2.0 | 0.5 | 4× 更弱 |
| `target_pruned_ratio` | 0.8 | 0.0 | 旧版强制 80% 剪枝，新版不要求 |
| `max_rmse_degrade` | 1.1 | 1.01 | 新版对精度几乎零容忍 |
| `hidden_width_final` | 4 | 32 | 旧版 prune 后压缩到 4 节点 |

### 6.3 新版结果

**性能大幅提升：**

| 模型 | test RMSE | test R² |
|------|-----------|---------|
| 新版 KAN (scaled lag1) | 569 | 0.952 |
| 新版 KAN (scaled canonical) | 682 | 0.931 |
| LSTM warm_freeze | 1572 | 0.632 |
| MLP best (trial 3) | 1800 | 0.516 |

**但物理变量 feature importance 完全不同于旧版：**
- 旧版 direct KAN：31 个特征中只有 `load` 有 active_edges=6，其余全为 0（load-only collapse）
- 新版 canonical：31/31 特征全部激活，active_ratio 0.72-0.81
- 新版 lag1：34/34 特征全部激活，active_ratio 0.84-0.91

**Prune sweep 结果（lag1 版，已完成 `protocol_exec_20260420_ro00__prune_sweep`）：**

| edge_th | pruned_ratio | active_physical | test R² |
|---------|-------------|-----------------|---------|
| 0.0001 | 2.4% | 23/23 | 0.952 |
| 0.001 | 3.1% | 23/23 | 0.952 |
| 0.005 | 8.5% | 23/23 | 0.934 |
| 0.01 | 15.2% | 23/23 | 0.798 |
| 0.02 | 25.7% | 23/23 | 0.654 |

关键发现：**物理变量在所有剪枝水平下全部保留**（23/23），但最大 pruned_ratio 仅 25.7%，R² 已跌到 0.654。距离 symbolic extraction 需要的 80%+ 稀疏度差距巨大。

### 6.4 对论文叙事的冲击

**旧叙事的受损部分：**
- "direct KAN 连物理因素都学不进去" — 对新版不成立
- "direct KAN 的最终结构天然坍缩成 load-only" — 被证明是配置问题（无 scaling + 过度剪枝 + 网络太窄），不是 KAN 的固有限制
- 答辩时如被问"你试过 normalize 输入吗？"会很被动

**旧叙事仍然成立的部分：**
- "高性能 KAN predictor ≠ 可解释的物理公式" — 反而更强了
- S2 阻断实验 — 在旧配置下仍然成立
- S3 分解方案 — 价值不变

### 6.5 旧版设计的历史还原

经查 `.planning/`、`doc/optimization/`、`doc/kan_tuning_notes.md`、`doc/已尝试/` 等文档，**没有找到任何文档明确记录"为什么 `include_base=False`"的设计决策**。旧版配置的隐含逻辑是：

1. **`include_base=False`**：预测目标是 `delta_net_load_h6`（变化量），当前 load/wind/solar 原值被认为属于"等式左边的已知基线"而非输入特征。这个选择在理论上合理，但缺少对其他方案的对比验证。
2. **无 feature scaling**：pyKAN 教程和论文示例都是低维物理函数（2-5 个输入、量级相近），不存在 load~40000 vs wind_speed~5 的尺度问题。这是在高维真实数据上才暴露的工程盲点。
3. **`hidden_width=10` + `target_pruned_ratio=0.8`**：直接跟 pyKAN 教程走。Phase 2 成功标准写的是"80% edges pruned"，这个目标在 26 维真实数据上过于激进。
4. **`sparsity_lamb=0.01` + `entropy=2.0`**：跟 pyKAN 论文推荐值走。

**总结：旧版不是"故意设计成弱配置"，而是在高维、高噪声、强自回归的真实数据场景下，暴露了低维学术示例中不存在的工程问题。**

### 6.6 提议的新叙事方向

不改变论文大结构，把新结果前置作为引子：

1. **前人把 KAN 用成了黑盒**：文献中已有 MCKAN 等工作证明 KAN 在能源预测上有性能优势，但都只关注精度，未做 symbolic extraction（论文 Chapter 1.2 / 2.4 已有这个铺垫）
2. **新版 KAN 前置，确认性能优势**：展示 scaled + 宽网络 KAN 的性能碾压所有 baseline，且物理变量全部进入结构层
3. **论证"这条路到不了公式"**：用 prune sweep 的 Pareto 曲线证明不存在"既有好性能又足够稀疏"的中间态
4. **旧版架构作为"为可解释性的有意义妥协"**：窄网络 + aggressive pruning 牺牲性能换稀疏度，使 symbolic extraction 成为可能
5. **后续沿原有 S1/S2/S3 思路展开**

### 6.7 后续实验计划

#### 6.7.1 中间态搜索（关键实验，用于支撑"不可兼得"结论）

**目的**：在参数/架构空间里系统搜索，确认不存在一个 KAN 配置同时保有好性能和高稀疏度，从而把“predictor 性能提升”与“symbolic extraction 可行性不足”之间的张力，写成有实验支撑的 Pareto 结论，而不是主观判断。

**核心假设**：
1. 在与论文主线一致的 `no-base` 旧版任务设定下，加入 `feature scaling` 后，KAN predictor 的性能会显著改善，但结构仍不足以自动进入 `80%+` 剪枝、且保持小退化的 symbolic 区域。
2. 性能与稀疏度之间更接近连续权衡，而不是存在一个“稍微调一下就两者兼得”的隐藏最优点。
3. 如果右上角长期为空，则新版高性能 KAN 更适合被写成“性能上界与结构层可学到物理量”的证据，而不能直接当成可提公式的最终方案。

**实验协议**：
1. 固定数据与任务口径不变，保持与论文 S1/S2/S3 相同的 `delta_net_load_h6`、相同切分、相同 `no-base` 特征集。
2. 固定特征集为旧版 `26` 个输入：`include_base=False`，`lag_steps=[12,24,48]`。
3. 仅引入一个工程修正：`feature scaling`。不加入 `lag_1`，不恢复 `include_base=True`，避免把“任务协议变化”误写成“训练技巧有效”。
4. 宽度与稀疏惩罚做二维搜索：
   - `hidden_width`: `10, 16, 24, 32`
   - `sparsify_lamb`: `0.001, 0.005, 0.01, 0.02`
5. 其余配置默认先锁定旧版主协议，仅在必要时补一维小范围附加扫描：
   - `sparsify_lamb_entropy` 维持旧值；
   - prune profile 维持与旧版相同的 aggressive 路径；
   - 若二维搜索后出现边界点，再补 `target_pruned_ratio in {0.6, 0.8}` 做确认，而不是一开始就扩成大网格。

**记录指标**：
1. predictor 层：
   - `val/test RMSE`
   - `val/test R²`
   - `skill`
2. 结构层：
   - `pruned_ratio`
   - `active_edges`
   - `active_physical_features / total_physical_features`
   - 是否仍出现 `load-only` 或单一变量主导
3. symbolic 可提取层：
   - 在 `1%` 与 `5%` RMSE degradation 两个容忍阈值下的最大可剪枝比例
   - 对应配置是否能稳定进入 symbolic extraction 流程
   - 若能提公式，记录 `complexity`、`TGR` 与物理变量是否保留

**判定标准**：
1. 若某配置同时满足：
   - `test R²` 明显优于旧版 direct KAN，且
   - `pruned_ratio >= 0.8`，且
   - symbolic 提取后公式复杂度与 transfer gap 可接受，
   则“不可兼得”不能作为结论，后续应直接改写为“存在中间态配置”。
2. 若所有配置都表现为：
   - 高性能区集中在低剪枝比，
   - 高剪枝区性能快速崩塌，
   - 或虽可剪枝但 symbolic 公式不可用，
   则可以把“高性能 predictor 与可提取公式之间存在稳定张力”写成主结论之一。
3. 若出现少数边界配置接近右上角，但 seed 间波动很大，则结论应写成“存在候选中间态，但稳定性不足”，不能提前写成已经打通。

**交付物**：
1. 一张 `pruned_ratio - test R²` 的 Pareto 散点图。
2. 一张按配置排序的 summary table，至少列 `width`、`sparsify_lamb`、`best_pruned_ratio`、`test R²`、`symbolic_status`。
3. 若出现候选中间态，单独补一张 representative formula 表；若未出现，则保留“右上角为空”的主图即可。

#### 6.7.2 旧版架构性能优化

**目的**：如果最终论文仍以旧版窄网络 + aggressive pruning 作为“更接近可解释公式”的主工作点，则这个工作点的 predictor 性能至少要达到“明显优于旧版失败基线、且不至于被 LSTM 轻易压制”的水平，否则答辩时会被质疑为“为了公式而牺牲了过多预测有效性”。

**优化原则**：
1. 只做不改变主叙事的修正，不把 6.7.2 做成另一套新架构。
2. 优先保留 `no-base`、高剪枝目标、可进入 symbolic extraction 这三个核心约束。
3. 每次改动都必须回答一个清晰问题：是在修正工程缺陷，还是在改变任务本身。前者可以接受，后者不能混入主结果。

**候选优化项**：
1. 加 `feature scaling`，这是当前唯一几乎无争议、且已被新版结果证明必要的工程修正。
2. 将 `hidden_width` 从 `10` 小幅放宽到 `16` 或 `24`，观察是否能在不破坏稀疏化前提下提高 teacher 性能。
3. 微调 `grid` / `k` 等结构超参，优先寻找“同等剪枝率下更稳”的配置，而不是盲目追最高 `R²`。
4. 适度延长训练步数，检查旧版是否存在“还没收敛就被拿去 prune”的问题。

**明确不做的改动**：
1. 不引入 `include_base=True`。
2. 不引入 `lag_1`。
3. 不把 `target_pruned_ratio` 直接降到接近 `0`。
4. 不切换到新版宽网络 + gentle prune 的主路径，因为那会直接改变论文要论证的对象。

**验收条件**：
1. predictor 指标相对旧版 direct KAN 有可见提升。
2. 剪枝后仍能进入 symbolic extraction，而不是停留在“结构层全保留”的黑盒 predictor。
3. 提取出的公式不能再次退化为纯 `load`，至少要保持已有的“物理量可入式”特征。
4. 若性能提升来自明显更复杂的公式，需同步报告 complexity 与 TGR，不能只报 predictor 结果。

#### 6.7.3 实施顺序与收口规则

1. **先做 6.7.1，再决定 6.7.2 是否继续扩展。**
   - 如果 6.7.1 已经找到稳定中间态，则论文叙事应转向“存在可兼顾候选，但稳定性/复杂度仍需约束”，6.7.2 只做补充验证。
   - 如果 6.7.1 明确右上角为空，则 6.7.2 的任务就变成：为旧版可解释路径争取一个更体面的 predictor 下界。
2. **优先输出能直接进入论文的证据对象。**
   - 图表优先于零散 run；
   - summary table 优先于口头描述；
   - 若没有完成 Pareto 图与代表性配置表，就不算这一节真正闭环。
3. **所有结论必须按对象分层写。**
   - predictor 层说性能；
   - pruned structure 层说稀疏性；
   - symbolic formula 层说复杂度、物理变量保留和 transfer gap；
   - 不允许再把三层证据拼成一个“KAN 已经同时解决精度与解释性”的强结论。

**实验顺序**：先做 6.7.1；只有在 6.7.1 不能直接给出稳定收口结论时，再进入 6.7.2。

## 7. 审查报告筛选结论（2026-04-13）

### 7.1 质量排序（1 = 最值得信）

1. `gedt-1.md`
   - 最稳。紧扣现稿，能准确区分“证据链未闭合”和“主张可以成立但应降强度”，几乎每条批评都能落到当前论文修改上。
2. `gp-1.md`
   - 与 `gedt-1.md` 接近，尤其擅长把 `Case 4` 与 `S3` 的 artifact 混写问题讲清楚；质量很高，但个别措辞比 `gedt-1.md` 稍更审稿口吻。
3. `gp-1-gc.md`
   - 图表改造建议最贴近当前正文结构，能较好地区分“该保留的表”和“该改成图的证据点”，可执行性强。
4. `gpp-1-gc.md`
   - 对“图少表多、缺 split table、缺 protocol ledger、缺代表公式表”的判断有价值，适合作为图表层面的补充参考。
5. `gedt-1-gc.md`
   - 对“4 张核心图”的把握是对的，但有些表达偏顶会包装和展示导向，图型思路可用，具体包装不必照搬。
6. `gpp-1.md`
   - 排名最低。并非完全无用，但它把若干真实问题直接上升为“致命 flaw / 当前版本无法接收”这类过强定性；这些定性本身不直接进入正文口径，但对应的事实性问题仍应纳入后续修改。

### 7.2 可直接采纳的文字口径

1. `Case 4` 不能再写成已经严格闭合的机制证明。更稳的写法应是：阻断实验提供了支持 `shortcut competition` 的干预性证据，但由于 `unblocked` 与 `blocked` 当前统计对象和口径不完全同层，这一节应避免“唯一机制已被完全证明”的强表述。
   来源：`gedt-1.md`、`gp-1.md`
2. `S3` 不能把“局部公式的可解释性”和“组合预测器的精度”混写成同一个对象。即使现在已经补出 `S3 composite formula`，正文中也仍必须明确区分：
   - `三条局部公式 + 结构化组合预测器`
   - `由三条局部公式组合得到并已完成 test 复算的净负荷总公式`
   来源：`gedt-1.md`、`gp-1.md`、`gpp-1.md`
3. 当前主结论的边界应继续保持：
   - `KAN > PySR` 仅限当前 canonical 主实验设置；
   - `wind` 更适合写成“非单调”或“先增强、后减弱”，不要扩成稳定普遍规律；
   - 其他物理量只能写“更不稳定、部分减弱”，不要写成“持续下降”。
   来源：`gedt-1.md`、`gp-1.md`
4. `局限性` 一节可以保留“划分前插值带来非严格无泄漏问题”的记录，但不要直接把它升级成“足以推翻全文结论的致命缺陷”；更稳的做法是承认边界、避免把机制结论写得过强。
   来源：`gpp-1.md`（事实问题），结合现稿与代码核对
5. 需要补一段更明确的“证据对象说明”：哪些结果是 `teacher/composite predictor` 层面的，哪些是 `symbolic formula` 层面的，不能在讨论与结论里跨对象拼接成一个更强结论。
   来源：`gedt-1.md`、`gp-1.md`

### 7.3 可直接采纳的结构与图表改法

1. 当前正文确实存在“1 张图 + 大量表格”的问题，关键转折点仍主要靠读者自己扫表拼出来；这一判断可信，应采纳。
   来源：`gedt-1-gc.md`、`gp-1-gc.md`、`gpp-1-gc.md`
2. 最值得优先补的 4 张图是：
   - `direct symbolic collapse` 的特征族保留热图或 presence matrix，并配一个代表性坍缩公式；
   - `solar/wind` 可辨识性随任务或 horizon 变化的曲线图，突出 `solar` 正例与 `wind` 非单调边界；
   - `Case 3/Case 4` 的 paired plot / dumbbell plot / CI 图，用来可视化阻断前后变化；
   - `S3` 的结构图，把三条局部公式、组合规则和组合精度放进同一个视觉对象。
   来源：`gedt-1-gc.md`、`gp-1-gc.md`、`gpp-1-gc.md`
3. 应新增一张“代表性公式表”，至少并列展示：
   - `direct collapsed formula`
   - `load local formula`
   - `wind local formula`
   - `solar local formula`
   并附 `FAR / TGR / complexity` 等简表信息。
   来源：`gedt-1.md`、`gp-1.md`、`gpp-1-gc.md`
4. 一些表可以合并、下沉或转附录，尤其是：
   - `Case 3/Case 4` 的逐 seed 明细表；
   - `collapse` 的 9 行重复表；
   - 若正文版面紧，则“阶段性总结型表格”优先压缩。
   来源：`gp-1-gc.md`、`gedt-1-gc.md`
5. 建议新增一张“实验协议对齐表”，统一列清：
   - 目标变量；
   - 特征组；
   - lag 设置；
   - 统计单位是 `seed`、`symbolic config` 还是 `run`；
   - 评估对象是 `teacher`、`pruned structure` 还是 `symbolic formula`。
   来源：`gpp-1-gc.md`、`gp-1.md`

### 7.4 现稿核对后应顺手修掉的一致性问题

1. 已确认真实切分口径来自代码：`TRAIN_RATIO=0.7`、`VAL_RATIO=0.15`，即 `70/15/15 + 48步gap`。第三章、第五章、主文件与流程图已统一到这一口径。
   来源：代码核对 `src/config.py`、`src/data/split.py`
2. 报告中提到的 `26/28` 维、`lag_1` vs `lag_12/24/48`、扩展函数库定义不清等问题，确实属于此前“协议文本未完全冻结”的信号；本轮已经统一扫过主稿、章节稿和 `thesis_draft` 的核心表述，当前不再作为阻塞项。
   来源：`gp-1.md`
3. `Case 4` 已经按 canonical `no-base` direct-task 口径重跑并收齐 3 对 paired seed；但由于效应量仍偏弱且波动明显，正文和答辩口径仍应把它写成支持 `shortcut competition` 的干预性证据，而不是最硬的一条机制证明。
   来源：`gedt-1.md`、`gp-1.md`

### 7.5 采纳原则（改成按属实与否，不按难度）

1. 后续是否纳入修改，只看一条：该判断或其对应问题是否属实。
2. 只要与代码、实验资产、现稿核对后属实，就进入后续改动清单；区别只在于分阶段推进，而不是简单标成“不采纳”。
3. 需要区分两类内容：
   - 事实性问题：例如 `Case 4` 口径未完全对齐、`S3 predictor` 与 `S3 formula` 容易被混写、当前存在划分前插值、当前只有单数据集/有限 seed/有限 baseline。这些若属实，全部纳入后续修改。
   - 结论性定性：例如“这是致命 flaw”“当前版本无法接收”。这类属于外部评审口吻，不直接照抄进论文正文；但其背后对应的事实性问题，仍按上条纳入处理。

### 7.6 分阶段纳入清单

1. 第一阶段：口径与一致性修正
   - 【已于 2026-04-17 完成】已统一 `main.tex` / `chapters/*.tex` / `thesis_draft` 中的 `S3` 总公式闭环口径、`Case 4` 边界说明、`PySR=0.076`、`strict/medium/strict_poly4` 函数库定义与旧的 `load_lag_1` 残留表述；并已根据 canonical `no-base` 的 Case 4 direct-task paired 结果下调相关结论强度：当前 3 对 final-pred seed 的 `blocked - unblocked` RMSE 分别为 `+53.05`、`+470.44`、`+214.82`，均值 `+246.10`，方向一致但强度有限。
   - 统一数据切分、特征维度、lag 记法、函数库定义等协议文本。
   - 收紧 `Case 4`、`S3`、`KAN > PySR`、`wind 非单调` 等结论强度。
   - 明确区分 `teacher/composite predictor` 与 `symbolic formula` 两类证据对象。
   来源：`gedt-1.md`、`gp-1.md`、代码核对 `src/config.py`、`src/data/split.py`
2. 第二阶段：正文证据呈现补齐
   - 【已于 2026-04-17 完成】已新增 `protocol_ledger_20260417.csv`、`representative_formula_table_20260417.csv`、`direct_symbolic_collapse_20260417.png`、`wind_solar_horizon_20260417.png`、`s2_blocking_summary_20260417.png`、`case4_matched_blocking_seed_detail_20260417.csv`、`case4_matched_blocking_summary_20260417.csv`，并已接入主稿 `main.tex` 与章节版 `chapter4.tex/chapter5.tex`。
   - 增加 `split/protocol ledger`、代表性公式表、关键对比图。
   - 把当前最重要的证据链从“主要靠表格扫描”改成“图表与表格共同支撑”。
   - 明确把 `S3` 写成“`三条局部公式 + 结构化组合预测器 + 已复算总公式`”，并在正文中区分 predictor 与 formula 两个对象。
   来源：`gedt-1-gc.md`、`gp-1-gc.md`、`gpp-1-gc.md`、`gedt-1.md`、`gp-1.md`
3. 第三阶段：实验与工程闭环补强
   - 【已于 2026-04-17 完成】显式构造 `S3 composite formula` 并完成 test 逐点复算。
   - 【已于 2026-04-17 完成】已补做 `Case 4` 的 canonical `no-base` direct-task 对照；结果显示 3 对 paired seed 在 final-pred 口径下均为 blocked 更差，但效应量仅属弱到中等支持，因此正文不再保留旧的 `+0.80 / 强成功` 口径。
   - 【已于 2026-04-17 转入独立后处理】`wind/solar` 更深的 full-grid symbolic 提取不再作为当前 `next` 的完成条件。原因是 symbolic 提取运行在 Modal 上、单次 job 受 `2h` 限制，且现有公式复杂度已经偏高；后续若要继续加强，可由人工单独筛选与重跑。
   - 若继续加强外部说服力，则补充更多 baseline、seed、以及额外数据/区域验证；这些现在归入长期证据增强项，不再视为本轮 `next` 清单的未完成项。
   来源：`gedt-1.md`、`gp-1.md`、`gpp-1.md`
4. 图表层面的建议也按同样规则处理：
   - “需要把坍缩、恢复、S3 出路可视化”这一判断属实，应纳入第二阶段。
   - 具体图型如 `Sankey`、拓扑炫图、特定绘图库风格是否采用，不按”建议里写了什么”决定，而按是否服务于事实表达决定；若只是包装而不增加证据表达，就不作为优先项。
   来源：`gedt-1-gc.md`、`gp-1-gc.md`、`gpp-1-gc.md`

## 8. 6.7 中间态搜索阶段性结果与叙事修正（2026-04-22 更新）

### 8.1 已发现的中间态候选：w16_l0p001

- run: `kan_67_execution__kan67_train_w16_l0p001`
- `status = completed`
- `test RMSE = 1296.5795`，`test MAE = 858.4613`，`test R² = 0.74897`
- `pruned_ratio = 0.83046`（训练内 prune 候选：`node_th=0.01, edge_th=0.05`）
- `active features = 21/28`，`active physical features = 15`
- 保留的代表性物理变量：`wind_speed_10m_m_s`、`ghi_w_m2`、`ghi_day_w_m2`、`solar_altitude`、`solar_azimuth`、`is_night`，以及多个 `wind_lag_*` / `solar_lag_*`
- 外部 prune sweep（`kan_67_execution__kan67_prune_w16_l0p001_rerun`）已确认该候选点稳定

**这条结果直接推翻了 6.7.1 原假设中”右上角为空”的临时判断。** 但它仍然只是 predictor/pruned-structure 层面的证据，不等于已经有可用的 symbolic formula。

### 8.2 w10 已完成子集汇总

| 配置 | test R² | pruned_ratio | 状态 |
|------|---------|-------------|------|
| w10_l0p001 | -0.333 | 0.40 | 性能不可用 |
| w10_l0p005 | 0.718 | 0.47 | 性能可接受但稀疏度不足 |
| w10_l0p01 | 0.443 | 0.16 | 性能与稀疏度均不足 |
| w10_l0p02 | -6.801 | 0.21 | 完全失败 |

w10 子集中没有出现”高性能 + 0.8 以上稀疏度”的候选。

### 8.3 叙事修正：从”不存在”改为”存在但有缺陷”

原计划的 6.7.1 结论是”不存在中间态”，当前必须修正为：

**中间态在 predictor/pruned-structure 层存在，但有以下明确缺陷：**
1. 性能代价显著：R² 从 0.952（全性能 KAN）降至 0.749，降幅约 21%
2. active features 仍有 21/28，结构密度远高于 S3 局部任务的 ~5-8 个特征
3. symbolic extraction 尚未完成：21 个 active features 做提取大概率产生高复杂度公式
4. S3 composite predictor（RMSE=1254.62）仍优于该候选点（RMSE=1296.58）

因此叙事第三步应改为：
> “中间态搜索发现候选点（w16, λ=0.001），pruned_ratio 达 0.83 且保留 15 个物理变量。但该候选点性能显著下降（R² 0.75 vs 0.95），且剪枝后仍有 21 个 active features，结构密度不足以支撑简洁的符号提取。”

### 8.4 关于 feature scaling 与公式坍缩的两难关系

6.7 网格的 w10 子集已经暴露了一个关键的两难：

1. **无 scaling（旧版）**：load 梯度主导 → 训练可以达到 0.8+ 剪枝比 → 但公式坍缩为 load-only
2. **有 scaling（6.7 网格）**：梯度均衡、物理变量全部激活 → 但 w10 最高只能到 0.47 剪枝比，不够稀疏做提取

这说明坍缩不只是”工程缺陷的下游后果”这么简单——**修了 scaling 丢稀疏度，保了稀疏度但坍缩**。这个两难本身就是 S3 分解方案的真正动机：把任务拆开后，每个子任务既不需要极端稀疏度，也不会被 load 主导。

**对论文的影响：**
- 不需要再”证明加了 scaling 还坍缩”（这可能不成立）
- 也不需要”证明中间态完全不存在”（已被 w16_l0p001 推翻）
- 应把两难本身写成发现，然后自然引出 S3

### 8.5 高性能 KAN symbolic extraction 已终止

- app `ap-4xF12vE5xJUp7u0nYbe5BE` 已 `stopped, Tasks=0`
- 根因不是公式提取逻辑错误，而是 **Modal 运行时 heartbeat 超时**（反复出现 `ConnectionError('Deadline exceeded')`）
- `modal_jobs/kan_symbolic.py` 三个入口均未配 `retries=`，不是业务重试
- 关键产物（`formula_eval_val.json`、`formula_eval_test.json`、`physics_mapping.json`）均未生成
- **结论：高性能 KAN 的 symbolic extraction 不适合在当前 Modal 配置下等待结果，转为后续独立处理**

### 8.6 当前待完成实验与下一步

**6.7 网格剩余状态：**
- `w10 × 4`：全部完成 ✅
- `w16_l0p001`：完成 ✅（强中间态候选）
- `w16 × {0.005, 0.01, 0.02}`：待同步
- `w24 × 4`：待同步
- `w32 × 4`：待同步
- prune sweep：已提交 `w10 × 4` 和 `w16_l0p001`

**行动项（按优先级排序）：**

#### A1. 同步剩余 train run 并画 Pareto 图（阻塞论文收口）

1. 继续通过 `modal volume ls/get` 同步剩余 12 个 train run（w16 剩余 3 + w24×4 + w32×4）
2. 对所有已完成 run 提取 `test R²` 和 `pruned_ratio`
3. 画一张 `pruned_ratio (x) - test R² (y)` 散点图，按 `hidden_width` 着色
4. 结论口径从”右上角为空”改为”右上角有候选（w16_l0p001）但有明确缺陷（21 active features、R² 降至 0.75）”
5. **交付物**：Pareto 散点图 PNG + summary table CSV，落盘到 `doc/thesis_sweeps/kan_67_execution/`

#### A2. Modal heartbeat 超时问题修复（阻塞后续 symbolic extraction）

**问题**：`kan_symbolic.py` 的三个入口虽然配了 `timeout=24h`，但在长时间 CPU-bound 计算中 Modal client-worker heartbeat 反复 `Deadline exceeded`，导致任务看似在运行但无法完成。app `ap-4xF12vE5xJUp7u0nYbe5BE` 已手动终止。

**根因**：pyKAN 的 `auto_symbolic()` 对每条 active edge 逐一尝试候选函数库，21 个 active features 的模型计算量极大，期间无任何 I/O 或 volume 交互，Modal 运行时误判连接已死。

**候选修复方案（按侵入性从低到高）：**
1. **在 symbolic 循环中加 periodic `volume.commit()`**：每处理完一条 edge 后做一次 volume commit，既能 checkpoint 进度、也能保持 Modal 心跳活跃。侵入性最低，优先尝试。
2. **加 `retries=1`**：如果 heartbeat 真的杀死了 worker，至少能自动重启一次。但由于没有 checkpoint，重启后从头开始，浪费计算。应与方案 1 配合使用。
3. **缩减候选函数库**：对 21 个 active features 的模型，默认函数库（含 `exp`、`log`、`sqrt`、`tanh` 等）组合爆炸。可限制为 `['x', 'x^2', 'x^3', 'sin']` 等小函数库，降低单次提取耗时。
4. **拆分提取为 per-layer 子任务**：把 `auto_symbolic()` 拆成按 layer 分步提取，每层完成后落盘，下一层从 checkpoint 继续。侵入性最高但最彻底。

**建议**：先实施方案 1 + 2，观察是否足以让 w16_l0p001 的 symbolic extraction 在 Modal 上跑完。若仍超时，再补方案 3。

#### A3. w16_l0p001 的 symbolic extraction（A2 完成后执行）

- 在 A2 修复后对 w16_l0p001 执行 symbolic extraction
- 预期该候选点因 21 个 active features 会产生高复杂度公式
- 记录 `complexity`、`TGR`、物理变量保留情况
- 若公式不可用（过于复杂或 transfer gap 过大），直接写成”中间态在 formula 层不可行”的闭环证据

#### A4. 旧版 KAN + scaling 分析（已有数据，无需新实验）

- 6.7 网格 w10 子集（见 8.2）已经是”旧版 KAN + scaling”的结果
- 当前结论：性能改善但稀疏度全面下降（最高 0.47），无法达到 0.8 剪枝目标
- 这个结论将直接写入 Pareto 图的解读中，无需单独跑实验

## 9. 完整 Pareto 数据与净负荷空间转换（2026-04-22）

### 9.1 数据来源

- **6.7 网格 16 cell（已全部完成）**：`runs/kan_67_execution__kan67_train_w{10,16,24,32}_l{0p001,0p005,0p01,0p02}/payload.json`
- **Ceiling run**：`runs/kan_67_execution__kan67_train_ceiling_w32_l0p0005_v2/payload.json`
- **旧版 KAN 与 baseline**：`doc/thesis_sweeps/paperref_20260306_121725_v2/paper_assets/comparison_table.csv`
- **LSTM baseline**：`doc/thesis_sweeps/protocol_exec_20260419_ro00_baseline_family_refresh/` 目录下的 payload

### 9.2 净负荷空间转换方法

由于预测目标是 `delta_net_load_h6`，重建净负荷预测时 `net_load_hat = net_load_t + delta_hat`，每个样本加了一个常数。因此：
- **RMSE 在 delta 空间和净负荷空间完全相同**
- **R² 不同**，因为分母（总方差）不同：`R²_net = 1 - RMSE² / var(net_load_test)`
- 由旧版 KAN 反推：`var(net_load_test) = 2588.41² / (1 - 0.9701) ≈ 224,076,000`

### 9.3 特征集不一致问题（2026-04-22 发现）

在对比 6.7 网格与论文基线时，发现存在**三套不同的特征集**，源于 `derive_dataset` 管线在不同时间点的演化：

| 数据源 | 日期 | 特征数 | `hub_est` | `temp_corr` | 使用者 |
|--------|------|--------|-----------|-------------|--------|
| `2026_03_01_142726…derived_h1_6_12_24` | 3月1日 | **26** | ❌ | ❌ | 论文基线 KAN（`2026-03-01_151000_kan_nobase_nogrid_gpu`） |
| `paperref_20260306_121725…derived_h1_6` | 3月6日 | **28+** | ✅ | ✅ | paperref_v2 的 S1（31维，含base）、S3 子任务（11-15维，按需选子集） |
| `protocol_exec_20260419_ro00…derived_h1_6` | 4月19日 | **28** | ✅ | ✅ | 6.7 网格全部 16 cell + ceiling |

新增的两个特征：
- `wind_speed_hub_est`：幂律风廓线外推到 100m 轮毂高度（`v_hub = v_10m × (100/10)^0.14`）
- `ghi_temp_corr_w_m2`：温度修正 GHI（`ghi × (1-0.004×(T-25)) × daytime`）

这两个特征是为了让物理量更容易进入公式而后期加入的（见 `plan_kan.py`：”目的：让 wind_speed_hub_est / ghi_temp_corr_w_m2 等物理量保住激活边”）。

**影响**：
- 6.7 网格（28维）与论文基线（26维）不在同一特征集上，不能直接做绝对值对比
- 6.7 网格内部是一致的（都是 28 维），Pareto 图本身有效
- S3 各子任务使用了 3 月 6 日数据源中的新特征（wind 用了 hub_est，solar 用了 temp_corr）
- comparison_table.csv 中的 s1（RMSE=2588.41）使用的是 3 月 6 日数据源（31维，含 base），与论文第五章引用的 3 月 1 日 run（RMSE=1413.51，26维）是完全不同的 run

### 9.4 论文基线复现验证

为确认论文数字可靠，用论文原始 26 维数据源重跑了完全相同的配置：

**复现 run**：`kan_67_execution__kan67_repro_thesis_26dim`
**数据源**：`2026_03_01_142726_9ab14f0b__derived_h1_6_12_24`（26维）
**配置**：`w10, grid=5, k=3, λ=0.01, entropy=2.0, no scaling, no include_base, target_pruned_ratio=0.8, default prune profile`

| 指标 | 本次复现 | 论文 run | 差异 |
|------|---------|---------|------|
| test RMSE | **1403.0** | **1413.5** | -0.7% |
| pruned_ratio | **0.803** | **0.827** | 接近 |
| total_edges | 81 | 81 | 一致 |
| unpruned RMSE | 1418.3 | — | — |

**结论：论文数字可复现。** RMSE 差异在随机性范围内（0.7%），剪枝比也都过了 0.8。

**对比 28 维重跑的失败**：用 28 维数据（`protocol_exec_20260419_ro00`）重跑同一配置时，pruned_ratio 仅 0.319，远未达标。说明**多出的 2 个物理特征显著改变了剪枝动态**——26 维下模型能自然稀疏化到 80%，28 维下模型更难稀疏化。

| 重跑配置 | 特征数 | test RMSE | pruned_ratio | 备注 |
|---------|--------|-----------|-------------|------|
| 26 维（论文数据源） | 26 | 1403.0 | **0.803** | ✅ 复现成功 |
| 28 维 grid=5（4月数据源）| 28 | 1248.2 | 0.319 | ❌ 稀疏度不足 |
| 28 维 grid=3（4月数据源）| 28 | 1584.4 | 0.218 | ❌ 稀疏度不足 |

### 9.5 论文基线的真实性能

论文第五章的 KAN 基线来自 `2026-03-01_151000_kan_nobase_nogrid_gpu`（26维，无 scaling），**不是** comparison_table.csv 中的 paperref_v2 s1 run（31维，含 base，RMSE=2588）。两者是完全不同的 run：

| | 论文基线 KAN | comparison_table s1 |
|--|------------|-------------------|
| run_id | `2026-03-01_151000_kan_nobase_nogrid_gpu` | `paperref_20260306_121725_v2__s1_delta_net_load_h6` |
| 数据源 | 3月1日（26维） | 3月6日（31维，含base） |
| RMSE | **1413.5** | **2588.4** |
| skill | **0.453** | -0.00003（坍缩） |
| pruned_ratio | 0.827 | 0.938 |
| 状态 | 正常工作 | load-only 坍缩 |

论文基线 KAN（RMSE=1413）远优于 persistence（2585），**已经显著优于 LSTM（约2590）**。

### 9.6 全模型净负荷空间对比表（修正版）

RMSE 在 delta 和净负荷空间相同（重建只加 per-sample 常数）。R² 转换公式：`R²_net = 1 - RMSE² / var(net_load_test)`，其中 `var(net_load_test) ≈ 224,076,000`（由论文基线反推）。

| 配置 | 特征数 | RMSE | 净负荷 R² | pruned_ratio | 数据位置 |
|------|--------|------|----------|-------------|---------|
| ceiling w32 λ=0.0005 | 28 | 1149.5 | 0.9941 | 0.753 | `runs/…ceiling_w32_l0p0005_v2` |
| w24_l0p001 | 28 | 1251.4 | 0.9930 | **0.833** | `runs/…w24_l0p001` |
| S3 composite pred | 混合 | 1254.6 | 0.9930 | — | `comparison_table.csv` |
| w16_l0p001 | 28 | 1296.6 | 0.9925 | **0.830** | `runs/…w16_l0p001` |
| **论文基线 KAN** | **26** | **1413.5** | **0.9911** | **0.827** | `runs/2026-03-01_151000…` |
| 复现验证 | 26 | 1403.0 | 0.9912 | 0.803 | `runs/…repro_thesis_26dim` |
| MLP（论文） | 26 | 1474.4 | 0.9903 | — | 论文 chapter5 |
| persistence | — | 2585.7 | 0.9702 | — | 论文 chapter5 |
| LSTM best | — | ~2590 | ~0.9701 | — | baseline refresh |

**注意**：6.7 网格（28维）与论文基线（26维）不在同一特征集上。6.7 网格内部对比有效，但与论文基线做绝对值对比时需标注差异。

### 9.7 待决定事项

1. **特征集统一问题**：
   - 6.7 网格（28维）的 Pareto 图内部一致，可直接使用
   - 若需要和论文基线（26维）做严格对比，需用 26 维数据源补跑关键点（ceiling + 1-2 个中间态）
   - 或在论文中标注特征集差异，解释多出的 2 个物理特征的目的和影响
2. **论文第五章的 G=3 表述需修正**：实际 run 使用 `grid=5`，不是论文文本写的 `G=3`
3. **comparison_table.csv 与论文第五章数字不一致**：需明确论文最终引用哪一组数字（3月1日 run 还是 3月6日 paperref_v2）

### 9.8 工作优先级（更新后）

1. **实验收口**：
   - 画 Pareto 图（A1，6.7 网格 28 维数据已齐）
   - 修 Modal heartbeat 问题（A2）
   - 中间态 symbolic extraction（A3，依赖 A2）
2. **协议对齐决策**：确定论文最终使用哪套数据源、哪套特征集作为统一基准
3. **论文撰写**：所有实验和协议问题收口后再统一修改正文
