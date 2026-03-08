# Thesis Asset Index

本文件用于汇总 `runs/` 与 `doc/paper_assets/` 下可直接用于论文撰写的产物。

## Global Tables/Plots

- `doc/paper_assets/ablation_table.csv`
- `doc/paper_assets/ablation_rmse_pruned.png`
- `doc/paper_assets/ablation_rmse_vs_sparsity.png`
- `doc/paper_assets/comparison_table.csv`
- `doc/paper_assets/transfer_gaps.csv`
- `doc/paper_assets/transfer_gap_ratio.png`
- `doc/paper_assets/pareto_rmse_vs_complexity.png`
- `doc/thesis_sweeps/2026-03-01_142726_9ab14f0b/manifest.json`
- `doc/thesis_sweeps/2026-03-02_s0s3_t4/manifest.json`
- `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/paper_assets/comparison_table.csv`
- `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/paper_assets/pareto_rmse_vs_complexity.png`
- `doc/thesis_sweeps/paperref_20260306_121725/manifest.json`
- `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- `doc/thesis_sweeps/paperref_20260306_121725_v2/paper_assets/comparison_table.csv`
- `doc/thesis_sweeps/paperref_20260306_121725_v2/paper_assets/pareto_rmse_vs_complexity.png`
- `doc/thesis_sweeps/s0a_physics_v1/manifest.json`
- `doc/thesis_sweeps/s0a_physics_v2/manifest.json`
- `doc/thesis_sweeps/s3_saveact_fix/manifest.json`
- `doc/thesis_sweeps/s4_pure_physics/manifest.json`
- `doc/thesis_sweeps/s4_pure_physics_v2/manifest.json`
- `doc/thesis_sweeps/s4_pure_v3/manifest.json`
- `doc/thesis_sweeps/s4_pure_v4/manifest.json`
- `doc/thesis_sweeps/s4_pure_v5/manifest.json`
- `doc/paper_assets/kan_pysr_cross_validation_2026-02-26_064508_3e631069.md`
- `doc/paper_assets/physics_mapping_2026-02-26_041718_5579aeeb.md`
- `doc/paper_assets/physics_mapping_2026-02-26_090620_1fc7d27a.md`
- `doc/paper_assets/physics_mapping_2026-02-26_091400_ba9fd48c.md`
- `doc/paper_assets/physics_mapping_2026-02-26_130037_55f49a5c.md`
- `doc/paper_assets/physics_mapping_2026-02-26_130651_18ca3f58.md`
- `doc/paper_assets/physics_mapping_2026-03-01_072253_5c9f7912.md`
- `doc/paper_assets/physics_mapping_2026-03-01_072418_8b55ce9a.md`
- `doc/paper_assets/physics_mapping_2026-03-01_072603_6825d4d0.md`
- `doc/paper_assets/physics_mapping_2026-03-01_072722_fc08d99e.md`
- `doc/paper_assets/sensitivity_summary_2026-02-26_041718_5579aeeb.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_090620_1fc7d27a.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_091400_ba9fd48c.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_130037_55f49a5c.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_130651_18ca3f58.csv`
- `doc/paper_assets/sensitivity_summary_2026-03-01_072253_5c9f7912.csv`
- `doc/paper_assets/sensitivity_summary_2026-03-01_072418_8b55ce9a.csv`
- `doc/paper_assets/sensitivity_summary_2026-03-01_072722_fc08d99e.csv`
- `doc/paper_assets/PAPER_REPRO_MAP_20260306.md`
- `doc/paper_assets/paper_delivery_20260306/comparison_table.csv`
- `doc/paper_assets/paper_delivery_20260306/day_night_2026-03-01_151000_kan_nobase_nogrid_gpu.csv`
- `doc/paper_assets/paper_delivery_20260306/day_night_2026-03-01_155600_baseline_mlp_match_kan151000.csv`
- `doc/paper_assets/paper_delivery_20260306/day_night_2026-03-01_160200_sym_strict_r2_0_995__kan151000.csv`
- `doc/paper_assets/paper_delivery_20260306/pareto_rmse_vs_complexity.png`
- `doc/paper_assets/paper_delivery_20260306/seasonal_2026-03-01_151000_kan_nobase_nogrid_gpu.csv`
- `doc/paper_assets/paper_delivery_20260306/seasonal_2026-03-01_155600_baseline_mlp_match_kan151000.csv`
- `doc/paper_assets/paper_delivery_20260306/seasonal_2026-03-01_160200_sym_strict_r2_0_995__kan151000.csv`
- `doc/paper_assets/paper_delivery_20260306/solar_h288_boundary_20260306.json`
- `doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv`
- `doc/paper_delivery_closure_20260306.md`
- `doc/solar_ablation_summary_20260304.csv`

## Runs

### 2026-02-26_032058_1957fda1

- phase: `01-data-pipeline`
- kind: `data_pipeline`

### 2026-02-26_035935_74ef1f78

- phase: `02-kan-training`
- kind: `kan`
- `runs/2026-02-26_035935_74ef1f78/artifacts/eval_pruned.json`
- `runs/2026-02-26_035935_74ef1f78/artifacts/predictions_test.parquet`
- `runs/2026-02-26_035935_74ef1f78/artifacts/feature_importance.csv`
- `runs/2026-02-26_035935_74ef1f78/artifacts/sparsity.json`
- figures:
  - `doc/paper_assets/figures/feature_importance_2026-02-26_035935_74ef1f78.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_035935_74ef1f78.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_035935_74ef1f78.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_035935_74ef1f78.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_035935_74ef1f78.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_035935_74ef1f78.png`
- kan_plot:
  - `doc/paper_assets/figures/kan_plot_2026-02-26_035935_74ef1f78/topology.png`
  - spline_plots: `100` files in `doc/paper_assets/figures/kan_plot_2026-02-26_035935_74ef1f78`

### 2026-02-26_041718_5579aeeb

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-02-26_041718_5579aeeb/artifacts/formula_eval_test.json`
- `runs/2026-02-26_041718_5579aeeb/artifacts/formula.tex`
- `runs/2026-02-26_041718_5579aeeb/artifacts/formula.sympy.txt`
- `runs/2026-02-26_041718_5579aeeb/artifacts/formula_metrics.json`
- `runs/2026-02-26_041718_5579aeeb/artifacts/predictions_test.parquet`
- `runs/2026-02-26_041718_5579aeeb/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-02-26_041718_5579aeeb.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_041718_5579aeeb.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_041718_5579aeeb.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_041718_5579aeeb.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_041718_5579aeeb.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_041718_5579aeeb.png`

### 2026-02-26_043102_777fac2d

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-02-26_043102_777fac2d/artifacts/eval_test.json`
- `runs/2026-02-26_043102_777fac2d/artifacts/predictions_test.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_2026-02-26_043102_777fac2d.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_043102_777fac2d.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_043102_777fac2d.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_043102_777fac2d.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_043102_777fac2d.png`

### 2026-02-26_043230_b2b5c68f

- phase: `04-baselines-torch`
- kind: `lstm`
- `runs/2026-02-26_043230_b2b5c68f/artifacts/eval_test.json`
- `runs/2026-02-26_043230_b2b5c68f/artifacts/predictions_test.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_2026-02-26_043230_b2b5c68f.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_043230_b2b5c68f.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_043230_b2b5c68f.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_043230_b2b5c68f.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_043230_b2b5c68f.png`

### 2026-02-26_045336_77244377

- phase: `04-baselines-pysr`
- kind: `pysr`
- `runs/2026-02-26_045336_77244377/artifacts/eval_test.json`
- `runs/2026-02-26_045336_77244377/artifacts/equations.csv`
- `runs/2026-02-26_045336_77244377/artifacts/best_equation.txt`
- `runs/2026-02-26_045336_77244377/artifacts/predictions_test.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_2026-02-26_045336_77244377.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_045336_77244377.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_045336_77244377.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_045336_77244377.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_045336_77244377.png`

### 2026-02-26_053425_2e4bc623

- phase: `02-kan-training`
- kind: `kan_full`
- `runs/2026-02-26_053425_2e4bc623/artifacts/eval_pruned.json`
- `runs/2026-02-26_053425_2e4bc623/artifacts/predictions_test.parquet`
- `runs/2026-02-26_053425_2e4bc623/artifacts/feature_importance.csv`
- `runs/2026-02-26_053425_2e4bc623/artifacts/sparsity.json`

### 2026-02-26_054408_f605ac11

- phase: `02-kan-training`
- kind: `kan_no_entropy`
- `runs/2026-02-26_054408_f605ac11/artifacts/eval_pruned.json`
- `runs/2026-02-26_054408_f605ac11/artifacts/predictions_test.parquet`
- `runs/2026-02-26_054408_f605ac11/artifacts/feature_importance.csv`
- `runs/2026-02-26_054408_f605ac11/artifacts/sparsity.json`

### 2026-02-26_055200_958b3949

- phase: `02-kan-training`
- kind: `kan_no_l1`
- `runs/2026-02-26_055200_958b3949/artifacts/eval_pruned.json`
- `runs/2026-02-26_055200_958b3949/artifacts/predictions_test.parquet`
- `runs/2026-02-26_055200_958b3949/artifacts/feature_importance.csv`
- `runs/2026-02-26_055200_958b3949/artifacts/sparsity.json`
- figures:
  - `doc/paper_assets/figures/feature_importance_2026-02-26_055200_958b3949.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_055200_958b3949.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_055200_958b3949.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_055200_958b3949.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_055200_958b3949.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_055200_958b3949.png`

### 2026-02-26_060024_d6250f56

- phase: `02-kan-training`
- kind: `kan_no_magnitude`
- `runs/2026-02-26_060024_d6250f56/artifacts/eval_pruned.json`
- `runs/2026-02-26_060024_d6250f56/artifacts/predictions_test.parquet`
- `runs/2026-02-26_060024_d6250f56/artifacts/feature_importance.csv`
- `runs/2026-02-26_060024_d6250f56/artifacts/sparsity.json`

### 2026-02-26_064508_3e631069

- phase: `04-baselines-pysr`
- kind: `pysr_seeded`
- `runs/2026-02-26_064508_3e631069/artifacts/eval_test.json`
- `runs/2026-02-26_064508_3e631069/artifacts/equations.csv`
- `runs/2026-02-26_064508_3e631069/artifacts/best_equation.txt`
- `runs/2026-02-26_064508_3e631069/artifacts/seed_features.json`
- `runs/2026-02-26_064508_3e631069/artifacts/predictions_test.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_2026-02-26_064508_3e631069.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_064508_3e631069.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_064508_3e631069.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_064508_3e631069.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_064508_3e631069.png`

### 2026-02-26_064925_a74e5d63

- phase: `02-kan-training`
- kind: `kan_solar`
- `runs/2026-02-26_064925_a74e5d63/artifacts/eval_pruned.json`
- `runs/2026-02-26_064925_a74e5d63/artifacts/predictions_test.parquet`
- `runs/2026-02-26_064925_a74e5d63/artifacts/feature_importance.csv`
- `runs/2026-02-26_064925_a74e5d63/artifacts/sparsity.json`
- figures:
  - `doc/paper_assets/figures/feature_importance_2026-02-26_064925_a74e5d63.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_064925_a74e5d63.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_064925_a74e5d63.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_064925_a74e5d63.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_064925_a74e5d63.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_064925_a74e5d63.png`

### 2026-02-26_070523_c05a4c19

- phase: `02-kan-training`
- kind: `kan_mult`
- `runs/2026-02-26_070523_c05a4c19/artifacts/eval_pruned.json`
- `runs/2026-02-26_070523_c05a4c19/artifacts/predictions_test.parquet`
- `runs/2026-02-26_070523_c05a4c19/artifacts/feature_importance.csv`
- `runs/2026-02-26_070523_c05a4c19/artifacts/sparsity.json`
- figures:
  - `doc/paper_assets/figures/feature_importance_2026-02-26_070523_c05a4c19.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_070523_c05a4c19.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_070523_c05a4c19.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_070523_c05a4c19.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_070523_c05a4c19.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_070523_c05a4c19.png`

### 2026-02-26_090620_1fc7d27a

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-02-26_090620_1fc7d27a/artifacts/formula_eval_test.json`
- `runs/2026-02-26_090620_1fc7d27a/artifacts/formula.tex`
- `runs/2026-02-26_090620_1fc7d27a/artifacts/formula.sympy.txt`
- `runs/2026-02-26_090620_1fc7d27a/artifacts/formula_metrics.json`
- `runs/2026-02-26_090620_1fc7d27a/artifacts/predictions_test.parquet`
- `runs/2026-02-26_090620_1fc7d27a/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-02-26_090620_1fc7d27a.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_090620_1fc7d27a.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_090620_1fc7d27a.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_090620_1fc7d27a.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_090620_1fc7d27a.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_090620_1fc7d27a.png`

