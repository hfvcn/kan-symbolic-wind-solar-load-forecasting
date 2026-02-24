# Pitfalls Research

**Domain:** KAN-SR Symbolic Regression for Wind-Solar Load Forecasting
**Researched:** 2026-02-24
**Confidence:** MEDIUM-HIGH (multiple sources cross-validated; some KAN-SR-specific claims rely on limited published work)

## Critical Pitfalls

### Pitfall 1: Spline Grid Range Mismatch Silently Destroys Training

**What goes wrong:**
KAN's B-spline functions are only defined within the configured `grid_range` (default `[-1, 1]`). If input data falls outside this range -- even by a small margin such as `[-1.25, 1.25]` -- the spline activations become undefined, the network fails to achieve sparsity, and training silently produces garbage results without raising an error. This is especially dangerous for hidden layers where latent variable ranges are unbounded even after input normalization.

**Why it happens:**
Practitioners normalize inputs to `[-1, 1]` and assume this is sufficient. But KAN's internal activations (hidden layer outputs) are not bounded by input normalization. During training, activation values drift outside the grid range as weights update, causing extrapolation beyond spline support. The pykan library does not raise warnings when this happens.

**How to avoid:**
- Set `grid_range` conservatively wider than the data range (e.g., `[-3, 3]` or `[-5, 5]`).
- After each training epoch, monitor the actual range of activations at each layer. If any activation exceeds the grid range, extend the grid before continuing.
- Use `model.update_grid_from_samples(x)` periodically to re-anchor the grid to observed data distributions.
- For wind-solar data with extreme weather outliers, add extra grid margin (at least 2x the standard deviation beyond observed extremes).

**Warning signs:**
- Training loss plateaus at a high value despite correct hyperparameters.
- Network fails to become sparse despite strong regularization.
- `auto_symbolic()` returns poor R-squared values for all edges.
- Activation plots show flat or erratic behavior near grid boundaries.

**Phase to address:**
Phase 2 (KAN Architecture and Sparse Training) -- must be validated at network initialization before any serious training begins.

---

### Pitfall 2: Two-Stage Error Accumulation (Spline Fitting then Symbolic Matching)

**What goes wrong:**
KAN-SR is inherently a two-stage process: (1) train a sparse KAN with spline activations, then (2) match each surviving spline edge to a symbolic function from a library. Errors in stage 1 (imperfect spline fit, residual noise capture, suboptimal pruning) propagate and often amplify in stage 2. The symbolic matching step may select the wrong function because the spline curve it is fitting against was already slightly wrong. The composed final expression can diverge significantly from the true underlying equation, especially when multiple layers are stacked.

**Why it happens:**
The spline-to-symbol matching relies on curve similarity (R-squared or MSE between the spline curve and candidate symbolic functions). Even small distortions in the learned spline -- caused by noise in training data, insufficient regularization, or local optima in the spline parameter space -- can shift the best-matching symbol. When you compose wrong symbols across layers, errors multiply. For wind-solar data with inherent measurement noise, this is particularly acute.

**How to avoid:**
- Use the **interleaved symbolic fixing** approach: after each round of training, fix edges whose symbolic match is confident (high R-squared) immediately, then continue training the remaining spline edges. This prevents error from accumulating across all edges simultaneously.
- Set a strict `r2_threshold` in `auto_symbolic()` (e.g., 0.99). Edges below this threshold should remain as splines and be investigated manually.
- After symbolic extraction, always **re-optimize the numerical constants** in the final symbolic expression using nonlinear least-squares (e.g., scipy `curve_fit`) against the original data -- not the KAN predictions.
- Cross-validate extracted formulas against PySR results on the same dataset to detect divergence.

**Warning signs:**
- Large gap between KAN's prediction accuracy (pre-symbolic) and the symbolic formula's accuracy (post-extraction).
- `auto_symbolic()` reports R-squared below 0.95 for multiple edges.
- The extracted formula produces nonsensical predictions on held-out extreme weather events.
- The symbolic formula complexity is unexpectedly high (many nested terms) despite strong pruning.

**Phase to address:**
Phase 3 (Symbolic Expression Extraction) -- the core extraction pipeline must include re-optimization and validation steps.

---

### Pitfall 3: PIKAN Loss Balancing Failure (Physics Loss vs Data Loss Gradient War)

