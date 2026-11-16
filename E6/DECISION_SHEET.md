# E6 Researcher Approval Sheet

**Status: recommendations only; no option below has been approved.** The
validator currently reports 64 unresolved or invalid items, grouped here into
26 independent decisions. Assignment and repository facts are separated from
choices that need the researcher's approval. The approval timing column says
when a choice is needed, not that it may be filled automatically.

## Established by the assignment or repository

- Arms/order: D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled; K=6 and M=3.
- Six question candidates and 15 pairwise duplicate decisions; configured
  complete-link order, earliest representative, QH-sel rubric/weights, and
  QH-rand SHA-256 selection with seed 2026.
- HypoBench TEST has 501 rows; held-out labels are unavailable to generation
  and prediction. The 14 planted hypotheses are dataset-level only.
- 216 literature candidates passed source-backed eligibility checks. The
  assignment minimum is 100 targets, each with 10 abstract-bearing cited
  references; target extraction and 20 manual checks are required.
- A deterministic 100-ID proposal and first-20 review list exist, but both
  remain pending approval. Candidate manifest hash:
  `c48f2b30532f282929df10165ad5de682344b71c817dee0bcd9aee106a7aaf21`.
- Equal generation-token budgets, 95% paired input-set bootstrap intervals,
  and evaluation of the seven arms are required. The positive token cap and
  analysis details are not established.
- Gemma 3 12B runtime verification is saved in
  `E6/data/gemma3_local_verification_v1.json` (report SHA-256
  `705211d2dafd25afd7c42c52e11d8f3373efc089da313b5fb650ab4068f8783a`). Its
  verified tokenizer metadata fingerprint is
  `0a5090e20207bece62fbd58e81e2d6dcc3ee529d5173f2e66e336ae90507fecb`;
  exact counting, accounting parity, smoke inference, and the 32-token output
  limit probe passed. Model selection still requires researcher approval.

## Approval table

