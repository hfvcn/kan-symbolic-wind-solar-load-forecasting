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
- `doc/paper_assets/kan_pysr_cross_validation_2026-02-26_064508_3e631069.md`
- `doc/paper_assets/physics_mapping_2026-02-26_041718_5579aeeb.md`
- `doc/paper_assets/physics_mapping_2026-02-26_090620_1fc7d27a.md`
- `doc/paper_assets/physics_mapping_2026-02-26_091400_ba9fd48c.md`
- `doc/paper_assets/physics_mapping_2026-02-26_130037_55f49a5c.md`
- `doc/paper_assets/physics_mapping_2026-02-26_130651_18ca3f58.md`
- `doc/paper_assets/sensitivity_summary_2026-02-26_041718_5579aeeb.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_090620_1fc7d27a.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_091400_ba9fd48c.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_130037_55f49a5c.csv`
- `doc/paper_assets/sensitivity_summary_2026-02-26_130651_18ca3f58.csv`

## Runs

### 2026-02-25_093805_9134fe03

- phase: `00-smoke-test`
- kind: `smoke_test`

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
- `runs/2026-02-26_041718_5579aeeb/artifacts/physics_mapping.json`
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

### 2026-02-26_052312_f85bed5b

- phase: `01-data-pipeline`
- kind: `data_pipeline`

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
- `runs/2026-02-26_090620_1fc7d27a/artifacts/physics_mapping.json`
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
- `runs/2026-02-26_091400_ba9fd48c/artifacts/physics_mapping.json`
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
- `runs/2026-02-26_130037_55f49a5c/artifacts/physics_mapping.json`
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
- `runs/2026-02-26_130651_18ca3f58/artifacts/physics_mapping.json`
- `runs/2026-02-26_130651_18ca3f58/artifacts/predictions_test.parquet`
- `runs/2026-02-26_130651_18ca3f58/artifacts/separability.json`
- figures:
  - `doc/paper_assets/figures/formula_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/residual_box_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/residual_hist_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/residual_qq_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/seasonal_rmse_2026-02-26_130651_18ca3f58.png`
  - `doc/paper_assets/figures/timeseries_2026-02-26_130651_18ca3f58.png`

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

