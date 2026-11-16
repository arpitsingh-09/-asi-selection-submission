# Pre-TEST readiness, 2026-11-12

Offline readiness was executed: `E6/data/pre_test_readiness_20261112_v1.json`.
Frozen protocol, researcher approval, runtime evidence, local Git gate, all seven
arms, rubric hashes, source isolation, donor cohorts and terminal TRAIN inventory
pass. No inference was performed.

The schedule retains 20 TRAIN evidence units and 100 literature units, each with
D, QH, QH-sel, QH-rand, HQ, D-empty and D-shuffled (840 planned cells).
19 TRAIN checkpoints contain 125 successful cells and 8 failed cells. Set 0007
has no completed envelope, remains unresolved and is never retried or replaced.
All prior JSON/JSONL histories are file-hash inventoried in the readiness record.

Mandatory outstanding evidence:
- Actual validation of reconstruction, semantic already-asked, diversity and
  question-type evaluators. Frozen statuses remain unchanged.
- Source-bound literature target extraction and actual independent reviews and
  adjudications under Decision 24 (20 reviewed targets).
- Source-grounded HDR feature mappings and relationship judgments for 125
  evaluable TRAIN/arm cells. The readiness artifact contains the exact
  hypothesis-bound worklist. Do not substitute planted-hypothesis recall.

Provide actual HDR payloads as a JSON object keyed by generation input-set ID,
then arm. Each payload follows `inductive_execution.bound_hdr_score` and must
bind hypotheses_sha256, source-ground-truth SHA, feature mapping and judgments.
No placeholder annotations or validation attestations have been generated.

Recheck after supplying actual evidence through the frozen protocol's authorized
artifact process (use a new output path each time):

```sh
cd /Users/arpit/asi-selection
python3 E6/test_readiness.py --hdr-inputs E6/data/hdr_inputs_actual.json --output E6/data/pre_test_readiness_20261112_v2.json
```

Prepared TEST command, BLOCKED until all mandatory gates pass and the new
implementation is committed locally. No push is required. This command is for
a subsequent authorized turn, and was not executed:

```sh
cd /Users/arpit/asi-selection
python3 E6/run_confirmatory_test.py --hdr-inputs E6/data/hdr_inputs_actual.json --output-dir E6/runs/confirmatory_test_v1
```

The launcher rechecks readiness before constructing clients, verifies its local
committed implementation, consumes TRAIN checkpoints only, generates the
literature cohort through the existing gated orchestrator, and connects the
existing reconstruction, TEST accuracy, recovery, HDR, diversity, question-type
and historical-question evaluators. Failed generation remains missing. Every
request is journaled before/after invocation. A launch marker blocks restarting
an interrupted launch; no automatic retries or regeneration are implemented.
Explicit reconciliation is required after an interruption. Scoring artifacts
are exclusive-create. Analysis and post-outcome human error review remain
separate steps; no completed confirmatory evaluation is claimed.

## TRAIN evaluator validation attempt (current follow-up)

No readiness audit was repeated. Implemented and executed
`E6/validate_evaluators_train.py` against preserved TRAIN checkpoints 0000/0001
only. It prepared 16 frozen-rubric validation calls (four per evaluator), including
six exact identity controls, and ten cases requiring independent human labels.
The selection is a small operational pilot; no frozen sample size, threshold or
settings were changed. It is not a completed semantic validation.

Actual execution stopped at local runtime identity verification:
`/api/version` returned `Operation not permitted` under this Codex session's
network sandbox. No request reached evaluator inference. Validations completed:
**0/4**. Metrics of semantic agreement are unavailable, not zero. The report's
zero valid-response/planned-case coverage reflects zero executed cases.

Evidence: `E6/data/evaluator_validation_train_v1/` contains `cases.json`,
`human_labels_required.json`, `provenance_started.json`, `execution_blocker.json`
and `report.json`. Frozen settings and the source checkpoint hashes remained
unchanged. No TEST calls, TRAIN generation retries, changes to historical call
logs, or GitHub pushes were made. Four focused offline tests and compilation pass.

Minimal next action: run the following in a normal local terminal that can reach
Ollama (the failed attempt directory is preserved; use a new directory):

```sh
cd /Users/arpit/asi-selection
python3 E6/validate_evaluators_train.py --output-dir E6/data/evaluator_validation_train_v2
```

An independent reviewer must label the ten entries in
`human_labels_required.json` (two similarity, two semantic equivalence, two
hypothesis distinctness and four question-type judgments), with identity and
rationale. Reviewers should not see model outputs before labeling. Researcher
assessment of acceptable validation performance and missing category coverage is
also required: no numeric acceptance rule is specified in the frozen files.
These ten labels are the minimum for the prepared pilot, not a claim that ten
labels suffice to establish evaluator validity. TRAIN-only checks cannot supply
literature target extraction or its Decision 24 independent source reviews.
The other existing literature-review and grounded-HDR blockers remain unchanged.

