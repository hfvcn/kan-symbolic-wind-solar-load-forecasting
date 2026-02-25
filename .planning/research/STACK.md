# Technology Stack

**Project:** KAN-SR Wind-Solar Load Forecasting (Symbolic Regression for Interpretable Prediction)
**Researched:** 2026-02-24
**Overall Stack Confidence:** MEDIUM -- KAN-SR paper (arXiv:2509.10089) provides a clear reference architecture in JAX+Equinox, but its code is not publicly released, so we will need to reimplement core components. PyKAN offers a working symbolic regression pipeline but has severe performance limitations.

---

## Strategic Decision: JAX+Equinox vs PyTorch (pykan)

**Recommendation: Build on JAX+Equinox as the primary framework. Use pykan only for rapid prototyping and sanity checks.**

| Criterion | JAX+Equinox | PyTorch (pykan) |
|-----------|-------------|-----------------|
| Performance | JIT compilation, vmap, automatic vectorization | Orders of magnitude slower than efficient alternatives |
| Symbolic SR pipeline | Must reimplement (KAN-SR paper provides design) | Built-in `auto_symbolic`, `suggest_symbolic` |
| PIKAN support | Natural fit via Diffrax (neural ODEs, autodiff) | Manual implementation required |
| Cloud GPU availability (Modal) | Works out of box via container image | Works out of box via container image |
| Ecosystem maturity | Equinox 0.13.x, Optax 0.2.6, Diffrax 0.7.1 -- actively maintained by Patrick Kidger | pykan 0.2.8 (Nov 2024), sporadic updates, 16k stars but many open issues |
| L-BFGS support | Via Optimistix (modular, composable) | Via torch.optim.LBFGS |
| SymPy integration | sympy2jax 0.0.7 (bidirectional, trainable) | Built-in symbolic_formula() |

**Rationale:** The KAN-SR paper (September 2025, Buhler & Guillen-Gosalbez) -- the most directly relevant academic work for this project -- was built entirely on JAX+Equinox+Optax+Optimistix+Diffrax. This stack provides 3 critical advantages: (1) JIT-compiled KAN training is dramatically faster than pykan, (2) Diffrax provides first-class neural ODE support for PIKAN, and (3) Optimistix provides Levenberg-Marquardt/Gauss-Newton solvers needed for symbolic matching. pykan is useful for early-stage exploration (its `suggest_symbolic`/`auto_symbolic` API works out of the box) but should not be the production framework.

**Confidence: MEDIUM** -- KAN-SR paper verified this stack works; however, since the code is not public, we must reimplement from the paper's description.

---

## Recommended Stack

### Core Deep Learning Framework

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| JAX | >=0.5.2, up to 0.8.0 available | Array computation, JIT, autodiff, vmap | KAN-SR paper's foundation; JIT gives 10-100x speedup over eager PyTorch for spline operations | HIGH |
| Equinox | 0.13.x (latest 0.13.2) | KAN network architecture, PyTree-based neural networks | Patrick Kidger ecosystem; KAN-SR paper uses it; PyTorch-like syntax but fully JAX-compatible; models are just PyTrees | HIGH |
| Optax | 0.2.6 | First-order optimizers (AdamW, learning rate schedules) | Google DeepMind maintained; composable optimizer chains; KAN-SR paper uses it | HIGH |
| Optimistix | 0.0.10 | Nonlinear least-squares (Gauss-Newton, Levenberg-Marquardt) | Critical for symbolic matching step -- curve-fitting spline activations to symbolic library; KAN-SR paper uses it | HIGH |
| Diffrax | 0.7.1 | Neural ODEs/CDEs for PIKAN implementation | First-class neural differential equation support; needed for physics-informed constraints on dynamic systems; KAN-SR paper uses it | HIGH |

### KAN Implementation Strategy

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Custom Fast-KAN (JAX/Equinox) | N/A (self-built) | Core KAN with RBF activations instead of B-splines | KAN-SR paper uses Fast-KAN variant with RSWAF (Reflectional Switch Activation Functions); 5 basis functions per activation suffice; avoids B-spline grid extension issues | MEDIUM |
| pykan | 0.2.8 | Prototyping, validation, symbolic regression reference | Has working `auto_symbolic()`/`suggest_symbolic()` for rapid exploration; use to validate JAX implementation against known behavior; DO NOT use for final training (too slow) | HIGH |
| efficient-kan | latest | Reference for efficient B-spline batching pattern | Key insight: reformulate activation as linear combination of basis functions -> matrix multiplication; adapt this pattern to JAX | MEDIUM |

