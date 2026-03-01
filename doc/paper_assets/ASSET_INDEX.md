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

### 2026_03_01_142726_9ab14f0b__derived_h1_6_12_24

- phase: `01.5-derived-dataset`
- kind: `unknown`

### 2026_03_02_s0s3_t4__s3_comp_load_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_load_delta_h6`

### 2026_03_02_s0s3_t4_nogrid__s3_combo_net_load

- phase: `05-structured-combination`
- kind: `net_load_from_components`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_combo_net_load/artifacts/eval_test.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_combo_net_load/artifacts/predictions_test.parquet`

### 2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_load_delta_h6`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_load_delta_h6/artifacts/sparsity.json`

### 2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_solar_delta_h6`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_solar_delta_h6/artifacts/sparsity.json`

### 2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6

- phase: `02-kan-training`
- kind: `s3_comp_wind_delta_h6`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/eval_test_reconstructed.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/eval_pruned.json`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/predictions_test.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/predictions_test_reconstructed.parquet`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/feature_importance.csv`
- `runs/2026_03_02_s0s3_t4_nogrid__s3_comp_wind_delta_h6/artifacts/sparsity.json`

### 2026_03_02_s0s3_t4_nogrid__sym_medium_r2_0_98_2026_03_01_151000_kan_nobase_nogrid_gpu

- phase: `03-symbolic-extraction`
- kind: `kan_symbolic`
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

