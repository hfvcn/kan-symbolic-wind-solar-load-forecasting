---
phase: 03-symbolic-expression-extraction
verified: 2026-02-26T06:21:29Z
status: verified
score: "Modal run complete; extracted SymPy/LaTeX formula + per-edge report"
evidence:
  - run_id: 2026-02-26_041718_5579aeeb
    train_run_id: 2026-02-26_035935_74ef1f78
    data_run_id: 2026-02-26_032058_1957fda1
    target: load
    eval_test_rmse: 5021.452405087558
    artifacts:
      - runs/2026-02-26_041718_5579aeeb/artifacts/formula.sympy.txt
      - runs/2026-02-26_041718_5579aeeb/artifacts/formula.tex
      - runs/2026-02-26_041718_5579aeeb/artifacts/formula_eval_test.json
      - runs/2026-02-26_041718_5579aeeb/artifacts/edge_symbolic_report.csv
      - runs/2026-02-26_041718_5579aeeb/artifacts/separability.json
      - runs/2026-02-26_041718_5579aeeb/artifacts/predictions_test.parquet
local_verification:
  - tests/test_symbolic_extraction.py
notes:
  - "Legacy runs may omit payload.phase; evaluation code should infer Phase 03 from artifacts."
---

# Phase 03 Verification

## Verified locally

- `tests/test_symbolic_extraction.py` passes (synthetic function end-to-end extraction).

## Verified via Modal (real data)

- `runs/2026-02-26_041718_5579aeeb/` contains real-data symbolic extraction artifacts:
  - `artifacts/formula.sympy.txt` (SymPy expression)
  - `artifacts/formula.tex` (LaTeX)
  - `artifacts/edge_symbolic_report.csv` (per-edge symbolic matching report)
  - `artifacts/formula_eval_test.json` (formula evaluated on test split)
  - `artifacts/predictions_test.parquet` (y_true/y_pred/residual)
  - `artifacts/separability.json` (Phase 06 separability detector output)
