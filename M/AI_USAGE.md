# Scoped implementation disclosure

Codex assistant, 2026-11-13: read all Main Problem pages 42–46, implemented the
shared immutable representation, six readout interfaces, cache adapters,
baselines, train-only quality factors, controls, CLI and synthetic tests.

Reused E5 lightweight hashing/facet functions and combinatorial diversity code;
reused E2 pure RND/bounded novelty and SQLite cache validation without launching
any model. Did not reinterpret E1 relevance scores as identity predictions.

Caught and corrected an update error: assigning an arrival time earlier than a
future paper's publication made a valid future exclusion raise an exception.
Availability now defaults to no earlier than publication. Also eliminated a
potential future-annotation leak by removing unavailable answers from Phi itself,
not merely hiding them at the groundedness head. The future-annotation fix has
direct synthetic regression coverage in
`tests/test_space.py::test_future_answer_annotation_is_removed_not_just_hidden_by_head`.
`tests/test_space.py::test_late_arrival_not_backdated_and_versions_immutable`
covers the related late-arrival behavior; there is no dedicated test for the
exact earlier-arrival crash that prompted the first correction. The last
recorded M software suite contains 92 passing tests; these tests were not
rerun during the current report work.

No scientific accuracy, actual held-out performance, model cutoff or real outcome
was manufactured. Synthetic fixtures were used for the implementation and
software-test work described above; that statement does not characterize the
separate supplementary analyses, which are reported separately in
[`FINAL_REPORT.md`](FINAL_REPORT.md). This file is the scoped Main Problem AI-use
record; it does not replace the assignment's submission-level AI log if the
final package requires a single consolidated log.
The original M preregistration and amendments are preserved in the verified Git
history bundle; this disclosure does not substitute for their chronology evidence.

2026-11-20: Codex compared the saved supplementary S1 metrics and A1 statistical decision with the final report, summarized the two measured outcomes, and corrected the overview of baseline availability. No scoring was run for this edit.
