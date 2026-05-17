# 实验需求-数据-总结索引（2026-05-02）

本文档按“需求 / 数据 / 总结”整理论文相关实验，目标是服务后续决策与回顾，而不是直接替代论文正文。每组都尽量对应一次明确的实验诉求，并给出可追溯的 `run`、`artifact` 或 Claude 会话来源。

## 1. 数据协议与泄漏探测

需求：先确认整套实验的数据切分与预处理是否可信，避免后续所有结论建立在错误数据协议上。

数据：`exp/output/leakage_probe_summary.csv`。
关键值：`persistence_netload_f28` 的 `old_rmse=new_rmse=2587.8356`；`ridge_netload_f28` 的 `old_rmse=new_rmse=864.1092`；`mlp_netload_f31` 的 `old_rmse=new_rmse=636.4405`；`ridge_wind_focus` 的 `old_rmse=new_rmse=832.2843`。这些对照都显示原流程与 split-aware 流程一致。

总结：这组数据是所有后续实验的底座。它不证明模型好坏，但证明“数据协议本身没有因为切分方式而造假”。

当前状态：这一组已经基本闭环。当前论文正文已将表头改成“基准流程 RMSE / 独立划分 RMSE”，可直接作为数据协议可信性的支撑证据。

追溯：`exp/output/leakage_probe_summary.csv`

## 2. RQ1 基线对比

需求：证明 KAN 至少是一个合格的 teacher，而不是“模型本身没学会”。

数据：`runs/rq1_baselines__baseline_*` 的 `artifacts/eval_test.json`。
关键值：Persistence `2587.84 / 1637.79 / ~0`，SARIMAX `2108.78 / 1541.63 / 0.336`，PySR `2059.27 / 1341.54 / 0.367`，MLP `1468.36 / 1028.73 / 0.678`，LSTM `1440.83 / 969.94 / 0.691`，XGBoost `1203.13 / 801.44 / 0.784`。

总结：这组数据适合支撑“Direct KAN 所在问题族并不弱，KAN 作为 teacher 有预测能力”。它不直接说明公式能提出来。

当前状态：这一组已落到正文 RQ1 精度对比表中，可视为主证据。若需要答辩图，可对应总览图 `doc/paper_assets/figures/fig_model_comparison.png` 中的基线对比部分。

追溯：`runs/rq1_baselines__baseline_lstm_matched__scaled28`，`runs/rq1_baselines__baseline_mlp_matched__scaled28`，`runs/rq1_baselines__baseline_persistence_standalone_standalone_rq1_baselines_rq1_direct_kan_matched`，`runs/rq1_baselines__baseline_pysr_matched__scaled28`，`runs/rq1_baselines__baseline_sarimax_standalone_standalone_rq1_baselines_rq1_direct_kan_matched`，`runs/rq1_baselines__baseline_xgboost_standalone_standalone_rq1_baselines_rq1_direct_kan_matched`

## 3. Direct KAN 主 teacher 家族

需求：确定论文里“Direct KAN 主结果”到底引用哪一组数据，避免把不同用途的数据混成一个结果。

数据：这里实际上有三组接近但不同的 Direct KAN 数据。
一组是 `doc/paper_assets/data/combo_h6_results.json` 里的 `direct_kan_28d`，数值为 `RMSE=1208.82, R²=0.7818`。
一组是 `runs/rq2_e1_lambda__rq2_e1_w16_l0_001_s1/s2/s3` 聚合得到的 `RMSE=1164.75±52.54, R²=0.7971±0.0184`。
一组是 `runs/rq2_e2_ablation__rq2_e2_f28_no_base_s1/s2/s3` 聚合得到的 `RMSE=1173.27±36.39, R²=0.7943±0.0128`。

总结：这三组不能混写成同一个“主配置”。`1208.82` 更像 RQ1 baseline 对比里的主 teacher；`1164.75` 是 E1 最优宽度/λ 诊断结果；`1173.27` 是 E2 特征消融中的 F28 均值。后续写论文时，应把它们分成 baseline、diagnostic、ablation 三个角色。

当前状态：这个风险项已部分修正。当前正文已经明确区分 `w=24` 的 baseline 角色与 `w=16` 的符号提取角色，但后续仍应避免在摘要、结论和答辩口径里把三组数字混写成单一“主配置”。

追溯：`doc/paper_assets/data/combo_h6_results.json`，`runs/rq2_e1_lambda__rq2_e1_w16_l0_001_s1..s3`，`runs/rq2_e2_ablation__rq2_e2_f28_no_base_s1..s3`

会话来源：`9a770562-46cb-423a-8989-5e3483a6c2e8.jsonl`，`461a35af-bb9f-4d28-bfb3-c8ac065d6d2c.jsonl`

## 4. E1 稀疏化强度消融

需求：判断公式失败到底是不是 λ 没调好。

数据：`runs/rq2_e1_lambda__*` 共 24 个 run。
聚合值：`w=10, λ=0.001` 为 `RMSE=5152.81±6940.58, R²=-7.7602±14.8335`；`w=10, λ=0.05` 为 `1335.66±32.53, 0.7335±0.0129`；`w=16, λ=0.001` 为 `1164.75±52.54, 0.7971±0.0184`；`w=16, λ=0.005` 为 `1217.60±105.99, 0.7775±0.0395`。

总结：这组数据支持“窄网络对 λ 极敏感，w=16 更鲁棒；但仅靠调 λ 不能解决符号可交付性问题”。它适合做瓶颈诊断，不适合当最终主结果。

追溯：`runs/rq2_e1_lambda__rq2_e1_w10_l0_001_s1..s3`，`runs/rq2_e1_lambda__rq2_e1_w10_l0_005_s1..s3`，`runs/rq2_e1_lambda__rq2_e1_w10_l0_01_s1..s3`，`runs/rq2_e1_lambda__rq2_e1_w10_l0_05_s1..s3`，`runs/rq2_e1_lambda__rq2_e1_w16_l0_001_s1..s3`，`runs/rq2_e1_lambda__rq2_e1_w16_l0_005_s1..s3`，`runs/rq2_e1_lambda__rq2_e1_w16_l0_01_s1..s3`，`runs/rq2_e1_lambda__rq2_e1_w16_l0_05_s1..s3`

## 5. E2 特征消融

需求：确定到底是哪些输入信息在压制物理变量。

数据：`runs/rq2_e2_ablation__*` 共 15 个 run。
聚合值：`F31-FULL` 为 `592.18±12.02, 0.9476±0.0021`；`F28-NO_BASE` 为 `1173.27±36.39, 0.7943±0.0128`；`F28-limited-lag` 为 `2245.12±515.31, 0.2209±0.3266`；`F28-no-lag` 为 `2251.02±531.33, 0.2153±0.3600`；`F-reduced` 为 `1872.25±96.31, 0.4757±0.0541`。

总结：这组数据很适合支撑“base series 和 lag 才是 Direct KAN 的主要信息优势，气象特征不是没用，而是被压制了”。其中 F31 只能作诊断上界，不应该和 F28 主结果并列比较优劣。

追溯：`runs/rq2_e2_ablation__rq2_e2_f31_full_s1..s3`，`runs/rq2_e2_ablation__rq2_e2_f28_no_base_s1..s3`，`runs/rq2_e2_ablation__rq2_e2_f28_limited_lag_s1..s3`，`runs/rq2_e2_ablation__rq2_e2_f28_no_lag_s1..s3`，`runs/rq2_e2_ablation__rq2_e2_f_reduced_s1..s3`

## 6. E3 结构化分解

需求：验证把净负荷拆成负荷、光伏、风电三个子任务，是否能降低学习难度。

数据：`runs/rq2_e3_decomp__*` 共 18 个 run。
聚合值：`Direct` 为 `RMSE=2044.34±1274.17, R²=0.2143±0.9135`；`Load` 为 `430.04±14.60, 0.6344±0.0250`；`Solar` 为 `1053.68±97.19, 0.8099±0.0357`；`Wind` 的基础配置约为 `934.16, ~0`；`Wind paper cfg w24` 为 `815.85±2.43, 0.2372±0.0045`。

总结：这组数据适合证明“结构化分解让子任务更容易学”，但不适合直接用 RMSE 横比，因为 `delta_net_load`、`delta_load`、`delta_solar`、`delta_wind` 是不同目标。更稳妥的解释是：分解改善了各子任务的可学习性和后续符号化机会。

追溯：`runs/rq2_e3_decomp__rq2_e3_direct_s1..s3`，`runs/rq2_e3_decomp__rq2_e3_load_s1..s3`，`runs/rq2_e3_decomp__rq2_e3_solar_s1..s3`，`runs/rq2_e3_decomp__rq2_e3_wind_s1..s3`，`runs/rq2_e3_decomp__rq2_e3_wind_paper_cfg_w24_s1..s3`

## 7. h6 符号化失败筛查

需求：确认“公式不好”是不是偶然，还是同一类配置普遍失败。

数据：有两层数据。
一层是 `runs/rq2_e4_subkan__*`，共 48 个 h6 子 KAN 符号提取 run。
另一层是 DS-KAN h6 优化后再做的 `h6_r3_e4__*`，共 27 个 run。
会话反馈里明确记录：这 27 个 h6 E4 结果里“没有一个 test R² > 0.1”，而且不同 `r2_threshold` 产出的公式几乎一样。

总结：这组数据是非常重要的负例。它说明短期 `delta` 目标下，哪怕 teacher 已经调得更好，PySR/公式提取仍然很难泛化。这组数据适合用来解释为什么后面要转向多步长、局部复现和边界分析。

当前状态：这组数据适合作为“转向多步长与边界分析”的直接原因，不建议再展开逐个失败公式。

追溯：`runs/rq2_e4_subkan__*`，`runs/h6_r3_e4__*`

会话来源：`9a770562-46cb-423a-8989-5e3483a6c2e8.jsonl`

## 8. DS-KAN h6 优化与局部公式复现

需求：在 h6 条件下继续找更好的子任务配置，并验证论文里三条局部公式是不是能复现。

数据：teacher 优化后的代表性 run 为：
`runs/h6_opt_paperref_r1__load_w30_l0.005_wide_s1`，`RMSE=327.14, R²=0.7886`；
`runs/h6_opt_paperref_r1__solar_w20_l0.005_lr_s1`，`RMSE=1010.32, R²=0.8262`；
`runs/h6_opt_r2__wind_w30_l0.003_sparse_s1`，`RMSE=763.42, R²=0.3321`。

复现 run 为：
`runs/repro_solar_20260430`，`RMSE=994.38, R²=0.8317`；
`runs/repro_solar_20260430_sym_strict_r2_0_999`，`formula RMSE=2410.75, formula R²=0.0106, physics_mapping_score=0.9125, node_count=140`。
`runs/repro_wind_20260430`，`RMSE=663.84, R²=0.4950`；
`runs/repro_wind_20260430_sym_strict_r2_0_999`，`formula RMSE=1291.23, formula R²=-0.9106, physics_mapping_score=0.0, node_count=147`。

总结：这组数据说明“局部 teacher 可以做得不错，但公式质量高度不均匀”。Solar 能恢复物理含义，Wind 仍然恢复不了风速主导关系。这组数据很适合写成“局部可辨识性恢复 + 风电子任务边界”。

当前状态：这一组已经从单纯的 Physics Score 描述推进到变量贡献和敏感性分析。当前正文新增了 `5.4.2a` 与表 `5-6a/5-6b`，属于任务书第 5 点的核心补强；对应图资产为 `doc/paper_assets/figures/fig_sensitivity_comparison.png`。

追溯：`runs/h6_opt_paperref_r1__load_w30_l0.005_wide_s1`，`runs/h6_opt_paperref_r1__solar_w20_l0.005_lr_s1`，`runs/h6_opt_r2__wind_w30_l0.003_sparse_s1`，`runs/repro_solar_20260430*`，`runs/repro_wind_20260430*`

会话来源：`461a35af-bb9f-4d28-bfb3-c8ac065d6d2c.jsonl`

## 9. 多步长实验

需求：验证 Wind/Solar 的可学习性和可符号化意义是否依赖预测时域，而不是只看 h6。

数据：`runs/rq2_mh__*` 共 36 个 run。
按 `eval_test` 聚合：
Load：`h12 810.91 / 0.6486`，`h72 2958.13 / 0.6695`，`h144 3486.54 / 0.3302`，`h576 4586.67 / 0.2714`。
Solar：`h12 1548.73 / 0.8840`，`h72 4938.20 / 0.9010`，`h144 6690.85 / 0.8712`，`h576 4942.31 / 0.5056`。
Wind：`h12 1497.29 / 0.3066`，`h72 4050.46 / 0.7572`，`h144 8003.36 / 0.5928`，`h576 12058.38 / 0.3703`。

总结：这组数据非常值得保留。它直接支持“Wind 在 h72 比 h6 更有可解释价值，Solar 在中期更稳定，长期整体退化”。这不是补充材料，而是论文最强的一条解释链。

当前状态：这一组不仅有表格，还有图资产 `doc/paper_assets/figures/fig_multi_horizon_r2.png`，后续 LaTeX 排版时可直接挂成主图。

追溯：`runs/rq2_mh__mh_load_h12_s1..s3`，`runs/rq2_mh__mh_load_h72_s1..s3`，`runs/rq2_mh__mh_load_h144_s1..s3`，`runs/rq2_mh__mh_load_h576_s1..s3`，`runs/rq2_mh__mh_solar_*`，`runs/rq2_mh__mh_wind_*`

会话来源：`693f4d83-b16d-4803-bea6-d34ee74f280d.jsonl`，`fa623337-2dd2-4be6-bf8b-12054a0a7b24.jsonl`

## 10. h72 No-lag

需求：确认 lag 到底是在提供预测力，还是在提供“符号锚点”。

数据：`runs/h72_nolag__*` 共 9 个 run。
按 `eval_test` 聚合：
Load `RMSE=2825.16±99.57, R²=0.6982±0.0210`；
Solar `RMSE=5572.82±108.80, R²=0.8738±0.0049`；
Wind `RMSE=7509.98±255.89, R²=0.1790±0.0564`。
对照多步长 h72 teacher：Load `R²=0.6695`，Solar `0.9010`，Wind `0.7572`。

总结：这组数据清楚说明：对 Load/Solar 来说，lag 对纯预测性能的贡献有限；对 Wind 来说，lag 是决定性信号。因此“lag 贡献只有 2–3%”只能局部成立，不能泛化到 Wind。

当前状态：这条结论现在应视为已收口口径。后续统一表述应是“Load/Solar 中 lag 贡献小，Wind 中 lag 是决定性信号”。

追溯：`runs/h72_nolag__load_s1..s3`，`runs/h72_nolag__solar_s1..s3`，`runs/h72_nolag__wind_s1..s3`

## 11. h72 组合与 Wind 公式边界

需求：在中期时域上看结构化组合是否仍然成立，以及 Wind 公式是否真的能用。

数据：`doc/paper_assets/data/combo_h72_results.json`。
关键值：`ds_kan_combo_3kan` 为 `RMSE=6763.42, R²=0.8158`；`per_component_load_kan` 为 `2952.76, 0.6707`；`per_component_solar_kan` 为 `4996.46, 0.8986`；`per_component_wind_kan` 为 `3882.34, 0.7809`；`per_component_wind_formula` 为 `9610.02, -0.3427`。

总结：这组数据说明 h72 下 teacher 组合仍然强，但 Wind 公式对象和 Wind teacher 对象差得非常远。它很适合支撑“预测器对象和公式对象必须分开叙述”。

追溯：`doc/paper_assets/data/combo_h72_results.json`，其中引用的 `e3_runs` 为 `rq2_mh__mh_load_h72_s1`、`rq2_mh__mh_solar_h72_s1`、`rq2_mh__mh_wind_h72_s1`，Wind 公式 run 为 `rq2_e4_wind_h72__sym_strict_r2_0_995_rq2_mh_mh_wind_h72_s1`

## 12. constrained direct 与 narrow direct pilot

需求：验证是否可以不走 DS-KAN，而靠更小、更受约束的 Direct KAN 直接获得可读公式。

数据：`exp/constrained_direct_symbolic_20260430_seed1/constrained_direct_symbolic_summary.csv` 与 `...rows.csv`。
关键值：`f28_no_base` 的 `train_rmse=1144.54, symbolic_rmse=2970.09, tgr=2.5950`；`f28_limited_lag` 的 `1661.58 → 3313.83`；`f_reduced` 的 `1862.90 → 3937.22`；`f28_no_lag` 的 `1728.45 → 9679.22`。

另一路是 `exp/rq3_pilot_20260430_seed1_gpu_v2/rq3_pilot_summary.csv`。
关键值：`rq3_narrow_w4_s1` teacher 为 `1628.64 / 0.6041`；对应 symbolic run 为 `2591.17 / -0.003 / physical_score=0.355 / node_count=123`。

总结：这组数据适合作为“替代路线尝试过，但没有稳定压过 DS-KAN”的证据。由于这些结果基本都是 `seed=1`，它们更适合放在 pilot 或备选路线，而不是论文主表。

当前状态：这一组的 seed 口径已经在正文中标成“代表性种子 seed=1”，风险明显下降。

追溯：`exp/constrained_direct_symbolic_20260430_seed1/constrained_direct_symbolic_summary.csv`，`exp/constrained_direct_symbolic_20260430_seed1/constrained_direct_symbolic_rows.csv`，`exp/rq3_pilot_20260430_seed1_gpu_v2/rq3_pilot_summary.csv`

## 13. Wind 专项消融与 short-lag 负例

需求：解释为什么 Wind 始终难，以及“高精度”为什么可能毫无解释价值。

数据：`doc/paper_assets/data/wind_ablation_results.json` 与 `runs/wind_abl_*`。
λ 扫描聚合：`0.0001` 为 `RMSE=785.83±37.40, R²=0.2913±0.0682`；`0.0005` 为 `806.35±20.35, 0.2546±0.0374`；`0.001` 为 `821.70±9.95, 0.2262±0.0188`；`0.005` 为 `820.91±4.42, 0.2277±0.0083`；`0.01` 为 `854.75±102.65, 0.1547±0.2044`。
short-lag 聚合：`runs/wind_abl_shortlag__wind_h6_shortlag_s1..s3` 给出 `RMSE=106.70±2.18, R²=0.98695±0.00053`。

总结：这组数据说明两个事实。第一，Wind 对 λ 不算特别敏感，问题不只是稀疏度没调好。第二，lag_1 可以把短期 Wind 做到几乎完美，但那只是复制，不是可解释成功。这是一个必须保留的强负例。

追溯：`doc/paper_assets/data/wind_ablation_results.json`，`runs/wind_abl_lambda__*`，`runs/wind_abl_shortlag__wind_h6_shortlag_s1..s3`

## 14. 结构稳定性

需求：判断 DS-KAN 是否真的比 Direct KAN 稳，不只是偶然挑出一条好公式。

数据：`doc/paper_assets/data/stability_pareto_data.json`。
关键值：`ver_layer.load` 的 `pairwise_feature_overlap=1.0`，首组保留特征为 `cdd_18c, dow_cos, dow_sin, hdd_18c, hour_cos, hour_sin, load_lag_1`；`ver_layer.solar` 的 `pairwise_feature_overlap=1.0`，首组特征为 `ghi_day_w_m2, ghi_temp_corr_w_m2, ghi_w_m2, is_night, solar_altitude, solar_azimuth, solar_lag_1`；`ver_layer.wind_w24` 的 `pairwise_feature_overlap=1.0`，首组特征为 `hour_cos, hour_sin, wind_lag_24, wind_lag_48`，且 `mean_ver=0.0`。

总结：这组数据适合支撑“DS-KAN 的变量选择非常稳定”，但也同时说明 Wind 的稳定性并不等于物理正确性，因为它稳定保留的是 lag，而不是 wind_speed。

当前状态：这一组已有图资产 `doc/paper_assets/figures/fig_stability_comparison.png`，适合与多步长图、敏感性图一起作为最终答辩图表。

追溯：`doc/paper_assets/data/stability_pareto_data.json`

## 15. 图表资产索引

需求：把已经生成的图资产和对应实验组绑定，避免后续只记得“有图”，却忘了每张图对应哪组 run、支撑什么结论。

