# Research Proposal v2: Symbolic Identifiability of Physical Variables in KAN-Based Net Load Forecasting

> Enhanced version building on v1 (score 8.5/10). Focus: stronger causal evidence, new metrics, additional experiments.

## Problem Anchor

- **Bottom-line problem**: Extract physically meaningful, human-readable mathematical formulas from high-accuracy KAN models for net load forecasting. The key technical barrier: autoregressive dominance causes physical meteorological variables to be pruned away during sparsification, collapsing formulas to load-only expressions.

- **Must-solve bottleneck**: The transfer gap (KAN skill=0.453 → symbolic formula skill=0.076) is unacceptable, AND the formula loses all physical variables. We must understand WHY variables are lost, provide CAUSAL evidence for the mechanism, and demonstrate constructive solutions.

- **Non-goals**: New architecture, SOTA accuracy, deployable system, dataset replacement, strict leak-free guarantee.

- **Constraints**: Graduation thesis deadline (~4 weeks); 247+ runs already complete; Modal cloud GPU; must reference MCKAN (Chen et al., 2025); existing pykan + Phase3 symbolic pipeline.

- **Success condition**: A thesis demonstrating (1) KAN+symbolic works for net load; (2) systematic + CAUSAL evidence for WHY physical variables enter/exit formulas; (3) quantitative identifiability metrics with competition analysis; (4) S3 decomposition as constructive solution; (5) honest failure/boundary documentation.

## Technical Gap & Positioning

### Against closest work

| Work | What they do | What they DON'T do (our gap) |
|------|-------------|------------------------------|
| KAN original (Liu et al., 2024, ICLR 2025) | Symbolic regression on synthetic/physics data | Don't study autoregressive dominance or real-world time series identifiability |
| KAN Meets Science (PRX 2025) | Feature identification, modular structures, symbolic formulas | Don't address feature competition in multi-variate forecasting with autoregressive shortcuts |
| KAN-SR for energy (arXiv 2504.03913) | KAN symbolic regression for EHD/energy applications | Focus on clean physics problems; don't face the substitution problem in time series |
| MCKAN (Chen et al., 2025) | Multi-scale convolutional KAN for wind/solar | Pure accuracy focus; no symbolic extraction or identifiability analysis |
| PySR (Cranmer, 2023) | GP-based symbolic regression | Doesn't leverage KAN's structured sparsification; no identifiability analysis |
| Micro-step SR (Springer 2025) | GP symbolic regression for time series | Focus on accuracy via decomposition; don't study variable identifiability |

**Our unique contribution**: First systematic study of physical variable symbolic identifiability in real-world time series forecasting — specifically:
1. **Causal evidence** via autoregressive blocking that the substitution mechanism (not model failure) drives variable pruning
2. **Quantitative framework** (VER/FAR/TGR/CPI) for measuring identifiability and competition pressure
3. **Constructive solution** via structured task decomposition

### Why the problem is hard

In 5-minute resolution net load data, lag features (especially `load_lag_1`) explain >90% of short-term variance. Any sparsification algorithm rationally prunes weaker meteorological signals first. This is not a bug — it is an inherent property of high-frequency autoregressive time series. The challenge is structural, not parametric.

## Method Thesis

**One-sentence thesis**: We propose a KAN-teacher-guided symbolic extraction framework with autoregressive blocking ablation and structured task decomposition, providing the first causal and quantitative characterization of when and why physical variables survive or fail to survive the sparsification-to-symbolization pipeline in renewable net load forecasting.

**Why this is the smallest adequate intervention**: We do not invent new architectures. We use the existing KAN → prune → symbolic pipeline and add only: (a) controlled ablation experiments, (b) quantitative metrics, (c) task decomposition — all within existing infrastructure.

## Contribution Focus

