# Pre-registration (append only; never edit past entries)
## Entry 0 - <date>
Hypotheses / metrics / test sets / pass criteria / margins: TODO

## Entry 1 - 2026-10-19 (design and splits; no test data touched yet)
**Problems chosen:** T1-T5, E1, E2, E4, E6, Main Problem.
**Compute tier:** small tier. Embeddings: Qwen3-Embedding-0.6B on Apple MPS. LM: TODO (see Entry 2).
**Time splits (Main Problem):** train up to end of 2023; choose settings on 2024; test once on papers from July 2025 onward.
**Test-set rule:** the test list is hashed and the hash committed here BEFORE any test evaluation. Test is opened once.
**Resampling unit:** paper (or input group / generating system when pairs share them).
**Controls on every result:** empty inputs, shuffled inputs, decoy question.
**Baselines:** B-Q, B-ABS, B-TF, B-LEN.
**Predictions (E1, made before measuring):** TODO - fill in below.
- E1 prediction: Qwen3-Embedding-0.6B places C closer to A than B on about __% of items (my guess, from one example: ...).
- Correction (2026-10-20): Entry 1 above was dated 2026-10-19 in error; it was written on 2026-10-20. Git commit time is authoritative.
- E1 prediction (2026-10-20, before measuring): Qwen3-Embedding-0.6B places C closer to A than B on about NN% of items. Reason: one example showed 0.986 vs 0.803.
- E1 prediction, corrected (2026-10-20): the "NN" above was a placeholder. My number: XX% of items (Qwen3-Embedding-0.6B puts C closer to A than B).
- E1 prediction, corrected (2026-10-20): the "NN" above was a placeholder. My number: XX% of items (Qwen3-Embedding-0.6B puts C closer to A than B).

## Entry 2 - 2026-10-21 (E1 evaluation protocol)

**Status:** Evaluation protocol documented after the development evaluation had already been run. This entry is a retrospective protocol record, not a genuine preregistration of those results. Earlier placeholder entries remain as historical record.

**Models:** Scientific-document embedding: `allenai/specter2_base`. General-purpose embeddings: `intfloat/e5-base-v2`, `BAAI/bge-base-en-v1.5`, `sentence-transformers/all-MiniLM-L6-v2`. Cross-encoder baseline: `cross-encoder/ms-marco-MiniLM-L-6-v2`. Include Qwen3-Embedding-0.6B if it remains the preregistered primary model.

**Predictions:** Before measuring, I predict that Qwen3-Embedding-0.6B will rank C closer to A than B on 60% of items. I predict that general-purpose embedding models will make this error on approximately 40–70% of items. These are hypotheses, not measured results.

**Distance:** For embeddings, d(x,y) = 1 - cosine_similarity(x,y), with normalized embeddings.

**Metrics:** Report near-miss error, overlap shortcut, low-overlap shortcut, scope ordering, and length-flipped scope-ordering performance. Report overall and per near-miss type. For retrieval, retrieve the ten nearest candidates for each A and use the cross-encoder to rank them. Report precision and recall for B and B_min as positives and C and C_tilde as negatives. Compare with a cosine-distance threshold selected with hindsight on the same evaluation set and label it as hindsight-tuned.

**Controls:** Include empty-input, shuffled-input, and decoy-question checks where implemented; clearly report any control not run.

**Held-out test:** Do not use `E1/test_item.jsonl` for model selection, prompt development, debugging, or threshold tuning. Record its SHA-256 hash before formal evaluation and evaluate it only once after the implementation is fixed. The file was printed during an earlier terminal inspection, so it should not be described as completely unseen.

**Cross-encoder caveat:** `cross-encoder/ms-marco-MiniLM-L-6-v2` is a passage-relevance baseline, not a model specifically trained for research-question identity. Do not interpret its score as a calibrated probability of identity.

## Entry 3 - 2026-10-21 (transparency and evaluation limitations)

This entry documents issues identified after the development evaluation. It does
not retroactively preregister the results already observed.