**What goes wrong:**
When integrating physics constraints (PIKAN), the total loss function combines data fitting loss, sparsity regularization loss, AND physics residual loss. These loss components have vastly different magnitudes and gradient scales. In practice, one loss term dominates training while others are effectively ignored. Common failure mode: the physics loss (PDE residual) has gradients 100-1000x larger than the data loss, causing the network to satisfy physics constraints perfectly while fitting the actual data poorly -- or vice versa. The sparsity regularization can also conflict with both.

**Why it happens:**
Physics residual losses involve computing derivatives of the network output (via autodiff), which amplifies gradient magnitudes. The scale mismatch between `MSE_data` (typically 0.001-0.01), `L1_sparsity` (typically 0.1-1.0), and `PDE_residual` (can be 10-1000) creates a pathological optimization landscape. Standard adaptive optimizers like Adam partially compensate but cannot fully resolve the issue. Additionally, B-spline derivative computation in KAN introduces numerical noise that further destabilizes the physics loss gradients.

**How to avoid:**
- Implement **adaptive loss weighting** (e.g., GradNorm or uncertainty-based weighting) that dynamically adjusts the relative weights of data loss, physics loss, and sparsity loss based on gradient magnitudes each epoch.
- Start training with data loss only (no physics constraint) for the first N epochs to establish a reasonable fit, then gradually introduce physics loss with a warmup schedule (linear ramp over 50-100 epochs).
- Normalize each loss component to unit scale before combining. Monitor the ratio of gradient norms for each loss component -- they should remain within 10x of each other.
- For KAN specifically: compute physics derivatives using the symbolic expressions (after partial extraction) rather than autodiff through splines, when possible. Symbolic derivatives are exact and noise-free.

**Warning signs:**
- One loss component decreases while others increase or plateau.
- Training loss oscillates wildly between epochs.
- The network satisfies physics constraints but has poor data fit (or vice versa).
- Gradient norms for different loss components differ by more than 100x.

**Phase to address:**
Phase 3 (PIKAN Integration) -- loss balancing strategy must be designed and tested before combining all loss terms.

---

### Pitfall 4: KAN Overfits to Noise with Misleading High Accuracy

**What goes wrong:**
KANs can fit random noise to extremely high accuracy. With spline activations, the network has enough flexibility to memorize any continuous mapping, including pure noise in the data. For wind-solar forecasting data -- which contains substantial measurement noise from sensors, weather model errors, and stochastic atmospheric processes -- this means the KAN can achieve near-perfect training accuracy while learning noise patterns instead of physical relationships. The subsequent symbolic extraction then produces spurious formulas that encode noise rather than physics.

**Why it happens:**
B-spline activations with fine grids (high grid resolution) can approximate arbitrarily complex functions. Without sufficient regularization, the network exploits this flexibility to fit every data point exactly, including noise. The typical warning sign (training loss much lower than validation loss) may not trigger early enough because KAN's sparsity regularization sometimes masks overfitting in early epochs. Wind-solar data is particularly vulnerable because measurement noise correlates with weather patterns (e.g., sensor errors increase during storms), creating plausible-looking but spurious correlations.

**How to avoid:**
- **Never increase grid resolution beyond 10 initially.** Start with grid size 3-5, achieve sparsity, then selectively refine only after confirming symbolic structure. The pykan pattern of progressive grid refinement (3 -> 5 -> 10 -> 20) should stop at the point where validation loss stops improving.
- Always evaluate on a held-out test set that includes different seasons or weather regimes than the training data. Time-series cross-validation (e.g., walk-forward) is mandatory -- do not use random train/test splits for temporal data.
- Use the `denoise=True` option in PySR benchmarking to compare against denoised results.
- Compute and plot the Pareto front (complexity vs accuracy) early. If accuracy is suspiciously high for very simple formulas, the data may be too easy; if only complex formulas achieve high accuracy, overfitting to noise is likely.

**Warning signs:**
- Training R-squared above 0.99 on noisy real-world weather data (this is almost always overfitting).
- The extracted symbolic formula includes high-frequency oscillatory terms (deeply nested sin/cos) that have no physical justification.
- Performance degrades sharply on data from a different ISO region or a different year.
- The formula complexity on the Pareto front shows no clear "knee" -- accuracy improves linearly with complexity.

