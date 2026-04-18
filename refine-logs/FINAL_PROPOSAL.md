# Research Proposal: Symbolic Identifiability of Physical Variables in KAN-Based Net Load Forecasting

## Problem Anchor

- **Bottom-line problem**: Extract physically meaningful, human-readable mathematical formulas from high-accuracy KAN models for net load forecasting. The key technical barrier: autoregressive dominance causes physical meteorological variables to be pruned away during sparsification, collapsing formulas to load-only expressions.

- **Must-solve bottleneck**: The transfer gap (KAN skill=0.453 → symbolic formula skill=0.076) is unacceptable, AND the formula loses all physical variables. We must understand WHY variables are lost and provide a constructive solution.

- **Non-goals**: New architecture, SOTA accuracy, deployable system, dataset replacement.

- **Constraints**: Graduation thesis deadline; 247 runs already complete; Modal cloud GPU; must reference MCKAN (Chen et al., 2025).

- **Success condition**: A thesis demonstrating (1) KAN+symbolic works; (2) systematic evidence for WHY physical variables enter/exit formulas; (3) S3 decomposition as constructive solution; (4) honest failure mode documentation.

## Technical Gap & Positioning

### Against closest work

| Work | What they do | What they DON'T do (our gap) |
|------|-------------|------------------------------|
| KAN original (Liu et al., 2024) | Symbolic regression on synthetic/physics data | Don't study autoregressive dominance or real-world time series identifiability |
| KAN-SR framework (Bühler et al., 2025) | Guided symbolic regression framework | Don't address feature competition in multi-variate forecasting |
| KAN-SR for nuclear (Panczyk et al., 2025) | KAN symbolic regression in nuclear energy | Nuclear tasks have clear physics variables; don't face the autoregressive dominance problem |
| MCKAN (Chen et al., 2025) | Multi-scale convolutional KAN for wind/solar | Pure accuracy focus; no symbolic extraction or interpretability analysis |
| PySR (Cranmer, 2023) | GP-based symbolic regression | Doesn't leverage KAN's structured sparsification; no identifiability analysis |

**Our unique contribution**: First systematic study of physical variable symbolic identifiability in real-world time series forecasting — specifically, characterizing HOW feature competition, pruning trajectory, task structure, and prediction horizon jointly determine whether physical variables survive the KAN sparsification → symbolization pipeline.

### Why the problem is hard

In 5-minute resolution net load data, lag features (especially `load_lag_1`) explain >90% of short-term variance. Any sparsification algorithm rationally prunes weaker meteorological signals first. This is not a bug — it is an inherent property of high-frequency autoregressive time series. The challenge is structural, not parametric.

## Method Thesis

**One-sentence thesis**: We propose a KAN-teacher-guided symbolic extraction framework with structured task decomposition, and provide the first empirical characterization of when and why physical variables survive or fail to survive the sparsification-to-symbolization pipeline in renewable net load forecasting.

## Contribution Focus

- **Dominant contribution**: Systematic characterization of physical variable symbolic identifiability, operationalized via three metrics:
  1. **Variable Entry Rate (VER)**: Fraction of seeds where variable retains active edges after pruning
  2. **Formula Appearance Rate (FAR)**: Fraction of seeds where variable appears in final SymPy expression
  3. **Transfer Gap Ratio (TGR)**: `RMSE_symbolic / RMSE_teacher` — measures information loss in symbolization

  Evidence from symmetric solar (positive case: VER=3/3, FAR=3/3) and wind (boundary case: non-monotonic VER across horizons) establishes that identifiability depends on task structure and feature competition, not information content.

- **Supporting contribution**: S3 structured decomposition as a constructive methodology that guarantees physical variable presence by decomposing net_load into physically natural sub-tasks.

- **Explicit non-contributions**: No new architecture, no SOTA claims, no strict leak-free guarantee.

## Proposed Method

### System Overview (Three-Act Structure)

**Act 1 — Accuracy Baseline**: Train sparse KAN on `delta_net_load_h6`, demonstrating KAN > matched MLP > persistence.

**Act 2 — Problem Discovery**: Extract symbolic formula from KAN teacher → formula collapses to `0.0007*load - 3.0` (load-only). This is systematic across 9 symbolic configurations. Physical variables are pruned to zero importance.

**Act 3 — Analysis & Solution**:
- **Diagnosis**: Feature group ablation on solar/wind sub-tasks reveals variable-specific identifiability patterns
- **Solar positive case**: GHI enters stably (3/3 seeds) in focused teacher, with horizon-dependent competition dynamics
- **Wind boundary case**: Raw wind_speed shows non-monotonic identifiability — peaks at medium horizon (h=144), absent at short (h=72) and long (h=576)
- **S3 constructive solution**: Decompose into wind/solar/load sub-KANs → each formula contains its target physical variable → combine into interpretable composite

### Operationalized Identifiability Metrics

```
Variable Entry Rate (VER_v):
  VER_v = (# seeds where variable v has active_edges > 0) / (total seeds)

Formula Appearance Rate (FAR_v):
  FAR_v = (# seeds where variable v appears in final SymPy expression) / (total seeds)

Transfer Gap Ratio (TGR):
  TGR = RMSE_symbolic / RMSE_teacher
  (TGR=1.0 means perfect transfer; TGR>>1 means severe degradation)

Current values:
  TGR_direct = 2388.46 / 1413.51 = 1.69 (39% degradation, formula loses physics)
  Solar GHI: VER=3/3, FAR=3/3 (high identifiability)
  Wind speed: VER varies 0/3 to 3/3 by horizon (low, non-monotonic identifiability)
```

