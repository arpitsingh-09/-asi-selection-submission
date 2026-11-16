# Essential local recovery from 44077c4 — 2026-11-13

**Task 3 remains blocked; E2 is not submission-ready.** This run resolves the
missing local OpenReview records and reference-pool inputs. It does not repeat
previous scoring or run any new model inference.

## Task 3: three major inputs recovered

The original `~/Downloads/iclr.tar.bz2` contains
`data/iclr_2026/papers.jsonl` as well as the earlier years. Previous checks had
covered only the extracted historical directories. The archive was streamed
without extracting it; its SHA-256 fingerprint is recorded in
`analysis/openreview_archive_v1/summary.json`.

All **299 benchmark forum IDs** match archived notes, and all titles agree
under normalization. Those notes provide:

- **299 full paper abstracts** with source identities and raw timestamp fields.
- **299 OpenReview public-release timestamps**, all
  **2025-10-08T04:11:45.795+00:00**, from the earlier available positive odate or
  pdate. Creation/modification timestamps were not substituted for publication.
- A dated test manifest retaining the existing **154 positive / 145 negative**
  benchmark labels; labels were not regenerated from reviews or judged anew.

These dates establish release through OpenReview, **not the first appearance
of each paper anywhere**. Earlier arXiv versions are not ruled out. The encoder
cutoff/release bound for the pinned weights still lacks verified evidence, so
post-encoder-cutoff eligibility is not asserted.

Earlier same-venue reviews and full abstracts already support **25,186 eligible
historical papers** after the four conservative exclusions. Their chosen public
release dates all precede every recovered test OpenReview date; the latest is
**2024-10-05T05:26:21.204+00:00**. The separate pdate field can be later than
online release (the previous report's 2025-03-02 maximum was a pdate maximum).
The newly frozen `analysis/recovered_inputs_v1/reference_manifest.csv` records
IDs, source lines, dates, date fields, and original-abstract hashes for this
strictly prior same-venue reference pool. Test IDs are excluded. Publication
date filtering establishes paper-level eligibility; it does not independently
prove that every archived abstract revision was already available at that date.

### Important representation correction

R2's `idea` field is **model-edited**, not the full original abstract. This is
explicit in the downloaded source `data/README.md`, and the
`remove_eval_data.jinja2` template removes results, baselines and evaluation
information. Only **14/299** R2 ideas exactly equal the archived abstracts
(19 after whitespace normalization). Editing and possible note-version changes
must not be silently conflated.

`analysis/recovered_inputs_v1/benchmark_inputs.jsonl` preserves both the edited
idea and the archived source abstract, with separate hashes and source labels.
`evaluate_human_check.py` now requires original abstracts and aligned
`test_abstract_sha256` before fitting the baseline. A regression test ensures
that an edited-idea hash cannot stand in for an original-abstract hash.

### Exact remaining blockers

1. Verified encoder training-cutoff or defensible release-bound evidence for
   the pinned weights; OpenReview dates alone do not exclude older preprints.
2. Complete raw abstract-only historical and test embedding matrices. Existing
   title-plus-abstract/normalized cache vectors are not substitutes. New
   inference is prohibited in this run, so none was attempted.
3. Benchmark atomic claim sets and four novelty prediction vectors. Reference
   **paper records are now available**, but those model-specific scoring inputs
   and outputs are not.

The previously committed continuation protocol is preparatory and discloses
prior test exposure. Recovering the original abstracts introduces a material
representation distinction: any future evaluation must freeze which texts feed
novelty versus the quality baseline, bind their hashes, and satisfy the existing
eligibility/provenance gates before execution. No held-out scoring, AUROC,
ridge fit or bootstrap human-check comparison ran in this session. No metric
was fabricated. Task 3 is **not executable under the current inputs/constraints**.

## Task 1: three further short sets completed for future use

The earlier recovery deduplicated by evidence excerpt as well as claim text.
That can hide independent assertions supported by the same sentence. This run
reviewed 45 previously filtered saved claim strings, without generating new
claim text. Three distinct, source-supported additions were retained:

- `2112.14983v1`: recurrent prediction in the CNN/RNN architecture.
- `2302.00595v1`: differentiable graphics/neural rendering in agent training.
- `2412.20666v2`: real-image comparisons, distinct from the retained synthetic
  image result.

`analysis/shared_excerpt_recovery_v1/` records verbatim claims, excerpts, saved
source filenames/line numbers, and explicit **Codex AI** decisions. These are
not human judgments. The separate cumulative future artifact now has **255
sets with 4–10 claims by count**, leaving **45 below four**. Count compliance
alone is not independent semantic validation. Original selected extractions
and the experiment's original 58 short sets remain unchanged. None of the
recovered claim sets was evaluated.

## Task 2: no additional cached condition is executable

The 964 existing nearest-paper plans were checked for exact modified-paper
embedding availability: **zero** have all required vectors. **1,304 distinct
modified text embeddings are missing**. The five saved paraphrases also lack
cached vectors, as established previously; their statuses were reused rather
than scoring them. No new inference was launched.

Remaining mandatory work is therefore scored nearest-paper planting, complete
paraphrase coverage, and extension of the existing 241-paper near/far and
temporal comparisons to the required focal coverage. Existing pass rates and
original scoring outputs are preserved; `E2/run_scoring.py` was not run.

## Validation and preservation

**69 offline tests passed**, including date semantics, exact forum joins,
original/edited abstract separation and hash binding, strict reference-date
filtering, and saved-source provenance for the additional claims. All six
protected original source hashes remain unchanged. Task 4's interpretation
was preserved. No E6 or Ollama operations were invoked, and nothing was pushed.
