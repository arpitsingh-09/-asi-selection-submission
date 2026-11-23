# Independent S1 pair review — Reviewer B

## Purpose and independence

Review the 122 anchor/candidate pairs in `reviewer_B.jsonl` independently. You must be a real human, independent of the original E1 question author and of the other reviewer. Do not use model predictions, ask an AI to make judgments, or consult the other reviewer's answers. The package contains no model predictions or proposed relation labels.

## What to assess for each row

- Read `anchor`, `candidate`, and the source paper information in `source_context`.
- Judge whether the two texts express the same scientific question, based on meaning rather than wording overlap.
- Check whether the pair's source alignment is supported by the supplied source context/paper. Use the URL and paper identity when needed; record the evidence you checked in `rationale`.
- If evidence is insufficient or you are uncertain, leave the relevant judgment `null`. Do not guess. Unresolved rows do not count as consensus.
- `source_context.paper_first_posted` is a paper publication date. It is not the creation or availability date of the question.

## Fill these reviewer fields in every assessed row

- `reviewer_id`: your stable reviewer identifier, distinct from the other reviewer and original author.
- `reviewer_kind`: set to the literal string `human` only if you personally made the assessment.
- `independent_of_author`: set to JSON `true` only if you are independent of the original E1 author; otherwise use `false`.
- `same_question`: JSON `true` if the anchor and candidate have the same scientific meaning; `false` if they ask materially different questions; `null` if unresolved.
- `source_alignment_verified`: JSON `true` only if you verified the source alignment; `false` if you checked and found it does not align; `null` if unresolved.
- `rationale`: concise, specific reasoning and source evidence checked. Use `null` only if the judgment is unresolved.
- `reviewed_at`: actual review completion time in ISO-8601 with timezone, for example `2026-11-19T16:30:00+05:30`. Do not backdate.

## Preserve the packet

Do not change `pair_id`, `pair_sha256`, `anchor`, `candidate`, or any value inside `source_context`. Keep all 122 rows, their order, and one JSON object per line. Do not add/remove rows or rewrite pair text. Make a separate completed copy named `reviewer_B_completed.jsonl`; keep the supplied blank `reviewer_B.jsonl` unchanged. Do not copy the example row into the completed file.

## Example format

`example_format.jsonl` shows the JSONL field shape only. It uses placeholders and null judgments, contains no expected answer, and must not be imported or copied into your review. Review judgments and independence attestations are your responsibility. The import checker validates structure but cannot authenticate a reviewer's identity.

Two independent reviewers must agree on the same-question decision and both confirm source alignment for a pair to reach reviewer consensus. Disagreement, unverified alignment, or unknown judgments remain unresolved. Even completed reviews do not by themselves establish question dates, original input IDs/versions, shuffled inputs, a valid decoy, model cutoff, or eligibility for the original registered S1 evaluation.