**Phase to address:**
Phase 2 (KAN Training) and Phase 4 (Evaluation) -- regularization strategy must be locked before heavy training, and evaluation must test generalization across weather regimes.

---

### Pitfall 5: Colab Resource Ceiling Kills Long Experiments

**What goes wrong:**
Google Colab imposes hard limits: free tier has ~12 GB RAM, ~15 GB GPU VRAM (T4), 90-minute idle timeout, and 12-hour maximum session. KAN training with compound regularization on multi-dimensional wind-solar data is memory-intensive (spline coefficients scale as O(N_edges x grid_size x batch_size)). PySR baseline runs are CPU-only and can consume 80+ GB RAM with default population settings. A typical experimental workflow involves hours of KAN training followed by PySR comparison -- exceeding Colab session limits. Losing training state mid-experiment wastes days of work.

**Why it happens:**
KAN's memory footprint is fundamentally higher than MLPs (approximately 11x more parameters per layer for equivalent connectivity). PySR's evolutionary algorithm maintains large populations in memory (default 80 populations) and cannot use GPU. The two tools cannot easily coexist in the same Colab session due to PyTorch/Julia C binding conflicts (importing torch after juliacall causes segfaults). Researchers often underestimate runtime and start experiments without checkpointing.

**How to avoid:**
- **Separate KAN and PySR into different Colab notebooks/sessions.** Save KAN results (trained model, extracted features, predictions) to Google Drive, then load in a fresh session for PySR.
- For PySR on Colab: set `procs=2` (Colab has 2 CPU cores), `populations=15-20` (not the default 80), and `maxsize=30-40`. Use `batching=True` with `batch_size=50` for large datasets.
- Implement aggressive checkpointing: save KAN model state every 50 epochs to Drive. Use `torch.save()` for model weights and save grid/spline parameters separately.
- For KAN training: start with small networks ([input, 3, 1] not [input, 10, 5, 1]) and small grid sizes. Only scale up after confirming the approach works.
- Import order matters: always `import juliacall` before `import torch` in the same session to avoid segfaults.

**Warning signs:**
- Colab RAM usage exceeds 80% during training (visible in the system monitor).
- Training has been running for >4 hours without checkpoint.
- PySR reports "Killed" or "TaskFailedException" -- this is memory exhaustion.
- Kernel crashes without error message when running PySR after PyTorch code.

**Phase to address:**
Phase 1 (Data Preprocessing and Environment Setup) -- Colab workflow, checkpointing strategy, and resource budgets must be established before any training begins.

---

### Pitfall 6: Symbolic Library Too Narrow or Too Broad

**What goes wrong:**
The symbolic function library used for matching spline activations to closed-form expressions critically determines what formulas KAN-SR can discover. If the library is too narrow (e.g., only polynomials and sin/cos), the system cannot express the true physical relationship even if the KAN learned it correctly as a spline. If the library is too broad (e.g., includes Bessel functions, error functions, Lambert W, etc.), the matching step has too many candidates, leading to spurious matches where exotic functions accidentally fit noise-corrupted splines better than the correct simple function.

**Why it happens:**
Researchers either copy the default pykan library (which includes basic functions but may miss domain-specific ones like power laws `x^3` for Betz limit) or throw in every function they know. The matching algorithm minimizes MSE between the spline curve and candidate functions over the observed data range. Exotic functions with more free parameters will always fit better in-sample, regardless of physical correctness. For wind-solar physics, specific functional forms matter: cubic power laws (wind), exponential temperature decay (PV efficiency), and sinusoidal diurnal cycles are expected, but they must be present in the library without being drowned out by unnecessary alternatives.

**How to avoid:**
- Design the symbolic library with domain physics in mind:
  - **Include:** `x, x^2, x^3, sqrt(x), exp(x), exp(-x), log(x), sin(x), cos(x), tanh(x), 1/x, abs(x), sigmoid(x)`
  - **Explicitly add:** `x^(3/2)` (wind turbine power curves), `exp(-ax)` (thermal decay)
  - **Exclude initially:** Bessel functions, error functions, Lambert W, hypergeometric functions -- only add if simpler functions consistently fail
