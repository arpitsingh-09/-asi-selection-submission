# E6 Seven-Arm Experiment: Preregistration Record

**Preregistration status:** FINALIZED  
**Execution status:** Generation is authorized only after the exact local committed-artifact gate passes; no confirmatory experiment has been run. Scoring retains actual evaluator-validation and source-review requirements.  
**Protocol basis:** `E6/protocol.md`, `E6/config.json`, `E6/question_pipeline_config.json`,
`E6/evaluation_config.json`, and `E6/literature_testbed_config.json`.

The current Gemma 3 12B protocol is the governing protocol by explicit researcher instruction; it supersedes the older Qwen draft preserved unchanged at `E6/prior_protocol_2026-11-04.md`. The researcher has now approved the documented sampling, task/control, model/budget, selection/retry/missingness and descriptive analysis settings. The three qualitative predictions and Decision 24 review procedure are approved. This does not supply evaluator validation, missing source data, completed human reviews or runtime evidence, or finalize preregistration.

This document separates implemented/project-recorded choices from open
decisions. This is the prospective record for future evaluation; preceding development is explicitly historical. It does not bypass the committed-artifact or scoring gates. Items described as unresolved must not be filled with defaults.

## 1. Objective and hypotheses

The objective is to compare seven workflows for generating six research
hypotheses from a research task and evidence, with all applicable workflows
paired on the same input set. The testbeds are (a) literature target-paper
reconstruction and (b) HypoBench TRAIN-evidence hypothesis generation with held-out TEST prediction.

The researcher explicitly approves these directional predictions on the existing
primary hypothesis-quality outcome, literature `main_hypothesis_best_similarity`:

- H1: QH > D.
- H2: QH-sel > QH-rand.
- H3: QH > D-shuffled.

Numerical effect sizes are unspecified by the researcher. No zero or other
magnitude is inferred. These predictions are recorded before future evaluation;
earlier development and historical working predictions remain development
history, not completed prospective preregistration.

TRAIN held-out accuracy remains the separate primary data-utility outcome.
The three hypothesis-quality directions are not extrapolated to accuracy, HDR,
diversity or question-type outcomes. All 21 applicable paired comparisons remain
descriptive with the approved unadjusted 95% intervals, complete pairs and explicit
denominators. The earlier D versus D-empty contrast remains a diagnostic, not a
fourth directional prediction. No composite quality score or adjusted significance
claim is introduced. Source-bound reconstruction and genuine independently
sourced prior questions are required. HDR needs grounded feature and relationship
judgments. The prepared diversity rubric is methodologically approved subject
to validation; question-type categories include `other`. Failed/unavailable
evaluations remain null.

## 2. Arms and output contracts

The arm order is fixed in the code and configuration:

| Arm | Existing workflow | Output contract |
|---|---|---|
| D | Direct task/evidence-to-hypotheses | K=6 hypotheses |
| QH | Joint question and hypothesis generation | 3 questions, 2 hypotheses per question |
| QH-sel | Candidate questions, deduplication, rubric ranking, then generation | M=3 selected questions, 2 hypotheses each |
| QH-rand | Same candidate pool and deduplication, deterministic random selection | M=3 selected questions, 2 hypotheses each |
| HQ | Hypotheses first, then linked questions | 6 linked question/hypothesis pairs |
| D-empty | Direct generation with evidence fields removed | K=6 hypotheses |
| D-shuffled | Recipient task with another paper's evidence | K=6 hypotheses |

The generator prompts require at most 50 words per hypothesis. The existing
prompt set is under `prompts/e6/`. QH-sel and QH-rand share the same six
candidate questions per input set. D, D-empty, and D-shuffled do not generate
questions under their current prompt contracts; question-based scores for
those outputs must be recorded unavailable, not inferred from hypotheses.

## 3. Question candidate processing and selection

