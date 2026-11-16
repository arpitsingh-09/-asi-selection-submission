# E2 Paraphrase Pilot — v21 Review Note

Date: 2026-10-26
Input: E2/data/paraphrase_pilot5_v20.jsonl
Output: E2/data/paraphrase_pilot5_v21.jsonl

## Provenance and integrity
- Five records retained in their original order.
- Paper IDs unchanged.
- Only `candidate_abstract` changed, for `2012.14371v3`.
- All other fields were verified unchanged relative to v20.
- Earlier JSONL versions and review notes are preserved.
- All `manual_validation_status` fields remain `not_reviewed`.
- All `scoring_authorized` fields remain `false`.
- No scoring was run.

## Paper 2 — 2012.14371v3
The final theorem description was revised to distinguish:
1. The number of detectors, stated as binom(Z*,r).
2. Each detector's association with an r-dimensional subspace.
3. The detector's role in detecting whether a higher-order occurrence is projected into that subspace.

The wording was checked against the extracted source text, particularly the abstract and Section D. This is a source-text comparison, not independent mathematical verification of every assumption in the theorem.

## Remaining validation work
- Complete the manual semantic-preservation checklist for all five records.
- Verify every claim, method, dataset, named component, relationship, and conclusion strength against its source.
- Record explicit final accept/revise/reject decisions only after the checklist is complete.
- Do not treat provisional recommendations as recorded validation decisions.
- Do not enable scoring until validation decisions and authorization requirements are satisfied.
- Do not modify `E2/data/scoring_results.jsonl` during this review.
- Lexical similarity is not proof of semantic preservation.