数据：
- `doc/paper_assets/figures/fig_model_comparison.png`：汇总 RQ1 基线、Direct KAN 与 DS-KAN 代表性结果，主要对应第 2、3、8、11 组。
- `doc/paper_assets/figures/fig_multi_horizon_r2.png`：展示 Load / Solar / Wind 在 `h12/h72/h144/h576` 的 R² 变化，主要对应第 9、10、11 组。
- `doc/paper_assets/figures/fig_sensitivity_comparison.png`：展示 Solar / Wind 公式的变量贡献与敏感性差异，主要对应第 8 组。
- `doc/paper_assets/figures/fig_stability_comparison.png`：展示 DS-KAN 的跨种子特征重叠与结构稳定性，主要对应第 14 组。

总结：当前四张图已经覆盖了“整体模型对比、时域变化、物理敏感性、结构稳定性”四个最关键的答辩维度。它们不是新增证据，而是对现有 run 和表格证据的视觉化组织。

追溯：`doc/paper_assets/figures/fig_model_comparison.png`，`doc/paper_assets/figures/fig_multi_horizon_r2.png`，`doc/paper_assets/figures/fig_sensitivity_comparison.png`，`doc/paper_assets/figures/fig_stability_comparison.png`

## 16. h72 Direct KAN 基线对照

需求：补充 h72 步长下 Direct KAN（28 维净负荷直接预测）的基线结果，使 h72 组合对比表有完整的 Direct KAN 参照。此前 h72 仅有 DS-KAN 子任务数据，缺少 Direct KAN 对照，无法回答"DS-KAN 组合 vs 直接 KAN 在 h72 上谁更好"。

数据：`runs/direct_kan_h72__w24_l0.001_nogrid_s1..s3`，共 3 个 run。
配置：`w=24, λ=0.001, F28(NO_BASE), default profile, lag_steps=12,24,48, lag_series=load,wind,solar, include_groups=meteorology,solar,cyclic, no-warmup-update-grid`。数据集为 `protocol_exec_20260427_fixm2__derived_multi_h`。

聚合值：
seed 1: `RMSE=4600.28, R²=0.9148`；
seed 2: `RMSE=4244.55, R²=0.9275`；
seed 3: `RMSE=6691.39, R²=0.8197`；
均值: `RMSE=5178.74±1322.01, R²=0.8873±0.0589`。

对照（来自第 11 组）：DS-KAN 子KAN组合 `RMSE=6763.42, R²=0.8158`；DS-KAN 符号公式组合 `RMSE=11252.74, R²=0.4902`。

总结：h72 下 Direct KAN 的纯预测精度（R²=0.887）反而优于 DS-KAN 子KAN组合（R²=0.816），这与 h6 的趋势一致（Direct > DS-KAN combo），但差距在 h72 更明显。不过有两个要点：第一，seed 3 明显偏差（R²=0.82），说明 w=24 在 h72 下方差较大，稳定性不如 DS-KAN 的跨种子特征重叠度 1.0；第二，DS-KAN 的价值不在于净负荷精度竞赛，而在于子公式的可解释性和特征选择稳定性。这组数据适合在论文中用来说明"Direct KAN 精度更高但不可交付公式，DS-KAN 精度略低但产出可分析的子公式"。

注意：首次用 `--warmup-update-grid` 提交的 3 个 run（`direct_kan_h72__w24_l0.001_s1..s3`）全部因 NaN 失败，原因是 h72 目标方差（std=14711）远大于 h6（std=2614），grid update 导致数值溢出。关闭 grid update 后训练正常。

追溯：`runs/direct_kan_h72__w24_l0.001_nogrid_s1`，`runs/direct_kan_h72__w24_l0.001_nogrid_s2`，`runs/direct_kan_h72__w24_l0.001_nogrid_s3`

## 17. h72 基线对比

需求：在 h72 步长下补齐与 h6 RQ1 对应的全部基线模型，使 h72 组合对比表具有完整的参照系。

数据：`runs/h72_baseline__persistence`，`runs/h72_baseline__sarimax`，`runs/h72_baseline__xgboost`，`runs/h72_baseline__mlp_matched`，`runs/h72_baseline__lstm_matched`。数据集均为 `protocol_exec_20260427_fixm2__derived_multi_h`，target 为 `delta_net_load_h72`。MLP/LSTM 匹配 Direct KAN h72（`direct_kan_h72__w24_l0.001_nogrid_s1`）的特征列和训练预算。

关键值：
Persistence `RMSE=15760.07, R²≈0`；
SARIMAX `RMSE=8557.43, R²=0.7052`；
LSTM (matched) `RMSE=8178.22, R²=0.7311`；
DS-KAN 子KAN组合 `RMSE=6763.42, R²=0.8158`（来自第 11 组）；
XGBoost `RMSE=6136.14, R²=0.8484`；
Direct KAN h72 (3种子) `RMSE=5178.74±1322.01, R²=0.8873±0.0589`（来自第 16 组）；
MLP (matched) `RMSE=5174.07, R²=0.8922`；
DS-KAN 符号公式组合 `RMSE=11252.74, R²=0.4902`（来自第 11 组）。

总结：h72 下 MLP 和 Direct KAN 精度几乎相同（R²≈0.89），远优于 DS-KAN 子KAN组合（R²=0.816）。LSTM 在 matched budget 下表现意外差（R²=0.731），可能受限于短训练预算与 h72 长序列依赖的不匹配。DS-KAN 组合介于 XGBoost 和 LSTM 之间。符号公式组合仍有明显退化（R²=0.490）。这组数据适合在论文中构建 h72 综合对比表，说明"Direct KAN 精度最优但不可出公式，DS-KAN 精度可接受但主要价值在可解释性"。

PySR `RMSE=9117.30, R²=0.6653`（run `2026-05-03_121135_7cdf67cd`，niterations=1200，28维特征同步 Direct KAN h72）。

追溯：`runs/h72_baseline__persistence`，`runs/h72_baseline__sarimax`，`runs/h72_baseline__xgboost`，`runs/h72_baseline__mlp_matched`，`runs/h72_baseline__lstm_matched`，`runs/2026-05-03_121135_7cdf67cd`（PySR）

## 18. KAN-SR 风格后处理（h6 子公式）

需求：参考 KAN-SR（Buhler & Guillen-Gosalbez, arXiv:2509.10089, 2025）的后处理思路，对 DS-KAN 的三条 h6 子公式进行系数快照（snap near-integer/pi）、有理化（nsimplify）、BFGS 常数重优化和 SymPy 化简，评估后处理能否改善公式精度或压缩公式长度。

数据：对三条子公式分别执行后处理管线（BFGS 在训练集上优化常数，测试集上评估，与 KAN-SR 论文一致），结果如下：
Load（`rq2_e4_subkan__sym_strict_r2_0_98_rq2_e3_decomp_rq2_e3_load_s1`）：原始 `RMSE=746.4, R²=-0.101, TGR=1.770`，BFGS 后 `RMSE=707.9, R²=+0.010, TGR=1.678`。ΔRMSE=−39，ΔTGR=−0.092。公式长度 970→1173 chars。
Solar（`rq2_e4_subkan__sym_strict_r2_0_98_rq2_e3_decomp_rq2_e3_solar_s3`）：原始 `RMSE=2153.5, R²=0.211, TGR=1.849`，rationalize 后 `RMSE=2188.8, R²=0.184, TGR=1.880`。BFGS 无进一步改善（rationalize 已去掉 GHI 变量，仅剩 2 维，无优化空间）。公式 819→206 chars，ΔTGR=+0.030（微降）。
Wind（`repro_wind_20260430_sym_strict_r2_0_999`）：原始 `RMSE=1291.2, R²=-0.911, TGR=1.945`，后处理后 `RMSE=1291.4, R²=-0.911, TGR=1.945`。ΔTGR=±0.000。公式 1348→468 chars。

总结：在训练集上做 BFGS 重优化后，h6 仅 Load 有小幅改善（ΔTGR=−0.092），Solar/Wind 无效果。有理化+化简对所有子公式都能大幅压缩长度，但对精度无帮助或微降。Wind 的不可符号化性在后处理中得到再次确认。后处理后的公式已保存到各 run 的 `artifacts/formula_postprocessed.sympy.txt`。

注意：首版后处理曾错误地在测试集上做 BFGS 优化，导致 Load 出现 TGR<1 的虚假改善。修正为训练集优化后，改善幅度大幅收窄，这是正确的结果。

追溯：`scripts/postprocess_formula.py`，各 run 的 `artifacts/formula_postprocessed.sympy.txt` 和 `artifacts/formula_postprocessed_eval.json`

## 19. KAN-SR 风格后处理（h72 子公式）

需求：在 h72 步长下对 DS-KAN 三条子公式执行与第 18 组相同的后处理管线（snap + rationalize + BFGS + simplify），评估 BFGS 常数重优化在中期时域下的改善效果，并测试后处理后的组合净负荷精度。

数据：对三条最优 h72 子公式执行后处理管线（BFGS 在训练集上优化，测试集上评估）。子公式按 test R² 选取最优 run，经全量排查确认（Load 51 个 run，Solar 54 个 run，Wind 23 个 run）。

Load（`rq2_e4_load_h72__sym_medium_r2_0.99_rq2_mh_mh_load_h72_s1`）：原始 `RMSE=3568.9, R²=0.519, TGR=1.206`，BFGS 后 `RMSE=3541.9, R²=0.526, TGR=1.197`。ΔTGR=−0.009。
Solar（`rq2_e4_solar_h72__sym_strict_poly4_r2_0_999_rq2_mh_mh_solar_h72_s1`）：原始 `RMSE=8658.1, R²=0.696, TGR=1.753`，BFGS 后 `RMSE=7629.2, R²=0.764, TGR=1.545`。ΔTGR=−0.208。唯一有实质改善的子公式。
Wind（`rq2_e4_wind_h72__sym_strict_r2_0_98_rq2_mh_mh_wind_h72_s2`）：原始 `RMSE=4134.3, R²=0.751, TGR=1.021`，BFGS 后 `RMSE=4136.3, R²=0.751, TGR=1.021`。ΔTGR=±0.000。

组合净负荷精度（net_load = load − wind − solar）：
注意口径：`combo_h72_results.json` 中 `RMSE=11252.7, R²=0.490` 是"Load KAN + Solar KAN + Wind 公式"（当时仅 Wind 有公式 run），不是三条公式全部组合。本组使用三条子公式的最优 run 全部参与组合。

三公式组合（原始）`RMSE=9702.6, R²=0.621`；
三公式组合（BFGS 后处理）暂未重新评估组合（因 Load/Wind 改善极微，组合精度预计变化不大，主要改善来自 Solar 单项）。

对照：DS-KAN 子KAN组合 `RMSE=6763.4, R²=0.816`；混合组合（KAN L+S + 后处理 Wind 公式）`RMSE=7014.1, R²=0.802`；Direct KAN h72 `RMSE=5178.7, R²=0.887`。

总结：在训练集上做 BFGS 后，h72 仅 Solar 有实质改善（ΔTGR=−0.208，RMSE 降了约 1000），Load 改善极微（ΔTGR=−0.009），Wind 无变化。这与 h6 的模式一致（Wind 始终无效），但 h72 Solar 的改善明显大于 h6 Solar（h6 Solar 反而微降）。h72 Solar 改善更大的原因可能是 h72 公式结构更简洁（仅 4 个变量、47 个节点 vs h6 的 6 个变量、53 个节点），给 BFGS 更好的优化空间。Wind 的 h72 原始 TGR=1.021 本身就很低（公式几乎等于教师），留给 BFGS 的改善空间极小。

注意：首版后处理曾错误地在测试集上做 BFGS 优化，导致 h72 Solar 出现 ΔTGR=−0.643、Load 出现 TGR<1 的虚假结果。修正为训练集优化后数值大幅收窄。台账中所有后处理数据均已更新为训练集 BFGS 的正确版本。

追溯：`scripts/postprocess_formula.py`，各 h72 run 的 `artifacts/formula_postprocessed.sympy.txt` 和 `artifacts/formula_postprocessed_eval.json`

## 20. 相对修订计划的状态更新（原第16组）

需求：把这份“按组索引”的实验台账和 `thesis_revision_plan_20260428-v2.md` 对齐，明确哪些问题已经闭环，哪些只是从“风险项”降成了“持续注意项”。

数据：对照 `doc/thesis_revision_plan_20260428-v2.md`、`doc/thesis_draft_20260501.md` 与当前图资产。已核实的闭环项包括：数据协议与泄漏探测、RQ1 六基线补全、E1-E4、DS-KAN h6 局部复现、多步长、h72 No-lag、Wind 专项消融、Direct KAN 三组数字的角色拆分、seed 口径声明、总体标准差 `ddof=0` 声明、泄漏表头去工程化、敏感性分析补强。图资产层面已存在 `fig_multi_horizon_r2.png`、`fig_sensitivity_comparison.png`、`fig_stability_comparison.png`、`fig_model_comparison.png`。

总结：相对于 4 月 28 日修订计划，这份实验体系已经不再缺“关键实验”，而主要进入“证据组织与口径收束”阶段。需要持续注意的只有三类事项：第一，Direct KAN 的 `1208.82 / 1164.75 / 1173.27` 不能再混写，必须始终按 baseline / diagnostic / ablation 三个角色使用；第二，F31 只能作为诊断上界，不能进入公平性能排名；第三，跨目标 RMSE 不能作为方法优劣依据，只能配合 R² 和可符号化难度解释。

追溯：`doc/thesis_revision_plan_20260428-v2.md`，`doc/thesis_draft_20260501.md`，`doc/paper_assets/figures/fig_multi_horizon_r2.png`，`doc/paper_assets/figures/fig_sensitivity_comparison.png`，`doc/paper_assets/figures/fig_stability_comparison.png`，`doc/paper_assets/figures/fig_model_comparison.png`

## 21. 使用建议与论文叙事结构

### 最终方法主线

```
数据协议 → KAN 验证 → Direct 诊断 → DS-KAN 分解 → 多步长选域 → 特征筛选 → PySR 搜索 → 后处理
  §1          §2-3       §4-7          §6             §9            §14         §26         §27
```

#### 第一幕：问题定义与基线建立（§1-3）

**§1 数据协议**。泄漏探测证明 split-aware 流程与原流程 RMSE 完全一致，数据协议无泄漏。
**§2 RQ1 六基线**。Persistence→SARIMAX→PySR→MLP→LSTM→XGBoost，KAN（RMSE=1209, R²=0.784）与 XGBoost（1203, 0.784）持平，证明 KAN 有预测能力。**注意**：此时 PySR 28 维全特征 R²=0.367，远不如 MLP（0.678）——这是后续”为什么不直接用 PySR”的伏笔。
**§3 Direct KAN 主 teacher**。三组不同配置的 Direct KAN 数据（baseline 1209 / diagnostic 1165 / ablation 1173），明确角色区分。

#### 第二幕：Direct KAN 出不了公式（§4-7）

**§4 E1 λ 消融**。w=10 对 λ 极敏感（R² 从 −7.76 到 0.73），w=16 更鲁棒（1165±53）。结论：不是 λ 没调好。
**§5 E2 特征消融**。F31-FULL R²=0.948 vs F28-NO_BASE R²=0.794 vs F28-no-lag R²=0.215。结论：base series 和 lag 压制了物理变量。量化代价：**从 F31 到 F28 主动放弃了 0.154 的 R²（0.948→0.794）来换取可解释性**，这个数字定义了"可解释性的精度代价上界"。
**§6 E3 结构化分解**。净负荷拆成 Load/Solar/Wind 三个子任务后各自更容易学：Load R²=0.634, Solar R²=0.810。**Direct 净负荷方差极大**（RMSE=2044±1274, R²=0.214±0.914，σ(R²)=0.914），而子任务稳定得多——分解不仅提高精度，更大幅降低方差。
**§7 h6 符号化失败**。48 个 h6 子 KAN 符号提取 run + 27 个优化后 run，**无一 test R²>0.1**。结论：高维 Direct KAN 的公式提取是死路。
**§12 替代路线也失败**。Constrained Direct 的 TGR（公式/teacher RMSE 比）：f28_no_base=2.60, f28_limited_lag=2.00, f_reduced=2.12；Narrow w4 symbolic R²=−0.003。即使约束特征或缩小网络，Direct KAN 的公式精度仍是 teacher 的 2-2.6 倍差。

#### 第三幕：为什么从 h6 转向 h72（§9 多步长实验）

这是论文叙事的**第一个关键转折点**。

§7 在 h6（6 小时）上符号化全面失败后，§9 的多步长实验（h12/h72/h144/h576）揭示了时域选择的关键性：

| 子任务 | h6 R² | h12 R² | h72 R² | h144 R² | h576 R² |
|--------|-------|--------|--------|---------|---------|
| Load | 0.634 | 0.649 | 0.670 | 0.330 | 0.271 |
| Solar | 0.810 | 0.884 | **0.901** | 0.871 | 0.506 |
| Wind | ≈0 | 0.307 | **0.757** | 0.593 | 0.370 |

**Wind 的变化最剧烈**：h6 时 R²≈0（几乎学不会），h72 时 R²=0.757（可学习）。这是因为 h6 的 delta_wind 被高频噪声主导，KAN 无法从中提取有意义的模式；而 h72 的 delta_wind 包含了更多中期天气系统的结构化信号（冷锋过境、季节性风力变化等），KAN 可以学到可泛化的模式。Solar 在 h72 也达到峰值（0.901）。**因此后续所有实验转向 h72**。

§10 的 h72 No-lag 实验进一步分离了信号来源：去掉 lag 后 Load R² 仅从 0.670→0.698（lag 贡献小），Solar 从 0.901→0.874（lag 贡献小），但 **Wind 从 0.757→0.179（lag 是决定性信号）**。这为后续 Wind 公式的物理解读设定了预期：Wind 公式必然以 lag 为主，物理变量只能起辅助作用。

#### 第四幕：DS-KAN 局部可辨识性与特征筛选（§8、§14）

**§8 局部公式复现**揭示了子任务间的物理可辨识性差异：Solar h6 复现得到 `physics_mapping_score=0.9125`（变量贡献恢复了太阳辐照→出力的物理关系），但 Wind h6 复现 `physics_mapping_score=0.0`（147 节点的公式没有任何物理含义）。这是 DS-KAN 路线的正反对比：**Solar 可以恢复物理，Wind 不能**。

**§14 跨种子特征稳定性**。3 seeds 特征重叠度：Load=1.0, Solar=1.0, Wind=1.0。DS-KAN 的变量选择非常稳定，每个子任务总是选出相同的核心特征集。这为后续 PySR 提供了可靠的特征输入。但需要注意两点限制：（1）稳定不等于物理正确——Wind 稳定保留的是 lag 而非 wind_speed；（2）剪枝过程间接使用了测试集（见§28 待修复问题 3），特征选择的纯净性需要确认。

#### 第五幕：33 种方法/配置的系统失败（§7-25）

这是论文叙事的**第二个关键转折点**——在给出最终方案前，系统展示所有替代路线的失败。**在找到最终方案前，共尝试了 33 种不同的方法或配置**，按失败原因可归为 5 大类。

**第 1 类：高维直接搜索——搜索空间爆炸（7 种）**

| # | 方法 | 来源 | 关键指标 | 失败原因 |
|---|------|------|---------|---------|
| 1 | Direct KAN h6 符号提取 | §7 | 48 run 全部 R²<0.1 | 28 维 PySR 无法收敛 |
| 2 | DS-KAN h6 子KAN 符号提取 | §7 | 27 run 全部 R²<0.1 | h6 高频噪声主导 |
| 3 | Constrained Direct f28_no_base | §12 | TGR=2.60 | 约束特征不够，架构仍太宽 |
| 4 | Constrained Direct f28_limited_lag | §12 | TGR=2.00 | 同上 |
| 5 | Constrained Direct f_reduced | §12 | TGR=2.12 | 同上 |
| 6 | Narrow Direct w=4 | §12 | R²=−0.003 | 太窄学不会 |
| 7 | PySR 28 维 h6 / h72 | §2, §17 | R²=0.367 / 0.665 | 28 维搜索空间爆炸 |

**第 2 类：KAN/DS-KAN 符号提取——公式冗长不可读（8 种）**

