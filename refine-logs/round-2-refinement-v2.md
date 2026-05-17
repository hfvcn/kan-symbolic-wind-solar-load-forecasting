# Round 2 Refinement (v2 Cycle)

## Problem Anchor
[Verbatim — unchanged]

## Anchor Check
- Original bottleneck: Autoregressive dominance prunes physical variables from symbolic formulas
- Why the revised method still addresses it: S2 now includes direct-task blocking (closes the integration gap)
- Reviewer suggestions rejected as drift: None

## Simplicity Check
- Dominant contribution: Shortcut competition mechanism, tested by blocking intervention
- Components removed/merged: TGR demoted to one-time diagnostic
- Added: Active-edge count as continuous signal; direct-task blocking comparison
- Still the smallest adequate route: one controlled ablation + one decomposition

## Changes Made

### 1. CRITICAL: Direct-Task Blocking Comparison Added
- **Reviewer said**: "Close the integration between focused-teacher S2 evidence and direct net-load collapse. Add ONE blocked-vs-unblocked comparison on direct task."
- **Action**: Add one S2 blocking experiment on the DIRECT `delta_net_load_h6` task. Train with `lag_series=["load"]` (remove wind_lag/solar_lag), keep all meteorological features. Compare VER(physical) against the confirmed 0/9 baseline.
- **Reasoning**: This closes the narrative loop. The 4-case evidence chain becomes:
  - Direct with all lags → VER=0 (complete collapse)
  - Direct with blocked wind/solar lags → VER(physical) measured (partial recovery?)
  - Focused wind with lags → VER(wind) low
  - Focused wind without lags → VER(wind) high
  The direct-task comparison shows that even on the hardest task, blocking the autoregressive shortcut produces measurable identifiability change.
- **Prediction**: On direct task, blocking wind/solar lags may not fully restore physical variables (because load_lag still dominates), but even partial VER increase proves the mechanism operates on the original task.
- **Cost**: +5 runs (5 seeds on direct blocked). Total S2 budget: ~15-20 runs.

### 2. IMPORTANT: Active-Edge Count as Continuous Signal
- **Reviewer said**: "Add one continuous competition signal beyond binary VER/FAR."
- **Action**: Report `active_edge_count(v)` — the number of non-zero edges connected to variable v after pruning. This is already captured in `feature_importance.csv`. Use it as a continuous complement to binary VER.
- **Reasoning**: Binary VER is coarse (0 or 1 per seed). Active-edge count provides gradient information: "how strongly does the variable survive?" vs "does it survive at all?" The existing wind horizon data already shows this: wind_speed_edges varies from 0 to 9 to 11 across horizons.
- **Presentation**: Report VER (binary entry), FAR (formula presence), and edge_count (continuous intensity) together. edge_count is not a new metric — it's the granular version of VER.

### 3. IMPORTANT: S3 Fully Specified
- **Reviewer said**: "Specify S3 exactly: target definitions, training inputs, combination rule, what 'preserves' means."
- **Action**: Full specification below.

#### S3 Exact Specification

**Target definitions** (all at horizon h=6, i.e., 30 minutes ahead):
- `delta_load_h6 = load(t+6) - load(t)`: change in total electrical load
- `delta_wind_h6 = wind(t+6) - wind(t)`: change in wind power generation
- `delta_solar_h6 = solar(t+6) - solar(t)`: change in solar power generation

**Training inputs per sub-task**:
- Load sub-KAN: `temp_2m_c`, `cdd_18c`, `hdd_18c`, `load_lag_12`, `load_lag_24`, `load_lag_48`, `hour_sin`, `hour_cos`, `dow_sin`, `dow_cos`
- Wind sub-KAN: `wind_speed_10m_m_s`, `wind_speed_10m_m_s_cubed`, `wind_speed_hub_est`, `wind_lag_12`, `wind_lag_24`, `wind_lag_48`, `hour_sin`, `hour_cos`
- Solar sub-KAN: `ghi_w_m2`, `ghi_day_w_m2`, `solar_altitude`, `is_night`, `solar_lag_12`, `solar_lag_24`, `solar_lag_48`, `hour_sin`, `hour_cos`

