# E2 continuation protocol — 2026-11-13

This protocol is committed before the new computations it specifies. Original
E2 manipulation results and R2 labels were already inspected. It is prospective
only for the new computations below, **not a blind preregistration** of E2 or
R2, and does not erase previous benchmark exposure. Original scores and claims
remain immutable. No Ollama, accelerator inference, E6 control or network calls.

## Cached manipulation extension

Use only original focal selections with 4–10 claims. Recovered claims remain
separate candidate sets until semantic/atomicity review; do not use them in this
new analysis. Every exclusion is reported. Retain all three original subfields.
For each focal, take its manifest pool, remove the focal and same-normalized-
abstract duplicates, require publication strictly before focal posting time,
and retain only exact title-plus-abstract embeddings in the existing cache for
`specter2_base+proximity-adapter+cls-v1`. Report missing cached papers, not impute.

Set k=min(100, floor(eligible_cached_count/2)); require k>=2. Near/far are the
first/last k by descending cosine similarity to the focal, with lexical ID ties.
Older/newer are the first/last k by publication time, with lexical ID ties.
The two members of each contrast are disjoint and have equal sizes. This
cache-available design differs from the original full candidate corpus.

Use existing Y, N, yours=0.75Y+0.25N and density formulas without tuning or
encoder inference. Higher scores indicate novelty. Predictions: near<far and
newer<older for each measure. These are empirical hypotheses, not universal
axioms (especially newer<older). Count pass if left<right-1e-8; ties fail.
Report numerator, valid denominator, exclusions, ties, mean paired difference,
and 95% percentile intervals for pass rates and differences from 10,000 paired
paper resamples, seed 20261113. The unit is a distinct focal paper, not a claim.
Report per-pool counts too. No changes after looking at these new outcomes.

Nearest-paper coverage constructors must replace, rather than append beside,
cloned nearest eligible originals. Plant ceil(m*p/100) claims in extraction
order for p=25/50/75/100. All synthetic interventions must be identified as such;
no original publication is represented as actually containing planted claims.
Plan and audit may be written now; modified-paper embeddings are missing, so
coverage scores must remain absent unless genuinely computed separately.

Paraphrase support preserves saved candidate titles, abstracts, provenance and
acceptance records. Do not infer human approval from an AI review. Existing
`scoring_authorized=false` flags are preserved. The user's current continuation
request permits preparing evaluation support, but does not supply missing
embeddings or establish complete 300-paper paraphrase coverage. Emit blocked
cases when embedding or meaning-preservation evidence is unavailable.

## Human check

Keep the existing Task 3 chronological ridge design, alpha grid and paired
bootstrap specification unchanged. Never select hyperparameters or score
orientation on R2 outcomes. Prior R2 exposure must remain disclosed in any
result; no assertion of blind prospective validation is permitted.

Before held-out numerical evaluation, require genuine item-level posting dates,
a documented encoder cutoff, disjoint training/test IDs and overlap exclusions,
frozen abstract-only embeddings with source/model revisions and text hashes,
and saved four-measure benchmark predictions with a frozen eligible literature
pool and claims. Hash and freeze all evaluation inputs before execution.
Do not manufacture dates from venue years. If these conditions fail, do not
execute human-check AUROC analysis, even though this document is committed.

Exact abstract-only cache reuse and small CPU-only historical embedding batches
are permitted as preparation. CPU preparation must use local model files,
one thread, low priority, separate outputs, no title-plus-abstract substitution,
no Ollama or accelerators, and no changes to the existing cache. Never label
partial matrices complete. Stop preparation on missing local model assets or
resource uncertainty; it does not justify disrupting the running E6 job.
