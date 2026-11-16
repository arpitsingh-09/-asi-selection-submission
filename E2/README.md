# E2 — Novelty axioms, rebuilt

Current task-by-task evidence status and saved-result summary: see
[COMPLETION_REPORT.md](COMPLETION_REPORT.md). The historical status notes below
describe the original saved-score cohort; cache-only near/far and temporal
extensions are reported separately and do not complete the original missing
conditions. Task 1 and Task 2 remain partial, Task 3 remains blocked at
evaluation, and Task 4's interpretation is complete.

Task 3 execution preparation: see [TASK3_EXECUTION.md](TASK3_EXECUTION.md) for
the frozen CPU workflow, pinned encoder evidence, authorization gates, resource
estimates and exact remaining blockers. No inference or evaluation ran.

Latest recovery: see [LOCAL_RECOVERY_RESULTS.md](LOCAL_RECOVERY_RESULTS.md).
All 299 archived OpenReview records and a dated 25,186-paper reference pool
are now recovered; 45 future claim sets remain short. This supersedes earlier
claims that test dates and original abstracts were unavailable locally.

Latest continuation: see [CONTINUATION_RESULTS.md](CONTINUATION_RESULTS.md) for
claim recovery, newly computed cache-only near/far and temporal comparisons,
and the exact remaining Task 3 blockers. The sections below describe the
b784a39 baseline; continuation results supersede the corresponding gap counts.

Status on 2026-11-16: **not submission-ready**. Tasks 1–2 are partial,
Task 3 is blocked at evaluation, and Task 4 is complete. The authoritative
rubric was read directly from pages 30–31 of the local original
`~/Downloads/ASI_Intern_Recruitment_Form.pdf`; its text agrees with
`~/Downloads/asi_assignment.txt`. No new inference or experiment was run.

## Task 1: partial

Actual manifests contain three pools of 1,000 unique papers each and 100
focal papers each (300 distinct focal papers total). The selected extraction
artifact has 242 records with 4–10 claims and **58 with fewer than four**
(2 with one, 13 with two, 43 with three). Original extraction records are
preserved; adding claims without source review would not resolve this gap.

The existing generator and scored plan contain baseline, exact copy,
25/50/75/100% coverage, concentration and distribution (300 cases each).
Focal IDs are excluded. The coverage implementation inserts new synthetic
papers containing the first N claims; it does **not** plant those claims into
nearest existing papers as required by the rubric. Ceiling coverage can
exceed its nominal percentage; see `data/coverage_manipulation_audit_v1.md`.
The existing paraphrase pilot and AI review notes do not establish a complete,
independently reviewed 300-paper paraphrase condition.

`manipulation_extensions.py` now supplies offline constructors for nearest
paper planting, equal-size strictly prior near/far and older/newer pools,
and provenance-bearing paraphrased copies. These functions require frozen
similarities and reviewed paraphrase inputs; they have **not been scored**.
New artifacts should be written separately, never over the saved scoring
files. The old experiment cannot be repaired by relabeling it.
Predictions in `../PREREG.md` are retrospective relative to Git history;
new constructors do not cure that timing limitation.

## Task 2: partial

`novelty.py` already exposes the required `score(idea_text, claims, pool_ids,
t)` interface and implements Y, N, density and yours. All four scores point
upwards for greater novelty; density is a local-distance rank percentile.
The RND implementation uses SPECTER2 rather than the original paper's
embedding configuration and caps neighbour counts for small eligible pools.
Synthetic unit-test success does not establish exact reproduction or validity.

`analysis/saved_results_report.json` reports the 2,400 existing successful
scores, per-measure pass counts/denominators and 95% paper-bootstrap intervals
(10,000 replicates, seed 20261113). Each of 300 distinct focal papers is one
sampling unit. Coverage is compared both with baseline and with the preceding
coverage level. Nonincrease permits ties within 1e-8; exact copy and lower
concentration require a decrease greater than 1e-8. These explicit reporting
rules are retrospective, not newly preregistered experimental outcomes.

| Contrast (passes / 300) | Y | N | yours | density |
|---|---:|---:|---:|---:|
| Exact copy < baseline | 300 | 284 | 300 | 295 |
| Concentrated < distributed | 216 | 0 | 96 | 26 |

The concentration row is a descriptive direction count. In particular, the
old N equality prediction conflicts with its T2 derivation; density had no
fixed concentration direction. Do not call all columns axiom passes. Cache-only
near/far and newer/older results on subsets are reported in
`CONTINUATION_RESULTS.md` and `analysis/task2_extension_52_v1/REPORT.md`; they
do not provide complete original-condition coverage for all four measures.
Paraphrased copy and nearest-paper planting still have no scored results.
`run_scoring.py` was not run and must not be used to overwrite existing work.

## Task 3: blocked; offline implementation complete

`analysis/benchmark_audit.json` validates the cached R2 source: 299 records,
154 POSITIVE and 145 NEGATIVE. This local Parquet revision has title, rating,
contribution and forum ID at the top level. `human_check.normalize` supports
nested `metadata` too, and rejects conflicting duplicate fields. All 299
records already supply forum IDs: the mapping report preserves these direct
source mappings. Unique normalized-title resolution is available for other
sources; ambiguous matches remain unresolved.

