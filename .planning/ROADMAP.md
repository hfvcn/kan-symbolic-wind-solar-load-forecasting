# Roadmap: KAN-SR Wind-Solar Load Forecasting

## Overview

This roadmap transforms 19 v1 requirements into 8 phases that deliver a complete graduation thesis: from raw ARPA-E PERFORM data to interpretable symbolic formulas for wind-solar load prediction, with rigorous baselines, physics constraints, and publication-ready visualizations. The critical path runs through data preparation, KAN training, and symbolic extraction -- everything downstream depends on extracting at least one meaningful formula from noisy energy data. Baseline experiments (PySR, LSTM/MLP) can partially overlap the KAN pipeline since they only need the data. Enhancement phases (physics constraints, interpretability analysis, generalization) elevate the thesis from adequate to excellent.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Data Pipeline & Infrastructure** - Acquire ARPA-E PERFORM data, build preprocessing pipeline, establish Modal + persistent storage infrastructure
- [ ] **Phase 2: KAN Architecture & Sparse Training** - Implement KAN network with composite regularization, achieve 80%+ edge pruning
- [ ] **Phase 3: Symbolic Expression Extraction** - Extract closed-form mathematical formulas from sparse KAN via symbolic matching
- [ ] **Phase 4: Baseline Experiments** - Run PySR and deep learning (LSTM/MLP) baselines for comparison
- [ ] **Phase 5: Evaluation Framework & Ablation** - Build multi-dimensional evaluation system and conduct regularization ablation study
- [ ] **Phase 6: Physics-Informed Enhancements** - Integrate PIKAN constraints, MultKAN multiplication nodes, and separability detection
- [ ] **Phase 7: Interpretability & Validation** - Map formulas to physics, conduct sensitivity analysis, cross-validate with PySR
- [ ] **Phase 8: Generalization & Visualization** - Test multi-ISO transfer and produce publication-quality thesis figures

## Phase Details

### Phase 1: Data Pipeline & Infrastructure
**Goal**: Researcher can load, preprocess, and split ERCOT wind-solar-load data into ML-ready feature tensors with guaranteed temporal integrity
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria** (what must be TRUE):
  1. ARPA-E PERFORM ERCOT data loads from HDF5 into pandas DataFrames with correct timestamps (UTC-aligned, 5-min resolution)
  2. Preprocessing pipeline outputs clean tensors: missing values interpolated, Z-score normalized, no NaN/Inf values in output
  3. Feature matrix includes all four feature groups: meteorological (temp/GHI/wind speed/pressure), astronomical (solar angle), cyclic time encoding, and autoregressive lags (t-1 to t-48)
  4. Train/val/test split is strictly chronological with lag-window gap at boundaries; no future information leaks into training data
  5. Persistent artifact store (Modal Volume and/or S3) saves and restores raw/processed data and intermediate results; jobs can resume without re-downloading data
**Plans**: TBD

Plans:
-- [ ] 01-01: Modal smoke test + artifact contract
- [ ] 01-02: PERFORM download + cache (Volume/S3)
- [ ] 01-03: Preprocess + split smoke test
- [ ] 01-04: Sync artifacts to local runs/

### Phase 2: KAN Architecture & Sparse Training
**Goal**: Researcher has a trained, reliably sparse KAN model where 80%+ of edges are pruned, producing interpretable feature importance rankings
**Depends on**: Phase 1
**Requirements**: KAN-01, KAN-02, KAN-03
**Success Criteria** (what must be TRUE):
  1. pykan KAN network trains on ERCOT data with B-spline activations and converges (training loss decreasing, validation loss monitored)
  2. Composite regularization (L1 magnitude + entropy loss + linear L1) with progressive lambda scheduling drives edge magnitudes toward zero
  3. After pruning via pykan prune(), at least 80% of edges are removed while validation RMSE remains within 10% of unpruned model
  4. Spline grid range is set to [-5, 5] and updated from samples periodically; no silent range mismatch failures
  5. Training checkpoints persist to a Modal Volume every 15 minutes; training can resume from any checkpoint
**Plans**: TBD

Plans:
- [ ] 02-01: KAN training (small slice) + checkpoints
- [ ] 02-02: Prune + refit + sparsity report

### Phase 3: Symbolic Expression Extraction
**Goal**: At least one closed-form symbolic formula for ERCOT load prediction is extracted from the sparse KAN, with per-edge quality metrics and LaTeX rendering
**Depends on**: Phase 2
**Requirements**: KAN-04
**Success Criteria** (what must be TRUE):
  1. Per-edge symbolic matching produces candidate symbolic functions with R-squared >= 0.99 for high-confidence edges
  2. Interleaved fixing approach works: high-confidence edges are fixed symbolically while remaining edges continue training
  3. Final combined symbolic expression is a valid SymPy expression that can be evaluated on test data and rendered as LaTeX
  4. Formula complexity metrics are computed (AST node count, operator count, tree depth) for Pareto analysis
**Plans**: TBD

Plans:
- [ ] 03-01: auto_symbolic + per-edge R² report