### Symbolic Regression Baseline

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| PySR | 1.5.9 (stable) or 2.0.0a1 (alpha) | Gold-standard GP-SR baseline for comparison | Academic benchmark standard; Julia backend (SymbolicRegression.jl) is extremely fast; auto-generates Pareto frontier of complexity vs accuracy; scikit-learn compatible API; cited by your research plan as required baseline | HIGH |
| Julia | 1.10+ | PySR backend runtime | Auto-installed by `pysr.install()`; no manual Julia setup needed | HIGH |

### Symbolic Mathematics

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| SymPy | >=1.12 | Symbolic expression manipulation, simplification, LaTeX rendering | Industry standard for Python symbolic math; PySR outputs SymPy expressions; needed for formula simplification and symmetry detection | HIGH |
| sympy2jax | 0.0.7 | Convert SymPy expressions to trainable JAX modules | Bridges PySR output and JAX training; allows gradient-based fine-tuning of discovered symbolic expressions; part of Kidger ecosystem | HIGH |

### Data Handling

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| h5py | >=3.10 | Read ARPA-E PERFORM HDF5 files | PERFORM dataset is distributed as .h5 files on AWS S3; h5py is the standard Python HDF5 interface | HIGH |
| pandas | >=2.0 | Tabular data manipulation, time series alignment | Standard for time series preprocessing; ISO load data from ARPA-E is tabular | HIGH |
| NumPy | >=1.24 | Array operations, feature engineering | Foundation of scientific Python; JAX arrays are drop-in compatible | HIGH |
| boto3 or s3fs | latest | AWS S3 access for ARPA-E data download | PERFORM data hosted at `s3://arpa-e-perform/`; download to persistent storage (Modal Volume and/or S3) before training for reliability | MEDIUM |
| scikit-learn | >=1.3 | Preprocessing (StandardScaler, train/test split), metrics | Z-score normalization, R2/MAE/RMSE metrics; lightweight, universally available | HIGH |

### Visualization

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Matplotlib | >=3.8 | Publication-quality static plots: Pareto fronts, loss curves, KAN topology | Academic standard; required for thesis figures; PySR Pareto front plots use Matplotlib | HIGH |
| Seaborn | >=0.13 | Statistical plots: correlation heatmaps, distribution plots | Built on Matplotlib; cleaner API for statistical visualization | MEDIUM |
| Plotly | >=5.18 | Interactive exploration of Pareto frontiers in Jupyter | Hover over equations on Pareto front to see formula details; useful for development, not final thesis figures | LOW |

### Development Environment

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Modal | N/A | Primary compute environment (cloud GPU + CPU) | Long-running, restartable jobs; environment isolation; persistent Volumes for artifacts; avoids notebook session timeouts | HIGH |
| Jupyter Notebook | N/A | Experiment tracking, inline visualization | Use locally for analysis/plots; heavy training runs on Modal jobs | HIGH |
| Python | >=3.11 | Runtime | Pin Python in Modal image for reproducibility; compatible with PyTorch + PySR toolchain | HIGH |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| DL Framework | JAX+Equinox | PyTorch (pykan) | pykan is orders of magnitude slower; lacks JIT compilation; symbolic branch not parallelized; OK for prototyping only |
| DL Framework | JAX+Equinox | PyTorch (efficient-kan) | Efficient for forward pass but lacks symbolic regression pipeline entirely; no pruning, no `auto_symbolic` |
| KAN Variant | Fast-KAN (RBF-based) | Original B-spline KAN | B-spline grid extension stops training; RBF is smoother and avoids this issue; KAN-SR paper made this choice explicitly |
| KAN Variant | Fast-KAN (RBF-based) | ChebyKAN (Chebyshev polynomials) | Less well-studied for symbolic extraction; polynomial basis can cause Runge phenomenon at edges |
| KAN for Time Series | Custom KAN-SR pipeline | TimeKAN (ICLR 2025) | TimeKAN focuses on forecasting accuracy, not symbolic extraction; does not produce interpretable formulas |
| KAN for Time Series | Custom KAN-SR pipeline | TKAN (Temporal KAN) | Wraps KAN in RNN cells (LSTM/GRU); adds black-box recurrence that defeats interpretability goal |
| SR Baseline | PySR | gplearn | gplearn is unmaintained, much slower, lacks PySR's Julia backend and Pareto optimization |
| SR Baseline | PySR | Operon | C++ backend is fast but Python bindings less mature; PySR has broader academic adoption |
| Optimizer | Optax (AdamW) + Optimistix (L-BFGS) | torch.optim | Optimistix provides modular nonlinear least-squares solvers (Gauss-Newton, LM, Dogleg) composable with trust regions; torch.optim lacks this |
| PIKAN | Custom via Diffrax | NABLA-SciML framework | NABLA-SciML provides tutorials but is a teaching repo, not a production library; better to build directly on Diffrax |
| PIKAN | Custom via Diffrax | J-PIKAN (Jacobi polynomial) | Code not yet released (pending publication); interesting variant but unavailable |
| Visualization | Matplotlib | Plotly only | Thesis requires static publication-quality figures; Plotly is for interactive exploration only |

