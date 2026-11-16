# Prospective evidence-recovery amendment — 2026-11-13

Parent preregistration: commit 6e21dfe, `M/PREREG.md`. Original protocol, frozen
configuration, lists and SHA-256 files are unchanged. No pass threshold, model,
metric, control requirement or test cohort is altered. No real scoring is enabled.
This amendment records local evidence recovery and explicitly **does not** waive
eligibility or public-version dates. Any future eligible cohort/model amendment
must be committed before its predictions or scoring.

Fixed bounded recovery: first 1,000 JSONL records from each local ICLR 2023 and
2024 review archive (development evidence, not outcome-selected cohorts). Exact
record bytes, offsets, lengths and SHA-256s bind each imported field. Verify the
actual forum IDs before joining paper records. Never infer label public availability
from cdate/tcdate, venue year, present `readers`, or a review's revision date. An
odate earlier than the current version does not date the current score. A missing
public observation remains null, even if a version timestamp is available.

Results of recovery, not experimental scores: 570 genuine recommendations (270
from 2023 archive prefix, 300 from 2024); 277 exact paper-ID links, nine linked
abstracts with verbatim interrogative passages. These passages are **not** human-
verified focal questions. Zero labels currently have verified public observation
and publication-time question-version linkage. Imported benchmark aggregates:
299, all still undated as outcomes. They are not individual review observations.
Rubric definitions remain year/field-specific; no cross-rubric pooling or training.

Cache-only adapter: exact B-Q/B-ABS text/hash, model identity, dimension and finite
vector checks; no inference fallback. For the current 80 candidates the local E2
cache has zero exact question vectors and zero exact available abstract vectors.
Existing E1 item distances are already-evaluated outputs, not embedding vectors.
A model cutoff requires explicit source evidence, not a guessed release-date bound.

Per-test status/cohort files are under `M/data/ingestion_v2/`. All nine eligible
lists are empty; all metrics/intervals are null, status BLOCKED. No frozen prediction
records are manufactured for empty cohorts. Existing E2 completed comparisons are
not reclassified as fresh M heldout tests. No real heldout file is passed to the
scoring runners. New ingestion/cohort/baseline code hashes and data artifact hashes
are locked in the companion stage4 lock file before any future eligible testing.

Next executable data task: obtain source-backed independent verification of an
E1 same-question/near-miss subset, dated question availability, original reference
links, same-topic decoy judgments and exact cached B-Q texts/model cutoff. Only
then prepare a new prospective S1 cohort/model lock. Alternatively, recover original
public paper/review-version snapshots to make historical quality training feasible.
