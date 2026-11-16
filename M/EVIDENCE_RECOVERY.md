# Local evidence recovery update

Read-only review of the existing ingestion receipt, review outcomes, and generated-question source records; no evaluations or result changes.

## Recovered locally

- Six generated-question records each have a generation timestamp and explicit input-paper IDs with source-record bindings and version dates (`M/data/generated_questions_v1/generated_questions.jsonl`). These establish generation inputs for those records, not independently authored/published question provenance or human validation.
- The local ingestion receipt records 570 genuine review values and 277 exact paper identity links; 9 linked papers have verbatim question candidates.

## Still requires external evidence or human review

- Zero of the 570 reviews have a verified public observation date or are marked usable for fitting (`M/data/ingestion_v2/summary.json`, `review_outcomes.jsonl`). Existing record-version timestamps do not establish when that exact review value became public.
- Zero question-linked labels are usable. Exact paper identity alone does not supply question identity, version-at-posing, or label availability.
- The six generated questions have no independent human question/contrast judgments; same-topic decoys remain unverified or unresolved. Historical E1 question creation dates and original input sets remain unavailable.
- No verified, dated later-community-use labels were recovered for the second quality factor.

## Evaluation eligibility

No registered evaluation became eligible. The consolidated status remains 0/9 completed; no results or frozen protocols were changed.

## Next concrete action

Obtain source-version evidence showing when exact review recommendations became publicly observable and bind those versions to exact question records; separately obtain independent human reviews for the generated question/contrast and decoy judgments. Then rerun the existing eligibility preparation, without relaxing its gates.
