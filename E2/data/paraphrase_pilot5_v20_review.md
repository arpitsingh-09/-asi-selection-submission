# E2 Paraphrase Pilot — v20 Review Note

Date: 2026-10-26
Input: E2/data/paraphrase_pilot5_v19.jsonl
Output: E2/data/paraphrase_pilot5_v20.jsonl

## Provenance and integrity
- Five records retained in the original order.
- Paper IDs unchanged.
- Only `candidate_abstract` changed, for `2012.14359v1` and `2012.14371v3`.
- All other fields were verified unchanged relative to v19.
- v19 and its review note are preserved.
- All `manual_validation_status` fields remain `not_reviewed`.
- All `scoring_authorized` fields remain `false`.
- No scoring was run.

## Revision 1 — 2012.14359v1
The visual-computing sentence was revised to:
"It integrates advances in visual computing into a modular framework designed for general use within hybrid architectures supporting real-time perception and control."

Purpose: keep the claim closer to the supplied source abstract and avoid the stronger wording "state-of-the-art visual-computing methods."

Status: revised; full manual checklist still required.

## Revision 2 — 2012.14371v3
The final theorem description was rewritten to clarify the relationship between Eigenvalue Power Normalization, an order-r tensor, and the stated number of detectors.

Status: wording revised, but technical correctness is UNVERIFIED.
Required follow-up: compare the claim directly with the theorem and definitions in the source paper before acceptance. Do not infer mathematical equivalence from clearer wording alone.

## Provisional recommendations
- `2012.14359v1`: REVISE recommendation remains pending final checklist.
- `2012.14371v3`: REVISE recommendation remains pending source-paper theorem verification.
- `2012.13915v2`: provisional ACCEPT recommendation; checklist not finalized.
- `2012.14271v3`: provisional ACCEPT recommendation; checklist not finalized.
- `2012.14961v1`: provisional ACCEPT recommendation; checklist not finalized.

These are recommendations only, not final validation decisions.

## Authorization safeguards
- Do not change validation statuses without explicit final decisions.
- Do not enable scoring until the validation protocol is completed and the required decisions are explicitly approved.
- Do not modify `E2/data/scoring_results.jsonl` as part of this review.
- Lexical similarity is not evidence of semantic preservation.
