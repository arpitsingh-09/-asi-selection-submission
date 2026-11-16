# Supplementary S1-style comparison on exposed E1 contrasts

**Status: FROZEN SUPPLEMENTARY PREREGISTRATION.** This is an explicitly
exploratory supplement. It does not authorize inference or scoring and does not amend or complete original
S1, replace its frozen cohort, or support an unseen-data claim.

## Question and exposure

Compare the fixed M identity readout and a fixed semantic embedding baseline on
the creator-intended minimal paraphrase and near-miss relationships in the E1
contrast set. E1 contrasts and E1 model results were already exposed before
this draft. The M preregistration itself calls existing E1/E2 results
development material (`M/PREREG.md`, lines 3–6), and E1 previously evaluated
multiple embedding encoders on `E1/contrast.jsonl`. Treat every result here as
exploratory and exposed, not confirmatory.

## Cohort and deterministic selection

Input records are `E1/contrast.jsonl` and
`E1/results_v2/source_alignment_audit.csv`. Join `contrast.id` to
`audit.item_id`; retain a record iff the audited source publication date parses
as ISO `YYYY-MM-DD` and is on or after `2025-07-01`, and fields `A`, `B`,
`B_min`, `C`, and `source_arxiv` are all nonempty. Sort retained records by
`id` ascending. This yields 60 records and 60 distinct source papers. The one
excluded record is `h004`, dated `2025-01-22`.

Input SHA-256 values at drafting:

- `E1/contrast.jsonl`: `57f95f7690746d3b22670434410c4ce80894b42f0f8dc504cac58f7d9cdaedcc`
- `E1/results_v2/source_alignment_audit.csv`: `45786a684a0c5bb5abfa12c74e9aed5e1cdb111f6a9b933fcdb09c1a77615218`

The frozen selection-list serialization is one UTF-8 line per selected record,
sorted by `id`, formatted exactly as `id<TAB>source_arxiv<TAB>date<LF>`.
SHA-256 of those 60 lines, including the final LF, is
`af485191ba1464153c6d2812e77e1bd54f06db32f12ba5ab99751393778b727e`.

| E1 id | Source paper | Publication date |
|---|---|---|
| h001 | 2610.26863 | 2026-10-19 |
| h002 | 2610.26847 | 2026-10-19 |
| h003 | 2610.26817 | 2026-10-19 |
| h005 | 2609.17863 | 2026-09-15 |
| h006 | 2604.19764 | 2026-03-26 |
| h007 | 2602.17445 | 2026-02-19 |
| h008 | 2610.08680 | 2026-10-06 |
| h009 | 2608.06422 | 2026-08-05 |
| h010 | 2507.23341 | 2025-07-31 |
| h011 | 2610.20288 | 2026-10-14 |
| h012 | 2610.26974 | 2026-10-18 |
| h013 | 2610.27773 | 2026-10-20 |
| h014 | 2610.27030 | 2026-10-19 |
| h015 | 2607.13192 | 2026-07-14 |
| h016 | 2610.27280 | 2026-10-19 |
| h017 | 2610.27140 | 2026-10-19 |
| h018 | 2610.22599 | 2026-10-15 |
| h019 | 2610.27214 | 2026-10-19 |
| h020 | 2610.14238 | 2026-10-09 |
| h021 | 2602.16315 | 2026-02-18 |
| h022 | 2609.05279 | 2026-09-04 |
| h023 | 2609.36855 | 2026-09-29 |
| h024 | 2610.19712 | 2026-10-14 |
| h025 | 2604.25096 | 2026-04-28 |
| h026 | 2510.20039 | 2025-10-22 |
| h027 | 2605.29278 | 2026-05-28 |
| h029 | 2609.37631 | 2026-09-29 |
| h030 | 2606.31166 | 2026-06-30 |
| h031 | 2606.21406 | 2026-06-19 |
| h032 | 2609.35479 | 2026-09-28 |
| h033 | 2609.02811 | 2026-09-02 |
| h034 | 2606.13675 | 2026-06-11 |
| h035 | 2609.02653 | 2026-09-02 |
| h036 | 2608.22701 | 2026-08-24 |
| h037 | 2605.19881 | 2026-05-19 |
| h038 | 2608.05464 | 2026-08-05 |
| h039 | 2609.15014 | 2026-09-14 |
| h040 | 2609.10221 | 2026-09-09 |
| h041 | 2609.23525 | 2026-09-20 |
| h042 | 2609.32874 | 2026-09-26 |
| h043 | 2608.27394 | 2026-08-27 |
| h044 | 2608.17271 | 2026-08-18 |
| h045 | 2609.05079 | 2026-09-04 |
| h046 | 2609.33357 | 2026-09-27 |
| h047 | 2610.19159 | 2026-10-13 |
| h048 | 2606.12736 | 2026-06-10 |
| h049 | 2608.16951 | 2026-08-16 |
| h050 | 2609.09203 | 2026-09-05 |
| h051 | 2610.18449 | 2026-10-13 |
| h052 | 2610.08927 | 2026-10-06 |
| h053 | 2610.00084 | 2026-09-07 |
| h054 | 2610.21082 | 2026-10-15 |
| h055 | 2608.25286 | 2026-08-26 |
| h056 | 2610.18933 | 2026-10-13 |
| h057 | 2604.25256 | 2026-04-28 |
| h058 | 2606.13662 | 2026-06-11 |
| h059 | 2606.07591 | 2026-05-28 |
| h060 | 2607.28631 | 2026-04-18 |
| h061 | 2606.15497 | 2026-03-31 |
| h062 | 2605.08323 | 2026-05-08 |