- Use `r2_threshold=0.98` in matching. If no library function achieves this, the edge likely represents a composite function that should be decomposed across layers rather than force-matched.
- Run matching twice: once with the full library, once with a physics-constrained subset. If results differ, investigate which is more physically plausible.
- Validate against known wind-solar physics: the Betz limit implies cubic wind speed dependence, the NOCT model implies linear-to-quadratic temperature dependence, diurnal patterns imply sin/cos.

**Warning signs:**
- The extracted formula includes exotic functions (Bessel, erf, Lambert W) in a context where simple physics applies.
- Multiple library functions achieve similar R-squared for the same spline edge (ambiguous match).
- The formula fails dimensional analysis or produces wrong units when physical units are tracked.
- PySR discovers a simpler formula than KAN-SR for the same relationship.

**Phase to address:**
Phase 3 (Symbolic Extraction) -- the library must be designed during Phase 2 but validated during extraction.

---

### Pitfall 7: Ignoring Temporal Structure in Data Splitting

**What goes wrong:**
Wind-solar load data is time series with strong autocorrelation, seasonal patterns, and trend components. Using random train/test splits (standard in ML) destroys temporal structure: the model sees "future" data during training and "past" data during testing, producing wildly optimistic accuracy estimates. The extracted symbolic formulas appear to generalize but actually leak future information. When deployed on truly unseen future data, accuracy collapses.

**Why it happens:**
Many symbolic regression tutorials and benchmarks use i.i.d. data (e.g., physics equations evaluated at random points). Researchers applying KAN-SR to time series may follow these tutorials without adapting the data splitting strategy. Additionally, the autoregressive lag features (`P(t-1), P(t-2), ...`) create direct data leakage if train/test boundaries are not handled with proper gap windows.

**How to avoid:**
- Use **strictly chronological splitting**: train on years 2017-2018, validate on first half of 2019, test on second half of 2019 (using ARPA-E PERFORM data).
- Insert a gap between train and test sets equal to the maximum lag window (e.g., if using 24-hour lag features, skip 24 hours between train end and test start).
- For cross-validation, use **expanding window** or **sliding window** time-series CV, never k-fold.
- Report accuracy separately for each season (winter, spring, summer, fall) to detect seasonal bias.
- If KAN-SR achieves R-squared > 0.95 on test data from a different year than training, be cautiously optimistic but verify on a third year or different ISO region.

**Warning signs:**
- Test accuracy is suspiciously close to training accuracy (within 1-2%).
- The formula works perfectly on the test set but fails on data from a different ISO region.
- Removing lag features causes a disproportionately large accuracy drop (suggesting the model is mostly doing autoregressive prediction, not discovering physics).
- Seasonal decomposition shows the formula captures only the dominant annual cycle, not weather-driven deviations.

**Phase to address:**
Phase 1 (Data Preprocessing) -- data splitting strategy must be defined before any model training.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip PySR baseline, only run KAN-SR | Saves 30-50% of experiment time | Cannot claim KAN-SR advantage without baseline; reviewers will reject | Never for the final thesis -- always need PySR comparison |
| Use default pykan hyperparameters | Quick start, no tuning needed | Default grid_range=[-1,1] and regularization weights are for toy problems; will fail on real data | Only for initial "hello world" sanity checks |
| Train one KAN configuration | Saves compute time | Cannot determine if poor results are from the approach or the specific config; no ablation study | Never -- at minimum run 3 seeds x 3 regularization weights |
| Evaluate only on RMSE/MAE | Standard metrics, easy to compare | Misses the entire point of the thesis (interpretability); reviewers expect complexity-accuracy tradeoff analysis | Never -- Pareto front analysis is the thesis contribution |
| Use all features without selection | Lets the model figure it out | KAN with >10 inputs becomes extremely slow and hard to interpret; extracted formulas are unreadable | Only in initial feature importance screening |
| Hardcode loss weights for PIKAN | Simpler implementation | Physics loss may dominate or vanish; results are fragile to data changes | Only for proof-of-concept; must implement adaptive weighting for final results |

## Integration Gotchas