- Candidate generation requests six questions.
- Deduplication requests all 15 pairwise decisions among the six candidates.
- Clustering is configured as complete-link in candidate-generation order;
  the configured representative is the earliest candidate in generation
  order.
- The implemented policy requires Boolean duplicate judgments for all 15 pairs;
  malformed/missing decisions fail preparation. Fewer than three unique
  questions blocks both selection arms without replacement. No numeric
  threshold is needed for this Boolean policy. This selection policy is approved; final preregistration remains pending.
- QH-sel ranking criteria are novelty (0.30), specificity (0.25), scientific
  significance (0.25), and evidence grounding (0.20). Each criterion uses the
  existing prompt's integer 1–5 score scale. Scores are combined by weighted
  sum; ties are broken by candidate-generation order. The ranking prompt is
  `prompts/e6/12_qh_sel_ranking.txt`.
- QH-rand uses `sha256_key_ascending_v1`, SHA-256, seed 2026, without
  replacement, and per-question key
  `E6-QH-RAND-v1|2026|<input_set_id>|<question_id>`.

## 4. Testbeds and eligibility

### Literature reconstruction

The source is the versioned citation-verified literature candidate manifest
`E6/data/literature_citation_verified_manifest_v1.json`. Its current recorded
hash is
`c48f2b30532f282929df10165ad5de682344b71c817dee0bcd9aee106a7aaf21`.
The manifest currently contains 216 eligible candidate sets among 400 exact
OpenAlex target matches. The candidates satisfy the preparation rules of
publication after the documented Gemma training cutoff (August 2024, month
precision), exact target identity, exclusions, and at least ten unique cited
references with abstracts. These 216 are not selected or frozen; no final
sample size is declared by this count.

A separate hash-ranked proposal now lists 100 IDs from this pool using seed
2026. It is stored at E6/data/literature_sample_proposal_v1.json with status
pending_researcher_approval in the preserved proposal; active approval is recorded separately. Source selection has since been frozen in the separate selected manifest; this preserved proposal is unchanged. Its first 20
ranked IDs are proposed for manual extraction checks. Sampling and Decision 24 review methodology are approved. The unchanged proposal remains a historical pending artifact; the source selection is now frozen in `E6/data/literature_selected_manifest_v1.json`, with exactly 100 distinct papers and at least ten reference abstracts each. Its immutable approval snapshot is `E6/data/literature_selection_approval_v1.json`. This is not evidence of completed reviews.

The target's own OpenAlex `referenced_works` list is the only source of citation
edges. Reference metadata is retrieved by exact OpenAlex Work ID. No fuzzy
title matching is used. Generation receives only cited-reference abstracts,
with a proposed first-ten-in-manifest-order subset recorded separately in `data/literature_reference_selection_proposal_v1.json`; first-ten reference methodology is approved; source freezing remains gated. target abstract/text is reserved for fixed-prompt
research-question/hypothesis extraction and is excluded from ExperimentInput.
The extracted fields are evaluation annotations, not established gold truth,
until the required manual checks are completed.

Exactly 20 distinct target extractions must be checked manually using the
existing worklist/review functions. Decision 24 approves the deterministic 20-case selection and the source-bound review procedure, with error/disagreement/correction records; actual reviews remain unperformed. Evaluator validation and inter-rater results are not supplied. No
review is represented as complete in this preregistration.

### HypoBench

The prepared testbed is `hypobench-synthetic-election-level2`, source split
`TEST`, with 501 stable input-set IDs in
`E6/data/hypobench_election_level2_test_manifest_v1.json`. Its recorded
manifest SHA-256 is
`b4a7c6da1ef9f0bf9bb27c160c850ab4a2b8cd3a7082e4ee48d82223f7ea6cc0`.
The legacy TEST-row generation adapter is transductive and is not the proposed
confirmatory design. `data/hypobench_inductive_proposal_v1.json` proposes 20
disjoint evidence sets of 20 labelled TRAIN observations (seed 2026). Each arm
produces six hypotheses once per evidence set; those hypotheses remain unchanged
across all 501 TEST predictions. TEST observations and labels do not enter
generation; prediction receives each TEST observation without its label.
Invalid/missing predictions are incorrect within each evidence-set/arm's fixed
501-row denominator. Sampling values are approved. Earlier researcher
inspection of TEST labels is documented in NOTEBOOK.md; this is not an historically
unseen test split.