No item-level publication dates exist in the inspected benchmark. Forum IDs
and the ICLR 2026 cohort do not establish posting dates or an encoder training
cutoff. **Post-cutoff eligibility remains unverified for all 299 records.**
No dates were inferred from IDs, review ratings, or the cohort year.

Earlier same-venue official reviews are locally available in
`~/Downloads/iclr_task3_baseline/data`. The implemented reader handles
OpenReview v1 `recommendation` and v2 `rating` fields, wrapped values and
official-review invitations, deduplicates review IDs and requires at least
two numeric official reviews and a nonempty abstract. After conservative
exclusions, eligible counts are 2,617 (2022), 3,792 (2023), 7,260 (2024), and
11,517 (2025): **25,186**. `analysis/historical_manifest.csv` records IDs,
years, titles, review counts and mean ratings. Four title-overlap candidates
are listed in the audit; exact test IDs and normalized titles are excluded
too. This does not guarantee discovery of all semantic near-duplicates.

`human_check.py` implements abstract-only frozen-embedding ridge regression,
training-fold standardization, chronological expanding-window validation for
2023/2024/2025, the protocol's nine-alpha grid, pooled validation MSE selection,
and final historical refit. Benchmark labels, ratings and contribution fields
are never baseline inputs. Embeddings must be supplied separately with aligned
IDs and provenance; the title-plus-abstract novelty cache is not a substitute.
No SPECTER2 model was loaded for Task 3 and no historical fit was executed.

It also implements tied-rank AUROC and paired class-stratified bootstrap
intervals (10,000 replicates, seed 20261113) for all AUROCs and novelty minus
quality AUROC differences. `evaluate_human_check.py` connects the baseline
and comparison, rejects test overlap and missing publication dates, and
requires verified preregistration/cutoff declarations and a matching protocol
hash before evaluation. It refuses to overwrite output. Synthetic tests use
invented arrays only as fixtures, never as benchmark results.

**Numerical results unavailable:** no saved benchmark scores for the four
novelty measures or provenance-verified abstract-only historical/test
embedding matrices are present among the inspected E2 artifacts. Consequently
no benchmark AUROC or baseline difference/interval is reported. Historical
reviews themselves are not the blocker. The retrospective `TASK3_PROTOCOL.md`
is not prospective preregistration. A later authorization cannot turn earlier
test exposure into a prospective study; the evaluation design and exposure
must be reconciled before held-out evaluation. The pipeline is implemented
without bypassing this restriction.

R2's operational labels are not independent of quality: positives combine
reviewer novelty praise without dissent, acceptance, top-area rating decile
and contribution >=3; negatives combine novelty criticism without praise,
rejection, bottom-area decile and contribution <=2. Source construction uses
AI-assisted processing. These are operationally mined reviewer judgments,
not newly collected unanimous human ratings; quality confounding and benchmark
selection must be disclosed in any eventual AUROC comparison.

## Task 4: completed interpretation

A measure that passes every axiom but fails the human check may respond
consistently to controlled literature manipulations while measuring a notion
of novelty that differs from reviewers' judgments, or while losing semantic
information through its representation; axiom compliance alone does not
establish usefulness on real papers. Conversely, a measure that agrees with
human labels but fails axioms may exploit quality, topic, writing style, or
benchmark selection rather than novelty, or reveal that an axiom's idealized
assumptions do not describe natural text. Agreement on both tests is stronger
evidence than either alone, but requires valid manipulations, temporal
separation and leakage controls, and novelty AUROC beyond the quality-only
baseline with paired uncertainty intervals; intervals crossing zero do not
prove equivalence. Here the missing human-check predictions prevent any
empirical claim of agreement or disagreement, and the saved concentration
results already show that the proposed combined measure's idealized guarantee
does not reliably transfer to these real embeddings.

## Offline validation and preservation

Run `.venv/bin/python -B -m unittest discover -s E2/tests -p 'test_*.py' -v`.
Validation on 2026-11-13: **44 tests passed**. Tests use mocked embeddings or
tiny arrays; they do not run experiments. The existing urllib3/LibreSSL warning
is nonfatal. Local Parquet reading also emits sandbox sysctl warnings; metadata
loading completed successfully.
`python3 -B E2/complete_offline.py --benchmark PATH.parquet --history PATH/data`
regenerates analysis reports from existing scores and local metadata. It
requires NumPy and PyArrow, which are not version-pinned in this repository.
The benchmark Parquet and historical data are external inputs. The script
verifies saved scoring hashes before and after and never imports `novelty`, but
it writes to `E2/analysis/` and overwrites several report JSON files. Preserve
or copy those report files before invoking it if the current reports must
remain unchanged.

The saved score hashes are in `analysis/saved_results_report.json`. No E6
file, lock, process, supervisor or Ollama service was modified or controlled.
No push was performed.
