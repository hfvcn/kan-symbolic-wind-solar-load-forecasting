# Round 1 Refinement (v2 Cycle)

## Problem Anchor
[Verbatim from round 0]
- **Bottom-line problem**: Extract physically meaningful, human-readable mathematical formulas from high-accuracy KAN models for net load forecasting. The key technical barrier: autoregressive dominance causes physical meteorological variables to be pruned away during sparsification, collapsing formulas to load-only expressions.
- **Must-solve bottleneck**: The transfer gap (KAN skill=0.453 → symbolic formula skill=0.076) is unacceptable, AND the formula loses all physical variables. We must understand WHY variables are lost, provide evidence for the mechanism, and demonstrate constructive solutions.
- **Non-goals**: New architecture, SOTA accuracy, deployable system, dataset replacement.
- **Constraints**: Graduation thesis deadline (~4 weeks); 247+ runs complete; Modal GPU; must reference MCKAN.
- **Success condition**: Thesis demonstrating (1) KAN+symbolic works; (2) systematic evidence for WHY physical variables enter/exit formulas; (3) identifiability metrics; (4) S3 decomposition as constructive solution; (5) honest failure documentation.

## Anchor Check
- **Original bottleneck**: Autoregressive dominance prunes physical variables from symbolic formulas
- **Why the revised method still addresses it**: S2 autoregressive blocking directly tests the shortcut competition mechanism; S3 decomposition provides workaround. Both address why and how to fix the bottleneck.
- **Reviewer suggestions rejected as drift**: None — all feedback stays within the anchored problem.

## Simplicity Check
- **Dominant contribution after revision**: ONE claim — autoregressive shortcut competition destroys symbolic identifiability in KAN forecasting; a blocked-shortcut intervention isolates the mechanism; structured decomposition partially restores identifiability.
- **Components removed or merged**:
  1. S0 transfer gap reduction → demoted to engineering implementation detail (appendix/footnote)
  2. CPI → no longer a headline "fourth metric"; derived naturally from VER contrast between blocked/unblocked
  3. Horizon landscape → compressed to appendix unless it changes the conclusion
  4. Metric count reduced from 4 (VER/FAR/TGR/CPI) to 2 primary (VER/FAR) + 1 diagnostic (TGR)
- **Reviewer suggestions rejected as unnecessary complexity**: None
- **Why the remaining mechanism is the smallest adequate route**: We add only one controlled intervention (S2 blocking) to the existing pipeline + one task restructuring (S3). No new architecture, no new training objectives.

## Changes Made

### 1. Contribution Focus: Tightened to ONE Dominant Claim
- **Reviewer said**: "Paper reads as diagnosis + metrics suite + transfer-gap patch + decomposition method. Too many contributions."
- **Action**: Restructured around single dominant claim: **Autoregressive shortcut competition is the mechanism that destroys physical variable identifiability in KAN symbolic extraction.** S2 is the centerpiece experiment. S3 is explicitly secondary.
- **Reasoning**: The reviewer is right — the previous version sprawled. The core insight is the competition mechanism; everything else supports it.
- **Impact**: Paper now has one sharp thesis instead of four parallel threads.

### 2. Language: "Causal" → "Interventional", "Guarantees" → "Preserves"
- **Reviewer said**: "'Causal evidence' and 'guarantees' too strong for blocked-feature ablation + 3-seed rates."
- **Action**: S2 renamed to "interventional mechanism test." S3 rephrased from "guarantees physical variable presence" to "preserves physical variable presence under decomposition." All frequency claims caveated with seed count.
- **Reasoning**: Valid criticism. A single-factor ablation with 3 seeds is evidence for a mechanism, not a formal causal proof. Similarly, S3 doesn't "guarantee" in the mathematical sense.
- **Impact**: Claims now defensible at thesis level and upgradable to publication with more seeds.

### 3. S0 Demoted to Implementation Detail
- **Reviewer said**: "Safe wrappers = engineering hygiene, not the paper."
- **Action**: S0 moved from "Act 4" to an implementation note in the methods section. No longer a numbered sweep or claimed contribution.
- **Reasoning**: Correct — safe_exp/safe_div is necessary plumbing but not intellectually interesting.
- **Impact**: Paper cleaner; one fewer "contribution" competing for attention.

### 4. Seeds: Increase for Key Comparisons
- **Reviewer said**: "3/3 not enough for main-track claims."
- **Action**: For S2 blocked-vs-unblocked comparison, target 5 seeds minimum. Report VER/FAR with bootstrap 95% CI. For existing frozen evidence (B1-B4), keep 3 seeds but caveat clearly.
- **Reasoning**: The key new claim (S2 mechanism) deserves stronger statistical backing. Existing claims are already caveated.
- **Impact**: ~10 additional runs (5 seeds × 2 variants), feasible within compute budget.

