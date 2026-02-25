# Architecture Patterns

**Domain:** KAN-SR Symbolic Regression for Wind-Solar-Load Forecasting
**Researched:** 2026-02-24

## Recommended Architecture

The KAN-SR wind-solar-load forecasting system is a **five-stage pipeline** that transforms raw multimodal energy data into interpretable closed-form mathematical equations. Each stage has clear boundaries, well-defined inputs/outputs, and can be independently developed and tested.

```
+-------------------+     +-------------------+     +-------------------+
|  1. DATA PIPELINE |---->| 2. KAN NETWORK    |---->| 3. SR EXTRACTION  |
|                   |     |    TRAINING        |     |    PIPELINE       |
| Raw HDF5 data     |     | Sparse KAN with   |     | Spline-to-symbol  |
| Feature eng.      |     | composite reg.     |     | matching          |
| Normalization     |     | Pruning & refit    |     | Simplification    |
+-------------------+     +-------------------+     +-------------------+
                                    |                         |
                                    v                         v
                          +-------------------+     +-------------------+
                          | 4. PIKAN PHYSICS  |     | 5. EVALUATION &   |
                          |    CONSTRAINT     |     |    BENCHMARKING   |
                          |                   |     |                   |
                          | DAE residual loss |     | KAN-SR vs PySR    |
                          | Energy conserv.   |     | Pareto frontier   |
                          | Boundary enforce. |     | Physical validity |
                          +-------------------+     +-------------------+
```

### Component Boundaries

| Component | Responsibility | Communicates With | Input | Output |
|-----------|---------------|-------------------|-------|--------|
| **Data Pipeline** | Ingestion, cleaning, feature engineering, normalization, train/val/test split | KAN Network (provides tensors), Evaluation (provides test data) | Raw HDF5 files from ARPA-E PERFORM S3 bucket | Normalized feature tensors, cyclic-encoded time features, lag features |
| **KAN Network** | Architecture init, composite regularized training, sparsification, pruning, grid refinement | Data Pipeline (receives tensors), SR Extraction (provides trained sparse network), PIKAN (shares architecture) | Feature tensors `[batch, n_features]` | Trained sparse KAN model with pruned edges, activation function weights |
| **SR Extraction** | Symbolic library matching per edge, algebraic simplification, symmetry/separability detection, constant re-optimization | KAN Network (receives trained model), Evaluation (provides equations) | Sparse KAN with trained spline activations | SymPy closed-form equations, Pareto set of formulas |
| **PIKAN Physics** | Physics loss computation, DAE residual enforcement, derivative constraints, boundary conditions | KAN Network (augments loss function during training) | Physical equations (swing eq., energy conservation), KAN predicted outputs + autodiff derivatives | Physics-augmented loss terms, constrained KAN weights |
| **Evaluation** | Accuracy metrics (RMSE/MAE/R2), complexity scoring (AST depth, operator count), Pareto analysis, PySR baseline comparison | All components (consumes final equations + test data) | Symbolic equations from SR Extraction, PySR baseline equations, test dataset | Metric tables, Pareto frontier plots, physical consistency reports |

### Data Flow

