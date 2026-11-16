# E2-informed A1 replication — supplementary registration

**Status:** registration text prepared for approval; not committed or authorized
for scoring. This is a new supplementary evaluation, not an unchanged execution
of frozen A1. The original `M/PREREG.md` and `M/frozen/A1_test_list.json` remain
authoritative and untouched. Existing E2 outcomes and this already-selected
candidate cohort are known development material; this is an exposed replication,
not a blinded or independent confirmatory test.

## Cohort and provenance

The 50-paper cohort in `cohort_manifest.json` was selected from cached
`E2/data/raw_papers.jsonl` by the manifest's seeded SHA-256 ranking (seed 49),
after excluding the 300 original E2 focal IDs and the successfully scored
focals recovered by joining result case IDs to the E2 manipulation plan. Each
record binds its arXiv ID/version, title, publication/update/retrieval dates,
URL, source line and byte offset, source-line and file hashes, and abstract
hash. The selection is prospective in date only; it is not a frozen registered
test cohort.

Focal text is the exact E2 form `title + "\n\n" + abstract`. R is constructed
as all IDs in `E2/data/pool_manifest.csv` for the focal paper's E2 `pool`, with
valid source text and publication time strictly earlier than the focal paper,
excluding the focal ID and duplicate normalized abstracts as the E2 eligibility
function does. The pool manifest SHA-256 is
`e36009be0e3d8991175cc91ac93f661633b82a9f4d1959a425eb6b513991f104`.

This is an explicit deviation from original A1's recovered author-supplied
input references: the source records do not contain such R sets. The study
tests E2's corpus-pool operationalization and will not describe R as
author-supplied. The synthetic manipulated papers are interventions, not
historical publications; E2's `cutoff - 1 second` timestamps are intervention
ordering values only and must never be cited as actual publication or
availability dates.

## Prior exposure and directional expectations

E2 history is exposed. `E2/data/scoring_results.jsonl` contains 2,400 successful
condition records mapped to 300 focal papers and the existing plan defines
baseline, exact-copy, coverage-25/50/75/100, concentrated, and distributed
conditions. The MATMUL pilot contains 10 successful records. The E2 extension
report documents prior coverage of 293 Y/density records and 241 N/custom
records; these are prior results and must not be pooled with this cohort.
The E2 plan predicts decreases in Y, density, N, and `yours` for synthetic
coverage interventions. The existing E2 report defines concentration as
concentrated < distributed; retrospective counts were Y 216/300, N 0/300,
`yours` 96/300, and density 26/300. These prior outcomes motivate the
replication but are not new predictions or independent evidence. The
concentration results make outcomes uncertain, especially for N and density.

## Conditions and manipulation fidelity

For each focal instance, fix the partial-coverage levels at 25%, 50%, 75%, and
100%, using the existing E2 claim-order construction rule. Fix concentration
as the complete claim set placed in one synthetic prior-work item; fix
distribution as one claim per synthetic item. Retain the unmanipulated original
pool as the reference. Also prepare an explicitly empty pool, a shuffled pool
from a different eligible focal instance, and a distinct same-topic decoy
question evaluated against the original input pool. The new M adapter labels
the empty-pool score undefined because E2 `novelty.score` rejects an empty
eligible pool; it will never insert a numeric substitute.

Existing `primary_pool_category` metadata supports reproducible decoy
candidate selection: require the same category and use ascending
SHA-256(`49|focal_id|decoy_id`) as the deterministic tie-break. The dataset has
only broad classes (`cs.CV`, `cs.LG`, `cs.CL`), so category matching alone does
not establish semantic same-topic validity. The original M preregistration
requires an independently verified same-topic decoy and provenance; that
validation remains mandatory. Keep all four control outputs separate and
paired by focal-paper ID.

## Model, normalization, and baseline