### Phase 4: Baseline Experiments
**Goal**: PySR and deep learning baselines produce comparison results on the same ERCOT data, enabling fair evaluation of KAN-SR
**Depends on**: Phase 1 (data pipeline); Phase 3 optional (evaluation benefits from KAN-SR results but baselines can start earlier)
**Requirements**: EVAL-01, EVAL-02
**Success Criteria** (what must be TRUE):
  1. PySR runs in a separate job/environment (isolated from pykan/PyTorch when needed), produces a Pareto frontier of symbolic formulas for ERCOT load
  2. LSTM baseline trains on same chronological split with same features, producing RMSE/MAE/R-squared on test set
  3. MLP baseline trains with equivalent parameter count to KAN, producing RMSE/MAE/R-squared on test set
  4. All baselines use identical test data and evaluation metrics for fair comparison
**Plans**: TBD

Plans:
- [ ] 04-01: PySR baseline (isolated job)
- [ ] 04-02: LSTM/MLP baselines + metrics

### Phase 5: Evaluation Framework & Ablation
**Goal**: Multi-dimensional evaluation framework quantifies KAN-SR against all baselines, and ablation study demonstrates understanding of each regularization component
**Depends on**: Phase 3, Phase 4
**Requirements**: EVAL-03, EVAL-05
**Success Criteria** (what must be TRUE):
  1. Evaluation framework produces a comparison table with at least 5 dimensions: prediction accuracy (RMSE/MAE/R-squared), formula complexity, Pareto optimality, physical consistency score, and computation time
  2. Pareto frontier plot shows KAN-SR and PySR formulas on the same accuracy-vs-complexity plane
  3. Ablation study disables each regularization component independently (magnitude penalty, entropy loss, linear L1) and quantifies impact on formula quality and prediction accuracy
  4. Per-season accuracy breakdown reveals whether model generalizes across weather regimes
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

### Phase 6: Physics-Informed Enhancements
**Goal**: PIKAN physics constraints, MultKAN multiplication nodes, and separability detection improve formula quality and physical interpretability beyond vanilla KAN-SR
**Depends on**: Phase 2 (requires working KAN training loop); benefits from Phase 3 (baseline symbolic extraction for comparison)
**Requirements**: PIKAN-01, PIKAN-02, PIKAN-03
**Success Criteria** (what must be TRUE):
  1. At least one hard physics constraint (nighttime PV = 0) is enforced and never violated in model outputs
  2. At least one soft physics constraint (wind power ~ v-cubed, load-temperature monotonicity) reduces physics inconsistency in extracted formulas
  3. MultKAN with multiplication nodes discovers at least one product-form relationship (e.g., power term resembling P = 0.5*rho*A*v^3)
  4. Separability detection identifies additive or multiplicative decomposition structure in the load forecasting problem
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD
- [ ] 06-03: TBD

### Phase 7: Interpretability & Validation
**Goal**: Extracted formulas are mapped to known physical laws, validated via sensitivity analysis, and cross-checked with independent PySR verification
**Depends on**: Phase 3, Phase 5
**Requirements**: EVAL-06, EVAL-07, EVAL-08
**Success Criteria** (what must be TRUE):
  1. At least one extracted sub-expression is mapped to a known physical relationship (Betz law for wind, NOCT correction for PV, thermal inertia for load)
  2. Partial derivatives (dLoad/dTemp, dPV/dWindSpeed, etc.) computed symbolically via SymPy produce physically plausible signs and magnitudes
  3. Key KAN-SR sub-expressions are independently recovered by PySR when used as search seeds, strengthening academic credibility
**Plans**: TBD

Plans:
- [ ] 07-01: TBD
- [ ] 07-02: TBD

### Phase 8: Generalization & Visualization
**Goal**: Model generalization is tested across ISO regions, and all thesis figures and tables are publication-ready
**Depends on**: Phase 5, Phase 6, Phase 7 (needs all results for final visualization)
**Requirements**: GENL-01, EVAL-04
**Success Criteria** (what must be TRUE):
  1. ERCOT-trained model is tested on at least one other ISO region (MISO, NYISO, or SPP) in zero-shot and/or few-shot settings
  2. Transfer performance metrics quantify generalization gap between home region and target regions
  3. Complete visualization suite is generated: KAN topology diagram, learned spline curves, Pareto frontier comparison, time-series prediction vs actual, residual distribution, and LaTeX formula rendering
  4. All figures are publication-quality (proper axis labels, legends, font sizes suitable for thesis document)
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8
Note: Phase 4 (baselines) can start after Phase 1 completes, in parallel with Phases 2-3.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Pipeline & Infrastructure | 0/TBD | Not started | - |
| 2. KAN Architecture & Sparse Training | 0/TBD | Not started | - |
| 3. Symbolic Expression Extraction | 0/TBD | Not started | - |
| 4. Baseline Experiments | 0/TBD | Not started | - |
| 5. Evaluation Framework & Ablation | 0/TBD | Not started | - |
| 6. Physics-Informed Enhancements | 0/TBD | Not started | - |
| 7. Interpretability & Validation | 0/TBD | Not started | - |
| 8. Generalization & Visualization | 0/TBD | Not started | - |