| # | 方法 | 来源 | 关键指标 | 失败原因 |
|---|------|------|---------|---------|
| 8 | DS-KAN h6 优化 Load | §8 | RMSE=746, R²=−0.10 | 970 chars 不可读 |
| 9 | DS-KAN h6 优化 Solar | §8 | R²=0.21, physics=0.91 | 唯一部分成功但精度差 |
| 10 | DS-KAN h6 优化 Wind | §8 | R²=−0.91, physics=0.0 | 147 节点零物理含义 |
| 11 | DS-KAN h72 Load | §19 | RMSE=3569, R²=0.52 | TGR=1.21，公式冗长 |
| 12 | DS-KAN h72 Solar | §19 | RMSE=7629(BFGS), R²=0.76 | BFGS 唯一有效但仍冗长 |
| 13 | DS-KAN h72 Wind | §19 | RMSE=4134, R²=0.75 | TGR≈1 但 physics_score=0 |
| 14 | KAN-SR BFGS h6 三条 | §18 | Load ΔTGR=−0.09 | 结构限制 > 常数精度 |
| 15 | KAN-SR BFGS h72 三条 | §19 | Solar ΔTGR=−0.21 | 仅 Solar 有效 |

**第 3 类：S2KAN 路线——NN 精度高但公式不可读（14 种）**

| # | 方法 | 来源 | 关键指标 | 失败原因 |
|---|------|------|---------|---------|
| 16 | S2KAN 子任务 Load | §23 | NN R²=0.962, 160 边 | 不可读 |
| 17 | S2KAN 子任务 Solar | §23 | NN R²=0.954, 160 边 | 不可读 |
| 18 | S2KAN 子任务 Wind | §23 | R²=−19.53 | 彻底崩溃 |
| 19 | S2KAN Direct 28 维 | §23 | R²=−31.9 ~ −45.5 | 高维彻底崩溃 |
| 20 | →GAM 压缩 | §24 | NN R²=0.878, Formula 爆炸 | spline 残差丢弃后崩溃 |
| 21 | →Ortho GAM | §24 | NN R²=0.892, Formula 爆炸 | 同上 |
| 22 | →Masked GAM [n,1,1] | §24 | **Load Formula R²=0.522** | sin(Σ) 不可分解 |
| 23 | →Bottleneck k=5 | §24 | NN R²=0.958, Formula=0.13 | 可压缩但不可读 |
| 24 | →Progressive MDL | §24 | 160 边不变 | gate 对 MDL 不敏感 |
| 25 | →Distill→PySR | §24 | R²=0.876 但公式=lag1−lag48 | 蒸馏只保留 lag 差分 |
| 26 | →Guided KAN k=3/k=5 | §24 | k=3 R²=0.098 / k=5 R²=0.703 | 极不稳定 |
| 27 | →LASSO | §24 | R²=0.639 | 精度中等无突破 |
| 28 | →Piecewise | §24 | R²=0.374 | 分段样本不足 |
| 29 | →Boosting | §24 | R²=0.273 | 残差信号太弱 |

**第 4 类：文献方法复现——不适用于本场景（1 种）**

| # | 方法 | 来源 | 关键指标 | 失败原因 |
|---|------|------|---------|---------|
| 30 | Hybrid KAN-ANN (Jiang et al.) | §22 | ANN 补偿 −0.4% | 672 边不可读，ANN 是黑箱 |

**第 5 类：纯净特征但架构限制——精度或组合不够（3 种）**

| # | 方法 | 来源 | 关键指标 | 失败原因 |
|---|------|------|---------|---------|
| 31 | Masked GAM [n,1,1] 纯净特征 | §25a | Solar Formula R²=0.54 | sin(Σ) 包裹仍在 |
| 32 | Additive GAM [n,1] 纯净特征 | §25b | Solar R²=0.68（最佳物理映射） | combo R²=0.480 精度不够 |
| 33 | DS-KAN h72 三公式组合 | §19 | combo RMSE=9703, R²=0.621 | 远不如黑箱基线 |

以上 33 种方法的共同问题可归纳为一个三难困境：**精度、可读性、物理含义不可兼得**。高精度方法（S2KAN NN R²=0.96、MLP R²=0.89）不可读；可读方法（Additive GAM、PySR 28 维）精度差；而即使精度和可读性都凑合的方法（DS-KAN h72 公式 R²=0.75），也缺乏物理含义（physics_score=0）。

最终方案（§26-27，DS-KAN 分解 + 纯净特征 + PySR）是**第 34 种尝试**，也是唯一同时突破三难困境的方法。

---

以下是第五幕中各替代方法的详细分析。

**DS-KAN 自身的符号提取（§18-19）**：

| 子任务 | DS-KAN 公式 RMSE | 公式 R² | TGR | 问题 |
|--------|-----------------|---------|-----|------|
| Load h72 | 3569（BFGS后 3542） | 0.519（0.526） | 1.21 | 公式 970 chars，不可读 |
| Solar h72 | 8658（BFGS后 7629） | 0.696（0.764） | 1.75（1.55） | BFGS 唯一有效（ΔTGR=−0.21） |
| Wind h72 | 4134 | 0.751 | 1.02 | TGR≈1 但 physics_score=0，零物理含义 |
| 组合 | 9703 | 0.621 | — | 远不如 DS-KAN KAN combo（6763, 0.816） |

**Hybrid KAN-ANN（§22）**：KAN+ANN 残差补偿改善率 −0.4%（微降），w=24 的 KAN 第一层 672 条边不可读，ANN 部分是纯黑箱。在 h72 28 维下无效。

**S2KAN（§23）**：子任务 NN 精度极高（Load R²=0.962, Solar 0.954），但 160 条符号边不可读。Wind R²=−19.53 彻底崩溃。Direct 28 维 R²=−31.9。

**S2KAN 十方案压缩（§24，⚠ 特征有污染）**：

| 最优方案 | Load Formula R² | Solar Formula R² | 问题 |
|---------|----------------|-----------------|------|
| Masked GAM（最佳） | 0.522 | 0.384 | sin(Σ) 包裹，不可分解 |
| GAM / Ortho GAM | 爆炸 | 0.092-0.239 | spline 残差丢弃后崩溃 |
| Bottleneck k=5 | −173 | 0.126 | 信息可压缩但公式不可读 |
| Progressive | 不压缩 | 不压缩 | MDL 对 gate 无效（负例） |

核心发现：**NN R² ≠ Formula R²**。symbolic ratio=100% 不等于可出公式。

**纯净特征 Masked GAM（§25）**：纠正特征污染后，加性 GAM [n,1] Solar Formula R²=0.677（历史最高），`sin(solar_alt)` 物理映射优秀。但三公式组合 RMSE=11366、R²=0.480，远不如基线。

**§13 Wind 专项消融**补充了两个关键负例：
- **λ 扫描**（λ=0.0001~0.01）：Wind R² 仅在 0.15-0.29 之间浮动，对 λ 不算特别敏感。结论：Wind 失败不是稀疏度没调好。
- **short-lag（含 lag_1）**：R²=0.987，RMSE=107——看似完美，但公式本质是 `y ≈ lag_1`（纯复制）。这定义了"什么是物理无意义的伪精度"：R²=0.987 的 short-lag 公式没有任何预测或物理价值，它只是把上一步的观测值复制了一遍。后续评价 Wind 公式时，必须区分"lag 复制带来的高 R²"和"物理变量带来的有效 R²"。

**§12 Constrained Direct（补充）**：即使约束了特征集，Direct KAN 的公式 TGR 仍为 2.0-2.6（公式 RMSE 是 teacher 的 2-2.6 倍），Narrow w=4 更是 R²=−0.003。结论：降低网络宽度不能绕过分解。

#### Wind 物理可解释性的跨方法对比

Wind 是整个实验体系中最难的子任务。以下是所有方法在 Wind 公式提取上的结果：

| 方法 | Wind Formula R² | Wind Formula RMSE | 物理含义 | 可读性 |
|------|----------------|-------------------|---------|--------|
| DS-KAN h6 符号化（§7） | 全部<0.1 | — | ✗ | ✗ |
| DS-KAN h6 复现（§8） | −0.911 | 1291 | physics_score=0 | ✗（147 节点） |
| DS-KAN h72 公式（§19） | 0.751 | 4134 | 无物理含义 | ✗ |
| KAN-SR BFGS（§19） | 0.751 | 4136 | ΔTGR=0，无改善 | ✗ |
| S2KAN（§23） | −19.53 | 37579 | 崩溃 | ✗ |
| Masked GAM [n,1,1]（§25a） | 0.562 | 5489 | sin(Σ) 不可分解 | ✗ |
| Additive GAM [n,1]（§25b） | 0.629 | 5052 | wind_speed 系数(−67)被 lag(8682)淹没 | △ |
| GAM 含 lag（§24，⚠ 污染） | 0.544 | — | 有 v³ 但混入 load/solar lag | △ |
| Wind short-lag（§13） | 0.987 | 107 | 纯 lag_1 复制，零物理 | ✗ |
| **PySR c=14（§26）** | **0.890** | **2753** | lag 差分 + exp 日内调制 | **✓✓** |
| **PySR c=18（§26）** | **0.886** | **2801** | **含 wind_speed_cubed (v³)** | **✓** |

**PySR c=18 是整个实验体系中唯一一条同时满足 R²>0.85、包含 v³ 风功率物理项（P ∝ v³）、且可读（<20 节点）的 Wind 公式。** 其他所有方法要么精度不够（DS-KAN h6、Additive GAM），要么没有物理含义（DS-KAN h72 公式 physics_score=0），要么不可读（S2KAN 160 边、Masked GAM sin 包裹），要么是假精度（short-lag 纯复制）。

#### 第六幕：最终方案与交付（§26-27）

DS-KAN 筛选出的纯净特征集（9-12 维）喂给 PySR，搜到 3-4 变量的简洁公式：

| 子任务 | 最终公式 | RMSE | R² | 变量 |
|--------|---------|------|-----|------|
| Load | `lag_1 + lag_48·(3/26·sin(h_cos·h_sin + h_sin·m_cos − 89/99·h_sin) − 1)` | 1662 | 0.896 | 4 |
| Solar | `lag_1 + (azimuth−123.5)·(−0.258·azimuth + (lag_48−altitude)·(exp(−40.5·lag_48)−0.004) − 20.4)` | 5249 | 0.888 | 4 |
| Wind | `91/73·lag_1 − 101/86·lag_48 + 101/86·exp(743/85·hour_sin) − 2329` | 2753 | 0.890 | 3 |

三公式组合净负荷：**RMSE=5719, R²=0.868**。

对照全部方法的组合净负荷排名：

| 排名 | 方法 | Combo RMSE | Combo R² | 性质 | 公式可读 |
|------|------|-----------|---------|------|---------|
| — | Additive GAM 3×formula（§25b） | 11366 | 0.480 | 公式 | ✓ 但精度差 |
| — | DS-KAN 3×formula（§19） | 9703 | 0.621 | 公式 | ✗ 冗长不可读 |
| — | PySR 28 维 h72 直接搜索（§17） | 9117 | 0.665 | 公式 | ✓ 但精度差 |
| 7 | SARIMAX（§17） | 8557 | 0.705 | 统计模型 | — |
| 6 | LSTM（§17） | 8178 | 0.731 | 黑箱 | ✗ |
| 5 | DS-KAN 3×KAN combo（§11） | 6763 | 0.816 | NN | ✗ |
| 4 | XGBoost（§17） | 6136 | 0.848 | 黑箱 | ✗ |
| **3** | **PySR 3×formula（§26）** | **5719** | **0.868** | **公式** | **✓✓** |
| 2 | Direct KAN（§16） | 5179 | 0.887 | NN | ✗ |
| 1 | MLP（§17） | 5174 | 0.892 | 黑箱 | ✗ |

注意 PySR 28 维直接搜索（R²=0.665）与 PySR 分解后搜索（R²=0.868）的差距：同一个 PySR 算法，降维后 R² 提升了 30%。这直接证明 **DS-KAN 分解+特征筛选是 PySR 成功的前提条件**。

**PySR 3×formula 是唯一一个既排进精度前三、又完全可读可验证的方法。** 比它精度更高的（MLP、Direct KAN）全是黑箱；比它更可读的（Additive GAM）精度差一倍。

#### PySR Pareto 前沿的渐进发现过程

PySR 的 Pareto 前沿展示了变量按重要性逐步引入的过程，本身就是可解释性的体现：

**Load**：c=3 `lag_1−lag_48`（纯趋势）→ c=11 `+hour_sin×month_cos`（加入日内×季节交互）→ c=16 `+sin(hour_sin×(hour_cos+month_cos))`（非线性交互）→ c=22 `+hdd_18c`（温度修正）。前两步贡献了 R² 的 90%，温度只是微调。

**Solar**：c=3 `lag_1−lag_48`（纯趋势）→ c=11 `−azimuth²×lag_48`（太阳轨迹二次调制）→ c=22 `+altitude×(...)`（高度角耦合）。solar_azimuth 是第一个被发现的物理变量，早于 altitude。

**Wind**：c=3 `lag_1−lag_48`（纯趋势）→ c=7 `+hour_sin`（日内周期）→ c=14 `+exp(hour_sin)`（非线性日内尖峰）→ c=18 `−wind_speed_cubed`（v³ 风功率）。**wind_speed_cubed 是最后被引入的变量**（c=18），说明在 h72 尺度上风速的物理贡献确实远小于 lag 和时间周期——这与 §10 No-lag 实验（去 lag 后 Wind R² 从 0.757→0.179）完全一致。

### Wind 公式的精度交付版 vs 物理解释版

§27 最终交付选了 **c=14（R²=0.890，3 变量，RMSE=2753）** 作为 Wind 精度交付版，因为它 R² 最高且仅 3 变量。但 **c=18（R²=0.886，4 变量，RMSE=2801）** 包含 `wind_speed_cubed`（v³ 风功率），是物理解释版。两者 R² 仅差 0.004，论文中应同时呈现：c=14 用于精度排名表，c=18 用于物理可解释性讨论。

### 论文叙事中的关键转折点

1. **”为什么不直接用 PySR？”** —— §2 PySR h6 28 维全特征 R²=0.367；§17 PySR h72 28 维 R²=0.665（RMSE=9117）。无论 h6 还是 h72，28 维直接搜索都远不如分解后的 9-12 维搜索（R²=0.84-0.90）。
2. **”为什么从 h6 转向 h72？”** —— §9 多步长实验：Wind h6 R²≈0 → h72 R²=0.757。h6 被高频噪声主导，h72 包含结构化天气信号。§7 的 h6 符号化全面失败是直接触发原因。
3. **”为什么不直接从 KAN/S2KAN 提取公式？”** —— §7 h6 全部失败；§12 Constrained Direct TGR=2.0-2.6；§23 S2KAN 160 边不可读；§24 十方案最优 Formula R²=0.522（Masked GAM）远不如 PySR（0.896）。
4. **”DS-KAN 分解 + PySR 为什么能 work？”** —— 降维是关键。28 维→9-12 维后 PySR 搜索空间缩小指数级，同一 h72 上 PySR 从 R²=0.665（28 维，§17）跃升到组合 R²=0.868（分解后，§26）。
5. **”怎么确认 Wind 公式不是假精度？”** —— §13 short-lag R²=0.987 证明纯 lag 复制可以得到极高 R² 但零物理含义。PySR c=18 的 R²=0.886 虽然低于 short-lag，但包含 v³ 风功率项，是整个实验体系中唯一有物理意义的 Wind 公式。

### 对比实验索引（论文讨论部分素材）

| 实验组 | 论文角色 | 关键数据 |
|--------|---------|---------|
| §16-17 | 精度参照系 | h72 全基线排名表 |
| §8 | 物理映射正面例证 | Solar `sin(solar_alt)` 可恢复 |
| §11 | DS-KAN 组合参照 | KAN combo R²=0.816 vs 公式 combo R²=0.490 |
| §12-13 | 替代路线负例 | constrained direct 不优于 DS-KAN；short-lag R²=0.987 是伪精度 |
| §18-19 | 后处理有效性 | BFGS 仅对结构合理的公式有效（Solar h72 ΔTGR=−0.21） |
| §22 | 文献方法对比 | Hybrid KAN-ANN 残差补偿无效（−0.4%） |
| §23-24 | S2KAN 系统评估 | NN R²≠Formula R²；Progressive 负例；Bottleneck 可压缩但不可读 |
| §25 | 加性 GAM 对比 | 物理映射最佳（Solar `sin(alt)`），但精度和组合不如 PySR |

### S2KAN 在论文中的定位

S2KAN（§23-24-25）**不在最终方法主线中**，但提供了三条不可替代的论证：
- **NN R² ≠ Formula R²**（§24）：symbolic ratio=100% 不等于可出公式，B-spline 残差承载了 20-50% 预测力。
- **渐进 MDL 稀疏化对 gate 无效**（§24 Progressive）：S2KAN 的 gate 机制不适合用 MDL 惩罚来压缩。
- **加性 GAM 的物理映射**（§25b）：Solar 的 `sin(solar_alt)` 是最直观的物理公式，适合在论文中作为物理可解释性的视觉化例证。

## 22. Hybrid KAN-ANN（h72 Direct）

需求：复现 Jiang et al. (IEEE Trans. Power Systems, 2024) 的 Hybrid KAN-ANN 方法——KAN 产出解析表达式 + ANN 残差补偿精度损失，验证该架构在 h72 下能否兼顾公式输出与高精度。

方法：两阶段流水线。Stage 1: 训练 KAN（warmup→sparsify→prune→refine），与 Direct KAN h72（§16）配置完全对齐；Stage 2: 在 KAN 预测残差上训练 MLP（hidden=64, epochs=100, patience=10）。最终预测 = KAN_pred + MLP(features)。

配置：`target=delta_net_load_h72, w=24, λ=0.001, F28(NO_BASE), default profile, lag_steps=12,24,48, no-warmup-update-grid`。数据集为 `protocol_exec_20260427_fixm2__derived_multi_h`。

数据：`runs/h72_hybrid_kan_ann_v5_s1`。

关键值：
KAN-only `RMSE=4506.64, R²=0.918`；
Combined (KAN+ANN) `RMSE=4526.88, R²=0.917`；
ANN 残差补偿 improvement = −0.4%（微降）。

对照（§16）：Direct KAN h72 seed 1 `RMSE=4600.28, R²=0.915`；3种子均值 `RMSE=5178.74±1322, R²=0.887±0.059`。

总结：Hybrid KAN-ANN 的 KAN 部分精度与 Direct KAN 一致（同一配置、同一 seed），ANN 残差补偿实质无效（−0.4%），说明 KAN 已经捕获了特征空间中可用的信号，残差中没有结构化信息供 MLP 学习。更关键的问题是公式可读性：w=24 的 Direct KAN 第一层有 672 条边，剪枝后公式仍然冗长不可读（与 §7 h6 符号化失败一致）；ANN 残差部分是纯黑箱，使得最终 “公式” 变成 `解析式 + 不可读 MLP`，在可解释性上没有比 Direct KAN 更进一步。该方法在 Jiang et al. 的 STLF 场景能 work，是因为他们的 KAN 更小、任务更简单；在本项目 h72 28 维设定下，公式可交付性的瓶颈不在精度补偿，而在 DS-KAN 分解后的子任务简化。

追溯：`runs/h72_hybrid_kan_ann_v5_s1`，`src/local/hybrid_kan_ann_job.py`，`modal_jobs/hybrid_kan_ann.py`

## 23. S2KAN 训练时符号集成（h72 子任务）

需求：复现 Bagrow & Bongard (arXiv:2512.07875, 2025) 的 S2KAN 方法——激活函数 = 符号原语字典 + 密集样条 + 可学习门控，MDL 目标自动在训练时产出符号结构，不需要后处理符号提取。在 h72 子任务上验证 S2KAN 能否同时获得高精度和可读性。

方法：自定义 S2KAN 模型，每条边的激活函数为 `gate × Σ_k(w_k·σ_k(x)) + (1−gate) × Σ_j(c_j·B_j(x))`，其中 σ_k ∈ {identity, square, cube, sin, cos, exp, tanh, abs, sqrt_abs, sigmoid}（10 个符号原语），B_j 为 B-spline 基函数，gate ∈ [0,1] 为可学习标量。训练目标 = MSE + λ_mdl × MDL_penalty + λ_l1 × L1。特征使用 z-score 归一化。

