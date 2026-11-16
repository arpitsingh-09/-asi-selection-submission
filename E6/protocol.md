# E6 Seven-Arm Experiment Protocol

**Status: approved.** The current Gemma 3 12B protocol is the governing protocol by explicit researcher instruction and supersedes `E6/prior_protocol_2026-11-04.md` (older Qwen draft), preserved unchanged for provenance. Sampling, task/control interpretations, model/decoding/budget, selection/retry/missingness and descriptive analysis settings have explicit researcher approval recorded in RESEARCHER_APPROVAL.json. H1–H3 and the Decision 24 review procedure are approved. Evaluator/source evidence and unresolved evaluator details, actual evaluator validation and extraction reviews remain pre-scoring requirements; protocol and artifact sign-off are now authorized by the researcher and bound to the finalized record. Repository facts, existing prompt contracts, and unresolved proposals are distinguished below. The E6 entry appended to PREREG.md is a working draft and does not claim prospective preregistration.

<!-- E6-CONTRACT status=approved arms=D,QH,QH-sel,QH-rand,HQ,D-empty,D-shuffled raw=2680 focal=300 targeted=15 overlap=15 eligible=2380 hypotheses_per_arm=6 hypothesis_word_limit=50 candidate_count=6 dedup_prompt_count=6 outputs=D:0q6h;QH:3q6h2;QH-sel:3q6h2;QH-rand:3q6h2;HQ:6q6h1;D-empty:0q6h;D-shuffled:0q6h -->

## 1. Objective and experimental unit

E6 compares seven approaches on both required testbeds, reported separately. Independent units are literature targets (generation uses cited-reference abstracts) and fixed TRAIN generation evidence sets (generation uses TRAIN text and observed labels). TEST rows are evaluation items, not independent generation replications. Arms are paired within each input set, with D-empty/D-shuffled manipulating evidence.

Approved directional predictions apply to the existing literature primary
hypothesis-quality outcome (`main_hypothesis_best_similarity`): H1 QH > D;
H2 QH-sel > QH-rand; H3 QH > D-shuffled. Numerical effect sizes are explicitly
unspecified. TRAIN accuracy remains the separate primary data-utility outcome;
no quality direction is extrapolated to other outcomes. Prior development is
retained as development history. All intervals remain descriptive, not tests
of adjusted statistical significance.

| Arm | Procedure | Existing prompt-level output constraints |
|---|---|---|
| D | Direct generation from task and abstract | Six hypotheses |
| QH | Generate questions, then hypotheses in one response | Three questions, two hypotheses each, six total |
| QH-sel | Select questions, then generate hypotheses | Three questions, two hypotheses each, six total |
| QH-rand | Randomly select questions, then generate hypotheses | Three questions, two hypotheses each, six total |
| HQ | Generate hypotheses first, then questions | Six hypotheses and six linked questions |
| D-empty | Direct generation without substantive paper evidence | Six hypotheses |
| D-shuffled | Recipient task with another paper's evidence | Six hypotheses |

All existing hypothesis-generation prompts impose a maximum of 50 words per hypothesis. The question prompts do not impose a question word limit. QH-sel and QH-rand use six candidate questions and select M=3; this matches the existing deduplication prompt's six-question/15-pair contract and the configured selection count.

The seven prompt families exist under prompts/e6/. The source-bound TRAIN runner is integrated but gated; there is no approved completed protocol or confirmatory E6 output. Arm output constraints are prompt contracts, not approval of the overall design.

## 2. Dataset eligibility, provenance, and separation

**Established repository facts:** 2,680 unique stored paper IDs in E2/data/raw_papers.jsonl; 300 focal IDs excluded; all 15 targeted-comparison IDs overlap with those 300; 2,380 remaining candidate IDs by exact-ID subtraction. Exposure records are incomplete. No E6 sample is selected or frozen.

**Proposed frame:** use the raw corpus, abstracts, and unique paper as unit, subject to approval. The 2,380 are candidates, not a sample. Preparation must apply exact-ID exclusions, validate abstracts and canonical IDs, preserve cross-category membership, and record IDs, inclusion/exclusion reasons, evidence hashes, split labels, and source/manifest hashes.