The 14 planted hypotheses are dataset-level ground truth. The source does not
provide row-level planted-hypothesis assignments, and none will be inferred.
Recovery compares each TRAIN-generated set with those 14 references under the
configured evaluator; recovery is macro-averaged across TRAIN evidence sets,
with 14 as each set's denominator. This recall differs from R44's feature-discovery
rate times relationship-correctness HDR; the HDR calculation interface requires
source-grounded feature mapping and real judge inputs before any value exists. Ambiguous and invalid judgments do not count as
recovered and are reported separately.

HypoBench TRAIN supplies proposed generation evidence; VALIDATION remains available only for development. Neither is part of the held-out evaluation manifest. The prepared TEST manifest documents split isolation. Development
IDs are excluded by the E6 development manifest.

## 5. Outcomes and evaluation interfaces

### Literature outcomes

- Best similarity of generated questions to extracted target research
  question, and of generated hypotheses to extracted main hypothesis.
- Configured same-question judgment for each generated question against the
  extracted research question.
- Existing evaluation records retain candidate scores, raw evaluator output,
  target extraction hash, reference provenance, arm, and arm manifest. An
  unavailable target field or arm output is recorded blocked; no text or score
  is substituted.

The similarity function, same-question judgment policy, score scale, per-arm
aggregation across candidates, and validation of extraction annotations remain unresolved; unavailable metric cells stay null and are excluded explicitly from complete-pair contrasts. No metric value is asserted here.

### HypoBench outcomes

- Proposed utility metric: exact-match accuracy on all 501 TEST observations per fixed TRAIN-generated hypothesis set; invalid predictions are incorrect.
- Dataset-level planted-hypothesis recovery: per-input-set recovered count / 14,
  then arithmetic mean across TRAIN generation evidence sets; TEST rows are not independent hypothesis-generation replications. A GT hypothesis is recovered
  if at least one generated hypothesis receives an accepted MATCH. This is a
  single-model semantic judgment and has no row-level ground truth mapping.

The configured prediction and recovery prompts, model options, label leakage
barrier, output validation, and provenance are in `E6/evaluation_config.json`
and `E6/evaluation.py`. Their status remains pending protocol approval.

### Other required metrics

The evaluation code has interfaces for already-asked rate, K=6 diversity,
constructive/analytic/ambiguous question type, optional pairwise LLM judging,
and paired bootstrap intervals. The source corpus for already-asked
questions, semantic match policy, diversity construct/aggregation, question
type classifier/repetition policy, pairwise comparison schedule and length
matching rule, and bootstrap statistic/replicate count/RNG/multiplicity policy
are unresolved. The pairwise judge must remain at most one judge, use both
comparison orders and length-matched pairs if used, and be labelled explicitly
as LLM judge output. No operational scores are defined by this draft.

## 6. Generator, decoding, and token budget

The proposed generator is `gemma3:12b`, with local Ollama backend 0.40.15,
model-layer digest
`sha256:13576eb6dd8d9d04b4da04d015ff343968628d3c2984195569d9d3585651d4f1`,
and documented training cutoff August 2024 at month precision. Local runtime
verification is recorded in `E6/data/gemma3_local_verification_v1.json`
(SHA-256 `705211d2dafd25afd7c42c52e11d8f3373efc089da313b5fb650ab4068f8783a`),
including digest checks, adapter inference, `num_predict=32`, exact prompt-token
preflight, accounting parity, and the tokenizer metadata fingerprint
`0a5090e20207bece62fbd58e81e2d6dcc3ee529d5173f2e66e336ae90507fecb`. This
closes the runtime-evidence gap but does not itself approve Gemma as the final
protocol choice. Approved active generation settings are temperature 0, top_p 1, seed 2026, 2048 output tokens/call, 32768 context for generation and counting, and one replicate. Exact-limit runtime verification remains required.