### 2026-02-26_091400_ba9fd48c

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-02-26_091400_ba9fd48c/artifacts/formula_eval_test.json`
- `runs/2026-02-26_091400_ba9fd48c/artifacts/formula.tex`
- `runs/2026-02-26_091400_ba9fd48c/artifacts/formula.sympy.txt`
- `runs/2026-02-26_091400_ba9fd48c/artifacts/formula_metrics.json`
- `runs/2026-02-26_091400_ba9fd48c/artifacts/predictions_test.parquet`
- `runs/2026-02-26_091400_ba9fd48c/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-02-26_091400_ba9fd48c.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_091400_ba9fd48c.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_091400_ba9fd48c.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_091400_ba9fd48c.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_091400_ba9fd48c.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_091400_ba9fd48c.png`

### 2026-02-26_122629_b5a495b4

- phase: `02-kan-training`
- kind: `kan`
- `runs/2026-02-26_122629_b5a495b4/artifacts/eval_pruned.json`
- `runs/2026-02-26_122629_b5a495b4/artifacts/predictions_test.parquet`
- `runs/2026-02-26_122629_b5a495b4/artifacts/feature_importance.csv`
- `runs/2026-02-26_122629_b5a495b4/artifacts/sparsity.json`
- figures:
  - `doc/paper_assets/figures/feature_importance_2026-02-26_122629_b5a495b4.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_122629_b5a495b4.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_122629_b5a495b4.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_122629_b5a495b4.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_122629_b5a495b4.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_122629_b5a495b4.png`

### 2026-02-26_130037_55f49a5c

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-02-26_130037_55f49a5c/artifacts/formula_eval_test.json`
- `runs/2026-02-26_130037_55f49a5c/artifacts/formula.tex`
- `runs/2026-02-26_130037_55f49a5c/artifacts/formula.sympy.txt`
- `runs/2026-02-26_130037_55f49a5c/artifacts/formula_metrics.json`
- `runs/2026-02-26_130037_55f49a5c/artifacts/predictions_test.parquet`
- `runs/2026-02-26_130037_55f49a5c/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-02-26_130037_55f49a5c.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_130037_55f49a5c.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_130037_55f49a5c.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_130037_55f49a5c.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_130037_55f49a5c.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_130037_55f49a5c.png`

### 2026-02-26_130651_18ca3f58

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-02-26_130651_18ca3f58/artifacts/formula_eval_test.json`
- `runs/2026-02-26_130651_18ca3f58/artifacts/formula.tex`
- `runs/2026-02-26_130651_18ca3f58/artifacts/formula.sympy.txt`
- `runs/2026-02-26_130651_18ca3f58/artifacts/formula_metrics.json`
- `runs/2026-02-26_130651_18ca3f58/artifacts/predictions_test.parquet`
- `runs/2026-02-26_130651_18ca3f58/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_130651_18ca3f58.png`

### 2026-02-27_111856_3d590023

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026-02-27_130143_635744ad

- phase: `02-kan-training`
- kind: `kan`
- `runs/2026-02-27_130143_635744ad/artifacts/eval_test_reconstructed.json`
- `runs/2026-02-27_130143_635744ad/artifacts/eval_pruned.json`
- `runs/2026-02-27_130143_635744ad/artifacts/predictions_test.parquet`
- `runs/2026-02-27_130143_635744ad/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-02-27_130143_635744ad/artifacts/feature_importance.csv`
- `runs/2026-02-27_130143_635744ad/artifacts/sparsity.json`
- figures:
  - `doc/paper_assets/figures/feature_importance_2026-02-27_130143_635744ad.png`
  - `doc/paper_assets/figures/residual_box_2026-02-27_130143_635744ad.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-27_130143_635744ad.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-27_130143_635744ad.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-27_130143_635744ad.png`
  - `doc/paper_assets/figures/timeseries_2026-02-27_130143_635744ad.png`

### 2026-02-27_163309_0420c80c

- phase: `02-kan-training`
- kind: `kan`
- `runs/2026-02-27_163309_0420c80c/artifacts/eval_test_reconstructed.json`
- `runs/2026-02-27_163309_0420c80c/artifacts/eval_pruned.json`
- `runs/2026-02-27_163309_0420c80c/artifacts/predictions_test.parquet`
- `runs/2026-02-27_163309_0420c80c/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-02-27_163309_0420c80c/artifacts/feature_importance.csv`
- `runs/2026-02-27_163309_0420c80c/artifacts/sparsity.json`
- figures:
  - `doc/paper_assets/figures/feature_importance_2026-02-27_163309_0420c80c.png`
  - `doc/paper_assets/figures/residual_box_2026-02-27_163309_0420c80c.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-27_163309_0420c80c.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-27_163309_0420c80c.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-27_163309_0420c80c.png`
  - `doc/paper_assets/figures/timeseries_2026-02-27_163309_0420c80c.png`

### 2026-03-01_061313_c5642fb5

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_061313_c5642fb5/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_061313_c5642fb5/artifacts/formula_eval_test.json`
- `runs/2026-03-01_061313_c5642fb5/artifacts/formula.tex`
- `runs/2026-03-01_061313_c5642fb5/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_061313_c5642fb5/artifacts/formula.sympy.txt`
- `runs/2026-03-01_061313_c5642fb5/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_061313_c5642fb5/artifacts/formula_metrics.json`
- `runs/2026-03-01_061313_c5642fb5/artifacts/predictions_test.parquet`
- `runs/2026-03-01_061313_c5642fb5/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_061313_c5642fb5/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_061313_c5642fb5.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_061313_c5642fb5.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_061313_c5642fb5.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_061313_c5642fb5.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_061313_c5642fb5.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_061313_c5642fb5.png`

### 2026-03-01_061458_59db1fe6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_061458_59db1fe6/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_061458_59db1fe6/artifacts/formula_eval_test.json`
- `runs/2026-03-01_061458_59db1fe6/artifacts/formula.tex`
- `runs/2026-03-01_061458_59db1fe6/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_061458_59db1fe6/artifacts/formula.sympy.txt`
- `runs/2026-03-01_061458_59db1fe6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_061458_59db1fe6/artifacts/formula_metrics.json`
- `runs/2026-03-01_061458_59db1fe6/artifacts/predictions_test.parquet`
- `runs/2026-03-01_061458_59db1fe6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_061458_59db1fe6/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_061458_59db1fe6.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_061458_59db1fe6.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_061458_59db1fe6.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_061458_59db1fe6.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_061458_59db1fe6.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_061458_59db1fe6.png`

### 2026-03-01_061747_92da9d64

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_061747_92da9d64/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_061747_92da9d64/artifacts/formula_eval_test.json`
- `runs/2026-03-01_061747_92da9d64/artifacts/formula.tex`
- `runs/2026-03-01_061747_92da9d64/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_061747_92da9d64/artifacts/formula.sympy.txt`
- `runs/2026-03-01_061747_92da9d64/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_061747_92da9d64/artifacts/formula_metrics.json`
- `runs/2026-03-01_061747_92da9d64/artifacts/predictions_test.parquet`
- `runs/2026-03-01_061747_92da9d64/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_061747_92da9d64/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_061747_92da9d64.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_061747_92da9d64.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_061747_92da9d64.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_061747_92da9d64.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_061747_92da9d64.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_061747_92da9d64.png`

### 2026-03-01_061911_4821be46

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_061911_4821be46/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_061911_4821be46/artifacts/formula_eval_test.json`
- `runs/2026-03-01_061911_4821be46/artifacts/formula.tex`
- `runs/2026-03-01_061911_4821be46/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_061911_4821be46/artifacts/formula.sympy.txt`
- `runs/2026-03-01_061911_4821be46/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_061911_4821be46/artifacts/formula_metrics.json`
- `runs/2026-03-01_061911_4821be46/artifacts/predictions_test.parquet`
- `runs/2026-03-01_061911_4821be46/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_061911_4821be46/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_061911_4821be46.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_061911_4821be46.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_061911_4821be46.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_061911_4821be46.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_061911_4821be46.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_061911_4821be46.png`

### 2026-03-01_062033_c6c12f8d

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-03-01_062033_c6c12f8d/artifacts/eval_test.json`
- `runs/2026-03-01_062033_c6c12f8d/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_062033_c6c12f8d/artifacts/predictions_test.parquet`
- `runs/2026-03-01_062033_c6c12f8d/artifacts/predictions_test_reconstructed.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_2026-03-01_062033_c6c12f8d.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_062033_c6c12f8d.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_062033_c6c12f8d.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_062033_c6c12f8d.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_062033_c6c12f8d.png`

### 2026-03-01_072253_5c9f7912

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_072253_5c9f7912/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_072253_5c9f7912/artifacts/formula_eval_test.json`
- `runs/2026-03-01_072253_5c9f7912/artifacts/formula.tex`
- `runs/2026-03-01_072253_5c9f7912/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_072253_5c9f7912/artifacts/formula.sympy.txt`
- `runs/2026-03-01_072253_5c9f7912/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_072253_5c9f7912/artifacts/formula_metrics.json`
- `runs/2026-03-01_072253_5c9f7912/artifacts/physics_mapping.json`
- `runs/2026-03-01_072253_5c9f7912/artifacts/predictions_test.parquet`
- `runs/2026-03-01_072253_5c9f7912/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_072253_5c9f7912/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_072253_5c9f7912.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_072253_5c9f7912.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_072253_5c9f7912.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_072253_5c9f7912.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_072253_5c9f7912.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_072253_5c9f7912.png`

### 2026-03-01_072418_8b55ce9a

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/formula_eval_test.json`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/formula.tex`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/formula.sympy.txt`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/formula_metrics.json`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/physics_mapping.json`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/predictions_test.parquet`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_072418_8b55ce9a/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_072418_8b55ce9a.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_072418_8b55ce9a.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_072418_8b55ce9a.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_072418_8b55ce9a.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_072418_8b55ce9a.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_072418_8b55ce9a.png`

### 2026-03-01_072603_6825d4d0

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_072603_6825d4d0/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_072603_6825d4d0/artifacts/formula_eval_test.json`
- `runs/2026-03-01_072603_6825d4d0/artifacts/formula.tex`
- `runs/2026-03-01_072603_6825d4d0/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_072603_6825d4d0/artifacts/formula.sympy.txt`
- `runs/2026-03-01_072603_6825d4d0/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_072603_6825d4d0/artifacts/formula_metrics.json`
- `runs/2026-03-01_072603_6825d4d0/artifacts/physics_mapping.json`
- `runs/2026-03-01_072603_6825d4d0/artifacts/predictions_test.parquet`
- `runs/2026-03-01_072603_6825d4d0/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_072603_6825d4d0/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_072603_6825d4d0.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_072603_6825d4d0.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_072603_6825d4d0.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_072603_6825d4d0.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_072603_6825d4d0.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_072603_6825d4d0.png`

