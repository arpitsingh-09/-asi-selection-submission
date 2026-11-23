# Novelty scores after planting claims in the nearest papers

We evaluated all 964 fixed conditions for the 241 eligible focal papers. Each comparison pairs scores for the same paper. At each coverage level, the synthetic papers replace the original nearest papers in the same pool positions. A pass means the score increased by at most 1e-8. Values in parentheses count ties included among the passes. Each cell has denominator 241.

| From | To | Y passes (ties) | N passes (ties) | Custom passes (ties) | Density passes (ties) |
|---|---|---:|---:|---:|---:|
| baseline | 25 | 240 (95) | 241 (0) | 241 (0) | 235 (122) |
| baseline | 50 | 241 (83) | 241 (0) | 241 (0) | 236 (99) |
| baseline | 75 | 241 (62) | 241 (0) | 241 (0) | 234 (73) |
| baseline | 100 | 241 (52) | 241 (0) | 241 (0) | 233 (66) |
| 25 | 50 | 238 (194) | 237 (3) | 237 (3) | 237 (162) |
| 50 | 75 | 239 (175) | 235 (3) | 238 (2) | 234 (162) |
| 75 | 100 | 239 (185) | 230 (3) | 233 (2) | 235 (193) |

The three subfields contributed 76 computation language, 86 computer vision, 79 machine learning papers. The pass rates describe this cache-eligible development cohort. Per-paper baseline and condition scores are in results.jsonl. The complete rates, mean differences and input database fingerprint are in summary.json.
