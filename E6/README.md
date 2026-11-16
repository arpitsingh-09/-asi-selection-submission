# E6 submission — incomplete, evidence-preserving snapshot

Use this directory with the repository root. The original requirements are in
`assignment_e6_excerpt_v1.txt`; active methods are in `PREREG.md`, `protocol.md`,
`RESEARCHER_APPROVAL.json`, `config.json`, `evaluation_config.json`,
`question_pipeline_config.json`, and `literature_testbed_config.json`.
Older PRIORITY9/DRAFT notes are historical; the final preregistration record
supersedes them. This snapshot does not claim the full assignment is complete.

## Deliverables and verified status

| Requirement | Included evidence | Status |
|---|---|---|
| Prompts, protocols, frozen settings, scripts | `submission_v1/prompts/`, root `prompts/e6/`, E6 scripts/configurations/tests | Included; preserve root paths for execution |
| All available completed TRAIN generations | `submission_v1/generations.jsonl`; original envelopes and call histories under `runs/priority10_train*` | 750 hypotheses, 125 successful arm cells from 19 sets |
| Failures and missing cells | `submission_v1/failed_generation_cells.jsonl`, `terminal_missing_cells.jsonl` | 8 failed cells plus 7 unresolved set-0007 cells; never zero-imputed |
| Existing evaluation outputs | Original files indexed with SHA-256 in `submission_v1/manifest.json` | Stable evidence included by reference; active TEST deliberately excluded |
| Literature reference extraction | `data/literature_evidence_finalized_v1/` | 100 verified extractions, 20 review packets; not seven-arm experiments |
| Independent source review | `data/literature_reviewer_documents_v1/` | 40 reviews / 280 checks pending; source-component annotations missing |
| Evaluator validation | `data/evaluator_validation_train_v2_finalized/` | 16 responses verified; 6 identity controls correct; 0/10 independent labels; 0/4 validations complete |
| Held-out accuracy | Separate active run; do not rerun or package while active | Pending final results |
| HDR | `data/hdr_scoring_v3/`, `HDR_SCORING.md` | 0/125; denominator/mapping and actual judgments unresolved |
| Twenty-set error analysis | `data/error_analysis_memo_v2/packets/`, review sheet and pending forms | Fixed 10 data + 10 literature cases prepared; 0/20 actual reviews |
| One-page memo | `submission_v1/memo_one_page.md` | Verified cost summaries; outcome conclusions explicitly pending |

The submission manifest indexes stable originals rather than duplicating raw
responses or replacing them. Keep those indexed files, original TRAIN call
histories/envelopes, root prompts, and the source data with the repository.
The generation JSONL uses assignment labels and includes required fields plus
provenance. `tokens_generated` repeats the set/arm workflow charge on its six
hypotheses: deduplicate by `token_accounting_id`; do not sum line costs.

## Reproduction commands

Run from the repository root with the recorded Python environment. Analysis checks
frozen runtime hashes; `error_analysis_memo.py` fails if that environment differs.
These commands are offline and produce new artifacts only:

```sh
# Focused non-inference checks (no TEST launch).
python3 -m unittest discover -s E6/tests -p test_execution_preparation.py
python3 -m unittest discover -s E6/tests -p test_error_analysis_memo.py
python3 -m unittest discover -s E6/tests -p test_assignment_requirements.py

# Reproduce completed-generation export, prompt snapshot and memo in a NEW directory.
python3 E6/package_submission.py --output-dir /tmp/e6-submission-reproduction

# Reverify saved TRAIN evaluator responses; no model calls.
python3 E6/finalize_evaluator_validation.py \
  --source E6/data/evaluator_validation_train_v2 \
  --output-dir /tmp/e6-evaluator-verification

# Reproduce offline descriptive cost summaries and pending-outcome memo.
python3 E6/error_analysis_memo.py --output-dir /tmp/e6-cost-memo
```

Output paths must not already exist. See `data/literature_reviewer_documents_v1/README.md`
for private human-review handoff/ingestion, `HDR_SCORING.md` for genuine HDR input
requirements, and `ERROR_ANALYSIS_AND_MEMO.md` for the completed-artifact index
schema. After final stable evaluations and genuine reviews exist, supply that
index and reviews to `error_analysis_memo.py` in a new output directory.

The inference launcher is `run_confirmatory_test.py`, documented in
`TEST_PHASE_REQUIREMENTS.md`; the heldout_accuracy phase is already running.
Do not invoke it again. No inference command is part of snapshot reproduction.

## Evaluation methodology and limitations

Seven arms: D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled. Six hypotheses per
successful cell, frozen model/decoding/seed and 8192 generated-token workflow cap.
TRAIN-generated sets stay fixed across 501 held-out predictions per arm.
Invalid predictions are incorrect within that denominator; missing generation
remains missing. Historical researcher TEST exposure is disclosed in PREREG.

Literature reconstruction uses source-extracted question/hypothesis targets,
best-similarity and same-question judgments after required human validation.
Fourteen-reference recovery is separate from HDR (feature discovery × relationship
correctness). Historical-question matching, diversity, and question categories
are specified but unavailable scientific outcomes remain pending. The optional
pairwise LLM judge is not reported as a completed experiment.

Report descriptive 95% input-set bootstrap intervals, 10,000 resamples, seed 2026;
use complete input-set pairs for arm contrasts, not hypotheses as replications.
Testbeds remain separate. Existing memo costs include charged failures/shared
preparation and do not establish scientific benefit. No selection benefit,
control success, most-common semantic error, or deployment recommendation can be
claimed yet. Literature seven-arm generations/evaluations and actual end-to-end
human error analysis remain required deliverables; templates are not reviews.

Next: obtain the pending independent reviews while TEST runs. When TEST has
finished, reconcile its stable outputs and missing cells, then build the completed
evaluation index and regenerate the memo/statistics. Literature generation and
scoring still require their applicable gates; no restart or retry is implied.
