# Prospective generated-question cohort amendment — 2026-11-13

Parent protocol: `M/PREREG.md`, committed at 6e21dfe. This amendment is committed
before generating any question text. It adds a generated-question cohort protocol;
it does not alter the primary test hypotheses, pass margins, bootstrap, date split,
control requirements, or authorize evaluation.

## Population and timing

The cohort contains up to 12 newly generated questions. Generation time is recorded
from the UTC system clock at execution, not backdated. A question is heldout-date
eligible only if it is generated at or after 2025-07-01. Source papers must each
have a verified arXiv record with `published < generated_at`, `updated < generated_at`,
and a versioned arXiv ID/URL. The exact source record and raw corpus line hash are
saved. An input pair is R for that newly generated question; no bibliography or
citation is used to infer an input. Existing E2 papers may serve only as prior
source inputs, never as heldout example identities. Exclude IDs in the E1/E2 focal
question lists. Generated question IDs/texts are checked against existing M/E1/E2
question strings before admission.

## Fixed generation rule

No model inference or external search is used. Within the `cs.CV` source subset,
select six disjoint pairs by descending token-Jaccard overlap of normalized titles
(minimum 0.10), then lexical paper IDs. Require distinct source paper IDs and
identical primary categories. Generate the text with the fixed template:

`How do the approaches in {title_a} and {title_b} differ in their treatment of {topic_label}?`

`topic_label` is a fixed mapping for known arXiv categories; otherwise use the
literal category identifier. Store the rendered question, template version, both
input IDs, exact source text hashes, actual UTC generation timestamp and code hash.
This is a program-generated research question, not a published question or a human
claim that the inputs are semantically sufficient. The generator must produce no
more than 12 and fails closed if source/date/identity checks fail.

## Controls and admission

Original R is the selected two-paper set. Empty R is `[]`. The shuffled condition
uses two distinct, earlier, same-primary-category papers from other pair instances;
record every paper ID/version and its source binding. The decoy is a different
program-generated question from a disjoint same-category source pair and reuses the
original R. The common arXiv primary category provides source-backed categorical
matching only; it is not represented as an independent human semantic topic
judgment. Therefore records remain evaluation-ineligible until a permitted
independent same-topic verification is supplied. No control is scored by this
amendment.

## Integrity and evaluation gate

Each run records exact source line bytes/offset/hash, text hashes, ID sets, source
published/updated timestamps, generation time, source URLs, code SHA-256, and
exclusion reasons. Fail on any overlap with existing question IDs/texts, input
published/updated timestamp not strictly earlier than generation, duplicated
sources/controls, or unsupported topic mapping. A candidate-data manifest hash may
be committed after generation for provenance; this does not turn candidates into
an eligible test list or authorize scoring. A separate eligibility and evaluation
lock is required after independent control verification and must be committed
before any evaluation. No heldout tuning or performance claim is allowed.