The final-mode controller implements a shared generated-token cap per
input-set/arm and separately records prompt usage. It accounts for candidate generation, deduplication, ranking,
generation, and retries; QH-sel/QH-rand shared preparation is charged to both
arms. The cap is approved and configured at 8192 generated tokens per input-set/arm. Final execution remains gated on actual runtime evidence, complete methods and preregistration. Evaluation-only prediction/judge call
budget treatment follows the separate evaluation configuration and must not
be conflated with generation-arm usage.

## 7. Controls, exclusions, and contamination

- D-empty omits `abstract` and `reference_evidence`. The task's permissible
  paper-specific content still needs a leakage audit and a locked decision.
- D-shuffled uses the configured SHA-256 ordered derangement, seed 2026,
  within-split restriction, no self-donation, and no donor reuse in an
  assignment batch. Approved final donor cohorts are the 20 TRAIN evidence sets and the 100 literature ten-reference bundles, separately. Historical DEVELOPMENT-only constraints remain development-scoped. TRAIN swapping tests sensitivity to evidence draws within the same mechanism, without a guaranteed negative-control effect.
- E2 focal IDs (300) and the 15 targeted-comparison IDs are excluded by exact
  ID; all 15 targeted-comparison IDs overlap the focal exclusion set. The E6
  development manifest is also applied as an exact-ID exclusion.
- Literature candidates are post-cutoff and require ten abstract-bearing
  source-attested references. Target extraction is kept out of arm-generation
  evidence. HypoBench labels remain inaccessible until evaluation scoring.
- No replacement after observing an outcome is authorized. Approved retries: one attempt, no transport/timeout retries, 600-second timeout; malformed or incomplete output fails the cell; missing cells remain null and contrasts use complete pairs as specified below in `E6/config.json`.

## 8. Statistical analysis, blinding, and error analysis

The implementation supports 21 pairwise contrasts among the seven arms and
paired resampling at the input-set level with descriptive 95% linear-percentile confidence intervals for arithmetic means and paired mean differences. Failures remain null; arm means use available units, contrasts use complete pairs, and every estimate reports planned, included and excluded denominators. Invalid TEST predictions remain incorrect within the fixed 501 denominator only for an evaluable generated set; failed generation is not a zero score. Questionless arms are N/A. Intervals are unadjusted marginal intervals, with no Holm-adjusted or familywise significance claims. Approved bootstrap parameters are 10000 replicates, seed 2026, and Python MT19937 using SHA256(seed:replicate) streams. The two focal contrasts and all 21 descriptive comparisons are fixed. Exact runtime/dependency hashes must be frozen before analysis. No analysis command is confirmatory.

The optional pairwise judge is disabled under the approved analysis procedure; no pairwise judge results are asserted.
The error-analysis sample size, sampling method, strata, and coding rubric are
also not specified by the existing project files; they require researcher
decision and must be set before outcomes are inspected.

## 9. Provenance, storage, and reproducibility

For every input and arm, preserve stable input-set/paper IDs, split, source
records and source hashes, evidence and prompt hashes, model/backend/digest,
rendered prompts or hashes, raw outputs, attempts, validation errors,
timestamps, exact token usage, arm/control/selection provenance, and
evaluation inputs/outputs. Keep evaluation output provisional until schema
approval. Persist manifests and result bundles without overwriting existing
artifacts. Record every deviation before examining outcomes.

## 10. Execution gate and commands