| # | Independent decision | Recommended option and reason | Alternative | Needed by |
|---:|---|---|---|---|
| 1 | Study status and prospective record | Treat only the yet-to-run frozen study as confirmatory; label prior work as development. This preserves prospective interpretation without hiding protocol development. | Declare the study exploratory. | Before preregistration |
| 2 | Testbed scope and sample size | Use the proposed 20 disjoint TRAIN evidence sets of 20 labelled observations, each scored unchanged on all 501 TEST rows, and the proposed 100 literature targets. This meets the literature minimum while limiting cost. | Use all 216 eligible literature candidates. | Before dataset freeze |
| 3 | Testbed/unit and outcome scope | Keep testbeds separate; one input set is one literature target or one fixed TRAIN evidence cohort; TEST rows are evaluation items. Separate summaries avoid pooling unlike tasks. | Select one primary testbed and treat the other as secondary. | Before preregistration |
| 4 | Task construction and allowed fields | Lock task text and a field allowlist; generation may see only task plus cited-reference abstracts for literature, or TRAIN text and observed TRAIN labels for HypoBench. TEST observations/labels and planted ground truth remain outside generation. Keep target answers and labels evaluation-only. | A predeclared task taxonomy with an explicit field mapping. | Before dataset freeze |
| 5 | Literature sample/strata/seed | Approve the existing SHA-256-ranked 100, seed 2026, with no strata. It is deterministic and avoids outcome-informed selection. | All 216, or a newly specified stratified design. | Before dataset freeze |
| 6 | Dataset hashes/freeze | Freeze separate per-testbed manifests and record each hash; do not combine unrelated source hashes. | Freeze only after selecting one primary testbed. | Before execution authorization |
| 7 | IDs, arXiv versions, category overlap | Retain implemented canonical arXiv IDs (strip vN), stable HypoBench row IDs, and unioned category memberships; this avoids duplicate experimental units. | Preserve arXiv versions as separate units, requiring regenerated data. | Before dataset freeze |
| 8 | Generator identity/evidence | Approve `gemma3:12b` using the saved runtime report and fingerprint; their provenance is now recorded in config. The choice itself remains unapproved. | Select another locally available model if desired. | Before configuration freeze |
| 9 | Decoding and output/context limits | Use temperature 0 and top_p 1.0 for deterministic decoding; consider the explicitly unapproved 2048 output / 32768 context limits, with 32768 counting context in the fixed-cap proposal; their adequacy is unmeasured. | Explicitly seeded nonzero temperature. | Before configuration freeze |
| 10 | Replicates, generation seed and run order | One replicate per input-set/arm; seed 2026; deterministic seeded arm order within input set. This is the smallest paired design. | Multiple preregistered replicates. | Before preregistration |
| 11 | Generation retries | One content-generation attempt; no quality-based regeneration. Keep failed cells. This prevents retries from changing selection or spending unequal budget. | No retries at all, including transport retries. | Before configuration freeze |
| 12 | Invalid output, missing cells, replacement | Invalid JSON/schema and incomplete K=6 are failed cells; retain them in denominator and report missingness; no outcome-based replacement. | Content-independent technical replacement under a frozen rule. | Before preregistration |
| 13 | Deduplication | Require Boolean pair decisions under the fixed prompt; reject numeric similarity output rather than inventing a cutoff. Keep complete-link order, earliest representative, and fail-closed insufficient-question behavior. | Approve a numeric similarity metric and threshold after development calibration. | Before configuration freeze |
| 14 | D-empty task leakage | Remove evidence fields and require an audit that retained task text has no paper-specific evidence. This isolates the evidence-removal control. | Allow a named, audited metadata allowlist. | Before dataset freeze |
| 15 | D-shuffled donors/assignments | Separately within approved TRAIN evidence cohorts and literature reference bundles, assign one other input's evidence by seeded derangement; prohibit self-donation and donor reuse within the assignment. No labels or target answers enter donor evidence. | Restrict donors to DEVELOPMENT, if a control with non-evaluation evidence is scientifically intended. | Before dataset freeze |
| 16 | Shared generation-token cap | Propose 8192 generated tokens per arm/input set as a cost-constrained design; record prompt usage separately. Historical development ceilings used a different unit. No completed usage profile establishes adequacy; approve retained exhaustion failures and related limits together. A full ten-record profile is not required. | A lower cap chosen for cost, accepting more incomplete arms. | Before configuration freeze |
| 17 | Output schema | Approve the current common envelope only after checking that it retains arm/input IDs, calls, tokens, errors, raw output/provenance, and evaluation links. | Revise/version the schema before approval. | Before preregistration |
| 18 | Outcomes and confirmatory contrasts | Use HypoBench exact-match accuracy and literature best target similarity as separate testbed-specific primaries; no composite. Report all 21 arm pairs, with multiplicity handled under decision 26. | Name one primary testbed/outcome and make the rest secondary. | Before preregistration |
| 19 | Literature similarity/same-question scoring | Use the available Gemma 3 12B with temperature 0, seed 2026 and a frozen rubric prompt; score each generated item 1–5 against the target field (1 unrelated, 3 partial substantive match, 5 substantively equivalent), report the maximum per field, and separately ask a Boolean same-question judgment. Preserve raw judgments and mark the shared-model limitation. This avoids acquiring an unverified evaluator. | A frozen embedding/cosine model for similarity and manual same-question adjudication. | Before preregistration; annotations validated before scoring |
| 20 | Already-asked rate | Use a versioned, deduplicated corpus of actual research questions and one fixed binary matcher; report numerator, eligible-question denominator, and missing-corpus status. Do not proxy titles or abstracts as questions. No such corpus is established in the current config, so this is a data dependency, not a value to guess. | Omit only if the assignment permits omission; otherwise locate/prepare and freeze a sourced corpus. | Before preregistration |
| 21 | K=6 diversity | Use the same Gemma judge and frozen binary distinctness rubric on all 15 unordered hypothesis pairs; report distinct-pair proportion per input set and arm. This reuses the configured model and directly matches K=6. | A frozen embedding-distance measure with a development-set threshold. | Before preregistration |
| 22 | Question-type classification | Use the same Gemma model with the fixed classification prompt, one judgment per generated question, and report constructive/analytic/ambiguous proportions. Questionless arms are N/A. | Multiple judgments with a predeclared disagreement rule. | Before preregistration |
| 23 | Optional pairwise LLM judge | Disable it in the primary analysis to avoid extra cost and subjective multiplicity. If later enabled, use at most one named judge, blind labels, matched lengths, both orders, and a fixed order-aggregation rule; label output as judge output. | Approve a specific pairwise comparison schedule and enable it. | Before preregistration if enabled; otherwise none |
| 24 | Target extraction/manual review | Extract every approved target with the fixed prompt; review the proposal's first 20 hash-ranked cases using two independent reviewers and a written disagreement/adjudication rule. Do not treat extraction as gold before review. | One reviewer plus independent adjudication of disagreements. | Policy before preregistration; complete checks before literature scoring |
| 25 | Error-analysis sample | Read 20 input sets end to end across all seven arms, with a fixed pre-outcome sampling policy and real-example error analysis. This can wait until analysis preparation, but not until after inspecting outcomes. | Fixed-size stratified review sample. | Before opening outcome text |
| 26 | Statistics/missingness/dependencies | Paired input-set bootstrap, 10,000 replicates, seed 2026, percentile 95% intervals, all 21 comparisons with Holm adjustment; retain/report failures. Record exact runtime/library versions when the analysis environment is frozen. | Another named interval, replicate count, RNG, multiplicity correction, or missing-data rule with rationale. | Methods before preregistration; exact versions before analysis |