Approved methodological design: 20 disjoint TRAIN evidence sets of 20 labelled observations; 100 literature targets selected by the existing SHA256 proposal; seed 2026 and no strata. Exact common tasks and source allowlists are recorded in config and approval decision 4. Decision 24 review policy is approved and the 100-paper literature selection is frozen separately; no completed extraction or review is asserted. Development inputs may support engineering and prompt tuning. Evaluation inputs must not be used for tuning.

### HypoBench supplementary testbed

The repository documents a prior audit of `data/HypoBench-datasets/synthetic/election/level2` in `NOTEBOOK.md`; E6 retains its supplied `TEST` split for evaluation only. The proposed minimum inductive adaptation generates from TRAIN evidence sets and scores each unchanged hypothesis set on all TEST rows. The source splits contain 1,750 TRAIN, 249 VALIDATION, and 501 TEST rows. Exact observation-text overlap across these three splits is zero. The prepared deterministic manifest is `E6/data/hypobench_election_level2_test_manifest_v1.json` (501 input sets; SHA-256 `b4a7c6da1ef9f0bf9bb27c160c850ab4a2b8cd3a7082e4ee48d82223f7ea6cc0`).

Each source row has no native row ID. E6 derives a stable input-set ID from dataset ID, split, zero-based source-row index, and the prefix of the canonical complete-row SHA-256; the complete row remains in the manifest. `text` in this TEST manifest is an evaluation observation, not generation evidence. `label` is held-out evaluation data and is excluded from `ExperimentInput`. The source metadata declares three classes, while the supplied TEST split contains only `likely democratic voter` and `likely republican voter`; the absent third-party class is not synthesized.

The 14 planted hypotheses are supplied at dataset level in `gt_hypotheses_level2.json`; the metadata's `ground_truth_hypotheses` copy is verified identical. Each row references this dataset-level set, but the source provides no row-to-planted-hypothesis assignment. E6 records that absence explicitly and does not infer an assignment. The upstream `config.yaml` contains unsuffixed split paths that do not match the actual `_level2.json` filenames; the E6 manifest records and hashes the actual files.

#### HypoBench evaluation policies (specified, pending approval)

**Held-out prediction:** For each TRAIN evidence-set/arm, a fixed hypothesis set is reused across TEST rows; each fixed prediction prompt receives the task description, the row's `text`, that arm's six generated hypotheses in generation order with IDs H1–H6, and the metadata-declared class names. The source row's `label` is kept outside the predictor and outside the generation `ExperimentInput`; only the scorer receives it after prediction. The evaluator uses the configured Gemma 3 12B Ollama client at temperature 0, seed 2026, and `num_predict=32`; its prompt is hashed and its raw output retained. It must return exactly a JSON object with one allowed `predicted_label` and one or more valid supporting hypothesis IDs. Malformed JSON, extra/missing fields, an out-of-set class, invalid support IDs, or a predictor failure becomes an invalid/null prediction. Invalid predictions count as incorrect and remain in the fixed denominator of 501. Primary metric: exact-match accuracy, aggregated as total correct/501 in manifest order. The third class remains a legal metadata-declared output although no TEST row has that label.

**Dataset-level planted-hypothesis recovery:** For each TRAIN evidence-set/arm output, a single fixed-prompt Gemma 3 12B judge compares every H1–H6 with every GT1–GT14, in source order, in both generated-first and planted-first presentation orders. It returns two 6×14 matrices of MATCH, NO_MATCH, or AMBIGUOUS. A pair is accepted only when both orders return the same definitive verdict; disagreement becomes AMBIGUOUS. Temperature is 0, seed 2026, `num_predict=512`; prompt, model usage, raw output, matrices, disagreements, and final verdict matrix are retained. MATCH requires the same substantive predictor/condition, outcome, and direction; wording may differ. Shared topic alone is insufficient. AMBIGUOUS means the relationship cannot be determined or only partially overlaps. Missing or invalid matrix cells are converted to AMBIGUOUS and reported; they never count as recovery. A GT item is recovered for an input set if at least one generated hypothesis matches it; an explicit MATCH takes precedence over ambiguous pairs for that GT. Per-TRAIN-evidence-set recovery is recovered GT count/14. Per-arm recovery is the arithmetic mean across generation evidence sets, not across TEST rows; report ambiguous/invalid and order-disagreement counts separately. No one-to-one constraint is imposed because the source does not establish such a mapping. This uses one blinded semantic judge for all arms and is not independent human ground truth.

