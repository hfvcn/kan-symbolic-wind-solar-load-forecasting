# Research Proposal: Symbolic Identifiability of Physical Variables in KAN-Based Net Load Forecasting

## Problem Anchor

- **Bottom-line problem**: In short-term net load forecasting with high renewable penetration, we need prediction models that are both accurate AND physically interpretable. The specific technical problem is: when we extract symbolic formulas from high-accuracy KAN teachers, key physical variables (wind speed, GHI, temperature) often get pruned away, replaced by autoregressive lags. We need to understand when and why physical variables can (or cannot) survive the sparsification-to-symbolization pipeline, and how to ensure they appear in the final formula.

- **Must-solve bottleneck**: The "transfer gap" between KAN teacher accuracy (skill=0.453) and extracted symbolic formula accuracy (skill=0.076) is unacceptably large, AND the formula collapses to load-only expressions, losing all physical interpretability. The real bottleneck is not prediction accuracy — it is the symbolic extraction pipeline's inability to preserve physical variable structure while maintaining acceptable accuracy.

- **Non-goals**: (1) Proposing a new neural architecture for load forecasting. (2) Achieving state-of-the-art prediction accuracy. (3) Building a deployable real-time forecasting system. (4) Replacing the entire data pipeline or switching datasets. (5) True teacher-student distillation training.

- **Constraints**: (1) Graduation thesis (毕业设计) with deadline — must prioritize deliverability over novelty. (2) 247 experiments already complete with frozen paper assets — build on existing evidence, not restart. (3) Modal cloud GPU for computation. (4) Must reference the MCKAN paper (Chen et al., 2025) on multi-step wind/solar forecasting. (5) Current pipeline has pre-split interpolation leakage (documented, not fixable within timeline).

- **Success condition**: A thesis that (1) demonstrates KAN+symbolic extraction pipeline works for net load forecasting; (2) explains WHY physical variables enter or exit formulas through systematic ablation evidence; (3) provides S3 structured decomposition as a viable path to physically interpretable formulas; (4) honestly documents limitations and failure modes as boundary contributions.

## Technical Gap

### Where current methods fail

The standard approach to interpretable forecasting is either: (a) use inherently interpretable models (linear regression, decision trees) that sacrifice accuracy, or (b) apply post-hoc explanation methods (SHAP, attention weights) that don't produce auditable mathematical formulas. KAN-based symbolic regression offers a middle path — train a high-accuracy KAN, then extract symbolic formulas from the learned spline activations.

However, our 247-run experimental campaign reveals a fundamental structural problem: **autoregressive dominance**. In 5-minute resolution net load data, recent lags (especially load lags) are so predictive that sparse KAN training prunes away physical meteorological inputs (wind speed, GHI, temperature) before they reach the symbolic extraction stage. This is not a training failure — it is a rational response by the sparsification algorithm to the signal structure of the data.

### Why naive fixes are insufficient

- **Just training longer/harder**: The pruning outcome is structurally determined by signal competition, not training duration.
- **Forcing variables into the model**: We tried this via `s3_comp_wind_delta_h6` — wind variables enter the formula (3/3 consistency) but skill drops to -0.080, meaning forced inclusion destroys generalization.
- **Different symbolic libraries**: We swept strict/medium/poly4 with multiple r2_thresholds — all 9 combinations collapse to load-only formulas on the direct net_load teacher.
- **Longer prediction horizons**: Helps somewhat (wind identifiability peaks at medium horizons) but introduces new failure modes (solar h=288 extrapolation collapse).

### The smallest adequate intervention

The key insight from our evidence is that the problem has a **structural decomposition solution**: instead of extracting one formula for net_load, decompose into wind/solar/load sub-models where each sub-task has a natural physical variable as its primary driver. This is not just a workaround — it reveals that **symbolic identifiability is task-dependent**, and the choice of prediction target determines which physical variables can survive the sparsification-symbolization pipeline.

### Core technical claim

**Physical variable identifiability in KAN symbolic extraction is governed by feature competition and pruning trajectory, not by the variable's intrinsic information content.** We demonstrate this through: (1) the direct net_load collapse (load dominates), (2) solar as a stable positive case (GHI enters reliably), (3) wind as a boundary case (non-monotonic horizon dependence), and (4) S3 structured decomposition as a constructive solution.

### Required evidence

1. Main result table: KAN > MLP > persistence on delta_net_load_h6 (already frozen)
2. Direct formula collapse evidence (9 symbolic configs, all load-only)
3. Solar ablation: GHI entry rates across horizons and feature group ablations
4. Wind ablation: non-monotonic identifiability pattern
5. S3 structured decomposition: sub-formulas with explicit physical variables
6. Boundary failure: solar h=288 extrapolation collapse

