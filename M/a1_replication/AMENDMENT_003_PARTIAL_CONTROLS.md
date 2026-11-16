# Amendment 003 — Partial supplementary evaluation without decoy control

**Status: APPROVED PROSPECTIVE AMENDMENT.** Approved 2026-11-14 for the
supplementary A1 partial replication. Scope is limited to the evaluation
described below. This approval does not authorize scoring before the independent
claim-review and other preregistered readiness gates are satisfied.

## Scope and retained cohort

This amendment changes only the supplementary E2-informed A1 replication in
`M/a1_replication/PREREG_REPLICATION.md`. It does not change, replace, or
reinterpret the original `M/PREREG.md` or frozen `M/frozen/A1_test_list.json`.
Results must be reported as an exposed, partial supplementary replication using
the E2 pool operationalization, not as an unchanged, complete, blinded, or
independent execution of original A1.

Retain the frozen 50-paper cohort and its manifest without substitutions.
Preserve all source papers, extracted claims, validation records, original
decoy proposals and review records, Copilot suggestions, and human-review
template unchanged. Report the 43-paper/217-claim review packet as a subset
available for review; do not infer missing claim records for the other seven
cohort papers.

## Conditions and missing decoy

Retain the original-pool reference, empty-pool diagnostic, and shuffled-pool
diagnostic, as well as the registered partial-coverage and concentration
manipulations. The empty-pool score remains undefined and must not be imputed.
Keep controls separate and paired by focal-paper ID.

The same-topic decoy condition is **unavailable for every focal paper** in this
partial evaluation. Do not select or use replacement candidates, and do not
score or impute decoy results. Preserve every existing candidate and its
evidence as recorded, including the missing independent topical verification,
unverified input-pool temporal checks, and temporal failures. The 50-paper
cohort remains frozen; lack of a decoy does not authorize focal replacement.

This is an explicit prospective deviation from the supplementary registration's
missing-required-condition rule. The decoy condition is removed from the
conditions required for this partial evaluation; all other source, temporal,
claim, model, manipulation-fidelity, and analysis requirements remain in force.
Log missing or invalid non-decoy conditions and exclusions before analysis and
do not replace excluded focal papers.

## Analyses and limits

For eligible focal records with complete non-decoy inputs, the following
analyses remain in scope:

- Partial coverage: original-pool reference versus 25%, then adjacent
  25% → 50% → 75% → 100% coverage comparisons.
- Concentration: distributed versus concentrated claim placement.
- Diagnostic reporting of original, shuffled, and undefined empty-pool
  controls.

Retain the registered coordinates, strict-decrease pass rule, paired
percentile bootstrap, 2,000 draws, PCG64 seed 20261113, focal-paper clustering,
and undefined-replicate rule. Report all planned coordinates, condition-level
results, exclusions, and undefinedness. The registered pass criterion can be
assessed only for partial coverage and concentration. No decoy-condition effect
or decoy-based conclusion is estimable, and results cannot establish completion
of the full control set or the original registered A1 evaluation.

## Independent claim-review gate before scoring

Before any focal paper is scored, one independent human reviewer who did not
produce that paper's extraction must review every extracted claim for that
focal against its original abstract. For every claim, record a semantic-support
judgment, an atomicity judgment, and a short rationale. The review must include
reviewer identity or code and date. Resolve or exclude claims judged
unsupported, uncertain, or compound; do not treat Copilot suggestions or other
AI assistance as human verification.

Each focal included in scoring must have 4–10 distinct retained atomic claims,
an exact supporting abstract excerpt for each, and complete source and
validation records. Otherwise exclude it from scoring, log the reason, and do
not replace it. This amendment does not waive any separate preregistered
approval, provenance, model-digest, or readiness requirement.

**Approval of this protocol deviation is not approval of individual claim
judgments and is not authorization to begin scoring.**