Common mistakes when connecting components of the KAN-SR pipeline.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| PyTorch (pykan) + Julia (PySR) | Importing torch before juliacall causes segfault from C binding conflict | Always import juliacall first, or use separate notebook sessions; save intermediate results to disk |
| KAN training + grid refinement | Calling `update_grid_from_samples()` after `auto_symbolic()` causes NaN errors in `curve2coef` | Complete all symbolic fixing before any grid refinement, or do grid refinement only before symbolic extraction |
| PySR on Colab | Using default `populations=80` exhausts Colab RAM within minutes | Set `procs=2, populations=15, maxsize=35, batching=True, batch_size=50` |
| Periodic encoding + KAN | Feeding raw hour/month integers as features; KAN wastes capacity learning periodicity | Pre-encode time features as sin/cos pairs before KAN input; this is an explicit recommendation in the research plan |
| ARPA-E PERFORM data + feature matrix | Mixing actual measurements with forecast values in the same feature vector without tracking provenance | Separate features into "measured" and "forecast" groups; train and evaluate interpretability on measured features only |
| PIKAN derivative computation | Using numerical finite differences through splines for physics loss | Use PyTorch autograd through the spline computation graph; numerical derivatives add noise that destabilizes physics loss |

## Performance Traps

Patterns that work at small scale but fail as experiments grow.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Large KAN architecture ([in, 20, 10, 5, 1]) | Training takes hours, extracted formulas have 50+ terms, unreadable | Start with [in, 3, 1] or [in, 5, 3, 1]; increase only if underfitting | Anything beyond 2 hidden layers with >5 nodes each |
| Fine spline grid (size > 20) | Training instability (NaN loss), excessive memory, overfitting | Start with grid size 3, increment to 5 then 10 max; only refine specific edges | Grid size > 15 on Colab with >5 features |
| PySR with all features | Runs for hours/days, produces only trivial linear formulas | Pre-select top 5-8 features via KAN feature importance or mutual information | More than 10 input features |
| Saving full training history | Colab Drive fills up, notebook slows down | Save only checkpoints (every 50 epochs) and final model; log metrics to CSV, not in-memory | Training > 500 epochs with grid > 5 |
| Exhaustive symbolic library matching | Matching takes hours, produces spurious exotic function matches | Limit library to 15-20 domain-relevant functions; use R-squared cutoff | Library > 25 functions with > 10 surviving edges |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **KAN training converged:** Loss plateaued, but did you check that the sparsity actually emerged? Plot activation magnitudes -- if all edges have similar magnitude, pruning will be arbitrary. Verify that the entropy loss drove specialization.
- [ ] **Symbolic formula extracted:** `auto_symbolic()` returned formulas, but did you verify R-squared for each edge individually? Edges with R-squared < 0.95 are unreliable. Did you re-optimize constants in the composed formula?
- [ ] **PIKAN physics constraint satisfied:** Physics loss is low, but is the data loss also low? A formula that satisfies physics but does not fit data is useless for forecasting. Check both independently.
- [ ] **PySR baseline completed:** PySR returned a Pareto front, but did you run it long enough? PySR needs 100+ iterations minimum (1000+ recommended). Check if the best equations are still improving at the last iteration.
- [ ] **Evaluation metrics computed:** RMSE and MAE look good, but did you compute them on the chronological test set (not random split)? Did you also compute per-season metrics? Per-ISO-region metrics?
- [ ] **Formula is "interpretable":** The formula is compact, but does it pass physical sanity checks? Does load increase with temperature in summer? Does wind power scale roughly cubically with wind speed? Does solar output go to zero at night?
- [ ] **Pareto front plotted:** You have complexity vs accuracy, but did you include both KAN-SR and PySR results on the same plot? The comparison is the thesis contribution, not either one alone.
- [ ] **Experiment is reproducible:** You got results, but did you save the random seeds, exact hyperparameters, data splits, and pykan/PySR versions? Can you rerun from scratch and get the same formulas?

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Grid range mismatch (silent failure) | LOW | Extend grid_range to [-5, 5], call `update_grid_from_samples()`, retrain from last good checkpoint |
| Two-stage error accumulation | MEDIUM | Re-run symbolic matching with stricter R-squared threshold; manually inspect edges with R-squared < 0.95; try interleaved fixing approach |
| PIKAN loss imbalance | MEDIUM | Freeze physics loss weight, retrain with data loss only for 100 epochs, then gradually re-introduce physics loss with 10x lower weight |
| KAN overfitting to noise | HIGH | Must retrain from scratch with coarser grid (size 3-5) and stronger L1 regularization (lambda_L1 x 10); no shortcut |
| Colab session crash (lost state) | LOW-HIGH | LOW if checkpointed (restore from Drive); HIGH if no checkpoints (restart experiment from scratch) |
| Wrong symbolic library | MEDIUM | Re-run `auto_symbolic()` with corrected library; if interleaved fixing was used, may need to unfix and retrain some edges |
| Temporal data leakage | HIGH | Must redo all experiments with correct chronological splits; all previously reported metrics are invalid |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Spline grid range mismatch | Phase 1 (Setup) + Phase 2 (KAN Training) | Activation range monitoring script runs every training session |
| Two-stage error accumulation | Phase 3 (Symbolic Extraction) | Per-edge R-squared log; pre-vs-post symbolic accuracy gap < 5% |
| PIKAN loss imbalance | Phase 3 (PIKAN Integration) | Gradient norm ratio monitoring; all loss components decrease over training |
| KAN overfitting to noise | Phase 2 (KAN Training) + Phase 4 (Evaluation) | Validation loss tracked; generalization test on different ISO/year |
| Colab resource limits | Phase 1 (Environment Setup) | Checkpointing tested before real experiments; PySR resource budget validated |
| Symbolic library design | Phase 2 (Design) + Phase 3 (Extraction) | Library reviewed against known wind-solar physics before extraction |
| Temporal data leakage | Phase 1 (Data Preprocessing) | Data splitting code reviewed; no future information in training features |
| Ignoring PySR as baseline | Phase 4 (Evaluation) | PySR Pareto front exists and is plotted alongside KAN-SR |
| Skipping ablation studies | Phase 4 (Evaluation) | Minimum 3 seeds, 3 regularization settings documented |
| Formula without physical validation | Phase 4 (Evaluation) | Partial derivatives checked for sign consistency with known physics |