```
[ARPA-E PERFORM HDF5 on AWS S3]
    |
    v
1. DATA PIPELINE
    |-- Download: s3://arpa-e-perform/ via boto3/h5py
    |-- Load: 5-min resolution wind/solar/load for ERCOT/MISO/NYISO/SPP (2017-2019)
    |-- Clean: ANN-based interpolation for missing values (NOT mean fill)
    |-- Feature Engineering:
    |   |-- Meteorological: temperature, GHI, wind_speed, wind_dir, pressure
    |   |-- Astronomical: solar_altitude, solar_azimuth, sunrise/sunset flags
    |   |-- Cyclic encoding: sin/cos transforms for hour, month (preserve periodicity)
    |   |-- Autoregressive lags: P(t-1), P(t-6), P(t-12), ..., P(t-288) for 24h
    |   |-- Cross-coupling: wind_speed^3 (Betz proxy), temp*GHI interaction
    |-- Normalize: Z-score or Min-Max per feature column
    |-- Split: chronological train/val/test (no random shuffle -- time series!)
    |
    v
[Tensor: X shape (N, d_features), y shape (N, 1)]
    |
    v
2. KAN NETWORK TRAINING
    |-- Init: KAN([d_features, hidden_1, hidden_2, 1]) -- keep shallow (1-2 hidden layers)
    |   |-- grid=5 initially (coarse B-splines), k=3 (cubic)
    |-- Phase 2a: Train with composite regularization
    |   |-- Loss = MSE + lambda_1 * L_magnitude + lambda_2 * L_entropy + lambda_3 * L1_weights
    |   |-- Optimizer: AdamW with cosine LR schedule
    |   |-- Monitor: validation loss + sparsity metrics per epoch
    |   |-- Checkpoint every 15 min (job safety)
    |-- Phase 2b: Prune
    |   |-- model.prune() -- remove edges with near-zero activation magnitude
    |   |-- Verify pruned architecture makes structural sense
    |-- Phase 2c: Refit pruned model
    |   |-- Train pruned model with lower lambda (accuracy recovery)
    |   |-- Grid refinement: model.refine(new_grid=10) for finer splines
    |   |-- Retrain on refined grid
    |
    v
[Sparse KAN model: few surviving edges with trained spline activations]
    |
    +----------------+
    |                |
    v                v
3. SR EXTRACTION    4. PIKAN (optional, augments step 2)
    |                |-- Compute autodiff derivatives: d(KAN_output)/dt
    |                |-- Evaluate DAE residual: swing_eq(theta, omega, Pm, Pe)
    |                |-- Add to loss: Loss += lambda_phys * MSE_physics_residual
    |                |-- Boundary: enforce P_solar(night) = 0, P_load >= 0
    |                +-- Returns to step 2 training loop
    |
    |-- For each surviving edge phi_k_i(x_i):
    |   |-- Evaluate spline over effective input range
    |   |-- Fit against symbolic library:
    |   |   {x, x^2, x^3, 1/x, sqrt(x), exp(x), log(x),
    |   |    sin(x), cos(x), tanh(x), abs(x), ...}
    |   |-- Select: min(MSE * 5^complexity) -- complexity-penalized score
    |   |-- Replace spline with symbolic function + fitted params (a,b,c,d)
    |-- Compose: combine per-unit symbolic functions via sum/product
    |-- Simplify: SymPy algebraic simplification
    |-- Detect symmetries: translational (x_i - x_j), multiplicative (x_i * x_j)
    |-- Detect separability: additive f(x_S) + f(x_S_bar), multiplicative f(x_S) * f(x_S_bar)
    |   |-- If separable: recursively solve each subproblem with smaller KAN
    |-- Re-optimize constants: BFGS on final symbolic expression parameters
    |
    v
[SymPy equations: e.g., P_load = a*sin(2*pi*hour/24) + b*temp^2 + c*wind^3 + d]
    |
    v
5. EVALUATION & BENCHMARKING
    |-- Accuracy: RMSE, MAE, R^2 on held-out test set
    |-- Complexity: AST depth, operator count, free parameter count
    |-- Pareto frontier: plot accuracy vs complexity, find knee point
    |-- Physical consistency:
    |   |-- Partial derivatives: dP_load/dT > 0 above cooling threshold
    |   |-- Boundary: P_solar = 0 at night
    |   |-- Conservation: sum of loads ~ sum of generation
    |-- PySR baseline: run PySR on same features, compare Pareto fronts
    |-- Computational: training time (GPU-hours), inference latency (ms)
    |-- Visualization: equation heatmaps, activation plots, formula display
```

## Component Design Details

### Component 1: Data Pipeline

**Technology:** Python, h5py, pandas, numpy, scikit-learn

