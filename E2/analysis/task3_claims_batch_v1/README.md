# Task 3 source-bound claim preprocessing, batch 1

Completed a genuinely new Task 3 input: **10 supplied benchmark claim sets,
51 atomic/source-qualified claims** from the original archived abstracts. The
batch is the first ten records in the existing benchmark order, not a newly
selected evaluation subset. The other 289 IDs are in `remaining_forum_ids.json`.
No novelty labels, ratings, contribution fields or outcome scores are included
in the new claim or claim-text request files.

`claims_supplied.jsonl` uses the existing `task3_plan.validate_claims` importer
schema: forum ID, original-abstract SHA-256, provenance and exact claim/excerpt
pairs. `semantic_review.jsonl` records source filename/line, source file and
abstract hashes, character offsets, claim kind and explicit Codex AI review.
`claim_text_requests.jsonl` contains the 51 exact future claim-embedding texts
and hashes. No local extraction model was launched; claims were supplied and
reviewed by the current Codex session. Independent human review is not implied.

The existing importer accepted all ten sets. All 51 excerpts also passed exact
character-offset checks against the frozen original abstracts. No earlier test
suite, publication audit, historical scan, numerical metric or embedding job was
rerun. This is new-data validation using the existing implementation, not a new
audit framework. Source and frozen-manifest fingerprints remain unchanged.
The new supplied records have **not** been inserted into the old frozen plan.
Its claim count therefore remains zero; these ten are separate future inputs.

## Precise unresolved eligibility conditions

**Zero of 299 papers is verified eligible.** This is a verification count, not
an assertion that all 299 are actually ineligible. Existing evidence verifies
299 OpenReview release observations, not their earliest global release or the
absence of earlier preprints. The three older-title identity candidates remain
unresolved; no new identity evidence was manufactured. First-publication dates,
primary source provenance and paper/text-version binding still need verification
before any post-cutoff claim or replacement of the eligible-reference manifest.

The pinned local model card, whose exact file SHA-256 was checked against the
saved model inventory, establishes two relevant training stages: citation-triplet
training and subsequent SciRepEval adapter training. It states neither stage's
last training-data publication date. The card's 2023 usage/renaming notes and its
reference to a separate newer-paper refresh do not prove a 2018 or 2023 cutoff
for the pinned 2024 base-plus-adapter revisions. The repository's saved
December 2024 weights-existence bound is retained exactly; it is not promoted
to an exact training-data cutoff. The gate must not be bypassed using cache file
modification times, venue years, model-family release dates or topic clues.

Accordingly, no eligible subset manifest or new numerical evaluation protocol
was fabricated. Existing protocols stay unchanged. A future protocol must
explicitly reconcile cutoff/bound policy, verified first-publication evidence,
archived abstract versions, the final eligible paper/reference lists, complete
claims/embeddings and prior benchmark exposure before new authorization.

## What remains

- Verify first-publication histories and resolve cutoff/bound policy.
- Supply/review the remaining 289 benchmark claim sets.
- Prepare complete raw abstract-only history/test embeddings and claim vectors
  only in an authorized safe resource window; old normalized title-plus-abstract
  vectors cannot substitute for the raw quality-baseline representation.
- Create a new execution freeze only when inputs/evidence are ready; the old
  plan's stale code bindings are not repaired in place.
- Obtain explicit future authorization before any held-out AUROC, ridge fit or
  bootstrap comparison. **No new AUROCs or numerical experiment results exist.**

With the eligibility block documented, also advanced mandatory Task 2 data:
three new source-bound paraphrase drafts are in `../paraphrase_additions_v2/`.
They preserve source hashes and claim-to-passage mappings, have no independent
approval or scoring permission, and were not embedded/evaluated. Candidate
coverage is now 11 papers, with 289 still lacking candidates. Original pilot
records and frozen manipulation plans remain unchanged.

Single next action: continue the source-supported benchmark claim preprocessing
from `remaining_forum_ids.json`, using the existing importer and original
abstracts. This work does not require model loading or affect E6 resources.