These policies are fully specified for reproducibility but remain draft pending researcher approval. The same-model semantic judge is the material approval decision: it may favor outputs from the generator and has no independent validation in the source package. No held-out predictions or recovery judgments have been run.

## 3. Arm procedures and prompt mapping

- **D:** prompts/e6/01_generator_D.txt; task plus abstract.
- **QH:** prompts/e6/02_generator_QH.txt; three questions and two linked hypotheses per question.
- **Candidate pool:** prompts/e6/07_question_candidate_generation.txt once per paper; the exact six-question pool is shared by QH-sel and QH-rand.
- **Deduplication:** prompts/e6/08_question_dedup.txt requests every pair among six candidates (15 pairs). Pairwise decisions do not specify clustering/adjudication. Clustering and fewer-than-three handling remain unresolved.
- **QH-sel:** prompts/e6/03_generator_QH_sel.txt receives three selected questions. Rubric, scoring, selector, aggregation, and tie rule remain unresolved.
- **QH-rand:** prompts/e6/04_generator_QH_rand.txt receives three random questions. Seed, RNG/version, derivation, replacement policy, and fallback remain unresolved; repository prompt prose does not establish an E6 seed.
- **HQ:** prompts/e6/05_generator_HQ.txt; six hypotheses and six linked questions.
- **D-empty:** prompts/e6/06_generator_controls.txt; retain task, omit substantive abstract evidence. Exact empty representation and task leakage rule remain unresolved.
- **D-shuffled:** prompts/e6/06_generator_controls.txt; recipient task and donor abstract. Donor matching, split boundary, seed, assignment count, and donor reuse remain unresolved. Reject self-donation.
- prompts/e6/03_hypotheses_from_questions.txt, 08_same_question.txt, 09_target_extraction.txt, 10_question_type.txt, and 11_judge_pairwise.txt are auxiliary/evaluation prompts, not implementations.

Existing prompts are preserved. Some contain authoring instructions or typographic quotation marks in JSON examples; runtime adaptation/correction requires review and versioning.

## 4. Model configuration and inference budget

E2 fact only: E2/extract_claims_v8_qwen.py uses qwen3:8b via local Ollama, JSON mode, thinking disabled, temperature zero, 2,800 output tokens, and 600-second timeout. These are not approved E6 settings.

E6 model/version, backend/version, decoding, token/context limits, random-seed behavior, runtime/hardware, generation and judge models remain unresolved. Record model digest, prompt/input/evidence hashes, raw requests/responses, timestamps, attempts, and validation outcomes.

**Equal-budget implementation:** The shared controller in `E6/token_budget.py` enforces one configurable generated-token cap in final mode independently for each input-set/arm. Every arm-generation output and retry is charged; prompt usage is recorded separately; candidate generation and deduplication debit both QH-sel and QH-rand, while QH-sel ranking debits QH-sel. The controller requires an exact generator tokenizer and a backend that accepts a request-level output-token ceiling. It blocks calls that do not fit, records usage, and marks budget-limited incomplete generations as failures. Ollama requests honor the remaining output ceiling. The approved cap is 8192 generated tokens per input-set/arm. Generation and counting context are 32768; per-call output limit 2048; temperature 0, top_p 1, seed 2026. One replicate and sha256_seeded_arm_order_v1 are approved. Exact-limit runtime evidence and full preregistration gates remain required. HypoBench evaluation makes one prediction call per TEST row per TRAIN evidence-set/arm, and one recovery call per TRAIN evidence-set/arm; these evaluation-only calls are outside the generation cap, are not retried, and retain backend token usage in their individual evaluation records. Accounting for other evaluation judges remains unresolved.