```python
# Core data pipeline structure
class DataPipeline:
    """Handles ARPA-E PERFORM data from raw HDF5 to model-ready tensors."""

    def __init__(self, iso="ERCOT", resolution="5min"):
        self.iso = iso
        self.resolution = resolution

    def download(self, s3_path):
        """Download HDF5 files from s3://arpa-e-perform/"""
        # Uses boto3 with no-sign-request (public data)
        pass

    def load_and_align(self, year):
        """Load wind/solar/load and align timestamps (all UTC)."""
        # h5py for HDF5 reading
        # Apply scale_factor from HDF5 attributes
        # Align to common 5-min index
        pass

    def clean(self, df):
        """Interpolate missing values using spline (not mean fill)."""
        pass

    def engineer_features(self, df):
        """Create meteorological, astronomical, cyclic, lag features."""
        # Cyclic: sin(2*pi*hour/24), cos(2*pi*hour/24)
        # Lags: configurable window sizes
        # Cross terms: wind^3, temp*GHI
        pass

    def normalize(self, df, method="zscore"):
        """Z-score or MinMax normalization. Save scaler for inverse."""
        pass

    def split(self, X, y, train_ratio=0.7, val_ratio=0.15):
        """Chronological split. NO shuffle for time series."""
        pass

    def to_tensors(self, X, y, device="cuda"):
        """Convert to PyTorch tensors on target device."""
        pass
```

**Key design decisions:**
- HDF5 format requires h5py (NOT pandas read directly). Scale factors stored as attributes.
- Chronological split is mandatory -- random split causes data leakage in time series.
- Cyclic encoding (sin/cos) for time features eliminates the need for KAN to rediscover periodicity, saving significant computation.
- Lag features with multiple windows (1-step, 6-step, 12-step, 288-step for 24h at 5-min resolution) capture multi-scale temporal dependencies.

### Component 2: KAN Network

**Technology:** pykan (official KAN library) with PyTorch backend

```python
# Core KAN training structure
from kan import KAN

class KANTrainer:
    """Manages KAN lifecycle: init, train, prune, refine, checkpoint."""

    def __init__(self, width, grid=5, k=3, device="cuda"):
        self.model = KAN(
            width=width,        # e.g., [20, 10, 5, 1]
            grid=grid,          # B-spline grid resolution
            k=k,                # Spline order (3 = cubic)
            device=device,
            symbolic_enabled=True,
        )

    def train_sparse(self, X, y, steps=500, lamb=0.01):
        """Train with composite regularization for sparsity."""
        # lamb controls sparsity strength
        # Gradually increase lamb if network not sparse enough
        self.model.fit(
            {"train_input": X_train, "train_label": y_train,
             "test_input": X_val, "test_label": y_val},
            opt="Adam", lr=1e-3, steps=steps, lamb=lamb,
            lamb_entropy=2.0,  # Entropy regularization weight
        )

    def prune(self):
        """Remove dead edges. Returns pruned model."""
        self.model = self.model.prune()

    def refit(self, X, y, steps=200):
        """Retrain pruned model for accuracy recovery."""
        self.model.fit(..., lamb=0.0, steps=steps)  # No sparsity penalty

    def refine_grid(self, new_grid=10):
        """Increase spline resolution for finer approximation."""
        self.model = self.model.refine(new_grid)

    def checkpoint(self, path):
        """Save model state (critical for long runs)."""
        self.model.saveckpt(path)

    @staticmethod
    def load(path):
        """Resume from checkpoint."""
        return KAN.loadckpt(path)
```

**Key design decisions:**
- Use pykan (KindXiaoming/pykan) because it is the reference implementation with built-in symbolic regression support. Efficient-KAN and Fast-KAN lack the symbolic pipeline.
- Keep architecture shallow: maximum 2 hidden layers. Deeper networks produce ASTs too complex for human interpretation.
- Grid refinement is a two-phase process: train coarse (grid=5) first, then refine (grid=10+) for accuracy. This avoids local optima in high-resolution splines.
- The `lamb` parameter is the single most important hyperparameter. Start at 0.001, increase gradually. Too high = underfitting. Too low = no sparsity.

### Component 3: SR Extraction Pipeline

**Technology:** pykan symbolic API, SymPy, scipy.optimize