The protocol/config validator and orchestrator are fail-closed. Final mode is
disabled and must remain so until protocol approval, data/config freeze, fixed
token cap, complete required datasets, and the prospective preregistration
commit are all verified. The validator now also requires `E6/PREREG.md`,
the frozen protocol/configuration files, and the development, HypoBench TEST,
and literature-candidate manifests to be present in `HEAD` byte-for-byte,
with this document marked FINALIZED. Any selected literature manifest must
also be added to the gate's required committed paths. No commit is created by
this preparation.

Commands currently safe and executable:

```sh
cd ~/asi-selection
python3 E6/validate_protocol.py --non-inference
python3 -m unittest discover -s E6/tests -p 'test*.py' -q
```

The Python seven-arm runner and statistical-analysis adapter are implemented; unresolved settings still block final execution. Historical gap description: no approved command-line seven-arm runner or statistical-analysis
CLI. The repository provides Python interfaces (`run_seven_arms` and
evaluation functions), but exact HypoBench/literature execution commands
cannot be prepared without inventing runner options, finalized inputs,
selection policies, and unresolved evaluator/numerical bootstrap settings. Add those
commands only after those inputs and policies are approved. These omissions
are blockers, not permission to execute through an improvised call.

## 11. Decisions required to finalize

1. Confirmatory versus exploratory status; final directional hypotheses,
   primary outcomes/contrasts, and prospective sign-off.
2. Final dataset/sample/sampling/exclusion and freeze plan for both testbeds;
   target task construction and leakage constraints; resolve the selected
   literature sample from the 216 eligible candidates.
3. Gemma runtime evidence is reconciled with checked-in config; approve model and choose
   decoding values, replicate count, and one positive per-arm token cap.
4. Set candidate retry count; deduplication threshold/adjudication and
   fewer-than-three policy; verify QH-sel evaluator identity.
5. Lock D-empty task leakage and D-shuffled held-out donor/assignment policy.
6. Specify extraction review selection/adjudication and finish the 20 real
   manual checks before treating target annotations as validated.
7. Lock similarity and same-question methods, already-asked corpus/matcher,
   diversity and type-classification definitions, and optional judge/blinding
   policy.
8. Lock bootstrap statistic, interval procedure, replicates, seed/RNG,
   multiplicity, missing-data and error-analysis sampling policies.
9. Approve the output schema and failure/retry/replacement rules; implement
   the run and analysis command-line entry points.
10. Mark this record FINALIZED only after all decisions are recorded, then
    commit this preregistration together with the frozen protocol/configs and
    verify the Git gate. Until then, the protocol and experiments remain
    blocked.

## 12. Priority 9 preparation addendum (unapproved)

The 26-group decision sheet supplies proposal context. The fixed-cap proposal
at `E6/data/fixed_token_cap_proposal_v3.json` recommends a common 8192
generated-token cap as a cost-constrained study design, not an empirical
completion estimate. It includes prompt preflights and shared preparation.
Its related 2048 output / 32768 context limits are also proposals; the saved
32-token runtime probe does not validate their adequacy. No full ten-record
profile is required to approve a resource-constrained design. Actual cap,
decoding, failure and denominator settings remain unresolved in config.

The 100-row approval CSV and 20-row proposed review CSV under `E6/data/` resolve
the original sample proposal against saved citation sources and exclusions.
No selected manifest, extraction, human validation, or freeze is claimed.
The minimum source specification for already-asked questions is recorded in
`E6/ALREADY_ASKED_SOURCE_REQUIREMENTS.md`; the existing zero-question audit
continues to block that metric. All execution and sign-off gates remain active.

## 13. Consolidated approval and finalization workflow

`E6/RESEARCHER_APPROVAL.json` contains all 26 pending decisions and is the single
editable researcher approval record. `E6/researcher_approval.py` validates explicit
approval, chosen values, mandatory operational details, identity/time attestations
and evidence hashes. Finalization additionally requires a configuration sign-off
binding the actual artifacts and decision records. Neither passing software
validation nor filling a recommendation authenticates researcher identity or
establishes scientific correctness.

