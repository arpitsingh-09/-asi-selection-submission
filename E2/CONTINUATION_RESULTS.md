# E2 continuation from b784a39

Work performed on 2026-11-13. Task 1 remains partial, Task 2 remains partial,
Task 3 remains blocked, and Task 4 remains complete. **Not submission-ready.**

## Preregistration and preservation

`CONTINUATION_PROTOCOL.md` was committed as `a8364cd` before any new cached
manipulation results were computed. It fixes selection, exclusions, equal pool
sizes, score orientation, comparisons, tie rule, seed and bootstrap scheme.
Original E2 results and R2 labels had already been inspected: the new protocol
is prospective for these new computations, not a blind study of E2 or R2.
No held-out human-check evaluation was executed. No E6 or Ollama operation was
invoked. No network requests or new model inference occurred. All numerical
work used one CPU/BLAS thread. Lowering process priority was denied by the
sandbox; cache-only arithmetic completed without loading a model.

`cached_extensions_v1/summary.json` records unchanged SHA-256 hashes for the
original selected claims, pool manifest, raw papers, embedding database, and
both protected scoring outputs. Neither `run_scoring.py` nor the existing
manipulation generator was run. Original artifacts and Task 4 were preserved.

## Claim recovery: source-backed additions, not inflated counts

`recover_claims.py` inspected all 58 original short sets against saved
extraction artifacts, including saved raw LLM responses. Candidates retain
verbatim claim/evidence strings, filename, line number and source kind. Empty
or nonexact excerpts are rejected; same-excerpt restatements are deduplicated.
No claims were generated, and no original selection was changed.

The automated candidate screen found 57 distinct additional candidates. An
initial minimal selection contained 28 additions across 24 papers and brought
22 candidate sets to four. **Those are not the final accepted recovery counts.**
`review_claim_recovery.py` records a subsequent explicit Codex AI support,
redundancy and atomicity review of all 57 candidates. Many candidates merely
restated an original claim, supplied a more detailed version of an existing
result, described paper organization, or combined overlapping assertions.

The review retained **13 verbatim additions across 13 papers**. Ten short sets
now reach four in the separate future-use artifact; three improve but remain
short. Thus **48 of the original 58 still have fewer than four**, and 252/300
future sets have 4–10 claims by count. The original experiment still has its
original 58 short sets. Background assertions are identified as background,
not presented as new contributions. Neither the new review nor a numeric
claim count establishes independent human validation of all claims.

Artifacts in `analysis/claim_review_v1/` include all decisions/reasons and
`claims_future.jsonl`. Every review is explicitly `reviewer: Codex AI` and
`human_review: false`. Prior manual-review requirements and original audit
values are retained in provenance. New exact-evidence audit counts are
recomputed. These future claim sets were **not used** in the new comparisons,
as specified before evaluation.

## New cache-only manipulation results

`cached_extensions.py` reads the existing SQLite database with `mode=ro` and
checks model ID, text/hash binding, vector shape, finite values and unit norm.
It never calls an encoder. Its score formulas match the existing `novelty.py`
interface in a direct fixture test; the existing pure RND helper is reused.

The new analysis includes **241 distinct focal papers**: 76 computation/language,
86 vision and 79 machine learning. It excludes all 58 original short claim sets
and one additional focal with fewer than four cached strictly prior papers.
Every comparison excludes focal IDs and duplicate abstracts. Candidate-cache
misses and chosen pool IDs are retained per paper. Each pair has equal size,
k=min(100, floor(n/2)), where n is the number of cached eligible prior papers.

| Strict predicted decrease | Y | N | yours | density |
|---|---:|---:|---:|---:|
| Near < far | 241/241 | 241/241 | 241/241 | 236/241 |
| Newer < older | 152/241 | 143/241 | 151/241 | 133/241 |

Full 95% percentile bootstrap intervals, mean paired differences, tie counts,
valid denominators and exclusions are in `analysis/cached_extensions_v1/summary.json`.
There are 10,000 paper resamples, seed 20261113; strict decrease requires a
change below -1e-8. Near selection uses the same embedding geometry as the
score, so this checks controlled response rather than independent semantic
validity. Temporal ordering is an empirical hypothesis, not a universal axiom.
These results cover a cache-available development subset, **not all 100 focal
papers per pool**. They do not repair the old experiment retrospectively.

## Nearest planting and paraphrase support

