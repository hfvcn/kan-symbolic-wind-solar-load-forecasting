# KAN-SR: Symbolic Regression via Kolmogorov-Arnold Networks for Renewable Energy Forecasting

Interpretable symbolic regression for wind-solar coupled load forecasting using Kolmogorov-Arnold Networks (KAN). This project discovers mathematical relationships between meteorological factors (wind speed, solar irradiance, temperature) and net load changes through a structured decomposition approach.

## Key Contributions

1. **Autoregressive Shortcut Competition**: Discovered and experimentally verified that lag features systematically suppress physical variables during KAN sparsification
2. **VER/FAR Diagnostic Metrics**: Quantitative indicators for measuring physical variable identifiability in symbolic formulas
3. **S3 Structured Decomposition**: A decompose-then-symbolize approach that recovers physical interpretability while maintaining prediction accuracy
4. **Boundary Analysis**: Systematic investigation of wind power's low symbolic identifiability and its non-monotonic horizon dependence

## Project Structure

```
kan-sr/
├── src/                    # Core library
│   ├── config.py           # Centralized configuration
│   ├── data/               # Data pipeline (download, preprocess, derive)
│   ├── kan_sr/             # KAN training, pruning, symbolic extraction
│   ├── models/             # S2KAN architecture variants
│   ├── baselines/          # MLP, LSTM, XGBoost, SARIMAX baselines
│   ├── eval/               # Evaluation metrics, physics mapping, significance tests
│   ├── local/              # Local execution job implementations
│   └── thesis_sweep/       # Experiment protocol framework
├── modal_jobs/             # Modal cloud compute job definitions
├── scripts/                # Utility scripts and experiment submission
├── tests/                  # Unit and integration tests
├── doc/                    # Paper LaTeX source and assets
└── requirements.txt        # Python dependencies
```

## Quick Start

### Prerequisites

- Python >= 3.9
- [Modal](https://modal.com/) account (for cloud training)

### Installation

```bash
git clone https://github.com/hfvcn/graduation-design.git
cd graduation-design
pip install -e ".[dev,modal]"
```

### Data Pipeline (Phase 1)

Downloads ARPA-E PERFORM ERCOT wind/solar/load actuals and generates features:

```bash
modal run modal_jobs/data_pipeline.py --year 2018 --iso ERCOT
```

### Derived Dataset (Phase 1.5)

Generates net load, delta targets, and physics proxy features:

```bash
modal run modal_jobs/derive_dataset.py \
  --source-data-run-id <data_run_id> \
  --horizon-steps 1,6,12,24 \
  --add-physics-proxies \
  --net-load-lag-steps 1,12,48 \
  --degree-base-c 18
```

### KAN Training (Phase 2)

```bash
modal run modal_jobs/kan_train.py \
  --data-run-id <data_run_id> \
  --target delta_net_load_h6 \
  --use-gpu
```

### Symbolic Extraction (Phase 3)

```bash
modal run modal_jobs/kan_symbolic.py \
  --train-run-id <kan_train_run_id> \
  --use-gpu
```

### Baselines (Phase 4)

```bash
# MLP / LSTM
modal run modal_jobs/baseline_torch.py \
  --data-run-id <data_run_id> --model-type mlp --target delta_net_load_h6

# PySR symbolic regression
modal run modal_jobs/pysr_baseline.py \
  --data-run-id <data_run_id> --target delta_net_load_h6
```

### Syncing Results

```bash
# List remote runs
scripts/sync_from_modal.sh ls

# Sync latest run to local runs/ directory
scripts/sync_from_modal.sh latest
```

### Local Evaluation (Phase 5+)

```bash
# Reconstruct absolute predictions from delta
python scripts/reconstruct_predictions.py --run runs/<run_id>

# Generate comparison tables and figures
python scripts/evaluate_runs.py --run runs/<id1> --run runs/<id2>

# S3 structured combination
python scripts/combine_net_load_runs.py \
  --load-run runs/<load_id> \
  --wind-run runs/<wind_id> \
  --solar-run runs/<solar_id> \
  --out-run-id <combo_id>
```

## Experiment Driver

For batch experiments, use the integrated driver:

```bash
# Dry run (print commands without executing)
python scripts/experiment_driver.py --dry-run

# Execute full pipeline
python scripts/experiment_driver.py --execute
```

## Data Source

This project uses the [ARPA-E PERFORM](https://arpa-e.energy.gov/technologies/programs/perform) dataset (public S3 bucket, anonymous access). No API keys required.

## Tests

```bash
pytest tests/
```

## Citation

If you use this code in your research, please cite:

```bibtex
@thesis{kan_sr_2026,
  title={面向符号可解释性的KAN风光耦合负荷预测方法研究},
  author={vfch},
  year={2026},
  school={University},
  type={Bachelor's Thesis}
}
```

## License

[MIT](LICENSE)
