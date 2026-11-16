# Exploratory comparison of the two supplied review responses

Both source JSON files are preserved unchanged in `../review_responses/`; SHA-256 hashes and declarations are recorded in `results.json`.
Reviewer 1 (`reviewer_1`, 2026-11-15) declares independence, which was not externally verified. Reviewer 2 (`reviewer_2`, 2026-11-15) declares `independent_review_confirmed=no`; the source is identified as AI-assisted. The supplied JSON files contain no separate provenance field.

## Validation and rating agreement

Both files passed structural validation for all 18 registered question-paper IDs and all six association pairs. All ratings were 0/1/2 and all evidence notes were nonempty. This is exploratory validation only; the two-independent-review gate did not pass.
Exact rating agreement: **17/18 (94.4%)**. Unweighted Cohen's κ: **0.912**; linear-weighted κ: **0.927**. Rating disagreements: 1.

## Association checks

Same-topic decisions agreed on 6/6 checks. Unsupportedness decisions agreed on 6/6. Both decisions jointly agreed on 6/6 association records. There were 0 field-level disagreements across 0 records.

The detailed disagreements are listed in `results.json` and the paired CSV files. Agreement and κ are descriptive for a small set of repeated pairs; they do not establish correctness, independent review, or model performance. No model inference or preregistered V2 scoring was run.

Reproduce from the repository root with `python3 -m M.prospective_grounding.exploratory_evidence.compare_review_responses`.