### 2026-03-01_072722_fc08d99e

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_072722_fc08d99e/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_072722_fc08d99e/artifacts/formula_eval_test.json`
- `runs/2026-03-01_072722_fc08d99e/artifacts/formula.tex`
- `runs/2026-03-01_072722_fc08d99e/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_072722_fc08d99e/artifacts/formula.sympy.txt`
- `runs/2026-03-01_072722_fc08d99e/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_072722_fc08d99e/artifacts/formula_metrics.json`
- `runs/2026-03-01_072722_fc08d99e/artifacts/physics_mapping.json`
- `runs/2026-03-01_072722_fc08d99e/artifacts/predictions_test.parquet`
- `runs/2026-03-01_072722_fc08d99e/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_072722_fc08d99e/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-03-01_072722_fc08d99e.png`
  - `doc/paper_assets/figures/residual_box_2026-03-01_072722_fc08d99e.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_072722_fc08d99e.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_072722_fc08d99e.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_072722_fc08d99e.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_072722_fc08d99e.png`

### 2026-03-01_072844_f65399e8

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-03-01_072844_f65399e8/artifacts/eval_test.json`
- `runs/2026-03-01_072844_f65399e8/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_072844_f65399e8/artifacts/predictions_test.parquet`
- `runs/2026-03-01_072844_f65399e8/artifacts/predictions_test_reconstructed.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_2026-03-01_072844_f65399e8.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_072844_f65399e8.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_072844_f65399e8.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_072844_f65399e8.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_072844_f65399e8.png`

### 2026-03-01_075447_1cff3b05

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-03-01_075447_1cff3b05/artifacts/eval_test.json`
- `runs/2026-03-01_075447_1cff3b05/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_075447_1cff3b05/artifacts/predictions_test.parquet`
- `runs/2026-03-01_075447_1cff3b05/artifacts/predictions_test_reconstructed.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_2026-03-01_075447_1cff3b05.png`
  - `doc/paper_assets/figures/residual_hist_2026-03-01_075447_1cff3b05.png`
  - `doc/paper_assets/figures/residual_qq_2026-03-01_075447_1cff3b05.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-03-01_075447_1cff3b05.png`
  - `doc/paper_assets/figures/timeseries_2026-03-01_075447_1cff3b05.png`

### 2026-03-01_105353_fullflow_t4_1e551b__baseline_mlp_match_main

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mlp_match_main/artifacts/eval_test.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mlp_match_main/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mlp_match_main/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mlp_match_main/artifacts/predictions_test_reconstructed.parquet`

### 2026-03-01_105353_fullflow_t4_1e551b__baseline_mscnn_attn_match_main

- phase: `04-baselines-torch`
- kind: `mscnn_attn`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mscnn_attn_match_main/artifacts/eval_test.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mscnn_attn_match_main/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mscnn_attn_match_main/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__baseline_mscnn_attn_match_main/artifacts/predictions_test_reconstructed.parquet`

### 2026-03-01_105353_fullflow_t4_1e551b__derived_h1_6_12_24

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6

- phase: `02-kan-training`
- kind: `fullflow_main`

### 2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase

- phase: `02-kan-training`
- kind: `fullflow_main_nobase`

### 2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase_nogrid

- phase: `02-kan-training`
- kind: `fullflow_main_nobase_nogrid`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase_nogrid/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase_nogrid/artifacts/eval_pruned.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase_nogrid/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase_nogrid/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase_nogrid/artifacts/feature_importance.csv`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__kan_delta_net_load_h6_nobase_nogrid/artifacts/sparsity.json`

### 2026-03-01_105353_fullflow_t4_1e551b__s3_combo_net_load_h6

- phase: `05-structured-combination`
- kind: `net_load_from_components`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_combo_net_load_h6/artifacts/eval_test.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_combo_net_load_h6/artifacts/predictions_test.parquet`

### 2026-03-01_105353_fullflow_t4_1e551b__s3_comp_load_delta_load_h6

- phase: `02-kan-training`
- kind: `s3_comp_load`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_load_delta_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_load_delta_load_h6/artifacts/eval_pruned.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_load_delta_load_h6/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_load_delta_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_load_delta_load_h6/artifacts/feature_importance.csv`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_load_delta_load_h6/artifacts/sparsity.json`

### 2026-03-01_105353_fullflow_t4_1e551b__s3_comp_solar_delta_solar_h6

- phase: `02-kan-training`
- kind: `s3_comp_solar_delta_solar_h6`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_solar_delta_solar_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_solar_delta_solar_h6/artifacts/eval_pruned.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_solar_delta_solar_h6/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_solar_delta_solar_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_solar_delta_solar_h6/artifacts/feature_importance.csv`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_solar_delta_solar_h6/artifacts/sparsity.json`

### 2026-03-01_105353_fullflow_t4_1e551b__s3_comp_wind_delta_wind_h6

- phase: `02-kan-training`
- kind: `s3_comp_wind`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_wind_delta_wind_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_wind_delta_wind_h6/artifacts/eval_pruned.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_wind_delta_wind_h6/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_wind_delta_wind_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_wind_delta_wind_h6/artifacts/feature_importance.csv`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__s3_comp_wind_delta_wind_h6/artifacts/sparsity.json`

### 2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/formula_eval_test.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/formula.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/formula.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/formula_metrics.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_995/artifacts/separability.json`

### 2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/formula_eval_test.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/formula.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/formula.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/formula_metrics.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_medium_r2_0_999/artifacts/separability.json`

### 2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/formula_eval_test.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/formula.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/formula.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/formula_metrics.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_995/artifacts/separability.json`

### 2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/formula_eval_test.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/formula.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/formula.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/formula_metrics.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/physics_mapping.json`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/predictions_test.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_105353_fullflow_t4_1e551b__sym_strict_r2_0_999/artifacts/separability.json`

### 2026-03-01_135354_030f529b

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026-03-01_135923_c1efe231

- phase: `02-kan-training`
- kind: `kan`

### 2026-03-01_140101_bee69845

- phase: `02-kan-training`
- kind: `kan`
- `runs/2026-03-01_140101_bee69845/artifacts/eval_pruned.json`
- `runs/2026-03-01_140101_bee69845/artifacts/predictions_test.parquet`
- `runs/2026-03-01_140101_bee69845/artifacts/feature_importance.csv`
- `runs/2026-03-01_140101_bee69845/artifacts/sparsity.json`

### 2026-03-01_140121_8177bb88

- phase: `03-symbolic`
- kind: `unknown`
- `runs/2026-03-01_140121_8177bb88/artifacts/formula_eval_test.json`
- `runs/2026-03-01_140121_8177bb88/artifacts/formula.tex`
- `runs/2026-03-01_140121_8177bb88/artifacts/formula.sympy.txt`
- `runs/2026-03-01_140121_8177bb88/artifacts/formula_metrics.json`
- `runs/2026-03-01_140121_8177bb88/artifacts/predictions_test.parquet`

### 2026-03-01_143200_deep8_gpu_nogrid

- phase: `02-kan-training`
- kind: `debug_deep8_gpu_nogrid`
- `runs/2026-03-01_143200_deep8_gpu_nogrid/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_143200_deep8_gpu_nogrid/artifacts/eval_pruned.json`
- `runs/2026-03-01_143200_deep8_gpu_nogrid/artifacts/predictions_test.parquet`
- `runs/2026-03-01_143200_deep8_gpu_nogrid/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_143200_deep8_gpu_nogrid/artifacts/feature_importance.csv`
- `runs/2026-03-01_143200_deep8_gpu_nogrid/artifacts/sparsity.json`

### 2026-03-01_143900_baseline_mlp_gpu

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-03-01_143900_baseline_mlp_gpu/artifacts/eval_test.json`
- `runs/2026-03-01_143900_baseline_mlp_gpu/artifacts/predictions_test.parquet`

### 2026-03-01_144500_sym_strict_r2_0.995

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/formula_eval_test.json`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/formula.tex`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/formula.sympy.txt`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/formula_metrics.json`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/predictions_test.parquet`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_144500_sym_strict_r2_0.995/artifacts/separability.json`

### 2026-03-01_150000_baseline_mlp_gpu

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-03-01_150000_baseline_mlp_gpu/artifacts/eval_test.json`
- `runs/2026-03-01_150000_baseline_mlp_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_150000_baseline_mlp_gpu/artifacts/predictions_test.parquet`
- `runs/2026-03-01_150000_baseline_mlp_gpu/artifacts/predictions_test_reconstructed.parquet`

### 2026-03-01_151000_kan_nobase_nogrid_gpu

- phase: `02-kan-training`
- kind: `fullflow_nobase_nogrid_gpu`
- `runs/2026-03-01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_151000_kan_nobase_nogrid_gpu/artifacts/eval_pruned.json`
- `runs/2026-03-01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026-03-01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_151000_kan_nobase_nogrid_gpu/artifacts/feature_importance.csv`
- `runs/2026-03-01_151000_kan_nobase_nogrid_gpu/artifacts/sparsity.json`

### 2026-03-01_155600_baseline_mlp_match_kan151000

- phase: `04-baselines-torch`
- kind: `mlp`
- `runs/2026-03-01_155600_baseline_mlp_match_kan151000/artifacts/eval_test.json`
- `runs/2026-03-01_155600_baseline_mlp_match_kan151000/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_155600_baseline_mlp_match_kan151000/artifacts/predictions_test.parquet`
- `runs/2026-03-01_155600_baseline_mlp_match_kan151000/artifacts/predictions_test_reconstructed.parquet`