`E6/data/literature_freeze_plan_v1.json` binds the 100 candidate records, first 20
review IDs, source-text hashes and exact extraction prompts without selecting,
freezing or extracting anything. `E6/literature_finalization.py` provides the future
approval-gated freeze and source-bound extraction/review validation interfaces.
The review guide is proposed, and its format file contains no real reviews.
`E6/FINALIZATION_WORKFLOW.md` describes the remaining sequence. The Git gate now
also checks explicit approvals and every signed artifact against HEAD; it remains
blocked. This document is DRAFT and no workflow described here has been executed.

## 14. Assignment constraints and minimum approval scope

The original assignment requires generated-token equality, both testbeds, at least
100 literature targets with ten abstract-bearing references, fixed extraction and
20 hand checks, the required metric families, 95% paired input-set bootstrap
intervals, a separate 20-input-set end-to-end error analysis and a one-page memo.
These constraints are installed without researcher approval of recommendations.
Historical DEVELOPMENT accounting and results retain their original unit.

`DECISION_CLASSIFICATION.json` records A/B/C components for all 26 groups;
`APPROVAL_CHECKLIST.md` reduces the scientific questions to ten grouped choices.
Hashes, preserved IDs and schema compatibility (IDs 6,7,17) are administrative,
covered by final artifact sign-off rather than extra scientific approval.
All existing approval fields remain unchanged. A prior local protocol labelled
approved is preserved as `prior_protocol_2026-11-04.md`; its conflict with this
DRAFT must be explicitly resolved before finalization. No claim that the current
protocol supersedes it is made. DRAFT status and all execution gates remain.

## 15. R44 and context safeguards

The current Gemma-based protocol is adopted as governing and supersedes the preserved older Qwen draft. Full methodological approval and finalization remain pending. `PRIORITY9_TECHNICAL_RESOLUTION.md` records source evidence, the minimum
TRAIN-only adaptation, proposed sampling, exact remaining decisions and limitations.
No protected source/result artifact was modified. All cap/sampling/context proposals
remain pending; the generated-token cap is still null in active configuration.

New execution plans prepare 20 data evidence sets and 100 literature sets but
explicitly disable execution. The proposed 32768 context is supported by 131072
model metadata, not by a completed runtime context test. Fixed prompt character
counts are descriptive; actual model token counts and dynamic prompt fit remain
mandatory. Final-mode guards reject TEST evidence, mismatched runtime settings,
cap overrides and prompt-plus-output context overflow. Final inference remains
blocked. Assignment JSONL export preserves real hypotheses and separate failures;
workflow costs repeat with explicit non-additive scope, never fabricated per-item
costs. No confirmatory generation or evaluation was performed.

## 16. TRAIN execution integration and DEVELOPMENT runtime evidence

The source-bound TRAIN context is integrated into the seven-arm orchestrator,
including a generic-task empty-control audit and independently verified
no-self/no-reuse TRAIN donor assignments. The TRAIN final path is callable only
when config, researcher, source, Git and exact-limit runtime gates pass; the old
unconditional block remains for unsupported final contexts, including literature.
No confirmatory call has been made. All methodological approval fields remain pending.

The minimal `development_runtime_probe.py` attempt was denied local loopback
access before any model call. Its real report is retained under
`data/development_runtime_probe_v1/report_01.json`; actual new prompt counts are
null, not estimates or substituted fixture results. A normal-terminal run of the
same script can resume checkpoints and measure actual DEVELOPMENT prompt counts,
long-context use, 2048-token limit pressure and context guard behavior.

Generation and counting now use the same proposed 32768 context; 131072 remains
model metadata, not a required unverified runtime allocation. The proposed
8192-generated-token cap and 2048 per-call output remain unchanged. A successful
report must be registered by path/hash and validated before final execution.

