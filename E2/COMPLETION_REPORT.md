# E2 completion report: evidence status

This report consolidates the official E2 Tasks 1–4 against saved repository
artifacts. Official requirements are in the assignment PDF, pp. 30–31. No
scoring, model inference, training, or new experiment was run for this report.
The protected `data/scoring_results*.jsonl` files were read only.

## Status by task

| Task | Status | What the available evidence establishes | Remaining gap |
|---|---|---|---|
| 1 — construct pools/manipulations | Partial | Three 1,000-paper pools; 100 focal papers per pool; 300 distinct focals; eight saved conditions; 242/300 original focal claim sets contain 4–10 claims. | 58 original sets have fewer than four claims. Paraphrase has only five incomplete/unscored candidates. The original partial-coverage implementation adds synthetic claim-bearing papers instead of planting claims into nearest existing pool papers. Nearest planting plans are unscored; full near/far and older/newer coverage is incomplete. |
| 2 — novelty measures/axioms | Partial | Saved results contain 2,400 successful scores for Y, N, yours, and density across baseline, exact copy, four coverage levels, concentrated, and distributed. Directional pass rates and paper-bootstrap intervals are available. | No original scored paraphrase or nearest-planting condition. Full eligible focal coverage for near/far and temporal comparisons is absent; newer cache-only comparisons cover Y/density only. RND uses SPECTER2 rather than the original paper's embedding configuration, and small-pool neighbor counts are capped. |
| 3 — human check | Blocked at evaluation | The supplied human-only benchmark has 299 records (154 positive, 145 negative), and the source human-review-derived labels and archived original abstracts are locally available. The official task asks for this existing human-check comparison; it does not require new independent human ratings. | No benchmark novelty predictions, historical/test abstract-only embeddings, complete source-supported claim sets, or resolved first-publication histories. The encoder's exact training cutoff is unknown; the pinned weights only establish an existence bound. Eligibility and the numerical AUROC/quality-baseline comparison therefore cannot be established. |
| 4 — interpretation | Complete | `README.md` explains both possible disagreements between axiom and human-check outcomes and states the limits of agreement. | None for the required interpretation paragraph. |

## Saved Task 2 results

The original saved-results analysis covers 300 distinct papers, with no focal
paper appearing in its pool. It reports 95% paper-bootstrap percentile
intervals from 10,000 replicates (seed 20261113). Values below are directional
pass counts/300 and pass-rate intervals; they are descriptive of the saved
implementation and not evidence that a task condition was implemented exactly
as the assignment specifies.

| Saved contrast | Y | N | yours | density |
|---|---:|---:|---:|---:|
| Exact copy < baseline | 300 (100%; 100–100%) | 284 (94.7%; 92–97%) | 300 (100%; 100–100%) | 295 (98.3%; 96.7–99.7%) |
| Concentrated < distributed | 216 (72%; 67–77%) | 0 (0%; 0–0%) | 96 (32%; 26.7–37.3%) | 26 (8.7%; 5.7–12%) |
| 50% coverage ≤ 25% coverage | 272 (90.7%; 87.3–93.7%) | 172 (57.3%; 51.7–63%) | 252 (84%; 79.7–88%) | 280 (93.3%; 90.3–96%) |
| 100% coverage ≤ 75% coverage | 196 (65.3%; 60–70.7%) | 120 (40%; 34.3–45.7%) | 177 (59%; 53.3–64.7%) | 279 (93%; 90–95.7%) |

The concentration pattern is a genuine negative result for the proposed
combined measure (`yours`: 32% directional decreases; density: 8.7%). The
saved N concentration result also contradicts the old equality prediction
(0/300 strict decreases), while density had no fixed concentration direction.
These outcomes must not be described as universal axiom passes. For successive
coverage, the saved `N` pass rates are 57.3% (50 vs 25%) and 40% (100 vs 75%),
also demonstrating substantial non-monotonicity.

## Cache-only extensions (supplementary, not Task 1/2 completion)