### 2026-03-01_160200_sym_strict_r2_0_995__kan151000

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/formula_eval_test.json`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/formula.tex`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/formula_reconstructed.tex`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/formula.sympy.txt`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/formula_metrics.json`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/predictions_test.parquet`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-01_160200_sym_strict_r2_0_995__kan151000/artifacts/separability.json`

### 2026-03-02_031524_080d3036

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026-03-02_031525_fa70a81c

- phase: `02-kan-training`
- kind: `debug_physics_wind_absolute`
- `runs/2026-03-02_031525_fa70a81c/artifacts/eval_pruned.json`
- `runs/2026-03-02_031525_fa70a81c/artifacts/predictions_test.parquet`
- `runs/2026-03-02_031525_fa70a81c/artifacts/feature_importance.csv`
- `runs/2026-03-02_031525_fa70a81c/artifacts/sparsity.json`

### 2026-03-02_031625_16a61b54

- phase: `03-symbolic`
- kind: `unknown`
- `runs/2026-03-02_031625_16a61b54/artifacts/formula_eval_test.json`
- `runs/2026-03-02_031625_16a61b54/artifacts/formula.tex`
- `runs/2026-03-02_031625_16a61b54/artifacts/formula.sympy.txt`
- `runs/2026-03-02_031625_16a61b54/artifacts/formula_metrics.json`
- `runs/2026-03-02_031625_16a61b54/artifacts/predictions_test.parquet`

### 2026-03-02_031643_cb0c07da

- phase: `02-kan-training`
- kind: `debug_physics_wind_delta`
- `runs/2026-03-02_031643_cb0c07da/artifacts/eval_pruned.json`
- `runs/2026-03-02_031643_cb0c07da/artifacts/predictions_test.parquet`
- `runs/2026-03-02_031643_cb0c07da/artifacts/feature_importance.csv`
- `runs/2026-03-02_031643_cb0c07da/artifacts/sparsity.json`

### 2026-03-02_042915_70de6971

- phase: `02-kan-training`
- kind: `debug_physics_wind_absolute`

### 2026-03-02_042928_e812c028

- phase: `03-symbolic`
- kind: `unknown`
- `runs/2026-03-02_042928_e812c028/artifacts/formula_eval_test.json`
- `runs/2026-03-02_042928_e812c028/artifacts/formula.tex`
- `runs/2026-03-02_042928_e812c028/artifacts/formula.sympy.txt`
- `runs/2026-03-02_042928_e812c028/artifacts/formula_metrics.json`
- `runs/2026-03-02_042928_e812c028/artifacts/predictions_test.parquet`

### 2026-03-03_182340_cb0b379c

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026-03-03_182435_d7339689

- phase: `02-kan-training`
- kind: `exp_longh_wind_delta_h6`
- `runs/2026-03-03_182435_d7339689/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-03_182435_d7339689/artifacts/eval_pruned.json`
- `runs/2026-03-03_182435_d7339689/artifacts/predictions_test.parquet`
- `runs/2026-03-03_182435_d7339689/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-03_182435_d7339689/artifacts/feature_importance.csv`
- `runs/2026-03-03_182435_d7339689/artifacts/sparsity.json`

### 2026-03-03_183052_4888ee22

- phase: `02-kan-training`
- kind: `exp_longh_wind_delta_h72`
- `runs/2026-03-03_183052_4888ee22/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-03_183052_4888ee22/artifacts/eval_pruned.json`
- `runs/2026-03-03_183052_4888ee22/artifacts/predictions_test.parquet`
- `runs/2026-03-03_183052_4888ee22/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-03_183052_4888ee22/artifacts/feature_importance.csv`
- `runs/2026-03-03_183052_4888ee22/artifacts/sparsity.json`

### 2026-03-03_183731_c56e2dad

- phase: `02-kan-training`
- kind: `exp_longh_wind_delta_h144`
- `runs/2026-03-03_183731_c56e2dad/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-03_183731_c56e2dad/artifacts/eval_pruned.json`
- `runs/2026-03-03_183731_c56e2dad/artifacts/predictions_test.parquet`
- `runs/2026-03-03_183731_c56e2dad/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-03_183731_c56e2dad/artifacts/feature_importance.csv`
- `runs/2026-03-03_183731_c56e2dad/artifacts/sparsity.json`

### 2026-03-03_184352_2f87ed99

- phase: `02-kan-training`
- kind: `exp_longh_wind_delta_h288`
- `runs/2026-03-03_184352_2f87ed99/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-03_184352_2f87ed99/artifacts/eval_pruned.json`
- `runs/2026-03-03_184352_2f87ed99/artifacts/predictions_test.parquet`
- `runs/2026-03-03_184352_2f87ed99/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-03_184352_2f87ed99/artifacts/feature_importance.csv`
- `runs/2026-03-03_184352_2f87ed99/artifacts/sparsity.json`

### 2026-03-03_185031_6242fd21

- phase: `02-kan-training`
- kind: `exp_longh_wind_delta_h576`
- `runs/2026-03-03_185031_6242fd21/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-03_185031_6242fd21/artifacts/eval_pruned.json`
- `runs/2026-03-03_185031_6242fd21/artifacts/predictions_test.parquet`
- `runs/2026-03-03_185031_6242fd21/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-03_185031_6242fd21/artifacts/feature_importance.csv`
- `runs/2026-03-03_185031_6242fd21/artifacts/sparsity.json`

### 2026-03-04_101610_37271ac2

- phase: `02-kan-training`
- kind: `exp_longh_solar_delta_h288`
- `runs/2026-03-04_101610_37271ac2/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_101610_37271ac2/artifacts/eval_pruned.json`
- `runs/2026-03-04_101610_37271ac2/artifacts/predictions_test.parquet`
- `runs/2026-03-04_101610_37271ac2/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_101610_37271ac2/artifacts/feature_importance.csv`
- `runs/2026-03-04_101610_37271ac2/artifacts/sparsity.json`

### 2026-03-04_101610_8ff99665

- phase: `02-kan-training`
- kind: `exp_longh_solar_delta_h576`
- `runs/2026-03-04_101610_8ff99665/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_101610_8ff99665/artifacts/eval_pruned.json`
- `runs/2026-03-04_101610_8ff99665/artifacts/predictions_test.parquet`
- `runs/2026-03-04_101610_8ff99665/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_101610_8ff99665/artifacts/feature_importance.csv`
- `runs/2026-03-04_101610_8ff99665/artifacts/sparsity.json`

### 2026-03-04_101610_9a2d9cf4

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026-03-04_101610_a83af0bc

- phase: `02-kan-training`
- kind: `exp_longh_solar_delta_h6`
- `runs/2026-03-04_101610_a83af0bc/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_101610_a83af0bc/artifacts/eval_pruned.json`
- `runs/2026-03-04_101610_a83af0bc/artifacts/predictions_test.parquet`
- `runs/2026-03-04_101610_a83af0bc/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_101610_a83af0bc/artifacts/feature_importance.csv`
- `runs/2026-03-04_101610_a83af0bc/artifacts/sparsity.json`

### 2026-03-04_101610_ca0cff43

- phase: `02-kan-training`
- kind: `exp_longh_solar_delta_h144`
- `runs/2026-03-04_101610_ca0cff43/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_101610_ca0cff43/artifacts/eval_pruned.json`
- `runs/2026-03-04_101610_ca0cff43/artifacts/predictions_test.parquet`
- `runs/2026-03-04_101610_ca0cff43/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_101610_ca0cff43/artifacts/feature_importance.csv`
- `runs/2026-03-04_101610_ca0cff43/artifacts/sparsity.json`

### 2026-03-04_101610_d45e8e2f

- phase: `02-kan-training`
- kind: `exp_longh_solar_delta_h72`
- `runs/2026-03-04_101610_d45e8e2f/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_101610_d45e8e2f/artifacts/eval_pruned.json`
- `runs/2026-03-04_101610_d45e8e2f/artifacts/predictions_test.parquet`
- `runs/2026-03-04_101610_d45e8e2f/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_101610_d45e8e2f/artifacts/feature_importance.csv`
- `runs/2026-03-04_101610_d45e8e2f/artifacts/sparsity.json`

### 2026-03-04_120745_b455d7bc

- phase: `02-kan-training`
- kind: `ablate_solar_h72_both`
- `runs/2026-03-04_120745_b455d7bc/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_120745_b455d7bc/artifacts/eval_pruned.json`
- `runs/2026-03-04_120745_b455d7bc/artifacts/predictions_test.parquet`
- `runs/2026-03-04_120745_b455d7bc/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_120745_b455d7bc/artifacts/feature_importance.csv`
- `runs/2026-03-04_120745_b455d7bc/artifacts/sparsity.json`

### 2026-03-04_120746_93a46524

- phase: `02-kan-training`
- kind: `ablate_solar_h72_lags_only`
- `runs/2026-03-04_120746_93a46524/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_120746_93a46524/artifacts/eval_pruned.json`
- `runs/2026-03-04_120746_93a46524/artifacts/predictions_test.parquet`
- `runs/2026-03-04_120746_93a46524/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_120746_93a46524/artifacts/feature_importance.csv`
- `runs/2026-03-04_120746_93a46524/artifacts/sparsity.json`

### 2026-03-04_120749_01834d3e

- phase: `02-kan-training`
- kind: `ablate_solar_h72_meteo_only`
- `runs/2026-03-04_120749_01834d3e/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_120749_01834d3e/artifacts/eval_pruned.json`
- `runs/2026-03-04_120749_01834d3e/artifacts/predictions_test.parquet`
- `runs/2026-03-04_120749_01834d3e/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_120749_01834d3e/artifacts/feature_importance.csv`
- `runs/2026-03-04_120749_01834d3e/artifacts/sparsity.json`

### 2026-03-04_121142_9dd9aa4a

- phase: `02-kan-training`
- kind: `ablate_solar_h576_meteo_only`
- `runs/2026-03-04_121142_9dd9aa4a/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_121142_9dd9aa4a/artifacts/eval_pruned.json`
- `runs/2026-03-04_121142_9dd9aa4a/artifacts/predictions_test.parquet`
- `runs/2026-03-04_121142_9dd9aa4a/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_121142_9dd9aa4a/artifacts/feature_importance.csv`
- `runs/2026-03-04_121142_9dd9aa4a/artifacts/sparsity.json`

### 2026-03-04_121143_04bfbfc0

- phase: `02-kan-training`
- kind: `ablate_solar_h144_lags_only`
- `runs/2026-03-04_121143_04bfbfc0/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_121143_04bfbfc0/artifacts/eval_pruned.json`
- `runs/2026-03-04_121143_04bfbfc0/artifacts/predictions_test.parquet`
- `runs/2026-03-04_121143_04bfbfc0/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_121143_04bfbfc0/artifacts/feature_importance.csv`
- `runs/2026-03-04_121143_04bfbfc0/artifacts/sparsity.json`

### 2026-03-04_121143_49a2af36

- phase: `02-kan-training`
- kind: `ablate_solar_h144_both`
- `runs/2026-03-04_121143_49a2af36/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_121143_49a2af36/artifacts/eval_pruned.json`
- `runs/2026-03-04_121143_49a2af36/artifacts/predictions_test.parquet`
- `runs/2026-03-04_121143_49a2af36/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_121143_49a2af36/artifacts/feature_importance.csv`
- `runs/2026-03-04_121143_49a2af36/artifacts/sparsity.json`

### 2026-03-04_121143_c00221d5

- phase: `02-kan-training`
- kind: `ablate_solar_h576_lags_only`
- `runs/2026-03-04_121143_c00221d5/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_121143_c00221d5/artifacts/eval_pruned.json`
- `runs/2026-03-04_121143_c00221d5/artifacts/predictions_test.parquet`
- `runs/2026-03-04_121143_c00221d5/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_121143_c00221d5/artifacts/feature_importance.csv`
- `runs/2026-03-04_121143_c00221d5/artifacts/sparsity.json`

### 2026-03-04_121144_d6b684d1

- phase: `02-kan-training`
- kind: `ablate_solar_h576_both`
- `runs/2026-03-04_121144_d6b684d1/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_121144_d6b684d1/artifacts/eval_pruned.json`
- `runs/2026-03-04_121144_d6b684d1/artifacts/predictions_test.parquet`
- `runs/2026-03-04_121144_d6b684d1/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_121144_d6b684d1/artifacts/feature_importance.csv`
- `runs/2026-03-04_121144_d6b684d1/artifacts/sparsity.json`

### 2026-03-04_121145_74997b1b

- phase: `02-kan-training`
- kind: `ablate_solar_h144_meteo_only`
- `runs/2026-03-04_121145_74997b1b/artifacts/eval_test_reconstructed.json`
- `runs/2026-03-04_121145_74997b1b/artifacts/eval_pruned.json`
- `runs/2026-03-04_121145_74997b1b/artifacts/predictions_test.parquet`
- `runs/2026-03-04_121145_74997b1b/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026-03-04_121145_74997b1b/artifacts/feature_importance.csv`
- `runs/2026-03-04_121145_74997b1b/artifacts/sparsity.json`

### 2026-03-06_041802_0ad5813e

- phase: `01-data-pipeline`
- kind: `data_pipeline`

### 2026-03-06_042129_03d4b407

- phase: `01-data-pipeline`
- kind: `data_pipeline`

### 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24

- phase: `01.5-derived-dataset`
- kind: `unknown`
- manifest: `doc/thesis_sweeps/2026-03-01_142726_9ab14f0b/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/derive_dataset.py --source-data-run-id 2026-02-26_032058_1957fda1 --run-id 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24 --horizon-steps 1,6,12,24 --net-load-lag-steps 1,12,48`

### 2026_03_02_physics_s3_t4__derived_h1_6_12_24

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026_03_02_physics_s3_t4__s0p_solar_delta_h6

- phase: `02-kan-training`
- kind: `s0p_solar_delta_h6`
- `runs/2026_03_02_physics_s3_t4__s0p_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_physics_s3_t4__s0p_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_physics_s3_t4__s0p_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_physics_s3_t4__s0p_solar_delta_h6/artifacts/sparsity.json`

### 2026_03_02_physics_s3_t4__s0p_wind_delta_h6

- phase: `02-kan-training`
- kind: `s0p_wind_delta_h6`
- `runs/2026_03_02_physics_s3_t4__s0p_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_physics_s3_t4__s0p_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_physics_s3_t4__s0p_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_physics_s3_t4__s0p_wind_delta_h6/artifacts/sparsity.json`

### 2026_03_02_physics_s3_t4__s3_comp_load_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_load_delta_h6`
- `runs/2026_03_02_physics_s3_t4__s3_comp_load_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_physics_s3_t4__s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_physics_s3_t4__s3_comp_load_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_physics_s3_t4__s3_comp_load_delta_h6/artifacts/sparsity.json`