**Combination rule**: Fixed additive, no learned weights:
```
delta_net_load_h6_composite = delta_load_h6_pred - delta_wind_h6_pred - delta_solar_h6_pred
```
Reconstruction to absolute: `net_load_h6_pred = net_load(t) + delta_net_load_h6_composite`

**"Preserves" definition**: For each sub-task, VER(target_physical_var) ≥ 3/5 seeds AND FAR(target_physical_var) ≥ 3/5 seeds. Specifically:
- Wind sub-formula: VER(wind_speed_10m_m_s) ≥ 3/5
- Solar sub-formula: VER(ghi_w_m2) ≥ 3/5
- Load sub-formula: VER(temp_2m_c) ≥ 3/5

**Evaluation**: Composite RMSE and skill on absolute test set, compared against direct KAN teacher and persistence.

### 4. IMPORTANT: Novelty Language Narrowed
- **Reviewer said**: "Novelty is not 'KAN interpretability in energy' — it is the mechanism study of shortcut competition causing identifiability collapse."
- **Action**: All framing now centers on "shortcut competition mechanism." KAN and energy forecasting are the setting, not the contribution.

## Revised Proposal v4

# Research Proposal v4: Autoregressive Shortcut Competition Destroys Symbolic Identifiability — Evidence from KAN Net Load Forecasting

## Problem Anchor
[Same as all rounds]

## Technical Gap

KAN symbolic extraction succeeds on clean physics problems (Liu et al. ICLR 2025; PRX 2025) but faces a structural challenge in real-world time series: autoregressive lag features dominate sparsification and prune away physical meteorological variables. No prior work identifies or tests this mechanism.

## Method Thesis

In KAN-based symbolic extraction for net load forecasting, autoregressive shortcut competition — not variable irrelevance — is the primary mechanism that prevents physical variables from surviving sparsification-to-symbolization. An interventional blocking test isolates this mechanism across both focused and direct tasks, and structured decomposition partially restores identifiability.

## Contribution Focus

- **Dominant**: Identification + interventional testing of shortcut competition mechanism. Key measurement: ΔVER (VER_blocked - VER_unblocked) with bootstrap CI, complemented by active-edge count as continuous signal.
- **Supporting**: S3 decomposition preserves physical variables under task-level structural intervention.

## Pipeline (No Modifications to KAN Training)

KAN teacher → L1+entropy sparsification → structured pruning → symbolic extraction → SymPy formula → test evaluation

## Identifiability Diagnostics

| Metric | Type | Definition | Role |
|--------|------|------------|------|
| VER | Binary | Fraction of seeds where variable v has ≥1 active edge post-pruning | Primary: does variable survive? |
| FAR | Binary | Fraction of seeds where variable v appears in final SymPy expression | Primary: does variable reach formula? |
| edge_count(v) | Continuous | Number of active edges connected to v post-pruning | Continuous complement to VER |
| TGR | Ratio | RMSE_symbolic / RMSE_teacher | Diagnostic: overall extraction quality (reported once) |
| ΔVER | Contrast | VER(blocked) - VER(unblocked) | Key measurement for mechanism test |

## Four-Act Experimental Structure

### Act 1 — Baseline [COMPLETE]
KAN: skill=0.453. MLP: skill=0.430 (p=0.0005). PySR: skill≈0.20. Persistence: skill=0.0.
One table, minimal narrative space.

### Act 2 — Formula Collapse [COMPLETE]
9 symbolic configs on direct teacher → ALL load-only. VER(any_physical) = 0/9. edge_count(physical) = 0.
One table + one formula rendering.

### Act 3 — Mechanism Test [CORE — NEW EXPERIMENTS]

