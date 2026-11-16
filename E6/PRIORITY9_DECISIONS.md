# Priority 9 decision packet — pending researcher approval

These are recommendations, not approvals. Existing approval records, active
configuration and DRAFT preregistration remain unchanged. IDs refer to the
original 26-row record. Accepting a group must explicitly cover its listed
values and exceptions; evidence-dependent details cannot be accepted away.

| Group / IDs | Exact recommended choice | Reason / outstanding condition |
|---|---|---|
| 1 / 1 | Ratify `E6/protocol.md` current Gemma draft prospectively; supersede the old protocol explicitly; all earlier work is development. Proposed quantitative expectations: QH-sel minus QH-rand = +0.25 on literature hypothesis best-similarity (1–5), +0.05 TRAIN held-out accuracy; D minus D-empty likewise +0.25 and +0.05. D minus D-shuffled: +0.25 literature, 0 data. Other required metrics/contrasts: expected difference 0, no directional claim. | These magnitudes are proposed elicitation values, not estimates or researcher beliefs. Researcher must accept or replace them. Data shuffle shares the mechanism, so deterioration is not assumed. |
| 2 / 2,3,5 | Both testbeds, separate summaries; existing 20 disjoint TRAIN sets × 20 labelled observations, seed 2026, each unchanged generated set scored on all 501 TEST rows; existing hash-ranked 100 literature targets, seed 2026, no strata. | Minimal prepared design; approve exact proposal IDs/hashes, not just counts. Statistical units: TRAIN evidence sets and literature targets. TEST is not historically unseen by the researcher. |
| 3 / 4,14,15 | Data task: exact `task_description` in `data/hypobench_inductive_proposal_v1.json`. Literature task: `Generate research questions and hypotheses supported by the supplied scientific evidence.` Allow TRAIN `text` and observed TRAIN `label`, or exactly first ten verified cited-reference abstracts in preserved order; no target abstract, TEST text/labels, or planted hypotheses in generation. Empty controls retain only approved common task. Separate no-self/no-reuse donor derangements using existing `deterministic_evidence_donors`, seed 2026, within each full cohort. | Approve task wording, exact source allowlists and empty-task leakage audit. TRAIN swap measures evidence-draw sensitivity, not a mismatched-mechanism negative control. |
| 4 / 8–10 | `gemma3:12b`, existing immutable model digest and Ollama 0.40.15; temperature 0, top_p 1, seed 2026; one replicate; output 2048 tokens/call, context 32768 for generation AND counting; `sha256_seeded_arm_order_v1`. | Common model/limits and deterministic order. Existing exact-limit DEVELOPMENT probe is blocked, not passed; successful evidence still required before final execution. |
| 5 / 16 | 8192 generated tokens per input-set/arm; include intermediate/discarded/retry/probe outputs; shared candidate/dedup outputs charge both selection arms, ranking charges QH-sel. Record prompts separately; evaluation-only calls outside this cap with usage retained. | Explicit cost ceiling, not a guarantee of complete outputs. |
| 6 / 13 plus selector policy | Six candidates; all 15 Boolean duplicate pairs; complete-link in generation order; earliest representative; block both selection arms if fewer than three remain. QH-sel weights novelty .30, specificity .25, significance .25, evidence grounding .20; integer 1–5; generation-order tie break. QH-rand existing SHA256 seed-2026 rule without replacement. | Reuses implemented fixed selection; explicitly differs from the older equal-weight/no-dedup plan. |
| 7 / 11,12 | One content attempt; zero transport/timeout retries; timeout 600 seconds; no quality regeneration or replacements. Invalid JSON/schema or incomplete six hypotheses = failed cell. Missing metric values remain null, never numeric zero. Invalid TEST predictions count incorrect in the fixed 501 denominator only for an evaluable generated set. Report failure fraction over all planned arm cells; metric means/contrasts use available units/complete pairs with explicit exclusions. Structurally questionless arms = N/A. | Requires **replacement approval for ID12**: its current prose says failed cells stay in the denominator, which cannot define a missing 1–5 score. Complete-case estimates are conditional on successful evaluation and can be biased. |
| 8 / 18–23 | Primary reporting outcomes: TRAIN held-out accuracy and literature hypothesis best-similarity, separately; focal contrasts QH-sel−QH-rand and D−D-empty; all other applicable comparisons descriptive. Same fixed Gemma judge, temperature 0/seed 2026. Similarity per item 1–5 (1 unrelated, 2 topical only, 3 partial substantive match, 4 close with material difference, 5 substantive equivalence), maximum per target field. Same-question = proportion of generated questions judged substantively equivalent in question/outcome/scope. Diversity = distinct pairs/15. Type = constructive/analytic/ambiguous proportions per set. Questionless arms N/A. Disable optional pairwise judge. HDR = grounded feature discovery × relationship correctness; 14-reference recall separately. Already-asked = matched actual questions / eligible generated questions against frozen genuine corpus. | Required corpus scope/path/hash and matcher, grounded HDR mapping/judgments, and source-bound evaluator prompt hashes are unresolved. Missing targets/corpus/judgments block the affected metric; no proxies. Approving this group does not supply those artifacts. Shared generator/judge bias must be disclosed. |
| 9 / 24 | Extract all 100 with fixed `09_target_extraction.txt`, same Gemma identity, temperature 0, top_p 1, seed 2026, output 2048/context 32768. Review first 20 existing hash-ranked targets; two independent reviewers; existing review guide; disagreements resolved by a third independent adjudicator. Report agreement by Boolean check and counts; correct/review negative checks before scoring. | Real reviewer identities, extraction records and completed source-bound reviews are not available. Approve policy now; complete actual work before literature scoring. |
| 10 / 25,26 | Mean per independent input set; paired mean differences; 10000 bootstrap replicates, seed 2026, 95% linear-percentile CIs; Python MT19937 streams seeded by SHA256(`seed:replicate`) as implemented. All 21 unordered arm contrasts where metric applicable; unadjusted marginal intervals, **no familywise significance claims**; `complete_pairs` missingness. No additional sensitivity analyses. Pin exact Python runtime and stdlib implementation hashes before analysis; no third-party analysis library. Error review: 10 units/testbed, lowest SHA256(`E6-ERROR-REVIEW-v1|2026|<testbed>|<input_set_id>`), across seven arms, selected before outcomes; one reviewer codes generation/schema failure, unsupported evidence, redundancy, question–hypothesis mismatch and target mismatch, with real examples. | Requires **replacement approval for ID26**: existing Holm proposal needs a specified hypothesis test/p-value method and further implementation; it cannot adjust percentile CIs by itself. Error review is separate from the 20 extraction checks. |

