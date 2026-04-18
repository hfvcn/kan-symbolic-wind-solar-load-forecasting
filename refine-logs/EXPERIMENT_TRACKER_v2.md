# Experiment Tracker v2

## Status Overview

| Milestone | Goal | Status | Key Result |
|-----------|------|--------|------------|
| M0: S3 Polish | Complete B5 evidence | **COMPLETE** | Composite skill=0.456, FAR=3/3 all sub-tasks |
| M1: S2 Blocking | Interventional mechanism test | **COMPLETE** | ΔVER=+0.60 (wind), +0.80 (direct) — both CI>0 |
| M2: Analysis | ΔVER bootstrap CI, figures | **COMPLETE** | Both cases SUCCESS per pre-specified rules |
| M3: Paper Writing | Chapters 1-7 | TODO | All evidence ready |

## Completed Blocks

| Block | Claims | Key Evidence | Status |
|-------|--------|-------------|--------|
| B1 | C1 (accuracy) | KAN skill=0.453 > MLP 0.430 > PySR 0.20 | COMPLETE |
| B2 | C2 (collapse) | 9 configs → load-only, VER(physical)=0/9 | COMPLETE |
| B3 | C3 (solar) | VER(GHI)=3/3, FAR=3/3 | COMPLETE |
| B4 | C3 (wind) | Non-monotonic VER across horizons | COMPLETE |
| B5 | C4 (S3) | Composite skill=0.456, FAR=3/3 all sub-tasks | **COMPLETE** |
| B7 | boundary | Solar h=288 failure documented | COMPLETE |
| **B_S2** | **C3 (causal)** | **ΔVER=+0.60 wind, +0.80 direct, CI>0** | **COMPLETE** |

## All Claims Have Evidence

| Claim | Status | Strength |
|-------|--------|----------|
| C1: KAN > MLP > persistence | COMPLETE | High (p=0.0005) |
| C2: Direct extraction collapses | COMPLETE | High (0/9 configs) |
| C3: Identifiability = task structure + competition | **COMPLETE (observational + interventional)** | **Very High** |
| C4: S3 preserves physical variables | COMPLETE | High (FAR=3/3 all sub-tasks) |
| C5: Not from more parameters | COMPLETE | High (budget-matched) |

## What's Ready for Paper Writing

All experimental evidence is frozen. No more runs needed. Proceed to M3.