## Saved TRAIN validation evidence finalized (v2)

The user completed the local run. Offline finalization verified all **16/16**
responses against saved cases and started records, source checkpoint hashes,
frozen rubric files and rendered prompts, both prompt-hash conventions, raw JSON,
saved predictions, model/decoding/token limits, saved runtime identity and backend
usage. No inference or readiness audit was repeated. Saved validation inputs and
frozen settings were preserved.

The six logical identity controls are correct: reconstruction **2/2**, semantic
same-question **2/2**, distinctness **2/2**. Reconstruction identity-control MAE is
**0**. These are exact identity references, not independent human labels.
No independent semantic accuracy/agreement can yet be computed. Four question
classifications all return `analytic`; this supplies no demonstrated accuracy or
coverage for the other three categories. Verified usage is 4,019 prompt tokens
and 112 generated tokens from the existing run, not new inference.

**Validations genuinely completed: 0/4.** Operational response/provenance checks
are complete; all four remain pending independent semantic validation and
researcher assessment of adequacy. No acceptance threshold was invented and no
frozen `validation_status` field was changed.

Created `E6/data/evaluator_validation_train_v2_finalized/`:
- `validation_status.json`: recomputed metrics, status and provenance inventory.
- `verified_responses.json`: all 16 verified outputs and reference types.
- `human_review.json`: ten actual examples, outputs and blank reviewer fields.
- `human_review_blind.md`: independent label sheet without evaluator outputs.
- `human_review_with_outputs.md`: actual examples with saved evaluator outputs.

Minimum next action for this pilot: an independent reviewer labels **10 cases**
(two reconstruction similarities, two same-question pairs, two distinctness pairs,
four question categories), recording identity/date/rationale under the frozen
rubrics. Label the blind sheet first, then use the output sheet to compare.
Researcher assessment must address sample adequacy, untested categories and
external validity; ten labels alone are not asserted to complete validation.
Literature target extraction and Decision 24 source reviews, historical matcher
coverage/temporal eligibility, and source-grounded HDR remain separate issues.
Five focused offline finalization tests pass, including tamper rejection and a
network-prohibited full verification. No TEST calls, TRAIN retries or pushes.

## Literature and HDR source evidence prepared

Implemented and executed `E6/prepare_required_evidence.py` with zero inference.
Its output is `E6/data/required_evidence_v1/`. This completes 100 source packets
from the exact frozen literature rows, with original target text, source hashes,
source URLs, fixed extraction prompts and prompt hashes. No fixed-model output
exists in those rows; **0/100 actual fixed-model extractions are complete**.
Missing outputs are `missing_not_executed`, not fabricated all-null extractions.

Source review deliverables:
- `literature_review_sheet.md`: actual source text for the 20 frozen review cases.
- `literature_review_forms.json`: 40 pending independent reviewer forms, with all
  seven check fields, errors/corrections/notes, identity/time and extraction hash.
- `literature_adjudication_forms.json`: conditional third-person forms; use only
  after real independent reviewers disagree. None is represented as a review.

Material protocol/interface blocker: the frozen extraction prompt returns only
question/hypothesis and two explicitness flags, while the approved source-review
procedure additionally requires extracted problem/method/result checks and
explicitly requires a negative check when a component is absent. Current exact
four-field extraction validation does not admit those three extra fields.
Therefore merely running the four-field extractor will not make all seven
checks acceptable. A researcher-authorized compatible supplemental annotation
and validation path is needed; frozen prompts/settings were not changed here.

HDR deliverables:
- `ground_truth_rule_inventory.json`: 14 original ground-truth rules, with exact
  predictor/value and relationship quotations and character spans.
- `HDR_feature_mapping_proposal.json`: three literal predicate-field groups
  (`template`, `partisan_language`, `political_event_reaction`) with exact rule
  indices/quotations. This is a source-grounded grouping proposal, not approval
  of an HDR feature denominator. No claim of 14 independent features is made.
- `HDR_judgment_forms.json` / `HDR_review_sheet.md`: all 125 successful TRAIN/arm
  cells, each with six actual hypotheses, checkpoint hashes and source-bound
  comparison material. Discovery sets, relationship values and judge provenance
  stay null until genuine judgments exist. **HDR inputs complete: 0/125.**
- `hdr_inputs_actual.json`: empty completion map, with no fake zero scores.
- `terminal_missing_cells.json`: 8 failed arm cells and 7 unresolved 0007 cells;
  none is replaced, retried or given an HDR value.