### 5. Experimental Core Compressed to 4+1 Cases
- **Reviewer said**: "Compress to four cases: direct failure, solar positive, wind boundary, blocked-lag intervention."
- **Action**: Main paper has exactly 4 core experimental cases + 1 constructive solution:
  1. Direct net-load failure (Act 2)
  2. Solar positive case
  3. Wind boundary case
  4. S2 blocked-lag intervention (Act 3 centerpiece)
  5. S3 structured decomposition (Act 4)
  Everything else (horizon landscape, S0, robustness) → appendix
- **Reasoning**: This gives the paper a clean narrative arc: observe → diagnose → test mechanism → solve.
- **Impact**: Tighter paper, fewer distractions.

## Revised Proposal

# Research Proposal v3: Autoregressive Shortcut Competition Destroys Symbolic Identifiability in KAN Net Load Forecasting

## Problem Anchor
[Same as above — verbatim]

## Technical Gap

Current KAN symbolic regression work (Liu et al. ICLR 2025; PRX 2025; arXiv 2504.03913) demonstrates successful formula extraction on clean physics problems and controlled benchmarks. However, none address the structural challenge of real-world time series forecasting: when autoregressive lag features are available, they dominate sparsification and cause physical meteorological variables to be pruned away, collapsing formulas to trivial autoregressive expressions.

This is not a failure of KAN or symbolic regression — it is a structural property of high-frequency time series where lag features explain >90% of short-term variance. Understanding this mechanism and finding principled workarounds is essential for KAN-based interpretability in energy forecasting.

## Method Thesis

**One-sentence thesis**: In KAN-based symbolic extraction for net load forecasting, autoregressive shortcut competition — not variable irrelevance — is the primary mechanism that prevents physical meteorological variables from surviving the sparsification-to-symbolization pipeline; an interventional blocking test isolates this mechanism, and structured task decomposition partially restores identifiability.

## Contribution Focus

- **Dominant contribution**: Identification and interventional testing of the autoregressive shortcut competition mechanism in KAN symbolic extraction, operationalized via Variable Entry Rate (VER) and Formula Appearance Rate (FAR) measured across blocked vs. unblocked lag conditions.

- **Supporting contribution**: S3 structured decomposition as a constructive workaround that preserves physical variable presence by decomposing net_load into physically natural sub-tasks.

- **Explicit non-contributions**: No new architecture, no SOTA accuracy claims, no formal causal theory, no strict leak-free guarantee.

## Proposed Method

### Pipeline (Existing — No Changes)

KAN teacher training → L1+entropy sparsification → structured pruning → symbolic extraction (pykan `suggest_symbolic` / `fix_symbolic`) → SymPy formula → evaluation on test set

### Identifiability Diagnostics

Two primary metrics, one diagnostic:

- **VER (Variable Entry Rate)**: Fraction of seeds where variable v retains ≥1 active edge post-pruning. Measures whether the variable survives the sparsification bottleneck.
- **FAR (Formula Appearance Rate)**: Fraction of seeds where variable v appears as a free symbol in the final SymPy expression. Measures whether the variable survives symbolic fitting.
- **TGR (Transfer Gap Ratio)**: RMSE_symbolic / RMSE_teacher. Diagnostic for overall extraction quality.

CPI (Competition Pressure Index) is not a separate metric — it is the VER contrast between blocked and unblocked conditions: `ΔVERv = VER_v(blocked) - VER_v(unblocked)`. A large positive ΔVER indicates strong shortcut competition.

### Four-Act Experimental Structure

**Act 1 — Accuracy Baseline** [COMPLETE]
- KAN teacher on delta_net_load_h6: RMSE=1413.51, skill=0.453
- Matched MLP: RMSE=1474.38, skill=0.430 (paired t-test p=0.0005)
- PySR: RMSE≈2070, skill≈0.20
- Persistence: RMSE=2585.66, skill=0.0

**Act 2 — Problem Discovery: Formula Collapse** [COMPLETE]
- 9 symbolic configurations (3 libraries × 3 r² thresholds) on canonical teacher
- ALL collapse to load-only: `0.0007*load - 3.0`
- 11 additional direct S0 runs: all skill < 0
- VER(wind_speed) = 0/9, VER(GHI) = 0/9, FAR(any_physical) = 0/9

**Act 3 — Mechanism Test: Shortcut Competition** [CORE NEW EXPERIMENT]

Three experimental cases isolate the mechanism:

*Case 1: Solar — Positive Control*
- Focused solar teacher on delta_solar_h{72,144,576}
- Feature groups: lags-only / meteo-only / both
- Result: GHI VER=3/3, FAR=3/3 in focused teacher (lags-only and both)
- Interpretation: Solar signal strong enough to survive competition with lags
- [COMPLETE — frozen evidence]

