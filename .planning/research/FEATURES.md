# Feature Landscape

**Domain:** KAN-SR based interpretable wind-solar coupled load forecasting (graduation thesis)
**Researched:** 2026-02-24
**Overall confidence:** MEDIUM-HIGH

## Table Stakes

Features the thesis committee and reviewers expect. Missing any of these = thesis feels incomplete or undefendable.

### TS-1: KAN Network Implementation

| Aspect | Detail |
|--------|--------|
| **Feature** | Working KAN architecture with learnable spline activation functions on edges |
| **Why Expected** | Core of the thesis title; without it, there is no thesis |
| **Complexity** | Medium |
| **Notes** | Use pykan (KindXiaoming/pykan) as base. Must demonstrate B-spline parameterized univariate functions on edges, summation-only nodes. ICLR 2025 paper establishes this as the canonical architecture. Need to handle grid refinement for improving spline resolution during training. Confidence: HIGH (pykan is well-documented, ICLR 2025 publication). |

### TS-2: Composite Regularization and Sparsification Training

| Aspect | Detail |
|--------|--------|
| **Feature** | Magnitude penalty (L1 on activation amplitudes) + entropy loss (row/column-wise on activation matrix) + L1 on linear weights |
| **Why Expected** | The entire KAN-to-SR pipeline depends on producing a sparse network skeleton; without sparsification, symbolic extraction is meaningless |
| **Complexity** | Medium |
| **Notes** | Three-term loss: MSE_data + lambda_mag * L1_magnitude + lambda_ent * Entropy_activation + lambda_L1 * L1_weights. The magnitude penalty forces feature selection by suppressing unimportant edges. The entropy loss forces information concentration (each sub-node focuses on 1-2 variables). Must implement gradual lambda scheduling (start small, increase). Confidence: HIGH (documented in pykan and KAN-SR paper arXiv:2509.10089). |

### TS-3: Symbolic Expression Extraction Pipeline

| Aspect | Detail |
|--------|--------|
| **Feature** | Spline-to-symbol matching: fit each surviving spline edge to a library of univariate symbolic functions, then compose into closed-form equation |
| **Why Expected** | The "SR" in KAN-SR; this is the interpretability deliverable |
| **Complexity** | Medium-High |
| **Notes** | Build a symbolic function library: constants, linear, polynomials (x^n), power laws (x^a), exp, log, sin, cos, tan, gaussian, sigmoid, tanh. For each pruned edge, use nonlinear least-squares (Gauss-Newton / Levenberg-Marquardt) to find best-fit symbolic form. pykan provides `auto_symbolic()` and `suggest_symbolic()` methods. Must handle the `weight_simple` parameter (0 = accuracy-first, 1 = simplicity-first) to explore the simplicity-accuracy tradeoff. Confidence: HIGH (core pykan functionality). |

### TS-4: Network Pruning

