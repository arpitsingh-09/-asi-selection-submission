# E6 completion report

Official task wording: `assignment_e6_excerpt_v1.txt` (PDF pp. 38–40). This
report uses the saved development records and the completed, locked HypoBench
accuracy outputs copied byte-for-byte from the original repository. No
generation, inference, evaluation rerun, or edit to protocol/data/result records
was performed. The held-out runner was not invoked.

## Task 1 — preregistration: partial

| Official requirement | Existing record | Status |
|---|---|---|
| Hypotheses and predictions | `PREREG.md` records H1 QH>D, H2 QH-sel>QH-rand, H3 QH>D-shuffled for literature main-hypothesis similarity. | Partial: no predicted magnitudes and no winner/direction prediction for every official metric on both testbeds. |
| Primary metric per testbed | Literature main-hypothesis best similarity; data exact-match accuracy on 501 TEST rows. | Present. Planted recovery/HDR is separate and not a substitute for accuracy. |
| Common budget | K=6 hypotheses, M=3 questions, 8,192 generated-token cap per input-set/arm; actual token accounting is retained. | Present. |
| QH-sel rule | Six candidate questions, 15 pairwise dedup decisions, complete-link grouping, novelty/specificity/significance/grounding weighted ranking and generation-order tie break. | Present as the recorded rule; evaluator validation remains incomplete. |
| Analyses fixed whatever the outcome | 21 paired arm contrasts, input-set bootstrap, 10,000 replicates, seed 2026, complete-pair missingness, unadjusted intervals. | Partly present; several metric definitions/evaluator settings remain unresolved in the record. |

The file is marked FINALIZED, but it also explicitly leaves evaluator choices,
the literature review completion, some analysis definitions, and the 20-case
error-analysis procedure open. This report records those gaps; it does not
rewrite the historical preregistration.

## Task 2 — seven arms on both testbeds: partial

The seven-arm implementation and prompts are present. The saved development
export contains 750 hypothesis rows from 19 HypoBench TRAIN input sets; there
are no literature-arm generation rows. The locked HypoBench accuracy snapshot
covers 19 of 20 planned sets: 13 have all seven arms, 125/140 cells have
accuracy outcomes, and 15 cells remain missing (eight failed generations and
all seven cells for unresolved set 0007). Each evaluated cell covers the same
501 TEST observations. Missing cells were not imputed or retried.

| Arm | Sets | Correct / assignments | Accuracy, 95% input-set bootstrap CI | Invalid predictions |
|---|---:|---:|---:|---:|
| D | 16 | 401 / 8,016 | 5.00% [0.00, 10.94] | 6,748 / 8,016 (84.18%) |
| QH | 19 | 282 / 9,519 | 2.96% [0.00, 7.15] | 8,020 / 9,519 (84.25%) |
| QH-sel | 16 | 105 / 8,016 | 1.31% [0.00, 3.16] | 7,016 / 8,016 (87.52%) |
| QH-rand | 17 | 127 / 8,517 | 1.49% [0.00, 3.71] | 7,516 / 8,517 (88.25%) |
| HQ | 19 | 216 / 9,519 | 2.27% [0.00, 4.75] | 8,019 / 9,519 (84.24%) |
| D-empty | 19 | 2,641 / 9,519 | 27.74% [27.74, 27.74] | 19 / 9,519 (0.20%) |
| D-shuffled | 19 | 770 / 9,519 | 8.09% [0.00, 16.36] | 8,016 / 9,519 (84.21%) |

The intervals resample TRAIN generation input sets (10,000 replicates, seed
2026); these are conditional on the fixed 501-item test list. Paired contrasts
include only complete input-set pairs. D−QH is +2.32 percentage points
(n=16; 95% CI [0.00, 5.70]); QH-sel−QH-rand is −0.27 pp (n=16; [−0.79,
0.00]); QH−D-shuffled is −5.13 pp (n=19; [−11.51, 0.00]). These data metrics
do not replace the preregistered literature hypotheses.

Both negative controls failed their expected direction by point estimate:
D-empty scored 27.74% versus D at 5.00%, and D-shuffled scored 8.09%. The
D-empty contrast is confounded by its 0.20% invalid rate versus 84–88% for
other arms. Across all 62,625 assignments, 45,354 predictions were invalid
(72.42%); 45,324 recorded failures were local Ollama connection refusals.
These results chiefly measure serving/response failures, not clean reasoning
quality. No literature reconstruction, already-asked rate, diversity,
question-type result, validated judge result, or HDR value is available.
HDR is 0/125 cells. The optional pairwise LLM judge was disabled.

## Task 3 — frozen 20-case error analysis: partial; human review incomplete

[`TASK3_ERROR_ANALYSIS.md`](TASK3_ERROR_ANALYSIS.md) gives a case-by-case
inventory for all 20 frozen sample members, including packet/source evidence,
generation rows, associated saved 501-item outcomes, examples, and missing
cells. Seven data cases have complete saved seven-arm evidence for automatic
inspection; two data cases have six arms each; data case 0007 has no outputs;
and the ten literature cases have source/reference packets but no generated
arms or evaluations. Thus 7 cases support complete automatic evidence review,
2 are partial, and 11 are blocked for output-based analysis.

This is not a completed human-coded error analysis: the frozen review-status
record remains 0/20 sets and 0 coded arm cells. A record-based, AI-assisted
check of saved case `TRAIN-SET:0011` found D H2's directional statement about
debate-presence frustration and Republican voters was not supported by the
four matching observations (2 Republican-labelled, 2 Democratic-labelled).
This is explicitly an automated/AI-assisted example, not independent
annotation. Saved non-D-empty arms repeatedly returned 0/501 correct with
501/501 invalid held-out predictions in the sampled data cases; this indicates
invalid-output failure, not semantic falsity of their hypotheses. The
direction, cause, and scientific interpretation of generated claims remain
unverified by independent reviewers. See the case report for exact
record-level limitations and links.

## Task 4 — one-page memo: completed with limits

`submission_v1/memo_one_page.md` now gives the observed data results, D baseline
and controls, negative findings, invalid-output limitation, available token
cost, a reproducible saved-output command, and the next valid test. It makes
no conclusion about the absent literature comparison or about semantic errors
that the incomplete sample cannot establish.

## Evidence and reproduction

The original held-out run is preserved in `~/asi-selection`; the submission
contains a separate exact-copy snapshot of the 19 completed per-set evaluation
JSON files and five small run-provenance files in
`runs/heldout_accuracy_optimized_v1/`. Every copied file's size and SHA-256 is
listed in `PACKAGING_MANIFEST.json`. The 65,604-file request cache and execution
lock were not copied. The original run remains untouched. No existing
generation, prediction, label, or evaluation output in this repository was
overwritten.

Run from the submission repository root to verify copied file hashes, test-list
alignment, saved accuracy counts, arm means, all 21 paired intervals, and
successful generation-token charges. This is analysis of saved outputs only:

```sh
python3 E6/reproduce_saved_heldout_accuracy.py
```

It does not call the held-out runner, generator, or model-based evaluator, and
writes no files. The locked held-out run must never be restarted. Literature
reconstruction requires a separately authorized new test execution after
source reviews and evaluator validation; the present report does not license
or perform that execution.
