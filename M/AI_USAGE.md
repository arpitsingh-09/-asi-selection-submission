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
not merely hiding them at the groundedness head. Synthetic tests verify both.

No scientific accuracy, actual held-out performance, model cutoff or real outcome
was manufactured. Only synthetic fixtures were used for fitting/testing. Root
logs remain protected while E6 runs; later authorized root-log integration and
prospective experiment preregistration remain submission requirements.