- **Dominant contribution**: Systematic + CAUSAL characterization of physical variable symbolic identifiability, operationalized via four metrics:
  1. **Variable Entry Rate (VER)**: Fraction of seeds where variable retains active edges after pruning
  2. **Formula Appearance Rate (FAR)**: Fraction of seeds where variable appears in final SymPy expression
  3. **Transfer Gap Ratio (TGR)**: `RMSE_symbolic / RMSE_teacher` — measures information loss in symbolization
  4. **Competition Pressure Index (CPI)**: `CPI_v = 1 - VER_v(with_lags) / VER_v(without_lags)` — quantifies how much autoregressive shortcuts reduce a variable's identifiability

  Evidence chain:
  - Solar positive case: VER=3/3, FAR=3/3, low CPI (robust to lag competition)
  - Wind boundary case: non-monotonic VER across horizons, high CPI (easily absorbed by lags)
  - **S2 causal test**: Removing wind/solar lags forces raw physical variables into formulas → proves substitution mechanism

- **Supporting contribution**: S3 structured decomposition as a constructive methodology that guarantees physical variable presence by decomposing net_load into physically natural sub-tasks.

- **Explicit non-contributions**: No new architecture, no SOTA claims, no strict leak-free guarantee, no formal identifiability theory.

## Proposed Method

### System Overview (Four-Act Structure)

**Act 1 — Accuracy Baseline**: Train sparse KAN on `delta_net_load_h6`, demonstrating KAN > matched MLP > PySR > persistence.

**Act 2 — Problem Discovery**: Extract symbolic formula from KAN teacher → formula collapses to `0.0007*load - 3.0` (load-only). Systematic across 9 symbolic configurations. Physical variables are pruned to zero importance.

**Act 3 — Causal Diagnosis**:
- **S2 Autoregressive Blocking**: Remove wind/solar lag shortcuts → observe whether raw physical variables now survive pruning and enter formulas. If VER increases significantly when lags are removed, this provides CAUSAL evidence that substitution (not irrelevance) drives pruning.
- **Feature Group Ablation**: Solar focused teacher (GHI positive case) vs Wind focused teacher (boundary case)
- **Multi-Horizon Landscape**: Map VER/FAR across horizons for each variable type, revealing identifiability windows
- **Competition Pressure Analysis**: Compute CPI for each variable, showing solar has low CPI (robust) vs wind has high CPI (easily absorbed)

**Act 4 — Constructive Solution**:
- **S3 Decomposition**: Separate wind/solar/load sub-KANs → each sub-formula naturally contains its target physical variable → combine into interpretable composite
- **S0 Transfer Gap Reduction**: Safe function wrappers enable medium library → reduce TGR

### Operationalized Identifiability Metrics

```
Variable Entry Rate (VER_v):
  VER_v = (# seeds where variable v has active_edges > 0) / (total seeds)

Formula Appearance Rate (FAR_v):
  FAR_v = (# seeds where variable v appears in final SymPy expression) / (total seeds)

Transfer Gap Ratio (TGR):
  TGR = RMSE_symbolic / RMSE_teacher
  (TGR=1.0 means perfect transfer; TGR>>1 means severe degradation)

Competition Pressure Index (CPI_v):  [NEW]
  CPI_v = 1 - VER_v(with_lags) / VER_v(without_lags)
  (CPI=0 means lags don't affect identifiability; CPI=1 means lags completely suppress the variable)
  Note: If VER(without_lags) = 0, CPI is undefined (variable never identifiable)

Current values:
  TGR_direct = 2388.46 / 1413.51 = 1.69 (69% degradation, formula loses physics)
  Solar GHI: VER=3/3, FAR=3/3 (high identifiability)
  Wind speed: VER varies 0/3 to 3/3 by horizon (low, non-monotonic identifiability)
  CPI_GHI: to be measured (expected low — solar robust to lag competition)
  CPI_wind: to be measured (expected high — wind easily absorbed by lags)
```

### S2: Autoregressive Blocking Experiment [NEW — Key Innovation]

The strongest new experiment to strengthen the causal narrative:

1. **Setup**: For focused wind/solar teachers, train TWO variants:
   - **Variant A (baseline)**: Include all lag features (wind_lag_*, solar_lag_*, load_lag_*)
   - **Variant B (blocked)**: Remove wind_lag_* and solar_lag_* from `lag_series`, keep only load_lag_*

2. **Implementation**: Modify `lag_series` parameter in sweep config. Infrastructure already supports this — `derive_dataset.py` takes `lag_series` as a parameter list.

