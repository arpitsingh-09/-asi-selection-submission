# E6 Task 3 — saved-output error analysis

## Scope and rubric

The assignment asks: “Where did decomposition help and where did it hurt? Read 20 input sets end to end and write an error analysis with real examples. Does selection add anything beyond decomposition? Do the controls behave as they must? Which failure of the language model did you see most often and how would you detect it automatically?” This report inspects the frozen sample and saved records only. It does not claim the Task 3 human-review requirement is complete: only nine of 20 sampled cases have saved HypoBench generations, none has completed independent human coding, and the ten literature cases have no seven-arm generations or evaluations.

Source paths below are relative to the `asi-selection` repository root. The dated reading packet with full source examples is [`reading_packet_2026-11-17.md`](reading_packet_2026-11-17.md) (when both checkouts are siblings). Machine-readable per-set evaluation counts and source hashes are in the sibling [`post_hoc_saved_metrics_2026-11-17.json`](post_hoc_saved_metrics_2026-11-17.json). The underlying frozen case packets are under `E6/data/error_analysis_memo_v2/packets/`; saved generation rows are in `E6/submission_v1/generations.jsonl`; saved TEST evaluations are under `E6/runs/heldout_accuracy_optimized_v1/`. No generation, inference, scoring, protocol modification, or human judgment was performed for this analysis.

## Evidence classification

**Record-based observations** below are directly checkable in the saved packet, generation, or evaluation records: exact output text, question text, label/text pairs in the 20 TRAIN examples, saved invalid/refusal counts, and missing cells. **Interpretations requiring human review** are marked “candidate” or “review question”: whether an output is scientifically unsupported, hallucinated, redundant, misaligned, or harmful. Synthetic TRAIN labels are not independent semantic ground truth. A counterexample in this small input set can contradict a universal/strong directional wording within the set; it cannot establish population-level falsity.

## Concrete examples for the nine data cases with saved generations

The seven fully supported cases are 0017, 0011, 0013, 0015, 0014, 0012, and 0008. Cases 0019 and 0009 are partial. The linked reading packet has each case’s full 20-example input, available arm outputs/questions, arm omissions, and the evaluation artifact link.

### 1. Directional claim contradicted by examples in its own input set

**Case** `hypobench-synthetic-election-level2:TRAIN-SET:0011:a26c8c80a830`, **arm D, H2**: “Expressions of frustration regarding third-party debate presence are more frequent among users likely to vote Republican.” The frozen 20-row packet’s targeted count, also recorded in the existing Task 3 evidence table, finds four rows mentioning debate presence, split 2 Republican-labelled and 2 Democratic-labelled. This is a **record-based within-sample contradiction** to the stated directional frequency claim, not a human judgment or population estimate. The exact observations and their recorded labels are in [`data_133dd7a854d9398b.json`](data/error_analysis_memo_v2/packets/data_133dd7a854d9398b.json); generation rows 391–432 include D H2.

A related **scope limitation, not a contradiction**: **D H4**, “Advocating for universal healthcare, alongside criticism of mainstream parties, indicates a likely Democratic voter.” In this input packet, matching examples include Democratic-labelled rows (observations 5 and 8; source rows 287 and 1321), while no exact conjunction with a Republican-labelled record was found in the saved 20 rows. This is not an independent validation: the examples are synthetic, the conjunction is sparse, and the file alone cannot establish how well the claim generalizes. Source: packet observations in [`data_133dd7a854d9398b.json`](data/error_analysis_memo_v2/packets/data_133dd7a854d9398b.json).

### 2. Unsupported scope / overgeneralization candidates

These are not certified errors. They show where the saved wording makes a stronger claim than the included records alone can establish and merit manual review:

- **0017, QH H1**: “Tweets explicitly endorsing a candidate are stronger predictors of voting preference than sentiment expressed towards related policies.” The linked QH question asks for a comparison of predictive strength, but this single synthetic TRAIN set does not itself provide a validated predictive comparison. Saved text is at [`data_8f9b6e0d6d660a93.json`](data/error_analysis_memo_v2/packets/data_8f9b6e0d6d660a93.json); see QH generation rows 631–672. Record fact: it is a comparative “stronger predictors” claim. Whether its output is unsupported in the full experiment requires outcome-aware human review.
- **0015, D H1**: “Tweets expressing support for non-voting as protest correlate with a higher likelihood of Republican voter identification.” This generalizes a relation from the small synthetic TRAIN input. It is a saved claim, not proof of a model error; compare against the 20 examples and see the saved D output in [`data_15882043d59f01a1.json`](data/error_analysis_memo_v2/packets/data_15882043d59f01a1.json) / generation rows 559–600.
- **0008, QH H1/H2**: the two claims compare explicit candidate endorsements with event reactions (“stronger predictors” vs. predictive power diminishing with negative event reactions). Both are broad predictive-effect claims. The text establishes what was generated, not their empirical validity; saved packet [`data_06f934aaaf59bfed.json`](data/error_analysis_memo_v2/packets/data_06f934aaaf59bfed.json), rows 271–312.

### 3. Redundancy candidates

**0008, QH H5 and H6** reuse the same feature pair—advocating universal healthcare and championing gun rights—and both make a voting-preference prediction. H5 says it is more likely to predict Republican preference; H6 says the pair indicates a nuanced stance and is less reliable for a specific preference. The saved wording is objectively similar in subject and constructs; judging this as redundant versus a useful competing prediction is **subjective and requires human review**. Source: [`data_06f934aaaf59bfed.json`](data/error_analysis_memo_v2/packets/data_06f934aaaf59bfed.json), QH rows 271–312.