- Earlier entries contain unresolved placeholders. The 60% Qwen prediction in
  Entry 2 is recorded as a hypothesis in that entry, but because the development
  evaluation had already been run before that entry was added, it must not be
  described as a genuinely pre-evaluation prediction.
- The development results are exploratory until the dataset's source-paper
  provenance and manual semantic edits have been audited.
- The evaluator counts tokens with `re.findall(r"\b\w+\b", text.lower())`.
  Its length-flipped subset contains 39 items where the broader question has
  more tokens than the narrower question. The dataset checker's reported 43
  counts items where the broader question is longer using a different token
  pattern, so these counts are not directly interchangeable. The evaluation
  report uses the evaluator's 39-item definition.
- Unnormalized embedding norm is an exploratory diagnostic, not a validated
  measure of semantic scope.
- Retrieval thresholds were selected with hindsight on the development set.
  Retrieval precision and recall cover the four constructed target variants
  per query, not a fully labelled candidate pool.
- The cross-encoder is a passage-relevance baseline, not a calibrated
  research-question identity classifier.
- The held-out file was printed during an earlier inspection. It must not be
  described as completely unseen. Do not use it for further debugging or model
  selection. Its recorded SHA-256 is
  `c82d49bba8ac9a6cc4a184685d373e1cc2d26a1e7ad8cced8b10933a51577d12`.
  Any future evaluation must disclose this exposure limitation.

## Entry 2 - 2026-10-22 (E1 dataset frozen)
E1/contrast.jsonl frozen after re-read. SHA-256: 57f95f7690746d3b22670434410c4ce80894b42f0f8dc504cac58f7d9cdaedcc
No edits after this point; any change will be declared here as a deviation.

## Entry 4 - 2026-10-22 (declaration of deviations; corrects labels above)
- The entry headed "Entry 2 - 2026-10-22 (E1 dataset frozen)" above is the fourth entry, not a second Entry 2.
- The E1 prediction lines committed on 2026-10-19 and 2026-10-20 contain only template placeholders ("NN%", "XX%"). No numeric E1 prediction was recorded before the evaluation ran. The only numeric prediction (60% for Qwen3-Embedding-0.6B, in Entry 2) was written after the development evaluation, so it is retrospective and is not used as a pre-registered prediction.
- The single-example smoke test on 2026-10-20 (cos(A,C)=0.986 vs cos(A,B)=0.803) was exploratory and informed my expectation. Task 3 will therefore compare results with that stated expectation, not with a genuine prediction.
- On 2026-10-22 the Status line of Entry 2 was rewritten. Original text: "Proposed evaluation protocol, recorded before running the model evaluation." The original is in commit d2f0ed0 and in PREREG.md.before_e1_correction. It was changed because the evaluation had already run, so the original statement was false.
- Items h031-h062 were written less than 24 hours before the freeze commit (2026-10-22 13:59). Their 24-hour re-read is still to be done and will be declared separately.
- E1/results and E1/results_v2 are exploratory development results, not confirmatory.