3. **Prediction**:
   - In Variant A, raw wind_speed has low VER (absorbed by wind_lag_*)
   - In Variant B, raw wind_speed VER increases substantially (forced to be the information source)
   - The VER difference between A and B IS the Competition Pressure Index (CPI)

4. **Why this is causal**: This is a controlled intervention. We remove the "shortcut" and observe whether the physical variable becomes identifiable. If yes, we have causal evidence that the substitution mechanism — not variable irrelevance — explains the pruning.

5. **Cost**: ~6-12 Modal runs (2 variants × 3 targets × 1-2 horizons). Low risk, existing infrastructure.

### S0: Transfer Gap Reduction (Existing Plan — Execute)

1. Apply safe numerical functions to Phase 3 symbolic evaluation:
   - `safe_exp(x) = exp(clip(x, -10, 10))`
   - `safe_div(a, b) = a / (b + 1e-8)`
   - Input clip to training-set [p1, p99] quantile range
2. Re-evaluate existing teacher's symbolic extraction with medium library
3. Expected outcome: Medium library becomes usable → more expressive formulas → TGR decreases
4. **Acceptance**: TGR < 1.5 (formula RMSE < 2120 on abs test)

### S3: Structured Decomposition (Existing Evidence — Polish)

1. Ensure all 3 sub-formulas render cleanly in LaTeX
2. Compute composite skill = 1 - RMSE_composite / RMSE_persistence
3. Verify physical variable presence: wind_speed in wind formula, GHI in solar formula, temp in load formula
4. Compute VER/FAR/TGR for each sub-task
5. Generate composite prediction time series plot

### Training Plan

All KAN training uses the existing pipeline:
- Warmup (200 steps) → Sparsify (800 steps, L1+entropy) → Prune (target 80% edge removal) → Refine (200 steps post-prune)
- 3 seeds minimum for all reported results
- Z-score normalization, chronological split with 48-step gap
- S2 blocking: change `lag_series` from `["load","wind","solar"]` to `["load"]` (one line change in sweep config)

### Failure Modes & Mitigations

| Failure Mode | Detection | Mitigation | Status |
|-------------|-----------|------------|--------|
| Direct formula collapses to load-only | VER=0 for all physical vars | Document as finding; use S3 instead | Confirmed |
| Medium library NaN/inf | formula_eval_test.json contains NaN | safe_exp/safe_div clipping (S0) | To implement |
| Solar h=288 extrapolation | 67% negative predictions | Document as boundary failure | Confirmed |
| Wind forced inclusion degrades skill | s3_comp_wind skill=-0.080 | Document as identifiability limit | Confirmed |
| S2 blocking: VER doesn't increase when lags removed | VER(blocked) ≈ VER(unblocked) | Would weaken causal claim; report honestly as "variable truly hard to identify" | To test |
| S2 blocking: model performance degrades severely | skill << 0 when lags removed | Expected for short horizons; measure the accuracy-identifiability tradeoff | To test |
| S3 composite skill negative | composite RMSE > persistence RMSE | Already verified positive | Confirmed positive |

## Claim-Driven Validation

### Claim 1: KAN symbolic extraction pipeline works for net load forecasting
- **Evidence**: KAN RMSE=1413.51, skill=0.453; MLP RMSE=1474.38, skill=0.430; PySR ~2070; paired t-test p=0.0005
- **Status**: COMPLETE, frozen

### Claim 2: Direct symbolic extraction suffers autoregressive collapse
- **Evidence**: 9 symbolic configs on canonical teacher → all produce load-only formulas; 11 direct S0 runs → all skill<0
- **Status**: COMPLETE, frozen

### Claim 3: Identifiability depends on task structure and feature competition, not information content
- **Evidence (observational)**: Solar VER=3/3 (positive) + Wind non-monotonic VER (boundary) — COMPLETE
- **Evidence (causal) [NEW]**: S2 autoregressive blocking → VER increases when lags removed → proves substitution mechanism — TO RUN
- **CPI metric [NEW]**: Quantifies competition pressure per variable — TO COMPUTE

### Claim 4: S3 structured decomposition guarantees physical variable presence
- **Evidence**: Sub-formulas contain wind_speed, GHI, temp respectively; composite skill positive
- **Status**: MOSTLY COMPLETE, needs polish

