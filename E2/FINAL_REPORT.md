# E2 — final report from saved evidence

**Status date: 2026-11-17.** This report uses saved E2 records and offline arithmetic only. The original scorer, novelty functions, models and network were not run. Both protected scoring files remain read-only.

## Executive status

- **Task 1 — partial.** The original scored claim file has 58/300 sets below four claims. A later source-bound, AI-assisted future-use recovery reaches 294/300 sets with 4–10 claims by count; six remain evidence-limited. Recovered claims were not substituted into the 2,400-case experiment, and counts are not human validation.
- **Task 2 — partial.** The original run has 2,400/2,400 saved condition records for 300 focal papers across three 1,000-paper pools and eight conditions. Each record has four scores (9,600 scalar values). Saved near/far and temporal work covers 241 focals for all four measures; a separate, descriptive Y/density extension brings those two measures to 293/300. Nearest-paper planting and complete paraphrase scoring remain unavailable.
- **Task 3 — blocked.** The benchmark has 299 directly mapped records with 154 positive and 145 negative labels, but no saved four-measure benchmark predictions or provenance-verified abstract-only embedding matrices; therefore no AUROC or novelty-minus-quality interval is reportable. Publication/cutoff eligibility also remains unverified.
- **Task 4 — complete as interpretation.** The existing one-paragraph interpretation is in `E2/README.md`; it makes no empirical human-check claim.

## Sources and method

Primary saved files: `E2/data/manipulation_plan.jsonl` (2,400 planned cases), `E2/data/scoring_results.jsonl` (2,400 successful score records), `E2/analysis/saved_results_report.json` (original overall pass-rate summaries and hashes), `E2/analysis/cached_extensions_v1/summary.json` (241-focal all-measure near/far and newer/older results), and `E2/analysis/task2_extension_52_v1/summary.json` (the later Y/density-only 52-focal extension and descriptive 293-focal aggregation). Pool definitions and IDs are in `E2/data/pool_manifest.csv`; focal-to-pool assignments are in `E2/data/focal_papers.csv`. Benchmark counts/mappings are in `E2/analysis/benchmark_audit.json`.

For the original experiment, each plan was joined to exactly one saved score by `case_id`, then paired conditions were grouped by `(pool, focal_paper_id)`. No score was recomputed. Every original result is `status=ok`; each focal has eight conditions. Directional indicators use the existing tolerance `1e-8`: exact copy is a strict decrease; coverage comparisons are non-increasing (ties pass). Focal paper is the unit, not claim or score row.

The original report’s aggregate 95% percentile intervals use 10,000 focal-paper bootstrap resamples, seed 20261113. The read-only summarizer additionally emits per-pool pass-rate intervals for every contrast and paired mean-difference intervals (resampling focal papers within each fixed pool; same seed and replicate count). The report prints all per-pool pass counts and the concentration mean-difference intervals. These quantify within-cohort variation only; the three curated pools are fixed, not random samples of all literature.

Read-only reproducer:

```sh
python3 E2/summarize_saved_scores.py
```

It validates saved-result hashes against `saved_results_report.json`, joins records, and prints the full overall/per-pool summaries as JSON. It does not import `novelty.py`, write files, or score papers.

## Original 2,400-record experiment

### Pooled directional pass rates

Cells show passes/300 and 95% bootstrap interval for the pass percentage. The direction for **N under concentrated coverage** is the T2-derived increase (the earlier preregistered equality prediction was corrected in `PREREG.md` after the derivation was checked). Density had no fixed concentration direction, so its “lower” count is descriptive only.

