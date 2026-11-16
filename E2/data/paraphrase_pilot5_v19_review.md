# E2 Five-Paper Paraphrase Pilot — v19 Review Note

## Purpose
Record the two targeted abstract corrections in v19 and identify the remaining manual-review decisions.

## Artifact integrity
- Source: `E2/data/paraphrase_pilot5_v18.jsonl`
- New version: `E2/data/paraphrase_pilot5_v19.jsonl`
- Records preserved: 5
- Record order and paper IDs: unchanged
- Only changed field: `candidate_abstract`
- Records with abstract edits: `2012.14359v1`, `2012.14371v3`
- All other fields: unchanged
- v18 and its review report: preserved

## Corrections
1. `2012.14359v1`: restored the source abstract's claim that the work demonstrates the need for and potential of integrating vision and semantics.
2. `2012.14371v3`: removed the unsupported-by-abstract wording about suppressing burstiness and the attribution to earlier work. The revised EPN statement still requires careful comparison with the source paper before acceptance.

## Provisional manual-review recommendations
These are recommendations, not recorded validation decisions.

| Paper ID | Recommendation | Reason |
|---|---|---|
| `2012.14359v1` | Review again | Check the revised opening sentence and verify the remaining claims against the source. |
| `2012.14371v3` | Review again | Verify the EPN and tensor-theorem wording against the source paper, not only the abstract. |
| `2012.13915v2` | Consider accept | Candidate appears consistent with the supplied source abstract; complete manual checklist first. |
| `2012.14271v3` | Consider accept | Candidate preserves the four stated contributions; verify the claims and scope manually. |
| `2012.14961v1` | Consider accept | Candidate appears consistent with the supplied source abstract; complete manual checklist first. |

## Authorization and limitations
- `manual_validation_status` remains `not_reviewed` for every record.
- `scoring_authorized` remains `false` for every record.
- No scoring was run.
- `E2/data/scoring_results.jsonl` was not modified by this step.
- These recommendations do not establish semantic preservation or authorize acceptance.
- Lexical similarity diagnostics are not proof of semantic equivalence.
- The validation checklist must be completed before any final decisions or scoring.

## Next step
Manually compare each candidate title and abstract with its source. Record explicit accept/revise/reject decisions only after checking every item in the validation protocol and resolving any uncertain claims.

## Manual review assessments — 2026-10-26

These are provisional recommendations based on comparisons with the supplied source abstracts. They are not final validation decisions.

### Paper 1 — 2012.14359v1
Recommendation: REVISE.
The candidate preserves the main method, ASP, modular framework, benchmarks, and human-centred visual sensemaking claims. Consider revising the visual-computing sentence to stay closer to the source wording. Recheck the complete abstract after revision.

### Paper 2 — 2012.14371v3
Recommendation: REVISE.
The candidate preserves SCK, DCK, SCK(+), experimental categories, and the EPN discussion. The final technical theorem description needs careful verification against the full paper before acceptance. The supplied abstract alone is not sufficient to independently verify the mathematical interpretation.

### Paper 3 — 2012.13915v2
Recommendation: ACCEPT provisionally.
The candidate preserves the motivation, SDOI-SAN, dual-context architecture, Transformer encoder scope, all three evaluation tasks, and reported effectiveness. Complete the formal checklist before recording a final decision.

### Paper 4 — 2012.14271v3
Recommendation: ACCEPT provisionally.
The candidate preserves all four contributions, image-derived context, automatic corpus construction without manual labeling, the benchmark, and the authors' novelty claims. Complete the formal checklist before recording a final decision.

### Paper 5 — 2012.14961v1
Recommendation: ACCEPT provisionally.
The candidate preserves deep one-class classification, Deep Fair SVDD, the adversarial fairness approach, two fairness measures, reported findings, and model analyses. Complete the formal checklist before recording a final decision.

## Status and authorization safeguards
- All five `manual_validation_status` fields remain `not_reviewed`.
- All five `scoring_authorized` fields remain `false`.
- No scoring was run as part of these assessments.
- No changes to `E2/data/scoring_results.jsonl` are authorized by this note.
- Recommendations based on abstract comparison do not establish full semantic equivalence.
- Paper 2's mathematical interpretation requires particular care; verify it against the full paper.
- Final validation decisions require explicit review and approval.
