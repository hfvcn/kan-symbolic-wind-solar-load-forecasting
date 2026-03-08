# 论文交付收口（2026-03-06）

## 1. 一句话主命题

在 multi-horizon 设定下，稀疏 KAN 与符号提取能够从历史量与物理代理量中抽取可复算的解析关系；物理量能否进入最终结构并不是“有没有信息”的单因素问题，而主要由特征竞争与稀疏/剪枝轨迹共同决定。

## 2. 结论冻结

### 主结论

1. `delta_net_load_h6` 重建到 abs(test) 后，主结果 run `2026-03-01_151000_kan_nobase_nogrid_gpu` 的 RMSE=1413.51、skill=0.453，优于预算对齐 MLP `2026-03-01_155600_baseline_mlp_match_kan151000` 的 RMSE=1474.38、skill=0.430，也显著优于 persistence（RMSE=2585.66）。
2. 符号提取链路已经具备“可复算、可渲染、仍保持正 skill”的论文最低可用性；`2026-03-01_160200_sym_strict_r2_0_995__kan151000` 在 abs(test) 上 RMSE=2388.46、skill=0.076，但精度明显弱于 teacher。

### 副结论

1. Solar 侧的机制是“条件边际贡献 + 剪枝轨迹敏感”：
   - `h=72` 时 `both` 最优，且 `ghi_edges=8`；
   - `h=576` 时 `meteo_only` 最优，说明长尺度更依赖气象代理；
   - `h=144` 时 `both` 更差且 `ghi_edges=0`，构成“竞争导致外生量退式”的反例。
2. Wind 侧的机制是“风速边入式非单调，而不是简单的 horizon 越长越无效”：
   - `h=72`：abs(test) skill=0.588，但 `wind_speed_edges=0`；
   - `h=144`：abs(test) skill=0.354，且 `wind_speed_edges=9`；
   - `h=576`：abs(test) skill=0.203，`wind_speed_edges=0`。

### 边界结论

1. `delta_solar_h288` 是明确失败模式：`2026-03-04_101610_37271ac2` 的 abs(test) RMSE=45568.69、skill=-7.628，且重建后 `abs_pred < 0` 比例达到 67.45%。
2. 对该反例做最小 clip 修复只能把 RMSE 降到 10678.50，skill 仍为负，因此 clip 只能作为风险缓解，不构成性能改进结论。

## 3. 贡献点冻结

1. 形成了从 KAN teacher、符号公式、物理映射到论文资产输出的可复现闭环，且主结果对 matched MLP 与 persistence 有明确优势。
2. 用对称的 solar / wind 机制表说明“物理量入式/退式”主要受特征竞争与剪枝轨迹影响，而不是简单地把外生量判为无效。
3. 把 `delta_solar_h288` 的长 horizon 崩坏转化为论文边界结论，明确指出 ex post explanatory setting 下的越界风险。
4. 给出精度-复杂度取舍的正式证据：teacher KAN、matched MLP、strict symbolic 三者可直接在同一张主结果表与 Pareto 图中比较。

## 4. Claim 强度表

| 强度 | claim | 证据 |
|---|---|---|
| 强说 | `delta_net_load_h6` 上 KAN 优于 matched MLP 与 persistence | `doc/paper_assets/paper_delivery_20260306/comparison_table.csv` |
| 强说 | 符号链路已具备“正 skill + 可复算公式”的最低论文可用性 | `doc/paper_assets/paper_delivery_20260306/comparison_table.csv` + `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/formula_eval_test.json` |
| 强说 | Solar 的 GHI 入式受 horizon 与竞争关系共同影响 | `doc/solar_ablation_summary_20260304.csv` |
| 弱说 | Wind 的风速边在 `h=144` 可回归结构，但在 `h=72/576` 退式 | `doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv` |
| 边界 | `delta_solar_h288` 发生外推崩坏，clip 只能缓解不能扭转结论 | `doc/paper_assets/paper_delivery_20260306/solar_h288_boundary_20260306.json` |

## 5. 主实验矩阵冻结

| 模块 | 目标 | horizon | 证据来源 | 正文定位 |
|---|---|---:|---|---|
| 主结果 | `delta_net_load_h6` -> abs(test) | 6 | `doc/paper_assets/paper_delivery_20260306/comparison_table.csv` | 主表 |
| 机制验证 Solar | `delta_solar_h72/h144/h576` | 72/144/576 | `doc/solar_ablation_summary_20260304.csv` | Solar 机制表 |
| 机制验证 Wind | `delta_wind_h72/h144/h576` | 72/144/576 | `doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv` | Wind 机制表 |
| 边界反例 | `delta_solar_h288` | 288 | `doc/paper_assets/paper_delivery_20260306/solar_h288_boundary_20260306.json` | 失败模式 |
| 复杂度-精度 | KAN / matched MLP / symbolic | 6 | `doc/paper_assets/paper_delivery_20260306/pareto_rmse_vs_complexity.png` | 讨论章节 |

指标口径冻结：