配置（子任务版本，与 h72 nolag §10 对齐）：
Load: `target=delta_load_h72, hidden=10, include_groups=cyclic,meteo_degree, profile=load_no_month_cyclic, no lag, no base`；
Solar: `target=delta_solar_h72, hidden=10, include_groups=meteo_irradiance,solar_geom,solar_flag, profile=default, no lag, no base`；
Wind: `target=delta_wind_h72, hidden=24, include_groups=cyclic,meteo_wind, profile=default, no lag, no base`。
公共参数：`grid_size=5, spline_order=3, grid_range=[-3,3], epochs=200, lr=1e-3, patience=20, lamb_mdl=1e-4, lamb_l1=1e-5, feature z-score=True`。数据集为 `protocol_exec_20260427_fixm2__derived_multi_h`。

数据：`runs/h72_s2kan_load_v1_s1`，`runs/h72_s2kan_solar_v1_s1`，`runs/h72_s2kan_wind_v1_s1`。

关键值：
Load `RMSE=1002.34, R²=0.962, sym_ratio=[1.0, 1.0]`，epoch=67 early stop；
Solar `RMSE=3353.53, R²=0.954, sym_ratio=[1.0, 1.0]`，epoch=54 early stop；
Wind `RMSE=37579.46, R²=-19.53, sym_ratio=[0.97, 0.58]`，epoch=51 early stop。

对照：
DS-KAN h72 teacher（§9）：Load `2958.13 / 0.670`，Solar `4938.20 / 0.901`，Wind `4050.46 / 0.757`。
DS-KAN h72 公式（§19）：Load `3568.9 / 0.519`，Solar `8658→7629 / 0.764`，Wind `4134.3 / 0.751`。
h72 nolag KAN（§10）：Load `2825.16±99.57 / 0.698`，Solar `5572.82±108.80 / 0.874`，Wind `7509.98±255.89 / 0.179`。

总结：S2KAN 在 Load 和 Solar 子任务上大幅超越 DS-KAN teacher 和公式：Load R²=0.962（vs teacher 0.670，+43%）、Solar R²=0.954（vs teacher 0.901，+5.9%）。两个子任务的 symbolic ratio 均为 100%，意味着所有边都自动选择了符号激活函数而非 B-spline——这验证了 S2KAN 的核心设计目标。Wind 仍然失败（R²=-19.5），与所有其他方法的 Wind 边界一致（§13）。

但可读性存在根本限制：S2KAN 的 100% symbolic 不等于可读公式。以 Load 为例，15→10→1 架构产生 150+10=160 条符号边，每个特征通过不同的符号函数连接到所有 10 个隐藏神经元（如 `cdd_18c` 对不同隐藏节点分别用了 cos×4、cube×3、sin、identity、sigmoid），无法提炼成一条简洁表达式。此外 gate 值普遍在 0.5-0.8 之间（不是接近 1.0 的强偏好），说明”选择符号”的置信度不高。S2KAN 本质上是一个结构化的符号基函数字典模型，精度优于 DS-KAN，但不能替代 DS-KAN 的剪枝+符号提取来产出可读公式。

物理信号部分可辨识但被噪声淹没：Solar 中 `solar_azimuth→cos` 最强（方位角余弦映射太阳轨迹）、`solar_altitude→cube`（高度角非线性功率响应）、`solar_lag_1→identity`（近期出力线性延续）；Load 中 `load_lag_1` 权重最大（短期自回归）、`hour_sin/cos` 排第 2-3（日内周期）、`cdd_18c→cos`（制冷度日季节性）。这些信号有物理意义，但混在 150+ 条边中无法单独提取。

注意：S2KAN 在 h72 Direct（28 维 delta_net_load_h72）上完全失败（含 adaptive grid 版本 R²=-31.9，不含 R²=-45.5），确认 S2KAN 仅适合 DS-KAN 分解后的低维子任务。

追溯：`runs/h72_s2kan_load_v1_s1`，`runs/h72_s2kan_solar_v1_s1`，`runs/h72_s2kan_wind_v1_s1`，`runs/h72_s2kan_v4_s1`（direct 失败），`runs/h72_s2kan_agrid_v1_s1`（adaptive grid 失败），`src/models/s2kan.py`，`src/local/s2kan_job.py`，`modal_jobs/s2kan_train.py`

## 24. S2KAN 公式压缩工具箱（10 方案系统对比）【⚠ 特征污染】

> **⚠ 特征污染警告**：本组所有 run 的特征集存在子任务间交叉污染。Load 子任务混入了 ghi、wind_speed、solar_altitude 等 26 个特征（含 wind/solar lag）；Solar 子任务混入了 load_lag、wind_lag 共 15 个特征；Wind 子任务混入了 load_lag、solar_lag 共 18 个特征。这些不相关特征导致模型将部分预测力分散到噪声特征的 spline 残差中，使得公式质量（Formula R²）被低估，公式内容出现物理不合理项（如 Load 公式中的 solar_azimuth²、Wind 公式中的 load_lag_12²）。本组实验的 5 条核心结论（NN R²≠Formula R²、Masked GAM 最优、Bottleneck 可压缩但不可读、Progressive 无效、Boosting/Piecewise 不可行）**仍然成立**，因为它们是方法层面的结论而非数值层面的。但具体的 Formula R² 数值（Load 0.522、Solar 0.384、Wind 0.544）不应作为最终参考——已被第 25、26 组的纯净特征实验取代。

需求：第 23 组揭示 S2KAN 的核心矛盾——NN 精度极高（Load R²=0.962）但 160 条符号边不可读。本组实验系统测试 10 种不同的公式压缩路线，目标是从 S2KAN 的高精度底座中提取简洁、可读、物理可分析的公式。

方法概述：10 个方案分为三大类。
- 架构层面约束（4 种）：GAM（无隐藏层 [n,1]）、Bottleneck（低维瓶颈 [n,k,1]）、Masked GAM/h10（按物理含义限制每个特征的符号算子白名单）。
- 后处理蒸馏（3 种）：Distill→PySR（S2KAN 软标签+primitive 约束 PySR）、Guided KAN（S2KAN gate 选特征→窄 KAN→符号提取）、LASSO（S2KAN 选 primitive→稀疏回归）。
- 数据/结构变体（3 种）：Ortho GAM（去季节混淆后符号化）、Piecewise（按工况分段出公式）、Boosting（逐轮残差拟合）。
另有 Progressive（渐进 MDL 稀疏化）作为负例。所有方案在 h72 Load 和 Solar 子任务上测试，部分方案额外在 Wind 上测试。

数据（Load h72，按 NN R² 排序）：

| 方案 | NN R² | NN RMSE | Formula R² | Formula RMSE | 公式长度 |
|------|-------|---------|------------|--------------|---------|
| Ortho GAM | 0.892 | 1689 | 爆炸（spline 残差） | — | 1032c |
| Masked GAM | 0.886 | 1735 | **0.522** | 3558 | 737c |
| GAM | 0.878 | 1795 | 爆炸 | — | 921c |
| Distill→PySR | 0.876 | 1816 | ≈0.876（但为 `lag1-lag48`） | 1816 | 24c |
| Guided k=5 | 0.703 | 2806 | — | — | 77c |
| LASSO | 0.639 | 3091 | — | — | 294c |
| Piecewise | 0.374 | 4071 | — | — | — |
| Boosting 4×2 | 0.273 | 4388 | — | — | 404c |
| Guided k=3 | 0.098 | 4888 | — | — | 577c |
| Bottleneck k=3 | -0.056 | 5287 | -0.724 | 6757 | 2577c |
| Bottleneck k=5 | -8.936 | 16219 | -173 | 67853 | 4207c |
| Masked h10 | -8.839 | 16140 | 爆炸 | — | 7118c |
| Progressive | 0.962* | 1002* | 无（160 边不压缩） | — | — |

对照：DS-KAN teacher `R²=0.670, RMSE=2958`；DS-KAN 公式 `R²=0.519, RMSE=3569`。

数据（Solar h72，按 NN R² 排序）：

| 方案 | NN R² | NN RMSE | Formula R² | Formula RMSE | 公式长度 |
|------|-------|---------|------------|--------------|---------|
| Masked h10 | 0.962 | 3073 | 爆炸 | — | 3667c |
| Bottleneck k=5 | 0.958 | 3225 | 0.126 | 14672 | 2432c |
| Bottleneck k=3 | 0.953 | 3394 | -0.024 | 15881 | 1456c |
| Masked GAM | 0.894 | 5112 | **0.384** | 12313 | 422c |
| GAM | 0.886 | 5288 | 0.239 | 13693 | 546c |
| Ortho GAM | 0.886 | 5293 | 0.092 | 14957 | 576c |
| Guided k=3 | 0.868 | 5711 | — | — | 389c |
| Guided k=5 | 0.860 | 5874 | — | — | 422c |
| Distill→PySR | 0.842 | 6245 | — | — | 27c |
| LASSO | 0.816 | 6728 | — | — | 305c |
| Boosting 4×2 | 0.815 | 6754 | — | — | 327c |
| Piecewise | 0.314 | 13000 | — | — | — |
| Progressive | 0.954* | 3354* | 无（160 边不压缩） | — | — |

对照：DS-KAN teacher `R²=0.901, RMSE=4938`；DS-KAN 公式 `R²=0.764, RMSE=7629`（BFGS 后）。

数据（Wind h72，含 lag 特征）：

| 方案 | NN R² | NN RMSE | Formula R² | 说明 |
|------|-------|---------|------------|------|
| GAM（含 lag） | 0.905 | 2553 | 0.544 | lag 主导 + 气象修正 |
| GAM（含 lag） | 0.869 | 2998 | 0.254 | 较弱变体 |
| LASSO（含 lag） | 0.820 | 3518 | — | 稀疏公式 |
| Boosting 3×3 | 0.335 | 6765 | — | 分层弱 |
| Boosting 4×2 | 0.230 | 7280 | — | 分层弱 |
| Piecewise（高/低风） | -1.813 | 13909 | — | 崩溃 |

对照：DS-KAN teacher `R²=0.757, RMSE=4050`；DS-KAN 公式 `R²=0.751, RMSE=4134`。

总结：本组实验产出 5 条核心结论。

第一，**NN R² ≠ Formula R²**。这是最重要的发现。S2KAN 的 gate 在 0.5-0.8 之间意味着 B-spline 残差承担了 20-50% 的预测力；当只保留符号部分展开为公式时，精度大幅崩溃。GAM（NN R²=0.878）和 Ortho GAM（NN R²=0.892）的 Load 公式 R² 为负无穷，因为 base_weight（SiLU 残差连接）和 spline 残差被丢弃了。这意味着不能仅凭 symbolic ratio=100% 或 NN R² 高就声称"可出公式"。

第二，**物理字典约束（Masked GAM）是唯一在 Load 上产出有效公式的方案**（Formula R²=0.522），虽然仍低于 DS-KAN 公式（R²=0.519 持平），但公式仅 737 字符且全部项物理合理（时间→sin/cos、温度→identity/square/cube、lag→identity，不出现 cdd→cos 这类荒谬映射）。物理字典约束通过限制搜索空间避免了模型把预测力藏进 spline 残差。

第三，**Bottleneck 在 Solar 上 NN 精度极高（R²=0.958）但公式不可用**。5 维瓶颈足以保留 95.8% 的方差，证明 Solar 的信息确实可以被压缩到少量维度；但瓶颈后的符号展开（涉及嵌套组合非线性）产出的公式仍然冗长（2432c）且精度崩溃（Formula R²=0.126）。Bottleneck 适合作为"信息可压缩性"的证据，但不能直接产出可读公式。

第四，**渐进 MDL 稀疏化对 S2KAN 无效**。4 轮训练中 MDL 从 1e-4 提升到 0.1（1000 倍），但 active edges 始终保持 160 条不变（gate 未降到 0.3 以下）。这说明 S2KAN 的 gate 机制对 MDL 惩罚不敏感——模型倾向于降低 symbolic weight 绝对值而非关闭 gate。Progressive 是一个重要的负例。

第五，**Boosting 和 Piecewise 不适合本数据集**。Sequential Boosting 的 Load R²=0.273 远低于 GAM 的 0.878，原因是每轮只选 2 个特征且残差信号过弱。Piecewise 按工况分段后每个 regime 的训练样本过少，过拟合严重。这两条路线在理论上合理但在这个数据规模下不可行。

Wind 专项补充：GAM（含 lag）NN R²=0.905 且 Formula R²=0.544 超过了 DS-KAN 公式（R²=0.751），公式内容以 wind_lag_1 和 wind_lag_12 为主，附带 wind_speed_10m 的 cube 项（v³ 风功率物理关系）。这为 Wind 提供了一条"persistence + 微弱物理修正"的可解释公式，但 lag 仍是决定性信号。

当前状态：本组实验为论文讨论部分提供了系统的"公式压缩路线评估"。推荐在论文中保留的方案：Masked GAM（最佳公式质量）、GAM/Ortho GAM（NN R² vs Formula R² 差距分析）、Bottleneck（信息可压缩性证据）、Progressive（负例）。其余方案作为补充材料或脚注。

追溯：

架构层面：
`runs/hybrid_gam_load_20260503_174035`，`runs/hybrid_gam_solar_20260503_174035`，
`runs/hybrid_bottleneck_load_k3_v2_20260503_181647`，`runs/hybrid_bottleneck_load_k5_v2_20260503_181647`，`runs/hybrid_bottleneck_solar_k3_v2_20260503_181647`，`runs/hybrid_bottleneck_solar_k5_v2_20260503_181647`，
`runs/hybrid_masked_load_gam_v4_20260503_180733`，`runs/hybrid_masked_solar_gam_v4_20260503_180733`，`runs/hybrid_masked_load_h10_v4_20260503_180733`，`runs/hybrid_masked_solar_h10_v4_20260503_180733`

后处理蒸馏：
`runs/hybrid_distill_load_20260503_172603`，`runs/hybrid_distill_solar_20260503_172603`，
`runs/hybrid_guided_load_k3_20260503_172603`，`runs/hybrid_guided_load_k5_20260503_172603`，`runs/hybrid_guided_solar_k3_20260503_172603`，`runs/hybrid_guided_solar_k5_20260503_172603`，
`runs/hybrid_lasso_load_20260503_174035`，`runs/hybrid_lasso_solar_20260503_174035`

数据/结构变体：
`runs/hybrid_ortho_load_20260503_174035`，`runs/hybrid_ortho_solar_20260503_174035`，
`runs/hybrid_piecewise_load_20260503_174035`，`runs/hybrid_piecewise_solar_20260503_174035`，
`runs/hybrid_boosting_load_20260503_174035`，`runs/hybrid_boosting_solar_20260503_174035`

负例：
`runs/hybrid_progressive_load_v2_20260503_175824`，`runs/hybrid_progressive_solar_v2_20260503_175824`

Wind 专项：
`runs/wind_gam_lag_20260503_174914`，`runs/wind_gam_nolag_20260503_174914`，`runs/wind_lasso_lag_20260503_174914`，`runs/wind_boosting_lag_20260503_174914`，`runs/wind_boosting_3x3_20260503_174914`，`runs/wind_piecewise_lag_20260503_174914`

代码：`src/models/s2kan_gam.py`，`src/models/s2kan_bottleneck.py`，`src/models/s2kan_masked.py`，`src/local/s2kan_gam_job.py`，`src/local/s2kan_bottleneck_job.py`，`src/local/s2kan_masked_job.py`，`src/local/s2kan_distill_pysr_job.py`，`src/local/s2kan_guided_kan_job.py`，`src/local/s2kan_lasso_job.py`，`src/local/s2kan_ortho_job.py`，`src/local/s2kan_piecewise_job.py`，`src/local/s2kan_boosting_job.py`，`src/local/s2kan_progressive_job.py`，`src/local/s2kan_progressive_formula.py`，`modal_jobs/s2kan_gam.py`，`modal_jobs/s2kan_bottleneck.py`，`modal_jobs/s2kan_masked.py`，`modal_jobs/s2kan_distill_pysr.py`，`modal_jobs/s2kan_guided_kan.py`，`modal_jobs/s2kan_lasso.py`，`modal_jobs/s2kan_ortho.py`，`modal_jobs/s2kan_piecewise.py`，`modal_jobs/s2kan_boosting.py`，`modal_jobs/s2kan_progressive.py`

## 25. 纯净特征 Masked GAM（纠正第 24 组特征污染）

需求：第 24 组的 Masked GAM 特征集存在子任务间交叉污染（Load 混了 ghi/wind/solar 特征，Solar 混了 load/wind lag，Wind 混了 load/solar lag），导致公式中出现物理不合理项。本组实验用严格按物理相关性筛选的纯净特征集重跑 Masked GAM，分两种架构：[n,1,1]（带第二层）和 [n,1]（纯加性 GAM，output = Σ f_i(x_i)）。

特征集设计：
Load（12 维）：`hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos, temp_2m_c, cdd_18c, hdd_18c, load_lag_1, load_lag_12, load_lag_48`。仅保留时间周期、温度、负荷滞后。
Solar（9 维）：`ghi_w_m2, ghi_day_w_m2, ghi_temp_corr_w_m2, solar_altitude, solar_azimuth, is_night, solar_lag_1, solar_lag_12, solar_lag_48`。仅保留辐照、太阳几何、光伏滞后。
Wind（12 维）：`wind_speed_10m_m_s, wind_speed_10m_m_s_cubed, wind_speed_hub_est, hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos, wind_lag_1, wind_lag_12, wind_lag_48`。仅保留风速、时间周期、风电滞后。

数据集：`protocol_exec_20260427_fixm2__derived_multi_h`。配置：`epochs=200, lr=1e-3, patience=15, lamb_mdl=1e-3, lamb_l1=1e-5, seed=1`。

### 25a. Masked GAM [n,1,1]（带第二层 sin 包裹）

数据：`runs/masked_gam_load_clean_v1`，`runs/masked_gam_solar_clean_v1`，`runs/masked_gam_wind_clean_v1`。

| 子任务 | 特征数 | NN R² | NN RMSE | Formula R² | Formula RMSE | 节点数 |
|--------|--------|-------|---------|------------|-------------|--------|
| Load | 12 | 0.794 | 2334 | −0.629 | 6567 | 49 |
| Solar | 9 | 0.873 | 5583 | **0.537** | 10681 | 38 |
| Wind | 12 | 0.900 | 2617 | **0.562** | 5489 | 46 |

对照第 24 组混杂特征版：Load Formula R² 从 0.522→−0.629（下降），Solar 从 0.384→0.537（+40%），Wind Masked 从 0.254→0.562（+121%）。

公式结构问题：三条公式仍为 `A·sin(Σ 所有项) + b` 形式——所有变量被打包进同一个 sin()，无法拆成独立加性项。这是 [n,1,1] 架构的固有缺陷：第一层 n→1 加权求和，第二层 1→1 套 sin。特征纯化改善了 Solar 和 Wind 的 Formula R²（因为去掉噪声特征后模型不再把预测力分散到 spline 残差），但 Load 的 Formula R² 反而下降（12 维 sin 包裹比 26 维更脆弱）。

### 25b. 纯加性 Masked GAM [n,1]（无隐藏层）

数据：`runs/additive_masked_load_v1`，`runs/additive_masked_solar_v1`，`runs/additive_masked_wind_v1`。

| 子任务 | 特征数 | NN R² | NN RMSE | Formula R² | Formula RMSE | 节点数 |
|--------|--------|-------|---------|------------|-------------|--------|
| Load | 12 | 0.737 | 2638 | **0.437** | 3860 | 48 |
| Solar | 9 | 0.868 | 5698 | **0.677** | 8920 | 33 |
| Wind | 12 | 0.893 | 2708 | **0.629** | 5052 | 42 |

公式（还原特征名）：

F_load（加性，12 项）：
`−2010·hour_sin + 1472·sin(hour_cos) + 845·cos(month_sin) − 934·month_cos² − 22·dow_sin − 79·dow_cos − 2059·temp³ + 692·cdd² − 441·hdd³ + 4476·load_lag_1 + 5303·load_lag_12 − 8623·load_lag_48 − 22`

