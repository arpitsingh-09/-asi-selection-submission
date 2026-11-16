# Generated-question CPU development check v3

Six questions, original/empty/shuffled controls (18 snapshots). Development-only descriptive readouts; no core test or pass criterion applied. No confidence intervals.

| Condition | G proxy mean (n) | N.Y mean | Density mean | Pairwise cosine distance | Vendi | Class entropy |
|---|---:|---:|---:|---:|---:|---:|
| original | 0.49452637453948706 (6/6) | 0.468653 | 100.000000 | 0.645480 | 4.699807 | 1.791759 |
| empty | None (0/6) | 0.468653 | 100.000000 | 0.645480 | 4.699807 | 1.791759 |
| shuffled | 0.2655136629992328 (6/6) | 0.468653 | 100.000000 | 0.645480 | 4.699807 | 1.791759 |

N.Y now uses float64 einsum-based cosine calculations. The earlier matmul warnings did not recur. Q remains unavailable; no claim-based N/custom vectors were supplied. G is an unvalidated lexical relevance proxy. D is lexical shared-space set diversity. I only confirms identical question text across input controls; it is not paraphrase invariance. T confirms these snapshots exclude later literature; no time-update forecast was tested. Same-topic decoys remain unused pending human review.
