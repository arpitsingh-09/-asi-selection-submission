# E2 experimental results and review materials

## Nearest-paper planting

All 1,304 modified-paper vectors passed the frozen inventory check. The evaluator used the completed database to score all 964 planned conditions for 241 focal papers. At 100% planting compared with the matched baseline, N and the custom measure decreased for all 241 papers. Y was lower for 189 and tied for 52. Density was lower for 167, tied for 66 and higher for eight. Results across successive coverage levels were less consistent. For example, increasing coverage from 75% to 100% lowered N for 227 papers, tied for three and raised it for 11. The comparison unit is a focal paper. These counts apply to the 241 papers in this planting plan.

[All seven paired contrasts, with ties](analysis/nearest_planting_results_v1/REPORT.md) · [Numeric summary](analysis/nearest_planting_results_v1/summary.json) · [Per-paper scores](analysis/nearest_planting_results_v1/results.jsonl)

## Paraphrased copies

The review batch contains one candidate for each of the 300 original focal papers, 100 per subfield. Of the previous 17 candidates, nine retain their exact text and eight have updated titles, including the correction for extreme class imbalance. Every candidate now differs from its source in both title and abstract. The present candidates have zero exact vector matches in the original cache. Independent dispositions and experimental scores are pending.

The 283 additions use three authoring methods. Thirty-one received individually written abstracts, 37 received individually written openings and further edits where available, and 215 used sentence edits that draw on the source and previously extracted claims. Those edits retain substantial source wording. A case-insensitive word-sequence comparison, excluding punctuation, assigns a similarity of at least 0.85 to 248 abstracts and at least 0.95 to 133. This is an editorial screening measure. Strong copying makes a candidate less informative for testing robustness to paraphrasing even when the meaning is correct. Seven high-level drafts need particular attention to method coverage. Human decisions should consider both meaning and the extent of rewording. Source lines and hashes identify the records to compare.

[Side-by-side comparison](analysis/paraphrase_review_300_v1/compare.html) · [Decision worksheet](analysis/paraphrase_review_300_v1/review.csv) · [Candidate records](analysis/paraphrase_review_300_v1/candidates.jsonl) · [Inventory and checksums](analysis/paraphrase_review_300_v1/inventory.json)

## Other E2 stages

The saved N/custom extension contributes 52 additional papers to the 241 previously evaluated on the near/far and newer/older contrasts. Its stage-specific rates are reported separately because the cohorts used different claim-extraction stages. Six originally short abstract-based claim sets have a separate packet with 24 proposed full-text claims for future use.

[Fixed-52 results](analysis/task2_n_custom_52_v1_eval_2026-11-18/REPORT.md) · [Six-paper claim packet](analysis/blocker_recovery_v1/full_text_claims.md)

The supplementary Task 3 cohort policy has been adopted. Six works in the original cohort have documented pre-bound public versions. The other 293 remain unresolved under the first-publication and text-version requirements. The current verified subset is empty. The held-out AUROC and quality-baseline comparison are unavailable.

[Cohort decision](analysis/task3_subset_decision_v1/DECISION.md) · [All 299 dispositions](analysis/task3_subset_decision_v1/cohort_disposition.csv) · [New primary-source findings](analysis/task3_subset_decision_v1/VERSION_NOTES.md)