*Case 2: Wind — Boundary Case*
- Focused wind teacher across horizons h=6/72/144/288/576
- Result: Non-monotonic VER — peaks at h=144 (wind_speed_edges=9), absent at h=72 and h=288+
- Interpretation: Wind identifiability depends on horizon; at short horizons lags dominate, at long horizons signal decays
- [COMPLETE — frozen evidence]

*Case 3: Blocked-Lag Intervention — Mechanism Isolation* [NEW — 5+ seeds]
- **Setup**: Same focused wind/solar teachers, but `lag_series = ["load"]` only (wind_lag_* and solar_lag_* removed)
- **Prediction**: VER(wind_speed) increases substantially when wind_lag shortcuts are unavailable
- **Measurement**: ΔVER = VER(blocked) - VER(unblocked), reported with bootstrap 95% CI over 5 seeds
- **If ΔVER >> 0**: Shortcut competition confirmed as mechanism
- **If ΔVER ≈ 0**: Variable truly hard to symbolize (still publishable as honest null result)
- **Cost**: ~10-15 Modal runs (5 seeds × 2-3 targets)

**Act 4 — Constructive Solution: S3 Decomposition** [80% COMPLETE]
- Decompose net_load = load - wind - solar
- Train separate sub-KANs for each component
- Each sub-formula preserves its target physical variable (wind_speed, GHI, temp)
- Composite prediction: skill > 0 (verified)
- **Remaining**: LaTeX rendering, composite metrics, VER/FAR per sub-task

### Training Details

- Architecture: KAN [2, hidden_width, 1], grid=3-5, k=3
- Schedule: warmup 200 → sparsify 800 (λ_L1=1.0, λ_entropy=2.0) → prune (target 80%) → refine 200
- Data: ARPA-E PERFORM ERCOT, 5-min resolution, chronological split (60/20/20), 48-step gap
- Normalization: Z-score on train, applied to val/test
- Seeds: 3 for frozen evidence, 5 for S2 blocked-vs-unblocked key comparisons

### Failure Modes

| Mode | Detection | Mitigation | Status |
|------|-----------|------------|--------|
| Direct formula → load-only | VER=0 for physical vars | Documented as Act 2 finding | Confirmed |
| S2 blocking: ΔVER ≈ 0 | Bootstrap CI includes 0 | Report as "truly hard to symbolize" — honest null | To test |
| S2 blocking: model fails entirely | skill << 0 without lags | Expected for short h; measure accuracy-identifiability tradeoff | To test |
| S3 composite skill < 0 | RMSE > persistence | Already verified positive | Confirmed |
| Solar h=288 extrapolation | 67% negative predictions | Documented as boundary failure | Confirmed |

## Thesis Chapter Structure

1. **Introduction**: Renewable penetration → interpretable forecasting → KAN opportunity
2. **Literature Review**: KAN (ICLR/PRX 2025), symbolic regression, MCKAN, interpretable energy forecasting
3. **Data & Problem**: PERFORM dataset, delta targets, feature engineering, horizon design
4. **Method**: KAN pipeline, identifiability metrics (VER/FAR/TGR), blocked-lag protocol, S3 decomposition
5. **Experiments**:
   - 5.1 Accuracy baseline (Act 1) → Table 1
   - 5.2 Formula collapse (Act 2) → Table 2 + formula rendering
   - 5.3 Solar positive case → Table 3
   - 5.4 Wind boundary case → Table 4 + horizon figure
   - 5.5 Blocked-lag intervention (Act 3 centerpiece) → Table 5 + ΔVER figure
   - 5.6 S3 decomposition (Act 4) → Table 6 + composite formula
6. **Discussion**: Shortcut competition mechanism, accuracy-identifiability tradeoff, limitations (leakage, seed count, single dataset)
7. **Conclusion**: Contributions, future work (PIKAN constraints, more datasets, formal identifiability theory)

**Appendix**: Full horizon landscape, S0 safe function details, seasonal/robustness stratification, all formula renderings

## Compute & Timeline

| Phase | What | GPU-hours | Human-hours |
|-------|------|-----------|-------------|
| M0: S3 Polish | R001-R004 | 0 | 2h |
| M1: S2 Blocking | 10-15 new KAN runs (5 seeds × 2-3 targets) + symbolic extraction | 8-15h | 3h |
| M2: Analysis | VER/FAR computation, ΔVER bootstrap CI, figures | 0 | 4h |
| M3: Paper Writing | Chapters 1-7 | 0 | 40h+ |

Total new GPU-hours: ~8-15h on Modal
Critical path: M0 → M1 → M2 → M3