**Case 1: Solar positive control** [COMPLETE]
- Focused solar teacher, GHI VER=3/3, FAR=3/3, edge_count(GHI)>0 consistently
- Interpretation: strong physical signal survives even with lag competition

**Case 2: Wind boundary** [COMPLETE]
- Non-monotonic VER across horizons: edge_count(wind)=0,0,9,0,0 at h=6/72/144/288/576
- Interpretation: identifiability depends on horizon-specific signal-to-lag ratio

**Case 3: Blocked-lag intervention on FOCUSED tasks** [NEW, 5 seeds]
- Focused wind teacher: lag_series=["load"] (block wind_lag_*)
- Focused solar teacher: lag_series=["load"] (block solar_lag_*)
- Measure: ΔVER(wind_speed), ΔVER(GHI), Δedge_count, with bootstrap 95% CI
- Prediction: ΔVER(wind) >> 0 (large increase), ΔVER(GHI) ≈ 0 (already high)
- Cost: ~10 runs

**Case 4: Blocked-lag intervention on DIRECT task** [NEW, 5 seeds]
- Direct delta_net_load_h6 teacher: lag_series=["load"] (block wind_lag_*, solar_lag_*)
- Same meteorological features retained
- Measure: ΔVER(any_physical) relative to Act 2 baseline of 0/9
- Prediction: Partial recovery — some physical variables now enter, but load_lag still dominates
- This closes the loop: mechanism operates on the original task, not just focused teachers
- Cost: ~5 runs

### Act 4 — S3 Decomposition [80% COMPLETE → POLISH]

**Exact specification**:
- Targets: delta_load_h6, delta_wind_h6, delta_solar_h6
- Inputs: each sub-KAN gets its target-relevant physical variables + calendar + task-specific lags
- Combination: `net_load_composite = load_pred - wind_pred - solar_pred` (fixed additive)
- "Preserves" = VER(target_var) ≥ 3/5 seeds per sub-task
- Evaluation: composite skill vs persistence on absolute test set

**Remaining work**: LaTeX rendering, composite metrics, VER/FAR per sub-task

## Training Details
- KAN [2, width, 1], grid=3-5, k=3
- warmup 200 → sparsify 800 (λ_L1=1.0, λ_entropy=2.0) → prune 80% → refine 200
- PERFORM ERCOT 5-min, chronological 60/20/20, 48-step gap, Z-score
- Seeds: 3 for frozen evidence; 5 for S2 key comparisons + S3 sub-tasks

## Thesis Chapters
1. Introduction (renewable + interpretability)
2. Literature Review (KAN ICLR/PRX 2025, SR, MCKAN, energy forecasting)
3. Data & Problem (PERFORM, delta targets, features, horizons)
4. Method (pipeline, VER/FAR/edge_count, blocking protocol, S3 specification)
5. Experiments:
   - 5.1 Accuracy baseline → Table 1
   - 5.2 Formula collapse → Table 2 + formula
   - 5.3 Solar/Wind identifiability → Tables 3-4
   - 5.4 Blocked-lag intervention (focused + direct) → Table 5 + ΔVER figure [CENTERPIECE]
   - 5.5 S3 decomposition → Table 6 + composite formula
6. Discussion (mechanism, tradeoffs, limitations)
7. Conclusion

Appendix: horizon landscape, S0 safe functions, stratified analysis, all formulas, boundary failure

## Compute

| Phase | Runs | GPU-hours |
|-------|------|-----------|
| S2 focused blocking | 10 (5 seeds × 2 targets) | 5-8h |
| S2 direct blocking | 5 (5 seeds × 1 target) | 3-5h |
| S3 polish | 0 (post-processing) | 0 |
| Total new | ~15 | ~8-13h |

Critical path: S3 polish (M0) → S2 blocking runs (M1) → Analysis + ΔVER (M2) → Paper (M3)
