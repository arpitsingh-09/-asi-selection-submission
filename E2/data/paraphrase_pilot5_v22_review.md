# E2 Paraphrase Pilot — v22 Review Note

Date: 2026-10-26
Input: E2/data/paraphrase_pilot5_v21.jsonl
Output: E2/data/paraphrase_pilot5_v22.jsonl

## Provenance and integrity
- Five records retained in their original order.
- Paper IDs and record order verified unchanged.
- Only `candidate_abstract` changed, for `2012.14359v1`.
- All other fields were verified unchanged relative to v21.
- Earlier JSONL versions and review notes are preserved.
- All `manual_validation_status` fields remain `not_reviewed`.
- All `scoring_authorized` fields remain `false`.
- No scoring was run.
- `E2/data/scoring_results.jsonl` was not modified.

## Paper 1 — 2012.14359v1
The candidate abstract was revised to retain the source's claim that the framework integrates state-of-the-art visual computing.

A comparison with the source abstract found that the candidate retains the principal claims concerning:
1. The need for systematically integrating vision and semantics for visual sensemaking in autonomous driving.
2. A formally specified and implemented neurosymbolic online sensemaking method using answer set programming (ASP).
3. Integration of state-of-the-art visual computing in a modular framework for hybrid architectures supporting real-time perception and control.
4. Evaluation using KITTIMOD, MOT-2017, and MOT-2020.
5. Human-centred sensemaking, including semantic representation, explainability, question-answering, and commonsense interpolation in safety-critical driving.
6. The framework's domain independence and autonomous driving as an exemplar application.

The candidate title is shorter than the source title and omits its explicit reference to integrating vision and semantics. The candidate abstract retains this central concept. This title assessment is provisional.

These observations are a manual source-text comparison, not a final validation decision.

## Provisional review status
- Paper 1: principal abstract claims appear preserved; title assessment requires consideration during final checklist review.
- Papers 2–5: no changes were made in v22; their earlier provisional assessments are not final validation decisions.
- No `accept`, `revise`, or `reject` decision is recorded by this note.

## Remaining validation work
- Complete and record the manual semantic-preservation checklist for all five records.
- Verify claims, methods, datasets, named components, relationships, and conclusion strength against each source.
- Record explicit final accept/revise/reject decisions only after the checklist is complete.
- Keep all validation statuses unchanged until the required review and authorization steps are satisfied.
- Do not enable scoring without completed validation decisions and the required authorization.
- Do not modify `E2/data/scoring_results.jsonl` during this review.
- Lexical similarity is not proof of semantic preservation.
