# Task 2 N/yours-only extension results

Evaluated 2026-11-18 under the fixed 52-paper N/custom protocol. This is a
cache-only analysis using the 93 saved claim vectors. No model was loaded, no
embedding was generated, and neither earlier 241-paper results nor the saved
Y/density results were recomputed.

The 52 papers comprise 20 computation-language, 13 computer-vision, and 19
machine-learning focals. The protocol's four majority-pass predictions all
passed:

| Measure | Contrast | Passes / valid | Pass rate (95% paper-bootstrap CI) | Mean paired difference (95% CI) |
|---|---|---:|---:|---:|
| N | near < far | 52/52 | 100.0% (100.0–100.0%) | -0.04671 (-0.05181 to -0.04170) |
| yours | near < far | 52/52 | 100.0% (100.0–100.0%) | -0.08857 (-0.09464 to -0.08229) |
| N | newer < older | 34/52 | 65.4% (51.9–76.9%) | -0.00299 (-0.00586 to -0.00024) |
| yours | newer < older | 37/52 | 71.2% (59.6–82.7%) | -0.00681 (-0.01086 to -0.00297) |

Differences are left minus right. Pass requires a difference below -1e-8; ties
fail. Intervals use 10,000 paired paper-bootstrap draws, seed 20261113. These
are descriptive Task 2 development results: prior Y/density outcomes were
already visible, and the new claim extraction stage differs from the earlier
cohort. Do not pool numeric N/yours estimates across those stages. This is not
the held-out human check and does not establish independent semantic validity.

The frozen source, protocol, and sidecar hashes and run details are recorded in
`summary.json`; the 52 per-paper records are in `results.jsonl`. The source
protocol and inputs remain in the frozen `/Users/arpit/asi-selection` checkout;
the generated report and result files are in `ASI_Intern_Submission`.
