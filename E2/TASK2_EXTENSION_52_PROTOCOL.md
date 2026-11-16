# Separate E2 cache-only 52-paper extension preregistration

Recorded 2026-11-13, after inspection of the earlier 241-paper development
results and before ranking or scoring this extension. This is prospective for
these new computations only. It is not a blind study or a preregistration of
the earlier experiment. No previous preregistration is modified or backdated.
The user explicitly authorized this cache-only Task 2 experiment and this commit.

## Frozen cohort and inputs

Use exactly the 52 records marked `claim_independent_Y_density_ready=true` in
`analysis/claim_completion_v2/task2_reuse_readiness.json`, in their saved order.
Their full IDs, cutoff dates, existing pool identities, cached reference IDs,
pair sizes and input/code SHA-256 bindings are fixed in
`analysis/task2_extension_52_cohort_v1.json` (SHA-256
`c2323e060f1d8f8166ac353e078658ff82aec85ebe11ce10b4773922284a1bcb`).
The cohort is selected for cache availability and count-eligible future claims,
including AI-reviewed additions/revisions. This differs from the earlier cohort's
original-claim selection, but Y and density do not consume claims. All 52 IDs
must be disjoint from the existing 241. Fail closed on changed fingerprints,
missing/corrupt vectors, duplicate IDs, chronology violations or cohort mismatch;
report the blocker rather than changing the cohort or imputing scores.

The cohort manifest binds the scorer, tests, existing constructors and original
score implementation. Before any evaluation the protocol, manifest, scorer and
tests must all be committed unchanged. Record that commit in every new summary.
Existing root preregistration, 241-paper results, original scoring outputs,
embedding cache, notebook/AI log and frozen E2 execution plans are read-only and
hash-checked before and after. No E6 file or process is controlled or modified.

## Representation and manipulations

Reuse only exact `title.strip() + '\n\n' + abstract.strip()` normalized float32
CLS vectors for `specter2_base+proximity-adapter+cls-v1`, using the existing SQLite
cache opened with `mode=ro`. Validate text/hash binding, finite 768-dimensional
vectors and unit norm with the existing cache reader. No model import, model
initialization, inference, embedding generation, download, Ollama or accelerator.
Use one CPU/BLAS thread and bounded arrays. This is development manipulation
evaluation, not the held-out human check.

Use each focal's existing subfield manifest and exactly its frozen cached-prior
candidate IDs. Exclude the focal ID and abstracts equal to the focal under the
existing case/whitespace normalization; require each real publication timestamp
strictly earlier than the focal cutoff. Do not manufacture dates. Deduplicate IDs.
This preserves the previous study's duplicate-abstract exclusion convention;
no new deduplication of distinct reference IDs with similar abstracts is added.

Set k=min(100,floor(eligible_cached_count/2)), requiring k>=2; use the saved pair
size without tuning. Reuse `manipulation_extensions.select_pools`: sort by
similarity descending with lexical ID ties, take first k as near and last k as
far; sort by publication date ascending with lexical ID ties, take first k as
older and last k as newer. Preserve ordering within each chosen pool. Each
contrast has equal-size disjoint members. Save the selected IDs separately.

## Scores and predictions

Use the previous numerical conventions exactly: Y=1-max clipped cosine;
density is Relative Neighbour Density percentile on 0–100, P=100/Q=50 capped to
n/n-1, stable neighbor sorting, self excluded from reference density, equality
included in the percentile. The pure NumPy implementation is checked against
AST-loaded original pure functions on synthetic arrays without importing torch.
No tuning of formulas, orientation, neighbors or tolerance from new outcomes.

Four primary contrasts and predictions:

| Measure | Per-paper prediction | Cohort prediction |
|---|---|---|
| Y | near < far | More than half pass |
| density | near < far | More than half pass |
| Y | newer < older | More than half pass |
| density | newer < older | More than half pass |

Temporal decrease is an empirical hypothesis, not a universal axiom. Near/far
uses the same geometry as scoring and is not independent semantic validation.
For every contrast, pass iff left-right < -1e-8. Ties within 1e-8 fail; all other
outcomes fail. Record numerator, denominator, ties, rate and mean paired
difference. Do not turn a failed prediction into another orientation.

## Intervals and reporting

Resample distinct focal papers with replacement, keeping each paper's paired
condition scores together: 10,000 draws, NumPy default_rng seed 20261113, 95%
percentile intervals (2.5/97.5) for pass rate and mean paired difference.
Use contrast order near/far then newer/older, measure order Y then density;
continue one RNG stream across those four rows, restarting it for each separately
reported cohort. Batch index arrays at 250 replicates for bounded memory. No
bootstrap of claims, separate condition resampling, p-value tuning or stopping.
Report per-subfield sample counts. Intervals are conditional on the fixed
cache-available design, not independent random literature samples.

Save new 52-paper results and pool selections in a fresh versioned directory.
Retain earlier 241-paper rates exactly as saved, without rerunning their scores.
A pooled **descriptive** Y/density summary is permitted only after verifying
unique/disjoint cohorts, the same model/text representation, formulas,
chronological pool construction, k convention, ordering and pass rule. Report
its paired-paper bootstrap separately and disclose heterogeneous claim-screening
stages and prior exposure. Do not call the pooled 293 a single prospectively
registered or blind cohort. Do not pool N/yours or incompatible original coverage
manipulations with these results. Report N/yours coverage as unchanged at 241.

## Follow-on preparation boundary

After evaluation, query existing claim vectors read-only for the 53
count-eligible additional focals in readiness, deduplicate missing exact stripped
claim texts by SHA-256, and record per-paper/index bindings. The minimal request
set for N/yours on the 52 ready papers is the union of their missing hashes.
Record additional requests specific to the one prior-pool-blocked paper
separately; do not infer absent claims for the six evidence-limited papers.
Save an exact future execution plan with source/model hashes and representation
requirements; do not execute inference while E6 is active. Claim vectors alone
do not supply modified-paper vectors or missing reviewed paraphrases. No claim
that all remaining Task 2 requirements are resolved is permitted.
