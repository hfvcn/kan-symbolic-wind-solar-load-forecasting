# Research Proposal: Autoregressive Shortcut Competition Destroys Symbolic Identifiability — Evidence from KAN Net Load Forecasting

## Problem Anchor

- **Bottom-line problem**: Extract physically meaningful, human-readable mathematical formulas from high-accuracy KAN models for net load forecasting. The key technical barrier: autoregressive dominance causes physical meteorological variables to be pruned away during sparsification, collapsing formulas to load-only expressions.

- **Must-solve bottleneck**: The transfer gap (KAN skill=0.453 → symbolic formula skill=0.076) is unacceptable, AND the formula loses all physical variables. We must understand WHY variables are lost, provide interventional evidence for the mechanism, and demonstrate constructive solutions.

- **Non-goals**: New architecture, SOTA accuracy, deployable system, dataset replacement, formal causal theory.

- **Constraints**: Graduation thesis (~4 weeks); 247+ runs already complete; Modal cloud GPU; must reference MCKAN (Chen et al., 2025); existing pykan + Phase3 symbolic pipeline.

- **Success condition**: A thesis demonstrating (1) KAN+symbolic works for net load; (2) systematic + interventional evidence for WHY physical variables enter/exit formulas; (3) quantitative identifiability diagnostics; (4) S3 decomposition as constructive solution; (5) honest failure/boundary documentation.

## Technical Gap

Current KAN symbolic regression work (Liu et al. ICLR 2025; PRX 2025; arXiv 2504.03913) demonstrates successful formula extraction on clean physics problems and controlled benchmarks. However, none address the structural challenge of real-world time series forecasting: when autoregressive lag features are available, they dominate sparsification and cause physical meteorological variables to be pruned away, collapsing formulas to trivial autoregressive expressions.

This is not a failure of KAN or symbolic regression — it is a structural property of high-frequency time series where lag features explain >90% of short-term variance. Understanding this mechanism and finding principled workarounds is essential for KAN-based interpretability in energy forecasting. This is the first mechanism-level study of this phenomenon.

## Method Thesis

**One-sentence thesis**: In KAN-based symbolic extraction for net load forecasting, autoregressive shortcut competition — not variable irrelevance — is the primary mechanism that prevents physical meteorological variables from surviving the sparsification-to-symbolization pipeline; an interventional blocking test isolates this mechanism on both focused and direct tasks, and structured task decomposition partially restores identifiability.

## Contribution Focus

- **Dominant contribution**: Identification and interventional testing of the autoregressive shortcut competition mechanism in KAN symbolic extraction, operationalized via Variable Entry Rate (VER) and Formula Appearance Rate (FAR) measured across blocked vs. unblocked lag conditions. The key measurement is ΔVER = VER(blocked) - VER(unblocked), with pre-specified decision rules and bootstrap confidence intervals. Active-edge count provides a continuous complement.

- **Supporting contribution**: S3 structured task decomposition that preserves physical variable presence by decomposing net_load into physically natural sub-tasks (wind, solar, load), each with its target physical variable.

- **Explicit non-contributions**: No new architecture, no SOTA accuracy claims, no formal causal theory, no strict leak-free guarantee.

## Pipeline (No Modifications to KAN Training)

```
KAN teacher training → L1+entropy sparsification → structured pruning
→ symbolic extraction (pykan suggest_symbolic / fix_symbolic) → SymPy formula
→ evaluation on test set
```

## Identifiability Diagnostics

| Metric | Type | Definition | Role |
|--------|------|------------|------|
| VER | Binary | Fraction of seeds where variable v has ≥1 active edge post-pruning | Primary: does variable survive sparsification? |
| FAR | Binary | Fraction of seeds where variable v appears in final SymPy expression | Primary: does variable reach formula? |
| edge_count(v) | Continuous | Number of active edges connected to v post-pruning | Continuous complement to VER |
| TGR | Ratio | RMSE_symbolic / RMSE_teacher | Diagnostic: overall extraction quality (reported once) |
| ΔVER | Contrast | VER(blocked) - VER(unblocked) | Key measurement for mechanism test |

## Pre-Specified Decision Rules

### Case 3 (Focused tasks — wind and solar):
- **PRIMARY ENDPOINT**: ΔVER(wind_speed) on focused wind teacher
- **SUCCESS**: ΔVER > 0 with bootstrap 95% CI lower bound > 0, AND mean edge_count(wind_speed, blocked) > mean edge_count(wind_speed, unblocked)
- **STRONG SUCCESS**: ΔVER ≥ 2/5 (wind_speed enters in ≥2 more seeds when blocked)
- **NULL**: ΔVER CI includes 0 → shortcut competition not confirmed for wind on focused task
- **SECONDARY**: ΔVER(GHI) on focused solar teacher (expected ≈0 since solar already robust)