### 2026_03_02_physics_s3_t4__s3_comp_solar_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_solar_delta_h6`
- `runs/2026_03_02_physics_s3_t4__s3_comp_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_physics_s3_t4__s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_physics_s3_t4__s3_comp_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_physics_s3_t4__s3_comp_solar_delta_h6/artifacts/sparsity.json`

### 2026_03_02_physics_s3_t4__s3_comp_wind_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_wind_delta_h6`
- `runs/2026_03_02_physics_s3_t4__s3_comp_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_physics_s3_t4__s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_physics_s3_t4__s3_comp_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_physics_s3_t4__s3_comp_wind_delta_h6/artifacts/sparsity.json`

### 2026_03_02_physics_s3_t4__sym_strict_s0p_wind

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- `runs/2026_03_02_physics_s3_t4__sym_strict_s0p_wind/artifacts/formula_eval_test.json`
- `runs/2026_03_02_physics_s3_t4__sym_strict_s0p_wind/artifacts/formula.tex`
- `runs/2026_03_02_physics_s3_t4__sym_strict_s0p_wind/artifacts/formula.sympy.txt`
- `runs/2026_03_02_physics_s3_t4__sym_strict_s0p_wind/artifacts/formula_metrics.json`
- `runs/2026_03_02_physics_s3_t4__sym_strict_s0p_wind/artifacts/predictions_test.parquet`
- `runs/2026_03_02_physics_s3_t4__sym_strict_s0p_wind/artifacts/separability.json`

### 2026_03_02_s0s3_t4__s3_comp_load_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_load_delta_h6`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24 --run-id 2026_03_02_s0s3_t4__s3_comp_load_delta_h6 --kind s3_comp_load_delta_h6 --target delta_load_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_temp,meteo_degree,meteo_pressure,solar_flag --lag-series load --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --use-gpu`

### 2026_03_02_s0s3_t4_nogrid__s3_combo_net_load

- phase: `05-structured-combination`
- kind: `net_load_from_components`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_combo_net_load/artifacts/eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_combo_net_load/artifacts/predictions_test.parquet`

### 2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_load_delta_h6`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24 --run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6 --kind s3_comp_load_delta_h6 --target delta_load_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_temp,meteo_degree,meteo_pressure,solar_flag --lag-series load --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/sparsity.json`

### 2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_solar_delta_h6`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24 --run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6 --kind s3_comp_solar_delta_h6 --target delta_solar_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series solar --lag-steps 24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/sparsity.json`

### 2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_wind_delta_h6`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24 --run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6 --kind s3_comp_wind_delta_h6 --target delta_wind_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_wind --lag-series wind --lag-steps 24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/sparsity.json`

### 2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.98 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs,exp' --safe-exp-clip 10.0 --eval-clip-quantiles 0.01,0.99 --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs,exp' --safe-exp-clip 10.0 --eval-clip-quantiles 0.01,0.99 --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs,exp' --safe-exp-clip 10.0 --eval-clip-quantiles 0.01,0.99 --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,x^4,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,x^4,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_999_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,x^4,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_poly4_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.98 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_995_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_999_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026-03-01_151000_kan_nobase_nogrid_gpu --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_01_151000_kan_nobase_nogrid_gpu/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_load_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_solar_delta_h6/artifacts/separability.json`

### 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/2026-03-02_s0s3_t4_nogrid/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id 2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6 --run-id 2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__sym_strict_r2_0_99_2026_03_02_s0s3_t4_nogrid_s3_comp_wind_delta_h6/artifacts/separability.json`

### detached_verify_20260226__kan_train__physics_first_exogenous_only_cpu

- phase: `02-kan-training`
- kind: `kan`

### local_tune7_20260303_solar_hw60_g5_k3_l001_e3_fast_mtr5000

- phase: `02-kan-training`
- kind: `local_tune`
- `runs/local_tune7_20260303_solar_hw60_g5_k3_l001_e3_fast_mtr5000/artifacts/eval_pruned.json`
- `runs/local_tune7_20260303_solar_hw60_g5_k3_l001_e3_fast_mtr5000/artifacts/predictions_test.parquet`
- `runs/local_tune7_20260303_solar_hw60_g5_k3_l001_e3_fast_mtr5000/artifacts/feature_importance.csv`
- `runs/local_tune7_20260303_solar_hw60_g5_k3_l001_e3_fast_mtr5000/artifacts/sparsity.json`

### local_tune7_20260303_solar_hw60_g5_k3_l002_e2_fast_mtr5000

- phase: `02-kan-training`
- kind: `local_tune_batch`

### locate_20260303_s0p_wind_delta_h6

- phase: `02-kan-training`
- kind: `s0p_wind_delta_h6`
- `runs/locate_20260303_s0p_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/locate_20260303_s0p_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/locate_20260303_s0p_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/locate_20260303_s0p_wind_delta_h6/artifacts/sparsity.json`

### locate_20260303_s4_pure_solar_abs_h6

- phase: `02-kan-training`
- kind: `s4_pure_solar_abs_h6`
- `runs/locate_20260303_s4_pure_solar_abs_h6/artifacts/eval_pruned.json`
- `runs/locate_20260303_s4_pure_solar_abs_h6/artifacts/predictions_test.parquet`
- `runs/locate_20260303_s4_pure_solar_abs_h6/artifacts/feature_importance.csv`
- `runs/locate_20260303_s4_pure_solar_abs_h6/artifacts/sparsity.json`

### paperref_20260306_121725__derived_h1_6

- phase: `01.5-derived-dataset`
- kind: `unknown`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/derive_dataset.py --source-data-run-id 2026-03-06_041802_0ad5813e --run-id paperref_20260306_121725__derived_h1_6 --horizon-steps 1,6 --net-load-lag-steps 1,12,48 --add-hub-wind --add-temp-ghi --add-absolute-targets --source-timestamp 2026-03-06_041853`

### paperref_20260306_121725_v2__baseline_torch_mlp_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `04-baselines-torch`
- kind: `mlp`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/baseline_torch.py --data-run-id paperref_20260306_121725__derived_h1_6 --run-id paperref_20260306_121725_v2__baseline_torch_mlp_paperref_20260306_121725_v2_s1_delta_net_load_h6 --model-type mlp --target delta_net_load_h6 --match-kan-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --sync-kan-feature-cols --sync-kan-budget --patience 0 --max-train-rows 200000 --use-gpu`
- `runs/paperref_20260306_121725_v2__baseline_torch_mlp_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test.json`
- `runs/paperref_20260306_121725_v2__baseline_torch_mlp_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__baseline_torch_mlp_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__baseline_torch_mlp_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`

### paperref_20260306_121725_v2__s0p_solar_delta_h6

- phase: `02-kan-training`
- kind: `s0p_solar_delta_h6`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id paperref_20260306_121725__derived_h1_6 --run-id paperref_20260306_121725_v2__s0p_solar_delta_h6 --kind s0p_solar_delta_h6 --target delta_solar_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series solar --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.005 --sparsify-lamb-entropy 1.5 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/paperref_20260306_121725_v2__s0p_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__s0p_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_121725_v2__s0p_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__s0p_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__s0p_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_121725_v2__s0p_solar_delta_h6/artifacts/sparsity.json`

### paperref_20260306_121725_v2__s0p_wind_delta_h6

- phase: `02-kan-training`
- kind: `s0p_wind_delta_h6`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id paperref_20260306_121725__derived_h1_6 --run-id paperref_20260306_121725_v2__s0p_wind_delta_h6 --kind s0p_wind_delta_h6 --target delta_wind_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_wind,meteo_irradiance,meteo_temp,solar_flag --lag-series wind --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.005 --sparsify-lamb-entropy 1.5 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/paperref_20260306_121725_v2__s0p_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__s0p_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_121725_v2__s0p_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__s0p_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__s0p_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_121725_v2__s0p_wind_delta_h6/artifacts/sparsity.json`

### paperref_20260306_121725_v2__s1_delta_net_load_h6

- phase: `02-kan-training`
- kind: `s1_delta_net_load_h6`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id paperref_20260306_121725__derived_h1_6 --run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --kind s1_delta_net_load_h6 --target delta_net_load_h6 --hidden-width 10 --max-train-rows 50000 --include-groups meteorology,solar,cyclic --lag-series load,wind,solar --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-warmup-update-grid --use-gpu`
- `runs/paperref_20260306_121725_v2__s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__s1_delta_net_load_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_121725_v2__s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__s1_delta_net_load_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_121725_v2__s1_delta_net_load_h6/artifacts/sparsity.json`

### paperref_20260306_121725_v2__s3_combo_net_load

- phase: `05-structured-combination`
- kind: `net_load_from_components`
- `runs/paperref_20260306_121725_v2__s3_combo_net_load/artifacts/eval_test.json`
- `runs/paperref_20260306_121725_v2__s3_combo_net_load/artifacts/predictions_test.parquet`

### paperref_20260306_121725_v2__s3_comp_load_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_load_delta_h6`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id paperref_20260306_121725__derived_h1_6 --run-id paperref_20260306_121725_v2__s3_comp_load_delta_h6 --kind s3_comp_load_delta_h6 --target delta_load_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_temp,meteo_degree,meteo_pressure,solar_flag --lag-series load --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/paperref_20260306_121725_v2__s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__s3_comp_load_delta_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_121725_v2__s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__s3_comp_load_delta_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_121725_v2__s3_comp_load_delta_h6/artifacts/sparsity.json`

### paperref_20260306_121725_v2__s3_comp_solar_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_solar_delta_h6`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id paperref_20260306_121725__derived_h1_6 --run-id paperref_20260306_121725_v2__s3_comp_solar_delta_h6 --kind s3_comp_solar_delta_h6 --target delta_solar_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series solar --lag-steps 24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/paperref_20260306_121725_v2__s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__s3_comp_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_121725_v2__s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__s3_comp_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_121725_v2__s3_comp_solar_delta_h6/artifacts/sparsity.json`

### paperref_20260306_121725_v2__s3_comp_wind_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_wind_delta_h6`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id paperref_20260306_121725__derived_h1_6 --run-id paperref_20260306_121725_v2__s3_comp_wind_delta_h6 --kind s3_comp_wind_delta_h6 --target delta_wind_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_wind --lag-series wind --lag-steps 24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/paperref_20260306_121725_v2__s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__s3_comp_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_121725_v2__s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__s3_comp_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_121725_v2__s3_comp_wind_delta_h6/artifacts/sparsity.json`

### paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.98 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs,exp' --safe-exp-clip 10.0 --eval-clip-quantiles 0.01,0.99 --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs,exp' --safe-exp-clip 10.0 --eval-clip-quantiles 0.01,0.99 --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs,exp' --safe-exp-clip 10.0 --eval-clip-quantiles 0.01,0.99 --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_medium_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,x^4,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,x^4,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_999_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,x^4,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_poly4_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.98 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_98_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s0p_solar_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s0p_wind_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_load_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_solar_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_wind_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6 --r2-threshold 0.995 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_995_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s0p_solar_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s0p_wind_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_load_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_solar_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_wind_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6 --r2-threshold 0.999 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_999_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s0p_solar_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_solar_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s0p_wind_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s0p_wind_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s1_delta_net_load_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s1_delta_net_load_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_load_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_load_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_solar_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_solar_delta_h6/artifacts/separability.json`

### paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
- manifest: `doc/thesis_sweeps/paperref_20260306_121725_v2/manifest.json`
- command: `modal run /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_symbolic.py --train-run-id paperref_20260306_121725_v2__s3_comp_wind_delta_h6 --run-id paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6 --r2-threshold 0.99 --weight-simple 0.9 --sample-rows 20000 --lib 'x,x^2,x^3,sin,cos,abs' --use-gpu`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_eval_test.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.tex`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_reconstructed.sympy.txt`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/formula_metrics.json`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/paperref_20260306_121725_v2__sym_strict_r2_0_99_paperref_20260306_121725_v2_s3_comp_wind_delta_h6/artifacts/separability.json`