```python
class SymbolicExtractor:
    """Extract closed-form equations from trained sparse KAN."""

    def __init__(self, model, library=None):
        self.model = model
        self.library = library or DEFAULT_SYMBOLIC_LIB

    def suggest_all(self):
        """Get symbolic suggestions for each surviving edge."""
        # Uses model.suggest_symbolic(l, i, j) per layer/edge
        # Returns top-k candidates with R^2 scores
        pass

    def auto_symbolic(self, weight_simple=0.5):
        """Automatically fit symbolic functions to all edges."""
        # weight_simple trades accuracy vs simplicity
        # Higher = simpler formulas, lower = better fit
        self.model.auto_symbolic(lib=self.library)

    def fix_symbolic(self, l, i, j, fun_name):
        """Manually assign a symbolic function to an edge."""
        self.model.fix_symbolic(l, i, j, fun_name)

    def extract_formula(self):
        """Get final SymPy expression."""
        formula, variables = self.model.symbolic_formula()
        return formula

    def detect_separability(self, X, y, subsets):
        """Test additive/multiplicative separability."""
        # Fit f_S(x_S) and f_Sbar(x_Sbar) independently
        # Check if y ~ f_S + f_Sbar or y ~ f_S * f_Sbar
        pass

    def reoptimize_constants(self, formula, X, y):
        """BFGS optimization of constants in symbolic formula."""
        # Extract free parameters from SymPy expression
        # Optimize against (X, y) data
        pass
```

**Key design decisions:**
- The symbolic library must include domain-relevant functions: x^3 (Betz law for wind), exp(-x) (exponential decay), sin/cos (diurnal patterns). Add these to SYMBOLIC_LIB if not present.
- `weight_simple` parameter in auto_symbolic is critical: for this project, bias toward simplicity (0.6-0.8) because interpretability > marginal accuracy.
- Separability detection is the "secret weapon" -- if wind and temperature effects are multiplicatively separable, the problem collapses from d-dimensional to two independent low-dimensional problems.

### Component 4: PIKAN Physics Constraints

**Technology:** PyTorch autograd, pykan

```python
class PIKANConstraints:
    """Physics-informed loss terms for KAN training."""

    def __init__(self, model):
        self.model = model

    def energy_conservation_loss(self, P_gen, P_load, P_loss):
        """Sum of generation = load + losses."""
        residual = P_gen - P_load - P_loss
        return torch.mean(residual ** 2)

    def solar_night_constraint(self, P_solar, is_night_mask):
        """Solar power must be zero at night."""
        violation = P_solar[is_night_mask]
        return torch.mean(violation ** 2)

    def monotonicity_constraint(self, model_output, temperature, threshold=25):
        """dP_load/dT > 0 when T > threshold (cooling load increases)."""
        # Use autograd to compute partial derivative
        grad = torch.autograd.grad(model_output, temperature,
                                    create_graph=True)[0]
        hot_mask = temperature > threshold
        violations = torch.relu(-grad[hot_mask])  # Penalize negative gradients
        return torch.mean(violations ** 2)

    def compute_total_physics_loss(self, **kwargs):
        """Weighted sum of all physics constraint violations."""
        loss = 0.0
        loss += self.lambda_energy * self.energy_conservation_loss(...)
        loss += self.lambda_solar * self.solar_night_constraint(...)
        loss += self.lambda_mono * self.monotonicity_constraint(...)
        return loss
```

**Key design decisions:**
- PIKAN constraints are "soft" -- added to loss function, not hard-coded. This allows the model to learn approximate compliance rather than forcing exact satisfaction.
- Start training WITHOUT physics constraints. Add them after the model has learned basic patterns (curriculum learning approach). Otherwise the model struggles to converge.
- The swing equation (from the research plan) is only relevant if modeling generator-level dynamics. For zone/system-level load forecasting, simpler energy balance and monotonicity constraints suffice.

### Component 5: Evaluation & Benchmarking

**Technology:** PySR, scikit-learn metrics, matplotlib, SymPy

```python
class Evaluator:
    """Multi-dimensional evaluation: accuracy, complexity, physics, comparison."""

    def accuracy_metrics(self, y_true, y_pred):
        """RMSE, MAE, R^2."""
        pass

    def complexity_metrics(self, formula):
        """AST depth, operator count, parameter count from SymPy expr."""
        pass

    def pareto_frontier(self, formulas_with_scores):
        """Plot accuracy vs complexity. Identify knee point."""
        pass

    def physical_consistency(self, formula, X_test, feature_names):
        """Check partial derivative signs, boundary conditions."""
        pass

    def run_pysr_baseline(self, X, y, operators=["+","-","*","/","^"]):
        """Run PySR for comparison. Returns Pareto front of equations."""
        from pysr import PySRRegressor
        model = PySRRegressor(
            niterations=100,
            binary_operators=operators,
            unary_operators=["sin", "cos", "exp", "log", "sqrt"],
            populations=30,
            maxsize=30,
        )
        model.fit(X, y)
        return model.equations_

    def compare_pareto_fronts(self, kan_front, pysr_front):
        """Visual comparison of KAN-SR vs PySR Pareto frontiers."""
        pass
```