---

## Installation

```bash
# === Modal / Local Setup ===
# Use these installs in your Modal image and/or local virtualenv.

# Core JAX ecosystem (Patrick Kidger stack)
pip install equinox optax optimistix diffrax sympy2jax jaxtyping

# KAN prototyping (PyTorch-based, for validation only)
pip install pykan

# Symbolic regression baseline
pip install pysr
python -c 'import pysr; pysr.install()'  # Downloads Julia + SymbolicRegression.jl

# Data handling
pip install h5py boto3 s3fs

# Scientific Python (install in your Modal image / local env)
pip install numpy pandas scikit-learn sympy

# Visualization (install in your Modal image / local env)
pip install matplotlib seaborn plotly

# === Local Development (optional) ===
# For local GPU development with CUDA:
pip install jax[cuda12]
# Then same packages as above
```

### Modal Execution Notes

1. **Persistence**: Container local disk is ephemeral; save checkpoints/results to a Modal Volume (and/or S3) during training.
2. **Reproducibility**: Pin Python and key packages in the Modal image; write `pip freeze`/version metadata into each run directory.
3. **Julia for PySR**: First `pysr.install()` download can be slow; cache Julia artifacts within your image build or persistent storage where feasible.
4. **GPU memory**: Start with small/shallow KANs; scale only after the end-to-end pipeline is validated on a small slice of data.
5. **Data movement**: Download `.h5` to a Volume first; avoid repeated downloads per run.

---

## Key Library Version Compatibility Matrix

| Library | Min Version | Tested With | Python | Notes |
|---------|-------------|-------------|--------|-------|
| JAX | 0.5.2 | 0.8.0 | >=3.11 | 0.5+ requires Python 3.11 |
| Equinox | 0.12.0 | 0.13.2 | >=3.10 | Requires JAX 0.4.38+ |
| Optax | 0.2.4 | 0.2.6 | >=3.10 | |
| Optimistix | 0.0.9 | 0.0.10 | >=3.10 | Requires Equinox 0.11.11+ |
| Diffrax | 0.6.2 | 0.7.1 | >=3.10 | |
| sympy2jax | 0.0.7 | 0.0.7 | >=3.7 | Requires Equinox 0.5.3+ |
| pykan | 0.2.8 | 0.2.8 | >=3.9 | Requires PyTorch 2.2.2 |
| PySR | 1.5.9 | 2.0.0a1 | >=3.9 | 2.0.0a1 is alpha; use 1.5.9 for stability |

---

## Architecture-Specific Stack Decisions

### Fast-KAN Implementation (Self-Built)

The KAN-SR paper replaced B-splines with RSWAF (Reflectional Switch Activation Functions):
```
activation(x) = w_i * (s_i - tanh^2((x - c_i) / h_i))
```
where `w_i` is learnable weight, `s_i` is reference activation level, `c_i` is center, `h_i` controls sharpness. Five basis functions per edge activation are sufficient for most target functions.