The separately frozen continuation and 52-paper extension used cached vectors
only and had prior artifact exposure. Across 293 development papers, Y near<far
passed 293/293 (100%; 95% CI 100–100%) and density passed 287/293 (98.0%;
96.2–99.3%). For newer<older, Y passed 188/293 (64.2%; 58.7–69.6%) and
density 161/293 (54.9%; 49.1–60.8%). These are descriptive pooled results from
different claim-screening stages, not a single blind or original registered
cohort; N and yours remain at 241 papers. Exact paired mean-difference
intervals and exclusions are in `analysis/cached_extensions_v1/summary.json`
and `analysis/task2_extension_52_v1/summary.json`. Near/far shares the
embedding geometry used for selection, so its strong response is not an
independent semantic-validity check. Temporal direction is an empirical
hypothesis.

Other saved construction evidence is not scored: 964 nearest-paper planting
plans lack the modified-text vectors (1,304 unique vectors missing), and the
five paraphrase candidates have no matching cached vectors; the other 295
focals lack a complete paraphrase condition. Recovered claims are a separate
future-use artifact, reviewed by Codex AI rather than a human, and were not
used to revise original results.

## Task 3 evidence and human review

The 299 benchmark labels are existing human-review-derived labels, but their
operational selection also uses ratings and contribution assessments and the
source pipeline includes AI-assisted processing. They are not independent
new ratings. The official Task 3 does not require collecting a fresh
independent panel; no new human novelty labels have been fabricated.

The benchmark's observed OpenReview release is 2025-10-08 UTC for all 299
records, but that is not proof of first global publication. Current local
review evidence verifies zero first-publication dates and leaves all 299
eligibility decisions unresolved; three title-identity candidates cover four
older records. The pinned encoder revisions establish that weights existed by
2024-12-04, supporting a conservative 2024-12-31 bound, not the model's exact
training-data cutoff. These gaps, plus absent Task 3 embeddings, claims, and
four-measure predictions, block AUROC and quality-baseline comparison. No
Task 3 score is reported.

`analysis/task3_publication_review_v2/REVIEW_FORM.csv` is a blank form for a
genuine retrospective source review. It records only existing forum/title/
abstract-hash/observed-release metadata; every reviewer and first-publication
field is blank. See the adjacent `REVIEW_FORM_GUIDE.md`. This review may
resolve paper identity and source provenance; it cannot establish an unknown
model training cutoff or turn the analysis into prospective validation.

## Reproduction and preservation

For the already-saved Task 1/2 results, inspect `analysis/saved_results_report.json`;
its source hashes, denominators, pass counts, confidence intervals, resampling
count, and seed are recorded there. Supporting deliverables are
`data/pool_manifest.csv`, `data/manipulation_plan.jsonl`,
`manipulation_generator.py`, and `novelty.py`. The existing reproduction
command is documented in `README.md`:

```sh
python3 -B E2/complete_offline.py --benchmark PATH.parquet --history PATH/data
```

Replace both placeholders with the original local benchmark Parquet and
historical OpenReview data directory; those input archives are not bundled in
this E2 folder, so report regeneration is not self-contained from the
submission copy alone. The command requires Python 3 with NumPy and PyArrow
installed; this repository does not pin those dependencies. The script
recomputes descriptive reports from saved
scores and metadata, verifies the two protected scoring-file hashes before
and after, and does not import the scoring/model implementation. It overwrites
several JSON reports under `analysis/`; preserve those files first if their
current versions must be retained. Do not use `run_scoring.py` to reproduce
these saved results. No scoring output or analysis report was regenerated or
overwritten here.

Verified SHA-256 values remain:

| File | SHA-256 |
|---|---|
| `data/scoring_results.jsonl` | `8aa38111b3dbdf5e4a24534486bb55aa081d6b4bdd32a56244a00e0b2fa99bdc` |
| `data/scoring_results.matmul_pilot.jsonl` | `9ded2fd37ce365fb13a4621497367315027d54ff2a41608c55cfa04bd7840b1f` |

Analysis scripts report model/configuration in their source artifacts and
reports. No new model version or compute was used in this documentation-only
work. The saved score report records the legacy SPECTER2-backed density
implementation; it is not a claim of exact reproduction of the cited RND
encoder setup. AI-assisted claim review and this synthesis are disclosed in
`../AI_LOG.md`.
