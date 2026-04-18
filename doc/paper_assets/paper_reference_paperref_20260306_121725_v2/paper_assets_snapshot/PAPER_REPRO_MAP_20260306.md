# Paper Repro Map (2026-03-06)

本文件把本轮论文交付用到的关键图表、run_id 与生成命令固定下来，避免正文与附录引用漂移。

| 资产 | run_id / 输入 | 生成命令 | 输出路径 |
|---|---|---|---|
| 主结果对比表 | `2026-03-01_151000_kan_nobase_nogrid_gpu` / `2026-03-01_155600_baseline_mlp_match_kan151000` / `2026-03-01_160200_sym_strict_r2_0_995__kan151000` | `python3 scripts/evaluate_runs.py --run runs/2026-03-01_151000_kan_nobase_nogrid_gpu --run runs/2026-03-01_155600_baseline_mlp_match_kan151000 --run runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000 --out-dir doc/paper_assets/paper_delivery_20260306` | `doc/paper_assets/paper_delivery_20260306/comparison_table.csv` |
| S3四对象闭环表 | `2026-03-01_151000_kan_nobase_nogrid_gpu` / `2026-03-01_160200_sym_strict_r2_0_995__kan151000` / `paperref_20260306_121725_v2__s3_combo_net_load` / `paperref_20260306_121725_v2__s3_combo_net_load__formula` | 固化闭环快照（direct 对象取 canonical 主表，S3 对象取 paperref 正式 comparison table） | `doc/paper_assets/paper_delivery_20260306/s3_main_comparison_20260417.csv` |
| S3四对象闭环图 | `doc/paper_assets/paper_delivery_20260306/s3_main_comparison_20260417.csv` | `python3 scripts/render_paper_delivery_figures.py --s3-closure-csv doc/paper_assets/paper_delivery_20260306/s3_main_comparison_20260417.csv --out-dir doc/paper_assets/paper_delivery_20260306` | `doc/paper_assets/paper_delivery_20260306/s3_formula_closure_20260417.png` |
| 协议 ledger | 主文证据对象定义 + split/lag/statistics unit 约束 | 固化 protocol ledger 快照 | `doc/paper_assets/paper_delivery_20260306/protocol_ledger_20260417.csv` |
| 代表性公式表 | direct collapse / load local / wind local / solar local | 固化代表性公式快照 | `doc/paper_assets/paper_delivery_20260306/representative_formula_table_20260417.csv` |
| Direct collapse 图 | `direct symbolic` 9 组配置 presence matrix | `python3 scripts/render_paper_evidence_figures.py --out-dir doc/paper_assets/paper_delivery_20260306` | `doc/paper_assets/paper_delivery_20260306/direct_symbolic_collapse_20260417.png` |
| Wind/Solar horizon 图 | `wind_ablation_summary_20260306.csv` / `solar_ablation_summary_20260304.csv` | `python3 scripts/render_paper_evidence_figures.py --out-dir doc/paper_assets/paper_delivery_20260306` | `doc/paper_assets/paper_delivery_20260306/wind_solar_horizon_20260417.png` |
| S2 blocking 汇总图 | Case 3 / Case 4 论文冻结数值 | `python3 scripts/render_paper_evidence_figures.py --out-dir doc/paper_assets/paper_delivery_20260306` | `doc/paper_assets/paper_delivery_20260306/s2_blocking_summary_20260417.png` |
| 主结果 Pareto | 同上 | 同上 | `doc/paper_assets/paper_delivery_20260306/pareto_rmse_vs_complexity.png` |
| 主结果分层误差 | 同上 | 同上 | `doc/paper_assets/paper_delivery_20260306/seasonal_*.csv`、`day_night_*.csv` |
| Wind 机制表 | `2026-03-03_182435_d7339689` / `2026-03-03_183052_4888ee22` / `2026-03-03_183731_c56e2dad` / `2026-03-03_185031_6242fd21` | `python3 scripts/summarize_wind_ablation.py --run 2026-03-03_182435_d7339689 --run 2026-03-03_183052_4888ee22 --run 2026-03-03_183731_c56e2dad --run 2026-03-03_185031_6242fd21 > doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv` | `doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv` |
| Solar 机制表 | `2026-03-04_120745_b455d7bc` / `2026-03-04_120746_93a46524` / `2026-03-04_120749_01834d3e` / `2026-03-04_121143_04bfbfc0` / `2026-03-04_121143_49a2af36` / `2026-03-04_121145_74997b1b` / `2026-03-04_121143_c00221d5` / `2026-03-04_121142_9dd9aa4a` / `2026-03-04_121144_d6b684d1` | `python3 scripts/summarize_solar_ablation.py --run 2026-03-04_120746_93a46524 --run 2026-03-04_120749_01834d3e --run 2026-03-04_120745_b455d7bc --run 2026-03-04_121143_04bfbfc0 --run 2026-03-04_121145_74997b1b --run 2026-03-04_121143_49a2af36 --run 2026-03-04_121143_c00221d5 --run 2026-03-04_121142_9dd9aa4a --run 2026-03-04_121144_d6b684d1 > doc/solar_ablation_summary_20260304.csv` | `doc/solar_ablation_summary_20260304.csv` |
| Solar `h=288` 边界诊断 | `2026-03-04_101610_37271ac2` | `python3 scripts/diagnose_solar_bounds.py --run 2026-03-04_101610_37271ac2 > doc/paper_assets/paper_delivery_20260306/solar_h288_boundary_20260306.json` | `doc/paper_assets/paper_delivery_20260306/solar_h288_boundary_20260306.json` |
| 资产索引 | 本地 `runs/` + `doc/paper_assets/` | `python3 scripts/build_asset_index.py` | `doc/paper_assets/ASSET_INDEX.md` |

## 训练命令来源

1. `2026-03-01_151000_kan_nobase_nogrid_gpu` 的主训练与 `2026-03-01_160200_sym_strict_r2_0_995__kan151000` 的符号提取都可从 `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json` 追溯。
2. 结构化分解相关 run 与其他 thesis sweep run 的原始命令，也统一以 `doc/thesis_sweeps/*/manifest.json` 为准。
3. `doc/paper_assets/ASSET_INDEX.md` 现已补充 run 对应的 manifest 与 command 字段，可直接用于附录追溯。
4. S3闭环相关正式 run 统一以 `doc/thesis_sweeps/paperref_20260306_121725_v2/paper_assets/comparison_table.csv` 为准，论文交付侧只引用冻结快照 `s3_main_comparison_20260417.csv` 与 `s3_formula_closure_20260417.png`。
5. 第二阶段证据呈现资产统一固定为 `protocol_ledger_20260417.csv`、`representative_formula_table_20260417.csv`、`direct_symbolic_collapse_20260417.png`、`wind_solar_horizon_20260417.png`、`s2_blocking_summary_20260417.png`。
