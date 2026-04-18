# Experiment Plan

**Problem**: KAN symbolic extraction loses physical variables due to autoregressive dominance in net load forecasting. We need to characterize when/why variables survive the sparsification→symbolization pipeline and provide a constructive solution.

**Method Thesis**: KAN-teacher-guided symbolic extraction with structured task decomposition; first empirical characterization of physical variable symbolic identifiability in renewable net load forecasting.

**Date**: 2026-03-21

**Project Phase**: 90% complete — most evidence frozen, focus on remaining gaps + paper writing.

---

## Claim Map

| Claim | Why It Matters | Minimum Convincing Evidence | Linked Blocks | Status |
|-------|----------------|-----------------------------|---------------|--------|
| C1: KAN > MLP > persistence on net load | Establishes method validity | Main table + paired significance p<0.05 | B1 | COMPLETE |
| C2: Direct symbolic extraction collapses to load-only | Motivates the identifiability investigation | 9 symbolic configs all load-only + 11 direct S0 runs all skill<0 | B2 | COMPLETE |
| C3: Identifiability depends on task structure, not information content | Dominant contribution | Solar VER=3/3 (positive) + Wind non-monotonic VER (boundary) + feature group ablation | B3, B4 | COMPLETE |
| C4: S3 structured decomposition guarantees physical variable presence | Constructive solution | Sub-formulas contain target physical vars + composite skill positive | B5 | 80% COMPLETE |
| C5 (anti-claim): The gain is NOT from more parameters or longer training | Rules out trivial explanation | Budget-matched MLP baseline; symbolic formula has fewer parameters than any NN | B1 | COMPLETE |

## Paper Storyline

**Main paper must prove:**
- C1 (accuracy baseline) → Table 1
- C2 (direct collapse) → Table 2 + formula rendering
- C3 (identifiability characterization) → Tables 3-4 (solar/wind ablation) + horizon figure
- C4 (S3 decomposition) → Table 5 + composite formula rendering
- Boundary failure → solar h=288 figure

**Appendix can support:**
- Full multi-horizon sweep data
- PySR comparison details
- Stratified error tables (season, day/night, volatility)
- All formula LaTeX renderings
- Reproducibility map (run_id → command → artifact)

**Experiments intentionally cut:**
- S1×S2 multi-horizon + forced feature ablation (evidence already sufficient from existing h=6/72/144/576 runs)
- New KAN teacher training (current teachers adequate)
- PIKAN physics constraints (future work)
- Clean pipeline re-run (documented as limitation, not fixable in timeline)
- Additional baselines beyond MLP + persistence + PySR

---

## Experiment Blocks

### Block 1: Accuracy Baseline [COMPLETE]
- **Claim tested**: C1 (KAN > MLP > persistence) + C5 (not from more parameters)
- **Why this block exists**: Establishes method works before investigating interpretability
- **Dataset / split / task**: ARPA-E PERFORM ERCOT, chronological split (48-step gap), delta_net_load_h6 → reconstructed to abs(test)
- **Compared systems**: KAN teacher (skill=0.453), matched MLP (skill=0.430), persistence (skill=0.0)
- **Metrics**: RMSE, R², skill, paired t-test (p=0.0005), bootstrap 95% CI
- **Setup details**: KAN [2,5,1] grid=3, warmup 50 → sparsify → prune 80% → refine; MLP matched features + budget
- **Success criterion**: KAN skill > 0.4, statistically significant vs MLP ✓
- **Failure interpretation**: N/A — already achieved
- **Table / figure target**: Table 1 (main comparison), Pareto figure
- **Priority**: MUST-RUN ✓ COMPLETE
- **Evidence**: `doc/paper_assets/paper_delivery_20260306/comparison_table.csv`, `paired_significance_main_20260309.csv`