## Sources

- [KAN: Kolmogorov-Arnold Networks - ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/afaed89642ea100935e39d39a4da602c-Paper-Conference.pdf) -- Official KAN paper, grid range and training details [HIGH confidence]
- [Kolmogorov-Arnold Networks: A Critical Assessment](https://arxiv.org/abs/2407.11075) -- Comprehensive critique covering training instability, computational overhead, theoretical disconnects [HIGH confidence]
- [KAN-SR: A Kolmogorov-Arnold Network Guided Symbolic Regression Framework](https://arxiv.org/abs/2509.10089) -- Two-stage pipeline, divide-and-conquer approach [MEDIUM confidence]
- [Opening the Black-Box: Symbolic Regression with KAN for Energy Applications](https://arxiv.org/html/2504.03913v1) -- Energy domain application [MEDIUM confidence]
- [Free-Knots KAN: Analysis of Spline Knots and Advancing Stability](https://arxiv.org/html/2501.09283) -- Spline instability root causes and mitigations [MEDIUM confidence]
- [From PINNs to PIKANs: Recent Advances in Physics-Informed ML](https://arxiv.org/html/2410.13228v1) -- PIKAN training challenges, loss balancing [MEDIUM confidence]
- [Fundamental Flaws of PINNs in Engineering Systems](https://www.sciencedirect.com/science/article/pii/S0360835225008502) -- Physics loss gradient imbalance, convergence pathologies [MEDIUM confidence]
- [pykan GitHub Issues #89, #71, #385, #480, #555](https://github.com/KindXiaoming/pykan/issues) -- Practitioner-reported bugs: NaN after auto_symbolic, grid range failures, reproducibility [HIGH confidence for bug reports]
- [PySR GitHub Issues #61, #424, #764](https://github.com/MilesCranmer/PySR/issues) -- Memory issues, Colab limitations, reproducibility [HIGH confidence for bug reports]
- [PySR Tuning and Workflow Tips](https://astroautomata.com/PySR/tuning/) -- Official guidance on operator constraints, population sizing [HIGH confidence]
- [Contemporary Symbolic Regression Methods and their Relative Performance](https://pmc.ncbi.nlm.nih.gov/articles/PMC11074949/) -- Benchmarking pitfalls, reproducibility issues [MEDIUM confidence]
- [Review of Physics-Informed Neural Networks: Challenges in Loss Function Design](https://www.mdpi.com/2227-7390/13/20/3289) -- Multi-loss optimization pathologies [MEDIUM confidence]

---
*Pitfalls research for: KAN-SR Wind-Solar Load Forecasting (Graduation Design)*
*Researched: 2026-02-24*