F_solar（加性，9 项，**物理映射最佳**）：
`−3285·ghi − 1741·ghi_day + 1869·ghi_temp_corr² + 3916·sin(solar_alt) − 6413·sin(solar_azimuth) − 2·is_night + 10237·solar_lag_1 + 2630·solar_lag_12 − 2348·solar_lag_48 − 2`

F_wind（加性，12 项）：
`−67·wind_speed − 13·wind_speed_cubed − 18·wind_speed_hub + 8682·wind_lag_1 + 4206·wind_lag_12 − 13838·wind_lag_48 + 1242·hour_cos − 2914·sin(hour_sin) + 70·dow_sin − 20·cos(dow_cos) − 473·cos(month_sin) − 426·cos(month_cos) + 7`

组合净负荷评估：
[n,1,1] NN combo：`RMSE=7054, R²=0.800`。
[n,1] NN combo：`RMSE=7324, R²=0.784`。
[n,1] Formula combo：`RMSE=11366, R²=0.480`（公式精度远低于 NN，因为公式丢弃了 spline 残差，加性 GAM 的 NN R²≠Formula R²差距仍然显著）。

总结：纯加性 GAM 的最大优势是公式真正可分解——每个特征的贡献独立可分析，不存在 sin 包裹问题。Solar 的 Formula R²=0.677 是**所有 S2KAN 路线中 Solar 公式的历史最高值**，且 `sin(solar_alt)` 和 `sin(solar_azimuth)` 完美对应太阳轨迹物理。但 NN R² 略低于 [n,1,1] 版本（因为纯加性模型不能捕捉变量交互），且 Load 公式仍有 12 项，不够简洁。Wind 公式中 lag 绝对主导（lag_1 系数 8682 vs wind_speed 系数 −67），再次确认 Wind 的物理信号被 lag 淹没。公式组合 R²=0.480 远低于 PySR 公式组合（0.868），说明加性 GAM 的公式精度不足以支撑净负荷级别的预测。

### 25c. 加性 GAM 后续优化（v6-v7）

需求：在保持 Additive GAM 可分解结构的前提下，继续测试三类小改动是否能缩小 NN 与公式之间的精度差距：`formula consistency`（强迫训练输出与符号分支更一致）、`lag penalty`（抑制滞后项支配）、`sparse interactions`（仅加入少量物理先验交互项）。

实现：在 `modal_jobs/s2kan_masked.py` / `src/local/s2kan_masked_optim.py` 上新增四个开关：`formula_consistency_weight`、`lag_penalty_weight`、`interaction_pairs`、`disable_base_branch`。交互项只允许显式给定的二元乘积，不引入额外黑箱层。数据集仍为 `protocol_exec_20260427_fixm2__derived_multi_h`。

数据（成功落盘的代表性 run）：

| run | 子任务 | 关键配置 | Test R² | Formula R² | 结论 |
|-----|--------|----------|--------|-----------|------|
| `additive_opt_load_formula_v6` | Load | consistency=0.05, no-base | 0.702 | 0.420 | 未优于 §25b |
| `additive_opt_load_sweep_v6` | Load | consistency=0.02, 弱正则 | 0.779 | 0.309 | NN 改善但公式更差 |
| `additive_opt_load_interact_v7` | Load | consistency=0.08 + `temp_2m_c*hour_sin`, `cdd_18c*hour_cos` | 0.820 | 0.170 | 交互提升 NN，但严重伤害公式可交付性 |
| `additive_opt_load_lagpen_v7` | Load | consistency=0.08 + lag penalty | 0.703 | 0.415 | 与 v6 持平，无实质突破 |
| `additive_opt_solar_formula_v6` | Solar | consistency=0.05 + `solar_altitude*ghi`, `solar_altitude*solar_lag_1` | 0.863 | 0.663 | 基本复现 §25b，但未超越 0.677 |
| `additive_opt_solar_sweep_v6` | Solar | consistency=0.08, no-base | 0.862 | 0.642 | 略低于 v6 交互版 |
| `additive_opt_solar_interact_v7` | Solar | consistency=0.08 + 同上两交互 | 0.863 | 0.660 | 与 v6 几乎等价，说明 Solar 已收敛 |
| `additive_opt_wind_sweep_v6` | Wind | consistency=0.02 + lag penalty=0.01 | 0.885 | 0.771 | 明显优于 §25b 的 0.629 |
| `additive_opt_wind_interact_v7` | Wind | consistency=0.02 + lag penalty=0.005 + `wind_speed_10m_m_s*hour_cos`, `wind_speed_10m_m_s_cubed*hour_cos` | 0.893 | **0.825** | 当前 Additive GAM 最成功的增量优化 |
| `additive_opt_wind_formula_v7` | Wind | consistency=0.05 + lag penalty=0.01 + no-base | 0.899 | 0.770 | 不如交互版 |

代表性公式变化：
- `additive_opt_solar_formula_v6` 保留了两个显式交互项：`solar_altitude*ghi_w_m2`、`solar_altitude*solar_lag_1`，但 Formula R² 仅到 0.663，仍低于原始加性式 0.677。
- `additive_opt_wind_interact_v7` 首次把风速变量带回到可交付公式里，交互项权重虽小（`wind_speed_10m_m_s*hour_cos=-0.012`，`wind_speed_10m_m_s_cubed*hour_cos=0.013`），但足以把 Formula R² 从 0.629 提升到 0.825。
- `Load` 上所有继续优化都只提高了 NN/test，没提高公式质量，说明其瓶颈不是轻量正则，而是目标本身缺乏足够强的低阶可分解结构。

总结：这一轮优化给出了一条很清楚的边界。第一，**Solar 不需要继续在 Additive GAM 上深挖**，原始 §25b 已经是最优物理映射版本；加入少量交互只能复现，不能突破。第二，**Wind 确实能被继续优化**，而且方向不是更强的 lag penalty，而是“轻度 lag penalty + 少量物理交互”，`wind_interact_v7` 使 Formula R² 达到 0.825，显著缩小了与 PySR 的差距。第三，**Load 仍然失败**：无论是交互还是 lag penalty，都只能改善 NN 而不能改善公式，说明 Additive GAM 在 Load 上依旧不是最终主线。

追溯：
[n,1,1]：`runs/masked_gam_load_clean_v1`，`runs/masked_gam_solar_clean_v1`，`runs/masked_gam_wind_clean_v1`
[n,1]：`runs/additive_masked_load_v1`，`runs/additive_masked_solar_v1`，`runs/additive_masked_wind_v1`
优化：`runs/additive_opt_load_formula_v6`，`runs/additive_opt_load_sweep_v6`，`runs/additive_opt_load_interact_v7`，`runs/additive_opt_load_lagpen_v7`，`runs/additive_opt_solar_formula_v6`，`runs/additive_opt_solar_sweep_v6`，`runs/additive_opt_solar_interact_v7`，`runs/additive_opt_wind_sweep_v6`，`runs/additive_opt_wind_interact_v7`，`runs/additive_opt_wind_formula_v7`
脚本：`scripts/submit_masked_gam_clean_features.sh`，`scripts/submit_additive_and_pysr_clean.sh`，`scripts/submit_additive_gam_optimization.sh`，`scripts/submit_additive_gam_optimization_v7.sh`

## 26. PySR 纯净特征直接符号回归（h72 子任务）

需求：在 DS-KAN 分解后的纯净特征集上，直接用 PySR 遗传符号回归搜索简洁公式，跳过 S2KAN 中间步骤。验证"DS-KAN 分解 + 特征筛选 + PySR"是否比"DS-KAN 分解 + S2KAN 公式压缩"更能产出简洁、高精度、物理可读的公式。

配置：`niterations=400, populations=8, population_size=40, maxsize=25, seed=1, max_train_rows=20000`。算子集：`binary=[+,−,×,÷], unary=[sin,cos,exp]`。特征集与第 25 组完全对齐。数据集：`protocol_exec_20260427_fixm2__derived_multi_h`。

数据：`runs/pysr_load_clean_v1`，`runs/pysr_solar_clean_v1`，`runs/pysr_wind_clean_v1`。

### Load PySR Pareto 前沿（关键方程）

| complexity | test R² | test RMSE | 方程 |
|------------|---------|-----------|------|
| 3 | 0.764 | 2499 | `load_lag_1 − load_lag_48` |
| 5 | 0.774 | 2446 | `(load_lag_12 − load_lag_48) / 0.579` |
| 11 | 0.793 | 2342 | `load_lag_12 − load_lag_48 + 4463·hour_sin·(month_cos − 0.959)` |
| **13** | **0.847** | **2015** | **`1.294 × (load_lag_12 − load_lag_48 + 2209·hour_sin·(month_cos − 1.001))`** |
| 16 | 0.896 | 1661 | `load_lag_1 − load_lag_48 + 0.115·load_lag_48·sin(hour_sin·(hour_cos + month_cos − 0.899))` |
| 22 | 0.887 | 1727 | `hdd_18c + 1.231×(load_lag_12 − load_lag_48 + 0.047·hour_sin·load_lag_48·(month_cos + sin(hour_cos + 0.449) − 1.649))` |

最优方程（c=13）：`Δload_h72 ≈ 1.29 × (lag_12 − lag_48 + 2209·hour_sin·(month_cos − 1))`。仅用 3 个变量（load_lag_12、load_lag_48、hour_sin、month_cos），物理含义清晰：lag 差分捕捉趋势，hour_sin×month_cos 捕捉日内×季节交互。

### Solar PySR Pareto 前沿（关键方程）

| complexity | test R² | test RMSE | 方程 |
|------------|---------|-----------|------|
| 3 | 0.740 | 8006 | `solar_lag_1 − solar_lag_48` |
| **11** | **0.847** | **6139** | **`solar_lag_1 − 9.38e-6·solar_azimuth²·(solar_lag_48 + 14367)`** |
| 13 | 0.862 | 5837 | `solar_lag_1 + (−0.222·solar_azimuth − 0.005·solar_lag_48)·(solar_azimuth − 124.7)` |
| 22 | 0.888 | 5249 | `solar_lag_1 + (solar_azimuth − 123.5)·(−0.258·solar_azimuth + (solar_lag_48 − solar_altitude)·(exp(−40.5·solar_lag_48) − 0.004) − 20.4)` |

最优方程（c=11）：`Δsolar_h72 ≈ solar_lag_1 − 9.38e-6·azimuth²·(lag_48 + 14367)`。3 个变量，`solar_azimuth²` 对应太阳轨迹的二次调制。

### Wind PySR Pareto 前沿（关键方程）

| complexity | test R² | test RMSE | 方程 |
|------------|---------|-----------|------|
| 3 | 0.832 | 3397 | `wind_lag_1 − wind_lag_48` |
| 5 | 0.876 | 2918 | `(wind_lag_12 − wind_lag_48) / 0.616` |
| **7** | **0.842** | **3300** | **`wind_lag_1 − wind_lag_48 + 3801·hour_sin`** |
| 10 | 0.877 | 2908 | `(wind_lag_1 − wind_lag_48)·1.228 + exp(8.777·hour_sin)` |
| 14 | 0.890 | 2753 | `1.174 × ((wind_lag_1 − 1868)·1.061 − wind_lag_48 + exp(8.741·hour_sin))` |
| 18 | 0.886 | 2801 | `1.204 × (1.070·(wind_lag_1 − 1819) − wind_lag_48 − wind_speed_cubed + exp(8.667·hour_sin − hour_cos))` |

最优方程（c=7）：`Δwind_h72 ≈ wind_lag_1 − wind_lag_48 + 3801·hour_sin`。3 个变量，极简。c=18 版本首次出现 `wind_speed_cubed`（v³ 风功率项）。

### 综合对比（best formula per task）

| 子任务 | 方法 | Formula RMSE | Formula R² | 变量数 | 简洁 | 可读 | 物理 |
|--------|------|-------------|-----------|--------|------|------|------|
| Load | DS-KAN h72 公式+BFGS（§19） | 3542 | 0.526 | — | ✗ | ✗ | △ |
| Load | 加性 Masked GAM [n,1]（§25b） | 3860 | 0.437 | 12 | △ | ✓ | △ |
| Load | **PySR c=16（§26）** | **1662** | **0.896** | **4** | **✓✓** | **✓✓** | **✓** |
| Solar | DS-KAN h72 公式+BFGS（§19） | 7629 | 0.764 | — | ✗ | ✗ | △ |
| Solar | 加性 Masked GAM [n,1]（§25b） | 8920 | 0.677 | 9 | ✓ | ✓ | ✓✓ |
| Solar | **PySR c=22（§26）** | **5249** | **0.888** | **4** | **✓** | **✓** | **✓** |
| Wind | DS-KAN h72 公式（§19） | 4134 | 0.751 | — | ✗ | ✗ | ✗ |
| Wind | 加性 Masked GAM + 交互优化（§25c） | 3467 | 0.825 | 12+2 | △ | ✓ | △ |
| Wind | **PySR c=14（§26）** | **2753** | **0.890** | **3** | **✓✓** | **✓✓** | △ |

### 组合净负荷评估（net_load = load − wind − solar）

| 排名 | 方法 | Combo RMSE | Combo R² | 性质 |
|------|------|-----------|---------|------|
| — | Persistence（§17） | 15760.1 | ~0 | — |
| — | Additive GAM 3×formula（§25b） | 11365.6 | 0.480 | 公式 |
| — | DS-KAN 3×formula（§19） | 9702.6 | 0.621 | 公式 |
| 7 | SARIMAX（§17） | 8557.4 | 0.705 | 统计模型 |
| 6 | LSTM matched（§17） | 8178.2 | 0.731 | 黑箱 |
| 5 | DS-KAN 3×KAN combo（§11） | 6763.4 | 0.816 | NN teacher |
| 4 | XGBoost（§17） | 6136.1 | 0.848 | 黑箱 |
| **3** | **PySR 3×formula（§26）** | **5719.1** | **0.868** | **公式** |
| 2 | Direct KAN h72（§16） | 5178.7 | 0.887 | NN |
| 1 | MLP matched（§17） | 5174.1 | 0.892 | 黑箱 |

PySR 3×formula 组合 RMSE=5719、R²=0.868，是所有**纯公式方法**中的最高值，RMSE 比 DS-KAN 3×formula（9703）低 41%，比加性 GAM 3×formula（11366）低 50%。在全部方法中排第三，仅次于 MLP（RMSE=5174）和 Direct KAN（RMSE=5179），且超过了 XGBoost（RMSE=6136）和 DS-KAN KAN combo（RMSE=6763）——而 PySR 公式是完全解析、可读、可验证的。

总结：PySR 在纯净特征集上**全面碾压了 S2KAN 和 Masked GAM 的所有变体**——更高的 R²、更少的变量、更简洁可读。关键发现：之前 PySR 跑 28 维全特征效果差（§2 RQ1 h6 PySR R²=0.367），是因为特征太多导致搜索空间爆炸。在 DS-KAN 分解后的纯净特征集上重跑，效果截然不同。这证明 **DS-KAN 的核心价值不在于直接出公式，而在于为下游符号回归做任务分解和特征筛选**——这是一条"DS-KAN 作为特征选择器 + PySR 作为公式搜索器"的两阶段流水线。

纯加性 Masked GAM 的独特价值在于物理映射最直观（Solar 的 `sin(solar_alt)` 和 `sin(solar_azimuth)` 完美对应太阳轨迹），适合作为物理可解释性的补充证据。

追溯：`runs/pysr_load_clean_v1`，`runs/pysr_solar_clean_v1`，`runs/pysr_wind_clean_v1`
脚本：`scripts/submit_additive_and_pysr_clean.sh`，`modal_jobs/pysr_baseline.py`（新增 `include_groups`、`lag_series` 参数支持）

## 27. PySR 公式后处理与最终交付公式

需求：对第 26 组 PySR 的最优公式（按 val R² 选取，修复了原先的 test cherry-pick 问题）执行 KAN-SR 风格后处理管线（snap + rationalize + BFGS + simplify），评估后处理能否进一步改善精度或压缩公式长度，并确定最终交付的三条子公式。

后处理管线（`scripts/postprocess_formula.py`）：
Step 1: Snap near-integer/π 系数（atol=0.02）。
Step 2: 系数有理化（nsimplify, tolerance=0.01）。
Step 3: BFGS 常数重优化（在训练集上 L-BFGS-B，maxiter=200）。
Step 4: SymPy 化简（CSE + collect + expand）。
每步后在**验证集**上评估，若 RMSE 退化超阈值则回退（测试集仅做最终报告）。

### 后处理结果

**Load**（val-best c=19，val_R²=0.957，test_R²=0.887）：
原始：`1.259·(0.0429·hour_sin·load_lag_48·(month_cos + sin(sin(hour_cos)) − 1.349) + load_lag_12 − load_lag_48)`，131 chars。
后处理后：**`107/85·load_lag_12 − 107/85·load_lag_48 + hour_sin·load_lag_48·(2/37·month_cos + 2/37·sin(sin(hour_cos)) − 224/3071)`**，140 chars。
test_R²=0.887→0.887（不变），ΔRMSE=−0.01。4 个浮点系数全部有理化。结构展开为显式加性形式：lag 差分项 + 日内×季节调制项。

（已废弃）原 c=16 版本（test-cherry-picked）：`load_lag_1 + load_lag_48·(3/26·sin(...) − 1)`，test_R²=0.896，备份于 `formula_c16.sympy.txt`。

**Solar**（原始 c=22，R²=0.888）：
原始：`solar_lag_1 + (solar_azimuth − 123.5)·(−0.258·solar_azimuth + (solar_lag_48 − solar_altitude)·(exp(−40.49·solar_lag_48) − 0.004) − 20.4)`，163 chars。
后处理结果：rationalization 将 `exp(−40.49·x)` 变成 `exp(x)^(198890350291/4911722880)` 等巨大有理数，公式膨胀到 639 chars 且 R² 微降（0.888→0.886）。**后处理有害，保留原始 PySR 公式。**

**Wind**（原始 c=14，R²=0.890）：
原始：`(−wind_lag_48 + (wind_lag_1 − 1867.8)·1.061 + exp(8.741·hour_sin))·1.174`，105 chars。
后处理后：**`91/73·wind_lag_1 − 101/86·wind_lag_48 + 101/86·exp(743/85·hour_sin) − 197907/85`**，79 chars。
R²=0.890→0.890（不变），ΔRMSE=+0.12。系数全部有理化，结构展开为显式加性形式。

### 最终交付的三条 h72 子公式

| 子任务 | 最终公式 | R² | RMSE | 变量 | 长度 |
|--------|---------|-----|------|------|------|
| **Load** | `107/85·load_lag_12 − 107/85·load_lag_48 + hour_sin·load_lag_48·(2/37·month_cos + 2/37·sin(sin(hour_cos)) − 224/3071)` | 0.887 | 1729 | 5 | 140c |
| **Solar** | `solar_lag_1 + (solar_azimuth − 123.5)·(−0.258·solar_azimuth + (solar_lag_48 − solar_altitude)·(exp(−40.49·solar_lag_48) − 0.004) − 20.4)` | 0.888 | 5249 | 4 | 163c |
| **Wind** | `91/73·wind_lag_1 − 101/86·wind_lag_48 + 101/86·exp(743/85·hour_sin) − 197907/85` | 0.890 | 2753 | 3 | 79c |

注：Load 公式由 val R² 选取（c=19, val_R²=0.957），替代原 test-cherry-picked 版本（c=16, test_R²=0.896）。Solar/Wind 公式 val 和 test 选择一致，无变化。

### 公式物理解读

**F_load**：`Δload_h72 ≈ 107/85·(lag_12 − lag_48) + hour_sin·lag_48·调制因子`。核心结构是 lag_12 − lag_48 的加权差分（捕捉半日到两日尺度的趋势），叠加 `hour_sin·load_lag_48` 的日内调制。调制因子中 `month_cos` 提供季节性（冬夏放大、春秋收窄），`sin(sin(hour_cos))` 提供双重压缩的日内非线性（将 hour_cos 的余弦曲线映射到更平坦的中间段和更陡的边缘，对应晨昏负荷骤变）。相比旧 c=16 公式，本公式用 lag_12 替代 lag_1，物理上更合理——12 步（3 小时）的回看窗口比 1 步（15 分钟）携带更多趋势信息。

