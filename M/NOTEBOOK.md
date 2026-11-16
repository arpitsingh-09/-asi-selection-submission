# Main Problem experiment notebook

## Recorded execution status

The machine-readable record is [results/consolidated_v1/summary.json](results/consolidated_v1/summary.json): 0/9 registered evaluations completed, 9 blocked, and no registered metrics or confidence intervals. This notebook does not promote software tests or development checks to experimental findings.

## Data and limitations

The available manifests record 25 train, 2 validation, and 80 heldout candidates. Review ingestion records 570 genuine source recommendation values, but zero verified public observation dates and zero usable question-linked labels. Both quality factors remain unavailable. The heldout records are candidate metadata only. Generated-question and E1/E2 materials are development evidence unless independently eligible under the frozen protocol.

## Frozen scientific design

The protocol hypothesizes paraphrase stability versus near-miss drift,
novelty response to partial coverage and concentration, length-robust relevance
and novelty, quality agreement beyond text baselines, system-adjusted expert
preference prediction, and temporal equivalence across frozen training
cutoffs. The implementation uses a 512-bin lexical hash representation;
quality heads and semantic B-Q/B-ABS baselines are unavailable. Evaluation
windows are TRAIN through 2023, VALIDATION 2024, a first-half 2025 gap, and TEST
from 2025-07-01. Each registered metric uses paired cluster-bootstrap
confidence intervals (2,000 draws, PCG64 seed 20261113), with cluster unit
and threshold fixed per test in `PREREG.md`. No core evaluation is eligible:
0/9 are complete. Missing temporal links, labels, inputs/controls, fitted
heads, and task-specific baselines block the affected tests; missingness is
not a negative outcome.

## Reproduction commands

Run the summary generator (reads existing receipts/results; does not score):

```sh
python3 -m M.consolidate_results --out M/results/consolidated_v1/summary.json
```

Run focused CPU software tests (not experimental evaluations):

```sh
python3 -m unittest M.tests.test_consolidate_results M.tests.test_evaluation M.tests.test_training M.tests.test_space -q
```

The saved supplementary A1 statistics can be recomputed in memory with the
reproduction command in `FINAL_REPORT.md`. The exploratory V2 review
comparison can be reproduced with
`python3 -m M.prospective_grounding.exploratory_evidence.compare_review_responses`;
it writes only under the exploratory evidence directory and does not score V2.

No heldout evaluation or model inference is recorded by this notebook. Consult [FINAL_REPORT.md](FINAL_REPORT.md), [README.md](README.md), and [PREREG.md](PREREG.md) for methods, implementation scope, and frozen requirements.

## Supplementary prospective grounding status — 2026-11-15

The original nine remain 0/9 complete and blocked. The separate supplementary
A1 partial replication has its registered negative threshold result (n=2
focal clusters); it is not original A1. Grounding V1 failed on its first
generation call: qwen3:8b exhausted 512 tokens in thinking and returned an
empty response. The raw failed attempt is retained in `prospective_grounding/generated_v1/`.

The supplementary A1 analysis scored 16 nonempty targets over two focal
clusters, using original, four coverage, concentration, distribution, and
shuffled conditions; empty scores were undefined and the decoy was unavailable.
Y passed the concentration ordering (1.0, 95% CI [1.0, 1.0]) but its coverage
pass fraction was 0.5 [0.0, 1.0]; no coordinate met the combined threshold.
This exposed partial replication is too small for confirmatory inference.

Grounding V2 preregistration/implementation commit
`a87b631bc1b4237e950cbaf8abe4e1e4524cc652` predates its four successful
qwen3:8b generations (`think=false`). Records are in
`prospective_grounding/generated_v2/`. Two blinded reviewer forms are blank;
the subsequently supplied responses are retained as exploratory evidence in
`prospective_grounding/exploratory_evidence/`. Each response covers 18 ratings
and six association checks. Reviewer 1 declares independence, not externally
verified; reviewer 2 declares independence=false and the response is identified
as AI-assisted. Ratings agree on 17/18 pairs (unweighted κ=0.912), and all six
association decisions agree. They do not meet the two-independent-review gate.
V2 has no scores, baseline comparison, confidence interval, or evaluation
result. No inference or scoring is authorized by the generation records or
exploratory responses alone.

Minimum inputs still required before V2 scoring: two eligible independent,
dated 0/1/2 ratings with evidence notes for all registered non-empty
question-paper pairs; two independent same-topic/unsupported validations per
decoy; validated registered condition construction; and explicit scoring
authorization. The exploratory response pair does not supply these eligible
independent reviews.

Offline packet checks:

```sh
python3 -m unittest M.prospective_grounding.tests.test_human_review_v2 -v
python3 -m M.prospective_grounding.human_review_v2.validate_packet
```
