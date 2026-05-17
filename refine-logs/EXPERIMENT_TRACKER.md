# Experiment Tracker

## Remaining Runs (Ordered by Priority)

| Run ID | Milestone | Block | Purpose | System / Variant | Priority | Status | Notes |
|--------|-----------|-------|---------|------------------|----------|--------|-------|
| R001 | M0 | B5 | Verify S3 sub-formula LaTeX rendering | wind/solar/load formulas | MUST | TODO | Check `formula.sympy.txt` + `formula.tex` for all 3 sub-runs |
| R002 | M0 | B5 | Compute S3 composite prediction + skill | `combine_net_load_runs.py` | MUST | TODO | Use existing sub-model predictions; reconstruct abs; compute skill |
| R003 | M0 | B5 | S3 composite time series figure | `make_thesis_figures.py` on composite | MUST | TODO | Actual vs predicted with contribution breakdown |
| R004 | M0 | B5 | S3 identifiability metrics (VER/FAR/TGR per sub-task) | Post-processing | MUST | TODO | Compute VER/FAR from feature_importance.csv; TGR from formula_eval_test.json |
| R005 | M1 | B6 | Implement safe_exp/safe_div in symbolic.py | Code change | NICE | TODO | `safe_exp(x)=exp(clip(x,-10,10))`, `safe_div(a,b)=a/(b+1e-8)` |
| R006 | M1 | B6 | Add quantile clipping to Phase 3 eval | Code change | NICE | TODO | Clip inputs to train-set [p1, p99] before formula evaluation |
| R007 | M2 | B6 | Run S0 sweep: medium lib + safe functions | Modal cloud, 9 configs | NICE | TODO | 3 r2_thresholds × {strict+safe, medium+safe, medium+safe+clip} |
| R008 | M2 | B6 | Evaluate S0 results: reconstruct + TGR + NaN check | Post-processing | NICE | TODO | Target: TGR < 1.5, NaN count = 0 |
| R009 | M3 | B8 | Stratified analysis on S3 composite | `stratified_error_analysis.py` | NICE | TODO | Depends on R002 completing first |
| R010 | M3 | B8 | Robustness comparison table | Post-processing | NICE | TODO | KAN vs S3 composite across volatility/temp slices |

## Completed Blocks (Evidence Frozen)

| Block | Claims | Key Evidence Files | Frozen Date |
|-------|--------|--------------------|-------------|
| B1 | C1, C5 | `comparison_table.csv`, `paired_significance_main_20260309.csv` | 2026-03-09 |
| B2 | C2 | `direct_teacher_cloud_check_20260309.csv`, formula.sympy.txt (load-only) | 2026-03-09 |
| B3 | C3 (solar) | `solar_ablation_summary_20260304.csv`, `solar_stratified_error_20260309.csv` | 2026-03-09 |
| B4 | C3 (wind) | `wind_ablation_summary_20260306.csv`, `wind_stratified_error_20260309.csv` | 2026-03-09 |
| B7 | boundary | `solar_h288_boundary_20260306.json`, `solar_h288_boundary_20260306.png` | 2026-03-06 |

## Key Run IDs (Whitelist)

| Purpose | Run ID |
|---------|--------|
| Main KAN teacher | `2026-03-01_151000_kan_nobase_nogrid_gpu` |
| Matched MLP baseline | `2026-03-01_155600_baseline_mlp_match_kan151000` |
| Main symbolic formula | `2026-03-01_160200_sym_strict_r2_0_995__kan151000` |
| S3 wind sub-model | `paperref_20260306_121725_v2__s3_comp_wind_delta_h6` or fullflow equivalent |
| S3 solar sub-model | `paperref_20260306_121725_v2__s3_comp_solar_delta_h6` or fullflow equivalent |
| S3 load sub-model | `paperref_20260306_121725_v2__s3_comp_load_delta_h6` or fullflow equivalent |
| S3 composite | `paperref_20260306_121725_v2__s3_combo_net_load_h6` or fullflow equivalent |
| Solar h=288 boundary | `2026-03-04_101610_37271ac2` |