### paperref_20260306_fullflow__derived_h1_6_72_144_576

- phase: `01.5-derived-dataset`
- kind: `unknown`

### paperref_20260306_fullflow__kan_delta_net_load_h6

- phase: `02-kan-training`
- kind: `paperref_main_kan_delta_net_load_h6`
- `runs/paperref_20260306_fullflow__kan_delta_net_load_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_fullflow__kan_delta_net_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_fullflow__kan_delta_net_load_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_fullflow__kan_delta_net_load_h6/artifacts/sparsity.json`

### paperref_20260306_fullflow__s3_comp_load_delta_load_h6

- phase: `02-kan-training`
- kind: `paperref_s3_comp_load_delta_load_h6`
- `runs/paperref_20260306_fullflow__s3_comp_load_delta_load_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_fullflow__s3_comp_load_delta_load_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_fullflow__s3_comp_load_delta_load_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_fullflow__s3_comp_load_delta_load_h6/artifacts/sparsity.json`

### paperref_20260306_fullflow__s3_comp_solar_delta_solar_h6

- phase: `02-kan-training`
- kind: `paperref_s3_comp_solar_delta_solar_h6`
- `runs/paperref_20260306_fullflow__s3_comp_solar_delta_solar_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_fullflow__s3_comp_solar_delta_solar_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_fullflow__s3_comp_solar_delta_solar_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_fullflow__s3_comp_solar_delta_solar_h6/artifacts/sparsity.json`

### paperref_20260306_fullflow__s3_comp_wind_delta_wind_h6

- phase: `02-kan-training`
- kind: `paperref_s3_comp_wind_delta_wind_h6`
- `runs/paperref_20260306_fullflow__s3_comp_wind_delta_wind_h6/artifacts/eval_pruned.json`
- `runs/paperref_20260306_fullflow__s3_comp_wind_delta_wind_h6/artifacts/predictions_test.parquet`
- `runs/paperref_20260306_fullflow__s3_comp_wind_delta_wind_h6/artifacts/feature_importance.csv`
- `runs/paperref_20260306_fullflow__s3_comp_wind_delta_wind_h6/artifacts/sparsity.json`

### s0a_physics_v2__s0a_solar_delta_h6

- phase: `02-kan-training`
- kind: `s0a_solar_delta_h6`
- manifest: `doc/thesis_sweeps/s0a_physics_v2/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s0a_physics_v2__s0a_solar_delta_h6 --kind s0a_solar_delta_h6 --target delta_solar_h6 --hidden-width 15 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series solar --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.001 --sparsify-lamb-entropy 1.0 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s0a_physics_v2__s0a_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/s0a_physics_v2__s0a_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/s0a_physics_v2__s0a_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/s0a_physics_v2__s0a_solar_delta_h6/artifacts/sparsity.json`

### s0a_physics_v2__s0a_wind_delta_h6

- phase: `02-kan-training`
- kind: `s0a_wind_delta_h6`
- manifest: `doc/thesis_sweeps/s0a_physics_v2/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s0a_physics_v2__s0a_wind_delta_h6 --kind s0a_wind_delta_h6 --target delta_wind_h6 --hidden-width 15 --max-train-rows 50000 --include-groups cyclic,meteo_wind,meteo_irradiance,meteo_temp,solar_flag --lag-series wind --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.001 --sparsify-lamb-entropy 1.0 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s0a_physics_v2__s0a_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/s0a_physics_v2__s0a_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/s0a_physics_v2__s0a_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/s0a_physics_v2__s0a_wind_delta_h6/artifacts/sparsity.json`

### s3_saveact_fix__s0p_solar_delta_h6

- phase: `02-kan-training`
- kind: `s0p_solar_delta_h6`
- manifest: `doc/thesis_sweeps/s3_saveact_fix/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s3_saveact_fix__s0p_solar_delta_h6 --kind s0p_solar_delta_h6 --target delta_solar_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series solar --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.005 --sparsify-lamb-entropy 1.5 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s3_saveact_fix__s0p_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/s3_saveact_fix__s0p_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/s3_saveact_fix__s0p_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/s3_saveact_fix__s0p_solar_delta_h6/artifacts/sparsity.json`

### s3_saveact_fix__s0p_wind_delta_h6

- phase: `02-kan-training`
- kind: `s0p_wind_delta_h6`
- manifest: `doc/thesis_sweeps/s3_saveact_fix/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s3_saveact_fix__s0p_wind_delta_h6 --kind s0p_wind_delta_h6 --target delta_wind_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_wind,meteo_irradiance,meteo_temp,solar_flag --lag-series wind --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.005 --sparsify-lamb-entropy 1.5 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s3_saveact_fix__s0p_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/s3_saveact_fix__s0p_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/s3_saveact_fix__s0p_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/s3_saveact_fix__s0p_wind_delta_h6/artifacts/sparsity.json`

### s3_saveact_fix__s3_comp_load_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_load_delta_h6`
- manifest: `doc/thesis_sweeps/s3_saveact_fix/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s3_saveact_fix__s3_comp_load_delta_h6 --kind s3_comp_load_delta_h6 --target delta_load_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_temp,meteo_degree,meteo_pressure,solar_flag --lag-series load --lag-steps 12,24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s3_saveact_fix__s3_comp_load_delta_h6/artifacts/eval_pruned.json`
- `runs/s3_saveact_fix__s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/s3_saveact_fix__s3_comp_load_delta_h6/artifacts/feature_importance.csv`
- `runs/s3_saveact_fix__s3_comp_load_delta_h6/artifacts/sparsity.json`

### s3_saveact_fix__s3_comp_solar_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_solar_delta_h6`
- manifest: `doc/thesis_sweeps/s3_saveact_fix/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s3_saveact_fix__s3_comp_solar_delta_h6 --kind s3_comp_solar_delta_h6 --target delta_solar_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series solar --lag-steps 24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s3_saveact_fix__s3_comp_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/s3_saveact_fix__s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/s3_saveact_fix__s3_comp_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/s3_saveact_fix__s3_comp_solar_delta_h6/artifacts/sparsity.json`

### s3_saveact_fix__s3_comp_wind_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_wind_delta_h6`
- manifest: `doc/thesis_sweeps/s3_saveact_fix/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s3_saveact_fix__s3_comp_wind_delta_h6 --kind s3_comp_wind_delta_h6 --target delta_wind_h6 --hidden-width 10 --max-train-rows 50000 --include-groups cyclic,meteo_wind --lag-series wind --lag-steps 24,48 --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s3_saveact_fix__s3_comp_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/s3_saveact_fix__s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/s3_saveact_fix__s3_comp_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/s3_saveact_fix__s3_comp_wind_delta_h6/artifacts/sparsity.json`

### s4_pure_v3__s4_pure_solar_abs_h6

- phase: `02-kan-training`
- kind: `s4_pure_solar_abs_h6`
- manifest: `doc/thesis_sweeps/s4_pure_v3/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s4_pure_v3__s4_pure_solar_abs_h6 --kind s4_pure_solar_abs_h6 --target solar_h6 --hidden-width 15 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series none --lag-steps none --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.001 --sparsify-lamb-entropy 1.0 --no-include-base --use-gpu`

### s4_pure_v5__s4_pure_load_abs_h6

- phase: `02-kan-training`
- kind: `s4_pure_load_abs_h6`
- manifest: `doc/thesis_sweeps/s4_pure_v5/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s4_pure_v5__s4_pure_load_abs_h6 --kind s4_pure_load_abs_h6 --target net_load_h6 --hidden-width 15 --max-train-rows 50000 --include-groups cyclic,meteo_temp,meteo_degree,meteo_pressure,meteo_wind,meteo_irradiance,solar_flag --lag-series none --lag-steps none --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.001 --sparsify-lamb-entropy 1.0 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s4_pure_v5__s4_pure_load_abs_h6/artifacts/eval_pruned.json`
- `runs/s4_pure_v5__s4_pure_load_abs_h6/artifacts/predictions_test.parquet`
- `runs/s4_pure_v5__s4_pure_load_abs_h6/artifacts/feature_importance.csv`
- `runs/s4_pure_v5__s4_pure_load_abs_h6/artifacts/sparsity.json`

### s4_pure_v5__s4_pure_solar_abs_h6

- phase: `02-kan-training`
- kind: `s4_pure_solar_abs_h6`
- manifest: `doc/thesis_sweeps/s4_pure_v5/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s4_pure_v5__s4_pure_solar_abs_h6 --kind s4_pure_solar_abs_h6 --target solar_h6 --hidden-width 15 --max-train-rows 50000 --include-groups cyclic,solar_geom,solar_flag,meteo_irradiance,meteo_temp --lag-series none --lag-steps none --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.001 --sparsify-lamb-entropy 1.0 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s4_pure_v5__s4_pure_solar_abs_h6/artifacts/eval_pruned.json`
- `runs/s4_pure_v5__s4_pure_solar_abs_h6/artifacts/predictions_test.parquet`
- `runs/s4_pure_v5__s4_pure_solar_abs_h6/artifacts/feature_importance.csv`
- `runs/s4_pure_v5__s4_pure_solar_abs_h6/artifacts/sparsity.json`

### s4_pure_v5__s4_pure_wind_abs_h6

- phase: `02-kan-training`
- kind: `s4_pure_wind_abs_h6`
- manifest: `doc/thesis_sweeps/s4_pure_v5/manifest.json`
- command: `modal run -d /Users/vfch/Documents/project/graduation-design/modal_jobs/kan_train.py --data-run-id 2026_03_02_physics_s3_t4__derived_h1_6_12_24 --run-id s4_pure_v5__s4_pure_wind_abs_h6 --kind s4_pure_wind_abs_h6 --target wind_h6 --hidden-width 15 --max-train-rows 50000 --include-groups cyclic,meteo_wind,meteo_irradiance,meteo_temp --lag-series none --lag-steps none --warmup-steps 200 --sparsify-steps 800 --refine-steps 200 --sparsify-lamb 0.001 --sparsify-lamb-entropy 1.0 --no-include-base --no-warmup-update-grid --use-gpu`
- `runs/s4_pure_v5__s4_pure_wind_abs_h6/artifacts/eval_pruned.json`
- `runs/s4_pure_v5__s4_pure_wind_abs_h6/artifacts/predictions_test.parquet`
- `runs/s4_pure_v5__s4_pure_wind_abs_h6/artifacts/feature_importance.csv`
- `runs/s4_pure_v5__s4_pure_wind_abs_h6/artifacts/sparsity.json`

### todoS1_20260303_solar_hw50_g5_k3_l0014_e3_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1_20260303_solar_hw50_g5_k3_l0014_e3_pr085_rm105_req_nwug`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0014_e3_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0014_e3_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0014_e3_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0014_e3_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS1_20260303_solar_hw50_g5_k3_l0016_e3_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1_20260303_solar_hw50_g5_k3_l0016_e3_pr085_rm105_req_nwug`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e3_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e3_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e3_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0016_e3_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS1_20260303_solar_hw50_g5_k3_l0018_e3_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1_20260303_solar_hw50_g5_k3_l0018_e3_pr085_rm105_req_nwug`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e3_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e3_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e3_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0018_e3_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1_20260303_solar_hw50_g5_k3_l0020_e4_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS1fix1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1fix1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0016_e35_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS1fix1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug

- phase: `02-kan-training`
- kind: `todoS1fix1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/eval_pruned.json`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/feature_importance.csv`
- `runs/todoS1fix1_20260303_solar_hw50_g5_k3_l0018_e35_pr085_rm105_req_nwug/artifacts/sparsity.json`

### todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr090_rm105_reqS_nwug

- phase: `02-kan-training`
- kind: `todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr090_rm105_reqS_nwug`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr090_rm105_reqS_nwug/artifacts/eval_pruned.json`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr090_rm105_reqS_nwug/artifacts/predictions_test.parquet`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr090_rm105_reqS_nwug/artifacts/feature_importance.csv`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr090_rm105_reqS_nwug/artifacts/sparsity.json`

### todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr095_rm105_reqS_nwug

- phase: `02-kan-training`
- kind: `todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr095_rm105_reqS_nwug`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr095_rm105_reqS_nwug/artifacts/eval_pruned.json`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr095_rm105_reqS_nwug/artifacts/predictions_test.parquet`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr095_rm105_reqS_nwug/artifacts/feature_importance.csv`
- `runs/todoS2_20260303_solar_hw50_g5_k3_l0015_e3_pr095_rm105_reqS_nwug/artifacts/sparsity.json`

### todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l00005_e2_pr08_rm11_req_nwug

- phase: `02-kan-training`
- kind: `todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l00005_e2_pr08_rm11_req_nwug`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l00005_e2_pr08_rm11_req_nwug/artifacts/eval_pruned.json`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l00005_e2_pr08_rm11_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l00005_e2_pr08_rm11_req_nwug/artifacts/feature_importance.csv`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l00005_e2_pr08_rm11_req_nwug/artifacts/sparsity.json`

### todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug

- phase: `02-kan-training`
- kind: `todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/eval_pruned.json`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/feature_importance.csv`
- `runs/todoW1_20260303_wind_windonly_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/sparsity.json`

### todoW2_20260303_wind_full_hw50_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug

- phase: `02-kan-training`
- kind: `todoW2_20260303_wind_full_hw50_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug`
- `runs/todoW2_20260303_wind_full_hw50_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/eval_pruned.json`
- `runs/todoW2_20260303_wind_full_hw50_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoW2_20260303_wind_full_hw50_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/feature_importance.csv`
- `runs/todoW2_20260303_wind_full_hw50_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/sparsity.json`

### todoW3_20260303_wind_windonly_nocyc_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug

- phase: `02-kan-training`
- kind: `todoW3_20260303_wind_windonly_nocyc_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug`
- `runs/todoW3_20260303_wind_windonly_nocyc_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/eval_pruned.json`
- `runs/todoW3_20260303_wind_windonly_nocyc_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/predictions_test.parquet`
- `runs/todoW3_20260303_wind_windonly_nocyc_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/feature_importance.csv`
- `runs/todoW3_20260303_wind_windonly_nocyc_hw40_g5_k3_w600_s500_r400_l0001_e2_pr08_rm11_req_nwug/artifacts/sparsity.json`

### transfer_2026-02-26_052920

- phase: `08-transfer-eval`
- kind: `kan_transfer`
- `runs/transfer_2026-02-26_052920/artifacts/eval_test.json`
- `runs/transfer_2026-02-26_052920/artifacts/predictions_test.parquet`
- figures:
  - `doc/paper_assets/figures/residual_box_transfer_2026-02-26_052920.png`
  - `doc/paper_assets/figures/residual_hist_transfer_2026-02-26_052920.png`
  - `doc/paper_assets/figures/residual_qq_transfer_2026-02-26_052920.png`
  - `doc/paper_assets/figures/seasonal_rmse_transfer_2026-02-26_052920.png`
  - `doc/paper_assets/figures/timeseries_transfer_2026-02-26_052920.png`

### tune10_20260303_wind_pressure_hw40_g5_k3_l0002_e2_nwug

- phase: `02-kan-training`
- kind: `tune10_20260303_wind_pressure_hw40_g5_k3_l0002_e2_nwug`
- `runs/tune10_20260303_wind_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune10_20260303_wind_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune10_20260303_wind_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune10_20260303_wind_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/sparsity.json`

### tune10_20260303_wind_temp_pressure_hw40_g5_k3_l0002_e2_nwug

- phase: `02-kan-training`
- kind: `tune10_20260303_wind_temp_pressure_hw40_g5_k3_l0002_e2_nwug`
- `runs/tune10_20260303_wind_temp_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune10_20260303_wind_temp_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune10_20260303_wind_temp_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune10_20260303_wind_temp_pressure_hw40_g5_k3_l0002_e2_nwug/artifacts/sparsity.json`

### tune10_20260303_wind_windonly_hw40_g5_k3_l00015_e2_nwug

- phase: `02-kan-training`
- kind: `tune10_20260303_wind_windonly_hw40_g5_k3_l00015_e2_nwug`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00015_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00015_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00015_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00015_e2_nwug/artifacts/sparsity.json`

### tune10_20260303_wind_windonly_hw40_g5_k3_l00025_e2_nwug

- phase: `02-kan-training`
- kind: `tune10_20260303_wind_windonly_hw40_g5_k3_l00025_e2_nwug`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00025_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00025_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00025_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l00025_e2_nwug/artifacts/sparsity.json`

### tune10_20260303_wind_windonly_hw40_g5_k3_l0002_e2_nwug

- phase: `02-kan-training`
- kind: `tune10_20260303_wind_windonly_hw40_g5_k3_l0002_e2_nwug`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l0002_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l0002_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l0002_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune10_20260303_wind_windonly_hw40_g5_k3_l0002_e2_nwug/artifacts/sparsity.json`

### tune10_20260303_wind_windonly_hw50_g5_k3_l0002_e2_nwug

- phase: `02-kan-training`
- kind: `tune10_20260303_wind_windonly_hw50_g5_k3_l0002_e2_nwug`
- `runs/tune10_20260303_wind_windonly_hw50_g5_k3_l0002_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune10_20260303_wind_windonly_hw50_g5_k3_l0002_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune10_20260303_wind_windonly_hw50_g5_k3_l0002_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune10_20260303_wind_windonly_hw50_g5_k3_l0002_e2_nwug/artifacts/sparsity.json`

### tune3_20260303_solar_hl16_16_16_g5_k3_l002_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hl16_16_16_g5_k3_l002_e10`
- `runs/tune3_20260303_solar_hl16_16_16_g5_k3_l002_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hl16_16_16_g5_k3_l002_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hl16_16_16_g5_k3_l002_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hl16_16_16_g5_k3_l002_e10/artifacts/sparsity.json`

### tune3_20260303_solar_hl32_16_8_g5_k3_l002_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hl32_16_8_g5_k3_l002_e10`
- `runs/tune3_20260303_solar_hl32_16_8_g5_k3_l002_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hl32_16_8_g5_k3_l002_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hl32_16_8_g5_k3_l002_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hl32_16_8_g5_k3_l002_e10/artifacts/sparsity.json`

### tune3_20260303_solar_hl64_16_g5_k3_l005_e15

- phase: `02-kan-training`
- kind: `tune3_solar_hl64_16_g5_k3_l005_e15`
- `runs/tune3_20260303_solar_hl64_16_g5_k3_l005_e15/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hl64_16_g5_k3_l005_e15/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hl64_16_g5_k3_l005_e15/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hl64_16_g5_k3_l005_e15/artifacts/sparsity.json`

### tune3_20260303_solar_hl64_8_g5_k3_l005_e15

- phase: `02-kan-training`
- kind: `tune3_solar_hl64_8_g5_k3_l005_e15`
- `runs/tune3_20260303_solar_hl64_8_g5_k3_l005_e15/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hl64_8_g5_k3_l005_e15/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hl64_8_g5_k3_l005_e15/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hl64_8_g5_k3_l005_e15/artifacts/sparsity.json`

### tune3_20260303_solar_hw40_m4_g10_k3_l001_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hw40_m4_g10_k3_l001_e10`
- `runs/tune3_20260303_solar_hw40_m4_g10_k3_l001_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hw40_m4_g10_k3_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hw40_m4_g10_k3_l001_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hw40_m4_g10_k3_l001_e10/artifacts/sparsity.json`

### tune3_20260303_solar_hw40_m4_g5_k3_l001_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hw40_m4_g5_k3_l001_e10`
- `runs/tune3_20260303_solar_hw40_m4_g5_k3_l001_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hw40_m4_g5_k3_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hw40_m4_g5_k3_l001_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hw40_m4_g5_k3_l001_e10/artifacts/sparsity.json`

### tune3_20260303_solar_hw80_g10_k3_l001_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hw80_g10_k3_l001_e10`
- `runs/tune3_20260303_solar_hw80_g10_k3_l001_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hw80_g10_k3_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hw80_g10_k3_l001_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hw80_g10_k3_l001_e10/artifacts/sparsity.json`

### tune3_20260303_solar_hw80_g3_k3_l001_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hw80_g3_k3_l001_e10`
- `runs/tune3_20260303_solar_hw80_g3_k3_l001_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hw80_g3_k3_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hw80_g3_k3_l001_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hw80_g3_k3_l001_e10/artifacts/sparsity.json`

### tune3_20260303_solar_hw80_g5_k3_l001_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hw80_g5_k3_l001_e10`
- `runs/tune3_20260303_solar_hw80_g5_k3_l001_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hw80_g5_k3_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hw80_g5_k3_l001_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hw80_g5_k3_l001_e10/artifacts/sparsity.json`

### tune3_20260303_solar_hw80_g7_k4_l001_e10

- phase: `02-kan-training`
- kind: `tune3_solar_hw80_g7_k4_l001_e10`
- `runs/tune3_20260303_solar_hw80_g7_k4_l001_e10/artifacts/eval_pruned.json`
- `runs/tune3_20260303_solar_hw80_g7_k4_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune3_20260303_solar_hw80_g7_k4_l001_e10/artifacts/feature_importance.csv`
- `runs/tune3_20260303_solar_hw80_g7_k4_l001_e10/artifacts/sparsity.json`

### tune4_20260303_solar_hw30_hm10_g5_k3_l001_e1_nwug

- phase: `02-kan-training`
- kind: `tune4_solar_hw30_hm10_g5_k3_l001_e1_nwug`
- `runs/tune4_20260303_solar_hw30_hm10_g5_k3_l001_e1_nwug/artifacts/eval_pruned.json`
- `runs/tune4_20260303_solar_hw30_hm10_g5_k3_l001_e1_nwug/artifacts/predictions_test.parquet`
- `runs/tune4_20260303_solar_hw30_hm10_g5_k3_l001_e1_nwug/artifacts/feature_importance.csv`
- `runs/tune4_20260303_solar_hw30_hm10_g5_k3_l001_e1_nwug/artifacts/sparsity.json`

### tune4_20260303_solar_hw60_g5_k3_l001_e3_nwug

- phase: `02-kan-training`
- kind: `tune4_solar_hw60_g5_k3_l001_e3_nwug`
- `runs/tune4_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/eval_pruned.json`
- `runs/tune4_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/predictions_test.parquet`
- `runs/tune4_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/feature_importance.csv`
- `runs/tune4_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/sparsity.json`

### tune4_20260303_solar_hw60_g5_k3_l002_e2_nwug

- phase: `02-kan-training`
- kind: `tune4_solar_hw60_g5_k3_l002_e2_nwug`
- `runs/tune4_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune4_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune4_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune4_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/sparsity.json`

### tune4_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug

- phase: `02-kan-training`
- kind: `tune4_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug`
- `runs/tune4_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/eval_pruned.json`
- `runs/tune4_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/predictions_test.parquet`
- `runs/tune4_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/feature_importance.csv`
- `runs/tune4_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/sparsity.json`

### tune5_20260303_solar_hw60_g5_k3_l0015_e2_nwug

- phase: `02-kan-training`
- kind: `kan`
- `runs/tune5_20260303_solar_hw60_g5_k3_l0015_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune5_20260303_solar_hw60_g5_k3_l0015_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune5_20260303_solar_hw60_g5_k3_l0015_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune5_20260303_solar_hw60_g5_k3_l0015_e2_nwug/artifacts/sparsity.json`

### tune5_20260303_solar_hw60_g5_k3_l002_e15_nwug