The implemented QH-sel rubric scores novelty, specificity, scientific significance, and evidence grounding on integer 1–5 scales; weights are 0.30, 0.25, 0.25, and 0.20 respectively, with weighted-score descending then candidate-generation order as tie break. QH-rand uses the configured SHA-256 key ordering, seed 2026, and per-input key derivation. D-empty removes abstract and reference-evidence fields. D-shuffled uses a within-split, no-self, no-reuse deterministic assignment. These are existing implementation choices; task leakage and other safety constraints remain open where the config is null.

## 5. Common output schema and validation

A common JSON envelope is proposed, not approved. It must preserve protocol/config version, paper ID, arm, replicate, model/prompt versions, task and evidence/hash, donor ID, candidate pool, pairwise decisions, scores/seeds/selection, linked questions and hypotheses, raw output, attempts, validation errors/status, timestamps, and call/token/latency accounting.

Structural validation must check JSON, required types, arm-specific counts, unique IDs, nonempty strings, links, the 50-word hypothesis limit, known paper/candidate IDs, and control/selection provenance. Preserve invalid raw outputs; do not silently repair or substitute results. The output schema is an unresolved design decision.

## 6. Failure handling

Applied missing-score policy: failed/unavailable metric cells remain null, with no imputation. Arm means use available units; contrasts use complete input-set pairs with explicit included, excluded and planned denominators. Failed generation is never scored as zero. Invalid TEST predictions within an evaluable generated set remain incorrect in the fixed 501 denominator. Questionless arms are N/A. Approved operational policy: one content attempt, zero transport/timeout retries, 600-second timeout, no quality regeneration or replacement. Invalid JSON/schema or incomplete six-hypothesis output fails the cell and retains raw output. Proposed safeguards—not yet approved—are to log attempts, avoid output-quality-based selective regeneration, retain failures, and report missing cells. Do not replace papers after outcome inspection unless a prospective rule is approved.

## 7. Evaluation and human review

prompts/e6/11_judge_pairwise.txt covers specificity, testability, coherence, and evidence support, returning A/B/tie. It does not establish a primary outcome or evaluation design. prompts/e6/09_target_extraction.txt is not gold truth without independent validation.

Primary outcomes and all 21 descriptive comparisons are approved; question evaluation is assignment-required. Unresolved: operational evaluator matching/aggregation, validation and source evidence; judge model/count; evidence context for D-empty/D-shuffled judgments; blinding and A/B order; human-review scope/sample/reviewer count/guide/adjudication/inter-rater reporting; target extraction; and any composite score/weights. Define blind labels, randomized balanced presentation, locked unblinding key, and disagreement reporting in the approved plan.

## 8. Replication, execution, and statistical analysis

Applied analysis: descriptive paired arithmetic-mean differences with 95% linear-percentile bootstrap intervals at the input-set level, using complete pairs. Intervals are unadjusted marginal intervals; no Holm-adjusted significance or familywise claims are made. Independent units are literature targets or TRAIN evidence sets, never individual hypotheses, judges or TEST rows. Approved numerical analysis: 10000 replicates, seed 2026, Python MT19937 streams seeded by SHA256(seed:replicate), all 21 applicable arm contrasts. Directional focal contrasts are QH minus D, QH-sel minus QH-rand, and QH minus D-shuffled; D minus D-empty remains a diagnostic; separate primary reporting metrics are TRAIN accuracy and literature main-hypothesis best similarity. Freeze exact runtime/dependency hashes before analysis. Error review selects 10 input sets/testbed by the documented pre-outcome SHA256 rule across all seven arms; actual review is not represented as complete. Report failures, retries, exclusions, and missingness. Pin analysis dependencies and test with synthetic known-effect fixtures, not evaluation outputs.

## 9. Reproducibility gates and final report