Reuse the E2 novelty implementation without changing it: SPECTER2 base
(`allenai/specter2_base`, cached commit
`3447645e1def9117997203454fa4495937bfbd83`; config SHA-256
`6d9d68ca2bfeca756fd807e7c81e8e9d3203d8a002dff19cc42b29edd48e8802`; weights
SHA-256 `801eda968fad1752fe846a8e572bfdc25202be85544680dda4c99f4589646ebc`)
with proximity adapter (`allenai/specter2`, cached commit
`2081559630a80fc5851d8f798a05ba81e9468089`; config SHA-256
`1065ad610a661c5169f05d81040fe14429d2cc7ecdf83ed654dca4a62aaf9a8c`; weights
SHA-256 `5b6105714f78b294daa7e2d181134df12f0acb7a4ec7c1e3c13e512c908db94a`).
Tokenizer file hashes are checked by the M adapter against the local Hugging
Face cache before scoring. It forces offline loading and uses a new revision-
named cache at `M/a1_replication/novelty_embeddings_3447645_2081559.sqlite3`;
it will not use the existing E2 embedding cache, whose key omits model
revisions. The adapter also checks E2 `novelty.py` SHA-256
`30276aee4718359840fe72b143ccfccc7c166c74f5dcb5c0953fdd48fbd5215c`.

Use CLS pooling, max length 512, and L2-normalized encoded vectors. The reported
coordinates are Y, density, N, and `yours` (custom = 0.75 Y + 0.25 N). Density
uses the implementation's RND settings P=100 and Q=50. E2 has no fitted
feature-normalization stage; cosine inputs are unit normalized. The claim
extractor uses `deepseek-r1:8b`, prompt `atomic-claims-v8`, temperature 0, and
`num_predict=2800`; its local Ollama model digest must be recorded before
extraction. The original A1 primary statistic has no separate learned baseline:
the unmanipulated original pool is its reference condition. Do not add B-TF or
another post-hoc baseline to the confirmatory criterion; any supplementary
baseline must be specified and locked before scoring.

## Outcomes, pass criteria, and uncertainty

For partial coverage, compare baseline to 25%, then adjacent levels 25→50→75→100;
a pass is a strict decrease in novelty (positive signed delta, no tie credit).
For concentration, use E2's contrast concentrated < distributed, encoded as
distributed score minus concentrated score. Coordinates are Y, density, N, and
`yours` (custom = 0.75Y+0.25N). Report every coordinate and manipulation.
Preserve the original A1 pass rule: one same coordinate must have a lower paired
95% confidence bound >=0.80 on both partial coverage and concentration. The
E2 history was inspected before registration, so this is an exposed replication.
Use focal paper as cluster, paired percentile bootstrap, 2,000 draws, PCG64 seed
20261113, retaining all conditions within a cluster. Require at least two
independent focal clusters; >5% undefined replicates blocks inference. Controls
are diagnostic. Empty-pool scores remain undefined and are excluded from
numeric pass fractions, never imputed.

## Claim and missing-data rules

Only the existing title-plus-abstract extraction procedure may be used for
this registration. A record is eligible for scoring only if the extracted set has
4–10 distinct atomic claims, each with an exact supporting abstract excerpt,
and validation records are complete. Fewer/more claims, invalid evidence
spans, missing source text, malformed output, or any missing required
condition makes that focal record an extraction/control failure; log the
reason before scoring and do not replace it based on model outcomes. Preserve
the selected 50-row manifest and report exclusions. Do not impute absent
scores; undefined empty-pool scores remain explicitly undefined and are not
included in numeric axiom fractions.

## Temporal and approval gates

Every real source paper in a nonempty input pool must have a verified version
and publication timestamp strictly earlier than the focal paper. Re-filter
original and shuffled pools at each focal timestamp; for a decoy, all reused
original inputs must also predate that decoy question. Exclude focal IDs in the
original E2 focal list or any E2 scored-result history. Before scoring, obtain
the independent same-topic verification required by the original M
preregistration, complete claim/source validation, record the extractor model
digest, obtain approval, and commit this separately versioned registration,
cohort, and control code. The E2 pool deviation is fixed above; it does not
repair or alter original frozen A1. No claim extraction, model call, or scoring
has been authorized or run during preparation.
