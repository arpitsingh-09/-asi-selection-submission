# Generated-question development-only readouts

This is a descriptive smoke check over six program-generated questions and 18 snapshots. It is not an evaluation, no protocol pass criteria were applied, and no confidence intervals were computed. Original, empty and shuffled conditions only were used; same-topic decoys remain pending human review.

| Condition | Grounding proxy mean (n) | Novelty Y mean* | Density mean* | Set pairwise cosine distance | Vendi | Entropy |
|---|---:|---:|---:|---:|---:|---:|
| original | 0.49452637453948706 (6/6) | 0.4686527152856191 | 100.0 | 0.645480 | 4.699807 | 1.791759 |
| empty | None (0/6) | 0.4686527152856191 | 100.0 | 0.645480 | 4.699807 | 1.791759 |
| shuffled | 0.2655136629992328 (6/6) | 0.4686527152856191 | 100.0 | 0.645480 | 4.699807 | 1.791759 |

* Novelty computations produced NumPy divide-by-zero/overflow/invalid-value warnings at `M/readouts.py:55`; values serialized finite, but treat these novelty scores as numerically suspect. Identical novelty across input controls is expected here because N uses retrieved prior literature, not R.

The G score is a lexical input-relevance proxy. Empty input has no available G score. Q outputs are unavailable because neither quality factor has a trained head. I identifies the same exact generated question in each control; this does not test paraphrase invariance. D is computed from six questions using the lexical shared representation. T reports no future leakage for these snapshots; no update forecast was tested.

Failures/blockers: Q factors untrained; claim-based novelty absent; numerical warnings on N; human verification of same-topic decoys pending. No human labels were created and no test result is claimed.

Reproduce in a new output directory (the command is write-once):

```sh
.venv/bin/python -B -m M.run_generated_development --out M/results/generated_development_REPRO
```
