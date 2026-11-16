# ASI Lab E6 — Experimental Protocol

**Project:** Should an AI Scientist Ask Its Questions First?  
**Protocol status:** Design decisions approved; implementation and experiments not yet completed.  
**Protocol version:** 1.0 — 4 November 2026

## 1. Research objective

Test whether generating research questions before hypotheses improves hypothesis generation and recovery of underlying relationships, compared with generating hypotheses directly.

Two testbeds:
1. **Synthetic data:** Election Normal and Counterfactual tasks. This measures inductive rule recovery and held-out predictive utility, not broad scientific discovery.
2. **Scientific literature:** 100 target papers published after the verified training-data cutoff of the generator. Reconstruct each target paper's research question and main hypothesis from related cited-paper abstracts.

Primary comparison: **QH versus D**.

## 2. Experimental arms

Use the same generator model and generation settings across arms. Every arm produces exactly six final hypotheses per input set.

| Arm | Procedure |
|---|---|
| D | Evidence → six hypotheses directly. |
| QH | Evidence → three questions → two hypotheses per question. |
| QH-sel | Generate six candidate questions; deduplicate and score them; retain three; generate two hypotheses per retained question. |
| QH-rand | Use the same six candidate questions as QH-sel; randomly retain three without deduplication or ranking; generate two hypotheses per retained question. |
| HQ | Generate six hypotheses first, then state the question each answers. |
| D-empty | Domain/task instructions without substantive evidence → six hypotheses. |
| D-shuffled | Evidence from another input set/paper → six hypotheses. |

Each hypothesis must be one declarative sentence, at most 50 words, expressing a testable relationship, mechanism, or prediction. No explanation, citations, or multiple alternatives.

### QH-sel selection
- Score six candidate questions on relevance, groundedness, specificity, and novelty, each from 1–5.
- Use the equal-weight arithmetic mean.
- Rank highest first; compare candidates pairwise for duplicates.
- Greedily retain the highest-ranked nonduplicate questions until three are selected.
- If fewer than three distinct groups remain, fill remaining slots with the highest-ranked unselected candidates.
- Use Qwen3 8B with a fixed prompt for same-question evaluation.

### QH-rand control
Use the exact same six candidate questions generated for QH-sel. Randomly retain three using a fixed recorded seed. Do not deduplicate or rank. Save selected and discarded questions.

### Control construction
- **D-empty, synthetic:** task/domain instructions but no substantive observations.
- **D-empty, literature:** broad field/topic information but no cited-paper abstracts.
- **D-shuffled, synthetic:** permute evidence sets within the same election condition using a fixed derangement; no set maps to itself.
- **D-shuffled, literature:** use another target paper's abstracts from the same broad research field; no target receives its own evidence.

## 3. Models and generation settings

### Generator
- Qwen3 8B Q4_K_M through Ollama.
- Temperature 0.1; seed 49.
- Thinking disabled; context window 40,960 tokens.

### Inference/prediction model
- Qwen3 8B Q4_K_M.
- Temperature 0.0; seed 49.
- Thinking disabled; context window 40,960 tokens.

Record exact model tag, runtime version, prompt version, seed, and actual token counts.

**Model-cutoff gate:** Verify and record the documented training-data cutoff for this exact Qwen3 8B model before selecting literature targets. Do not substitute release date for training-data cutoff.

## 4. Token budget and generation failures

- Use 10 development input sets for token-budget calibration; exclude them from final evaluation.
- Run all seven arms on development sets. Count all generated tokens, including intermediate questions, discarded candidates, and retries. Record prompt-token counts separately.
- Choose one common generated-token cap per input set that allows the arms to complete as often as possible; freeze before the main experiment.
- Record truncations and incomplete generations.
- Allow one format-correction retry and one temporary-technical-failure retry. Count generated retry tokens. Do not regenerate merely because content is weak.
- Preserve unresolved failures and report them.

## 5. Synthetic-data testbed

### Primary task: Election Normal and Counterfactual

Use the published election Normal and Counterfactual datasets as two conditions of one controlled stress-test task. Counterfactual reverses Democratic/Republican feature directions while retaining the third-party relationship.

Interpret this as a **prior-conflict stress test**, not a pure causal measure of prior reliance. Report Normal and Counterfactual separately, their equal-weight average, and the condition difference. Row overlap is incomplete; do not assume all rows are paired.

### Input-set construction
- 20 non-overlapping input sets per condition.
- 78 training observations per set: 26 from each of the three classes.
- Same input sets supplied to every arm.
- Training split for main evidence construction.
- Validation for development/calibration; test untouched until final evaluation.
- Record row IDs and sampling seed for every set.

### Development/calibration sets
Use five validation-only calibration sets per condition, each containing 36 observations (12 per class), for 10 development sets total. These are separate from the main training-derived input sets.

