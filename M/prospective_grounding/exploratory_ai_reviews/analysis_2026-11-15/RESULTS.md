# Exploratory comparison of available prospective-grounding assessments

## Sources and eligibility

The available AI assessment source is `/Users/arpit/asi-selection/M/prospective_grounding/exploratory_ai_reviews/assessments_imported.csv`: 18 complete abstract-summary ratings, model identity unknown. No separate Claude or Gemini review files were located in the exploratory review directory or Downloads, so this dataset cannot be attributed to either model separately.
The second source is `/Users/arpit/Downloads/human_researcher_ai_exposed_review_2026-11-15.json`. It is submitted as `HUMAN-RESEARCHER-01` on `2026-11-15`. Its provenance describes it as researcher-authored with prior AI exposure, while also noting that authorship is not independently verified; it records `independent_review_confirmed=false`. It is not an independent blinded human review.
Both sources cover the same 18 registered question–paper pairs. Ratings and evidence-note presence were validated; source evidence remains unchanged. The AI file contains no association checks. The researcher file contains six complete association checks. Some researcher evidence notes contain `[cite: ...]` placeholders that have not been independently verified.

## Rating agreement

Exact agreement was **14/18 (77.8%)**. Unweighted nominal Cohen's κ was **0.664**; linear-weighted κ was **0.737**. Both sources had the same marginal counts: 0=6, 1=7, 2=5. No confidence interval or significance test was calculated.

| Registered comparison group | n | External-AI mean | AI-exposed researcher mean | Exact agreement |
|---|---:|---:|---:|---:|
| Primary questions — original papers | 6 | 1.500 | 1.500 | 4/6 |
| Same-topic decoys — original papers | 6 | 1.333 | 1.333 | 4/6 |
| Primary questions — cross-family shuffled controls | 6 | 0.000 | 0.000 | 6/6 |

Both sources rated all six shuffled cross-family pairs 0. Mean rating was 1.500 for primary/original pairs and 1.333 for decoy/original pairs. On the six within-family, same-paper primary-versus-decoy comparisons, mean primary-minus-decoy rating was 0.167 for each source; five pairs tied and one favored the primary. These are descriptive comparisons only, with two families and repeated papers/questions.

## Disagreements

All four rating disagreements were one-point 1-versus-2 differences, confined to two image-enhancement papers and repeated for both the primary and decoy question:

| Question | Paper | External AI | AI-exposed researcher |
|---|---|---:|---:|
| `decoy-image_enhancement-v2` | `2012.15020v1` | 2 | 1 |
| `decoy-image_enhancement-v2` | `2412.20916v1` | 1 | 2 |
| `primary-image_enhancement-v2` | `2012.15020v1` | 2 | 1 |
| `primary-image_enhancement-v2` | `2412.20916v1` | 1 | 2 |

These splits are at the rubric boundary between topical evidence and direct relevance, suggesting ambiguity in how these abstracts ground the premise. They do not establish which rater is correct or show model performance.

## Decoy checks and preregistered status

- `decoy-image_enhancement-v2` (image_enhancement): same broad topic = true; unsupported by supplied papers = false.
- `decoy-video_memorability-v2` (video_memorability): same broad topic = true; unsupported by supplied papers = true.

The available researcher check marks both decoys same-topic; it marks the video-memorability decoy unsupported, but does not mark the image-enhancement decoy unsupported. There is no AI association-check vector for comparison. The required **two independent reviewers** have not supplied eligible blinded reviews; the preregistered human-review requirement remains incomplete. No scoring authorization, G/B-TF score, baseline comparison, or registered confidence interval is present. These exploratory assessments do not complete any of the original nine evaluations.

## Reproduction and files

Run from the repository root (reads sources, writes only this exploratory analysis directory):

```sh
python3 M/prospective_grounding/exploratory_ai_reviews/analysis_2026-11-15/analyze_reviews.py --human-json '/Users/arpit/Downloads/human_researcher_ai_exposed_review_2026-11-15.json' --output-dir /tmp/prospective_grounding_analysis_reproduced
```

`results.json` contains validation, metrics, group summaries, decoy checks and disagreement pairs. `pairwise_comparison.csv` contains only IDs, group labels and the two ratings; source evidence notes remain in their original files.
