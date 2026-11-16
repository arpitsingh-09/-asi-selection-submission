# Offline error analysis and one-page memo

Implemented and executed `E6/error_analysis_memo.py`. Current deliverables:
`E6/data/error_analysis_memo_v2/`.

- `error_review_sheet.md` and `packets/`: the frozen 20 input sets (10 TRAIN,
  10 literature), each with all seven arms, original evidence, actual available
  generation entries/intermediates, metrics and call-history references/hashes.
- `human_error_review_pending.json`: source-hash-bound forms for one actual
  reviewer per set. Five frozen issue families are blank, not false. Preserve
  unavailable/failed arms with status `missing_not_evaluable`, null issue codes
  and actual notes. For evaluable arms use `reviewed`, actual Boolean codes and
  supporting quotes/explanations for positive codes. Record real reviewer/time
  and complete end-to-end review notes. Software checks attribution, not identity.
- `statistics/`: seven arm summaries and all 21 frozen paired contrasts for each
  required metric family, separately by testbed. Full cohorts are retained (20
  TRAIN and 100 literature), not only the selected error-analysis sample.
- `memo_one_page.md`: 337-word provisional one-page draft. Actual TRAIN generated
  token means/95% CIs are populated; absent primary/secondary outcomes and paired
  benefit/control findings remain pending. No winner or research-agent deployment
  recommendation is invented. Shared preparation is not summed across arms.
- `analysis.json`: runtime/dependency hashes, actual source hashes, full planned
  denominators, completed review count and per-metric analysis provenance.
- `completed_artifact_index_template.json`: explicit completed-output index.

The selected sample is independently checked against the frozen SHA256 ranking
and exact configured IDs. Set 0007 remains selected and missing. Existing failed
cells and raw call histories remain intact. Nineteen existing TRAIN checkpoints
were consumed, with no model/evaluation calls. No evaluation artifact was supplied,
so scientific outcome metrics are unavailable, not zero. Generation costs include
recorded expenditure on failed cells; they measure expenditure, not performance.
One unresolved TRAIN set is excluded from cost means with explicit denominators.

Intervals use the existing frozen analysis implementation: arithmetic means and
paired mean differences, 10,000 resamples, seed 2026, SHA256(seed:replicate) streams
using Python MT19937, 95% linear percentiles, complete-pair contrasts and unadjusted
marginal intervals. Runtime/executable/random/statistics hashes are verified
against the frozen observation before computation. Every reported estimate has
an interval and planned/included/excluded counts. No output is confirmatory.

No running literature extraction directory was scanned or read. Reference
extraction outputs are not scientific seven-arm generation/evaluation results.
Future literature generation and scoring must be supplied explicitly as stable,
completed, hashed artifacts. Accepted index kinds are `generation_checkpoint`,
`train_evaluation`, `literature_reconstruction`, and `secondary`. Each item names
`testbed`, `input_set_id`, `path`, `file_sha256`, and `kind`; secondary artifacts
also name `arm`. Native source checksums and unit identities are checked. Duplicate
or foreign metric records fail. Question types are summarized over complete
unique generated questions within each set, never as independent replications.

Next essential action: perform actual end-to-end review on the fixed packets as
outputs become available; record where decomposition helped/hurt, selection added
value, controls behaved as expected, and how observed errors might be detected.
Current literature arm outputs and scientific evaluation outcomes remain absent;
those parts of the mandatory analysis cannot be represented as complete. Preserve
prior draft records and use a new output directory on each update. Once actual
reviews and completed outcome artifacts exist:

```sh
cd /Users/arpit/asi-selection
python3 E6/error_analysis_memo.py --reviews E6/data/error_reviews_actual.json --artifact-index E6/data/completed_evaluation_index.json --output-dir E6/data/error_analysis_memo_v3
```

The two input filenames above must contain genuine completed evidence; no such
reviews or outcome artifacts were fabricated. Fourteen focused offline tests pass:
seven new error-analysis/memo tests and seven existing statistical-analysis tests.
Frozen settings, failures and set 0007 were preserved; no inference, TEST
execution, literature-process interference, commit or GitHub push occurred.