Held-out prediction transport can queue bounded independent one-observation
requests; no prompt combines TEST examples. Every prompt, seed, per-request limit,
output order and invalid-prediction denominator is preserved. Batches and generation
outputs are checkpointed; their identities bind source, context, outputs and policy.
HDR inputs must bind the actual arm/hypotheses and source-grounded feature mapping.
Missing inputs stay blocked; 14-reference recall never substitutes for HDR.
Mandatory JSONL and failed-cell export is integrated, with explicit non-additive
arm-workflow token attribution. See `RUNTIME_INTEGRATION.md` for the exact probe
command, evidence status, library entry points and remaining blockers.

Current approval scope includes qualitative predictions (ID1), methodology IDs 2,3,4,5,8–16,18,23–26, and the diversity rubric (ID21) subject to validation. Reconstruction and question-type method connections (IDs19/22) now use the existing fixed rubrics/settings, with actual validation still required. Decision 20 is now explicitly researcher-approved for the hash-bound 13-question limited historical sample, deterministic top-20 retrieval and Boolean semantic identity; historical coverage is incomplete. Final artifact sign-off remains pending. The literature source selection is frozen; its reviews remain unperformed. Earlier development entries describing unset budgets or pending numerical analysis are historical snapshots, superseded by the active settings above. No runtime probe or human review is represented as passed.

Current configured evaluation entry point is
`configured_evaluators.ConfiguredEvaluators`: it connects source-bound literature
reconstruction, diversity and question-type scoring to the existing implementations.
It checks configuration, scientific approvals, actual validation status, runtime
and committed preregistration before any model callback. Literature scoring also
validates the actual source-bound extraction/review bundle. Already-asked scoring
uses the approved limited 13-question corpus and its fixed semantic matcher identity;
there is no empty-corpus zero-rate fallback. HDR remains blocked without real
feature and relationship judgments. The source and manifest hashes are now bound
separately for each testbed using `per_testbed_artifact_files_v1`; validation checks
each named artifact's actual file hash. No pooled source identity is invented.
Final sign-off, finalized preregistration and execution authorization remain absent.

Decision 20 approval is recorded in RESEARCHER_APPROVAL.json. The existing
13-question corpus is a limited historical reference sample, not comprehensive
coverage of scientific questions. Candidate retrieval is deterministic with limit
20; lexical or cosine similarity cannot establish identity. Every reported rate
must disclose incomplete coverage and eligible-question denominators. Literature
cutoffs are verified original target publication timestamps; question source
versions must strictly predate the applicable cutoff. For HypoBench, independently
supported dataset provenance is required for any historical cutoff. In its
absence the already-asked evaluation is unavailable/null, not zero; this is the
approved method, not a missing methodological decision. No cutoff is fabricated.

Approved generation sources and the existing assignment output schema are
technically hash-bound/verified. Arm labels are omitted from evaluator prompts.
The optional pairwise preference judge is disabled, so its randomized A/B order
setting is inapplicable; the distinct HypoBench recovery policy still uses both
orders. All scientific decisions are recorded as approved. Whole-protocol final
sign-off, a passed exact-limit DEVELOPMENT runtime report, FINALIZED status and
execution authorization remain absent. Actual evaluator validation and source
reviews are still required before their scoring paths; no HDR judgments, reviews
or runtime evidence have been created by these configuration changes.

Finalized at 2026-11-12T03:40:42.515762+00:00 under explicit researcher authorization after verifying runtime report `E6/data/development_runtime_probe_v1/report_02.json` and its six checkpoints. Runtime file SHA-256: `1ae723209008e9a80d20d7194d85b443ae54480e21d32b081a4b86965b4ec1e6`. Active Ollama 0.40.16 replaces the historical 0.40.15 backend pin on the same model/tokenizer identity. All scientific decisions are approved; effect sizes remain explicitly unspecified. Historical DRAFT/unregistered-runtime statements in earlier development entries are superseded by this final record and active configuration. No source annotation review, HDR mapping, semantic-evaluator validation or confirmatory result is asserted by finalization. The local commit SHA is recorded by Git and reported externally, avoiding a self-referential artifact hash.
