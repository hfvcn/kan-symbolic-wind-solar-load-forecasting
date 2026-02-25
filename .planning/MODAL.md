# Modal Execution Guide (Planning)

This project runs long experiments on **Modal** and syncs artifacts back to **local** for analysis and thesis writing.

## Storage contract (required)

### Volume name

- Default Volume: `kan-sr`
- Override (Modal jobs): `KAN_SR_VOLUME=<volume>`
- Override (sync script): `VOLUME_NAME=<volume>`

### Remote paths

All Modal jobs must write artifacts to the mounted Volume at:

- `/vol/runs/<run_id>/...`

and call `volume.commit()` after writing, otherwise artifacts may not be visible to other jobs or to `modal volume get`.

Recommended `run_id` format:

- `YYYY-MM-DD_HHMMSS_<8hex>`

### Minimal artifacts per run

- `payload.json`: run metadata (hyperparams, versions, seeds)
- `metrics.csv`: append-only metrics log
- `checkpoint/` or `checkpoint.pt`: resume-capable state (model + optimizer)
- `artifacts/`: plots, formulas, tables

## Execution workflow (how to run in practice)

### 1) Preflight smoke test (before real experiments)

- CPU + Volume + retries + fanout:
  - `modal run modal_jobs/smoke_test.py`
- Optional GPU probe (if your workspace has GPU access):
  - `modal run modal_jobs/smoke_test.py --with-gpu`

### 2) Run jobs as separate units

Prefer separate Modal jobs/environments for:

- KAN training (pykan/PyTorch)
- Symbolic extraction (short job loading the latest checkpoint)
- PySR baseline (Julia)
- Evaluation/plotting (short job or local notebook reading artifacts)

Each job should:
- Create a new `run_id`
- Write to `/vol/runs/<run_id>/...`
- Call `volume.commit()` periodically (e.g., every 10–15 min during training)

### 3) Verify artifacts landed in Volume

- `modal volume ls kan-sr /runs`
- `modal volume ls kan-sr /runs/<run_id>`

### 4) Sync artifacts to local

This repo provides a helper script that downloads a run directory into local `runs/` (ignored by git):

- List remote runs:
  - `scripts/sync_from_modal.sh ls`
- Sync latest run:
  - `scripts/sync_from_modal.sh latest`
- Sync a specific run id:
  - `scripts/sync_from_modal.sh <run_id>`

## Isolation note (PyTorch + Julia)

PySR uses Julia bindings; mixing PySR and PyTorch in the same Python process can be fragile.
Prefer separate Modal jobs/environments for:

- KAN training (pykan/PyTorch)
- PySR baseline (Julia)