## Entry 5 - 2026-10-22 (evidence on the order of prediction and first evaluation)
- Shell history (this terminal only; all lines carry one import timestamp, so only command order is reliable) shows: the Entry 2 commit containing the 60% Qwen3-Embedding-0.6B prediction (history #928) precedes the creation and first run of eval_contrast.py (#930). File times agree: Entry 2 committed 2026-10-21 21:20, eval_contrast.py created 21:23, first result files 21:25-21:31.
- Entry 3 labelled the prediction retrospective. This evidence suggests it preceded the first evaluation, but I cannot rule out an earlier run in another terminal, so the conservative label stands.
- contrast.jsonl was last modified 21:11, before any result file. No item was edited after any result.
- eval_contrast_v2.py (21:51) and audit_sources.py (22:14) were created after v1 results and do not appear in this shell's history. v2 changes from v1: <describe>. v2 results are post hoc.

## Entry 6 - 2026-10-22 (fills the placeholder in Entry 5)
- v2 changes from v1: the v1 scope metric (scope_ok = dAW > 0 and dAN > 0) was true for nearly every item and measured nothing, so it is withdrawn. v2 tests norm(W) < norm(A) < norm(N) on unnormalized embeddings and compares it with a length-only baseline, also on the length-flipped subset. v2 results are post hoc.

## Entry 7 - 2026-10-22 (clarification of incomplete Entry 0)
- Entry 0 remains an incomplete historical template. Its date, hypotheses, metrics, test sets, pass criteria, and margins were not recorded in that entry. The missing details cannot be reliably reconstructed from the available record, so no values are supplied retrospectively.
- This clarification does not create a preregistration or change the status of any evaluation results.

## Entry 8 - 2026-10-23 (E2 protocol; development already underway)

**Status:** This entry records the E2 protocol after dataset construction,
claim-extraction development, implementation work, and mathematical tests had
begun. It is not a prospective preregistration of those earlier decisions or
results. Any choices made after inspecting development results will be
identified as development decisions.

**Research question:** Do idea-level similarity, claim-level coverage,
relative neighbour density, and the proposed combined measure respond to
controlled changes in prior-work coverage as expected, and do their scores
correspond to independent human novelty judgments?

**Measures:**
- Y = 1 - maximum cosine similarity between the focal idea and an eligible
  prior paper.
- N = 1 - mean, across extracted atomic claims, of each claim's maximum
  cosine similarity to an eligible prior paper.
- RND = relative-neighbour-density percentile, on a 0--100 scale.
- yours = 0.75 * Y + 0.25 * N.

**Embedding implementation:** The current implementation uses the SPECTER2
base model with its proximity adapter and normalized CLS-token embeddings.
This is a deliberate implementation choice and differs from the BGE-M3
embedding configuration reported in the original RND paper. The RND
implementation uses P=100 neighbours for ranking and Q=50 neighbours for
density estimation. For a pool too small to support these values, parameters
are capped to the available sample size. The implementation excludes each
pool paper from its own local-density estimate. These choices will be
reported as implementation details rather than claimed as an exact
reproduction of the original algorithm.

**Pools and focal papers:** The development dataset contains the cs.CV,
cs.CL, and cs.LG pools. The manifest and focal-paper file define the
candidate pools and focal-paper memberships. The focal paper must be excluded
from its comparison pool. Eligible comparison papers must have publication
timestamps strictly earlier than the focal cutoff.

**Controlled manipulations:** Evaluate exact-copy and paraphrased-copy
conditions; partial claim coverage at 25%, 50%, 75%, and 100%; concentrated
versus distributed claim coverage; near versus far comparison pools; and
older versus newer comparison pools. Each manipulation must record its
construction, expected direction for each measure, and any failures or
unavailable cases. Expected directions are hypotheses to test, not guaranteed
outcomes.

**Mathematical criteria for the proposed measure:** Under the orthonormal
claim-embedding assumptions specified in the assignment, the proposed measure
is yours = alpha * Y + (1-alpha) * N with alpha=0.75. The mathematical
argument predicts that this choice satisfies the gradient and concentration
axioms. These results are conditional on the stated assumptions and do not
establish that real text embeddings satisfy them.

**Implementation checks:** Run unit tests for the mathematical axioms,
RND behavior, strict date filtering, focal-paper exclusion, and score
monotonicity when adding papers. Distinguish tests of a formula on synthetic
vectors from tests of the end-to-end text-embedding implementation.

**Evaluation and reporting:** Report results for each manipulation and each
measure separately, with denominators, invalid cases, and uncertainty where
appropriate. Human-label evaluation must use the assignment's specified
novelty labels and quality-only baseline, and must document the source and
cutoff of every test item. Any test-set exposure, tuning after inspecting
results, missing labels, or deviation from the requested baseline must be
disclosed. No final evaluation result is asserted by this protocol entry.

## E2: Explicit manipulation predictions

Prediction record added: 2026-10-24, before running the E2 manipulation
evaluation. The protocol was originally recorded after dataset construction
and implementation work had begun; this addition does not make those earlier
decisions prospective.

### Directional predictions

Higher Y, N, `yours`, and RND scores are interpreted as indicating greater
novelty. For RND, this interpretation must be checked against the implemented
scoring convention before evaluating outcomes.

| Manipulation | Y prediction | N prediction | yours prediction | RND prediction |
|---|---|---|---|---|
| Exact-copy overlap | Decrease | Decrease when claims are also covered | Decrease | Decrease |
| Paraphrased-copy overlap | Decrease relative to the original, but less reliably than exact copy | Decrease when paraphrased claims remain semantically matched | Decrease | Decrease, with greater uncertainty than exact copy |
| Increasing prior coverage from 25% to 50%, 75%, and 100% | Non-increasing on average; may be insensitive to individual claims | Non-increasing, with the clearest expected response | Non-increasing | Non-increasing on average |
| Concentrated versus distributed coverage of the same claims | Lower under concentrated coverage if one paper matches the complete idea better | Approximately equal when claim-level coverage is matched | Lower under concentrated coverage if Y changes as predicted | Direction uncertain; test empirically |
| Near versus far prior-paper pools | Lower for the near pool | Lower for the near pool | Lower for the near pool | Lower for the near pool, subject to the RND definition |
| Older versus newer eligible-paper pools | Lower for the newer pool on average | Lower for the newer pool on average | Lower for the newer pool on average | Lower for the newer pool on average |

These are hypotheses, not observed results. Pool comparisons must use the same
focal idea and the same eligible-paper cutoff, with every included paper
published strictly before that cutoff. The near/far and older/newer pools must
be defined and frozen before their scores are inspected.

### Evaluation rules

1. Preserve original extraction records. Do not automatically replace a record
   merely because another extraction contains more claims.
2. Report the number of valid cases and failures for every manipulation and
   measure. Missing, invalid, or unscorable cases must not silently count as
   passes.
3. Evaluate the predicted direction at the independent experimental unit.
   Report pass rates and 95% bootstrap intervals, resampling papers or
   independently generated manipulation instances rather than individual
   claim-paper pairs.
4. Include empty-input and shuffled-input controls where applicable.
5. Separate synthetic implementation tests from empirical results on paper
   text. Passing a synthetic test does not establish that real embeddings obey
   the same property.
6. Do not tune weights or thresholds using the held-out human-label benchmark.
7. If the implementation's RND score has the opposite orientation from the
   stated novelty interpretation, document and resolve that discrepancy before
   evaluating any predictions.


## E2 declaration - 2026-10-26 (corrections to the recorded predictions; no earlier text edited)
- The N prediction for concentrated versus distributed coverage ("approximately equal when claim-level coverage is matched") contradicted T2 Part B.3, which proves N is higher under concentrated coverage. The scored results agree with the derivation (N lower under concentration in 0 of 300 focal papers). The prediction was wrong; the derivation was right.
- The "yours" prediction (lower under concentrated coverage) held in the orthonormal toy model for alpha in (1/2, 1) but not on real SPECTER2 embeddings: the combined score was higher under concentration on average (+0.0047) and lower in 96 of 300 focal papers. The combined measure therefore fails the concentration axiom on this data.
- The concentrated and distributed conditions differ in the number of added synthetic papers (1 versus the number of claims). T2 Part B defines them that way (one paper versus j papers), so this is built into the axiom; the real background papers and synthetic-text style remain uncontrolled.
- Paraphrased-copy, near versus far, older versus newer, and the empty-input and shuffled-input controls were not evaluated in the 2,400-case run.

## E2 timing declaration - 2026-10-26 (no earlier text edited)
- The E2 protocol and the explicit manipulation prediction table in this file are dated 2026-10-24 ("prediction record added 2026-10-24, before running the E2 manipulation evaluation"). Git cannot verify that date: before 2026-10-26 the E2 sections were never committed (the previous PREREG.md commit is 2026-10-22 21:21).
- E2/data/manipulation_plan.jsonl was last modified 2026-10-24 19:05 and E2/data/scoring_results.jsonl 2026-10-24 21:37. The E2 predictions were first committed after both files existed, so they must be treated as retrospective with respect to git, whatever the dates written in the text.
- The corrections in the "E2 declaration - 2026-10-26" entry apply to the same predictions.

## E6: seven-arm experiment working preregistration draft

Historical development entry: superseded for future execution by the finalized `E6/PREREG.md` and hash-bound E6 configuration. Preserve the following earlier proposals as provenance; approved H1–H3 and active limits are in that governing record.

**Status:** Draft only; not a prospective preregistration, approval, dataset freeze, or authorization to execute. E6 implementation and development work predate this entry. Do not interpret the directional hypotheses below as researcher-approved or as results.

### Research questions and directional hypotheses

E6 compares seven paired arms on the same paper-level task and abstract: D, QH, QH-sel, QH-rand, HQ, D-empty, and D-shuffled. Each arm returns K=6 hypotheses (maximum 50 words each). QH, QH-sel, and QH-rand make three questions with two hypotheses per question; HQ makes six linked questions; QH-sel/QH-rand select M=3 from six candidates.

Working predictions to be approved before confirmatory use:

1. QH-sel will exceed QH-rand on literature reconstruction (best similarity to the target research question and main hypothesis, and configured same-question judgment), because its fixed rubric selects questions using novelty, specificity, scientific significance, and evidence grounding while QH-rand samples from the same candidate pool.
2. D will exceed D-empty on literature reconstruction and HypoBench held-out accuracy because D-empty removes paper-specific abstract/reference evidence.
3. D will exceed D-shuffled on those same outcomes because D-shuffled supplies another paper's evidence.
4. No directional prediction is recorded here for the remaining arm comparisons or diversity/type outcomes; these comparisons are secondary and must not be described as confirming a preregistered directional hypothesis.

These are proposed, theory-motivated predictions, not conclusions supported by E6 results. Their confirmatory status and prospective timestamp require researcher sign-off before evaluation outcomes are observed.

### Testbeds and outcomes

**Literature reconstruction testbed (prepared candidates, unapproved sample):** The existing `E6/data/development_manifest_v2.json` defines a 10-input DEVELOPMENT-only engineering set and reserves those IDs from future evaluation candidates. It is not a final evaluation sample. The literature testbed requires at least 100 genuine target papers after the selected generator's documented training cutoff and at least 10 reference abstracts per input; 216 source-verified eligible literature candidates and a deterministic 100-paper proposal are present; final selection/freeze and independent target annotations remain unapproved/incomplete. Primary outcomes proposed for this testbed are best similarity to the target research question and main hypothesis, plus same-question judgment against the fixed-prompt target extraction. Extraction is not gold truth until manually checked under the existing 20-case review requirement.

**HypoBench testbed (specified, pending protocol approval):** Generate hypotheses from proposed disjoint TRAIN evidence sets (20 sets × 20 labelled observations, seed 2026). Keep the resulting six hypotheses per arm unchanged when predicting all 501 observations from the preserved TEST manifest. TEST labels are available only to scoring. The old per-TEST-row generation design is transductive and is not the proposed confirmatory design. Accuracy is correct/501 per evidence-set/arm; paired inference resamples TRAIN evidence sets. Recovery against the 14 dataset-level planted hypotheses is separate from R44's feature-discovery × relationship-correctness HDR; actual source-grounded feature mapping and judge scores are required for HDR. No row-to-planted-hypothesis assignment or missing third-party examples are invented. Earlier researcher inspection of TEST labels is disclosed in NOTEBOOK.md. All model/evaluator/sampling/missingness choices remain unapproved; no predictions or recovery judgments have been run.

**Secondary outcomes:** Already-asked rate using a prespecified reference-question corpus and matcher; K=6 hypothesis diversity using a locked construct and aggregation rule; constructive/analytic/ambiguous question-type classification. The optional LLM judge is at most one named judge, compares length-matched pairs in both A/B orders, and is reported as LLM judge output. The judge model, matching procedure, blinding key, aggregation, and metric-specific operational policies remain unresolved.

### Data, generator, and selection

The proposed experimental unit is a unique research paper, with all seven arms paired on the same input. The development manifest is DEVELOPMENT only. The evaluation split must be disjoint from development IDs and all exclusions, selected and frozen before evaluation. The raw E2 corpus is a candidate source, not an approved E6 evaluation dataset or selected sample.

The proposed generator is locally verified Gemma 3 12B; model selection and decoding remain unapproved. Runtime/tokenizer evidence and the documented cutoff are recorded in E6/data/gemma3_local_verification_v1.json and E6/config.json. E2's Qwen3 settings are not an E6 selection. Equal generated tokens are the assignment-mandated budget unit; prompt tokens are recorded separately. The final-mode controller applies a common generated-token cap to each input-set/arm, charges intermediate/retry/probe outputs, counts shared preparation against both selection arms, and checks exact prompt plus requested output against explicit context limits. The exact cap remains unset until preregistration, and enforcement requires the selected model's exact tokenizer plus a backend that honors output ceilings.

QH-sel uses the existing four-dimension scoring prompt; the configured weighted sum is novelty 0.30, specificity 0.25, scientific significance 0.25, and evidence grounding 0.20, ties by candidate generation order. QH-rand uses the existing deterministic SHA-256 ranking, seed 2026, sampling without replacement, and key `E6-QH-RAND-v1|2026|<input_set_id>|<question_id>`. D-empty omits abstract and reference-evidence fields. D-shuffled uses the existing SHA-256 ordered, within-split derangement with seed 2026, no self-donation, and no donor reuse within an assignment batch. The QH-sel rubric, exact tie/order implementation, control leakage constraints, and retry/dedup rules still need protocol lock where noted in `E6/config.json`.

### Statistical and analysis plan

For every outcome with valid paired input-set values, report all 21 pairwise arm differences with paired bootstrap 95% intervals, resampling input sets. The evaluation implementation supports this interface. The bootstrap replicate count, RNG/seed, statistic/interval implementation, multiplicity policy, and missing-cell rule are not yet fixed; no inferential output is authorized until these are prespecified. Report arm-level denominators, failures, exclusions, and missing values. Do not use development inputs or held-out outcomes for tuning. Report literature reconstruction, HypoBench, synthetic recovery, already-asked rate, diversity, and question-type results separately; do not form a composite without a prespecified justified weighting rule.

The protocol remains blocked from execution until the generator and cutoff, real testbeds/splits, token cap and tokenizer, primary metric operational policies, statistical bootstrap details, failure handling, and prospective approval are resolved. No final seven-arm experiment has been run under this draft.

E6 technical correction: the proposed governing draft is Gemma-based, with saved
runtime/tokenizer evidence. Source TEST rows are evaluation items, not generation
units; bootstrap TRAIN evidence sets for data utility. Proposed context 32768 and
output 2048 remain unapproved, alongside the unchanged 8192-generated-token cap.
See E6/PRIORITY9_TECHNICAL_RESOLUTION.md. No E6 protocol is finalized or authorized.
# Submission-scope amendment — 2026-11-18

The candidate’s current requested submission scope is T1–T5, E1, E2, E5, E6,
and Main Problem M. This amendment records that selection as of 2026-11-18.
It is retrospective to the historical root preregistration and the saved E5
development run: the original root file selected E4, while E5 has its own
scoped preregistration and controlled-baseline results. This amendment does
not backdate authorization, change any frozen protocol, or convert exploratory
and baseline results into confirmatory results. See
`PROVENANCE/experiment-selection-clarification-2026-11-16.md`,
`E5/PREREG.md`, and the per-experiment completion reports for the exact
status and limitations. No additional test data were opened or evaluated as
part of this amendment.

