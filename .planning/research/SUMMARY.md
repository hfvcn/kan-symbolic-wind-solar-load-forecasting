# Project Research Summary

**Project:** KAN-SR Wind-Solar Load Forecasting (Symbolic Regression for Interpretable Prediction)
**Domain:** Scientific machine learning / interpretable energy forecasting (graduation thesis)
**Researched:** 2026-02-24
**Confidence:** MEDIUM

## Executive Summary

This project applies Kolmogorov-Arnold Networks with a symbolic regression pipeline (KAN-SR) to wind-solar coupled load forecasting, producing closed-form mathematical equations rather than black-box predictions. The approach is directly motivated by a September 2025 arXiv paper (arXiv:2509.10089) that demonstrates KAN-SR on physical systems using a JAX+Equinox+Optax+Optimistix+Diffrax stack. The thesis goal is to prove that KAN-SR achieves accuracy comparable to deep learning baselines (LSTM, MLP) while generating physically interpretable symbolic formulas. The primary dataset is the ARPA-E PERFORM HDF5 dataset (AWS S3), which covers four US ISO regions at 5-minute resolution. Data is well-documented and publicly available with no access restrictions.

The recommended implementation builds on pykan (KindXiaoming/pykan) for the symbolic regression pipeline and PySR as the gold-standard comparison baseline. A critical stack decision is that the KAN-SR reference paper used JAX+Equinox, but since its code is not publicly available, the most practical approach for a graduation thesis is to use pykan directly — accepting its performance limitations — while following the KAN-SR paper's architectural decisions (shallow networks, RSWAF-style activations, composite regularization, hierarchical symbolic extraction). The production evaluation deliverable is a Pareto frontier of formula complexity vs prediction accuracy, compared between KAN-SR and PySR on ERCOT load data.

The two greatest risks are (1) symbolic extraction quality: real noisy energy data may not decompose cleanly into interpretable formulas, and the two-stage KAN-to-symbol pipeline accumulates errors; and (2) long-run execution reliability: experiments can take many hours, and without robust checkpointing + persistent artifacts, failures waste days. Both risks are mitigable with known techniques: strict per-edge R-squared thresholds and constant re-optimization for risk 1, aggressive checkpointing to persistent storage and isolating PySR runs from PyTorch runs (to avoid Julia/PyTorch binding conflicts) for risk 2.

## Key Findings

### Recommended Stack

The recommended stack centers on pykan (KindXiaoming/pykan v0.2.8) as the KAN implementation because it is the only KAN variant with a complete built-in symbolic regression pipeline (`auto_symbolic`, `suggest_symbolic`, `symbolic_formula`). Efficient-KAN and Fast-KAN are faster but lack symbolic extraction entirely. PySR 1.5.9 serves as the essential baseline SR method, providing a Pareto frontier via its Julia backend for direct comparison against KAN-SR results. SymPy integrates both tools and enables closed-form expression manipulation and LaTeX rendering.

If performance on real data is unacceptably slow with pykan, the fallback is to reimplement the architecture in JAX+Equinox following arXiv:2509.10089 — but this adds 2-4 weeks of implementation risk because the paper's code is not public. For a graduation thesis timeline, the pykan path is lower risk despite lower speed.

**Core technologies:**
- pykan 0.2.8: KAN architecture with built-in symbolic regression — only option with full SR pipeline
- PySR 1.5.9 (Julia backend): gold-standard GP symbolic regression baseline — required for academic credibility
- SymPy >=1.12: closed-form expression manipulation and LaTeX output — bridges KAN-SR and PySR
- h5py + pandas + scikit-learn: ARPA-E PERFORM HDF5 data ingestion, preprocessing, and evaluation metrics
- Matplotlib >=3.8: publication-quality Pareto fronts and visualization suite for thesis
- Modal (GPU): primary compute environment — supports long-running, restartable jobs with persistent Volumes/S3 for artifacts

**Critical version notes:** pykan requires PyTorch 2.2.2; PySR requires Julia 1.10+ (auto-installed). Import order matters if you run both in one Python process: `juliacall` must be imported before `torch` to reduce segfault risk; best practice is to run KAN and PySR in separate jobs/environments.

### Expected Features

See `.planning/research/FEATURES.md` for full details and dependency graph.