## Method Thesis

- **One-sentence thesis**: We propose a KAN-teacher-guided symbolic extraction framework with structured task decomposition to extract physically interpretable formulas from net load forecasting data, and systematically characterize when and why physical variables survive the sparsification-to-symbolization pipeline.

- **Why this is the smallest adequate intervention**: Rather than inventing new architectures, we use the existing KAN+symbolic extraction pipeline and add only structured task decomposition (S3) and systematic ablation analysis. The contribution is primarily in the experimental methodology and the findings, not in a new model.

- **Why this route is timely**: KAN (Liu et al., 2024) is a recent innovation; applying it to energy system interpretability and characterizing its symbolic extraction behavior is novel. The structured decomposition approach aligns with the MCKAN reference paper's wind/solar sub-task methodology.

## Contribution Focus

- **Dominant contribution**: A systematic characterization of physical variable identifiability in KAN symbolic extraction, showing that feature competition and pruning trajectory — not information content — determine whether wind/GHI/temperature appear in final formulas. Supported by symmetric solar (positive) and wind (boundary) evidence.

- **Supporting contribution**: S3 structured decomposition as a constructive methodology that guarantees physical variable presence by decomposing net_load into physically natural sub-tasks (wind/solar/load), each with its own KAN teacher and symbolic formula.

- **Explicit non-contributions**: (1) We do not claim a new architecture. (2) We do not claim to beat all baselines on all metrics. (3) We do not claim the pipeline is strictly leak-free (pre-split interpolation documented as limitation). (4) We do not claim wind identifiability is a universal phenomenon.

## Proposed Method

### Complexity Budget

- **Frozen / reused backbone**: Standard KAN (pykan 0.2.8) with magnitude+entropy sparsification, per-edge symbolic fitting, SymPy formula construction. Standard data pipeline (ARPA-E PERFORM, Z-score normalization, chronological split).
- **New trainable components**: None. All KAN training is standard.
- **Tempting additions intentionally not used**: (1) Physics-informed KAN (PIKAN) constraints — deferred to future work. (2) Custom symbolic libraries beyond strict/medium. (3) Multi-scale convolutional components from MCKAN. (4) Attention mechanisms. (5) Ensemble methods.

### System Overview

```
Phase 1: PERFORM data → preprocess → chronological split → normalize
Phase 1.5: derive delta targets (h=6,12,24,...) + physics proxies
Phase 2: Train sparse KAN teacher (warmup → sparsify → prune)
Phase 3: Symbolic extraction (per-edge fitting → SymPy formula)
Phase 4: Baselines (matched MLP, persistence, PySR)
Phase 5: Evaluation (reconstruct abs, comparison table, ablation, physics mapping)

S3 Decomposition:
  ├── Wind sub-KAN: delta_wind_h6 → wind formula (wind_speed as primary)
  ├── Solar sub-KAN: delta_solar_h6 → solar formula (GHI as primary)
  ├── Load sub-KAN: delta_load_h6 → load formula (temp/lags as primary)
  └── Combine: net_load = load - wind - solar
```

### Core Mechanism: Structured Task Decomposition for Symbolic Identifiability

- **Input**: Same PERFORM dataset with meteorological + lag features
- **Output**: Three sub-formulas that compose into an interpretable net_load prediction
- **Architecture**: Three independent KAN teachers, each trained on a physically natural sub-task
- **Training signal**: Standard MSE loss on delta targets
- **Why this is the main novelty**: The novelty is NOT in the decomposition itself (which is straightforward) but in the FINDING that decomposition is necessary for physical variable identifiability, and the systematic evidence supporting this claim

### Training Plan

1. Use existing KAN training pipeline (warmup 50 epochs → sparsify with L1/entropy → prune to 80% sparsity → refine)
2. For S3: train 3 sub-KANs independently with focused feature sets
3. Symbolic extraction: strict library, r2_threshold sweep {0.98, 0.99, 0.995}
4. Multi-seed (3 seeds minimum) for robustness

### Failure Modes and Diagnostics

1. **Direct formula collapse**: Detected via feature_importance.csv showing load-only active edges. Already documented as systematic finding.
2. **Symbolic numerical instability**: Medium library produces NaN/inf. Mitigated by safe_exp/safe_div in Phase 3 eval.
3. **Long-horizon extrapolation**: Solar h=288 produces 67% negative predictions. Documented as boundary failure.
4. **Wind forced inclusion degrades skill**: s3_comp_wind skill=-0.080 when raw wind is forced in. Documented as identifiability boundary.

### Novelty and Elegance Argument