### Block 2: Direct Symbolic Collapse [COMPLETE]
- **Claim tested**: C2 (direct extraction collapses to load-only)
- **Why this block exists**: Establishes the core problem — motivates entire identifiability investigation
- **Dataset / split / task**: Same as B1
- **Compared systems**: 9 symbolic configs (strict/medium/poly4 × r2={0.98,0.99,0.995}) on canonical teacher + 11 direct S0 cloud runs
- **Metrics**: Formula content (which variables appear), VER, FAR, TGR, skill
- **Setup details**: Phase 3 symbolic extraction from `paperref_20260306_121725_v2__s1_delta_net_load_h6`
- **Success criterion**: ALL configs produce load-only or skill<0 formulas ✓
- **Failure interpretation**: If any config produces positive-skill formula with physical variables → direct route works, S3 unnecessary
- **Table / figure target**: Table 2 (symbolic sweep results), formula rendering figure
- **Priority**: MUST-RUN ✓ COMPLETE
- **Evidence**: `doc/paper_delivery_closure_20260306.md` Section 8, `direct_teacher_cloud_check_20260309.csv`

### Block 3: Solar Identifiability — Positive Case [COMPLETE]
- **Claim tested**: C3 (identifiability depends on task structure)
- **Why this block exists**: Solar serves as the positive control — GHI reliably enters formulas in focused teachers
- **Dataset / split / task**: delta_solar_h{72,144,576}, feature group ablation (lags-only / meteo-only / both)
- **Compared systems**: 9 solar ablation runs across 3 horizons × 3 feature groups
- **Metrics**: VER(GHI), FAR(GHI), abs(test) skill, ghi_edges count, active edge distribution
- **Setup details**: Focused solar KAN teachers with restricted feature sets
- **Success criterion**: GHI VER=3/3 in at least one horizon+config ✓; competition dynamics visible (h=144 both worse) ✓
- **Failure interpretation**: N/A — already confirmed
- **Table / figure target**: Table 3 (solar ablation), solar horizon figure
- **Priority**: MUST-RUN ✓ COMPLETE
- **Evidence**: `doc/solar_ablation_summary_20260304.csv`, `solar_stratified_error_20260309.csv`

### Block 4: Wind Identifiability — Boundary Case [COMPLETE]
- **Claim tested**: C3 (identifiability depends on task structure) — wind as the hard case
- **Why this block exists**: Wind is the critical boundary — non-monotonic identifiability reveals feature competition mechanism
- **Dataset / split / task**: delta_wind_h{6,72,144,288,576}, feature group ablation
- **Compared systems**: Wind ablation runs across horizons, exp_longh_wind_delta_h* series
- **Metrics**: VER(wind_speed), FAR(wind_speed), abs(test) skill, wind_speed_edges count
- **Setup details**: Focused wind KAN teachers; long-horizon series
- **Success criterion**: Non-monotonic pattern confirmed (peaks at medium horizon) ✓; wind_speed_edges=9 at h=144 ✓
- **Failure interpretation**: N/A — already confirmed
- **Table / figure target**: Table 4 (wind ablation + horizon), wind horizon figure
- **Priority**: MUST-RUN ✓ COMPLETE
- **Evidence**: `doc/paper_assets/paper_delivery_20260306/wind_ablation_summary_20260306.csv`, system audit Section 8

### Block 5: S3 Structured Decomposition [80% COMPLETE — NEEDS POLISH]
- **Claim tested**: C4 (S3 guarantees physical variable presence)
- **Why this block exists**: Constructive solution — shows decomposition solves the identifiability problem
- **Dataset / split / task**: delta_{wind,solar,load}_h6 sub-tasks → combine to net_load
- **Compared systems**: S3 composite vs direct single-formula extraction vs KAN teacher
- **Metrics**: Physical variable presence (boolean per sub-formula), composite RMSE, composite skill, TGR per sub-task
- **Setup details**: 3 independent sub-KANs, each with focused features; combine via `net_load = load - wind - solar`
- **Success criterion**: Each sub-formula contains its target physical variable; composite skill > 0
- **Failure interpretation**: If composite skill < 0 → decomposition doesn't work as a solution (mitigate by adjusting sub-model features)
- **Table / figure target**: Table 5 (S3 results), composite formula rendering, composite time series plot
- **Priority**: MUST-RUN
- **Remaining work**:
  1. **R001**: Verify 3 sub-formula LaTeX renderings are clean and correct
  2. **R002**: Compute composite prediction → reconstruct abs → compute skill vs persistence
  3. **R003**: Generate composite time series plot (actual vs predicted, highlighting wind/solar/load contributions)
  4. **R004**: Compute VER/FAR/TGR for each sub-task → fill S3 row in identifiability summary table

