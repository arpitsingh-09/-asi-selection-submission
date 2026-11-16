# E5 AI use disclosure (pending later authorized root-log integration)

2026-11-13: Codex assistant read the complete official E5/general rules, designed
and implemented the API, controlled benchmark, gates, statistics and known-group
constructor, and wrote the prospective predictions before tests/evaluation.
No local language model or embedding model was invoked. Dataset text is
procedural controlled language, not human-authored research evidence. Semantic
calibration, same-question identity and paper citation facts are not fabricated.

Checks: exact Vendi extremes; independent brute-force subset comparison;
nontransitive identity chain counterexample; immutable/correctly matched
inputs; calendar date-window checks; missing semantic-cache and citation data
failures; fixed hashes and pre-evaluation commit. Actual results will be linked
from the report, with failures retained.

Important correction: a connected component of positive same-question edges is
not necessarily a pairwise-equivalent class. A three-node chain test detects
this shortcut; the implementation uses exact within-class cliques and reports
nontransitivity. The E1 MS MARCO cache is a relevance baseline, not a validated
same-question judge, and is not relabeled as such.

The user forbids editing root AI_LOG.md while E6 runs. This file preserves the
substantive disclosure, but root-log integration remains a submission task.
