# E6 approval and prospective preregistration workflow

Current state: FINALIZED under explicit researcher authorization after independently verified report_02. This file retains the historical preparation workflow. No sign-off, dataset freeze,
extraction inference, finalization, commit, or experiment is executed by preparation.

`RESEARCHER_APPROVAL.json` is the single editable decision record. It contains
all 26 proposals, evidence file hashes, unresolved operational detail keys, and
empty approval fields. The older decision sheet supplies narrative context.
An approval is an explicit researcher attestation; validation cannot authenticate
human identity or determine whether a scientific choice is sound.

For each Category C decision component the researcher must set `choice` to `accept_proposal` or
`replacement`, provide `approved_value`, fill `resolved_details`, set `status`
to `approved`, identify `approved_by` and `approved_at_utc` (UTC, not future), and
set `approved_payload_sha256` to `researcher_approval.digest(decision_payload(row))`.
Accepting a proposal requires exact equality with its proposed value. Replacement
values must be written explicitly. All required operational details must be
concrete; accepting broad recommendations does not resolve missing prompts,
corpus hashes or task text. Changing a signed value/evidence invalidates approval.
Group 23 explicitly approves disablement or a fully specified replacement.
Group 25 can approve a prospective plan that fixes its remaining details before
outcome inspection; group 26 can similarly specify dependency-freeze timing.
No approval fields are automatically populated by a tool.

Read-only checks, safe to run now (expected exit 2 until approval):

```sh
python3 E6/researcher_approval.py
python3 E6/researcher_approval.py --finalization
python3 E6/validate_protocol.py --non-inference
```

After explicit sample/review approval, use the prepared Python API
`literature_finalization.build_frozen_literature_manifest(candidate, proposal,
plan, approval)` and `write_manifest_exclusive` to create the separate
`E6/data/literature_selected_manifest_v1.json`. It verifies scientific decisions 2, 5 and 24, the existing identity/hash implementation, the approved proposal hash, and exact source/prompt/plan equality. The original
216-row candidate manifest and approval-pending proposal must never be changed.
If a replacement sampling policy is approved, regenerate its proposal and adapt
the deterministic implementation before freezing; a prose replacement alone
does not implement a new sampler. This frozen artifact contains evaluation-only
target text and is not itself safe generation input. Use the existing
`build_orchestrator_input_manifest` allowlist and leakage gates to prepare inputs.

The prepared `data/literature_freeze_plan_v1.json` binds 100 candidate records,
source-text hashes, fixed rendered extraction prompts, and the first 20 review
IDs. Preparing the plan calls neither a network service nor a model. Future
real extraction must use the approved extraction model/settings and the existing
`extract_proposed_literature_sample` fixed-prompt interface with an explicitly
supplied client. It produces annotations, not validated reference truth.

Use `literature_finalization.prepare_extraction_review` on actual extraction
records to validate unchanged candidates, exact source/prompt/model provenance,
raw/parsed output agreement, and all 100 IDs before packaging the extraction
manifest and 20-case worklist at exclusive new paths. Failed extraction records
are retained; failed review cases block worklist completion. No fake extraction
or completed review is created during preparation.

Human checks use `LITERATURE_REVIEW_GUIDE.md` only if approved. The decision 24
`review_policy` must specify `reviewer_count`, `guide_path`, `guide_sha256`, and
`disagreement_policy: independent_adjudicator`. Accepting the current proposal
requires two independent reviewers. A different policy requires replacement
approval and implementation if this validator does not support it.
`LITERATURE_REVIEW_RECORD_SCHEMA.json` describes empty review/adjudication fields.
After real reviews, call `validate_review_bundle(candidate, proposal,
extraction_manifest, worklist, records, adjudications, approval)`; this is the
source-bound validation entry point. It rechecks selection, every extraction,
model approval, all 20 exact cases, distinct reviewers, timestamps, four Boolean
checks and source/extraction/guide hashes. Disagreements require an independent
adjudicator and a hash binding the actual reviewer records. Negative checks are
completed reviews but do not make annotations usable; correction and renewed
source-bound review are required. Preserve original extractions/reviews and use
new versioned paths for corrections.

