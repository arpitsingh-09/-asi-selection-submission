# E6 memo for research-agent designers

**Recommendation:** Do not adopt questions-first decomposition or question
selection on these results alone. The saved HypoBench experiment is incomplete,
and the required literature reconstruction comparison has no generated arms.

On the data testbed, exact-match accuracy (mean across available TRAIN
generation sets; 95% input-set bootstrap interval) was:

| Arm | Sets | Accuracy, 95% CI |
|---|---:|---:|
| D | 16 | 5.00% [0.00, 10.94] |
| QH | 19 | 2.96% [0.00, 7.15] |
| QH-sel | 16 | 1.31% [0.00, 3.16] |
| QH-rand | 17 | 1.49% [0.00, 3.71] |
| HQ | 19 | 2.27% [0.00, 4.75] |
| D-empty | 19 | 27.74% [27.74, 27.74] |
| D-shuffled | 19 | 8.09% [0.00, 16.36] |

Paired differences do not show a clear decomposition benefit: D−QH was
+2.32 percentage points (n=16; 95% CI [0.00, 5.70]). Selection did not beat
random selection: QH-sel−QH-rand was −0.27 pp (n=16; [−0.79, 0.00]). Neither
comparison is the registered literature primary outcome.

**Controls and failure.** Both controls scored above D by point estimate:
D-empty was 27.74% and D-shuffled 8.09%, versus D at 5.00%. This is not
evidence that removing or shuffling evidence helps: 0.20% of D-empty
predictions were invalid, versus 84–88% for other arms. Overall, 45,354 of
62,625 TEST predictions were invalid; 45,324 were local Ollama connection
refusals. Preserve transport errors separately from semantic errors and detect
them before output parsing. In a saved TRAIN example, D asserted that
third-party-debate frustration was more frequent among Republican-labelled
users, while the four matching records split evenly (two Republican, two
Democratic). This is one AI-assisted example, not a human annotation.

**Cost, limits, next test.** The shared generation cap was 8,192 tokens per
set/arm. The saved runtime is Gemma 3 12B Q4_K_M, temperature 0, seed 2026.
Completed cells account for 90,833 generated tokens; failed-attempt charges
are not complete. Fifteen of 140 data cells are missing, and the fixed
20-case review has no completed human review; only nine sampled data sets have
any arm outputs. Literature reconstruction, HDR, already-asked rate, diversity
and question-type outcomes are unavailable. After evaluator validation and
the required source/target reviews, test literature reconstruction under a
separately approved protocol. Do not restart the locked HypoBench run.

Reproduce saved data accuracy and paired intervals, without generation or
model scoring: `python3 E6/reproduce_saved_heldout_accuracy.py`. See
`E6/COMPLETION_REPORT.md` for model, missingness, full comparisons, hashes and
limitations.