| Contrast and criterion | Y | N | yours | density |
|---|---:|---:|---:|---:|
| exact_copy vs baseline (strict decrease) | 300/300 (100.0%; [100.0, 100.0]%) | 284/300 (94.7%; [92.0, 97.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 295/300 (98.3%; [96.7, 99.7]%) |
| coverage_25 vs baseline (non-increase) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 289/300 (96.3%; [94.0, 98.3]%) |
| coverage_50 vs baseline (non-increase) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 286/300 (95.3%; [92.7, 97.7]%) |
| coverage_75 vs baseline (non-increase) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 287/300 (95.7%; [93.3, 97.7]%) |
| coverage_100 vs baseline (non-increase) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 289/300 (96.3%; [94.0, 98.3]%) |
| coverage_50 vs coverage_25 (non-increase) | 272/300 (90.7%; [87.3, 93.7]%) | 172/300 (57.3%; [51.7, 63.0]%) | 252/300 (84.0%; [79.7, 88.0]%) | 280/300 (93.3%; [90.3, 96.0]%) |
| coverage_75 vs coverage_50 (non-increase) | 277/300 (92.3%; [89.0, 95.3]%) | 182/300 (60.7%; [55.0, 66.0]%) | 267/300 (89.0%; [85.3, 92.3]%) | 281/300 (93.7%; [91.0, 96.3]%) |
| coverage_100 vs coverage_75 (non-increase) | 196/300 (65.3%; [60.0, 70.7]%) | 120/300 (40.0%; [34.3, 45.7]%) | 177/300 (59.0%; [53.3, 64.7]%) | 279/300 (93.0%; [90.0, 95.7]%) |
| concentrated vs distributed (Y/yours lower; N higher; density lower descriptive) | 216/300 (72.0%; [67.0, 77.0]%) | 300/300 (100.0%; [100.0, 100.0]%) | 96/300 (32.0%; [26.7, 37.3]%) | 26/300 (8.7%; [5.7, 12.0]%) |

For the concentrated-versus-distributed contrast, paired mean score differences (concentrated minus distributed) are:

| Measure | Mean paired difference | 95% paired bootstrap CI | Lower / tie / higher focal counts |
|---|---:|---:|---:|
| Y | -0.009104 | [-0.010572, -0.007658] | 216 / 29 / 55 |
| N | +0.046057 | [+0.044752, +0.047305] | 0 / 0 / 300 |
| yours | +0.004686 | [+0.003574, +0.005800] | 96 / 0 / 204 |
| density | +4.697623 | [+4.118025, +5.306448] | 26 / 26 / 248 |

**Interpretation.** Y decreases under concentration in 216/300 focals (72%; mean Δ −0.009104). N increases in all 300, consistent with the T2 derivation and opposite the original incorrect equality forecast (mean Δ +0.046057). The custom combination `yours` decreases in only 96/300 (32%); its mean difference is positive, +0.004686, with an interval above zero. Density decreases in 26/300; its mean increases by 4.697623 score units, but no fixed direction was predicted. Thus the custom measure does not reliably preserve the predicted concentration response on these embeddings.

### Per-pool pass counts

Each cell is passes/100 focal papers. Pass criteria are the same as the pooled table; for concentration, Y and `yours` count lower, N counts higher (T2-derived), and density’s lower count is descriptive.

#### computation language

| Contrast | Y | N | yours | density |
|---|---:|---:|---:|---:|
| exact_copy vs baseline (strict decrease) | 100/100 | 98/100 | 100/100 | 96/100 |
| coverage_25 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 98/100 |
| coverage_50 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 97/100 |
| coverage_75 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 97/100 |
| coverage_100 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 97/100 |
| coverage_50 vs coverage_25 (non-increase) | 88/100 | 46/100 | 78/100 | 93/100 |
| coverage_75 vs coverage_50 (non-increase) | 93/100 | 60/100 | 88/100 | 93/100 |
| coverage_100 vs coverage_75 (non-increase) | 68/100 | 43/100 | 59/100 | 94/100 |
| concentrated vs distributed (concentration directions) | 69/100 | 100/100 | 32/100 | 4/100 |

#### computer vision

| Contrast | Y | N | yours | density |
|---|---:|---:|---:|---:|
| exact_copy vs baseline (strict decrease) | 100/100 | 96/100 | 100/100 | 100/100 |
| coverage_25 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 98/100 |
| coverage_50 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 96/100 |
| coverage_75 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 95/100 |
| coverage_100 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 96/100 |
| coverage_50 vs coverage_25 (non-increase) | 92/100 | 60/100 | 89/100 | 91/100 |
| coverage_75 vs coverage_50 (non-increase) | 92/100 | 62/100 | 89/100 | 93/100 |
| coverage_100 vs coverage_75 (non-increase) | 67/100 | 44/100 | 63/100 | 94/100 |
| concentrated vs distributed (concentration directions) | 77/100 | 100/100 | 36/100 | 7/100 |

#### machine learning

| Contrast | Y | N | yours | density |
|---|---:|---:|---:|---:|
| exact_copy vs baseline (strict decrease) | 100/100 | 90/100 | 100/100 | 99/100 |
| coverage_25 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 93/100 |
| coverage_50 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 93/100 |
| coverage_75 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 95/100 |
| coverage_100 vs baseline (non-increase) | 100/100 | 100/100 | 100/100 | 96/100 |
| coverage_50 vs coverage_25 (non-increase) | 92/100 | 66/100 | 85/100 | 96/100 |
| coverage_75 vs coverage_50 (non-increase) | 92/100 | 60/100 | 90/100 | 95/100 |
| coverage_100 vs coverage_75 (non-increase) | 61/100 | 33/100 | 55/100 | 91/100 |
| concentrated vs distributed (concentration directions) | 70/100 | 100/100 | 28/100 | 15/100 |

Pool-specific paired concentration mean differences and 95% within-pool focal bootstrap intervals:

| Pool | Measure | Concentrated − distributed | 95% CI |
|---|---|---:|---:|
| computation language | Y | -0.008994 | [-0.011570, -0.006507] |
| computation language | N | +0.043801 | [+0.041461, +0.046055] |
| computation language | yours | +0.004205 | [+0.002324, +0.006067] |
| computation language | density | +3.587922 | [+2.755670, +4.566973] |
| computer vision | Y | -0.010829 | [-0.013290, -0.008261] |
| computer vision | N | +0.049665 | [+0.047420, +0.051873] |
| computer vision | yours | +0.004295 | [+0.002387, +0.006289] |
| computer vision | density | +6.229008 | [+5.050901, +7.439336] |
| machine learning | Y | -0.007490 | [-0.010039, -0.004976] |
| machine learning | N | +0.044705 | [+0.042641, +0.046657] |
| machine learning | yours | +0.005559 | [+0.003687, +0.007370] |
| machine learning | density | +4.275938 | [+3.313858, +5.243272] |

Across pools, the concentration pattern is consistent: N always increases; Y usually decreases; `yours` usually increases on average and decreases in only 28–36/100; density usually increases and has a small lower-direction count. These are fixed-pool descriptions, not evidence of transfer to other corpora.

## Additional saved cache-only comparisons (241 focals)

The existing `cached_extensions_v1` results compare equal-size, disjoint near/far and newer/older pools for 241 distinct focals: 76 computation/language, 86 computer vision, 79 machine learning. This is a cache-available subset, excluding 58 original short-claim focals and one focal without enough cached strictly prior papers; it is not the full 300-focal Task 2 cohort. Pass criterion was strict decrease by more than `1e-8`.

| Comparison | Measure | Passes / 241 | 95% CI for pass rate | Mean paired Δ and 95% CI |
|---|---|---:|---:|---:|
| near vs far | Y | 241/241 | [100.0, 100.0]% | -0.10141 [-0.10471, -0.09805] |
| near vs far | N | 241/241 | [100.0, 100.0]% | -0.04593 [-0.04836, -0.04354] |
| near vs far | yours | 241/241 | [100.0, 100.0]% | -0.08754 [-0.09051, -0.08459] |
| near vs far | density | 236/241 | [95.9, 99.6]% | -47.73929 [-51.19410, -44.21698] |
| newer vs older | Y | 152/241 | [56.8, 69.3]% | -0.00648 [-0.00882, -0.00421] |
| newer vs older | N | 143/241 | [53.1, 65.1]% | -0.00192 [-0.00311, -0.00073] |
| newer vs older | yours | 151/241 | [56.4, 68.5]% | -0.00534 [-0.00730, -0.00338] |
| newer vs older | density | 133/241 | [49.0, 61.4]% | -4.74019 [-7.26842, -2.22759] |

All four measures decrease for near vs far in 241/241 cases except density (236/241; two ties). Newer vs older passes are 152/241 Y, 143/241 N, 151/241 `yours`, and 133/241 density. Near/far selection uses the same embedding geometry as the scores; these are controlled response checks, not independent semantic-validity evidence. Temporal direction is an empirical hypothesis, not a universal axiom.

A separately preregistered Y/density-only extension adds 52 eligible focals (20 computation/language, 13 vision, 19 machine learning). Its saved summary also provides descriptive 293-focal pooled estimates for Y and density. This combines the earlier 241 with a later claim-recovery stage, so it is explicitly descriptive across stages; do not treat it as one blind cohort. N and `yours` remain at 241 because 93 claim vectors are missing.

| Descriptive combined Y/density contrast | Measure | Passes / 293 | 95% CI for pass rate | Mean paired Δ and 95% CI |
|---|---|---:|---:|---:|
| near vs far | Y | 293/293 | [100.0, 100.0]% | -0.10161 [-0.10474, -0.09852] |
| near vs far | density | 287/293 | [96.2, 99.3]% | -46.96607 [-50.19452, -43.82355] |
| newer vs older | Y | 188/293 | [58.7, 69.6]% | -0.00676 [-0.00884, -0.00464] |
| newer vs older | density | 161/293 | [49.1, 60.8]% | -4.91887 [-7.23052, -2.64177] |

## Benchmark and task status

The locally audited R2 benchmark contains 299 records with 154 positive and 145 negative labels. All have record-level source mappings in `analysis/benchmark_audit.json`. However, saved novelty predictions for the four measures and provenance-verified raw abstract-only historical/test embeddings are absent. The benchmark cannot support AUROC calculations from available evidence; this report does not infer scores from labels or the title-plus-abstract cache.

Task 3 additionally lacks verified earliest-publication dates and a defensible encoder training cutoff for every test record. The 25,186 historical review records are locally recovered, but there are no corresponding completed abstract-only matrices or benchmark predictions. Existing OpenReview release dates do not establish that a paper was first published after the model cutoff.

## Limitations and incomplete rubric requirements

- **Task 1:** six focal papers still lack four evidence-supported claims in the latest future-use artifact (294/300 meet the count); the original scored claim input is unchanged and had 58/300 short sets. Accepted additions were AI-reviewed, not independently human-certified.
- **Task 2:** original partial-coverage manipulations insert synthetic papers with claims, not claims planted into nearest existing papers. The 964 nearest-planting plans remain unscored and 1,304 modified-paper vectors are missing. Eleven paraphrase candidates are available, but zero are independently approved or scored and zero new embeddings are present. Near/far and temporal results cover 241/300 for all four measures; a separate saved Y/density extension covers 293/300 descriptively, while N/`yours` remain at 241. The original results are retrospective relative to Git history; written preregistration dates do not make them prospectively registered.
- **Task 3:** no AUROC, quality-baseline comparison, or paired novelty-minus-quality intervals; no cutoff/earliest-publication verification; no complete provenance-bound embedding matrices. Benchmark labels are existing operational labels, not newly collected human judgments.
- **Task 4:** interpretation is complete, but no empirical human-check agreement result can be asserted.
- Original pool manipulations include synthetic interventions and do not control for all differences in synthetic-text style or pool composition. Coverage uses the extraction-order first N claims; claim order is not a relevance ranking.
- No score was recalculated during report construction beyond arithmetic summaries of saved scores. Protected score hashes are checked by the included read-only reproducer.

## Single next recommended action

Obtain source-backed full-text evidence for the six remaining claim-short focal papers, then complete their claim review in a separately versioned future-use artifact; do not replace claims in the original 2,400-case score run.