Integration: `test_readiness.py --evidence-bundle E6/data/required_evidence_v1/bundle.json`
verifies this source bundle and reports its completion counts and blockers. It
does not override existing evaluator-validation, literature-review or HDR gates.
The new integration was tested directly; the full readiness audit was not rerun.
The bundle inventories the original frozen sources and all historical TRAIN
JSON/JSONL artifacts, which remain unchanged. Thirteen focused tests pass;
no model calls, TEST evaluation or GitHub push occurred.

Exact next essential action: a researcher/domain reviewer reviews the literal
HDR feature-mapping proposal, then supplies source-supported discovery and
relationship judgments with provenance for the 125 cells. In parallel, resolve
the literature component/interface mismatch through an authorized evidence path
before completing source reviews; actual fixed-model target extractions remain
absent and cannot be produced in a no-model-calls turn. Afterwards two independent
reviewers complete seven checks for each of the 20 fixed cases (40 reviews; 280
Boolean checks), with third-person adjudication only for disagreements. The ten
independent evaluator-pilot labels remain a separate pending requirement.

## Independent review ingestion and extraction runner

Read the actual `human_review_blind.md`: all ten label, reviewer/date and rationale
entries still contain underscores. The reported completed independent review is
not present in this file. `ingest_independent_review.py` was implemented and
executed; `E6/data/independent_review_status_v1.json` records **0/10 verified
labels**, unavailable agreement (null, not zero), missing fields per case and
**0/4 completed validations**. It never turns response agreement into a pass in
the absence of an acceptance/adequacy assessment. Recorded names can be checked
for completeness but real-world identity/independence cannot be authenticated by
software. No source review file was overwritten.

HDR: `E6/data/HDR_mapping_assessment_v1.json` records why the three literal source
predicate groups have not been promoted to a scoring denominator. The frozen
requirements call for grounded feature mapping, but do not establish that these
three groups define HDR features. No scores or discovery judgments were created.

Literature schema implementation: `literature_source_components.py` defines an
attributed source-annotation sidecar for problem/method/result. It preserves the
original exact four-field model extraction and fixed prompt. Each supplemental
annotation must bind the target source and fixed extraction, name its actual
annotator/time, and contain an exact source quotation and character span. Each
of the two source reviews must bind the sidecar digest and make all three actual
source-component decisions in addition to the existing question/hypothesis
checks. Existing source-review and independent adjudication validators still
apply; the sidecar never waives a failed/missing check. Readiness now validates
this combined source evidence after the existing review bundle passes. Default
actual sidecar evidence path is `E6/data/literature_source_components_actual.json`;
`--literature-components` can select a different evidence file. No such completed
annotation sidecar or human check is asserted here.

`run_literature_extraction.py` implements the actual fixed-prompt runner using
the approved Gemma identity, decoding, output limit and original extraction
interface. Its offline prepare mode was executed and created
`E6/data/literature_extraction_run_v1/extraction_plan.json` for all 100 targets.
No extraction or TEST inference was executed. Execute mode checks existing
protocol/approval/runtime/Git gates and live runtime identity; writes request
intent, prompt, options, raw reply and backend metadata durably; saves source-bound
terminal checkpoints; and packages the 100-record extraction manifest. Finished
and failed cells never trigger another call. An unresolved interrupted request
blocks resume; a durable saved response can reconstruct a missing checkpoint
without inference. Failed extraction records remain in the manifest. Review
packaging blocks explicitly if a required review case failed. Pending
source-component forms are produced separately, never inside the model output.

The new extraction implementation and sidecar module must be committed locally
before execute mode, as required for prospective execution code. No local commit
or push was made in this turn. After that local implementation commit, the exact
new-call command for a separately authorized extraction run is:

```sh
cd /Users/arpit/asi-selection
python3 E6/run_literature_extraction.py --output-dir E6/data/literature_extraction_run_v1 --execute
```

This is reference-target extraction only, not seven-arm TEST evaluation. Source
reviews and evaluator/HDR validations remain mandatory afterwards. Thirteen
focused offline tests and compilation pass. First save the ten actual completed
independent judgments into the specified blind sheet; then rerun ingestion with
a new output filename to preserve the previous status record:

```sh
python3 E6/ingest_independent_review.py --sheet E6/data/evaluator_validation_train_v2_finalized/human_review_blind.md --predictions E6/data/evaluator_validation_train_v2_finalized/verified_responses.json --output E6/data/independent_review_status_v2.json
```

## Automated HDR compilation completed

