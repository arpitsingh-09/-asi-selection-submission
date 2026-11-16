# Independent literature review handoff

Distribute `reviewer_A/review.md` only to reviewer A and `reviewer_B/review.md` only to a different reviewer B. Have each return their document privately to the coordinator before comparing answers. These local directories do not enforce access permissions. Keep coordinator outputs outside both reviewer directories.

Each reviewer completes 20 cases and all seven checks per case: 40 reviews / 280 checks overall. Read the frozen guide included in each document. Edit only `review-response` JSON blocks. Record identity, UTC completion time, Boolean judgments, a brief rationale and source quote/location per check, source notes, error/correction lists, and manual completion. No human answers have been prefilled.

Problem/method/result annotations are currently missing. Follow the frozen guide: record omissions and negative checks, or arrange separately attributed source-component annotations in a new version and prepare renewed source-bound review. Do not silently fill or overwrite the original model extraction or packets. Matching negative judgments do not make the annotation usable.

From the repository root, after receiving the private completed documents:

```sh
python3 E6/literature_review_documents.py ingest \
  --reviewer-a E6/data/literature_reviewer_documents_v1/reviewer_A/review.md \
  --reviewer-b E6/data/literature_reviewer_documents_v1/reviewer_B/review.md \
  --output /tmp/e6-literature-coordinator-review.json
```

The output must be a new file. `issues` lists missing or invalid review fields; `adjudication_required` lists genuinely disputed checks only for complete review pairs. Its blank adjudicator fields are not completed adjudications. `matching_negative_cases_require_correction` identifies concordant failures. The actual input records are retained under `records`; nothing is written to original evidence or TEST files.

For each disputed case, give the coordinator report and source packet to an independent third adjudicator who differs from both reviewers. Record all seven final Boolean checks, identity, UTC date/time and rationale, retaining the supplied `review_records_sha256` binding. Final acceptance must use the existing `literature_finalization.validate_review_records` / `validate_review_bundle` workflow, and `literature_source_components.validate_component_reviews` for completed attributed sidecars. Ingestion itself never authorizes scoring. Corrections require versioned annotations and renewed review.

Current baseline: 0/40 human reviews complete; 0/280 checks answered; no genuine disagreements yet. Software checks field completeness and evidence bindings, not real-world identity, independence, or scientific truth.