## Decisions that can travel together

Groups 2, 5 and 6 are a coherent prepared-design package. Group 3 can join it
only with explicit acceptance of the within-mechanism data control interpretation.
Group 4 is approvable conditionally on the real exact-limit runtime probe.
Groups 7, 8 and 10 must be considered together because denominators, estimands,
primary reporting and multiplicity interact. Group 1 needs the researcher's own
prospective expectations. Group 9 can approve a review policy now, not completed
human reviews. Group 8 cannot be made operational without its genuine sources.

## Minimum before a preregistration commit

1. Explicit signed decisions for the 23 scientific IDs in the 10 groups, including
   resolved operational details, current evidence hashes and honest predictions.
   IDs 6/7/17 are technical implementation/sign-off, not extra scientific votes.
2. Propagate those exact decisions to all four configs and protocol/PREREG;
   replace stale TEST-generation/descriptive pending text. Freeze separate
   manifests, exact task/source fields, donors, prompts/rubrics and analysis
   configuration; resolve all required validation fields. Do not set execution
   authorization merely because preparation is complete.
3. Identify/freeze genuine prior-question corpus and matcher, grounded HDR
   feature-mapping policy, evaluator prompt artifacts and extraction/review plan.
   Real extractions/reviews/judgments remain due before their scoring; they
   need not be falsely represented as already completed at preregistration.
4. Resolve successful exact-limit DEVELOPMENT runtime evidence for the final
   execution gate; this can be a declared pre-execution condition but is not
   supplied by the old 32-token smoke test.
5. After authorized final edits, hash/sign the actual configuration artifact set,
   including source manifests, analysis implementation/dependencies and review
   artifacts available at that stage. Run affected checks then required complete
   suite and `validate_protocol.py --non-inference --precommit`. Later explicit
   authorization is required to finalize and commit. No commit occurs here.

Current state: **not technically ready to finalize**. Methods are not fully
specified/approved and required source artifacts remain missing. Execution and
statistical adapters exist; they do not replace scientific decisions or evidence.

## Prepared approval-to-configuration integration

`approval_configuration.prepare_analysis_configuration` checks signed decisions
12/18/26 and returns copies of the two analysis-related configs. It changes no
files, approval fields, protocol status or authorization. Unsupported Holm plans
fail closed. Descriptive comparisons are not promoted to primary contrasts.
Primary hierarchy and outcome-specific rules still require explicit propagation
from decisions 18 and 12; this helper is not a whole-protocol finalizer.

Decision 26 must explicitly sign a `resolved_details.analysis_settings` object
with exactly: `statistic`, `interval_method`, `confidence_level`, `replicates`,
`seed`, `random_generator_and_version`, `comparisons`, `missing_policy`,
`multiplicity_method`, `analysis_dependency_versions`. Supported recommended
values are `arithmetic_mean`, `linear_percentile`, 0.95, 10000, 2026,
`python.random.Random/MT19937; sha256(seed:replicate) streams`, the explicit
21 arm-pair lists, `complete_pairs`, `unadjusted_marginal_intervals`, and the
actual pinned Python version string. Existing required detail keys must also be
filled and signed; no missing values are defaulted by the helper.

The preregistration Git gate now includes the analysis implementation, its
contract documentation, and this configuration helper. Existing active
configuration and every approval remain unchanged.
