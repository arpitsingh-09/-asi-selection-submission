# E1 Tasks 1–4: saved-evidence completion note (2026-11-16)

**Status:** Dataset construction passes the recorded mechanical checks; the saved evaluations support exploratory results. E1 is **not fully compliant or confirmatory** because mandatory provenance/recheck evidence is incomplete and the saved cross-encoder does not meet the instructed-judge requirement. This note supplements existing outputs and does not change the frozen preregistration or overwrite previous results.

## Task 1 — Items and provenance

- `E1/contrast.jsonl` contains 61 rows, above the 60-item minimum. All seven question-text fields (A, B, B_min, C, C_tilde, narrower, broader), type, and required row metadata are present; no row failed `E1/validate_all.py`’s structural/Jaccard checks. Type counts: inquiry change 11, role swap 10, direction flip 14, constraint flip 16, goal swap 10. The validator counts 43 W-longer-than-N examples (18 not flipped); the evaluation tokenizer records 39, as the frozen preregistration already notes.
- Saved source metadata records 61/61 arXiv sources as found, first posted from 2025-01-22 through 2026-10-20, with all marked date-eligible. This verifies the recorded paper/date metadata, not the fidelity of each hand-written A to the source question.
- The required 24-hour self re-check is only partly evidenced: NOTEBOOK.md explicitly records a completed re-read of h031–h062, while the earlier items have dated notes and due dates but no complete item-by-item completion record. `source_alignment_audit.csv` marks all 61 source/question alignments `PENDING_MANUAL_CONFIRMATION`; the single fixed extraction prompt is not preserved. Therefore semantic/source validity and full re-check completion cannot be certified from current artifacts.
- All 61 `second_reader_agrees` entries are null. The second reader for 20 items is explicitly optional in the assignment, so this is not a required-task failure; no independent judgments are claimed.

## Task 2 — Model results

Existing per-item result files cover all 61 IDs. Saved configurations include four required embedder families—E5, BGE, MiniLM, and SPECTER2—and the additional Qwen3 primary model. The SPECTER2 figures below use the corrected `allenai/specter2_base` + `allenai/specter2` proximity adapter, CLS-token configuration; the earlier SentenceTransformers default-pooling file is retained but superseded.

Rates below are percent of 61 source-paper clusters; brackets are 95% percentile source-cluster bootstrap intervals (5,000 resamples). The four specified error/shortcut metrics follow `eval_contrast_v2.py`; scope is its exploratory unnormalized-norm order W < A < N. The length-only baseline is the script’s token-count order. Per-type estimates and intervals are in [`saved_evidence_analysis_2026-11-16.json`](results_v2/saved_evidence_analysis_2026-11-16.json).

| Model (saved ID/configuration) | Near-miss error | Overlap shortcut | Low-overlap shortcut | Scope order | Length-only baseline |
|---|---:|---:|---:|---:|---:|
| E5-base-v2 | 98.4% [95.1, 100.0] | 6.6% [1.6, 13.1] | 41.0% [29.5, 54.1] | 0.0% [0.0, 0.0] | 9.8% [3.3, 18.0] |
| BGE-base-en-v1.5 | 98.4% [95.1, 100.0] | 8.2% [1.6, 14.8] | 34.4% [23.0, 45.9] | 0.0% [0.0, 0.0] | 9.8% [3.3, 18.0] |
| all-MiniLM-L6-v2 | 96.7% [91.8, 100.0] | 16.4% [8.2, 26.2] | 42.6% [31.1, 54.1] | 0.0% [0.0, 0.0] | 9.8% [3.3, 18.0] |
| SPECTER2 corrected (base + proximity adapter, CLS) | 95.1% [88.5, 100.0] | 11.5% [4.9, 19.7] | 39.3% [27.9, 52.5] | 18.0% [8.2, 27.9] | 9.8% [3.3, 18.0] |
| Qwen3-Embedding-0.6B | 96.7% [91.8, 100.0] | 13.1% [4.9, 21.3] | 42.6% [31.1, 55.7] | 1.6% [0.0, 4.9] | 9.8% [3.3, 18.0] |


The cross-encoder has saved results for 61 items under `cross-encoder/ms-marco-MiniLM-L-6-v2`, but the implementation calls it as a generic passage-relevance pair scorer. It was not instructed to answer “Do these two texts ask the same research question?” as required. Its saved per-type/aggregate metrics are preserved in the analysis JSON as exploratory only; they do not satisfy the required instructed cross-encoder evaluation. No new model run was made because no compliant frozen model/prompt configuration is recorded.

## Task 3 — Prediction comparison

There is no defensible pre-evaluation numeric prediction in the frozen history: the early entries contain placeholders, and the 60% Qwen prediction and general-model range were recorded retrospectively relative to the development evaluation under the conservative PREREG clarification. Consequently, a formal preregistered prediction comparison cannot be claimed. Descriptively, Qwen’s saved near-miss error is 96.7% (59/61), about 36.7 percentage points above the retrospective 60% expectation; the four required embedding families range from 95.1% to 98.4%. This indicates the saved constructed set is difficult for these similarity systems, but does not establish performance on general research questions.

## Task 4 — Deduplication

The saved retrieval set has 61 queries, a 427-text candidate pool, top-10 retrieval, and 244 labeled target variants (122 positives B/B_min; 122 negatives C/C_tilde). Labels are the hand-constructed contrast labels, not independent human judgments. Results concern the four known variants per query, not every candidate in the pool.