### Case 4 (Direct task):
- **PRIMARY ENDPOINT**: ΔVER(any_physical_variable) on direct delta_net_load_h6
- **Definition of "any_physical"**: {wind_speed_10m_m_s, ghi_w_m2, temp_2m_c}
- **SUCCESS**: At least ONE physical variable shows ΔVER > 0 with 95% CI lower bound > 0
- **STRONG SUCCESS**: ≥2 physical variables show ΔVER > 0
- **NULL**: No physical variable shows ΔVER CI excluding 0 → mechanism does not produce measurable effect on direct task (multi-level lag dominance too strong)
- **INTERPRETATION IF NULL**: Shortcut competition is real (confirmed by Case 3 on focused tasks) but insufficient to overcome multi-level lag dominance on full net-load. This motivates S3 decomposition as the necessary constructive solution.

### Experimental Control Protocol
All settings IDENTICAL between blocked and unblocked except:
- `lag_series`: `["load","wind","solar"]` (unblocked) vs `["load"]` (blocked)

Everything else fixed: same KAN architecture ([2, width, 1]), same grid, same sparsification λ (L1=1.0, entropy=2.0), same pruning threshold (80%), same symbolic library (strict), same r² threshold (0.99), same seeds (1-5), same evaluation pipeline. Bootstrap is paired across same seeds.

### S3 Framing Contingency
- **Case 3 SUCCESS + Case 4 SUCCESS**: S3 is "one constructive solution among possible structural interventions"
- **Case 3 SUCCESS + Case 4 NULL**: S3 is "the necessary constructive workaround when blocking alone cannot overcome multi-level lag dominance"
- **Case 3 NULL**: S3 becomes the main practical contribution; mechanism claim weakened to observational only

## Four-Act Experimental Structure

### Act 1 — Accuracy Baseline [COMPLETE]
- KAN teacher on delta_net_load_h6: RMSE=1413.51, skill=0.453
- Matched MLP: RMSE=1474.38, skill=0.430 (paired t-test p=0.0005)
- PySR: RMSE≈2070, skill≈0.20
- Persistence: RMSE=2585.66, skill=0.0
- **Presentation**: One table, minimal narrative space.

### Act 2 — Problem Discovery: Formula Collapse [COMPLETE]
- 9 symbolic configurations (3 libraries × 3 r² thresholds) on canonical teacher
- ALL collapse to load-only: `0.0007*load - 3.0`
- VER(wind_speed) = 0/9, VER(GHI) = 0/9, edge_count(any_physical) = 0
- **Presentation**: One table + one formula rendering.

### Act 3 — Mechanism Test: Shortcut Competition [CORE — NEW EXPERIMENTS]

**Case 1: Solar — Positive Control** [COMPLETE]
- Focused solar teacher on delta_solar_h{72,144,576}
- GHI VER=3/3, FAR=3/3, edge_count(GHI) consistently > 0
- Interpretation: Strong physical signal survives even with lag competition

**Case 2: Wind — Boundary Case** [COMPLETE]
- Focused wind teacher across horizons h=6/72/144/288/576
- Non-monotonic VER: edge_count(wind)=11,0,9,0,0
- Interpretation: Identifiability depends on horizon-specific signal-to-lag ratio

**Case 3: Blocked-Lag Intervention on Focused Tasks** [NEW — 5 seeds]
- Focused wind teacher: `lag_series=["load"]` (block wind_lag_*)
- Focused solar teacher: `lag_series=["load"]` (block solar_lag_*)
- Measure: ΔVER(wind_speed), ΔVER(GHI), Δedge_count, with bootstrap 95% CI (paired)
- Prediction: ΔVER(wind) >> 0, ΔVER(GHI) ≈ 0
- Cost: ~10 Modal runs

**Case 4: Blocked-Lag Intervention on Direct Task** [NEW — 5 seeds]
- Direct delta_net_load_h6 teacher: `lag_series=["load"]` (block wind_lag_*, solar_lag_*)
- All meteorological features retained
- Measure: ΔVER(any_physical) relative to Act 2 baseline of 0/9
- Prediction: Partial recovery — some physical variables enter, but load_lag still dominates
- Closes the loop: mechanism tested on the original task, not just focused proxies
- Cost: ~5 Modal runs

### Act 4 — Constructive Solution: S3 Decomposition [80% COMPLETE → POLISH]

**Exact specification**:

| Sub-task | Target | Key physical variable | Input features |
|----------|--------|----------------------|----------------|
| Load | delta_load_h6 | temp_2m_c | temp_2m_c, cdd_18c, hdd_18c, load_lag_{12,24,48}, hour_sin/cos, dow_sin/cos |
| Wind | delta_wind_h6 | wind_speed_10m_m_s | wind_speed_10m_m_s, wind_speed_cubed, wind_speed_hub_est, wind_lag_{12,24,48}, hour_sin/cos |
| Solar | delta_solar_h6 | ghi_w_m2 | ghi_w_m2, ghi_day_w_m2, solar_altitude, is_night, solar_lag_{12,24,48}, hour_sin/cos |