Before finalization, implement the approved configuration and per-testbed hash
schema, donor/evaluation/statistical policies and run/analysis entry points.
Supply the genuine already-asked corpus. Run the complete E6 suite and the
read-only validators. Resolve every unresolved protocol field; approval record
validation supplements the existing config gate and does not replace it.

Only after those steps and explicit prospective sign-off, a later authorized
operation may mark PREREG FINALIZED. The researcher then fills
`configuration_signoff.artifacts` with repository-relative file paths and actual
SHA-256 file hashes, `approved_by`, `approved_at_utc`, and
`approved_decisions_sha256 = digest(record['decisions'])`. Bind at least all configuration/protocol and sample-plan/selected-source
files in `researcher_approval.CONFIGURATION_PATHS`, plus the extraction manifest,
review worklist, review records, adjudications,
review validation report, genuine prior-question corpus, generator-input manifests,
analysis dependencies, review guide and freeze plan used by the approved study.
Evidence snapshots must remain accessible and hash-matching; updated evidence
requires renewed explicit decision approval. File hashes must be computed after
the final document edit to avoid stale sign-off.

After final edits and sign-off, check local readiness without requiring a commit:

```sh
python3 E6/validate_protocol.py --non-inference --precommit
```

This command is read-only and never authorizes execution; the full Git gate is
still required after a separately authorized commit. Actual extraction reviews
remain due before literature scoring, as in decision 24, even if their policy
is approved earlier. Sign and commit those artifacts when available before use.

A later separately authorized commit must include `RESEARCHER_APPROVAL.json`,
all `PREREGISTRATION_COMMITTED_PATHS`, and every signed artifact. The Git gate
checks every signed artifact against HEAD byte-for-byte and validates explicit
approvals plus artifact sign-off. It blocks missing or changed artifacts and
unfinalized PREREG. Do not bypass it by directly calling an inference interface.
No Git-mutating commands are supplied or run in this preparation task.

The minimum scientific checklist is now `APPROVAL_CHECKLIST.md`, with A/B/C
classification for every group in `DECISION_CLASSIFICATION.json`. Original IDs
6,7,17 require implementation and final artifact sign-off, not separate scientific
approvals; their pending row fields are preserved. Do not ask the researcher to
choose a hash value, reapprove a runtime measurement, or manually perform schema
plumbing. Resolve the older protocol's approval/precedence conflict first.
Use the v2 generated-token cap proposal, never infer a cap from total-token
historical profiles. Exact reviewer count, testbed design and model remain C.

## Current technical preparation

The current Gemma draft is the proposed governing draft; formal approval is still
pending. `PRIORITY9_TECHNICAL_RESOLUTION.md` supersedes older TEST-row generation
and 8192-context descriptions. Use `hypobench_inductive_proposal_v1.json` for
proposed TRAIN evidence and the original TEST manifest for scoring only; use the
separate first-ten-reference proposal for literature, subject to approval.
The cap v3 proposal keeps 8192 generated tokens and proposes 32768 context.
No previous cap/source/result artifact is overwritten.

Prepare a new data proposal offline, only when changed sampling is requested:

```sh
python3 E6/prepare_hypobench_inductive.py --input-set-count 20 --observations-per-set 20 --seed 2026 --output NEW_PROPOSAL_PATH.json
```

This does not freeze or approve data. Existing execution plan JSON files for both
testbeds are preparation-only. The final seven-arm executor stays blocked until
approved settings, final donors, frozen inputs, scoring and analysis are integrated.

Export an existing real final-format envelope without model calls:

```sh
python3 E6/execution_preparation.py --envelope EXISTING_ENVELOPE.json --testbed data --seed 2026 --output NEW_GENERATIONS.jsonl --failures-output NEW_FAILURES.jsonl
```

The exporter requires actual matching model seed and generated-token accounting.
Per-arm workflow cost is explicitly repeated/non-additive across hypothesis rows;
failed cells remain in a separate ledger, not fabricated hypotheses. No command
in this section launches inference, signs approval, finalizes or commits anything.

## Runtime and integrated TRAIN execution

The 32768-context/2048-output DEVELOPMENT probe is prepared and its local access
attempt is saved as blocked, not passed. In a normal Mac terminal with Ollama running:

```sh
cd ~/asi-selection
python3 E6/development_runtime_probe.py --output-dir E6/data/development_runtime_probe_v1
```