`analysis/cached_extensions_v1/nearest_planting_plan.jsonl` contains **964 unscored
plans** (241 papers x four coverage levels). Claims are assigned to their
nearest eligible paper in the cached geometry. Synthetic clones retain original
source provenance and replace their originals in the planned pool, so neither
pool-size inflation nor original-plus-clone duplication occurs. Tests inspect
every plan for replacement, focal exclusion and strict temporal eligibility.
No real prior paper was rewritten. Modified-paper embeddings are absent, so
no nearest-planting scores are asserted. `claims_future.jsonl` can support a
later separately frozen plan after its remaining review issues are resolved.

All five saved v33 paraphrase candidates are represented in a separate plan,
with recorded acceptance statuses and original `scoring_authorized=false`
flags preserved. None of their candidate texts has a matching cached embedding.
The API `evaluate_paraphrase` now supports a baseline and inserted-paraphrase
comparison using cached vectors, requires a recorded accepted review status,
and returns a blocker instead of a score when the vector is missing. The
calling workflow must establish protocol/authorization separately. It is
covered by synthetic tests; it was not used to invent any five-paper result.
A complete paraphrase condition for the other 295 focal papers is unavailable.

## Targeted Task 3 evidence and preparation

`task3_evidence.py` locates and validates the original nested-metadata YAML in
`~/Downloads/novelty-eval-main/data/human-only/pointwise.yaml`, as well as the
cached R2 Parquet. All 299 ideas and labels agree. The supplied title/forum CSV
resolves all 299 nested titles. It supplies no dates. The four historical ICLR
archives have no exact benchmark forum or normalized-title matches; existing
conservative semantic-overlap exclusions remain in force.

Historical OpenReview pdate, odate and cdate ranges are now recorded separately
in `analysis/task3_evidence_v2.json`. Latest available historical pdate is
2025-03-02 UTC. These fields are not silently substituted for one another.
Historical cohorts precede the ICLR 2026 benchmark cohort, but **zero test
posting dates were recovered**. Venue-year chronology is verified; item-level
train/test chronology and post-encoder-cutoff eligibility cannot be verified.

The targeted search of E1, E2, E4 and the downloaded benchmark/history sources
found no saved four-measure benchmark predictions or embedding matrices. None
of the 299 benchmark abstracts matches the model-specific novelty cache. That
cache also stores normalized CLS vectors, whereas the Task 3 protocol specifies
raw abstract-only CLS. Title-plus-abstract or normalized vectors were not
substituted for the required baseline representation.

`abstract_embeddings.py` implements resumable, exact-text-hashed abstract-only
preparation, pinned local SPECTER2 base/adapter revisions, 512-token raw CLS,
CPU-only execution, one thread, local-files-only loading and a separate cache.
It exposes historical preparation only; no benchmark scoring or test-label input
is passed to the encoder. Tests cover exact text, raw vector preservation,
resumption, validation and the no-model-load preflight boundary.

A `--max-new 1` historical preparation attempt stopped at `os.nice(15)` with
PermissionError **before any model loading or inference**. The committed
protocol requires low-priority preparation to protect the active E6 workload;
that requirement was not bypassed. `analysis/abstract_preparation_v1/status.json`
records **0/25,186 historical vectors**, zero test vectors, and the exact failure.
The matrices are still missing; a partial or nonexistent matrix is not a result.

Exact remaining human-check blockers:

- Verified item-level test posting dates and documented encoder cutoff.
- Complete, provenance-verified raw abstract-only historical and test embeddings.
- Frozen per-test eligible literature pools, benchmark claims, and four novelty
  prediction vectors; these are not recoverable from the manipulation results.

The continuation protocol is committed, but cannot erase prior test exposure.
Any future compliant analysis must disclose that limitation, freeze its inputs
before execution, and satisfy the evidence gates. No AUROC, ridge human-check
score, or novelty-minus-quality interval is claimed in this run.

## Validation

Offline unittest suite: **61 tests passed**. Coverage includes the pre-existing
suite, source-backed recovery/provenance, read-only cache access, score parity,
paraphrase missing-data behavior, all generated nearest plans, and CPU embedding
preparation/resumption. Existing urllib3/LibreSSL and sandbox sysctl warnings
were nonfatal. No experiments were rerun for testing.

Task 4's paragraph in `README.md` is unchanged. Submission still requires the
remaining claim sets, full mandatory manipulation coverage and scoring, and the
blocked human-check evidence/results. Nothing was pushed.