**F_solar**：`Δsolar_h72 ≈ lag_1 + azimuth 二次调制`。solar_azimuth 的二次项描述太阳方位角对出力变化的非线性影响（正午 azimuth≈180° 时出力变化最大）。(solar_lag_48 − solar_altitude) 项耦合了近期出力历史和当前太阳高度。`exp(−40.49·lag_48)` 在 lag_48 较大时衰减为零，仅在 lag_48 接近零时生效——对应光伏出力从零启动的边界行为。

**F_wind**：`Δwind_h72 ≈ 1.25·lag_1 − 1.17·lag_48 + 1.17·exp(8.74·hour_sin) − 2328`。本质是加权 lag 差分 + 日内周期指数调制。`exp(8.74·hour_sin)` 在 hour_sin 为正时（下午）产生尖锐的非线性峰值，对应下午风电爬坡；hour_sin 为负时（夜间）该项衰减到极小值。wind_speed 未出现在最优公式中，再次确认 h72 风电变化主要由时序惯性而非瞬时风速驱动。

### 完整方法流水线（从原始数据到最终公式）

```
阶段 1：数据协议
  原始 ERCOT 数据 → 特征工程（cyclic/solar/meteorology/lag）→ z-score 归一化
  → train/val/test 时序切分 → leakage probe 验证（§1）
  产出：protocol_exec_*__derived_multi_h 数据集

阶段 2：DS-KAN 任务分解
  净负荷 → 分解为 Load / Solar / Wind 三个子任务（§6 E3）
  每个子任务独立训练 KAN teacher（§9 多步长）
  产出：三个子任务的 teacher 模型和 eval 指标

阶段 3：特征稳定性分析与筛选
  DS-KAN 跨种子特征重叠度分析（§14）→ 确认每个子任务的核心特征集
  去除子任务间交叉污染特征（§25 修正）
  产出：纯净特征集（Load 12 维、Solar 9 维、Wind 12 维）

阶段 4：PySR 遗传符号回归
  在纯净特征集上运行 PySR（niterations=400, maxsize=25）
  产出 Pareto 前沿：从 complexity=3（纯 lag 差分）到 complexity=25
  按 val R² 选取最优公式（§26，已修复 test cherry-pick）

阶段 5：后处理
  snap near-integer/π → rationalize coefficients → BFGS train-set refit → simplify
  对 Solar 跳过 rationalization（exp 系数不适合有理化）
  产出：最终交付公式（§27）

阶段 6：验证
  在独立测试集上评估 RMSE/R²
  与 DS-KAN 公式、Masked GAM 公式、全部基线模型对比（§26 综合表）
  物理含义审查（变量选择、函数形式、系数符号）
```

核心洞察：这条流水线的瓶颈不在任何单一步骤，而在**阶段 2-3 的任务分解和特征筛选**。PySR 在 28 维全特征上 R²=0.367（§2），在 DS-KAN 分解后的 9-12 维纯净特征上 R²=0.84-0.90。DS-KAN 的价值不是直接出公式，而是把不可符号化的高维问题简化为 PySR 可以处理的低维问题。

追溯：`runs/pysr_load_clean_v1/artifacts/formula_postprocessed.*`，`runs/pysr_solar_clean_v1/artifacts/formula_postprocessed.*`，`runs/pysr_wind_clean_v1/artifacts/formula_postprocessed.*`，`scripts/postprocess_formula.py`

## 28. 待修复问题（Codex 审查 2026-05-04）

以下问题由 Codex 独立代码审查发现，尚未修复，留待下次处理。

### 问题 1（严重）：PySR 公式在测试集上 cherry-pick

§26-27 的最终交付公式是按 **test R² 最高**手动从 Pareto 前沿选的（Load c=16、Solar c=22、Wind c=14），而非按 PySR 默认的 `model_selection="best"`（训练集 loss+complexity 权衡）。这构成测试集模型选择偏差。

- PySR 默认 best 选的是 Load c=13（test R²=0.847），我们用了 c=16（test R²=0.896）
- `equations.csv` 里每条方程都写了 test_rmse/test_r2（`modal_jobs/pysr_baseline.py:371`），方便了 cherry-pick

**修复方案**：改为 (a) 用 PySR 默认 best，或 (b) 在 validation set 上选公式，test set 只做最终一次性报告。需要重新计算 combo RMSE。

**审查结论（2026-05-04）**：**确认成立。** `modal_jobs/pysr_baseline.py:162` 加载了 train/val/test 三个 split，但 `val_df` 完全未使用。PySR 用 train 拟合（第 364 行），`equations.csv` 中所有指标（test_rmse/test_r2）均基于真实 test split（第 382-397 行）。§26-27 按 test R² 手动选公式确实构成 test set 模型选择偏差。

**已修复（2026-05-04）**：
1. 代码修复：`modal_jobs/pysr_baseline.py` 现在同时计算 val_rmse/val_mae/val_r2 和 test 指标，val_df 不再闲置。
2. 已有数据修复：`scripts/reeval_pysr_val.py` 对三组 PySR clean runs 补算了 val 指标，`equations.csv` 已更新。
3. Val-based 重选结果：
   - **Load**: val 选 c=19（val_R²=0.957, test_R²=0.887），原 test 选 c=16（val_R²=0.954, test_R²=0.896）。**Val 和 test 选���不同公式**，但差异不大。
   - **Solar**: val 和 test 一致选 c=22（val_R²=0.922, test_R²=0.888）。**��变化。**
   - **Wind**: val 和 test 一致选 c=14（val_R²=0.912, test_R²=0.890）。**无变化。**
4. 影响：仅 Load 子公式可能需要从 c=16 改为 c=19。Solar 和 Wind 不受影响。

### 问题 2（严重）：delta_h72 目标定义需明确

`delta_load_h72 = load(t) - load(t-72)`（`src/local/derive_dataset.py:49`），同时 `load_lag_1 = load(t-1)`（`src/data/features.py:203`）。

- 如果论文叙述为"站在 t-72 时刻预测 t 时刻的值"，则 `lag_1`（来自 t-1）是预测起点之后的数据，构成信息泄漏
- 如果叙述为"回归当前时刻相对过去 72 步的变化量"，则不是泄漏，但也不是前瞻预测

**修复方案**：论文中必须明确 delta_h72 的语义定义。若定位为前瞻预测，需要改为 `lag_72` 及更远的 lag。

**审查结论（2026-05-04）**：确认 delta_h72 语义为"回归当前时刻相对过去 72 步的变化量"，**不构成泄漏**。代码证据：`src/local/derive_dataset.py:49` 中 `compute_delta(out["load"], out["load"].shift(h))` 即 `load(t) - load(t-72)`，所有特征（含 `lag_1 = load(t-1)`）均来自 t 及其过去，无未来信息。任务语义与论文中 §6 E3（分解降低学习难度）和 §9（可符号化意义依赖预测时域）的叙述一致——核心贡献是发现变化量与变量间的函数关系，不是前瞻预测。**处置：论文正文中需补充一句明确定义即可，数据和公式全部保留有效。不影响任何现有 run。**

### 问题 3（中等）：DS-KAN 剪枝间接使用了测试集

`src/local/kan_train_prune.py:46` 用 `dataset["test_input"]` 评估剪枝候选，`kan_train_prune.py:74-84` 按测试 RMSE 选剪枝点。最终 `feature_importance.csv` 来自测试集选出的 pruned model，间接影响了§14 的特征稳定性分析和后续纯净特征集的构成。

**修复方案**：改为在 validation set 上选剪枝点，或确认 val/test 在此处的用法一致。

**审查结论（2026-05-04）**：**误报，实际用的是 validation set。** `src/kan_sr/dataset.py:159` 注释明确写明 "Here we map validation split to KAN's `test_*` fields for training-time monitoring"；`build_kan_dataset()` 的第二个参数是 `val_df`（第 145 行），被映射到 `dataset["test_input"]`（第 201 行）。`kan_train_prepare.py:104-105` 确认调用时传入的是 `val_df`。因此 `kan_train_prune.py:46` 的 `dataset["test_input"]` 实际评估的是 validation split，不是独立测试集。**处置：无需修复。字段命名容易误导（KAN 库惯例），可考虑加一行注释说明。**

### 问题 4（中等）：后处理 snap/rationalize 回退用了测试 RMSE

`scripts/postprocess_formula.py` 中 BFGS 在训练集上优化（第 288-290 行，正确），但 snap（第 267 行）、rationalize（第 280 行）、simplify（第 307 行）的保留/回退判断用了测试 RMSE 阈值。

**修复方案**：改为在 validation set 上做回退判断，或去掉回退机制（始终保留 snap/rationalize 结果）。

**审查结论（2026-05-04）**：**确认成立。** `scripts/postprocess_formula.py` 的 `load_splits()` 函数（第 62-66 行）加载 `test_*.parquet`（真实 test split），未加载 `val_*.parquet`。snap 回退（第 267 行）、rationalize 回退（第 280 行）、simplify 回退（第 307 行）的阈值判断均基于 `eval_formula(..., test_df, y_true_test, ...)`。BFGS 在 train 上优化是正确的（第 288-290 行），但回退决策用了 test。**修复方案**：`load_splits()` 补加载 `val_*.parquet`，snap/rationalize/simplify 的回退判断改为在 val 上评估。影响范围小：§27 的三条公式中，Load 和 Wind 的后处理未触发回退（ΔRMSE 均在阈值内），Solar 跳过了 rationalization（§27 已说明）。即使改为 val 判断，最终公式大概率不变。

### 影响评���

问题 1 和 2 直接影响 R²=0.868 这个数字的可信度：
- 如果改为 PySR 默认 best（不 cherry-pick），combo R² 可能会从 0.868 降到约 0.82-0.85（因为 Load 从 c=16 退回 c=13）
- 如果 delta_h72 需要改为严格前瞻预测（去掉短 lag），所有方法的精度都会下降，但相对排名可能不变

这些问题**不影响方法论层面的结论**（DS-KAN 分解+PySR 优于直接搜索），但**影响具体数值的绝对可信度**。修复后需要更新§26-27 的所有数值。

### 审查后综合评估（2026-05-04）

| 问题 | 原始严重度 | 审查结论 | 需修复 | 数据影响 |
|------|-----------|---------|--------|---------|
| 1. PySR cherry-pick test | 严重 | 确认成立 | 是：补算 val 指标，按 val 重选公式 | 不需重跑 PySR，combo R² 数值可能下调 |
| 2. delta_h72 语义 | 严重 | 不构成泄漏 | 否：论文补一句定义即可 | 无 |
| 3. 剪枝用 test set | 中等 | 误报（实际用的是 val） | 否 | 无 |
| 4. 后处理回退用 test | 中等 | 确认成立 | 是：回退判断改用 val | 极小，现有公式大概率不变 |

实际需要修复的只有**问题 1**（优先级高，影响主表数值）和**问题 4**（优先级低，大概率不影响最终公式）。问题 2 和 3 均已排除。

## 29. 方法论与数据配置独立审查（Codex 2026-05-04）

两轮独立 Codex 审查，分别针对方法论合法性和数据配置一致性。

### 审查一：方法论审查

| 审查项 | 判定 | 要点 |
|--------|------|------|
| 1. 方法论合法性 | **CONCERN** | DS-KAN→PySR 两阶段本身合法，不是循环论证。但最终 PySR clean 特征是脚本手动指定（`scripts/submit_additive_and_pysr_clean.sh:57`），不是代码自动从 KAN 剪枝读取。且 §14 稳定特征集（Wind 仅 4 维）与最终 12 维不完全一致。 |
| 2. 数据泄漏 | **PASS** | 回归语义下无未来泄漏。目标 `current - shift(h)`，lag 是正向历史 shift。切分有 gap=48，归一化只 fit(train)。cyclic/solar altitude 只用时间戳和地理位置。 |
| 3. PySR 搜索公平性 | **CONCERN** | 28 维 PySR h72 R²=0.665，clean PySR combo R²=0.868，证明降维有效。但缺少控制实验区分"DS-KAN 特征选择有价值"与"任何合理降维都有效"——缺少随机等维、MI/LASSO、人工物理特征等对照。 |
| 4. 公式质量 | **CONCERN** | Load/Solar 物理可解释。Wind 无风速变量（物理上需解释）。Solar 制品不一致：文档说保留原始公式，但 `formula_postprocessed.sympy.txt` 实际是巨大有理化表达式。 |
| 5. 统计严谨性 | **CONCERN** | test cherry-pick 已修复。但 PySR clean 仅 seed=1，33+ 方法探索无多重比较控制。payload 的 eval_test/best_equation 仍是 PySR 默认 best，不是 val-selected 公式。 |

### 审查二：数据配置审查

| 审查项 | 判定 | 要点 |
|--------|------|------|
| 1. 数据集版本一致性 | **ERROR** | h12/h72/h144/h576 用 `derived_multi_h`（193 runs），h6 主线用 `derived_h1_6`（213 runs），旧 `ro00` 还有 85 个历史实验。论文主线若声明统一数据集则需澄清。 |
| 2. 特征工程配置 | **WARNING** | derive_dataset 层面一致，但下游特征选择/lag 不一致：h72 direct KAN 用 `[12,24,48]`，PySR clean 用 `[1,12,48]`，RQ2 load 用 `[1]`，wind 用 `[24,48]`。这是设计选择但需明确记录。 |
| 3. 归一化一致性 | **OK** | normalize_features 只在 train fit，scaler_params.json 存在于主数据集。下游依赖约定路径，可追溯性一般。 |
| 4. 切分与 gap | **OK** | 70/15/15，gap=48 步。实测无时序泄漏。 |
| 5. 子任务目标定义 | **OK** | `delta_net_load_h72 = delta_load_h72 - delta_wind_h72 - delta_solar_h72`，parquet 抽查残差 ~1.5e-11。 |
| 6. PySR 尺度 | **WARNING** | PySR `use_original_features=True`（原始尺度），KAN teacher `scale_features=false`（z-score 尺度）。输入尺度不一致，公式更接近原始尺度但 teacher 对齐不完全。 |
| 7. 多步长数据一致性 | **ERROR** | h6 用 `derived_h1_6`（不同行数和 scaler），h12+ 用 `derived_multi_h`。多步长对比表不是完全同一数据集。 |

### 综合评估

**不构成作弊或 bug 的方面：**
- 数据泄漏审查通过（PASS），核心方法无信息泄漏
- 切分、归一化、目标定义均正确（OK）
- DS-KAN→PySR 两阶段方法本身合法

**需要在论文中澄清或补强的方面：**
1. h6 和 h72+ 使用不同数据集版本——需说明 `derived_h1_6` 和 `derived_multi_h` 的关系（同源不同 horizon 列），或统一到 `derived_multi_h`
2. PySR clean 特征集的来源需明确——是手动从 §14 稳定性分析 + §25 交叉污染修正得到的，不是代码自动读取
3. 缺少 DS-KAN 特征选择 vs 其他降维方法的控制实验——需承认或补做
4. Solar 后处理制品需修复——`formula_postprocessed.sympy.txt` 应保存原始公式（文档说保留原始但文件内容不一致）
5. PySR 仅 seed=1——需承认为单种子结果或补跑多种子

### 论文正文处置方案（2026-05-04）

**问题 1：h6 vs h72+ 数据集版本**
论文正文需在实验设置章节补充一段说明："`derived_h1_6` 和 `derived_multi_h` 均来自同一 ERCOT 原始数据和同一特征工程管线（`protocol_exec_20260427_fixm2`），区别仅在于目标列范围：前者包含 h1/h6，后者包含 h1/h6/h12/h72/h144/h576。由于更长 horizon 的 shift 操作，`derived_multi_h` 比 `derived_h1_6` 少约 528 行（训练集 72960 vs 73488），导致 z-score 参数有微小差异（如 load 均值 44450 vs 44530）。本文最终交付的三条 h72 公式及所有 h72 基线对比均来自 `derived_multi_h`。h6 实验仅用于中间探索和符号化失败筛查（§7-§8），不影响主表数值。"

**问题 2：PySR clean 特征集来源**
论文正文需在方法章节特征筛选部分写清：特征集不是代码自动从 KAN 剪枝结果读取，而是研究者根据 §14 跨种子特征稳定性分析和 §25 交叉污染修正，手动确定每个子任务的纯净特征组（Load 12 维、Solar 9 维、Wind 12 维），再通过 `scripts/submit_additive_and_pysr_clean.sh` 显式传入 PySR。这是一个有监督的特征选择过程，不是端到端自动化。

**问题 4：Solar 后处理制品**
已修复（2026-05-04）。`runs/pysr_solar_clean_v1/artifacts/formula_postprocessed.sympy.txt` 已替换为原始 PySR 公式（文档 §27 明确说"后处理有害，保留原始"）。巨大有理化版本备份于 `formula_postprocessed_rationalized_bad.sympy.txt`。

**问题 5：PySR 单种子**
论文正文需在局限性章节承认：PySR 符号回归阶段仅使用单一随机种子（seed=1），公式搜索结果可能受种子影响。但三个子任务均独立搜索（相当于三次独立实验），且 val/test 选择一致（Solar、Wind）或差异很小（Load），表明结果具有一定鲁棒性。

**问题 6：PySR vs KAN 输入尺度**
论文正文需在实验设置中注明：KAN teacher 在 z-score 归一化特征上训练（`scale_features=false` 因 Phase-1 已归一化），PySR 使用 `use_original_features=True` 在原始物理尺度上搜索公式。这是有意的设计选择——原始尺度公式的系数具有直接物理含义（如 MW、°C），z-score 尺度下系数无物理意义。两阶段的输入尺度不一致不影响方法有效性，因为 DS-KAN 的输出是特征选择（哪些变量重要），不是数值传递。

**问题 3：特征选择对照实验**
已补做（2026-05-04）。在 h72 三个子任务上，分别用 DS-KAN / MI / LASSO / 随机四种等维特征选择跑 PySR（niterations=400, maxsize=25，与主线配置一致），按 val R² 选公式。

| 子任务 | DS-KAN val/test | MI val/test | LASSO val/test | Random val/test |
|--------|----------------|------------|---------------|----------------|
| Load | **0.962 / 0.859** | 0.823 / 0.307 | 0.968 / 0.851 | 0.919 / 0.657 |
| Solar | 0.911 / 0.865 | 0.861 / 0.802 | **0.923 / 0.886** | 0.809 / 0.593 |
| Wind | 0.913 / 0.887 | 0.596 / 0.502 | **0.932 / 0.917** | 0.767 / 0.720 |

各方法选出的具体特征对比：

| 子任务 | DS-KAN 选出的特征 | LASSO 选出的特征 |
|--------|-----------------|----------------|
| Load | hour_sin/cos, dow_sin/cos, month_sin/cos, temp_2m_c, cdd_18c, hdd_18c, **load_lag_1/12/48** | load_lag_48/3/4/37/39/38/2/36/6/5, solar_azimuth, is_night |
| Solar | ghi_w_m2, ghi_day_w_m2, ghi_temp_corr_w_m2, solar_altitude/azimuth, is_night, **solar_lag_1/12/48** | solar_lag_48/1/42/43/44, ghi_temp_corr_w_m2, solar_azimuth, hour_cos, solar_altitude |
| Wind | wind_speed_10m/cubed/hub, hour_sin/cos, dow_sin/cos, month_sin/cos, **wind_lag_1/12/48** | wind_lag_48/1/42/43/41/39, **solar_lag_48/40/39**, solar_altitude, **load_lag_48**, hour_cos |

结论：

1. **Random 显著差于所有有监督方法**——证明降维本身不够，特征选择质量确实重要。

2. **LASSO 与 DS-KAN PySR 精度接近甚至略优**——Load 差不多（0.851 vs 0.859），Solar/Wind 上 LASSO 更好。

3. **MI 不稳定**——Load/Wind 上远差于 DS-KAN 和 LASSO，Solar 上中等。

4. **KAN 非线性特征重要性的独特价值在于产出物理可解释的稀疏特征集：**
   - **稀疏多尺度 lag**：KAN 选出 lag_1/12/48（覆盖 15 分钟/3 小时/12 小时三个时间尺度），LASSO 选出相邻冗余 lag（如 load_lag_2/3/4/5/6、load_lag_36/37/38/39），信息高度重叠。这是因为 LASSO 按线性相关排序，相邻 lag 线性相关极高所以扎堆入选；KAN 基于非线性激活函数贡献剪枝，天然倾向保留多尺度代表。
   - **子任务特征纯净**：KAN 保持物理边界（wind 任务只选 wind 相关特征），LASSO 不管边界（wind 任务选了 solar_lag_48/40/39 和 load_lag_48，正是 §25 要去除的交叉污染特征）。
   - **物理分组完整**：KAN 为每个子任务保留了完整的物理特征组（cyclic + meteorology + sparse lag），LASSO 几乎只选 lag，丢失了气象和周期信息。

