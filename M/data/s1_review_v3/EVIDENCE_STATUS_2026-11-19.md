# S1 evidence status — 2026-11-19

Scope: repository and existing E1/M artifacts checked; reviewer files and existing sources copied byte-for-byte into `M/data/s1_review_v3/recovered_evidence_2026-11-19/`. No frozen protocol, original source, review file, result, or experiment was modified. No scoring or inference was run.

## 1. Evidence found

- **Question text, source versions, paper IDs, and hashes:** the E1 source `E1/contrast.jsonl` has 61 question records with question variants, item IDs, source paper IDs, and author codes. The S1 `annotation_manifest.jsonl` has 122 pair records with pair SHA-256, exact E1 source record path/line/offset/record hash, and source-context hash. E1 paper metadata includes paper IDs, publication dates, URLs, and abstracts. The local Git history has 61 commits touching `E1/contrast.jsonl`, covering item commits from 2026-10-20T10:33:01+05:30 through 2026-10-21T21:11:06+05:30 (see the exported history file). These are **local commit timestamps**, not verified question creation/posing or public-availability dates; the E1 checkout has no configured remote.
- **Original question dates:** none verified. All 122 S1 manifest rows have null `question_available_at` and `question_publication_date`. Paper dates do not establish question dates.
- **Inputs and controls:** no original input IDs or versioned input-pool records were found for these S1 pairs; all 122 `original_input_ids` values are null. E1 contrast rows contain question variants, not original/empty/shuffled input conditions or same-topic decoy provenance. No verified S1 four-control mapping was found.
- **MiniLM:** the existing preparation lock records revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` and exact model-file hashes. The revision-pinned model card describes its training sources and procedure but does not state a cutoff date, so it cannot establish the required training-data cutoff. [Pinned model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/README.md).
- **Human reviews:** completed Reviewer A and B files are present and byte-preserved. Each has 122 rows with the required fields populated; reviewer IDs are `arpit_singh_revA` and `revB_human_eval_02`. Both files contain `reviewer_kind=human` and `independent_of_author=true` self-attestations. No separate record confirming that they are distinct humans or that they worked independently of each other was found; the self-attestations are not treated as proof.

## 2. Added evidence copies

The following source files were copied byte-for-byte. Exact source paths, destination paths, sizes, and SHA-256 hashes are in `recovered_evidence_2026-11-19/source_copy_manifest.json`.

| Copied evidence | Original source path | Destination |
|---|---|---|
| Reviewer A completed JSONL | `/Users/arpit/Downloads/reviewer_A_completed.jsonl` | `recovered_evidence_2026-11-19/reviewer_A_completed.jsonl` |
| Reviewer B completed JSONL | `/Users/arpit/Downloads/reviewer_B_completed.jsonl` | `recovered_evidence_2026-11-19/reviewer_B_completed.jsonl` |
| E1 question source | `/Users/arpit/asi-selection/E1/contrast.jsonl` | `recovered_evidence_2026-11-19/E1_contrast.jsonl` |
| E1 paper metadata | `/Users/arpit/asi-selection/E1/results_v2/source_metadata.csv` | `recovered_evidence_2026-11-19/E1_source_metadata.csv` |
| S1 encoder preparation lock | `M/amendments/S1_encoder_preparation_lock.json` | `recovered_evidence_2026-11-19/S1_encoder_preparation_lock.json` |
| E1 local Git history export | `/Users/arpit/asi-selection/.git` history for `E1/contrast.jsonl` | `recovered_evidence_2026-11-19/E1_local_commit_history.tsv` |

The existing S1 annotation manifest and blank reviewer packets remain at their original paths and were not copied or changed.

## 3. Still missing

1. Authoritative creation/posing and availability dates for each E1 question version.
2. Exact original supplied-paper/input IDs, versions, hashes, and availability-before-question evidence.
3. S1-linked empty, cross-instance shuffled, and independently verified same-topic decoy inputs and provenance.
4. Authoritative training-data cutoff evidence for the pinned MiniLM checkpoint/base model.
5. Direct, independently verifiable confirmation of reviewer identities and independence from each other and the original authors.
6. A new eligible cohort, locked encoder/threshold configuration, and four-control prediction sources. These cannot be frozen until the missing evidence is supplied and eligibility is established.

## 4. Scoring eligibility

**Not eligible; original S1 scoring remains blocked.** The current manifest marks all 122 pairs ineligible, and the missing temporal, input/control, model-cutoff, and reviewer-independence evidence cannot be inferred from paper dates, source IDs, Git timestamps, model revision dates, or reviewer self-attestations. The frozen protocol and prior amendment remain unchanged.


## Read-only update — 2026-11-19T18:47:50+05:30

A targeted search of `M/data/s1_review_v3/recovered_evidence_2026-11-19/` and `/Users/arpit/Downloads/` found **no completed or signed Reviewer A/B confirmation forms**. The only S1 forms present are the blank templates `reviewer_A_independence_confirmation_FORM.md` and `reviewer_B_independence_confirmation_FORM.md` in the recovered-evidence directory. No completed form was copied. The Downloads files `completed_review_form.json` and `reviewer_2_AI_assisted_review.json` use a different paper-rating/association-review schema and are not these S1 confirmation forms.

Fresh read-only validation of `/Users/arpit/Downloads/reviewer_A_completed.jsonl` and `/Users/arpit/Downloads/reviewer_B_completed.jsonl`: A 122/122 and B 122/122 rows; parse errors A/B 0/0; missing/invalid required rows A/B 0/0; source or manifest mismatches A/B 0/0; duplicate pair IDs A/B 0/0; malformed timezones A/B 0/0. Recorded IDs are `['arpit_singh_revA']` and `['revB_human_eval_02']` (distinct: True); judgment disagreements: `same_question` 0, `source_alignment_verified` 0. File SHA-256 values remain A `97bfdf64cdc8dfe06b5e1136723e5ed53c49c50b7877dac4cd2b6333e0ca7c20` and B `c600f3b62d0a616ac93275f19dbe821a8f1330979263d02299547f88974c6b78`.

These results establish structural validity and unchanged source binding only. They do **not** establish actual human identity, reviewer independence, non-use of AI, truth of timestamps, or independence from E1 authors. Until completed forms and independent verification evidence are provided, the human-review independence requirement remains **UNVERIFIED**. No S1 scoring was run; the original gate remains blocked by this and the previously listed provenance/control/cutoff gaps.

## Follow-up: authoritative MiniLM source check — 2026-11-19

A focused check of the exact pinned [MiniLM model-card revision](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/README.md) found that it lists the fine-tuning dataset families and says the model was developed during Hugging Face's JAX/Flax Community Week. The [official event announcement](https://discuss.huggingface.co/t/open-to-the-community-community-week-using-jax-flax-for-nlp-cv/7104) schedules the event for July 7–14, 2021. The linked [MiniLM base-model card](https://huggingface.co/nreimers/MiniLM-L6-H384-uncased) does not provide a complete pretraining-data snapshot or cutoff.

This establishes useful development-period context, but not an exact training-data cutoff bound to the pinned weights: the cards do not identify dated snapshots for all corpora or the base-model pretraining data. Under the existing frozen amendment, the cutoff therefore remains **UNVERIFIED**, and this requirement still fails. Details are preserved in [`S1_MINILM_CUTOFF_FOCUSED_REVIEW_2026-11-19.md`](recovered_evidence_2026-11-19/S1_MINILM_CUTOFF_FOCUSED_REVIEW_2026-11-19.md). This follow-up did not change the protocol, generate vectors, or run scoring.
