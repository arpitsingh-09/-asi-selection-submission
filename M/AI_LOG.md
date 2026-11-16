# AI-assisted work record

This record summarizes only work evidenced by files in this repository. Dates and counts are taken from the artifact metadata; it is not a complete conversational transcript.

- The repository disclosure in [AI_USAGE.md](AI_USAGE.md) records the initial Phi implementation and explicitly limits claims to software behavior, not scientific accuracy.
- `training.py`, `prepare_quality_training.py`, and `train_quality_entrypoint.py` implement provenance/date-gated quality-data preparation and training. The recorded review ingestion has 570 recommendation values but zero verified public observation dates and zero usable question-linked labels; therefore no quality model was fit.
- `evaluation.py` provides the nine registered test runners and synthetic-only test path. The consolidated ledger records 0/9 registered evaluations completed and all nine blocked.
- E1/I1 review and provenance workflows retain blank human fields and unresolved status. They do not assert human verification where none is recorded.
- Generated-question development checks are labeled development-only. No heldout M evaluation is recorded in the consolidated summary.

No unrecorded dates, human judgments, model metrics, or experiments are claimed here.

## Supplementary S1 exploratory analysis

- The saved exploratory comparison covers 60 source questions in each of two
  categories. Using exposed E1 data and unverified author-intended labels,
  identity-minus-`B-Q` accuracy was 0.00 (95% CI [0.00, 0.00]) for
  minimal-paraphrase decisions and 0.15 (95% CI [0.0667, 0.25]) for near-miss
  decisions. The joint criterion (both lower bounds >0.02) failed. This does
  not complete original S1; original S1 and A1 remain incomplete. The frozen
  A1 list has 80/80 ineligible candidates. Full saved output:
  `supplementary_s1_e1_exploratory/results/run_001/results.json`.

## Prospective grounding V1/V2 event — 2026-11-15

- **Actual AI/model error caught:** the first V1 qwen3:8b generation attempt
  exhausted the registered 512-token budget in its `thinking` output and
  returned an empty `response` (`done_reason="length"`, `eval_count=512`). The
  V1 CLI rejected and recorded the empty result; the complete raw response and
  failed attempt remain preserved under
  `prospective_grounding/generated_v1/run_20261115T023429_468521Z/`. V1 was
  closed without retry or question substitution.
- V2 was separately preregistered and committed before inference
  (`a87b631bc1b4237e950cbaf8abe4e1e4524cc652`). It used the same locked
  qwen3:8b artifact/settings with `think=false`; four primary/decoy calls
  succeeded and their raw records remain under
  `prospective_grounding/generated_v2/`.
- Codex assisted with implementation, blinded packet preparation, and report
  documentation. V2 independent human review remains pending; no scoring or
  evaluation result is claimed.

## Exploratory V2 review responses — 2026-11-15

- Two supplied review JSON files were copied byte-for-byte into
  `prospective_grounding/exploratory_evidence/review_responses/`; their SHA-256
  hashes are recorded in the comparison `results.json`. The requested `(1)`
  suffixed Downloads names were absent; the corresponding base-named source
  files were used and their exact paths are recorded by the analysis.
- Reviewer 1 (`reviewer_1`) dated the form 2026-11-15 and declared
  `independent_review_confirmed=yes`. This is a self-declaration only; neither
  identity nor independence was externally verified.
- Reviewer 2 (`reviewer_2`) dated the form 2026-11-15 and declared
  `independent_review_confirmed=no`. The supplied file is identified as
  AI-assisted. Its JSON has no dedicated provenance field; this status is
  retained as supplied and is not inferred as independent review.
- The exploratory comparator validated 18 ratings and six association checks
  per response and calculated descriptive agreement. The result does not pass
  V2's two-independent-review requirement. No inference or registered V2
  scoring was run, and no reviewer identity or independence declaration was
  edited.
- Temporal eligibility was not inferred from venue years or bibliographic
  metadata. The saved quality-data review found 570 recommendation values but
  zero eligible question-linked labels with verified public observation dates;
  the quality heads remain unavailable. The supplementary A1 threshold was
  not met, and V1's failed generation remains a failure rather than a usable
  question.
