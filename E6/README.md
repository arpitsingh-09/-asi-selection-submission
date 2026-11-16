# E6 submission — incomplete, evidence-preserving snapshot

Use this directory with the repository root. The original requirements are in
`assignment_e6_excerpt_v1.txt`; active methods are in `PREREG.md`, `protocol.md`,
`RESEARCHER_APPROVAL.json`, `config.json`, `evaluation_config.json`,
`question_pipeline_config.json`, and `literature_testbed_config.json`.
Older PRIORITY9/DRAFT notes are historical; the final preregistration record
supersedes them. This snapshot does not claim the full assignment is complete.

Current task mapping: see [`COMPLETION_REPORT.md`](COMPLETION_REPORT.md). The
locked HypoBench held-out accuracy phase is complete in the original
repository. Its 19 saved per-set evaluation files are byte-identically copied
under `runs/heldout_accuracy_optimized_v1/`; never restart the runner. Recreate
the accuracy tables from those saved files with
`python3 E6/reproduce_saved_heldout_accuracy.py`.

## Deliverables and verified status

| Requirement | Included evidence | Status |
|---|---|---|
| Prompts, protocols, frozen settings, scripts | `submission_v1/prompts/`, root `prompts/e6/`, E6 scripts/configurations/tests | Included; preserve root paths for execution |
| All available completed TRAIN generations | `submission_v1/generations.jsonl` | 750 hypothesis rows, 125 successful arm cells from 19 data sets; source call envelopes remain in the original repository |
| Failures and missing cells | `submission_v1/failed_generation_cells.jsonl`, `terminal_missing_cells.jsonl` | 8 failed cells plus 7 unresolved set-0007 cells; never zero-imputed |
| Existing evaluation outputs | `runs/heldout_accuracy_optimized_v1/` and `PACKAGING_MANIFEST.json` | 19 completed per-set outputs copied byte-for-byte; request cache and lock not copied |
| Literature reference extraction | `data/literature_evidence_finalized_v1/` | 100 verified extractions, 20 review packets; not seven-arm experiments |
| Independent source review | `data/literature_reviewer_documents_v1/` | 40 reviews / 280 checks pending; source-component annotations missing |
| Evaluator validation | `data/evaluator_validation_train_v2_finalized/` | 16 responses verified; 6 identity controls correct; 0/10 independent labels; 0/4 validations complete |
| Held-out accuracy | `HELDOUT_ACCURACY_REPORT.md`, `runs/heldout_accuracy_optimized_v1/` | Complete for saved data accuracy only: 125 cells, 501 TEST rows each; 15 cells missing |
| HDR | `data/hdr_scoring_v3/`, `HDR_SCORING.md` | 0/125; denominator/mapping and actual judgments unresolved |
| Twenty-set error analysis | `data/error_analysis_memo_v2/packets/`, review sheet and pending forms | Fixed 10 data + 10 literature cases prepared; 0/20 actual reviews |
| One-page memo | `submission_v1/memo_one_page.md` | Updated with saved data findings, baselines/controls, failures, limits, and next test |

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
`TEST_PHASE_REQUIREMENTS.md`. The heldout_accuracy phase is complete and locked;
do not invoke it again. No inference command is part of snapshot reproduction.

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

Next: complete the pending literature target/source reviews and evaluator
validation, then obtain authorization for a separately frozen literature-only
execution if time permits. Do not retry the locked data run or impute its missing
cells. No conclusion about selection or decomposition on literature outcomes is
supported yet.