### Leakage prevention
- Main evidence-generation inputs use only training data.
- Validation is used only for development and calibration.
- Test is reserved for final evaluation.
- Prediction model sees test observations without labels.
- Ground-truth rules may be used for Oracle and feature-recovery evaluation, but must not be shown to ordinary generation arms or the prediction model.
- Do not tune prompts or settings on test outcomes.

### Prediction procedure
For each input set and arm:
1. Give the six hypotheses to the fixed inference model.
2. Evaluate every observation in the same untouched test split.
3. Require exactly one predicted class per observation.
4. Use only the observation and supplied hypotheses; do not reveal labels.
5. Do not invent relationships or abstain.
6. Apply one formatting retry if necessary.

Required prediction JSON:
```json
{
  "predicted_class": "Democratic",
  "supporting_hypotheses": [1, 3],
  "reasoning": "..."
}
```
`predicted_class` must be one of `Democratic`, `third-party/abstain`, or `Republican`.

### Primary synthetic outcome
Held-out **Macro-F1**, calculated separately for each input set and arm using the complete test split.

For each condition and arm:
- Report arithmetic mean Macro-F1 across 20 input sets.
- Report standard deviation across input sets.
- Compare QH and D using within-input-set differences.
- The input set is the experimental/statistical unit; test observations are not independent experimental replications.

### Secondary synthetic outcomes
- Feature recovery against the 20 ground-truth relationships.
- Breakdown by political endorsement, policy stance, partisan language, and political event reaction.
- Question diversity and process measures in Section 8.
- Election Normal–Counterfactual performance gap.

### Feature-recovery rubric
For each generated hypothesis, assess:
- Correct feature/feature-group identification.
- Correct direction.
- Correct description of the relationship.

Use a fixed rubric; report separately from Macro-F1 and break down by feature group. Audit a sample of automated judgments. Treat the 20 ground-truth relationships as a structured reference set, not 20 independent experimental replications.

### Floor and Oracle diagnostics
Retain Floor and Oracle as diagnostic baselines. Use them to check whether the predictive task and metric are informative. Report their construction and scores transparently; do not treat them as ordinary generation arms.

## 6. Literature testbed

### Target sample
- 100 eligible target papers.
- Each target postdates the verified training-data cutoff of the exact generator model.
- Accessible title, abstract, publication date, reference list, and verifiable DOI or OpenAlex ID.
- Identifiable research question and main hypothesis.
- At least 10 eligible cited-paper abstracts.
- Exclude targets without identifiable ground truth or fewer than 10 eligible abstracts; record reasons and select replacements.
- Manually verify 20 randomly selected target-paper extractions.

### Ground-truth extraction
Use Qwen3 8B with a fixed extraction prompt to identify the target paper's research question and main hypothesis. Manually verify 20 random examples and record corrections/failures. Do not treat an absent or ambiguous hypothesis as valid ground truth.

### Evidence retrieval
For each target:
1. Retrieve its reference list by DOI/OpenAlex ID.
2. Exclude the target itself and references published after it.
3. Retrieve cited-paper abstracts.
4. Embed target and cited-paper abstracts using `BAAI/bge-large-en-v1.5`.
5. Normalize embeddings and calculate cosine similarity.
6. Select the 10 highest-scoring eligible cited-paper abstracts.
7. Record reference IDs, dates, abstract availability, similarity scores, and selection order.

The target abstract is used only for retrieval and is never supplied to generation arms. Every arm receives the same selected evidence for a target. Missing abstracts are not fabricated.

### Literature controls
- D: selected 10 cited-paper abstracts.
- D-empty: broad field/topic instructions, no cited-paper abstracts.
- D-shuffled: 10 abstracts from another target in the same broad research field, with a fixed no-self mapping.

### Literature outcomes
Evaluate research-question reconstruction and hypothesis reconstruction separately.
- Primary similarity measure: maximum cosine similarity between target ground truth and generated candidate set.
- Supplementary similarity measure: mean similarity.
- One blinded LLM judge may be used as a supplementary measure. Use a fixed rubric, both presentation orders, length-matched comparisons, and hide arm identity.

For comparable research-question reconstruction:
- QH/QH-sel/QH-rand: associate each question with its two hypotheses, yielding six question statements by repeating the associated question twice.
- HQ: use the question generated for each hypothesis.
- D/D-empty/D-shuffled: use a fixed Qwen3 8B prompt to infer the question each hypothesis appears to address.
- Mark inferred questions distinctly from directly generated questions.

Report the difference in question provenance as a limitation. Do not describe inferred questions as directly generated.

## 7. Statistical analysis

### Synthetic primary comparison
- Primary comparison: QH versus D.
- Compute per-input-set differences.
- Paired bootstrap over input sets, 10,000 resamples.
- Report mean difference and 95% confidence interval.
- Use a two-sided significance test.

### Synthetic secondary comparisons
- QH-sel versus QH-rand.
- QH versus HQ.
- D versus D-empty.
- D versus D-shuffled.