- phase: `02-kan-training`
- kind: `kan`
- `runs/tune5_20260303_solar_hw60_g5_k3_l002_e15_nwug/artifacts/eval_pruned.json`
- `runs/tune5_20260303_solar_hw60_g5_k3_l002_e15_nwug/artifacts/predictions_test.parquet`
- `runs/tune5_20260303_solar_hw60_g5_k3_l002_e15_nwug/artifacts/feature_importance.csv`
- `runs/tune5_20260303_solar_hw60_g5_k3_l002_e15_nwug/artifacts/sparsity.json`

### tune5_20260303_wind_pure_full_hw60_g5_k3_l001_e1_nwug

- phase: `02-kan-training`
- kind: `kan`
- `runs/tune5_20260303_wind_pure_full_hw60_g5_k3_l001_e1_nwug/artifacts/eval_pruned.json`
- `runs/tune5_20260303_wind_pure_full_hw60_g5_k3_l001_e1_nwug/artifacts/predictions_test.parquet`
- `runs/tune5_20260303_wind_pure_full_hw60_g5_k3_l001_e1_nwug/artifacts/feature_importance.csv`
- `runs/tune5_20260303_wind_pure_full_hw60_g5_k3_l001_e1_nwug/artifacts/sparsity.json`

### tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_nwug

- phase: `02-kan-training`
- kind: `kan`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_nwug/artifacts/eval_pruned.json`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_nwug/artifacts/predictions_test.parquet`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_nwug/artifacts/feature_importance.csv`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_nwug/artifacts/sparsity.json`

### tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_pr60_nwug

- phase: `02-kan-training`
- kind: `kan`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_pr60_nwug/artifacts/eval_pruned.json`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_pr60_nwug/artifacts/predictions_test.parquet`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_pr60_nwug/artifacts/feature_importance.csv`
- `runs/tune5_20260303_wind_pure_windonly_hw30_g5_k3_l001_e1_pr60_nwug/artifacts/sparsity.json`

### tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug

- phase: `02-kan-training`
- kind: `tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug`
- `runs/tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune6_20260303_solar_hw30_hm10_g5_k3_l001_e2_nwug/artifacts/sparsity.json`

### tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug

- phase: `02-kan-training`
- kind: `tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug`
- `runs/tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/eval_pruned.json`
- `runs/tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/predictions_test.parquet`
- `runs/tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/feature_importance.csv`
- `runs/tune6_20260303_solar_hw60_g5_k3_l001_e3_nwug/artifacts/sparsity.json`

### tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug

- phase: `02-kan-training`
- kind: `tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug`
- `runs/tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune6_20260303_solar_hw60_g5_k3_l002_e2_nwug/artifacts/sparsity.json`

### tune6_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug

- phase: `02-kan-training`
- kind: `tune6_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug`
- `runs/tune6_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/eval_pruned.json`
- `runs/tune6_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/predictions_test.parquet`
- `runs/tune6_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/feature_importance.csv`
- `runs/tune6_20260303_solar_hw80_g5_k3_l001_e1_pr90_rm105_nwug/artifacts/sparsity.json`

### tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug

- phase: `02-kan-training`
- kind: `tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0002_e2_nwug/artifacts/sparsity.json`

### tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0005_e2_nwug

- phase: `02-kan-training`
- kind: `tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0005_e2_nwug`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0005_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0005_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0005_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l0005_e2_nwug/artifacts/sparsity.json`

### tune6_20260303_wind_pure_windonly_hw30_g5_k3_l001_e2_nwug

- phase: `02-kan-training`
- kind: `tune6_20260303_wind_pure_windonly_hw30_g5_k3_l001_e2_nwug`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l001_e2_nwug/artifacts/eval_pruned.json`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l001_e2_nwug/artifacts/predictions_test.parquet`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l001_e2_nwug/artifacts/feature_importance.csv`
- `runs/tune6_20260303_wind_pure_windonly_hw30_g5_k3_l001_e2_nwug/artifacts/sparsity.json`

### tune7_20260303_solar_hw60_g5_k3_l002_e3_nwug

- phase: `02-kan-training`
- kind: `kan`

### tune9_20260303_solar_hl48_16_g5_k3_l001_e3_pr085_rm105_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_solar_hl48_16_g5_k3_l001_e3_pr085_rm105_nwug`
- `runs/tune9_20260303_solar_hl48_16_g5_k3_l001_e3_pr085_rm105_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_solar_hl48_16_g5_k3_l001_e3_pr085_rm105_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_solar_hl48_16_g5_k3_l001_e3_pr085_rm105_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_solar_hl48_16_g5_k3_l001_e3_pr085_rm105_nwug/artifacts/sparsity.json`

### tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug`
- `runs/tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_solar_hw50_g5_k3_l0015_e3_pr085_rm105_nwug/artifacts/sparsity.json`

### tune9_20260303_solar_hw60_g5_k3_l001_e3_pr090_rm105_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_solar_hw60_g5_k3_l001_e3_pr090_rm105_nwug`
- `runs/tune9_20260303_solar_hw60_g5_k3_l001_e3_pr090_rm105_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_solar_hw60_g5_k3_l001_e3_pr090_rm105_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_solar_hw60_g5_k3_l001_e3_pr090_rm105_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_solar_hw60_g5_k3_l001_e3_pr090_rm105_nwug/artifacts/sparsity.json`

### tune9_20260303_solar_hw60_g5_k3_l002_e3_pr085_rm105_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_solar_hw60_g5_k3_l002_e3_pr085_rm105_nwug`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e3_pr085_rm105_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e3_pr085_rm105_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e3_pr085_rm105_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e3_pr085_rm105_nwug/artifacts/sparsity.json`

### tune9_20260303_solar_hw60_g5_k3_l002_e4_pr085_rm105_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_solar_hw60_g5_k3_l002_e4_pr085_rm105_nwug`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e4_pr085_rm105_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e4_pr085_rm105_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e4_pr085_rm105_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_solar_hw60_g5_k3_l002_e4_pr085_rm105_nwug/artifacts/sparsity.json`

### tune9_20260303_wind_temp_pressure_hw60_g7_k3_l0002_e1_pr06_rm12_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_wind_temp_pressure_hw60_g7_k3_l0002_e1_pr06_rm12_nwug`
- `runs/tune9_20260303_wind_temp_pressure_hw60_g7_k3_l0002_e1_pr06_rm12_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_wind_temp_pressure_hw60_g7_k3_l0002_e1_pr06_rm12_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_wind_temp_pressure_hw60_g7_k3_l0002_e1_pr06_rm12_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_wind_temp_pressure_hw60_g7_k3_l0002_e1_pr06_rm12_nwug/artifacts/sparsity.json`

### tune9_20260303_wind_temp_pressure_hw80_g7_k3_l0001_e1_pr06_rm12_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_wind_temp_pressure_hw80_g7_k3_l0001_e1_pr06_rm12_nwug`
- `runs/tune9_20260303_wind_temp_pressure_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_wind_temp_pressure_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_wind_temp_pressure_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_wind_temp_pressure_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/sparsity.json`

### tune9_20260303_wind_windonly_hw60_g10_k3_l00005_e1_pr06_rm12_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_wind_windonly_hw60_g10_k3_l00005_e1_pr06_rm12_nwug`
- `runs/tune9_20260303_wind_windonly_hw60_g10_k3_l00005_e1_pr06_rm12_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_wind_windonly_hw60_g10_k3_l00005_e1_pr06_rm12_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_wind_windonly_hw60_g10_k3_l00005_e1_pr06_rm12_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_wind_windonly_hw60_g10_k3_l00005_e1_pr06_rm12_nwug/artifacts/sparsity.json`

### tune9_20260303_wind_windonly_hw60_g7_k5_l0001_e1_pr06_rm12_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_wind_windonly_hw60_g7_k5_l0001_e1_pr06_rm12_nwug`
- `runs/tune9_20260303_wind_windonly_hw60_g7_k5_l0001_e1_pr06_rm12_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_wind_windonly_hw60_g7_k5_l0001_e1_pr06_rm12_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_wind_windonly_hw60_g7_k5_l0001_e1_pr06_rm12_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_wind_windonly_hw60_g7_k5_l0001_e1_pr06_rm12_nwug/artifacts/sparsity.json`

### tune9_20260303_wind_windonly_hw80_g7_k3_l0001_e1_pr06_rm12_nwug

- phase: `02-kan-training`
- kind: `tune9_20260303_wind_windonly_hw80_g7_k3_l0001_e1_pr06_rm12_nwug`
- `runs/tune9_20260303_wind_windonly_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/eval_pruned.json`
- `runs/tune9_20260303_wind_windonly_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/predictions_test.parquet`
- `runs/tune9_20260303_wind_windonly_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/feature_importance.csv`
- `runs/tune9_20260303_wind_windonly_hw80_g7_k3_l0001_e1_pr06_rm12_nwug/artifacts/sparsity.json`

### tune_20260303_solar_hl32_32_pr08_rm11_l005_e15

- phase: `02-kan-training`
- kind: `tune_solar_hl32_32_pr08_rm11_l005_e15`
- `runs/tune_20260303_solar_hl32_32_pr08_rm11_l005_e15/artifacts/eval_pruned.json`
- `runs/tune_20260303_solar_hl32_32_pr08_rm11_l005_e15/artifacts/predictions_test.parquet`
- `runs/tune_20260303_solar_hl32_32_pr08_rm11_l005_e15/artifacts/feature_importance.csv`
- `runs/tune_20260303_solar_hl32_32_pr08_rm11_l005_e15/artifacts/sparsity.json`

### tune_20260303_solar_pr06_rm11_hw15_l001_e10

- phase: `02-kan-training`
- kind: `tune_solar_pr06_rm11_hw15_l001_e10`
- `runs/tune_20260303_solar_pr06_rm11_hw15_l001_e10/artifacts/eval_pruned.json`
- `runs/tune_20260303_solar_pr06_rm11_hw15_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune_20260303_solar_pr06_rm11_hw15_l001_e10/artifacts/feature_importance.csv`
- `runs/tune_20260303_solar_pr06_rm11_hw15_l001_e10/artifacts/sparsity.json`

### tune_20260303_solar_pr07_rm11_hw15_l001_e10

- phase: `02-kan-training`
- kind: `tune_solar_pr07_rm11_hw15_l001_e10`
- `runs/tune_20260303_solar_pr07_rm11_hw15_l001_e10/artifacts/eval_pruned.json`
- `runs/tune_20260303_solar_pr07_rm11_hw15_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune_20260303_solar_pr07_rm11_hw15_l001_e10/artifacts/feature_importance.csv`
- `runs/tune_20260303_solar_pr07_rm11_hw15_l001_e10/artifacts/sparsity.json`

### tune_20260303_solar_pr07_rm13_hw15_l001_e10

- phase: `02-kan-training`
- kind: `tune_solar_pr07_rm13_hw15_l001_e10`
- `runs/tune_20260303_solar_pr07_rm13_hw15_l001_e10/artifacts/eval_pruned.json`
- `runs/tune_20260303_solar_pr07_rm13_hw15_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune_20260303_solar_pr07_rm13_hw15_l001_e10/artifacts/feature_importance.csv`
- `runs/tune_20260303_solar_pr07_rm13_hw15_l001_e10/artifacts/sparsity.json`

### tune_20260303_solar_pr08_rm11_hw60_l001_e10

- phase: `02-kan-training`
- kind: `tune_solar_pr08_rm11_hw60_l001_e10`
- `runs/tune_20260303_solar_pr08_rm11_hw60_l001_e10/artifacts/eval_pruned.json`
- `runs/tune_20260303_solar_pr08_rm11_hw60_l001_e10/artifacts/predictions_test.parquet`
- `runs/tune_20260303_solar_pr08_rm11_hw60_l001_e10/artifacts/feature_importance.csv`
- `runs/tune_20260303_solar_pr08_rm11_hw60_l001_e10/artifacts/sparsity.json`

