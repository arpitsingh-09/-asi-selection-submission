# Task 3 first-publication review — local evidence

The current output is `analysis/task3_publication_review_v2/REPORT.md`.
`review.json` preserves all 299 original abstract hashes, observed releases,
source hashes/line numbers, identity decisions and unverified URL leads.
`review.csv` is the compact per-paper queue; `identity_candidates.csv` lists
older-title candidates and their dates relative to the model bound.
The original pending-review file is unchanged. The v1 directory is an
intermediate output from this implementation; use v2.

Results:

| Decision | Papers |
|---|---:|
| Automatically verified observed OpenReview release | 299 |
| Verified first global publication | 0 |
| Confirmed earlier preprint | 0 |
| Older-title identity candidates | 3 (4 records) |
| Unresolved publication history / manual verification required | 299 |
| Verified eligible relative to the conservative model bound | 0 |

The matching implementation is `task3_publication_review.py`. It scanned all
25,485 available historical OpenReview submissions for 2022–2025 (including
records excluded from the frozen 25,186-paper reference pool), the 3,000-record
arXiv cache, all 299 recovered benchmark notes and the human-only upstream
metadata for unverified link leads. Source content is fingerprinted in the
report. It checked the benchmark fingerprint against the recovered-input freeze
and checked pending-review coverage and hashes. Historical author metadata is
retained with candidates. Benchmark author identity is unavailable in the
recovered notes, which omitted original author/external-link fields. No cached
complete publication-history attestation was found in these sources.

Reliable release observations require an exact forum plus original-abstract
hash, or matching normalized title and whitespace-normalized original abstract.
Title-only historical matches remain candidates. Changed abstracts or alternate
titles can hide earlier versions; absence of a match is never evidence that
no preprint exists. Links in reviewer metadata may cite other work, so they
remain unverified leads and cannot establish paper identity or release date.
No arXiv dates are inferred from identifiers. Creation/modification timestamps
and venue years are not publication dates.

The four older candidate records concern Conjuring Semantic Similarity,
Hot PATE (two historical submissions), and Counterfactual Techniques for
Enhancing Customer Retention. Their historical release dates precede the
conservative end-of-December 2024 weights-existence bound. If exact paper
identity is confirmed, those papers fail the declared post-bound requirement.
Their differing abstracts and missing benchmark authors prevent automatic
identity resolution. These OpenReview observations are not labeled preprints.

The exact SPECTER2 training-data cutoff is still unknown. The saved publisher
commit evidence supports only a conservative weights-existence bound. Each
paper's report separately records bound-relative uncertainty and exact-cutoff
uncertainty. None is promoted to eligible merely because its archived October
2025 release follows that bound. Availability of the exact archived abstract
at first public release remains unverified.

The raw 489 MiB compressed archive was not decompressed; the already-recovered
records were used to respect the lightweight-only boundary. No network lookup,
model loading, embeddings, fitting, bootstrap or benchmark metrics occurred.
No existing execution code, frozen plan, score, dataset, checkpoint, E6 artifact,
root notebook or AI log was modified by this step.

Offline validation: **77 tests passed**, comprising 12 new publication-review
tests and the 65 existing lightweight continuation/Task 3 tests. Tests cover
release-versus-first-publication separation, earlier exact preprint detection,
title-only ambiguity, text/hash binding, date semantics, unchanged inputs,
and evaluation-gate rejection of unresolved review output.

Reproduction (new output directory required):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B E2/task3_publication_review.py --output E2/analysis/NEW_REVIEW_DIRECTORY
```

Exact next action: obtain primary author/identifier and first-version evidence
for the three flagged benchmark papers, compare it to the four historical
submissions, and record a human identity decision with source provenance. This
requires evidence absent from the inspected lightweight local sources; use
saved primary records if supplied, otherwise targeted primary-source retrieval.
Then extend first-publication/preprint verification to the other 296 papers,
including archived-text version checks. Do not update the frozen plan or enable
evaluation until eligibility and cutoff-policy blockers are resolved.