### Decisions required before preregistration is finalized

Groups **1–22, 24, and the statistical methods in 26** must be approved or
replaced before finalization because they define protocol, data, outcomes, or
analysis. Group 23 requires a decision only if the optional judge will be
enabled; recommendation is disabled. Group 25's sampling implementation and
group 26's exact dependency versions may be completed at analysis preparation,
before any outcome text is inspected or scores are computed. Group 24's 20
reviews must be completed before literature target annotations are used as
validated references.

## Exact post-approval configuration changes

No values in this list are applied until the researcher approves or replaces
the corresponding recommendation. Values derived from frozen artifacts (such
as hashes) will be computed from those artifacts rather than guessed.

1. **`E6/config.json`** — set `protocol.approved_by`, `approved_at_utc`,
   `confirmatory_or_exploratory`, `prospective_protocol_record`, `status`, and
   `execution_authorized` only after sign-off. Set `dataset.sample_size`,
   `sampling_method`, `stratification_dimensions`, `selection_seed`,
   `task_domain_construction`, `task_domain_allowed_source_fields`, and
   `frozen`. Replace the ambiguous single `dataset.source_sha256` /
   `dataset.manifest_sha256` with a validated per-testbed record containing
   each source path/hash and selected manifest path/hash. Set
   `generation.temperature`, `top_p`, `max_output_tokens`, `context_limit`,
   `replicates_per_paper_arm`, and `random_seed_behavior`;
   `candidate_generation.candidate_generation_retries`;
   `controls.d_empty.task_may_contain_paper_specific_evidence`;
   `controls.d_shuffled.number_of_assignments` and approved donor rule;
   `inference_budget.tokens_per_input_set_arm`;
   `output.schema_approved`; all `failure_handling.*` fields;
   `evaluation_human_review.*` outcome/review fields;
   `execution_replication.*`; and `statistical_analysis.*`. Preserve established
   arms, K/M, weights, random seeds, IDs and exclusions.
2. **`E6/literature_testbed_config.json` and the separate selected manifest** — set
   `input_sets_selected`, `input_sets_frozen`,
   `target_sampling_and_deduplication_policy`,
   `manual_check_selection_and_adjudication_policy`, candidate/sample counts,
   IDs and computed selected-manifest hash. Create the selected manifest at a
   new versioned path; never overwrite the 216-row candidate manifest.
3. **`E6/question_pipeline_config.json`** — set
   `deduplication_threshold` only if a numeric policy is approved (otherwise
   retain null and enforce Boolean-only responses);
   `selected_hypothesis_max_attempts`, `selected_hypothesis_retry_policy`,
   `arm_hypothesis_max_attempts`, `arm_hypothesis_retry_policy`,
   `d_shuffled_donor_constraints.{eligible_split,recipient_split}`, and
   `orchestration.output_schema_status`. Keep existing complete-link ordering,
   representative, selection rule, seed, and weights.
4. **`E6/evaluation_config.json`** — set
   `reconstruction.{same_question_evaluation,reference_source,matching_and_aggregation_policy,explicitness_handling}`;
   `already_asked.{reference_question_corpus,semantic_matcher,threshold_or_adjudication_policy,denominator_and_missing_reference_policy}`;
   `diversity.{construct_definition,comparison_or_taxonomy_method,aggregation_policy}`;
   `question_type.{categories,classifier_model_and_version,replication_and_disagreement_policy}`;
   `pairwise_judging` enablement and unresolved schedule/blinding/length/order
   fields; and `paired_bootstrap.{statistic,interval_method,replicates,seed,random_generator_and_version}`.
   Preserve the existing HypoBench TEST labels, prediction policy,
   14-hypothesis source, and no-row-mapping rule.
5. **`E6/PREREG.md`, `E6/protocol.md`, and focused tests** — replace each
   unresolved statement with the approved value, record deviations and
   provenance, validate the frozen configuration, and update the Git gate's
   committed artifact paths if a selected literature manifest is added.
   Mark FINALIZED only after researcher sign-off; execution additionally
   requires the required preregistration commit and all existing gates.

Until approval, this sheet is a proposal only, the literature sample remains
unselected/unfrozen, and no experiment is authorized.

## Focused dependency work status

- Existing E2 raw and manipulation paper records and E6 development rows have
  no explicit native `research_question(s)` field. The source audit is saved
  as `E6/data/already_asked_corpus_source_audit_v1.json` with zero questions;
  it is an audit report, not an evaluation corpus. The already-asked metric
  still needs genuine question-bearing source data.
