# Task 3 execution preparation — 2026-11-13

This freezes an implementation plan before any new Task 3 inference or numerical
human-check evaluation. Prior benchmark labels were inspected; this is not blind
prospective validation. Current user authorization is **preparation and offline
tests only**: no inference, embedding job, model loading, or held-out evaluation.
The older continuation protocol remains unchanged. Read-only official publisher
commit pages were consulted to resolve model provenance; execution stays offline.

Inputs: use the exact 299 recovered forum IDs, labels and original archived
abstracts in recovered_inputs_v1, and its fixed 25,186-paper reference manifest.
Preserve the original/edited abstract distinction. The primary representation
for Task 3 is **original abstract only** for both novelty and quality; raw CLS for
ridge, unit-normalized copies for cosine-based novelty. This differs from the
old E2 manipulation experiment's title-plus-abstract representation. It is fixed
before new human-check outcomes, and must be disclosed with any eventual result.
Do not silently substitute benchmark edited ideas or titles.

Encoder: base revision 3447645e1def9117997203454fa4495937bfbd83 and proximity
adapter 2081559630a80fc5851d8f798a05ba81e9468089. Fingerprint local model assets.
Official HF commit pages place both revisions on 2024-12-04. Use 2024-12-31 end
of day UTC as a conservative weights-existence upper bound, **not an exact
training-data cutoff**. The October 2025 OpenReview dates are later, but earlier
preprints and archived abstract revisions still need an explicit eligibility
review before asserting post-cutoff evaluation. No automatic eligibility waiver.

CPU preparation: local files only; CPU, float32, evaluation mode, raw final CLS,
512-token cap, one intra-op/inter-op thread, batch size 2 by default, dynamic
length padding. Deduplicate exact text hashes and resume validated rows in a
new SQLite cache. Commit each batch. Limit records per invocation; no automatic
large job. Lower process priority before importing/loading a model; fail closed
if unavailable. Check explicit future inference authorization and plan/protocol
hashes before any model load. Current authorization template disables execution.

Claims: export 299 empty source-bound requests, without labels/ratings, and
import only supplied saved/reviewed claim+verbatim-excerpt records. Validate forum
IDs, original-abstract hashes, nonempty claims, duplicates and exact evidence.
No new extraction model or invented claims. A complete 299-paper claim file is
required before scoring all four novelty measures. Changing claims changes the
plan hash and requires an updated authorization/freeze before inference/scoring.

Novelty: use the existing four formulas, orientations and weights. Shared fixed
reference pool excludes every test paper and the four conservative historical
overlap candidates. Require each reference public date strictly before every
test public date. Y=1-max cosine; N=1-mean claim max cosine; yours=.75Y+.25N.
RND P=100, Q=50, self-excluding neighbor densities and existing small-pool caps.
Calculate neighbor densities in row blocks, memoize each reference density, and
never allocate a full 25,186-square matrix. Blocked formulas must match the old
implementation on synthetic fixtures. No tuning on benchmark scores or labels.

Quality baseline: original raw abstract CLS only; predict historical mean
numeric official-review rating. Keep the existing nine alphas and expanding
2022->2023, 2022-23->2024, 2022-24->2025 folds. Train-fold scaling/intercept,
pooled validation MSE and first/lowest alpha for exact ties. Reuse fold sufficient
statistics/eigendecomposition across alphas for efficiency; refit on all eligible
history. Never use test ratings, contribution, labels or novelty predictions in
model fitting or selection. Check training IDs, dates, text hashes and same venue.

Evaluation: requires a separate explicit future evaluation authorization, frozen
plan/protocol fingerprints, supplied eligibility-review evidence and verified
preregistration for these new computations, with prior exposure disclosed.
Use 10,000 paired class-stratified bootstrap samples, seed 20261113, percentile
95% intervals for each AUROC and each novelty-minus-quality AUROC difference.
No equivalence claim from an interval crossing zero. Refuse partial caches,
missing claim sets, reordered IDs, stale text/model hashes and overwritten output.

Resource estimates must be labeled estimates, not measurements. Benchmark a small
future authorized batch before budgeting the complete job. Do not touch E6 or
Ollama, request an accelerator, download a model, or auto-start any job.