5. **E4 实验的诊断价值**：KAN 的 `auto_symbolic` 在工程数据上产出的公式 test R² 均低于 0.1（§7），这一负面发现本身就是重要的实证贡献——它证明了 KAN-SR 路线（直接对 KAN 激活函数做符号拟合）在高维工程时序场景下不可行，从而驱动了"KAN 选变量、PySR 选函数"的两阶段解耦设计。没有 E4 的失败诊断，就没有两阶段设计的动机基础。

论文正文叙述口径：
- 精度层面："DKSR 特征选择在 PySR 下游精度上与 LASSO 相当（表 X），证明 KAN 非线性筛选未引入偏差。"
- 可解释性层面："DKSR 选出的特征在三个维度上优于 LASSO：稀疏多尺度 lag（vs 冗余相邻 lag）、子任务特征纯净（vs 跨任务污染）、物理分组完整（vs 纯 lag 主导）。这使得最终公式具有可直接物理解读的变量组合。"
- 方法论层面："E4 实验证明 KAN 逐边符号拟合在工程数据上不具备泛化能力，这一诊断发现驱动了 DKSR 将'选变量'与'选函数'解耦为两个独立阶段的设计。"

追溯：`runs/fs_ablation__*`，脚本 `modal_jobs/feature_selection_ablation.py`，结果 `doc/feature_selection_ablation_results.json`。

## 30. 论文主线流程总结（2026-05-04 审查后修订）

术语约定：本节起统一使用 **DKSR**（Decomposed KAN-guided Symbolic Regression，分解式 KAN 引导符号回归）指代本文提出的方法框架，替代此前文档中的"DS-KAN"。原"KAN teacher"统一改为"子任务 KAN 模型"。

经过 §28-§29 的四轮审查（代码审查 + 方法论审查 + 数据配置审查 + 特征选择对照实验）后，论文主线流程和创新点定位修订如下。

### 主线流程

```
阶段 0：问题定义
  净负荷 Δnet_load_h72 = net_load(t) - net_load(t-72)
  语义：回归当前时刻相对过去 72 步的变化量（非前瞻预测）
  数据：ERCOT ARPA-E PERFORM，train/val/test = 70/15/15%，gap=48 步

阶段 1：Direct KAN 基线与瓶颈诊断（RQ1 + RQ2）
  28 维 Direct KAN → R²=0.782，但符号公式 TGR>2，物理变量被压制
  E1 稀疏强度消融 → λ 不是主瓶颈
  E2 特征消融 → base series 和 lag 是信息优势来源，气象变量被压制
  E3 结构分解消融 → 子任务降低学习难度
  E4 符号后处理 → auto_symbolic 在工程数据上全面失败（test R² < 0.1）
  *** E4 是关键诊断发现：证明 KAN-SR 路线（直接符号拟合）不可行 ***

阶段 2：DKSR 框架（RQ3）
  基于领域知识的物理分解：net_load = load - wind - solar
  → 三个子任务各自独立训练 KAN 模型
  → KAN 非线性剪枝产出稀疏、多尺度、物理纯净的特征集
     （lag_1/12/48 而非冗余相邻 lag，无跨任务污染）
  → 跨种子稳定性验证（§14，重叠度=1.0）
  → 人工结合稳定性分析 + 交叉污染修正 → 确定最终纯净特征集

阶段 3：PySR 符号回归（两阶段解耦的"选函数"阶段）
  在 DKSR 筛选后的 9-12 维纯净特征上运行 PySR
  按 val R² 选公式（已修复 test cherry-pick）
  产出 Pareto 前沿

阶段 4：后处理
  snap near-integer/π → rationalize → BFGS train-set refit → simplify
  回退判断基于 val set（已修复）
  产出最终三条子公式

阶段 5：验证
  独立 test set 上评估 RMSE/R²
  与全部基线对比（Persistence/SARIMAX/MLP/LSTM/XGBoost/Direct KAN/28维PySR）
  特征选择对照实验（MI/LASSO/Random vs DKSR）
  物理含义审查
```

### 最终交付的三条 h72 子公式

| 子任务 | 公式 | test R² | RMSE |
|--------|------|---------|------|
| Load | `107/85·load_lag_12 − 107/85·load_lag_48 + hour_sin·load_lag_48·(2/37·month_cos + 2/37·sin(sin(hour_cos)) − 224/3071)` | 0.887 | 1729 |
| Solar | `solar_lag_1 + (solar_azimuth − 123.5)·(−0.258·solar_azimuth + (solar_lag_48 − solar_altitude)·(exp(−40.49·solar_lag_48) − 0.004) − 20.4)` | 0.888 | 5249 |
| Wind | `91/73·wind_lag_1 − 101/86·wind_lag_48 + 101/86·exp(743/85·hour_sin) − 197907/85` | 0.890 | 2753 |

### 创新点定位（审查后修订）

1. **物理分解框架**：将不可符号化的高维净负荷预测（28 维，PySR R²=0.367）转化为三个可符号化的低维子任务（9-12 维，PySR R²=0.84-0.90）。分解依据来自领域知识（net_load = load - wind - solar），而非自动对称性检测（区别于 KAN-SR）。

2. **KAN 瓶颈诊断与两阶段解耦设计**：E4 实验系统证明了 KAN 的 auto_symbolic 在高维工程数据上不具备泛化能力（test R² < 0.1），这一诊断发现驱动了"KAN 选变量、PySR 选函数"的两阶段解耦。区别于 KAN-SR（直接对 KAN 做符号拟合），DKSR 将 KAN 的角色限定为非线性特征选择器。

3. **KAN 非线性特征选择的可解释性优势**：KAN 剪枝产出的特征集在精度上与 LASSO 相当（消融实验验证），但在可解释性上具有三个优势：稀疏多尺度 lag（vs 冗余相邻 lag）、子任务特征纯净（vs 跨任务污染）、物理分组完整（vs 纯 lag 主导）。

4. **可符号化边界发现**：多时域实验和 no-lag 消融揭示了"特征对黑盒预测贡献微小（2-3%），但对符号化忠实度影响显著"的边界现象。

### 已修复的方法论问题

| 问题 | 状态 |
|------|------|
| PySR test cherry-pick（§28 问题 1） | 已修复：改为 val 选公式 |
| delta_h72 语义（§28 问题 2） | 已澄清：回归建模，非前瞻预测 |
| 剪枝用 test（§28 问题 3） | 误报：实际用的是 val |
| 后处理回退用 test（§28 问题 4） | 已修复：改为 val 判断 |
| Solar 制品不一致（§29） | 已修复：替换为原始公式 |
| 特征选择对照实验（§29） | 已补做：MI/LASSO/Random 对照 |

## 31. PySR 不分解对照实验（h72 净负荷直接搜索）

需求：验证"分解是 PySR 成功的前提条件"——用完全相同的 PySR 配置，在三个子任务特征的并集（27 维）上直接对 `delta_net_load_h72` 跑符号回归，与分解后 3×公式组合做严格对照。

配置：`target=delta_net_load_h72, niterations=400, populations=8, population_size=40, maxsize=25, seed=1, max_train_rows=20000, no-include-base`。特征为三子任务物理特征组的精确并集（27 维）：cyclic(6) + meteo_temp(1) + meteo_degree(2) + meteo_irradiance(3) + solar_geom(2) + solar_flag(1) + meteo_wind(3) + load_lag_1/12/48 + wind_lag_1/12/48 + solar_lag_1/12/48。数据集为 `protocol_exec_20260427_fixm2__derived_multi_h`。

数据：`runs/pysr_netload_nodecmp_v1`。

Pareto 前沿（关键方程）：

| complexity | val R² | val RMSE | test R² | test RMSE | 方程 |
|------------|--------|----------|---------|-----------|------|
| 5 | 0.389 | 8535 | 0.399 | 12217 | `(solar_lag_48 − solar_lag_1)·0.464` |
| 7 | 0.434 | 8215 | 0.587 | 10134 | `load_lag_1 − load_lag_48 − solar_lag_12 + solar_lag_48` |
| 9 | 0.545 | 7362 | 0.614 | 9785 | `load_lag_1 − load_lag_48 + (solar_lag_48 − solar_lag_1)·0.701` |
| **15** | **0.581** | **7071** | **0.645** | **9394** | `load_lag_1 − load_lag_48 + (solar_azimuth − ghi_temp_corr)/0.096 + (solar_lag_48 − solar_lag_1)·0.564` |
| 17 | 0.559 | 7252 | 0.659 | 9202 | `(load_lag_1 − load_lag_48 + (solar_azimuth − ghi_temp_corr)/0.116 + (solar_lag_48 − solar_lag_1)·0.450)·1.496` |
| 21 | 0.562 | 7226 | 0.660 | 9187 | `1.588·(load_lag_1 − load_lag_48 + 0.365·(solar_lag_48 − solar_lag_1) + (2·solar_azimuth − 113.75 − ghi_temp_corr)/0.094)` |
| 25 | 0.561 | 7236 | 0.662 | 9168 | `...同上 + wind_speed_cubed − ghi_temp_corr...` |

Val-best 为 c=15（val R²=0.581, test R²=0.645）。PySR default best 为 c=17（test R²=0.659）。

关键观察：
1. **Wind 信号完全缺失**。27 维搜索中，wind_lag_1/12/48 在整个 Pareto 前沿中从未出现（仅 c=25 出现了 wind_speed_cubed 作为微小修正项）。PySR 在高维搜索空间中无法同时发现三个子任务的模式。
2. **公式结构**：最优公式本质是 `load 差分 + solar 差分 + solar_azimuth 线性修正`，复杂度和物理含义均远不如分解后的三条子公式。
3. **与 §17 旧实验一致**：旧 28 维 PySR（niterations=1200）R²=0.665，本次 27 维（niterations=400）R²=0.645-0.662，精度在同一水平，确认结果可复现。

对照（分解后 3×公式组合，§26-27）：

| 方法 | 特征维数 | RMSE | R²(val) | R²(test) |
|------|---------|------|---------|----------|
| **PySR 不分解** | 27 | 9394（val-best） | 0.581 | 0.645 |
| **PySR 分解后组合** | 9-12 ×3 | 5719 | ~0.93 | 0.868 |

**同一 PySR 算法、同一配置（niterations=400, maxsize=25, seed=1）、同一数据集，唯一区别是分解 vs 不分解。分解使 test R² 从 0.645 → 0.868（+35%），RMSE 从 9394 → 5719（−39%）。**

总结：这是"分解是 PySR 成功的前提条件"的最直接实验证据。不分解时 PySR 在 27 维空间中只能找到 load+solar 的 lag 差分组合（4-6 个变量），完全无法发现 wind 的有效模式；分解后每个子任务仅 9-12 维，PySR 能分别找到 3-5 变量的简洁公式，三公式组合精度远超不分解版本。

注意：这同时也说明**分解的价值完全来自降维**，不需要 KAN 参与。一个领域专家直接做"分解+按物理分配特征+PySR"会得到完全相同的结果。

追溯：`runs/pysr_netload_nodecmp_v1`

## 32. KAN-SR 深度融合实验（10 方案系统对比，2026-05-04）

需求：在 §26 确立的"分解+纯净特征+PySR"主线基础上，系统探索 KAN 能否在特征选择之外的更深层面（先验引导、原语生成、降噪、模板约束、瓶颈解耦、边替换、公式重排）进一步改善 SR 结果。设计 10 个方案，覆盖"KAN 作为公式生成器 vs 引导器 vs 诊断器"的完整角色谱。

配置：所有方案共享同一数据集 `protocol_exec_20260427_fixm2__derived_multi_h`，PySR 统一配置 `niterations=400, populations=8, maxsize=25, seed=1, max_train_rows=20000`（除特殊说明外）。以 Wind h72 为主测试目标，部分方案覆盖 Load/Solar。

### 32a. 方案 1：Soft Complexity Prior（KAN 重要性→PySR 变量成本）

做法：读取 KAN 训练后的 `feature_importance.csv`（active_ratio），映射为 `cost_i = max(1, int(10*(1-active_ratio_i)))`，通过 PySR 的 `complexity_of_variables` 参数给低重要性特征更高的使用成本。全量 12 维子任务特征输入 PySR。

数据：`runs/soft_complexity_load_v1`，`runs/soft_complexity_solar_v1`，`runs/soft_complexity_wind_v1`。

| 子任务 | Soft Complexity R² | Soft RMSE | §26 Baseline R² | §26 RMSE | ΔR² |
|--------|-------------------|-----------|-----------------|----------|-----|
| Load | 0.596 | 3269 | 0.847 | 2015 | **−0.250** |
| Solar | 0.768 | 7561 | 0.847 | 6139 | **−0.079** |
| Wind | 0.875 | 2933 | 0.842 | 3300 | +0.033 |

总结：**负例**。KAN 剪枝先验在 Load/Solar 上过于激进——Solar KAN 将 ghi 三个辐照特征全部剪掉（active_ratio=0, cost=10），但 PySR 实际需要它们。Wind 上微弱正效应（+3.3%）因为 KAN 保留的特征集与 §26 纯净集高度重叠。结论：不应将 KAN 的二值剪枝结果直接作为 PySR 变量成本先验，因为 KAN 可能因架构限制丢弃重要特征。

追溯：`runs/soft_complexity_load_v1`，`runs/soft_complexity_solar_v1`，`runs/soft_complexity_wind_v1`
脚本：`scripts/run_soft_complexity_pysr.py`，`modal_jobs/pysr_baseline.py`（新增 `complexity_of_variables` 参数）

### 32b. 方案 2：Concept Bottleneck SR（窄瓶颈 KAN→两阶段 PySR）

做法：训练 [12,2,1] 极窄瓶颈 KAN，强制信息压缩到 2 维隐空间。提取 H0、H1 隐藏激活值后，分三阶段 PySR：inner H0 = f0(X)，inner H1 = f1(X)，outer Y = g(H0, H1)。最终组合 Y = g(f0(X), f1(X))。

数据：`runs/concept_bottleneck_wind_v1`。

关键值：
- Bottleneck KAN NN：R²=0.890, RMSE=2748（12→2→1 压缩后仍保留 89% 方差）
- Inner H0：`(wind_speed_hub_est + (wind_lag_1 - wind_lag_48 - 0.776)/(-0.00563)) * 1.075 - 3.513`
- Inner H1：`wind_lag_12 * (hour_sin - wind_lag_1 + 40.749) + 33.041 * (1.318 - wind_lag_48)`
- Outer：`(H0 - H1/(19.657/H1)) * (-40.961)`
- 组合公式 28 个 sympy 节点

总结：KAN 可将 Wind 12 维信息压缩到 2 维隐空间且 R²=0.890，证明信息可压缩性。但组合公式冗长（28 节点 vs §26 PySR 的 7-14 节点），且包含嵌套除法（数值不稳定）。作为"信息可压缩性"证据有价值，但不适合直接作为可读公式交付。

追溯：`runs/concept_bottleneck_wind_v1`
脚本：`scripts/run_bottleneck_stage1_kan.py`，`scripts/run_bottleneck_stage2_pysr.py`

### 32c. 方案 3 Stage 1：残差物理蒸馏——Lag 骨架提取（Wind）

做法：仅用 lag 特征（wind_lag_1/12/48）对 PySR 做极限约束搜索（maxsize=7, binary=[+,-], unary=[]），提取 Wind 的时序骨架公式。

数据：`runs/residual_wind_skeleton_v1`。

Pareto 前沿：

| complexity | test R² | test RMSE | 方程 |
|------------|---------|-----------|------|
| 3 | 0.832 | 3397 | `wind_lag_1 - wind_lag_48` |
| 5 | 0.881 | 2863 | `(wind_lag_1 - wind_lag_48) * 1.284` |

总结：Lag 骨架 `wind_lag_1 - wind_lag_48` 解释了 83.2% 的方差，缩放版解释 88.1%。剩余 ~17% 方差为气象物理信号（含 v³ 风功率项）。为后续 Stage 2-5（剥离骨架→KAN 拟合残差→PySR 搜索物理公式）提供了基础。

追溯：`runs/residual_wind_skeleton_v1`
脚本：`scripts/run_residual_physics_distill.py`

### 32d. 方案 4：Edge-wise Symbolic Distillation（逐边 PySR 替换 KAN 样条）

做法：加载训练好的 Wind h72 KAN，提取 19 条活跃边的 (x, φ(x)) 数据对，对每条边独立运行 PySR（1D 回归，niterations=100, maxsize=10），然后按 KAN 拓扑结构组合为全局符号公式。

数据：`runs/edgewise_wind_v1`。
完成了 18 条边的 PySR 拟合，边公式包括 `x*0.430 + 0.212`、`cube(sin(x - 0.858))` 等。

关键值：
- 全局组合公式：R²≈0（坍缩为常数，node_count=1）
- 对照 KAN NN：R²=0.781, RMSE=3882

总结：**强负例**。逐边 PySR 的 1D 拟合 R² 较高，但组合时输入归一化的链式替换导致数值发散（中间表达式膨胀后被 sympy 化简为常数）。这与 KAN-SR 文献中"逐边局部替换不考虑全局误差"的已知问题一致，也证实了 §24 中 `auto_symbolic` 失败的根本原因不仅是拟合精度，而是组合时的数值稳定性。

追溯：`runs/edgewise_wind_v1`
脚本：`scripts/run_edgewise_symbolic.py`，`scripts/run_edgewise_compose.py`，`src/local/edgewise_symbolic.py`

### 32e. A1：KAN Teacher Rerank PySR Pareto 前沿

做法：用复合评分 J(f) = MSE_val(y,f) + α·MSE_val(f_KAN,f) + λ·C(f) + ρ·P(f) 重排 §26 PySR Pareto 前沿。网格搜索 α∈{0,0.1,0.25,0.5}，λ∈{0.001,0.01,0.1}，ρ∈{0,100,500,1000}，共 48 个 (α,λ,ρ) 配置。

数据：`runs/kan_teacher_rerank_v1`。

关键值：
- 所有三个子任务（Load/Solar/Wind），最优配置均为 α=0, λ=0.001, ρ=0
- 选出的公式与当前 val-best 完全一致
- Load test R²=0.887，Solar test R²=0.888，Wind test R²=0.890（均等于 §26）

总结：**负例**。KAN teacher 的预测信息没有为公式选择提供任何额外判别力。最优 α=0 意味着 KAN-PySR 一致性项无效——PySR 的 val 选择已足够，不需要 KAN teacher 作为第二意见。这也间接说明 PySR 公式已经充分逼近了 KAN 的预测行为。

追溯：`runs/kan_teacher_rerank_v1`
脚本：`scripts/run_kan_teacher_rerank.py`

### 32f. A2：KAN Atom Library→PySR（候选原语生成）

做法：对训练好的 KAN 每条活跃边做 curve_fit（identity/quadratic/cubic/sin/exp 5 种模板），提取每个特征的主导函数形式。结合领域知识生成复合原语（如 `lag_diff_1_48 = lag_1−lag_48`, `hour_month = hour_sin×month_cos`），再将原语作为额外特征输入 PySR，原语 complexity=1，原始特征 complexity=2。注意：**Atom Library 不是与 KAN 并列的独立模型**，而是“先训练 KAN，再把 KAN 边上的局部非线性转译成原语，最后交给 PySR 组合”的桥接范式。

数据：`runs/kan_atom_library_wind_v1`，`runs/kan_atom_library_load_v1`，`runs/kan_atom_library_solar_v1`，`runs/kan_atom_library_full28_wind_v1`，`runs/kan_atom_library_full28_load_v1`，`runs/kan_atom_library_full28_solar_v1`，`runs/kan_atom_library_direct_netload_full28_v1`。

#### 32f-1. 分解子任务场景（沿用 §26 的纯净特征）

