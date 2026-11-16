# Task 3 local temporal validation — 2026-11-13

Completed source-level offline validation of the unchanged frozen inputs:
299 benchmark papers and 25,186 historical papers. See
`analysis/task3_date_validation_v1.json` for source fingerprints and results.
`validate_task3_dates.py` reproduces this check into a new output file without
model loading, embedding generation, fitting, or benchmark metrics.

The historical eligibility rule is strict public-date ordering against the
earliest benchmark OpenReview release, with disjoint forum IDs. Recomputed
each historical date from its original local source: the earliest positive
`odate`/`pdate`, never `cdate`, modification dates, or an inferred venue year.
All original abstract hashes and date-field selections matched. Rejoined all
299 benchmark abstracts/dates to the recovered archive records as well.
Latest history: 2024-10-05T05:26:21.204000+00:00. Earliest benchmark OpenReview
release: 2025-10-08T04:11:45.795000+00:00. This verifies the frozen shared pool
against OpenReview release dates; it does not establish first global publication.
If earlier benchmark preprints are found, shared-pool eligibility must also be
rechecked against those earlier dates before making first-publication claims.

Existing local model inventory and protocol record December 4, 2024 publisher
commit dates for the pinned base and adapter, and a conservative end-of-December
2024 weights-existence bound. These saved assertions were inspected locally;
no publisher page was fetched again. They do not identify the exact training-data
cutoff. Neither model cache timestamps nor venue years supply the missing proof.
The exact cutoff therefore remains unresolved from the inspected local evidence.

Fixed the prepared evaluation gate in `task3_execution.py` via
`task3_eligibility.py`: reviews must bind to each original abstract hash,
use literal boolean verification and a nonblank evidence source, cover the exact
benchmark IDs, have timezone-aware first-publication dates strictly after the
cutoff and no later than archived publication, and declare a cutoff at least as
late as the conservative pinned-weights bound. Plan generation now fingerprints
this validation module too. The gate also rechecks that every historical date
precedes every verified first-publication date, catching earlier-preprint leakage. Evidence still needs substantive human verification;
the code cannot certify a source's truth or completeness.

The existing `task3_execution_v1` plan is preserved. Its code fingerprints are
now stale by design, so loading it fails closed. Do not edit its hashes or reuse
its authorization. After evidence and claims are complete, generate a new plan
in a new directory with the updated implementation. Existing datasets, scores,
checkpoints and frozen manifests were not rewritten.

`analysis/task3_first_publication_review_pending_v1.json` contains 299 ID/hash-bound
review slots, all explicitly unverified. For each, find earliest global
publication/preprint evidence, record its date and source, and check archived
text-version availability. Do not mark OpenReview release alone as verified
first publication. The pending file cannot authorize evaluation.

Validation: **65 lightweight offline tests passed** across human-check,
abstract preparation, archive recovery, continuation, manipulation extensions,
Task 3 execution, and the new temporal-gate suite (9 new tests). Synthetic vectors
were used only in offline fixtures. The 25,485-record source/date audit passed.
No inference or full benchmark evaluation was executed. E6 and the root notebook
and AI log were not accessed for writing or process control.

Remaining: first-global-publication review for all 299 papers; acceptance of a
release bound versus an exact training cutoff; source-supported and semantically
reviewed claim sets; a new frozen execution plan; future authorized embeddings,
runtime/resource calibration and evaluation. Prior benchmark exposure remains
disclosed, and the original/edited abstract distinction remains intact.

Exact next step: complete the pending 299-row first-publication review using
primary publication/preprint records and original-text bindings, then revalidate
the frozen historical pool against the earliest verified first-publication date.
Resolve any pre-cutoff or chronology failures explicitly before preparing a new
execution plan. Embeddings and benchmark evaluation remain deferred.