- `E6/profile_development_token_budget.py` and
  `E6/development_profile_runner.py` now run only the ten hash-bound
  DEVELOPMENT rows, with an exact generic task, exact-source verification,
  development-scoped D-empty audit, verified Ollama tokenizer, one profile
  attempt, and a temporary profile-only ceiling. The profile was not run here:
  this environment cannot access the local Ollama API (`127.0.0.1:11434`,
  sandbox permission error). The final E6 cap remains null.
- `E6/verify_gemma3_local.py` now stores actual verification JSON exclusively;
  the supplied successful report and tokenizer fingerprint are integrated in
  `E6/config.json`. This evidence does not itself approve the generator.

## Priority 9 finalization update (2026-11-11)

All 26 recommendations were reviewed. Assignment requirements and previously
implemented values remain in place. No recommendation has been promoted to an
approved scientific choice. Groups 9 and 16 now offer concrete, explicitly
unapproved limits without making ten completed development records a prerequisite.
The current unapproved proposal is `E6/data/fixed_token_cap_proposal_v4.json`; earlier proposals remain preserved.
The earlier statement that a numeric cap could only follow a full profile is
superseded: a prospective cost-constrained estimand is legitimate if its failure
and denominator policies are approved; empirical adequacy remains unknown.

The original 100-paper proposal has been resolved against the current eligible
candidate manifest and deterministic rule. Its original bytes are preserved,
including its legacy omission of exclusion_hashes; current candidate validation
still enforces exclusions. Reviewable lists are
`E6/data/literature_sample_approval_v1.csv` (100) and
`E6/data/literature_manual_review_proposed_v1.csv` (20). These are approval
materials, not selected/frozen datasets or completed extraction reviews.

A development profile may now stop after 1–10 records with `--limit`, and
`--checkpoint-dir` writes each completed record exclusively before proceeding.
It does not checkpoint in-flight model calls or automatically resume a run.
Saved single-record arrays can be summarized via `--envelopes`. No model calls
were made for this finalization work.

The 64-item gate output remains a list of unresolved configuration/sign-off
items, not 64 additional independent scientific decisions. Dataset hash schema
migration, held-out donor configuration, evaluator settings and executable
run/analysis entry points still depend on approved policies. The existing
interfaces and gate do not establish a runnable finalized study.

## Consolidated approval and implementation record

`E6/RESEARCHER_APPROVAL.json` is now the single editable approval record. Every
one of the 26 proposals is copied there with supporting evidence hashes, required
operational detail keys, and empty approval fields. This sheet remains narrative
context. No choice has been approved. The original sample proposal is immutable;
selection/freezing produces a separate selected manifest after explicit approval.
See `E6/FINALIZATION_WORKFLOW.md` for the prepared workflow and read-only checks.

## Assignment-based minimum approval update

The original assignment is preserved in `assignment_e6_excerpt_v1.txt`.
`DECISION_CLASSIFICATION.json` separates A (assignment constraints), B (verified
facts/existing implementations, not automatic approval), and C (judgment) within
every original group. K=6/M=3 is an example in the assignment and an existing
E6 contract, not a mandated numeric value. Preserve it without relabelling it.

`APPROVAL_CHECKLIST.md` is the concise 10-choice checklist for C. IDs 6, 7 and 17
are implementation/final-artifact sign-off items, not three independent scientific
choices. Their pending statuses are preserved; the validator no longer demands
separate researcher attestations for them. No signed row existed in the current
record. A preserved prior protocol claims approval but conflicts with the current
plan; its governing status is a real researcher question, not a value to infer.

The assignment explicitly requires a **generated-token** cap. The historical
prompt-plus-output development unit and v1 cap proposal do not satisfy that unit.
Final-mode accounting now charges generated outputs (including intermediate,
retry and probe outputs), and separately records prompts. Numeric cap remains
null. `data/fixed_token_cap_proposal_v2.json` supersedes v1 as an unapproved
8192-generated-token proposal. Twenty end-to-end error-analysis cases are required
in addition to the twenty target-extraction checks; no reviewer count is mandated.

## Held-out and runtime correction

The current Gemma protocol is the proposed governing draft under the latest task,
not formally approved. Legacy TEST-row generation is transductive. See
`PRIORITY9_TECHNICAL_RESOLUTION.md` for the implemented TRAIN-only adaptation,
source evidence, proposed 20×20 sample and 70,140-call unbatched prediction cost.
The existing 501-row TEST manifest is preserved solely for scoring preparation.
The separate first-ten-reference proposal controls literature prompt expansion;
this selection and all context/output limits still need researcher approval.
The 14-reference recall is not paper HDR. No real HDR/annotation/corpus data were
fabricated. Final execution remains disabled and frozen integration is outstanding.
