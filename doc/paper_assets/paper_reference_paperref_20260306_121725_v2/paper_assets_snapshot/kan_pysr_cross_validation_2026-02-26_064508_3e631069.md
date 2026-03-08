# KAN ↔ PySR Cross-Validation Report

- pysr_run: `2026-02-26_064508_3e631069`
- symbolic_run: `2026-02-26_041718_5579aeeb`
- n_seed_features: `5`
- equations_using_seeds: `1` / `8`
- best_equation_uses_seed: `False`

## Seed Features

- `seed_01` (nodes=15, symbols=2): `19508.7226320794*exp(-(1.70862204204506e-5*load_lag_1 + 1.52396460869868e-5*load_lag_12 - 2.57161529466326)**2)`
- `seed_02` (nodes=13, symbols=2): `exp(-(1.70862204204506e-5*load_lag_1 + 1.52396460869868e-5*load_lag_12 - 2.57161529466326)**2)`
- `seed_03` (nodes=12, symbols=2): `-(1.70862204204506e-5*load_lag_1 + 1.52396460869868e-5*load_lag_12 - 2.57161529466326)**2`
- `seed_04` (nodes=10, symbols=2): `(1.70862204204506e-5*load_lag_1 + 1.52396460869868e-5*load_lag_12 - 2.57161529466326)**2`
- `seed_05` (nodes=8, symbols=2): `1.70862204204506e-5*load_lag_1 + 1.52396460869868e-5*load_lag_12 - 2.57161529466326`

## Notes

- Seed usage indicates PySR explicitly selected KAN-derived sub-expressions as building blocks.
- This is evidence for independent cross-checking (EVAL-08), not a proof of causal physics.