## Patterns to Follow

### Pattern 1: Checkpoint-Resume Training Loop (Cloud-Critical)

**What:** Save model state every N minutes and at end of each training phase. Resume seamlessly after job interruption.
**When:** Always. Long experiments fail in practice (OOM, timeouts, preemption, transient errors); artifacts must be persisted.

```python
import os, time

CHECKPOINT_DIR = "/vol/checkpoints/kan-sr/"

def train_with_checkpointing(model, data, total_steps, ckpt_interval_min=15):
    """Cloud-safe training loop with periodic checkpointing."""
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    last_ckpt_time = time.time()

    for step in range(total_steps):
        model.train_step(data)

        # Time-based checkpointing (more reliable than step-based)
        if time.time() - last_ckpt_time > ckpt_interval_min * 60:
            ckpt_path = f"{CHECKPOINT_DIR}/model_step_{step}.pt"
            model.saveckpt(ckpt_path)
            # Also save training state: step, optimizer, loss history
            torch.save({
                "step": step,
                "optimizer_state": optimizer.state_dict(),
                "loss_history": loss_history,
                "rng_state": torch.random.get_rng_state(),
            }, f"{CHECKPOINT_DIR}/train_state_{step}.pt")
            last_ckpt_time = time.time()
            print(f"Checkpoint saved at step {step}")
```

### Pattern 2: Progressive Sparsification (Curriculum Regularization)

**What:** Start with weak regularization, gradually increase. This avoids killing useful edges too early.
**When:** During KAN training (Component 2).

```python
def progressive_training(model, X, y, phases):
    """
    phases = [
        {"steps": 200, "lamb": 0.001, "description": "Learn rough patterns"},
        {"steps": 200, "lamb": 0.01,  "description": "Encourage sparsity"},
        {"steps": 100, "lamb": 0.05,  "description": "Aggressive pruning prep"},
    ]
    """
    for phase in phases:
        model.fit(
            {"train_input": X_train, "train_label": y_train,
             "test_input": X_val, "test_label": y_val},
            steps=phase["steps"], lamb=phase["lamb"],
        )
        print(f"Phase: {phase['description']} complete")
    # Prune after progressive training
    model = model.prune()
    # Refit without regularization
    model.fit(..., steps=200, lamb=0.0)
    return model
```

### Pattern 3: Modular Project Architecture (Modal + Local Notebooks)

**What:** Separate concerns across notebooks/scripts, share code via the repo `src/` package, and persist artifacts to cloud storage.
**When:** Project organization.

```
kan-sr-project/
|-- src/
|   |-- __init__.py
|   |-- data_pipeline.py       # Component 1
|   |-- kan_trainer.py          # Component 2
|   |-- symbolic_extractor.py   # Component 3
|   |-- pikan_constraints.py    # Component 4
|   |-- evaluator.py            # Component 5
|   |-- config.py               # Hyperparameters, paths, constants
|
|-- notebooks/                  # Local exploration / plotting
|   |-- 01_data_exploration.ipynb    # EDA, understand PERFORM data
|   |-- 02_data_pipeline.ipynb       # Build & test data pipeline
|   |-- 03_kan_training.ipynb        # Train KAN, visualize sparsification
|   |-- 04_symbolic_extraction.ipynb # Extract formulas, test simplification
|   |-- 05_pikan_physics.ipynb       # Add physics constraints, retrain
|   |-- 06_pysr_baseline.ipynb       # Run PySR comparison
|   |-- 07_evaluation.ipynb          # Full evaluation suite, plots
|
|-- modal_jobs/                 # Modal entrypoints (jobs)
|-- checkpoints/                # Mirrors persistent checkpoints layout
|-- results/                    # Equations, metrics, plots (synced from persistent storage)
|-- data/                       # Optional local cache (truth lives in persistent storage)
```

### Pattern 4: Feature Ablation via KAN Sparsification

**What:** Use KAN's built-in sparsification as automatic feature selection. After training, pruned input edges reveal which features the model considers important.
**When:** After initial KAN training, before symbolic extraction.