### Block 6: S0 Transfer Gap Reduction [NEW — TARGETED]
- **Claim tested**: Supports C2 and C4 — shows transfer gap can be partially reduced with better symbolic evaluation
- **Why this block exists**: Reduces the "teacher-to-formula" gap, making the entire pipeline more credible; also tests whether medium library (previously NaN) becomes usable
- **Dataset / split / task**: Same canonical teacher as B2, same test set
- **Compared systems**: (a) Strict lib with existing r2 thresholds (baseline=current); (b) Strict lib + safe functions; (c) Medium lib + safe functions; (d) Medium lib + safe functions + quantile clipping
- **Metrics**: TGR (target: <1.5), formula RMSE (target: <2120), NaN/inf count (target: 0), physical variable presence
- **Setup details**:
  - Add safe wrappers to `src/kan_sr/symbolic.py`:
    - `safe_exp(x) = exp(clip(x, -10, 10))`
    - `safe_div(a, b) = a / (b + 1e-8)`
    - Input quantile clip to [p1, p99] of training set
  - Re-run Phase 3 symbolic extraction on existing teacher checkpoint
  - 3 r2_thresholds × 2 libraries × safe_on/off = 12 runs (but can skip unsafe medium = 9 runs)
- **Success criterion**: At least one config achieves TGR < 1.5 with no NaN; bonus if physical variable appears
- **Failure interpretation**: If all configs still TGR > 1.5 → transfer gap is fundamental to the task structure (still publishable as negative result strengthening C2); document and move on
- **Table / figure target**: Table 6 (S0 sweep results), transfer gap comparison figure
- **Priority**: NICE-TO-HAVE (strengthens narrative but not blocking)
- **Remaining work**:
  1. **R005**: Implement safe_exp/safe_div wrappers in `src/kan_sr/symbolic.py`
  2. **R006**: Add quantile clipping to Phase 3 evaluation path
  3. **R007**: Run 9-config S0 sweep on Modal (medium lib + safe functions + 3 r2 thresholds)
  4. **R008**: Evaluate results: reconstruct abs, compute TGR, check NaN, check variable presence

### Block 7: Boundary Failure Documentation [COMPLETE]
- **Claim tested**: Supports C3 — documents where the method fails (solar h=288)
- **Why this block exists**: Honest boundary documentation strengthens paper credibility
- **Dataset / split / task**: delta_solar_h288
- **Compared systems**: solar h=288 model vs persistence vs clip mitigation
- **Metrics**: abs(test) RMSE, skill, negative prediction rate, quantile distribution
- **Setup details**: Existing run `2026-03-04_101610_37271ac2`
- **Success criterion**: Failure is well-documented and quantified ✓
- **Table / figure target**: Figure (solar h=288 boundary), paragraph in discussion
- **Priority**: MUST-RUN ✓ COMPLETE
- **Evidence**: `solar_h288_boundary_20260306.json`, `solar_h288_boundary_20260306.png`

### Block 8: Extreme Weather / Volatility Robustness [OPTIONAL — LIGHTWEIGHT]
- **Claim tested**: Supports C3/C4 — tests whether S3 composite is more robust under extreme conditions
- **Why this block exists**: Aligns with MCKAN reference paper's discussion of extreme weather stability; adds a "practical insight" layer
- **Dataset / split / task**: Existing predictions, sliced by temperature quantile (extreme cold/hot) and net_load volatility quantile
- **Compared systems**: KAN teacher vs S3 composite vs persistence on high-volatility slices
- **Metrics**: RMSE per slice, skill per slice, relative performance change
- **Setup details**: No new training — purely evaluation. Use `scripts/stratified_error_analysis.py` on existing predictions.
  - Temperature slices: p10 (cold), p50 (normal), p90 (hot)
  - Volatility slices: bottom 33%, middle 33%, top 33% by |delta_net_load|