Intervals below bootstrap the 61 query/source clusters, keeping each query’s four target variants together. Both thresholds were selected with hindsight on these same development examples; the intervals condition on those selected thresholds and do not correct selection optimism.

| Saved pipeline | Threshold | Precision (95% cluster CI) | Recall (95% cluster CI) | F1 (95% cluster CI) | Counts TP/FP/FN/TN |
|---|---:|---:|---:|---:|---:|
| Top-10 E5 + generic MS MARCO cross-encoder | -10.400358 | 50.5% [48.5, 52.5] | 83.6% [77.9, 89.3] | 63.0% [60.1, 65.6] | 102/100/20/22 |
| Best hindsight E5 cosine threshold | 0.167656 | 51.0% [50.2, 52.1] | 100.0% [100.0, 100.0] | 67.6% [66.8, 68.5] | 122/117/0/5 |

Before cross-encoder filtering, top-10 E5 retrieval found **83.6%** of positive B/B_min variants (95% source-cluster CI 77.9–89.3%; 102/122). The hindsight cosine baseline has slightly higher descriptive F1 and recall than the top-10-plus-cross-encoder pipeline; the latter’s top-10 gate misses 20 known positives. The comparison is optimistic and limited to this targeted contrast set.

## Completion and evidence limits

- **Task 1:** Mechanical constraints pass; source fidelity and all-item 24-hour re-check are not fully evidenced.
- **Task 2:** Embedder analyses are available for the four required categories and Qwen; the required instructed cross-encoder evaluation is missing. Saved embedding point estimates, cluster intervals, length-flipped scope results, and per-type breakdowns are in the JSON artifact.
- **Task 3:** Retrospective descriptive comparison is documented; a genuine preregistered comparison is unavailable.
- **Task 4:** Top-10 retrieval, generic cross-encoder threshold pipeline, and hindsight cosine comparison are recomputed from saved results with query-cluster intervals. This is not a compliant instructed-cross-encoder evaluation or fully labeled-pool deduplication result.

**No held-out test file was opened, no inference or training was run, and no existing result or preregistration was changed.** Hashes of the source and result inputs are recorded in the analysis JSON.


## Addendum — same-question model eligibility and retrospective source review (2026-11-16)

### Part A — Same-question cross-encoder: blocked by the frozen configuration

The official requirement is an instructed cross-encoder that decides whether two texts ask the same research question. The frozen E1 model list names `cross-encoder/ms-marco-MiniLM-L-6-v2`, and the frozen record explicitly characterizes it as a passage-relevance baseline, not a question-identity model. `E1/eval_contrast_v2.py` calls `CrossEncoder.predict((A, candidate))` without an instruction prompt or same-question decision configuration. No alternative model ID, instruction text, threshold rule, model revision, or approved evaluation configuration for an instructed same-question cross-encoder is recorded.

Therefore a compliant run is **not eligible under the frozen protocol**. Adding an instruction to this generic scorer or choosing another model would silently change the model/task configuration. The existing saved generic cross-encoder and deduplication results remain descriptive; no new cross-encoder inference was run, no raw predictions were created, and no old output was replaced. The 61-item development set is available, and the held-out file was not accessed, but that does not resolve the missing compliant model configuration.

### Part B — Fresh retrospective source review

I reviewed each of the 61 A questions against its matching locally saved arXiv abstract in `E1/results_v2/source_metadata.csv`. The per-item record in [`source_question_review_2026-11-16.csv`](source_question_review_2026-11-16.csv) gives the review date, status, source ID/title/official arXiv URL, a record-and-field locator, and the supporting abstract-based evidence note. All 61 are marked **verified for semantic alignment with the saved abstract**; none was rejected or left unresolved for that narrow alignment check.

For all 61, `provenance_status` remains **unresolved**: the saved material does not establish the exact author-authored research question, the single fixed extraction prompt, or the historical manual-edit trail. This review is an AI-assisted retrospective check of saved abstracts, not an independent human review or proof of historical authorship. It is not represented as the required historical 24-hour re-check. The earlier audit and notebook were preserved unchanged.

### Reproduction instructions

From the submission repository root, the mechanical checks and saved-output analysis can be reproduced with:

```sh
python3 E1/validate_all.py
python3 E1/analyze_saved_results.py
```

The second command recomputes cluster-bootstrap summaries from the existing item-level result JSON; it does not load a model. The saved raw model outputs are the files referenced in `E1/results_v2/` and `E1/results_specter2_corrected/`. Do not use `E1/eval_contrast_v2.py` as a reproduction command for this report: it runs inference, writes into the existing `E1/results_v2/` directory, and only invokes the generic MS MARCO relevance scorer. Exact pinned model revisions and full execution-environment records are not available for reproducing those historical raw scores.

### Current completion status

- Mechanical item constraints: passed; 61 rows.
- Saved-abstract alignment: completed as a new retrospective AI-assisted review for all 61 items.
- Historical fixed-prompt, manual-edit provenance, and full 24-hour re-check: unresolved; no retrospective claim added.
- Four embedder categories plus Qwen: saved development outputs and cluster-bootstrap analysis available.
- Required instructed same-question cross-encoder and its deduplication pipeline: blocked because the frozen protocol specifies only the explicitly non-instructional relevance baseline and records no compliant alternative.
- Task 3: descriptive comparison only; no verified pre-evaluation numeric predictions.
- No held-out test access, inference, training, Main Problem edits, or changes to frozen data or prior model outputs.