```python
def analyze_feature_importance(model, feature_names):
    """Read feature importance from KAN's first layer edge magnitudes."""
    # After training with sparsity, dead input edges = irrelevant features
    # Surviving edges = features the model uses
    model.plot()  # Visual inspection
    # Quantitative: sum activation magnitudes per input dimension
    importance = []
    for i, name in enumerate(feature_names):
        # Sum of absolute activation values across all output neurons
        edge_magnitude = compute_edge_magnitude(model, layer=0, input_idx=i)
        importance.append((name, edge_magnitude))
    importance.sort(key=lambda x: -x[1])
    return importance
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Deep KAN for Interpretability

**What:** Using more than 2 hidden layers in KAN when the goal is symbolic extraction.
**Why bad:** Each layer multiplies the depth of the resulting AST. A [20, 10, 5, 3, 1] KAN produces deeply nested formulas that are unreadable. The whole point of KAN-SR is human-interpretable equations.
**Instead:** Use [d_features, 5-10, 1] or [d_features, 5, 3, 1] maximum. If accuracy is insufficient, increase grid resolution rather than depth.

### Anti-Pattern 2: Random Train/Test Split on Time Series

**What:** Using sklearn's train_test_split with shuffle=True on temporal data.
**Why bad:** Future data leaks into training set. Model sees "tomorrow's weather" while predicting "today's load." Validation metrics become meaninglessly optimistic.
**Instead:** Always use chronological split. Train on 2017-2018, validate on early 2019, test on late 2019.

### Anti-Pattern 3: Symbolic Extraction Before Sufficient Sparsification

**What:** Running auto_symbolic() on a still-dense KAN (many active edges).
**Why bad:** With 50+ active edges, the symbolic library matching produces a massive formula with dozens of terms. This is no more interpretable than the original neural network.
**Instead:** Keep training with increasing lamb until model.plot() shows clearly only a handful of surviving edges. Pruning ratio should be 80%+ before attempting symbolic extraction.

### Anti-Pattern 4: Using Efficient-KAN or Fast-KAN for This Project

**What:** Choosing KAN variants optimized for speed over the original pykan.
**Why bad:** Efficient-KAN and Fast-KAN omit the symbolic regression pipeline entirely (no Symbolic_KANLayer, no suggest_symbolic, no symbolic_formula). They are designed for pure prediction, not equation discovery.
**Instead:** Use KindXiaoming/pykan (the original). Accept the speed penalty -- symbolic extraction is the entire point of this project.

### Anti-Pattern 5: PIKAN Constraints From Epoch 0

**What:** Adding physics loss terms to the training from the very start.
**Why bad:** The untrained KAN outputs random values. Physics residuals computed on random outputs produce massive gradients that destabilize training. The model never learns basic data patterns.
**Instead:** Use curriculum learning: (1) train on data only for 60% of epochs, (2) add physics constraints with small weight, (3) gradually increase physics loss weight.

## Modal Execution Considerations

### Memory Management

| Concern | At 5-min resolution | At hourly aggregation |
|---------|---------------------|-----------------------|
| **Dataset size** | ~105K rows/year per feature (~2GB loaded) | ~8.7K rows/year (~100MB) |
| **KAN training** | GPU selection + batch size control memory; start small and scale | Trivial |
| **PySR baseline** | May need to downsample; PySR is CPU-bound and slow on >50K rows | Feasible directly |
| **Checkpointing** | Save to persistent storage (Modal Volume/S3); ~50MB per checkpoint | ~10MB per checkpoint |

### Job Strategy

| Phase | Estimated Runtime | Job Strategy |
|-------|-------------------|------------------|
| Data download + preprocessing | 30-60 min | One job, persist processed tensors to storage |
| KAN training (sparse) | 2-6 hours | One long job with frequent checkpoints (resume on failure) |
| Symbolic extraction | 10-30 min | Separate short job loading the latest checkpoint |
| PIKAN retraining | 2-4 hours | Separate long job; only after baseline extraction works |
| PySR baseline | 4-12 hours | Dedicated job(s), resource-tuned for RAM/CPU |
| Evaluation + plotting | 30 min | Short job or local notebook reading persisted artifacts |

### Modal Volume Mount Pattern (Conceptual)

```python
import modal