A second candidate: **0011 QH H1/H2** share the exact same saved research question about third-party endorsement and political affiliation, while H1 links endorsement to conservative values and H2 links it to frustration with the two-party system. The duplicate question is an objective record fact. Whether these are redundant hypotheses or distinct mechanisms is a reviewer judgment. Source: [`data_133dd7a854d9398b.json`](data/error_analysis_memo_v2/packets/data_133dd7a854d9398b.json), QH rows 391–432.

### 4. Question-to-hypothesis mapping for review

**0011 QH-sel H6** is a concrete candidate misalignment. Its saved question asks about the relationship between condemning Republican shutdowns and **non-voting as protest**, including universal healthcare and Second Amendment opinions. H6 instead states that shutdown-condemners often advocate universal healthcare and defend Second Amendment rights, “reflecting complex political views”; it omits the question’s non-voting outcome. The text pairing and omission are objective record observations; whether the omitted outcome makes the hypothesis materially misaligned is a reviewer judgment. In the same case, QH H1 and H2 share one exact broad question but advance different correlates (conservative values versus two-party frustration), an objective duplicated assignment and a separate candidate for reviewing question specificity. Source: [`data_133dd7a854d9398b.json`](data/error_analysis_memo_v2/packets/data_133dd7a854d9398b.json), QH and QH-sel generation entries.

For contrast, **0008 QH H1** is textually aligned to its question: both compare explicit endorsements with event reactions. This is a useful negative example against overcalling every arm mapping as a mismatch. The question and output are linked in packet [`data_06f934aaaf59bfed.json`](data/error_analysis_memo_v2/packets/data_06f934aaaf59bfed.json).

### 5. Refusals and missing outputs

**Saved evaluation observation:** each present cell has 501 TEST assignments. Across all saved cells there are 45,354 invalid predictions / 62,625 observed assignments (72.42%); 45,324 (72.37%) match the saved local connection-refusal text exactly. In the seven complete data cases, all six non-D-empty arms show 0/501 correct and 501 invalid; D-empty shows 139/501 correct and 1 invalid. This is a repeatable output/serving validity failure signal, not evidence that generated hypotheses are false. The refusal classification is exact-text matching and does not establish service-side cause.

**Per-case missingness:** 0019 lacks QH-sel; 0009 lacks D; 0007 has no saved generation or per-set evaluation at all. For 0019 and 0009, six arm evaluations are present; the available non-D-empty cells show 0/501 correct and 501 invalid, while D-empty shows 139/501 correct and 1 invalid. Do not treat those absent cells as zero. The exact evaluation paths, cell denominators, and other set-level missing cells are in the JSON index and reading packet. All ten literature cases lack saved arm generations and per-case evaluations; no literature error example or outcome is claimed.

### 6. Across-arm comparison and controls

The saved records allow descriptive comparison of generated text and outcomes, but do not settle “Does selection add anything beyond decomposition?” Paired D−QH is +2.32 percentage points (16 complete pairs; 95% input-set bootstrap [0.00, 5.70]); QH-sel−QH-rand is −0.27 pp (16 pairs; [−0.79, 0.00]). Both intervals touch zero, and invalid-response rates differ substantially by arm. The data therefore do not establish an advantage from selection. The D-empty and D-shuffled controls also do not behave as predicted by point estimates: D-empty has 27.74% accuracy versus D 5.00%, while D-shuffled has 8.09%; D-empty’s 0.20% invalid rate versus ~84–88% for other arms confounds interpretation. These are saved numerical outcomes, not proof of control validity or scientific superiority. The preregistered literature comparisons remain unobserved.

## Most frequent detectable failure and an automatic detector

The most frequent observed failure is invalid response output, dominated by exact local connection-refusal strings: 45,324 of 62,625 observed assignments. A deterministic detector can flag (a) missing arm/input-set cells from planned-versus-present IDs, and (b) invalid prediction rows from the saved `invalid_reason`/parse-validity field, with a separate exact-text match category for known refusal strings. Report invalid and missing denominators by arm and set; never substitute missing for invalid or impute either as incorrect. This detector identifies operational validity failures, not hallucination or semantic error. The existing saved-metrics JSON and evaluation files contain these fields; no detector was run as part of this report.

## Coverage, status, and what remains

- **Nine data cases have generations:** seven complete and two partial. Examples above are evidence-grounded and explicitly separate record facts from review hypotheses.
- **Eleven cases cannot be evaluated for generated-output error:** data 0007 plus ten literature cases. Their absence is missing evidence, not a model error.
- **Human review remains 0/20 cases and 0 coded arm cells.** The dated manual review form is blank. No human labels, semantic ground truth, or independent verification are claimed.
- Consequently, the full rubric requirement to read all 20 cases end-to-end and give a human error analysis is **not complete**. Literature decomposition performance, selection benefit, and whether controls behaved as they must cannot be judged from the unavailable outputs; data controls are numerically unfavorable but operationally confounded.
- Genuine manual review must assess grounding, hallucination, redundancy, question type/alignment, and cross-arm differences from the nine available cases, record quotations and evidence for each judgment, and mark the other eleven “Cannot evaluate — saved arm outputs missing.” Reviewers should not use the synthetic TRAIN labels as external truth.

## Reproduction / verification

From the repository root, inspect the frozen case packets and saved evaluations; the existing read-only command for held-out summary/hash verification is:

```sh
python3 E6/reproduce_saved_heldout_accuracy.py
```

This reproduces only summaries of existing saved outputs; it does not perform semantic review or generate/scoring new predictions. Full case text is in `E6/reading_packet_2026-11-17.md` in the submission checkout; exact metrics and artifact hashes are in `E6/post_hoc_saved_metrics_2026-11-17.json` there.