**Must have (table stakes) — all 10 required for a defensible thesis:**
- TS-8: ARPA-E PERFORM data acquisition and preprocessing — foundation layer, must come first
- TS-10: Multi-dimensional feature engineering (meteorological, astronomical, cyclic encoding, lag features)
- TS-1: KAN network implementation with B-spline activations (pykan)
- TS-2: Composite regularization training (MSE + magnitude penalty + entropy loss + L1)
- TS-4: Network pruning after sparsification (pykan's built-in `model.prune()`)
- TS-3: Symbolic expression extraction pipeline (`auto_symbolic`, constant re-optimization)
- TS-5: PySR baseline comparison (Pareto frontier)
- TS-6: Deep learning baselines (LSTM + MLP minimum)
- TS-7: Multi-dimensional evaluation framework (RMSE/MAE/R2, complexity metrics, Pareto front)
- TS-9: Publication-quality visualization suite

**Should have (differentiators — ranked by impact-to-effort ratio):**
- D-6: Ablation study on regularization components — low effort, high academic value, demonstrates method understanding
- D-8: Partial derivative sensitivity analysis — purely computational (symbolic diff), proves interpretability value proposition
- D-7: Physical interpretation of discovered formulas — maps extracted terms to known physics (Betz law, PV thermal degradation)
- D-3: MultKAN with multiplication nodes — enables discovery of product relationships (wind power = 0.5*rho*A*v^3)
- D-1: PIKAN physics-informed constraints — high impact but high risk; even one simple constraint (PV=0 at night) is publishable

**Defer to future work:**
- D-5: Multi-ISO generalization study — interesting but not essential for graduation
- D-4: Cross-validation with PySR sub-expression verification — strengthens credibility but time-intensive
- D-2: Separability detection (AI Feynman-inspired) — powerful but complex; include only if KAN-SR pipeline works cleanly first

**Anti-features (explicitly do not build):**
- Real-time deployment system, web dashboard, GUI
- TPSR (Transformer-based SR) implementation
- Probabilistic/uncertainty quantification forecasting pipeline
- Multi-modal image fusion, EQL (Equation Learner) comparison

### Architecture Approach

The system is a five-stage sequential pipeline with one well-defined parallel branch: Data Pipeline → KAN Network Training → SR Extraction → Evaluation (the critical path); PIKAN Physics Constraints augment the KAN training loop as an optional add-on; PySR Baseline runs in parallel with KAN training once data is ready. Each component has clear input/output contracts and can be developed and tested in isolation. The recommended organization separates concerns into 7 notebooks/scripts: data exploration, data pipeline, KAN training, symbolic extraction, PIKAN physics, PySR baseline, and evaluation. All shared code lives in a `src/` directory in the repo, while large artifacts (data/checkpoints/results) live in persistent storage (Modal Volume and/or S3).

**Major components:**
1. Data Pipeline — HDF5 ingestion, feature engineering, chronological split, Z-score normalization; no random shuffle
2. KAN Network Trainer — pykan training with progressive sparsification (lamb scheduling), pruning, grid refinement; checkpoint every 15 minutes to persistent storage
3. SR Extraction Pipeline — per-edge spline-to-symbol matching, SymPy simplification, constant re-optimization via BFGS; interleaved fixing approach
4. PIKAN Physics Constraints — soft loss terms for energy conservation, solar night boundary, monotonicity; curriculum learning (add physics loss after initial convergence)
5. Evaluation and Benchmarking — PySR baseline, Pareto frontier comparison, physical consistency checks, per-season accuracy decomposition

**Key patterns to follow:**
- Progressive sparsification: start weak regularization (lamb=0.001), increase gradually; prune only after 80%+ edges are dead
- Checkpoint-resume: save every 15 minutes to persistent storage; never run >1 hour without a checkpoint
- Separate KAN and PySR runs: PyTorch/Julia binding conflict makes coexistence fragile
- Chronological data split only: 2017-2018 train, early 2019 val, late 2019 test; insert lag-window gap at boundary

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full detail including warning signs and recovery strategies.

1. **Spline grid range mismatch (silent failure)** — Set `grid_range=[-5, 5]` from the start; call `model.update_grid_from_samples(x)` periodically; monitor activation ranges at each layer. Default `[-1, 1]` fails silently on hidden layers even after input normalization.

2. **Two-stage error accumulation** — Use interleaved symbolic fixing (fix high-confidence edges immediately, continue training others); enforce `r2_threshold=0.99` per edge; always re-optimize symbolic formula constants against raw data (not KAN predictions) after extraction.

3. **PIKAN loss imbalance** — Implement gradient norm monitoring; start training with data loss only for 60% of epochs; use linear ramp warmup for physics loss. Gradient magnitudes for PDE residuals can be 100-1000x larger than data loss gradients.

4. **KAN overfitting to noise** — Never exceed grid size 10 initially; validate on chronologically held-out data from a different season or year; if training R-squared exceeds 0.99 on real weather data, suspect overfitting. Stop grid refinement when validation loss stops improving.

5. **Temporal data leakage** — Strictly chronological splitting; insert gap equal to maximum lag window between train and test; use expanding-window time-series CV, never k-fold. This is unrecoverable if discovered late — fix before any training.

6. **Resource ceiling / long-run reliability** — Isolate PySR from PyTorch when needed; set PySR to a conservative resource budget (e.g., fewer populations, batching); checkpoint aggressively; start with tiny networks to validate pipeline before scaling.

7. **Symbolic library too narrow or too broad** — Design library with wind-solar physics in mind (include `x^3` for Betz law, `exp(-ax)` for thermal decay); limit to 15-20 domain-relevant functions; exclude exotic functions (Bessel, erf) initially.

## Implications for Roadmap

Based on the combined research, the dependency graph from FEATURES.md and ARCHITECTURE.md both point to the same natural phase structure. The critical constraint is that all downstream work (SR extraction, evaluation, interpretation) depends on having a trained sparse KAN, which in turn depends on having clean data with correct preprocessing. Pitfalls research shows that the most catastrophically unrecoverable mistakes (temporal leakage, no checkpointing) occur in Phase 1.

### Phase 1: Foundation — Environment, Data, and Infrastructure

**Rationale:** Every downstream phase depends on this. Two of the most unrecoverable pitfalls (temporal data leakage, losing intermediate artifacts mid-experiment) must be addressed here before any training begins. This phase has no ML content but establishes constraints that affect all subsequent work.
**Delivers:** Working ARPA-E PERFORM data pipeline outputting normalized feature tensors; persistent artifact store (Modal Volume and/or S3) for data/checkpoints/results; environment configuration (pykan + PySR isolated runs confirmed working); feature matrix with meteorological, astronomical, cyclic, and lag features for ERCOT.
**Addresses:** TS-8 (data acquisition), TS-10 (feature engineering)
**Avoids:** Pitfall 5 (resource ceiling / long-run reliability), Pitfall 7 (temporal data leakage) — both are fatal if not addressed here
**Research flag:** Standard patterns — HDF5 + pandas + boto3 is well-documented; ARPA-E PERFORM has official GitHub documentation; no deeper research needed

### Phase 2: KAN Architecture and Sparse Training

**Rationale:** The core thesis contribution. Must produce a reliably sparse KAN before symbolic extraction is possible. This phase is iterative — get the sparsification working before attempting any symbolic matching.
**Delivers:** Trained sparse pykan model with 80%+ edges pruned; loss curves and sparsity metrics; feature importance ranking from first-layer edge magnitudes; checkpointing tested at scale.
**Addresses:** TS-1 (KAN implementation), TS-2 (composite regularization), TS-4 (network pruning)
**Avoids:** Pitfall 1 (spline grid range mismatch — set `grid_range=[-5,5]`), Pitfall 4 (KAN overfitting to noise — progressive grid refinement, validation loss monitoring)
**Stack:** pykan 0.2.8, PyTorch (pykan backend), Modal GPU
**Research flag:** Needs attention — progressive sparsification schedule (lamb values and epoch counts) requires empirical tuning specific to the ERCOT dataset; the reference paper used JAX not pykan so hyperparameters from the paper do not transfer directly

### Phase 3: Symbolic Expression Extraction

**Rationale:** The "SR" in KAN-SR. Once sparse KAN is working, this phase transforms it into the thesis deliverable: closed-form equations. This is the highest technical risk phase because real-world noisy data may not produce clean symbolic fits.
**Delivers:** At least one symbolic formula for ERCOT load prediction; per-edge R-squared report; formula complexity metrics (AST depth, operator count); SymPy expression for LaTeX rendering.
**Addresses:** TS-3 (symbolic extraction), TS-9 (visualization — formula display, activation plots, KAN topology)
**Avoids:** Pitfall 2 (two-stage error accumulation — interleaved fixing, strict R-squared thresholds, constant re-optimization against raw data), Pitfall 6 (symbolic library design — physics-informed library with x^3, exp(-ax))
**Stack:** pykan `auto_symbolic`/`suggest_symbolic`, SymPy >=1.12, scipy.optimize for constant re-optimization
**Research flag:** Needs deeper research — real-world energy data symbolic extraction is novel; most KAN-SR examples use clean physics benchmarks (Feynman database); results on noisy data are uncertain

### Phase 4: Baselines and Parallel Evaluation

**Rationale:** Academic rigor requires comparison. PySR and DL baselines can start as soon as data is ready (parallel with Phase 2), but this phase consolidates evaluation after KAN-SR extraction is complete. The Pareto front comparison is the thesis's core result.
**Delivers:** PySR Pareto frontier for ERCOT; LSTM and MLP accuracy benchmarks; multi-dimensional evaluation table (RMSE/MAE/R2, complexity, training time); Pareto frontier comparison plot (KAN-SR vs PySR); per-season accuracy breakdown.
**Addresses:** TS-5 (PySR baseline), TS-6 (DL baselines), TS-7 (evaluation framework), D-8 (partial derivative sensitivity), D-7 (physical interpretation)
**Avoids:** Technical debt of skipping baselines; RMSE-only evaluation; non-chronological test set
**Stack:** PySR 1.5.9 (separate job/environment), scikit-learn metrics, Matplotlib, SymPy symbolic differentiation
**Research flag:** PySR hyperparameter tuning for energy data — standard patterns exist via PySR's official tuning guide but ERCOT-specific settings need validation

### Phase 5: Differentiators (If Time Allows)

**Rationale:** These features elevate the thesis from "adequate" to "excellent." Ranked by impact-to-effort ratio based on FEATURES.md analysis. Each sub-item is independent and can be dropped if time runs short.
**Delivers (in priority order):**
  - D-6: Ablation study (disable each regularization component, compare formula quality) — low effort, required to demonstrate method understanding
  - D-3: MultKAN with multiplication nodes (pykan's MultKAN class) — enables P=0.5*rho*A*v^3 discovery
  - D-1: PIKAN physics constraints — curriculum learning approach; even one constraint (solar=0 at night) is publishable
**Addresses:** D-6, D-3, D-1
**Avoids:** Pitfall 3 (PIKAN loss imbalance — curriculum learning required), anti-pattern 5 (PIKAN from epoch 0)
**Research flag:** D-1 (PIKAN) needs deeper research — physics constraint formulation for load forecasting coupling is novel and untested per FEATURES.md; the swing equation from the research plan may be overengineered for zone-level load

### Phase Ordering Rationale

- Phase 1 before all others: temporal leakage and missing infrastructure are unrecoverable if discovered after training
- Phase 2 before Phase 3: symbolic extraction is meaningless on a dense KAN; 80%+ pruning ratio is a hard prerequisite
- Phase 4 can partially overlap Phase 2 (PySR and DL baselines only need the data pipeline); full evaluation consolidation happens after Phase 3
- Phase 5 is explicitly deferred: thesis is defensible at Phase 4 completion; Phase 5 features make it excellent
- Avoid combining KAN training (Phase 2) and PIKAN (Phase 5) in the same run early on — only integrate physics loss after the baseline symbolic extraction works

### Research Flags

Phases likely needing deeper research (`/gsd:research-phase`) during planning:
- **Phase 2:** Sparsification hyperparameter schedule for real ERCOT data — no direct pykan precedent on noisy energy data; the KAN-SR paper's hyperparameters are for JAX-based Fast-KAN on SRSD benchmarks
- **Phase 3:** Symbolic extraction quality on real-world noisy time series — most published KAN-SR results use clean Feynman physics datasets; energy data is messier
- **Phase 5 (D-1, PIKAN):** Physics constraint formulation — what specific DAE or ODE constraints are appropriate for zone-level wind-solar-load coupling; the swing equation may be wrong level of abstraction

Phases with standard patterns (skip research-phase):
- **Phase 1:** ARPA-E PERFORM has official GitHub docs; HDF5 + pandas data pipeline is standard; chronological splitting is well-documented for time series
- **Phase 4:** PySR has official tuning guide; LSTM/MLP baselines are standard; scikit-learn metrics are universal

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | pykan is well-documented but slow; the reference architecture (JAX+Equinox) has no public code; KAN-SR paper confirms the approach works but replication involves uncertainty |
| Features | HIGH | All 10 table-stakes features are confirmed necessary by multiple independent sources (KAN paper, pykan docs, energy forecasting literature); differentiator features are identified but their effectiveness on real data is uncertain |
| Architecture | MEDIUM-HIGH | Five-stage pipeline is clear and well-supported; component boundaries are well-defined; pykan API is documented; uncertainty is in how well real ERCOT data will cooperate with the pipeline |
| Pitfalls | HIGH | Pitfalls are well-documented from pykan GitHub issues, academic critiques, and PIKAN literature; most are known failure modes with documented solutions |

**Overall confidence:** MEDIUM

### Gaps to Address

- **KAN-SR code unavailability:** The reference paper (arXiv:2509.10089) has no public code. Implementation must be inferred from paper description. Clarify during Phase 2 whether pykan's built-in pipeline sufficiently reproduces the paper's approach, or whether a JAX reimplementation is required.
- **Real-data symbolic extraction quality:** All KAN-SR benchmarks in the literature use clean physics equations (Feynman SR dataset). Performance on noisy real-world wind-solar data is genuinely unknown. Set realistic expectations early — a partial symbolic formula with physical terms identified is a valid thesis contribution even if not a perfect closed-form equation.
- **PIKAN constraint formulation:** The research plan mentions the swing equation for generator dynamics, but the ARPA-E PERFORM data is at ISO zone level (aggregate load/generation), not individual generator level. The appropriate physics constraints for this data are simpler (energy balance, monotonicity, boundary conditions). Validate constraint choice before implementing PIKAN.
- **JAX version compatibility:** If pursuing the JAX path, verify JAX/jaxlib versions inside your container/runtime before committing to an implementation.

## Sources

### Primary (HIGH confidence)
- [KAN-SR: A KAN Guided Symbolic Regression Framework (arXiv:2509.10089)](https://arxiv.org/abs/2509.10089) — reference architecture for the entire project
- [KAN: Kolmogorov-Arnold Networks — ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/afaed89642ea100935e39d39a4da602c-Paper-Conference.pdf) — canonical KAN architecture, training details
- [PyKAN GitHub (KindXiaoming/pykan)](https://github.com/KindXiaoming/pykan) — official implementation, symbolic regression API
- [PyKAN Documentation](https://kindxiaoming.github.io/pykan/) — API reference for `auto_symbolic`, `suggest_symbolic`, `symbolic_formula`
- [PySR GitHub (MilesCranmer/PySR)](https://github.com/MilesCranmer/PySR) — GP-SR baseline, Pareto frontier API
- [ARPA-E PERFORM Datasets (NREL/OEDI)](https://data.openei.org/submissions/5772) — primary dataset documentation
- [ARPA-E PERFORM AWS Registry](https://registry.opendata.aws/arpa-e-perform/) — S3 data access
- [PIKAN for Power System Dynamics (arXiv:2408.06650)](https://arxiv.org/abs/2408.06650) — physics-informed KAN for energy systems
- [Opening the AI Black-Box: KAN-SR for Energy Applications (arXiv:2504.03913)](https://arxiv.org/abs/2504.03913) — direct domain application evidence
- [Kolmogorov-Arnold Networks Meet Science (Phys. Rev. X, Dec 2025)](https://link.aps.org/doi/10.1103/4t7t-v19l) — MultKAN and scientific application patterns
- [pykan GitHub Issues](https://github.com/KindXiaoming/pykan/issues) — practitioner-reported bugs and pitfalls
- [PySR Tuning Guide](https://astroautomata.com/PySR/tuning/) — tuning guidance (populations, batching, resource tradeoffs)

### Secondary (MEDIUM confidence)
- [KAN-SR Critical Assessment (arXiv:2407.11075)](https://arxiv.org/abs/2407.11075) — identifies training instabilities and computational overhead
- [S2KAN (arXiv:2512.07875)](https://arxiv.org/abs/2512.07875) — softly symbolifying KANs, recent improvements
- [From PINNs to PIKANs (arXiv:2410.13228)](https://arxiv.org/html/2410.13228v1) — PIKAN training challenges and loss balancing
- [Fundamental Flaws of PINNs in Engineering Systems](https://www.sciencedirect.com/article/pii/S0360835225008502) — physics loss gradient imbalance pathologies
- [Free-Knots KAN: Spline Stability Analysis (arXiv:2501.09283)](https://arxiv.org/html/2501.09283) — spline instability root causes
- [KANMTS: KAN for Multivariate Time Series (Nature, 2025)](https://www.nature.com/articles/s41598-025-07654-7) — KAN time series forecasting precedent
- [Equinox Docs](https://docs.kidger.site/equinox/) — JAX neural network library (fallback stack)
- [Optimistix Docs](https://docs.kidger.site/optimistix/) — nonlinear solvers for symbolic matching

### Tertiary (LOW confidence — needs validation)
- KAN-SR code availability: paper does not link a public repository; contact authors or reimplement from description
- JAX 0.8.0 availability on managed notebook environments: reported but not independently verified
- J-PIKAN (Jacobi polynomial PIKAN): code pending release at github.com/xgxgnpu/J-PIKAN

---
*Research completed: 2026-02-24*
*Ready for roadmap: yes*