The closest work is:
- **KAN original paper (Liu et al., 2024)**: Demonstrates KAN's symbolic regression ability on synthetic/physics problems. Does NOT study the autoregressive dominance problem or physical variable identifiability.
- **MCKAN (Chen et al., 2025)**: Uses multi-scale convolutional KAN for wind/solar power forecasting. Focuses on accuracy, not interpretability or symbolic extraction.
- **PySR (Cranmer, 2023)**: GP-based symbolic regression baseline. Our evidence shows KAN+symbolic outperforms direct PySR on matched settings.

Our exact difference: We are the first to systematically study HOW and WHY physical variables survive (or fail to survive) KAN symbolic extraction in real-world time series forecasting, providing the first empirical characterization of "symbolic identifiability" as a function of task structure, feature competition, and prediction horizon.

## Claim-Driven Validation Sketch

### Claim 1: KAN symbolic extraction works for net load forecasting (accuracy baseline)
- **Minimal experiment**: KAN vs matched MLP vs persistence on delta_net_load_h6
- **Baselines**: Persistence (shift-by-h), MLP (feature/budget aligned), PySR (direct symbolic)
- **Metric**: RMSE, skill score, statistical significance (paired t-test)
- **Expected evidence**: KAN skill > 0.4, significantly better than MLP (already achieved: skill=0.453, p=0.0005)

### Claim 2: Physical variable identifiability depends on task structure, not information content
- **Minimal experiment**:
  - Direct net_load symbolic extraction → load-only collapse (9 configs, all fail)
  - S3 decomposition → each sub-formula contains its target physical variable
  - Solar ablation (h=72/144/576): GHI entry rate vs horizon
  - Wind ablation (h=72/144/576): non-monotonic wind_speed edge survival
- **Baselines**: Feature group ablations (lags-only / meteo-only / both)
- **Metric**: Variable entry rate (edges > 0), formula appearance (sympy contains variable), transfer gap (RMSE_sym - RMSE_KAN)
- **Expected evidence**: Solar GHI enters 3/3 in focused teacher; wind_speed shows non-monotonic pattern; direct net_load collapses

### Claim 3: S3 structured decomposition is a constructive solution
- **Minimal experiment**: Train wind/solar/load sub-KANs, extract sub-formulas, combine
- **Baselines**: Direct single-formula extraction
- **Metric**: Physical variable presence in final composite formula; composite skill score
- **Expected evidence**: All three physical variable groups (wind_speed, GHI, temp) present in composite formula; composite skill positive

## Experiment Handoff Inputs

- **Must-prove claims**: (1) KAN > baselines on prediction; (2) Direct formula collapse is systematic; (3) Solar=positive, Wind=boundary for identifiability; (4) S3 guarantees physical variable presence
- **Must-run ablations**: Feature group (lags-only/meteo-only/both), horizon (h=6/72/144/576), symbolic library (strict/medium), r2_threshold sweep
- **Critical datasets**: ARPA-E PERFORM ERCOT, 5-min resolution, 2018-2020
- **Highest-risk assumptions**: (1) Pre-split interpolation leakage does not invalidate qualitative patterns; (2) S3 composite formula maintains positive skill; (3) Wind non-monotonic pattern replicates across seeds

## Compute & Timeline Estimate

- **Already spent**: 247 runs on Modal cloud, all paper assets frozen as of 2026-03-09
- **Remaining compute**: Minimal — potentially 10-20 new runs for S0 improvements (safe functions) and S3 refinement
- **Data cost**: Zero (PERFORM dataset already downloaded and processed)
- **Timeline**: Focus on thesis writing with existing evidence. New experiments only if they are low-cost and high-impact for the narrative.

## Alignment with MCKAN Reference Paper

The MCKAN paper (Chen et al., 2025) provides natural alignment points:

| MCKAN | Our Method | Connection |
|-------|-----------|------------|
| Multi-step wind/solar power forecasting | Multi-horizon net load forecasting | Same motivation: dispatch coordination |
| Pearson correlation for feature selection | Feature group ablation + pruning trajectory | Similar: identify which meteorological inputs matter |
| Min-Max scaling for stability | Z-score + safe_exp/safe_div for symbolic eval | Both address numerical stability |
| Multi-scale convolution | Multi-scale lags (12/24/48 steps) | Interpretable multi-scale alternative |
| Module ablation (MCKAN/EAA/CQALA) | S0-S3 sweep ablation | Both: systematic component contribution analysis |

The key difference: MCKAN optimizes for accuracy via architectural complexity; we optimize for interpretability via symbolic extraction + structured decomposition. The S3 strategy (separate wind/solar/load sub-models) directly mirrors MCKAN's task structure, making the reference natural rather than forced.