1. 预测指标统一使用 abs(test) 的 RMSE / R² / skill。
2. KAN 复杂度使用 `edge_pruned_ratio`，symbolic 复杂度使用 `sympy_node_count`，baseline 复杂度使用 `param_count`。
3. delta 口径只作为机制诊断附加信息，不进入正文主表。

## 6. Run 白名单

| 用途 | run_id / 资产 | 备注 |
|---|---|---|
| 主结果 KAN | `2026-03-01_151000_kan_nobase_nogrid_gpu` | 主结果 teacher |
| 主结果 baseline | `2026-03-01_155600_baseline_mlp_match_kan151000` | 预算/特征对齐 MLP |
| 主结果 symbolic | `2026-03-01_160200_sym_strict_r2_0_995__kan151000` | strict symbolic 公式 |
| Solar 机制 | `2026-03-04_120745_b455d7bc` / `2026-03-04_120746_93a46524` / `2026-03-04_120749_01834d3e` | `h=72` 的 both / lags-only / meteo-only |
| Solar 机制 | `2026-03-04_121143_49a2af36` / `2026-03-04_121143_04bfbfc0` / `2026-03-04_121145_74997b1b` | `h=144` 的 both / lags-only / meteo-only |
| Solar 机制 | `2026-03-04_121144_d6b684d1` / `2026-03-04_121143_c00221d5` / `2026-03-04_121142_9dd9aa4a` | `h=576` 的 both / lags-only / meteo-only |
| Wind 机制 | `2026-03-03_183052_4888ee22` / `2026-03-03_183731_c56e2dad` / `2026-03-03_185031_6242fd21` | `h=72/144/576` |
| Wind 对照 | `2026-03-03_182435_d7339689` | `h=6` 短期对照 |
| 边界反例 | `2026-03-04_101610_37271ac2` | Solar `h=288` 崩坏样本 |

## 7. 正文引用建议

1. 摘要与答辩首页只引用第 2 节冻结后的主命题、主结论和边界结论，不再引入额外说法。
2. 正文主表只使用第 6 节白名单中的 run 与资产。
3. 若需要解释“为什么物理量有时不入式”，优先引用 Solar `h=144` 与 Wind `h=72/144/576` 的组合证据，而不是泛化成单一规律。

## 8. 2026-03-09 收口补充

### 统计显著性

1. 主结果 paired 显著性已补齐，资产见 `doc/paper_assets/paper_delivery_20260306/paired_significance_main_20260309.csv`。
2. 在 abs(test) 的绝对误差口径上，KAN 相对 matched MLP 的 mean diff = 111.13，95% bootstrap CI = [100.42, 122.29]，置换检验 `p=0.0005`。
3. 在同一口径上，KAN 相对 strict symbolic 的 mean diff = 903.64，95% bootstrap CI = [882.04, 926.20]，置换检验 `p=0.0005`。

### 条件分层误差

1. Net-load 主结果在高波动切片上误差显著放大：KAN 的 high-volatility RMSE=1960.77，而 low/mid 仅为 1033.19 / 1045.59；这说明方法的主要风险集中在大幅跃迁段。
2. Solar 条件分层见 `doc/paper_assets/paper_delivery_20260306/solar_stratified_error_20260309.csv`：`h=72 both` 在日间 RMSE=5285.63、夜间 RMSE=3568.13；`h=144 both` 的日夜与 GHI 三分位都明显退化，和 “competition 导致外生量退式” 的机制结论一致。
3. Wind 条件分层见 `doc/paper_assets/paper_delivery_20260306/wind_stratified_error_20260309.csv`：`h=72` 在三个风速分位都保持正向表现，但 `h=576` 在 low-wind 分位出现最强退化（R²=-4.11），说明长 horizon 失效集中在低风速区间。

### Direct S0 结果

1. direct teacher S0 的远端同步巡检见 `doc/thesis_sweeps/paperref_20260309_direct_fullflow_s0_cloud/direct_sync_status_20260309.csv`：11 个 run 中仅 `20260309_modal_direct_fullflow__sym_strict_r2_0_99_fast5k` 有可见 artifacts。
2. 该 fast5k run 经本地重建后，abs(test) RMSE=3797.18、skill=-0.466、complexity=433，评估资产见 `doc/paper_assets/paper_delivery_20260306/direct_teacher_fast5k_assessment_20260309.csv`。
3. 结论是 direct S0 在当前 teacher 上未找到满足“稳定/可复算/正 skill”的配置，因此保留为失败证据，不进入正文正向 claim。

### 图表与 Future Work 冻结

1. 最小图表集合已补齐到 `doc/paper_assets/paper_delivery_20260306/`，新增包括 `system_flow_pipeline.png`、`solar_h288_boundary_20260306.png`、`successful_formula_summary_20260309.csv`、`formula_2026-03-01_160200_sym_strict_r2_0_995__kan151000.png` 以及 S3 子公式渲染图。
2. “更多 baselines / 更多 horizons”、“更强物理约束”、“架构创新” 已正式降级为 future work；当前主实验矩阵已经足以支撑论文主命题，不再扩展正文实验范围。