app = modal.App("kan-sr")
volume = modal.Volume.from_name("kan-sr", create_if_missing=True)

# In your Modal functions, mount the volume at /vol and read/write:
# /vol/data, /vol/checkpoints, /vol/results
```

## Build Order (Dependency Graph)

The components must be built in this order due to hard dependencies:

```
Phase 1: Data Pipeline (no dependencies)
    |
    +--> Phase 2: KAN Network Training (requires data pipeline output)
    |       |
    |       +--> Phase 3: SR Extraction (requires trained sparse KAN)
    |       |
    |       +--> Phase 4: PIKAN Constraints (requires working KAN training loop)
    |               |
    |               +--> Retrain KAN with physics (requires both 2 and 4)
    |                       |
    |                       +--> Re-extract symbols (requires retrained model)
    |
    +--> Phase 5a: PySR Baseline (requires data pipeline, independent of KAN)
            |
            +--> Phase 5b: Comparative Evaluation (requires KAN equations + PySR equations)
```

**Critical path:** Data Pipeline --> KAN Training --> SR Extraction --> Evaluation

**Parallel opportunity:** PySR baseline (Phase 5a) can run in parallel with KAN training (Phase 2), since PySR only needs the data pipeline output.

**Recommended build milestones:**
1. **M1 -- Data Ready:** Pipeline loads, cleans, and transforms ARPA-E PERFORM data into tensors. Validated with EDA notebook.
2. **M2 -- KAN Trains:** Model trains on real data, produces loss curves, model.plot() shows sparsification happening. Checkpointing works.
3. **M3 -- First Equation:** At least one symbolic formula extracted from trained KAN. May not be good yet, but the pipeline end-to-end works.
4. **M4 -- Physics-Informed:** PIKAN constraints added, model retrained, new equations extracted. Physical consistency improved.
5. **M5 -- Full Evaluation:** PySR baseline complete, Pareto frontiers compared, all metrics computed, publication-ready plots generated.

## Sources

- [KAN: Kolmogorov-Arnold Networks (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/file/afaed89642ea100935e39d39a4da602c-Paper-Conference.pdf) -- HIGH confidence, official publication
- [KAN-SR: A Kolmogorov-Arnold Network Guided Symbolic Regression Framework](https://arxiv.org/abs/2509.10089) -- MEDIUM confidence, arXiv preprint (Sep 2025)
- [PyKAN Official Documentation](https://kindxiaoming.github.io/pykan/) -- HIGH confidence, official docs
- [PyKAN GitHub Repository](https://github.com/KindXiaoming/pykan) -- HIGH confidence, source code
- [PyKAN DeepWiki API Reference](https://deepwiki.com/KindXiaoming/pykan) -- MEDIUM confidence, third-party docs
- [Physics-Informed KANs for Power System Dynamics (arXiv 2408.06650)](https://arxiv.org/abs/2408.06650) -- MEDIUM confidence, arXiv preprint
- [ARPA-E PERFORM Datasets (NREL)](https://data.openei.org/submissions/5772) -- HIGH confidence, official data source
- [ARPA-E PERFORM GitHub Documentation](https://github.com/PERFORM-Forecasts/documentation) -- HIGH confidence, official docs
- [PySR: High-Performance Symbolic Regression](https://github.com/MilesCranmer/PySR) -- HIGH confidence, official repo
- [Opening the AI black-box: Symbolic regression with KANs for energy applications](https://www.sciencedirect.com/science/article/pii/S2666546825001272) -- MEDIUM confidence, peer-reviewed journal
- [KAN for Solar Radiation and Temperature Forecasting](https://www.sciencedirect.com/science/article/pii/S030626192402227X) -- MEDIUM confidence, peer-reviewed journal
- [KANMTS: Multivariate Time Series Prediction with KAN (Nature, 2025)](https://www.nature.com/articles/s41598-025-07654-7) -- HIGH confidence, Nature Scientific Reports
- [Kolmogorov-Arnold Networks for Time Series: Bridging Predictive Power and Interpretability](https://arxiv.org/html/2406.02496v1) -- MEDIUM confidence, arXiv preprint
- (Removed) Colab-specific checkpointing blog — execution environment is Modal by default in this plan
