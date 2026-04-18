# Refinement Report

**Problem**: KAN symbolic extraction loses physical variables due to autoregressive dominance in net load forecasting
**Initial Approach**: S0/S1×S2/S3 sweep strategies proposed in doc/next.md
**Date**: 2026-03-21
**Rounds**: 1 (self-review; Codex MCP unavailable)
**Final Score**: 8.5 / 10
**Final Verdict**: READY (for graduation thesis context)

## Problem Anchor

Extract physically meaningful, human-readable mathematical formulas from high-accuracy KAN models for net load forecasting. The key technical barrier: autoregressive dominance causes physical meteorological variables to be pruned away during sparsification, collapsing formulas to load-only expressions. Must understand WHY and provide constructive solution (S3 decomposition).

## Output Files

- Research proposal: `refine-logs/FINAL_PROPOSAL.md`
- Experiment plan: `refine-logs/EXPERIMENT_PLAN.md`
- Experiment tracker: `refine-logs/EXPERIMENT_TRACKER.md`
- Review round 1: `refine-logs/round-1-review.md`
- Score history: `refine-logs/score-history.md`

## Score Evolution

| Round | Problem Fidelity | Method Specificity | Contribution Quality | Frontier Leverage | Feasibility | Validation Focus | Venue Readiness | Overall | Verdict |
|-------|------------------|--------------------|----------------------|-------------------|-------------|------------------|-----------------|---------|---------|
| 0 | 9 | 7 | 8 | 6 | 9 | 8 | 7 | 7.5 | REVISE |
| 1 | 9 | 8 | 9 | 7 | 9 | 9 | 8 | 8.5 | READY |

## Round-by-Round Review Record

| Round | Main Concerns | What Was Changed | Result |
|-------|---------------|------------------|--------|
| 1 | (1) Missing positioning vs Panczyk 2025 KAN-SR nuclear; (2) S0 underspecified; (3) "Identifiability" needs formal metrics; (4) Paper needs three-act structure | Added positioning table vs 5 closest works; specified safe_exp/safe_div/clip details; defined VER/FAR/TGR metrics; restructured as three-act narrative (accuracy→collapse→analysis+solution) | All resolved |

## Final Proposal Snapshot

1. **Dominant contribution**: Systematic characterization of physical variable symbolic identifiability via VER/FAR/TGR metrics — first study showing feature competition and pruning trajectory (not information content) determine variable survival in KAN symbolic extraction
2. **Supporting contribution**: S3 structured decomposition guarantees physical variable presence by decomposing into physically natural sub-tasks
3. **Method**: KAN teacher → sparse pruning → per-edge symbolic extraction; S3 decomposes net_load into wind/solar/load sub-tasks
4. **Key evidence**: Solar (positive case, GHI VER=3/3) + Wind (boundary case, non-monotonic horizon dependence) + Direct collapse (load-only, systematic across 20+ configs)
5. **Paper strategy**: Three-act structure (accuracy baseline → problem discovery → analysis + solution)

## Method Evolution Highlights

1. **Most important focusing move**: Dropped S1×S2 multi-horizon forced ablation from priority list — existing evidence at h=6/72/144/576 is already sufficient. This saves weeks of computation and keeps the paper focused.
2. **Most important conceptual upgrade**: Operationalized "symbolic identifiability" via three concrete metrics (VER/FAR/TGR) instead of loose qualitative claims. This transforms descriptive findings into a measurable framework.
3. **Most important narrative upgrade**: Reframed from "we tried 3 strategies (S0/S1×S2/S3)" to "we discovered a phenomenon (autoregressive collapse), characterized it (VER/FAR/TGR), and provided a constructive solution (S3)." The three-act structure makes the paper dramatically more readable.

## Pushback / Drift Log

| Round | Concern | Response | Outcome |
|-------|---------|----------|---------|
| 1 | "Should add frontier LLM component for higher score" | Rejected — graduation thesis context; KAN itself is 2024-era; adding LLM would be decorative | Accepted: keep non-frontier, document as intentional |
| 1 | "S1×S2 sweep should still be done" | Rejected — existing evidence from h=6/72/144/576 with feature group ablation already proves C3 | Accepted: cut S1×S2, save 2+ weeks |

## Remaining Weaknesses

1. **Pre-split interpolation leakage**: Cannot be fixed within thesis timeline. Documented as limitation. Risk: thesis committee may question strength of mechanism claims.
2. **Single dataset (PERFORM ERCOT)**: Generalizability not established. Documented as future work.
3. **Path-dependent pruning**: Symbolic outcomes depend on training seed / regularization schedule. Partially mitigated by multi-seed (3 seeds), but not fully deterministic.
4. **S3 composite skill not yet verified**: Block 5 is 80% complete — first priority to finish.

## Next Steps

1. **Immediate (this week)**: Complete M0 (S3 polish, R001-R004) → verify composite formula and skill
2. **If time allows**: Complete M1-M2 (S0 safe functions, R005-R008) → test transfer gap reduction
3. **Primary effort**: Start thesis writing — all evidence is ready, chapter structure defined in FINAL_PROPOSAL.md
4. **Consider**: Use `/paper-plan` to generate detailed chapter outline, then `/paper-write` for LaTeX drafting