Use the same paired-bootstrap framework and Holm correction across secondary comparisons. Report effect sizes, not only p-values.

### Literature analysis
- Primary comparisons: QH versus D for research-question and hypothesis reconstruction.
- Bootstrap over 100 target papers, 10,000 resamples.
- Report 95% confidence intervals.
- Apply Holm correction across the two primary literature comparisons.
- Secondary comparisons: QH-sel versus QH-rand and HQ versus D.

Report all arms and failures, not only significant results.

## 8. Question diversity and process measures

Secondary/process outcomes:
1. Semantic diversity: average pairwise embedding distance among questions.
2. Question-type diversity: coverage of predefined types such as causal, comparative, predictive, and explanatory.
3. Redundancy: proportion of near-duplicate questions.
4. Already-asked rate: proportion substantially repeating questions already addressed in supplied literature.

Use the fixed BGE embedding model and a predefined classification rubric consistently across arms. Document how question types and near-duplicates are operationalized.

## 9. Human audit

Audit 20 input sets:
- 10 literature.
- 5 election Normal.
- 5 election Counterfactual.

Select randomly within each stratum using a recorded seed. Inspect all seven arms. Blind arm labels, randomize output order, and apply the same rubric.

Score each output on five dimensions, 0–2 each:
1. Groundedness.
2. Relevance.
3. Specificity.
4. Distinctiveness.
5. Question–hypothesis alignment.

Record brief reasons. Compare human assessments with automated evaluations. This audit is diagnostic, not a substitute for full quantitative evaluation.

## 10. Logging and reproducibility

Store one JSONL record per generated hypothesis, with at least:
```json
{
  "input_set_id": "example_001",
  "testbed": "literature",
  "arm": "QH",
  "rq": "What relationship is being investigated?",
  "hypothesis": "A testable declarative hypothesis.",
  "model": "Qwen3 8B Q4_K_M",
  "seed": 49,
  "tokens_generated": 812,
  "prompt_tokens": 1450,
  "generation_status": "success",
  "timestamp": "ISO-8601 timestamp"
}
```

Also save:
- Prompt versions and hashes.
- Model/runtime versions and settings.
- Input-set row IDs and paper/reference identifiers.
- Target extraction outputs and manual-verification records.
- BGE scores and evidence-selection order.
- QH-sel scores, pairwise deduplication decisions, and final selection.
- QH-rand seed and selected/discarded candidates.
- D-shuffled mappings.
- Generation attempts, retries, truncations, and token counts.
- Predictions, labels used only for evaluation, and evaluation outputs.
- Human-audit sample selection, blinded outputs, scores, and reasons.
- Analysis scripts, environment details, and final report.

Preserve all existing E2 files and untracked project artifacts. Do not stage, clean, reset, or delete unrelated files.

## 11. Reporting and interpretation

The final report must:
- State primary results regardless of direction or significance.
- Separate Normal and Counterfactual results.
- Distinguish predictive utility, feature recovery, literature reconstruction, and question-diversity outcomes.
- Report all arms, failures, retries, token usage, and truncations.
- Include effect sizes and confidence intervals.
- Explain where decomposition helps or hurts, whether selection adds value over random selection, and common failure modes.
- Include human-audit findings.
- Avoid claiming broad scientific discovery from synthetic rule-recovery results.

### Limitations to disclose
- Synthetic task is controlled inductive rule recovery, not broad scientific discovery.
- Election text and labels are synthetic and may not generalize to real political behavior.
- Normal/Counterfactual versions have incomplete row overlap and must not be treated as fully paired datasets.
- Counterfactual results reflect both prior help and prior harm, not a pure measure of prior reliance.
- K=6 may not cover all 20 ground-truth relationships.
- A single model, quantization, seed, and inference family limit generalization.
- Literature training-data exposure may remain uncertain even for post-cutoff target papers.
- Similarity metrics and LLM judges have limitations and may favor particular wording or model styles.
- Inferred questions for hypothesis-first arms are not equivalent in provenance to directly generated questions.

## 12. Execution checklist

**Protocol approved; experiment not yet implemented or run.**

- [ ] Verify exact Qwen3 model training-data cutoff.
- [ ] Create and freeze protocol/prompts.
- [ ] Prepare synthetic input sets and record row IDs.
- [ ] Build literature target list and verify 100 eligible papers.
- [ ] Retrieve and freeze evidence abstracts.
- [ ] Implement all seven generation arms.
- [ ] Implement token accounting and retry logging.
- [ ] Run 10 development/calibration input sets.
- [ ] Freeze common token cap and prompts.
- [ ] Run all arms on both testbeds.
- [ ] Evaluate Macro-F1, feature recovery, literature reconstruction, and diversity.
- [ ] Complete 20-input-set human audit.
- [ ] Run preregistered statistical analyses.
- [ ] Produce one-page memo and final deliverables.

**This document does not claim that any E6 experiment has been run.**