Before selection or inference, validate protocol/config, exclusions, IDs, abstracts, split separation, hashes, prompt rendering, schemas, dedup/selection seeds, controls, failure policy, and call accounting with fixtures/mock responses only.

The final report must include protocol status/version/deviations; sample flow and exclusion counts; manifests and hashes; model/runtime/prompt versions; arm procedures and call costs; selection/control provenance; execution/failure counts; blinded and human evaluation; paired estimates, uncertainty, multiplicity; limitations; and reproduction artifacts.

Repository inclusion of E6 among selected problems is not a detailed preregistration. This draft does not approve protocol, dataset freeze, or execution.

## Assignment constraint update

The source assignment (preserved in `assignment_e6_excerpt_v1.txt`) caps generated
tokens, not prompt-plus-output tokens. Final runs use generated-token accounting;
historical development uses its original unit. The numeric cap is approved at 8192 generated tokens; historical measurements remain development evidence only.
Task 3 requires 20 end-to-end input-set error analyses separately from the 20
manual target-extraction checks. A/B/C classification and the ten-choice approval
checklist supersede the earlier blanket request for 26 scientific approvals.
The older Qwen protocol is superseded and preserved for provenance;
no pending decision or status in this draft has been approved by implementation.

## Governing Gemma protocol: R44 correction

The prior per-TEST-row generation design is transductive. The approved methodological design uses 20 disjoint TRAIN evidence sets of 20 labelled observations each,
seed 2026, with each generated set evaluated unchanged across 501 TEST rows.
Only TRAIN labels are generation evidence. Test labels and planted hypotheses
are evaluation-only. The 14-reference recall is not R44's FDR × RC HDR, whose
pure scoring interface now requires actual grounded feature mapping and scores.

The approved budget is 8192 generated tokens. Output 2048, context 32768
and counting context 32768 are approved settings requiring successful runtime evidence (131072 is model metadata only); exact prompt fit is checked
per call and context overflow blocks without truncation or silent cap reduction.
Approved reference evidence is the first ten verified references in original
manifest order to avoid uncontrolled 10–121-reference prompt expansion. No source
candidate, prior result, sample approval or review record has been changed.
The final seven-arm runner stays disabled pending approval and frozen integration.

## Essential runtime and execution integration

See `RUNTIME_INTEGRATION.md`. The attempted 32768/2048 DEVELOPMENT probe could not
access local Ollama; actual new counts remain unavailable. No successful evidence
was invented or registered. The TRAIN path is integrated through all seven arms,
source-bound controls, explicit frozen seed and supported run order, independent
one-row prediction batches, bound HDR and JSONL export with resumable checkpoints.
Researcher/config/runtime/source/Git gates must pass before any real callback.
Generation and counting use approved 32768 context; the cap is configured at 8192 generated tokens. Exact-limit runtime verification remains absent.
The code does not claim that same-task TRAIN evidence swaps must lower utility.
All scientific choices, literature final execution and final analysis remain open.

Approved evidence constraints: hypotheses use TRAIN only and are evaluated on
held-out TEST; HDR requires grounded feature and relationship judgments;
literature reconstruction requires original source-bound evidence; already-asked
evaluation requires genuine independently sourced questions. The prepared
diversity rubric is approved subject to validation before scoring. The existing
question-type schema includes other. Failed or unavailable evaluations stay null
with explicit denominators. These requirements do not create data, mappings,
validation results, numeric effect sizes, or completed human reviews.

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

Final preregistration record: the independently checked DEVELOPMENT report is `E6/data/development_runtime_probe_v1/report_02.json` (file SHA-256 `1ae723209008e9a80d20d7194d85b443ae54480e21d32b081a4b86965b4ec1e6`). Active Ollama is pinned to 0.40.16; the older 0.40.15 report remains unchanged historical evidence. The model/tag and tokenizer fingerprints are unchanged. Context 32768, long prompt 28871 and output 2048 are verified; accounting parity, allocation and the negative context guard pass. No confirmatory inference was run to finalize this protocol. Earlier draft-status entries are historical snapshots superseded by this final configuration and sign-off.