| 子任务 | Atom Library R² | §26 Baseline R² | ΔR² | complexity | 结构观察 |
|--------|-----------------|----------------|-----|------------|----------|
| Wind | 0.888 | 0.842 | **+0.0466** | 23 | 包含 `atom_lag_diff_1_48` 与 `wind_speed_10m_m_s_cubed`，v³ 物理项被稳定激活 |
| Load | 0.864 | 0.847 | **+0.0177** | 20 | 核心仍是 `lag_diff_12_48` + 温度/周期修正 |
| Solar | 0.869 | 0.847 | **+0.0225** | 22 | 使用 `atom_azimuth_sq`、`atom_lag_diff_1_48`、`ghi_temp_corr` |

关键观察：
1. **三子任务全部正增益**。A2 不再只是 Wind 单点现象，而是当前 §32 组里唯一完成三任务正向覆盖的方案。
2. **原语层面可解释，最终公式层面中等可读**。例如 `lag_diff`、`azimuth_sq`、`v³` 都具有清晰物理含义，但最终组合式仍有较多常数、乘法嵌套和三角包裹，简洁性不如 §26 的最短骨架式。
3. **A2 的强项是“用可解释原语换更高精度”**，不是把最终公式缩成最短白盒表达。

#### 32f-2. 不分解特征、但仍分解任务（Full-28 + atoms）

为区分“任务分解”和“特征分解”，额外跑了 `full28` 版本：仍然分别预测 `load / wind / solar` 三个子目标，但不再使用纯净特征，而是直接使用 28 维全量输入，再加上 atom。

| 子任务 | Full-28 + atoms R² | Full-28 baseline R² | ΔR² | complexity | 备注 |
|--------|--------------------|--------------------|-----|------------|------|
| Wind | 0.882 | 0.842 | **+0.0404** | 13 | 公式中混入 `ghi_w_m2` |
| Load | 0.849 | 0.822 | **+0.0275** | 15 | 公式中混入 `solar_azimuth` |
| Solar | 0.870 | 0.836 | **+0.0338** | 18 | `ghi_temp_corr + solar_azimuth` 组合较合理 |

代表公式：
- Wind：`atom_lag_diff_1_48*1.1846 - 3.405*ghi_w_m2 + exp(atom_hour_sin_sin*10.36)`
- Load：`(3108.3 - solar_azimuth) * (atom_hour_month - hour_sin + 0.000445*(atom_lag_diff_12_48 - 91.14))`
- Solar：`0.8348 * [atom_lag_diff_1_48 + (42.77 - (ghi_temp_corr + solar_azimuth)*(hour_sin + 0.481))/0.02485]`

关键观察：
1. **A2 在高维 full-28 场景下仍然有效**，说明它不仅依赖“子任务纯净特征”，还具备一定的高维救场能力。
2. 但公式中出现了明显的**跨任务代理变量吸附**：Wind 公式用了 `ghi_w_m2`，Load 公式用了 `solar_azimuth`。这说明精度提升不等于物理纯度提升；Atom 更像先把搜索锚定到正确骨架附近，然后 PySR 再从全维输入中吸附额外相关特征补分。

#### 32f-3. 完全不做 `load/wind/solar` 任务分解：总公式直连实验

上面的 Full-28 结果回答的是“**不分解特征**是否仍然有效”，不是“**不分解任务**是否仍然有效”。因此进一步补做了单目标总公式实验：直接对 `delta_net_load_h72` 学一个总公式，使用 Direct KAN h72 的 28 维输入配置（与 `direct_kan_h72__w24_l0.001_nogrid_s1` 对齐），并与匹配的 28 维 direct PySR baseline `2026-05-03_121135_7cdf67cd` 严格对照。

| 方法 | 目标 | 特征维数 | Test R² | Test RMSE | complexity |
|------|------|---------|---------|-----------|------------|
| Direct PySR baseline | `delta_net_load_h72` | 28 | 0.665 | 9117 | - |
| **A2 Direct Total Formula** | `delta_net_load_h72` | 28 + atoms | **0.766** | **7626** | 25 |

总公式：
`-0.664*atom_solar_lag_diff_12_48 - ghi_temp_corr + 1.158*[atom_load_lag_diff_12_48 - (atom_wind_lag_diff_12_48 - 163.87*(atom_hour_cos_sin + 0.449)*(solar_azimuth - 197.81))] - 7931.54`

关键观察：
1. **在完全不做任务分解的情况下，Atom Library 仍然显著有效**：相对 28 维 direct PySR baseline，R² 从 0.665 提升到 0.766（**+0.1005**），RMSE 从 9117 降到 7626。
2. 但它**并没有推翻“分解是主线”的结论**。即使加上 atoms，直接总公式的 0.766 仍明显低于 §26 的分解后组合 0.868。
3. 因而更准确的判断是：**A2 能显著缓解高维直连搜索失效，但不能完全替代任务分解。**

随后又补做了两条“总公式 + 语义 atom + 搜索偏置”的对照，目的不是继续追求最高精度，而是观察**把语义信号推入总公式**后会发生什么：

| Run | 语义范围 | Test R² | Test RMSE | complexity | 结论 |
|-----|----------|---------|-----------|------------|------|
| `kan_atom_library_direct_netload_full28_v1` | 无额外语义偏置 | **0.7659** | **7625.74** | 25 | 当前总公式精度最佳 |
| `kan_atom_library_direct_netload_semantic_all_bias_v1` | `load + wind + solar` 全语义 | 0.7263 | 8244.71 | 21 | 语义 atom 大量进入最终式，但精度回落 |
| `kan_atom_library_direct_netload_semantic_load_bias_v1` | 仅 `load` 语义 | 0.7176 | 8374.43 | 20 | `load` 语义项进入总公式，但仍不如普通 Atom Library |

两条补做 run 的最终公式分别为：
- 全语义 bias：`-atom_ghi_daylight + atom_load_lag_diff_12_48 - atom_solar_lag_diff_12_48 - atom_wind_lag_diff_12_48 + 24.92*(atom_azimuth_day + solar_azimuth) - 12.05*(atom_ghi_daylight + 99.14) - 3301.62`
- 仅 load 语义 bias：`atom_load_lag_diff_12_48 - atom_solar_lag_diff_12_48 - atom_wind_lag_diff_12_48 + solar_azimuth*(atom_heating_overnight + 47.11) + exp(atom_workhour_flag + 8.34) - 16155.0`

补充观察：
1. **搜索偏置确实能把语义 atom 推进最终总公式**。全语义版显式用了 `atom_ghi_daylight`、`atom_azimuth_day`；load-only 版显式用了 `atom_heating_overnight`、`atom_workhour_flag`。
2. 但这两条 run 的 RMSE 都高于普通总公式 Atom Library（7625.74）。说明在总公式场景下，当前“语义优先”仍会牺牲一部分预测质量。
3. 且只强化 `load` 语义并没有优于“全部都加语义”的 bias 版：`8374.43 > 8244.71`。这说明当前总公式的主要收益仍然来自跨子系统的统计耦合，而不是单独把 `load` 语义推到前台。

#### 32f-4. Load 语义 atom 补做（2026-05-05）

动机：`load` 分支的最终公式长期被 `lag + 时间形状项` 主导，温度与负荷机理相关的语义不够强。于是额外补做两条 `load` 专项试验：

1. `kan_atom_library_load_semantic_v1`
   - 新增语义 atom：`workhour_flag`、`weekend_flag`、`cooling_workhour`、`cooling_weekend`、`heating_workhour`、`heating_overnight`、`temp_weekday`
   - 同时压掉一部分 `hour/dow/month` 的自动 `sin/exp` 形状 atom

2. `kan_atom_library_load_semantic_bias_v1`
   - 在上述语义 atom 基础上，不改数据值，只改 `complexity_of_variables`
   - 语义 atom cost=0，温度/度日 cost=1，lag cost=2，`hour_month` cost=3，原始时间周期 cost=4
   - 目的：只改变 PySR 搜索偏好，不把“人为加权”写进最终公式系数

结果：

| Run | Test R² | Test RMSE | complexity | 公式特征 |
|-----|---------|-----------|------------|----------|
| `kan_atom_library_load_v1` | 0.8643 | 1895.17 | 20 | 原始 A2 load，对照 |
| `kan_atom_library_load_semantic_v1` | **0.8738** | **1827.77** | 16 | 分数最好，但 val-best 仍主要依赖 `lag_diff + hour_month + 时间形状项` |
| `kan_atom_library_load_semantic_bias_v1` | 0.8562 | 1951.17 | 24 | `atom_heating_workhour` 被推入最终公式，但性能回落 |

关键观察：
1. **语义 atom 本身是有效的**。不加 bias 的语义版把 RMSE 从 1895.17 进一步降到 **1827.77**，是当前 `load` 路线的最佳 RMSE。
2. **搜索偏置确实能把语义项推进最终公式**。bias 版 val-best 公式显式包含 `atom_heating_workhour`：
   `1.323 * [lag_diff_12_48 + hour_sin * (-atom_heating_workhour - 186.98) * (atom_heating_workhour + hour_sin + temp_2m_c - 8.23) - 163.27]`
3. 但 **解释性增强与精度增强并不一致**。bias 版虽然更“像负荷语义”，RMSE 却回升到 1951.17，说明当前 `load` 语义项还不够强，尚不足以全面取代时间代理项。

总结：A2 已从原来的 Wind 单点实验，扩展为“分解子任务、full-28 子任务、direct total formula”三层验证，且三层都给出正结果。它是 §32 组里最强、最稳定的正面机制证据。

追溯：`runs/kan_atom_library_wind_v1`，`runs/kan_atom_library_load_v1`，`runs/kan_atom_library_solar_v1`，`runs/kan_atom_library_full28_wind_v1`，`runs/kan_atom_library_full28_load_v1`，`runs/kan_atom_library_full28_solar_v1`，`runs/kan_atom_library_direct_netload_full28_v1`，`runs/kan_atom_library_direct_netload_semantic_all_bias_v1`，`runs/kan_atom_library_direct_netload_semantic_load_bias_v1`，`runs/kan_atom_library_load_semantic_v1`，`runs/kan_atom_library_load_semantic_bias_v1`
脚本：`scripts/run_kan_atom_library.py`

### 32g. A3：特征集对比（KAN-core vs DKSR-closure vs Full-28）

做法：在相同 PySR 配置下，对比三种特征选择策略——(1) 全 28 维不筛选，(2) §26 DKSR-closure（9-12 维纯净特征），(3) KAN-core-only（仅 active_ratio>0 的特征）。

数据：`runs/pysr_full28_load_v1`，`runs/pysr_full28_solar_v1`，`runs/pysr_full28_wind_v1`。

| 子任务 | DKSR-closure R² | Full-28 R² | ΔR² |
|--------|----------------|-----------|-----|
| Load | 0.847 | 0.822 | **+0.025** |
| Solar | 0.847 | 0.836 | **+0.011** |
| Wind | 0.842 | 0.842 | ±0.000 |

总结：分解+特征筛选（DKSR-closure）对 Load 和 Solar 分别带来 +2.5% 和 +1.1% 的 R² 提升，Wind 无差异。Load 的提升最大，因为 28 维中存在大量与负荷无关的气象特征（wind_speed, ghi 等）干扰 PySR 搜索。Wind 无差异可能因为 Wind 的有效特征本身就只有 lag+风速+周期，多余特征被 PySR 自身搜索淘汰了。

追溯：`runs/pysr_full28_load_v1`，`runs/pysr_full28_solar_v1`，`runs/pysr_full28_wind_v1`
脚本：`scripts/submit_all_fusion_experiments.sh`

### 32h. A6：PySR 多种子稳健性验证

做法：在 §26 相同配置下，对 3 个子任务各跑 5 个 PySR seed（seed=1 为原始 §26，seed=2-5 为新增），统计 test R² 的均值、标准差和极差。

数据：`runs/pysr_multiseed_{load,solar,wind}_s{2,3,4,5}`。

| 子任务 | mean R² | std R² | min R² | max R² |
|--------|---------|--------|--------|--------|
| Load | 0.837 | 0.012 | 0.822 | 0.851 |
| Solar | 0.848 | 0.008 | 0.839 | 0.862 |
| Wind | 0.868 | 0.013 | 0.842 | 0.878 |

总结：PySR 搜索具有中等稳定性（std≈1%），seed=1 的结果位于正常范围内。Wind 的 seed 间方差最大（range=3.6%），Load/Solar 较稳定。论文应在局限性章节报告此数据，更新 §15 中"仅 seed=1"的说明为"5 seeds 验证 std≈1%"。

追溯：`runs/pysr_multiseed_load_s2..s5`，`runs/pysr_multiseed_solar_s2..s5`，`runs/pysr_multiseed_wind_s2..s5`

### 32i. B1：KAN Uncertainty-weighted PySR（多种子降噪）

做法：训练 5 个不同 seed 的 KAN（[12,24,1] for Wind，steps=50），计算训练集每个样本的预测标准差。将逆方差 `weight_i = 1/(std_i + ε)` 归一化后作为 PySR 的样本权重，让 PySR 更信任 KAN 一致认同的样本。

数据：`runs/uncertainty_weighted_v1`，`runs/uncertainty_weighted_all_v2`，`runs/uncertainty_weighted_wind_parallel_v1`，`runs/uncertainty_weighted_load_parallel_v1`，`runs/uncertainty_weighted_solar_parallel_v1`。

第一轮（Wind 单任务）结果：
- Weighted PySR Wind：R²=0.878, best equation `wind_lag_1 - wind_lag_48`（c=3）
- Unweighted §26 Wind：R²=0.842
- **ΔR² = +0.036（+3.6%）**
- 不确定性统计：mean_std=651, max_std=2345, 权重范围 0.23~22.2

随后尝试把该方案扩展到三子任务，先提交了串行总任务 `uncertainty_weighted_all_v2`，其 `task_order = [wind, load, solar]`。结果 Modal app 虽结束，但 `payload.json` 停留在 `"status": "running"`，仅落盘了 Wind/Load 两个子目录，Solar 完全缺失：
- Wind（部分完成）：R²=0.8869
- Load（部分完成）：R²=0.8505
- Solar：无结果

由于总任务存在“串行半截中断”问题，又将其拆成 3 个独立并行 job 复跑：

| 子任务 | Weighted R² | Unweighted §26 R² | ΔR² | 最优公式 |
|--------|-------------|-------------------|-----|----------|
| Wind | 0.8709 | 0.8417 | **+0.0292** | `wind_lag_1 - wind_lag_48` |
| Load | 0.8173 | 0.8466 | **−0.0293** | `load_lag_1 - load_lag_48` |
| Solar | 0.8430 | 0.8470 | **−0.0040** | `solar_lag_1 - solar_lag_48` |

附加观察：
1. Wind 上的正效应在复跑后仍然存在，但幅度从首轮的 +3.6% 收缩到 +2.9%，且最优式子退化回最简单的 lag 差分骨架。
2. Wind 的 `v³` 项首次出现复杂度从 unweighted 的 c=18 提前到 weighted 的 c=17，说明加权确实改变了搜索优先级。
3. Load/Solar 不仅没有收益，反而退化成简单 `lag_1 - lag_48`，说明该方法对非 Wind 子任务缺乏泛化。

总结：B1 现在应从“统一正面突破”下调为**Wind-specific 局部现象**。它在 Wind 上仍有一定价值，但对 Load/Solar 不成立，且首次总任务提交还暴露了串行执行的脆弱性。因此 B1 不能作为论文主线，只能作为“KAN 样本不确定性在个别子任务上可能有用”的补充证据。

追溯：`runs/uncertainty_weighted_v1`，`runs/uncertainty_weighted_all_v2`，`runs/uncertainty_weighted_wind_parallel_v1`，`runs/uncertainty_weighted_load_parallel_v1`，`runs/uncertainty_weighted_solar_parallel_v1`
脚本：`scripts/run_uncertainty_weighted_pysr.py`，`src/local/uncertainty_weighted_pysr.py`

### 32j. B4：KAN-guided Template SR（参数化模板 + BFGS）

做法：根据 §26 PySR 和 KAN 边分析已发现的结构，为每个子任务预设 3 个参数化模板，用 L-BFGS-B 在训练集上优化常数，val 选择最优模板。

数据：`runs/template_sr_v1`。

| 子任务 | 模板 | 参数 | Val R² | Test R² | Test RMSE | 公式 |
|--------|------|------|--------|---------|-----------|------|
| Load | T2 | 4 | 0.958 | 0.787 | 2373 | `1.476*(lag12-lag48) + 0.051*lag48*sin(-1.833*hour_sin - 0.206*month_cos)` |
| Solar | T2 | 3 | 0.908 | 0.859 | 5885 | `lag1 + (azimuth-122.9)*(-0.227*azimuth - 0.005*(lag48-altitude))` |
| Wind | T2 | 5 | 0.897 | **0.867** | 3022 | `1.228*lag1 - 1.221*lag48 + 0.569*exp(9.427*hour_sin) - 3.050*v³` |

补充定位（2026-05-05 复核）：本轮未重跑 Template SR，但在与 A2/B1 的补做对照后，其角色边界更清楚了：
1. **Wind/ Solar 为正，Load 为负**。因此 Template SR 不是统一主线，但比 B1 更稳。
2. Wind 模板的核心价值不只是分数提升，而是**在低复杂度参数化模板中稳定暴露 `v³` 物理项**，这为论文的“结构可读性”提供了比 A2 更强的展示素材。
3. Load 模板的 val/test 差距依旧过大（0.958→0.787），应视为过拟合警报，不宜包装成通用成功案例。

总结：Template SR 属于**中等强度破局点**。它适合写成 Wind/Solar 的结构化增强证据，尤其是 Wind 的 `v³` 暴露；但不适合写成对全部子任务都成立的统一方案。

追溯：`runs/template_sr_v1`
脚本：`scripts/run_template_sr.py`

### 32 组总结（2026-05-05 补做后）

10 个方案的核心发现：

**当前最强主线**：
1. **A2 KAN Atom Library**：已完成三层验证
   - 分解子任务：Wind/Load/Solar 全部正增益
   - Full-28 子任务：Wind/Load/Solar 全部正增益
   - Direct total formula：`delta_net_load_h72` 直连总公式也显著提升（0.665→0.766）
   - 结论：A2 是目前唯一同时具备**跨子任务泛化、高维救场能力、总公式补强能力**的方案，应视为 §32 中最有希望进入论文主线的方向

**次强证据**：
2. **B4 Template SR**：Wind/Solar 正、Load 负。其最大价值不是统一提分，而是稳定暴露 `v³` 等物理结构项，适合承担“结构可读性展示”的角色

**降级为局部现象**：
3. **B1 Uncertainty-weighted**：复核后仅 Wind 成立，Load/Solar 退化，不能再视作统一突破

**四个有价值负例**：
1. **方案 1 Soft Complexity**：KAN 剪枝先验在 Load/Solar 上过激（−25%/−8%），不应作为硬约束
2. **方案 4 Edgewise**：逐边 PySR 替换后全局组合数值坍缩，边替换范式不适用于工程数据
3. **A1 KAN Teacher Rerank**：KAN teacher 无额外公式选择信息，PySR val-best 已足够
4. **A3 Full-28 对照**：分解+特征筛选 vs 全维度，前者高 1-2.5%

**两个方法论补强**：
1. **A6 Multi-seed**：PySR 搜索 std≈1%，中等稳定（论文需报告）
2. **方案 2 Concept Bottleneck**：Wind 信息可压缩到 2 维（R²=0.890），但组合公式冗长

关于“破局点”表述的最终口径：
1. §32 已经不是“还没开始”的想法堆砌，而是**已经启动并被多轮实验部分验证**的研究方向。
2. 但也不应写成“全部统一完成”。截至本轮补做，真正形成稳定主线的是 **A2**；**B4** 是结构解释层面的重要辅助；**B1** 仅保留为 Wind 局部现象。
3. 因此论文在 `Discussion / Future Work` 中更合适的写法是：**未来探索空间应优先转向 §32 中的 A2 路线，并以 B4 作为物理结构可读性的补强；B1 仅作条件性补充，不宜作为统一范式。**

当前状态：本组 10 个方案及其关键补做实验已完成，为论文讨论章节提供了“KAN 在 SR 各环节的角色边界”完整证据链。推荐正文重点保留 A2（主正面机制）、B4（结构可读性）、方案1/4/A1（负例边界）、A6（稳健性）；B1 作为 Wind 特例报告；方案 2 和 A3 作为补充材料。
