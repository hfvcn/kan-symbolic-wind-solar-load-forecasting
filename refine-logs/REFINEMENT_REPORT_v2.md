# Refinement Report (v2 Cycle)

**Problem**: KAN symbolic extraction loses physical variables due to autoregressive dominance
**Initial Approach**: Multi-metric identifiability framework + multiple sweep experiments
**Date**: 2026-03-21
**Rounds**: 4 / 5
**Final Score**: 9.0 / 10
**Final Verdict**: READY

## Problem Anchor
[Verbatim across all rounds]
Extract physically meaningful formulas from KAN net load models. Autoregressive dominance prunes physical variables. Must understand WHY and provide constructive solutions.

## Output Files
- Review summary: `refine-logs/REVIEW_SUMMARY_v2.md`
- Final proposal: `refine-logs/FINAL_PROPOSAL_v2.md`
- Score evolution: `refine-logs/score-history-v2.md`

## Score Evolution

| Round | Problem Fidelity | Method Specificity | Contribution Quality | Frontier Leverage | Feasibility | Validation Focus | Venue Readiness | Overall | Verdict |
|-------|------------------|--------------------|----------------------|-------------------|-------------|------------------|-----------------|---------|---------|
| 1     | 8                | 7                  | 6                    | 7                 | 9           | 8                | 6               | 7.1     | REVISE  |
| 2     | 8                | 8                  | 8                    | 8                 | 9           | 8                | 7               | 8.1     | REVISE  |
| 3     | 9                | 9                  | 8                    | 8                 | 9           | 9                | 8               | 8.6     | REVISE  |
| 4     | 9                | 9                  | 9                    | 9                 | 9           | 9                | 9               | 9.0     | READY   |

## Round-by-Round Review Record

| Round | Main Reviewer Concerns | What Was Changed | Result |
|-------|-------------------------|------------------|--------|
| 1 | Contribution sprawl; overclaimed language; 3 seeds weak | Tightened to 1 claim; softened language; increased seeds; demoted S0 | Resolved |
| 2 | Integration gap (focused→direct); need continuous signal; S3 underspecified | Added Case 4; added edge_count; fully specified S3 | Resolved |
| 3 | Case 4 needs pre-specified rules; endpoint precision | Pre-specified all rules; paired bootstrap; contingency plan | Resolved |

## Final Proposal Snapshot
- **Title**: Autoregressive Shortcut Competition Destroys Symbolic Identifiability — Evidence from KAN Net Load Forecasting
- **Core claim**: Shortcut competition (not irrelevance) is why physical variables are pruned from KAN formulas
- **Key experiment**: S2 blocked-lag intervention with ΔVER measurement (pre-specified rules)
- **Supporting**: S3 task decomposition preserves physical variables
- **Evidence**: 4-act structure (baseline → collapse → mechanism test → constructive solution)

## Method Evolution Highlights
1. **Most important focusing move**: Round 1 → tightened from 4 parallel contributions to 1 dominant mechanism claim
2. **Most important mechanism upgrade**: Round 2 → added Case 4 (direct-task blocking) to close integration gap
3. **Most important specification**: Round 3 → pre-specified decision rules and paired bootstrap protocol

## Pushback / Drift Log
| Round | Reviewer Said | Author Response | Outcome |
|-------|---------------|-----------------|---------|
| 1 | "S0 is engineering hygiene" | Agreed — demoted to appendix | Accepted |
| 1 | "CPI as separate metric is sprawl" | Agreed — absorbed into ΔVER contrast | Accepted |
| 2 | "Focused-teacher evidence doesn't close the loop" | Added Case 4 direct-task blocking | Accepted |
| 2 | "Binary VER is coarse" | Added edge_count as continuous complement | Accepted |
| All | "Do not replace KAN with foundation model" | Agreed — KAN-native is the right approach | No change needed |

## Remaining Weaknesses
1. Single dataset (PERFORM ERCOT) — generalizability untested
2. Seed count moderate (5 for S2, 3 for frozen evidence)
3. Pre-split interpolation leakage — documented limitation, not fixable in timeline
4. S2 outcome uncertain — Case 4 null result is possible (contingency plan exists)
5. S3 composite may not outperform direct KAN on accuracy (but that's not the claim)

## Raw Reviewer Responses

<details>
<summary>Round 1 Review (Score 7.1)</summary>

Contribution Quality (6/10): paper reads as diagnosis + metrics suite + transfer-gap patch + decomposition method. Too many contributions. Fix: one dominant claim, demote S0, simplify CPI.

Venue Readiness (6/10): "causal" and "guarantees" too strong for 3-seed ablation. Fix: rename to interventional, increase seeds, report CIs.

Simplification: Delete S0 from main story; merge metrics; compress to 4 cases.
Modernization: LLM post-hoc for formula canonicalization; retrieval for operator library.
Drift: NONE. Verdict: REVISE.
</details>

<details>
<summary>Round 2 Review (Score 8.1)</summary>

All dimensions improved. Remaining: CRITICAL integration gap (focused→direct), IMPORTANT continuous signal needed, IMPORTANT S3 underspecified.

Simplification: Keep S3 strictly secondary; move TGR to appendix; compress Act 1.
Drift: NONE. Verdict: REVISE.
</details>

<details>
<summary>Round 3 Review (Score 8.6)</summary>

Strong improvement. Remaining: CRITICAL pre-specify Case 4 rules; IMPORTANT endpoint precision; IMPORTANT control protocol.

Simplification: If Case 4 succeeds, demote Cases 1-2 to supporting.
Drift: NONE. Verdict: REVISE.
</details>

<details>
<summary>Round 4 Review (Score 9.0)</summary>

All dimensions at 9. Pre-specified rules sufficient. Design is clean and focused.

Remaining MINOR items: endpoint wording consistency; bootstrap protocol in method section; keep results disciplined.
Drift: NONE. Verdict: READY.
</details>

## Next Steps
- **Immediate**: Execute experiment plan starting with M0 (S3 polish) → M1 (S2 blocking runs)
- **Recommended**: Use `/experiment-plan` to generate detailed execution-ready roadmap from this proposal
- **After experiments**: Paper writing following the 7-chapter structure