The probe uses one hash-bound DEVELOPMENT abstract plus controlled padding,
counts actual runtime tokens, pressure-tests 2048 output, checks runtime context
allocation and performs a negative software context test with measured counts.
It checkpoints each completed step and preserves reports; no TRAIN/TEST generation
or hypothesis evaluation is run. A successful report is factual evidence only.
Before final execution its path/SHA must be registered in
`generation.development_runtime_probe_report{,_sha256}`; active context/output
values and researcher approvals remain separate decisions. Blocked/fixture reports
cannot satisfy the final runtime gate. Counting and generation use the same
approved context, with 131072 retained only as model metadata.

`inductive_execution.prepare_train_execution_context` validates sources and donors.
`execute_train_input_set` joins seven-arm generation, independent held-out
prediction batches, actual bound HDR inputs and assignment JSONL export. It checks
all real gates before any model callback; never invoke it through patched gates.
`evaluate_train_envelope` can replay completed batches, checkpoint final summaries
and rescore newly supplied HDR inputs without repeating prediction calls.
`create_local_hypobench_evaluators` now requires explicit context and output limits;
it never silently chooses them. Native multi-observation prompting is not used.

All current scientific decisions remain pending. A same-dataset TRAIN shuffle
swaps evidence draws sharing the same underlying mechanism: it cannot be assumed
to be a negative mismatched-mechanism control. Approve its interpretation or
specify a genuinely different-mechanism donor policy before treating controls as
expected to deteriorate. No alternative data or control intervention is invented.

## Current offline freeze preparation

Gemma is adopted as governing; full method approval and artifact sign-off are
still pending. Exact unresolved operational values are now stored as
`proposed_details` in the existing `RESEARCHER_APPROVAL.json` rows, not as
approvals. No predictions have been filled. Similarity and diversity rubric
prompts now exist as hash-bound proposals; prior-question sources and grounded
HDR judgments are not supplied by these prompts. Existing question-type prompt
and parser include `other`, now reflected in configuration.

After actual explicit sample and review-policy approvals (IDs 2, 5, 24) and
current source hashes, the exact source-selection freeze operation is:

```sh
python3 E6/literature_finalization.py --freeze-approved-selection \
  --candidate E6/data/literature_citation_verified_manifest_v1.json \
  --proposal E6/data/literature_sample_proposal_v1.json \
  --plan E6/data/literature_freeze_plan_v1.json \
  --approval-record E6/RESEARCHER_APPROVAL.json \
  --output E6/data/literature_selected_manifest_v1.json
```

This validates approvals/sources first, creates a new selected manifest
exclusively, and performs no inference, configuration approval or PREREG
finalization. Never reuse this command to overwrite an existing frozen artifact.

Once every mandatory method is approved and propagated, make the authorized
final PREREG edits. Then call
`researcher_approval.configuration_artifact_hashes(root=repository_root,
extra_paths=additional_artifacts)` to compute exact current hashes for sign-off.
It writes nothing and fails on missing required artifacts. Additional artifacts
must include the actual generator-input manifests, donor mappings, approved
runtime/dependency evidence and all additional source/review artifacts available
and used. Later extractions/reviews must be signed and committed before scoring.
The researcher must explicitly attest the final artifact set and decisions;
hash calculation supplies neither identity nor approval. Run
`python3 E6/validate_protocol.py --non-inference --precommit` before any separately
authorized commit. The Git gate remains closed until the finalized artifacts are
committed unchanged. No freeze/finalization/commit operation was run in preparing
this interface.

Final local preregistration packaging: commit the signed E6 implementation, configs, tests, frozen manifests, prompts, prior-question source snapshots, DEVELOPMENT report/checkpoints and the two E2 source corpora needed by DEVELOPMENT provenance/tests. The HypoBench sources remain unmodified and are pinned as the existing clean nested repository at commit `7e4bbc341ee90b7efaa607f67a81543cd68cdf2e` with `.gitmodules`. Acquisition-only OpenAlex cache/batch directories and model weights are excluded; full native metadata needed for study inputs is embedded in the signed frozen manifests. Model weights/tokenizer fingerprints and backend 0.40.16 are recorded, not vendored. Future extracted annotations, human reviews, evaluator validation and actual judgments must be versioned/signed before scoring. A local Git commit does not claim those future scoring artifacts exist.