**Implementation approach**: Build as an Equinox module with `eqx.Module` base class. Each KAN layer stores weights, centers, and sharpness as JAX arrays. Forward pass is a simple matrix multiplication after activation expansion (following efficient-kan's insight).

### Composite Regularization Loss

The training loss combines four terms (per KAN-SR paper):
```
L_total = L_MSE + sum_layers[lambda_0 * (lambda_1 * L_magnitude + lambda_2 * L_entropy + lambda_3 * ||W_base||_1)]
```

- **L_magnitude**: Sum of absolute activation values across input dimensions (sparsity pressure)
- **L_entropy**: Row/column entropy of activation matrix (forces attention concentration)
- **||W_base||_1**: L1 on linear base weights

All implemented as pure JAX functions (jit-compilable).

### Symbolic Matching Pipeline

Sequential stages with early return:
1. Brute-force search over simple multiplicative expressions
2. Single-unit KAN fitting (1 edge, summation or multiplication)
3. Multi-unit single-layer KAN
4. Simplification: detect separabilities and symmetries (AI Feynman-inspired)
5. Deep KAN fitting (if simpler stages fail)

Each stage uses Optimistix's `LevenbergMarquardt` or `GaussNewton` solvers for curve fitting against a symbol library containing: polynomials, trigonometric functions, exponentials, logarithms, and domain-specific forms.

### PIKAN Integration

Physics constraints are embedded via Diffrax:
```python
# Pseudocode for PIKAN loss
def physics_loss(model, t, x):
    # Forward pass through KAN
    y_pred = model(x)
    # Compute dy/dt via JAX autodiff
    dy_dt = jax.grad(model)(x)
    # Physics residual (e.g., energy conservation, swing equation)
    residual = physics_equation(dy_dt, y_pred, x)
    return jnp.mean(residual**2)

total_loss = data_loss + lambda_physics * physics_loss
```

For neural ODE formulations of the dynamic system, Diffrax provides `diffrax.diffeqsolve()` with adjoint methods for backpropagation through the ODE solver.

---

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| TensorFlow/Keras | No KAN support; JAX is strictly superior for scientific computing |
| gplearn | Unmaintained; PySR is the modern successor |
| EQL (Equation Learner) | Gradient explosion with division/exponential operators; superseded by KAN-SR |
| TPSR (Transformer-based SR) | Requires massive pretraining dataset; overkill for this project's scope; poor physics integration |
| Flax/Haiku | Older JAX NN libraries; Equinox is the modern standard (simpler, more Pythonic, actively developed) |
| PyTorch Lightning | Unnecessary abstraction; project is research-focused with custom training loops |
| Weights & Biases | Overkill for thesis project; use simple CSV logging + matplotlib |
| Docker/containers | Modal runs in containers by design; you must define and maintain the image for reproducibility |

---

## Sources

### Primary (HIGH confidence)
- [KAN-SR Paper (arXiv:2509.10089)](https://arxiv.org/html/2509.10089) -- The reference architecture for this project
- [pykan GitHub (KindXiaoming/pykan)](https://github.com/KindXiaoming/pykan) -- Official KAN implementation, v0.2.8
- [PySR GitHub (MilesCranmer/PySR)](https://github.com/MilesCranmer/PySR) -- Symbolic regression baseline
- [Equinox Docs](https://docs.kidger.site/equinox/) -- JAX neural network library
- [Optax GitHub (google-deepmind/optax)](https://github.com/google-deepmind/optax) -- JAX optimizers
- [Optimistix Docs](https://docs.kidger.site/optimistix/) -- Nonlinear solvers
- [Diffrax Docs](https://docs.kidger.site/diffrax/) -- Neural ODE solvers
- [ARPA-E PERFORM (data.openei.org)](https://data.openei.org/submissions/5772) -- Dataset documentation
- [ARPA-E PERFORM AWS Registry](https://registry.opendata.aws/arpa-e-perform/) -- Data access

### Secondary (MEDIUM confidence)
- [efficient-kan GitHub (Blealtan/efficient-kan)](https://github.com/Blealtan/efficient-kan) -- Efficient KAN batching pattern
- [sympy2jax GitHub](https://github.com/patrick-kidger/sympy2jax) -- SymPy to JAX conversion
- [KAN-benchmarking (Jerry-Master)](https://github.com/Jerry-Master/KAN-benchmarking) -- KAN performance benchmarks
- [TimeKAN (ICLR 2025)](https://github.com/huangst21/TimeKAN) -- KAN time series forecasting reference
- [NABLA-SciML](https://github.com/jdtoscano94/Learning-Scientific_Machine_Learning_Residual_Based_Attention_PINNs_PIKANs_DeepONets) -- PIKAN tutorials
- [jaxKAN (JOSS 2025)](https://github.com/srigas/jaxKAN) -- JAX KAN implementation reference
- [JAX Installation Docs](https://docs.jax.dev/en/latest/installation.html) -- JAX version/compatibility info
- (Removed) Colab-specific release notes — compute environment is Modal by default in this plan

### Tertiary (LOW confidence -- needs validation)
- KAN-SR code availability: Paper does not link to a public repository. May need to contact authors (Buhler, Guillen-Gosalbez) or fully reimplement from paper description.
- JAX 0.8.0 availability on managed notebook environments: Reported but not verified firsthand.
- J-PIKAN (Jacobi polynomial PIKAN): Code pending release at github.com/xgxgnpu/J-PIKAN.