| Aspect | Detail |
|--------|--------|
| **Feature** | Automatic pruning of near-zero edges and nodes after sparsification training |
| **Why Expected** | Prerequisite for readable symbolic extraction; dense networks produce incomprehensible formulas |
| **Complexity** | Low |
| **Notes** | pykan provides `model.prune()`. After sparsification training, visually inspect the network (pykan's built-in visualization scales edge transparency by magnitude). Prune edges below threshold, then retrain the pruned model briefly. Confidence: HIGH (built-in pykan feature). |

### TS-5: PySR Baseline Comparison

| Aspect | Detail |
|--------|--------|
| **Feature** | Run PySR (GP-based symbolic regression) on the same dataset as an independent baseline |
| **Why Expected** | Academic rigor demands comparison against the gold-standard SR method. PySR is the most cited open-source SR tool. Reviewers will ask "why not just use PySR?" |
| **Complexity** | Low-Medium |
| **Notes** | PySR uses Julia backend (SymbolicRegression.jl) with Python frontend. Produces its own Pareto front of complexity vs accuracy. Compare: (a) best-accuracy formulas, (b) best-simplicity formulas, (c) Pareto fronts. Document PySR's known weakness: dimensional curse with >20 features, lower sample efficiency. Confidence: HIGH (PySR is stable, well-maintained, reviewed in Genetic Programming and Evolvable Machines 2024). |

### TS-6: Deep Learning Baseline Comparison (LSTM / MLP)

| Aspect | Detail |
|--------|--------|
| **Feature** | Train standard black-box models (LSTM, MLP, optionally Transformer) on same data for accuracy comparison |
| **Why Expected** | Must prove that interpretability does not come at catastrophic accuracy cost. Committee will want to see KAN-SR accuracy vs state-of-the-art black-box |
| **Complexity** | Low-Medium |
| **Notes** | At minimum: MLP baseline (same parameter count as KAN), LSTM baseline (captures temporal dependencies). Optional: lightweight Transformer (PatchTST or similar). Focus on RMSE/MAE/R2 parity, not on beating them. The thesis argument is "comparable accuracy + far superior interpretability." Confidence: HIGH (standard practice). |

### TS-7: Multi-Dimensional Evaluation Framework

| Aspect | Detail |
|--------|--------|
| **Feature** | Evaluate on 5 axes: prediction accuracy (RMSE, MAE, R2), formula complexity (operator count, AST depth, parameter count), Pareto front analysis, physical consistency checks, computational efficiency |
| **Why Expected** | Single-metric evaluation is insufficient for an interpretability thesis. Pareto front (accuracy vs complexity) is THE core visualization |
| **Complexity** | Medium |
| **Notes** | Prediction: RMSE, MAE, MAPE, R2 (standard in energy forecasting literature). Complexity: count operators, measure AST depth, count free parameters. Pareto: plot complexity (x-axis) vs loss (y-axis), identify knee point. Physics: verify partial derivative signs match physical intuition (e.g., dLoad/dTemp > 0 above comfort threshold). Efficiency: training time, inference latency, parameter count. Confidence: HIGH (well-established metrics, multiple sources confirm). |

### TS-8: ARPA-E PERFORM Data Acquisition and Preprocessing

| Aspect | Detail |
|--------|--------|
| **Feature** | Download, parse, clean, and align time-coincident wind/solar/load data from ARPA-E PERFORM HDF5 files |
| **Why Expected** | No data = no experiments. This is the foundation layer |
| **Complexity** | Medium |
| **Notes** | Data is on AWS S3 (`s3://arpa-e-perform/`) in HDF5 format, 5-minute resolution. Covers ERCOT, MISO, NYISO, SPP. Must align timestamps (all UTC), handle missing values with spline interpolation (not mean fill), apply Z-score normalization, and encode cyclical time features (sin/cos encoding for hour-of-day, day-of-year). Select one ISO region for primary experiments (ERCOT recommended -- largest renewable penetration). Confidence: HIGH (NREL official dataset, well-documented). |

### TS-9: Visualization Suite for Thesis

| Aspect | Detail |
|--------|--------|
| **Feature** | Publication-quality plots: KAN network topology, spline activation shapes, Pareto fronts, prediction vs actual curves, error distributions, extracted formula display |
| **Why Expected** | Thesis is a visual document. KAN's built-in visualization IS the interpretability argument |
| **Complexity** | Medium |
| **Notes** | Required plots: (1) KAN network diagram with edge transparency proportional to magnitude, (2) individual spline activation curves with overlaid symbolic fits, (3) Pareto front: KAN-SR vs PySR, (4) time-series: predicted vs actual for wind/solar/load, (5) residual distributions, (6) extracted formula rendered in LaTeX. Use matplotlib + seaborn. pykan has built-in plot functions. Confidence: HIGH. |

### TS-10: Feature Engineering for Wind-Solar-Load Coupling

| Aspect | Detail |
|--------|--------|
| **Feature** | Construct multi-dimensional feature vectors: thermodynamic (temp, GHI, wind speed, pressure), spatiotemporal (solar angles, cyclic time encodings), autoregressive lags |
| **Why Expected** | Raw data alone is insufficient. Physical feature engineering demonstrates domain understanding and improves SR quality |
| **Complexity** | Medium |
| **Notes** | Three feature groups: (1) Meteorological: temperature, GHI, wind speed, wind direction, pressure. (2) Astronomical/temporal: solar altitude angle, azimuth, sin/cos hour encoding, sin/cos month encoding. (3) Autoregressive: lagged values of load/wind/solar (t-1, t-6, t-12, t-24, t-48 at 5-min resolution = up to 4 hours back). Deliberately include redundant features to test KAN-SR's built-in feature selection capability. Confidence: HIGH (standard energy forecasting practice). |

## Differentiators

Features that elevate the thesis from "adequate" to "excellent." Not strictly required but strongly recommended for competitive standing.

### D-1: PIKAN Physics-Informed Constraints

| Aspect | Detail |
|--------|--------|
| **Feature** | Embed physical laws (energy conservation, Newton's cooling law derivatives, power curve constraints) as soft penalty terms in the KAN loss function |
| **Value Proposition** | Transforms thesis from "data-driven SR" to "physics-aware SR" -- a much stronger academic contribution. Ensures extracted formulas respect physical laws even in extrapolation |
| **Complexity** | High |
| **Notes** | PIKAN adds physics residual terms to the loss function. For this thesis: (a) PV power must be 0 at night (hard constraint via solar angle mask), (b) wind power follows approximate cubic relationship with wind speed (soft constraint on partial derivative), (c) load-temperature relationship must be monotonically increasing above comfort threshold. The arXiv:2408.06650 paper demonstrates PIKAN for power system swing equations with 50% fewer parameters than PINN. This is the strongest differentiator but also the riskiest -- physics constraint formulation requires careful derivation. Confidence: MEDIUM (PIKAN proven for ODEs/DAEs in power systems, but application to load forecasting coupling is novel and untested). |

### D-2: Separability and Symmetry Detection (AI Feynman-inspired)

| Aspect | Detail |
|--------|--------|
| **Feature** | Automatically detect translational symmetries and multiplicative separabilities in the data to decompose high-dimensional problems into independent low-dimensional sub-problems |
| **Value Proposition** | Directly addresses the curse of dimensionality. If f(x,y) = g(x) * h(y), solve two 1D problems instead of one 2D problem. Dramatically improves formula simplicity and interpretability |
| **Complexity** | High |
| **Notes** | KAN-SR framework (arXiv:2509.10089) explicitly implements this as a "divide-and-conquer" strategy inspired by AI Feynman. Test for: (a) translational symmetry: f(x+c, y) = f(x, y) for some variables, (b) additive separability: f(x,y) = g(x) + h(y), (c) multiplicative separability: f(x,y) = g(x) * h(y). Each detected symmetry/separability reduces the effective dimensionality. Confidence: MEDIUM (proven on SRSD benchmarks, but requires careful implementation for real-world energy data which may not exhibit clean separabilities). |

### D-3: MultKAN with Multiplication Nodes

| Aspect | Detail |
|--------|--------|
| **Feature** | Extend standard additive KAN with multiplication nodes to capture product interactions (e.g., wind_speed^3 * air_density) |
| **Value Proposition** | Standard KAN can only compose additions of univariate functions. MultKAN adds explicit multiplication, which is essential for physical laws that involve products (power curves, heat transfer coefficients) |
| **Complexity** | Medium |
| **Notes** | pykan's MultKAN class supports this natively. The "KANs Meet Science" paper (Phys. Rev. X, December 2025) introduces MultKAN as a major new functionality. Multiplication nodes allow KAN to discover expressions like P = 0.5 * rho * A * v^3 (wind power) which require variable-variable products. Confidence: MEDIUM-HIGH (implemented in pykan, documented in Phys. Rev. X paper). |

### D-4: Cross-Validation with PySR Sub-Expression Verification

| Aspect | Detail |
|--------|--------|
| **Feature** | After KAN-SR extracts formulas, feed the sub-expressions into PySR for independent verification and potential simplification |
| **Value Proposition** | Dual-method verification dramatically strengthens academic credibility. Shows that findings are method-independent, not artifacts of KAN architecture |
| **Complexity** | Medium |
| **Notes** | The research plan explicitly calls for a "dual-track benchmark architecture." Feed KAN-SR extracted sub-expressions (e.g., the wind power component) as seed structures to PySR. If PySR independently converges to similar forms, confidence in the physical interpretation skyrockets. Also use PySR's native Pareto front to cross-check the knee point selection. Confidence: MEDIUM (methodologically sound, but integration requires manual work). |

### D-5: Multi-ISO Generalization Study

| Aspect | Detail |
|--------|--------|
| **Feature** | Train on one ISO region (e.g., ERCOT), extract formulas, then test formula transferability on other ISOs (MISO, NYISO, SPP) |
| **Value Proposition** | Proves that extracted physics are universal, not region-specific overfitting artifacts. This is the strongest possible validation of "real physics discovery" |
| **Complexity** | Medium |
| **Notes** | ARPA-E PERFORM covers 4 ISOs with identical data formats. Train KAN-SR on ERCOT, extract formulas. Then: (a) apply formulas directly to MISO/NYISO/SPP (zero-shot transfer), (b) fine-tune only the formula constants (few-shot transfer). If formulas transfer well, the thesis can claim discovery of universal physical coupling mechanisms. Confidence: MEDIUM (data is available, but different ISOs have different climates/grids, so transferability is uncertain). |

### D-6: Ablation Study on Regularization Components

| Aspect | Detail |
|--------|--------|
| **Feature** | Systematically disable each regularization term (magnitude penalty, entropy loss, L1) and measure impact on formula quality and accuracy |
| **Value Proposition** | Demonstrates deep understanding of the method. Shows which components are essential vs nice-to-have |
| **Complexity** | Low-Medium |
| **Notes** | Run 4 configurations: (a) full regularization, (b) no magnitude penalty, (c) no entropy loss, (d) no L1. Compare resulting formula complexity, accuracy, and sparsity. This is standard ablation study practice and reviewers love it. Confidence: HIGH (straightforward experimental design). |

### D-7: Physical Interpretation of Discovered Formulas

| Aspect | Detail |
|--------|--------|
| **Feature** | Map extracted symbolic formulas back to known physics: identify terms corresponding to Betz's law, NOCT corrections, thermal inertia effects |
| **Value Proposition** | This is THE thesis contribution -- not just extracting formulas, but proving they encode real physics. Elevates from "ML experiment" to "scientific discovery" |
| **Complexity** | Medium |
| **Notes** | After extracting formulas, systematically analyze each term: (a) cubic wind speed terms -> Betz's law (wind power proportional to v^3), (b) temperature-efficiency coupling -> known PV thermal degradation (~0.4%/C for crystalline Si), (c) sinusoidal time terms -> diurnal load patterns. Compare extracted coefficients to published physical constants. If they match approximately, this is the strongest result in the thesis. Confidence: MEDIUM (depends on whether KAN-SR actually discovers clean physics from real data, which is uncertain). |

### D-8: Partial Derivative Sensitivity Analysis

| Aspect | Detail |
|--------|--------|
| **Feature** | Compute and visualize analytical partial derivatives of extracted formulas (dLoad/dTemp, dPV/dWindSpeed, etc.) to show physical sensitivity |
| **Value Proposition** | Demonstrates the "calculus stress test" capability that black-box models cannot provide. Shows engineers exactly how sensitive predictions are to each input variable |
| **Complexity** | Low-Medium |
| **Notes** | Since formulas are closed-form, partial derivatives are trivially computable symbolically (use sympy). Plot sensitivity surfaces: how does predicted load change as temperature and wind speed vary simultaneously? Verify derivative signs match physical intuition. This directly supports the thesis argument about interpretable models enabling safe grid operation. Confidence: HIGH (purely computational, no uncertainty). |

## Anti-Features

Features to explicitly NOT build. Including these would waste time, expand scope beyond thesis boundaries, or introduce unnecessary complexity.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Real-time online deployment system | Thesis is research validation, not production engineering. Building a SCADA-integrated system is an entire separate project | Document deployment feasibility in "Future Work" section. Show inference latency numbers to prove it is theoretically deployable |
| TPSR (Transformer-based SR) implementation | Extremely high complexity: requires pre-training on massive synthetic dataset, MCTS integration. The research plan explicitly marks this as out-of-scope | Mention TPSR in related work, cite arXiv papers, note it as future direction for real-time inference scenarios |
| Mobile/edge deployment optimization | Completely outside thesis scope (power systems research, not embedded systems) | Note that extracted formulas are lightweight enough for edge deployment as a side benefit |
| Multi-modal image fusion (sky images, soiling photos) | Stanford SUNSET dataset integration adds enormous preprocessing complexity for marginal thesis value | List as future work. Focus on numerical time-series features which are sufficient for the core KAN-SR contribution |
| Web dashboard or GUI | Engineering deliverable, not academic contribution | Jupyter notebooks with clear visualizations are the correct medium for a thesis |
| Probabilistic/uncertainty quantification forecasting | While ARPA-E PERFORM provides probabilistic forecast data, building a full probabilistic KAN-SR pipeline is a separate research direction | Use deterministic forecasts. Mention probabilistic extension in future work. Optionally show simple confidence intervals via ensemble of formulas from Pareto front |
| Hyperparameter auto-tuning (NAS/Bayesian optimization) | Adds significant engineering complexity without strengthening the interpretability narrative | Manual grid search over key hyperparameters (grid size, spline order, regularization lambdas). Document search process clearly |
| Wind farm wake effect modeling | While physically interesting, requires CFD-level spatial data not available in ARPA-E PERFORM | Focus on aggregate zonal wind power prediction. Mention wake modeling as domain where KAN-SR could shine (cite existing wake SR papers) |
| EQL (Equation Learner) comparison | Research plan explicitly notes EQL is "outdated" with known gradient explosion issues. Not a credible modern baseline | Mention briefly in related work as historical context for deep SR. PySR + black-box DL are sufficient baselines |

## Feature Dependencies

```
TS-8 (Data) --> TS-10 (Feature Engineering) --> TS-1 (KAN) --> TS-2 (Sparsification)
                                                    |
                                                    v
TS-2 (Sparsification) --> TS-4 (Pruning) --> TS-3 (Symbolic Extraction) --> TS-9 (Visualization)
                                                    |
                                                    v
                                              D-7 (Physical Interpretation)
                                              D-8 (Partial Derivatives)
                                              D-2 (Separability Detection)

TS-8 (Data) --> TS-5 (PySR Baseline) --> D-4 (Cross-Validation)
TS-8 (Data) --> TS-6 (DL Baselines)

TS-3 (Symbolic Extraction) + TS-5 (PySR) + TS-6 (DL) --> TS-7 (Evaluation Framework)

D-1 (PIKAN) depends on: TS-1 (KAN) + TS-2 (Sparsification) + domain physics derivation
D-3 (MultKAN) depends on: TS-1 (KAN) -- can be swapped in early
D-5 (Multi-ISO) depends on: TS-3 (Symbolic Extraction) being complete for primary ISO
D-6 (Ablation) depends on: TS-2 (Sparsification) + TS-3 (Symbolic Extraction)
```

**Critical path:** Data -> Feature Engineering -> KAN -> Sparsification -> Pruning -> Symbolic Extraction -> Evaluation

**Parallelizable:** PySR baseline and DL baselines can run concurrently with KAN development after data is ready.

## MVP Recommendation

**Prioritize (must complete for defensible thesis):**

1. **TS-8** Data acquisition and preprocessing -- foundation, do first
2. **TS-10** Feature engineering -- enables meaningful experiments
3. **TS-1 + TS-2 + TS-4 + TS-3** KAN pipeline (train -> sparsify -> prune -> extract) -- core contribution
4. **TS-5 + TS-6** Baselines (PySR + LSTM/MLP) -- required for academic rigor
5. **TS-7** Multi-dimensional evaluation with Pareto front -- makes the results publishable
6. **TS-9** Visualization suite -- makes the thesis readable
7. **D-7** Physical interpretation -- makes the thesis meaningful (this is what turns "I ran an experiment" into "I discovered physics")
8. **D-8** Partial derivative analysis -- low effort, high impact proof of interpretability value

**Strongly recommended differentiators (do if time allows, in priority order):**

1. **D-6** Ablation study -- low complexity, high academic value
2. **D-3** MultKAN -- medium complexity, enables richer formulas
3. **D-1** PIKAN physics constraints -- high complexity but high impact; even a simple constraint (PV=0 at night) is publishable
4. **D-4** Cross-validation with PySR -- strengthens credibility
5. **D-2** Separability detection -- powerful but complex to implement correctly

**Defer (future work section):**

- **D-5** Multi-ISO generalization -- interesting but not essential for graduation
- TPSR comparison -- too complex
- Probabilistic forecasting -- different research direction
- Image/multi-modal fusion -- different data pipeline

## Sources

- [KAN: Kolmogorov-Arnold Networks (ICLR 2025)](https://arxiv.org/abs/2404.19756) -- HIGH confidence
- [pykan GitHub](https://github.com/KindXiaoming/pykan) -- HIGH confidence
- [pykan documentation](https://kindxiaoming.github.io/pykan/kan.html) -- HIGH confidence
- [KAN-SR: A Kolmogorov-Arnold Network Guided Symbolic Regression Framework (arXiv:2509.10089)](https://arxiv.org/abs/2509.10089) -- HIGH confidence
- [Kolmogorov-Arnold Networks Meet Science (Phys. Rev. X, Dec 2025)](https://link.aps.org/doi/10.1103/4t7t-v19l) -- HIGH confidence
- [S2KAN: Softly Symbolifying KANs (arXiv:2512.07875)](https://arxiv.org/abs/2512.07875) -- MEDIUM confidence (very recent)
- [PIKAN for Power System Dynamics (arXiv:2408.06650)](https://arxiv.org/abs/2408.06650) -- HIGH confidence
- [Opening the AI Black-Box: KAN-SR for Energy Applications (arXiv:2504.03913)](https://arxiv.org/abs/2504.03913) -- HIGH confidence
- [PySR GitHub](https://github.com/MilesCranmer/PySR) -- HIGH confidence
- [Review of PySR (Genetic Programming and Evolvable Machines, 2024)](https://link.springer.com/article/10.1007/s10710-024-09503-4) -- HIGH confidence
- [ARPA-E PERFORM Datasets (NREL/OEDI)](https://data.openei.org/submissions/5772) -- HIGH confidence
- [ARPA-E PERFORM on AWS](https://registry.opendata.aws/arpa-e-perform/) -- HIGH confidence
- [NREL Technical Report on PERFORM Phase II](https://docs.nrel.gov/docs/fy24osti/83828.pdf) -- HIGH confidence
- [Symbolic Regression in Energy Engineering (Lund University thesis)](https://lup.lub.lu.se/student-papers/record/9163117/file/9163122.pdf) -- MEDIUM confidence
- [Comparative Analysis of Model Selection Criteria for SR](https://link.springer.com/chapter/10.1007/978-3-032-15635-8_6) -- MEDIUM confidence
- [Comprehensive review of ML for solar PV and wind forecasting (2025)](https://jesit.springeropen.com/articles/10.1186/s43067-025-00239-4) -- MEDIUM confidence
