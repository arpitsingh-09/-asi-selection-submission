# Cache-only Task 2 extension results

Preregistered before new evaluation in commit `588d15bda62861b6ab4d7e1dc4820fcf46020588`. Prior development results were already exposed.

| Contrast | Earlier 241 | New 52 | Combined descriptive 293 |
|---|---|---|---|
| Y: near < far | 241/241 (100.0%; 100.0–100.0%) | 52/52 (100.0%; 100.0–100.0%) | 293/293 (100.0%; 100.0–100.0%) |
| density: near < far | 236/241 (97.9%; 95.9–99.6%) | 51/52 (98.1%; 94.2–100.0%) | 287/293 (98.0%; 96.2–99.3%) |
| Y: newer < older | 152/241 (63.1%; 56.8–69.3%) | 36/52 (69.2%; 55.8–80.8%) | 188/293 (64.2%; 58.7–69.6%) |
| density: newer < older | 133/241 (55.2%; 49.0–61.4%) | 28/52 (53.8%; 40.4–67.3%) | 161/293 (54.9%; 49.1–60.8%) |

Cells show passes/valid, rate and 95% paper-bootstrap percentile interval (10,000 draws, seed 20261113). Strict difference < -1e-8; ties fail. New density newer/older has four ties. All four preregistered majority-of-papers predictions passed; this is not a significance claim.

New sample counts: {'computation_language': 20, 'computer_vision': 13, 'machine_learning': 19}. Four conditions × two scores × 52 papers = 416 new scalar scores, 208 paired contrasts.

Combined results are descriptive Y/density aggregates only: identical representation, formulas, chronological candidate rules, pool sizes, ordering and pass criteria; distinct claim-screening stages. They are not one blind/prospectively registered cohort. Earlier scores were reused, not recomputed. N/yours coverage remains 241.

Protected original results, cache and frozen plan hashes were unchanged. No new embedding/model load, E6 write/control operation, original scoring run, or held-out evaluation occurred. Six targeted synthetic tests passed, including exact original-formula parity.

## Remaining and exact next action

Y/density now cover 293 focals. N/yours still require exactly **93** unique missing claim vectors across the new 52, enumerated in `missing_claim_vectors.jsonl`. The pool-blocked focal requires no additional claim vectors. Six papers remain claim-incomplete. Nearest planting and paraphrase remain unscored pending their missing inputs/vectors.

Implement the bounded 93-request Task 2 sidecar encoder/overlay adapter described in `claim_vector_execution_plan.json`, reusing pinned CPU loading and validation. Keep inference disabled until a safe authorized resource window; do not write the existing cache or alter Task 3 frozen plans.