### Claim 5 (anti-claim): The gain is NOT from more parameters or longer training
- **Evidence**: Budget-matched MLP baseline; symbolic formula has fewer parameters than any NN
- **Status**: COMPLETE, frozen

## Thesis Chapter Structure (Enhanced)

1. **Introduction**: Renewable penetration → need for interpretable forecasting → KAN opportunity → MCKAN reference
2. **Literature Review**: Symbolic regression, KAN (ICLR 2025 + PRX 2025), interpretable load forecasting, MCKAN and related work
3. **Data & Problem**: PERFORM dataset, net_load definition, delta targets, horizon design, feature engineering
4. **Method**: KAN teacher pipeline, symbolic extraction, identifiability metrics (VER/FAR/TGR/CPI), autoregressive blocking protocol, S3 decomposition
5. **Experiments**:
   - 5.1 Accuracy: KAN vs MLP vs PySR vs persistence (main table + significance)
   - 5.2 Direct formula collapse (load-only evidence, 9 configs)
   - 5.3 Solar identifiability (positive case, horizon dynamics, VER/FAR/CPI)
   - 5.4 Wind identifiability (boundary case, non-monotonic horizon, VER/FAR/CPI)
   - **5.5 Autoregressive blocking ablation (S2) — causal evidence for substitution** [NEW]
   - 5.6 S3 structured decomposition (constructive solution)
   - 5.7 Transfer gap reduction (S0, safe functions)
   - 5.8 Multi-horizon identifiability landscape [NEW]
   - 5.9 Boundary failure (solar h=288)
6. **Discussion**: Feature competition mechanism, CPI analysis, implications for KAN-based interpretability, limitations
7. **Conclusion & Future Work**: Summary, contributions, future directions (PIKAN, clean pipeline, more datasets)

## MCKAN Reference Alignment

| MCKAN Contribution | Our Corresponding Element | Connection Type |
|-------------------|--------------------------|----------------|
| Multi-step forecasting (15-45min) | Multi-horizon delta targets (h=6,12,24,...) | Methodological parallel |
| Pearson correlation for feature selection | Feature group ablation + VER/FAR/CPI metrics | Strengthened, quantitative version |
| Min-Max scaling for stability | Z-score + safe_exp/safe_div (S0) | Practical alternative + improvement |
| Multi-scale convolution (MCKAN) | Multi-scale lags (12/24/48 steps) | Interpretable alternative |
| Wind/solar sub-task structure | S3 structured decomposition | Direct parallel |
| Module ablation (MCKAN/EAA/CQALA) | S0-S3 systematic ablation sweep | More systematic methodology |
| Extreme weather stability | Stratified robustness analysis (optional B8) | Lightweight extension |

## Compute & Timeline Estimate

| Phase | What | GPU-hours | Human-hours | Risk |
|-------|------|-----------|-------------|------|
| M0: B5 S3 Polish | R001-R004 (post-processing) | 0 | 2h | Low |
| M1: S0 Safe Functions | R005-R006 (code change) | 0 | 2h | Low |
| M2: S0 Sweep | R007-R008 (Modal runs) | 4-8h | 2h | Medium |
| **M2.5: S2 Blocking** | **6-12 new KAN runs + symbolic extraction** | **6-12h** | **3h** | **Medium** |
| M3: CPI + Landscape | Post-processing of S2 + existing data | 0 | 3h | Low |
| M4: Robustness (optional) | Stratified evaluation | 0 | 1h | Low |
| M5: Paper Writing | Chapters 1-7 | 0 | 40h+ | — |

**Total new GPU-hours**: ~10-20h on Modal
**Critical path**: M0 → M1 → M2 + M2.5 (parallel) → M3 → M5

## Experiment Handoff Inputs

- **Must-prove claims**: C1-C4 (C3 with causal S2 evidence)
- **Must-run ablations**: S2 autoregressive blocking (key new experiment)
- **Must-complete polish**: B5 S3 composite
- **Nice-to-have**: S0 transfer gap, B8 robustness
- **Critical metrics**: VER, FAR, TGR, CPI (all four)
- **Highest-risk assumption**: S2 blocking will show clear VER increase for wind