### S0: Transfer Gap Reduction (New Experiment — Low Cost)

The single targeted new experiment to strengthen the narrative:

1. Apply safe numerical functions to Phase 3 symbolic evaluation:
   - `safe_exp(x) = exp(clip(x, -10, 10))`
   - `safe_div(a, b) = a / (b + 1e-8)`
   - Input clip to training-set [p1, p99] quantile range
2. Re-evaluate existing teacher's symbolic extraction with medium library (previously unstable due to NaN/inf)
3. Expected outcome: Medium library becomes usable → more expressive formulas → TGR decreases

**Acceptance criteria**: TGR < 1.5 (formula RMSE < 2120 on abs test)

### S3: Structured Decomposition (Existing Evidence — Polish)

Already executed. Polish by:
1. Ensure all 3 sub-formulas render cleanly in LaTeX
2. Compute composite skill = 1 - RMSE_composite / RMSE_persistence
3. Verify physical variable presence: wind_speed in wind formula, GHI in solar formula, temp in load formula
4. Generate composite prediction time series plot

### Training Plan

All KAN training uses the existing pipeline:
- Warmup (50 epochs, no regularization) → Sparsify (L1+entropy, progressive lambda) → Prune (target 80% edge removal) → Refine (20 epochs post-prune)
- 3 seeds minimum for all reported results
- Z-score normalization, chronological split with 48-step gap

### Failure Modes & Mitigations

| Failure Mode | Detection | Mitigation | Status |
|-------------|-----------|------------|--------|
| Direct formula collapses to load-only | VER=0 for all physical vars | Document as finding; use S3 instead | Confirmed |
| Medium library NaN/inf | formula_eval_test.json contains NaN | safe_exp/safe_div clipping | To implement (S0) |
| Solar h=288 extrapolation | 67% negative predictions | Document as boundary failure | Confirmed |
| Wind forced inclusion degrades skill | s3_comp_wind skill=-0.080 | Document as identifiability limit | Confirmed |
| S3 composite skill negative | composite RMSE > persistence RMSE | Already verified positive | Confirmed positive |

## Claim-Driven Validation

### Claim 1: KAN symbolic extraction pipeline works for net load forecasting
- **Evidence**: KAN RMSE=1413.51, skill=0.453; MLP RMSE=1474.38, skill=0.430; paired t-test p=0.0005
- **Status**: COMPLETE, frozen

### Claim 2: Direct symbolic extraction suffers autoregressive collapse
- **Evidence**: 9 symbolic configs on canonical teacher → all produce load-only formulas; 11 direct S0 runs → all skill<0
- **Status**: COMPLETE, frozen

### Claim 3: Identifiability depends on task structure, not information content
- **Evidence**:
  - Solar GHI: VER=3/3, FAR=3/3 in focused teacher (positive case)
  - Wind: non-monotonic VER across horizons h=6/72/144/288/576 (boundary case)
  - Feature group ablation: lags-only vs meteo-only vs both across horizons
- **Status**: COMPLETE, frozen

### Claim 4: S3 structured decomposition guarantees physical variable presence
- **Evidence**: Sub-formulas contain wind_speed, GHI, temp respectively; composite skill positive
- **Status**: MOSTLY COMPLETE, needs polish

## MCKAN Reference Alignment

| MCKAN Contribution | Our Corresponding Element | Connection Type |
|-------------------|--------------------------|----------------|
| Multi-step forecasting (15-45min) | Multi-horizon delta targets (h=6,12,24,...) | Methodological parallel |
| Pearson correlation for feature selection | Feature group ablation + VER/FAR metrics | Strengthened version |
| Min-Max scaling for stability | Z-score + safe_exp/safe_div (S0) | Practical alternative |
| Multi-scale convolution (MCKAN) | Multi-scale lags (12/24/48 steps) | Interpretable alternative |
| Wind/solar sub-task structure | S3 structured decomposition | Direct parallel |
| Module ablation (MCKAN/EAA/CQALA) | S0-S3 ablation sweep | Systematic methodology |

## Thesis Chapter Structure

1. **Introduction**: Renewable penetration → need for interpretable forecasting → KAN opportunity → MCKAN reference
2. **Literature Review**: Symbolic regression, KAN, interpretable load forecasting, MCKAN and related work
3. **Data & Problem**: PERFORM dataset, net_load definition, delta targets, horizon design, feature engineering
4. **Method**: KAN teacher pipeline, symbolic extraction, identifiability metrics (VER/FAR/TGR), S3 decomposition
5. **Experiments**:
   - 5.1 Accuracy: KAN vs MLP vs persistence (main table + significance)
   - 5.2 Direct formula collapse (load-only evidence)
   - 5.3 Solar identifiability (positive case, horizon dynamics)
   - 5.4 Wind identifiability (boundary case, non-monotonic horizon)
   - 5.5 S3 structured decomposition (constructive solution)
   - 5.6 Boundary failure (solar h=288)
   - 5.7 Complexity-accuracy Pareto
6. **Discussion**: Feature competition mechanism, implications for KAN-based interpretability, limitations (leakage, path dependence)
7. **Conclusion & Future Work**: Summary, contributions, future directions (PIKAN, clean pipeline, more datasets)

## Compute & Timeline

- **New computation needed**: ~10-20 Modal runs for S0 (safe functions on medium library)
- **Paper writing**: Primary remaining effort — all evidence frozen, chapter structure defined
- **Estimated timeline**:
  - Week 1: S0 safe function experiments + S3 polish
  - Week 2-3: Thesis draft (chapters 1-5)
  - Week 4: Discussion, conclusion, formatting, defense prep