- **Success criterion**: S3 composite shows less degradation in extreme slices than direct model
- **Failure interpretation**: If S3 is equally or more fragile → not a strong argument; report honestly or cut
- **Table / figure target**: Appendix table (stratified comparison)
- **Priority**: NICE-TO-HAVE
- **Remaining work**:
  1. **R009**: Run stratified analysis on S3 composite predictions (if composite predictions not yet generated, depends on R002)
  2. **R010**: Generate comparison table: KAN vs S3 composite across volatility/temperature slices

---

## Run Order and Milestones

| Milestone | Goal | Runs | Decision Gate | Cost | Risk |
|-----------|------|------|---------------|------|------|
| M0: S3 Polish | Complete Block 5 evidence | R001-R004 | All 3 sub-formulas clean + composite skill > 0 | ~1h local | Low — runs already exist, just post-processing |
| M1: S0 Implementation | Add safe functions to symbolic eval | R005-R006 | Code compiles, unit test passes on toy example | ~2h local | Low — localized code change |
| M2: S0 Sweep | Run S0 medium lib experiments | R007-R008 | At least one config NaN-free; record TGR | ~4h Modal GPU | Medium — medium lib may still be flaky |
| M3: Robustness | Extreme weather/volatility analysis | R009-R010 | Comparison table generated | ~1h local | Low — no training needed |
| M4: Paper Writing | Draft all thesis chapters | — | All tables/figures finalized | — | — |

**Decision gates:**
- After M0: If S3 composite skill < 0 → investigate sub-model quality before proceeding
- After M2: If all S0 configs TGR > 1.5 → stop S0, document as negative result, proceed to paper
- After M3: If robustness results are uninteresting → cut from paper, keep as appendix or drop entirely

---

## Compute and Data Budget

- **Total new GPU-hours**: ~4-8h on Modal (S0 sweep only; everything else is local post-processing)
- **Data preparation**: None (all data already processed and cached)
- **Human evaluation**: Formula inspection (30min), figure quality check (30min)
- **Biggest bottleneck**: Paper writing, not computation

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| S0 medium lib still produces NaN even with safe functions | Medium | Low (narrative already works without S0) | Document as additional negative evidence; proceed with strict-only results |
| S3 composite skill turns out negative when properly computed | Low | High (blocks C4) | Check sub-model quality; adjust combination weights; worst case = honest negative result |
| Pre-split interpolation leakage questioned by thesis committee | Medium | Medium | Document honestly in limitations; show qualitative patterns are stable across feature groups |
| Missing local dependencies (sympy/kan/pytest) block verification | Medium | Medium | Install dependencies or verify on Modal; use existing artifacts if local install fails |
| Timeline pressure delays paper writing | High | High | Prioritize paper writing over nice-to-have experiments (M2, M3) |

---

## Final Checklist

- [x] Main paper tables are covered (Tables 1-5 from Blocks 1-5)
- [x] Novelty is isolated (C3: identifiability characterization, not accuracy)
- [x] Simplicity is defended (no new architecture, minimal new code)
- [x] Frontier contribution is explicitly not claimed (graduation thesis context)
- [x] Nice-to-have runs (S0 sweep, robustness) are separated from must-run (S3 polish)
- [x] Anti-claim addressed (C5: budget-matched MLP rules out parameter advantage)
- [x] Boundary failure documented (solar h=288)
- [x] MCKAN reference alignment table prepared
- [ ] S3 composite evidence finalized (Block 5 — first priority)
- [ ] S0 safe functions implemented (Block 6 — second priority)
- [ ] Paper draft started (M4 — highest priority after M0)
