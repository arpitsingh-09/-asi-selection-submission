# Offline evaluation handoff

No scoring evidence is created by implementation. Current missing reviews remain
blocked. Frozen preregistration, settings, original artifacts, and active TEST
files are not modified. All filenames ending in `_actual` below require real
human or completed experiment evidence; they are not provided by these commands.

## Evaluator validation

`ingest_independent_review.py` ingests the existing ten-case Markdown sheet,
checks identity/date/rationale/example fields, and compares labels with saved
model predictions. Diversity `null` is a valid rubric abstention, distinct from
an unanswered label or false. Missing fields produce explicit incomplete status.
Completed pilot agreement still leaves researcher adequacy assessment pending:
no invented numeric acceptance threshold and no automatic `validated` status.
Existing configured evaluator execution gates continue to enforce this.

## Literature source reviews

Reuse the two private reviewer documents; pass genuine completed sidecars and
adjudications to the existing ingestion command:

```sh
python3 E6/literature_review_documents.py ingest \
  --reviewer-a E6/data/literature_reviewer_documents_v1/reviewer_A/review.md \
  --reviewer-b E6/data/literature_reviewer_documents_v1/reviewer_B/review.md \
  --components E6/data/literature_components_actual.json \
  --adjudications E6/data/literature_adjudications_actual.json \
  --output E6/data/literature_review_ingestion_actual.json \
  --export-dir E6/data/literature_reviews_validated_v1
```

Omit `--adjudications` when there are no genuine disagreements. Component entries
must be attributed and source-bound, and each review must bind their exact digest.
If the annotation version changes, renew the reviews; never silently rebind them.
The ingestion report is written even when export is blocked. Pending/negative
reviews never export as accepted evidence. Both reviewers' answers and combined
reports belong only to the coordinator until independent submission is complete.

Final validation reuses `literature_finalization.validate_review_bundle` and
`literature_source_components.validate_component_reviews`. It enforces all seven
checks and the existing independent-third-adjudicator policy. Export contains raw
`actual_review_records.json`, `actual_adjudications.json`, component sidecars,
validation results and `review_bundle_paths.json` in the existing six-path schema.
The exported paths can be bound through the existing legitimate scoring signoff
process; no frozen configuration is automatically rewritten. Source-review
acceptance alone does not bypass missing evaluator validation.

## Completed outputs and statistics

The existing explicit completed-artifact index remains the input to
`error_analysis_memo.py`: literature generation envelopes use kind
`generation_checkpoint`, `reconstruction.json` uses `literature_reconstruction`,
and each `<arm>_secondary.json` uses `secondary` with its arm. Completed data
summaries use `train_evaluation`. Every indexed file has its source SHA-256.
Do not index or scan an active run.

Separately compiled, genuinely scored HDR payloads now join via
`--hdr-compilation`. The adapter verifies the existing compilation, binds each
payload to its original successful TRAIN hypotheses and ground truth, recomputes
HDR with `bound_hdr_score`, and rejects conflicting scores. Unscored cells remain
pending; empty HDR inputs never turn into zero values.

```sh
python3 E6/error_analysis_memo.py \
  --artifact-index E6/data/completed_evaluation_index.json \
  --hdr-compilation E6/data/hdr_scoring_completed_v1 \
  --reviews E6/data/error_reviews_actual.json \
  --output-dir E6/data/error_analysis_memo_completed_v1
```

All arguments here refer to future completed evidence. Statistical summaries
continue to use the existing per-input-set scalar adapter, frozen bootstrap and
complete-pair rules. Missing/failed observations stay unavailable. Reconstruction
and secondary output schemas already match that adapter; fixture tests cover the
native literature output handoff and the separate HDR handoff.

Remaining evidence: independent evaluator labels plus adequacy assessment,
literature source/component reviews and any adjudications, actual HDR definition
and judgments, seven-arm literature outputs, and actual end-to-end error coding.
No script can legitimately replace these with automatic approval.