**Combination rule**: Fixed additive (no learned weights):
```
delta_net_load_composite = delta_load_pred - delta_wind_pred - delta_solar_pred
```

**"Preserves" definition**: VER(target_physical_var) ≥ 3/5 seeds per sub-task.

**Evaluation**: Composite skill on absolute test set vs persistence.

**Remaining work**: LaTeX rendering of 3 sub-formulas, composite metrics, VER/FAR per sub-task.

**Presentation**: One compact section, one table, one composite figure.

## Training Details

- Architecture: KAN [2, hidden_width, 1], grid=3-5, k=3
- Schedule: warmup 200 → sparsify 800 (λ_L1=1.0, λ_entropy=2.0) → prune (target 80%) → refine 200
- Data: ARPA-E PERFORM ERCOT, 5-min resolution, chronological split (60/20/20), 48-step gap
- Normalization: Z-score on train, applied to val/test
- Seeds: 3 for frozen evidence (B1-B4, B7), 5 for S2 key comparisons and S3 sub-tasks
- Bootstrap: Paired across same seeds, 10000 resamples, 95% percentile CI

## Failure Modes

| Mode | Detection | Mitigation | Status |
|------|-----------|------------|--------|
| Direct formula → load-only | VER=0 for all physical vars | Documented as Act 2 finding | Confirmed |
| S2 Case 3: ΔVER ≈ 0 | Bootstrap CI includes 0 | Report as "truly hard to symbolize" | To test |
| S2 Case 4: ΔVER ≈ 0 | Bootstrap CI includes 0 | Mechanism confirmed on focused (Case 3), S3 becomes necessary | To test |
| S2: model fails without lags | skill << 0 | Expected for short h; measure accuracy-identifiability tradeoff | To test |
| S3 composite skill < 0 | RMSE > persistence | Already verified positive | Confirmed |
| Solar h=288 extrapolation | 67% negative predictions | Documented as boundary failure | Confirmed |

## Thesis Chapter Structure

1. **Introduction**: Renewable penetration → need for interpretable forecasting → KAN opportunity → MCKAN reference
2. **Literature Review**: KAN (ICLR 2025, PRX 2025), symbolic regression (PySR), MCKAN, interpretable energy forecasting
3. **Data & Problem**: PERFORM dataset, net_load definition, delta targets, feature engineering, horizon design
4. **Method**: KAN pipeline, identifiability diagnostics (VER/FAR/edge_count), blocking protocol with control specification, S3 decomposition specification
5. **Experiments**:
   - 5.1 Accuracy baseline (Act 1) → Table 1
   - 5.2 Formula collapse (Act 2) → Table 2 + formula rendering
   - 5.3 Solar/Wind identifiability (Cases 1-2) → Tables 3-4
   - 5.4 Blocked-lag intervention (Cases 3-4) → **Table 5 + ΔVER figure** [CENTERPIECE]
   - 5.5 S3 structured decomposition (Act 4) → Table 6 + composite formula [SECONDARY]
6. **Discussion**: Shortcut competition mechanism, accuracy-identifiability tradeoff, multi-level lag dominance, limitations (leakage, seed count, single dataset)
7. **Conclusion**: Contributions, future work (PIKAN constraints, more datasets, formal identifiability theory)

**Appendix**: Multi-horizon identifiability landscape, S0 safe function implementation details, seasonal/robustness stratified analysis, complete formula renderings, boundary failure (solar h=288)

## MCKAN Reference Alignment

| MCKAN Contribution | Our Corresponding Element |
|-------------------|--------------------------|
| Multi-step forecasting (15-45min) | Multi-horizon delta targets (h=6,12,24) |
| Pearson correlation feature selection | VER/FAR-based identifiability diagnostics |
| Wind/solar sub-task structure | S3 structured decomposition |
| Module ablation | S2 autoregressive blocking ablation |
| Extreme weather stability | Stratified analysis (appendix) |

## Compute & Timeline

| Phase | What | Runs | GPU-hours | Human-hours |
|-------|------|------|-----------|-------------|
| M0 | S3 Polish (post-processing) | 0 | 0 | 2h |
| M1 | S2 Blocking: focused tasks (5 seeds × 2) | 10 | 5-8h | 2h |
| M1b | S2 Blocking: direct task (5 seeds × 1) | 5 | 3-5h | 1h |
| M2 | Analysis (ΔVER, bootstrap CI, figures) | 0 | 0 | 4h |
| M3 | Paper Writing (chapters 1-7) | 0 | 0 | 40h+ |

**Total new GPU-hours**: ~8-13h on Modal
**Total new runs**: ~15
**Critical path**: M0 → M1+M1b (parallel) → M2 → M3