See `E6/HDR_SCORING.md`. `E6/hdr_pipeline.py` processed 125 source-verified TRAIN
cells offline, finding zero literal full-rule matches; semantic nonmatches remain
unknown. Actual HDR scores remain **0/125**, not 125 zero scores. Compiler outputs
are in `E6/data/hdr_scoring_v2/`. All 15 missing cells, including all 0007 arms,
remain missing. `--hdr-compilation` now integrates genuine completed payloads
with readiness; the present payload map is empty. Fourteen focused tests pass.
Frozen HDR discovery/relationship semantic prompts and a justified feature
denominator are absent. No new prompt or denominator was invented and no model
judgment was attempted. The separately running literature process and its
outputs were not accessed; no TEST calls or push occurred.

## Error-analysis and memo infrastructure

`E6/error_analysis_memo.py` was implemented and executed offline into
`E6/data/error_analysis_memo_v2/`. It verifies the exact frozen 20-set error-review
sample (10/testbed, including unresolved 0007), provides seven-arm end-to-end
packets and genuine-review forms, and computes frozen arm/paired bootstrap
summaries over the full 20/100-unit cohorts. Actual TRAIN token-cost means and
95% intervals populate a 337-word memo; outcome estimates/contrasts remain pending.
No completed scientific evaluation artifacts were supplied. Human end-to-end
reviews remain 0/20; no semantic error codes or examples were fabricated.
Fourteen focused tests pass. See `E6/ERROR_ANALYSIS_AND_MEMO.md` for exact inputs
and next command. The running literature extraction process and its outputs were
not accessed. No model calls, TEST evaluation, frozen changes or push occurred.

## Completed literature extraction verified and joined to source-review packets

Actual saved run `E6/data/literature_extraction_run_v1` was finalized offline.
**100/100** extraction checkpoints/raw replies/source bindings/four-field schemas
and saved provenance verified; no calls were repeated. Checks include source and
plan hashes, exact request prompts, request/reply/checkpoint identities, raw JSON
and parsed-record replay, model/options/token limits, usage, timestamps and saved
runtime identity. Backend RFC3339 variable fractional precision is handled only
for parsing; original timestamps remain unchanged.

`E6/data/literature_evidence_finalized_v1/` contains **20/20** exact frozen review
packets using actual extractions and existing hash-bound sidecars, a full source
quotation sheet, literal extracted-text spans, review-attention flags, 40 genuine
independent-review forms and conditional adjudication forms. Automatic literal
matches/nonmatches never become semantic accuracy/explicitness judgments.
Problem/method/result sidecars are still pending actual source annotations; no
human names, decisions, quotations-as-semantic-annotations or corrections were
invented. All extracted null fields remain null.

The six mandatory source-review paths are prepared in `evidence_bundle.json`.
Actual decision files remain empty, distinct from pending review forms. Two
independent reviewers must each make the seven prescribed checks on the 20
fixed cases (40 reviews / 280 Boolean decisions), supported by source quotations
and locations. Actual component evidence or honest unsupported/negative findings
must be recorded for 60 problem/method/result components. Third adjudicators are
needed only where actual reviewers disagree; bind sorted review records, record
the disputed check, category and source-grounded rationale. Negative checks
require preserved corrections and renewed review, never automatic acceptance.

Readiness now recognizes the completed bundle by default (or explicit
`--literature-evidence`) and reports completed extraction/packet verification
separately from missing human review. The direct integration snapshot is
`E6/data/literature_evidence_readiness_update_v1.json`. No full readiness audit
was repeated. Remaining scoring gates are genuine independent source reviews
and component evidence, four evaluator validations, and HDR definition/judgments.
Fourteen focused non-inference tests passed. Frozen settings and original run
artifacts were preserved; no model calls, TEST evaluation or push occurred.

## Requirement timing correction: earliest compliant TEST phase

See `E6/TEST_PHASE_REQUIREMENTS.md`. The assignment asks for 20 hand-checked
literature targets; frozen Decision 24 adds 40 independent review records and
280 checks, explicitly **before literature scoring**, not before HypoBench
accuracy prediction. Four evaluator validations similarly precede their own
scorers; grounded HDR inputs precede HDR computation. The separate 20-set
end-to-end error analysis and final memo follow actual outputs. Ten pilot labels
are a prepared internal validation route, not a frozen ten-label quota.

Added `--phase heldout_accuracy` to readiness and the launcher. The default full
mode preserves all previous scoring gates. The restricted mode defers only
unused scoring stages and retains protocol, approval, runtime/source/model/Git,
501-row denominator, failure preservation and no-retry rules. It cannot invoke
literature, semantic secondary scorers or TRAIN regeneration. Genuine source
reviews/validation/HDR requirements are not waived for their own stages.

Executed only the non-inference phase readiness check:
`E6/data/heldout_accuracy_readiness_v1.json` reports READY for that restricted
phase, no scientific blockers, and `full_evaluation_ready=false`. Eleven focused
tests pass. No human judgments, model calls or TEST execution occurred. Local
commit of the corrected prospective execution code remains required before use.