The date filter uses source publication dates only. It does not establish when
the E1 questions were authored or posed, and it does not confer eligibility for
the original M temporal test cohort.

## Labels and readouts

Use the E1 contrast construction intent as **unverified author-assigned
labels**. For each selected source question `A`, label `B_min` as intended
same-question (1) and `C` as intended different-question/near-miss (0). The
data identify the E1 author code, but `second_reader_agrees` is null for these
records; no independent relationship verification is claimed. These labels
measure agreement with creator intent, not verified semantic truth. Bootstrap
intervals do not account for possible label error.

- **M identity:** use the existing M hash identity score unchanged. Predict
  same iff cosine/similarity is at least `0.65`; otherwise predict different.
  Do not alter its threshold or implementation.
- **B-Q:** use `intfloat/e5-base-v2`, Hugging Face revision
  `f52bf8ec8c7124536f0efb74aca902b2995e5bcd`. Encode every `A`, `B_min`, and
  `C` symmetrically with the exact prefix `query: `, the cached Sentence
  Transformers configuration and pooling, and L2-normalized embeddings. Pair
  similarity is cosine similarity. Predict same iff cosine is at least `0.65`.
  This operating point is fixed by inheriting the already frozen M identity
  threshold, without calibrating on these records. It is not a calibrated E5
  threshold; report this limitation. Do not tune it.

## Outcomes and analysis

For each source question, score two tasks separately: minimal edit (`A` vs
`B_min`, intended label 1) and near-miss (`A` vs `C`, intended label 0). For
each task report accuracy for M and B-Q and paired difference
`accuracy(M) - accuracy(B-Q)`. No pooled accuracy is a primary result.

Bootstrap the 60 source questions as clusters, keeping both comparisons and
both systems paired within each sampled question. Use 2,000 paired percentile
bootstrap draws, PCG64 seed `20261113`, and report point estimates and 95%
intervals. The fixed comparison margin is `0.02`. Report whether each task's
lower interval bound exceeds `0.02` as an exploratory benchmark only; this is
not an original S1 pass or completion.

Freeze the cohort, labels, encoder revision, prompts, normalization, decision
thresholds, metric, bootstrap, and exclusions before any new scoring. Report
all 60 records and missing/invalid inputs. Do not change the protocol, remove
items based on predictions, optimize thresholds, or select among encoders after
seeing results. Any implementation or input failure is reported as such; no
replacement records are allowed.

## Interpretation limits and status

This is an exposed supplementary analysis with creator-intended, unverified
labels. The same E1 contrasts were previously used for encoder evaluation;
results cannot establish prospective generalization, independent label
validity, or completion of original S1. No original frozen protocol or E1 data
is changed. This preregistration is frozen by this commit. A separate explicit
authorization is required before inference or scoring.
