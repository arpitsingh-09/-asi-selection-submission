# Original S1 evidence collection guide

This guide explains what evidence is needed to complete the existing inventories. It is an instruction document, not evidence. Do not infer missing values or recreate historical records. Preserve source files unchanged and give every received source a stable path and SHA-256.

## 1. E1 question history

Fill `E1_QUESTION_HISTORY.csv`, one row per question (`h001` through `h062`, excluding `h028`). Keep the question ID and existing question wording/version reference intact unless an original source proves a correction. The current `exact_question_text` cell preserves all seven E1 variants as a JSON object.

- `question_version`: exact original version label or archive/version identifier. The recorded `first_observed_local_git_commit` is only the earliest version found in this local repository; it is not proof that the question was first created then.
- `creation_timestamp`: actual time the question was created/posed, in ISO 8601 with timezone, for example format `YYYY-MM-DDThh:mm:ss±hh:mm`. Use only a contemporaneous record that directly establishes this event.
- `sharing_timestamp`: actual time that exact version was shared or became available to the relevant reviewers, with timezone. Cite the dated email, export, platform event, or archive record.
- `original_source_path`: path to the original contemporaneous source, not merely this inventory or a later recollection.
- `source_sha256`: SHA-256 of the preserved supporting source record. Keep a separate checksum for any attachment if the timestamp record and question text are in different files.
- `timestamp_evidence_path`: path to the source that supports both timestamps, or leave blank if a timestamp is unsupported.
- `evidence_status`: `VERIFIED` only if the original version and required dates are directly supported; `PARTIAL` if a genuine version exists but one or more required dates/links are absent; otherwise `MISSING` or `UNVERIFIED`.

Git commit metadata may be retained as Git evidence, but must not be entered as a question creation or sharing time unless a contemporaneous source explicitly says that is what the timestamp records.

## 2. Original supplied paper inputs

Fill `E1_PAPER_INPUTS.csv` with **one row per paper actually supplied for each question**. A question with multiple supplied papers therefore has multiple rows. Do not copy an associated `source_arxiv` value into this file unless a contemporaneous input record shows that the paper was actually supplied.

Required for each input row:

- `paper_id`: stable ID used in the original run (arXiv ID, DOI, or original local ID).
- `paper_version`: exact version supplied (for example arXiv v1 or a dated PDF revision).
- `paper_sha256`: hash of the exact supplied bytes, not a hash of a later download.
- `paper_availability_date`: the documented date/time the exact version was available to the question author, including timezone where recorded.
- `original_input_manifest_path`: contemporaneous manifest or run record that binds this paper/version to the question.
- `availability_evidence_path`: dated archive, email, repository, or platform record proving availability of that exact version.
- `evidence_status`: mark `VERIFIED` only when identity, version, hash, original-input binding, and availability are all supported; use `PARTIAL`, `MISSING`, or `UNVERIFIED` otherwise.

If no original input manifest exists, keep these fields blank and leave the row `MISSING`. Do not substitute a current paper copy, abstract match, or publication date.

## 3. Four registered S1 conditions

Fill the existing four rows per question in `E1_S1_CONTROLS.csv`. Evidence must be from the original run or a preserved contemporaneous record.

- `original`: exact paper IDs, versions, and source record for the original input condition.
- `empty`: source record showing the condition actually contained no input papers; preserve and hash the exact serialized empty payload/configuration.
- `cross_instance_shuffled`: identify `source_question_id` (the other instance), every paper ID/version, and the original shuffle/assignment record. Preserve source-instance IDs; do not create a shuffle now.
- `same_topic_unsupported_decoy`: identify exact paper IDs/versions and original source record. `independent_decoy_verification_path` must point to an actual independent review that establishes both same-topic relevance and that the decoy does not support the target claim.
- For every condition, `source_sha256` is the SHA-256 of the preserved exact source record/payload. `evidence_status` is `VERIFIED` only if the condition and all required provenance are supported.

Do not fill a row using a newly assembled condition and present it as original. If an original record is unavailable, leave unsupported cells blank and use `MISSING` or `UNVERIFIED`.

## 4. Reviewer identity and independence

The existing files `reviewer_A_independence_confirmation_FORM.md` and `reviewer_B_independence_confirmation_FORM.md` are blank. Each actual reviewer must complete and sign their own form; do not edit their judgment JSONL. A responsible independent verifier must complete the verifier section using evidence independent of the self-attestation.

The verifier must resolve whether Reviewer A (`arpit_singh_revA`) is the person represented by E1 author code `AS`, verify each reviewer's identity, confirm the reviewers are distinct, and check whether either authored any reviewed question. Record source paths/hashes for the verification evidence. Do not infer identity from a name-like ID.

## 5. Exact MiniLM checkpoint cutoff evidence

The pinned encoder revision is `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Obtain an authoritative record from the model publisher/training authors that binds to the exact weights/revision and documents both:

1. Fine-tuning dataset names, exact snapshots/versions, and latest included data date/cutoff.
2. The exact base-model checkpoint and its pretraining dataset snapshot(s) and cutoff.

Save the source response/document unchanged, record its source URL/path and SHA-256, and state which exact revision it covers. A release date, model-card publication date, or general statement about training era is not cutoff evidence.

## 6. Evidence receipt and validation

When records arrive, preserve each original in this directory without editing it. Record the provider, date received, original source location, byte size, SHA-256, question IDs covered, and exact requirements supported in the handoff manifest. Keep a record `PARTIAL` or `UNVERIFIED` if any required link is not established. Update the aggregate question counts only after checking all 61 IDs and all 122 S1 pair bindings.

The current blockers are not resolved by completing this guide. Original S1 remains blocked from locking/scoring until every mandatory requirement is supported and the prospective lock is prepared under the frozen protocol.
