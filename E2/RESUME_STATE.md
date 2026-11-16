# E2 resume state — 2026-11-13

Read the official local ASI_Intern_Recruitment_Form.pdf, pages 30–31, directly.
The repository stopped at commit `1fa6cf5` (Task 3 preparation), followed by
uncommitted temporal/publication-review work. Earlier substantive commits are
`e8577a9` (archived inputs), `44077c4` (cached comparisons and claim recovery),
`a8364cd` (continuation protocol), and `b784a39` (offline analysis). Existing
uncommitted scripts, artifacts and modifications were retained.

The precise pre-run state: 300 focal records; original extraction 242 compliant
by count and 58 short; cumulative saved recovery 255 count-complete and **45
short**. Original `scoring_results.jsonl` contains **2,400 successful records**,
300 each for baseline, exact copy, four coverage levels, concentrated and
distributed. These are score records with all four measures, not 2,400 individual
scalar values. Cached comparisons cover **241 distinct papers**, and **964
nearest-planting plans remain unscored**. The Task 3 saved validation has 0/25,485
historical/test vectors and 0/299 claim sets. Its earlier 87-test record and later
77-test publication-review record refer to different recorded suite selections;
neither is experimental evidence and neither was rerun here.

## Requirement-by-requirement disposition

| Mandatory requirement | Status at resume | Existing evidence / precise gap |
|---|---|---|
| Three pools, at least 1,000 each; 100 focal papers each | Completed with experimental evidence | `data/pool_manifest.csv`, `data/focal_papers.csv`, `data/claims_v8_selected.jsonl`; 3 × 1,000 pool records and 300 distinct focals |
| 4–10 atomic claims per focal, extracted with an LM | Partially completed | Original 58 short; prior cumulative `analysis/shared_excerpt_recovery_v1/claims_future.jsonl` had 45 short. This run's cumulative `analysis/claim_completion_v1/claims_future.jsonl` had 23 short; latest `analysis/claim_completion_v2/claims_future.jsonl` has 6 short (294 count-eligible). Atomicity/source-review caveats remain |
| Exclude focal; enforce strictly prior literature | Completed implementation, partial experimental coverage | `novelty.py`, `manipulation_extensions.py`, frozen pool plans and cached comparisons; current Task 3 chronology is only against observed OpenReview releases |
| Exact-copy manipulation | Completed with experimental evidence | `data/manipulation_plan.jsonl`, `data/scoring_results.jsonl`, `analysis/saved_results_report.json` (300 cases) |
| Paraphrased-copy manipulation | Partially completed | Five existing v33 pilots plus six new source-bound AI drafts in `analysis/paraphrase_additions_v1/` and `v2/`; 289 candidates absent; new drafts lack independent review/vectors/approval; no scored pass rates |
| Nearest-paper planting at 25/50/75/100% | Implemented but not executed | `manipulation_extensions.py`, 964 nearest plans in `analysis/cached_extensions_v1/nearest_planting_plan.jsonl`; 1,304 distinct modified texts lack vectors. Old scored coverage inserts synthetic papers and does not satisfy nearest planting |
| Concentrated vs distributed | Completed with experimental evidence, limited by original short sets | `data/scoring_results.jsonl`, `analysis/saved_results_report.json`; 300 paired cases, descriptive concentration directions; old N equality prediction was wrong |
| Near vs far | Partially completed | Earlier 241 plus `analysis/task2_extension_52_v1/`: Y/density 293 papers, N/yours 241; cache-available pools |
| Older vs newer | Partially completed | Y/density 293 papers, N/yours 241; temporal direction is an empirical prediction, not universal |
| Predict each manipulation/measure first | Partially completed | `../PREREG.md` timing is retrospective; committed `CONTINUATION_PROTOCOL.md` predates cached-extension computations only. Do not relabel earlier results as prospective |
| Four measures and public scoring interface | Completed with experimental evidence | `novelty.py`, original 2,400 score records; density uses SPECTER2 adaptation and capped small-pool neighbors |
| Per-measure pass rates for every manipulation | Partially completed | Saved original and cached-comparison summary JSON; paraphrase/nearest planting and full focal coverage remain missing |
| Post-cutoff human-check paper identities/labels | Partially completed; eligibility blocked | 299 benchmark records and source hashes in `analysis/recovered_inputs_v1/`; `analysis/task3_publication_review_v2/`: 299 observed releases, zero first-global verifications, three identity-review candidates |
| Quality-only ridge on earlier same-venue review ratings | Implemented but not executed | `human_check.py`, `task3_execution.py`; 25,186 historical targets/manifests available; required raw abstract-only vectors absent |
| Four novelty AUROCs and quality AUROC | Blocked | Eligibility/cutoff, 299 benchmark claim sets, embeddings and four predictions absent; `TASK3_EXECUTION.md`, publication-review report. Frozen plan is preserved and has stale code fingerprints; no evaluation authorization |
| Novelty-minus-quality with intervals | Implemented but not executed; blocked with AUROCs | `human_check.py`, `evaluate_human_check.py`, Task 3 protocol; no benchmark numerical outputs |
| Task 4 interpretation paragraph | Completed | `README.md`, Task 4 paragraph, unchanged |
| Deliverable manifest/generator/results/interface | Partially completed overall | Manifest, generators, original JSON results and interface exist; missing mandatory results above prevent submission readiness |

## Work completed in the previous run

Resumed Task 1 rather than repeating the completed publication audit or blocked
Task 3 evaluation. Extracted **27 new source-bound claims for 22 papers**, reducing
the cumulative short-set queue from **45 to 23**; **277/300** now meet the count
range. Saved distinctness reviews and exact source hashes/lines in
`analysis/claim_completion_v1/`. Claims are explicitly Codex AI extractions,
not historical recovery or human approval. No scored input was changed.

`complete_claim_additions.py` materializes the new cumulative artifact separately,
rejects unsupported/duplicate claims and conflicting source duplicates, and
checks source preservation. All 27 excerpts matched; six new focused tests
passed. All 27 new claim vectors are absent, so no new experimental score was
available safely. No original experiment, audit pipeline or full test suite ran.

## Latest short-set continuation

Reviewed all 23 remaining short sets in `analysis/claim_completion_v2/`.
Completed 17 using 73 source-bound atomic/qualified claims (22 reused verbatim).
Six papers lack sufficient substantive evidence in cached abstracts and have
no matching local full text in the inspected paths. The cumulative artifact now
has **294/300 count-eligible focal papers**. Those six are explicitly unresolved;
prior semantic limitations are preserved. Seven targeted revision tests passed.
See `analysis/claim_completion_v2/TASK1_SUMMARY.md` for exact evidence and limits.

## Latest executed Task 2 extension

Preregistered the exact 52-paper cache-ready cohort, fixed protocol, scorer and
synthetic tests in commit `588d15b` before any new evaluation. Saved outcomes in
`analysis/task2_extension_52_v1/`. New pass counts: Y near/far 52/52; density
near/far 51/52; Y newer/older 36/52; density newer/older 28/52. Full bootstrap
intervals, prior-versus-new results and descriptive compatible aggregation are
in `REPORT.md` and `summary.json`. Y/density now cover 293 distinct focals;
N/yours remain at 241. Earlier experiments were not rerun. Six new targeted
synthetic tests passed. Source/cache/frozen-plan hashes remained unchanged.

## Latest sidecar implementation

`claim_sidecar.py` now implements the bounded 93-request CPU encoder and
read-only original+sidecar overlay. `analysis/claim_sidecar_v1/` is prepared with
all request, source, code and model fingerprints; it has **0/93 vectors** and
inference is disabled. Nineteen targeted synthetic tests passed. `novelty.py`
and the old cache are unchanged; the overlay supplies a private read-only
encoder binding to the original score function. See `CLAIM_SIDECAR.md`.

Without inference, also materialized 1,304 exact missing modified-paper text
requests for the existing 964 nearest-planting plans in
`analysis/nearest_planting_vector_requests_v1/`. No plan or experiment was rebuilt.

## Latest N/custom continuation

`task2_claim_extension.py` and the separate fixed-52 protocol/input manifest
were committed as `77a4091`. Sixteen targeted synthetic tests passed. The driver
reuses saved pools and Y, computes only N/custom, and requires all 93 vectors plus
new checksum-bound evaluation authorization. It has not run on real data;
actual sidecar status is 0/93, authorization false. Existing Y/density 293 and
N/custom 241 coverage is unchanged. See `TASK2_N_CUSTOM_IMPLEMENTATION.md`.

Also produced three new source-bound paraphrase drafts, with claim-to-passage
coverage and AI review, in `analysis/paraphrase_additions_v1/`. There are now eight
candidate papers and 292 without candidates. All three new drafts remain pending
independent review, with no vector or scoring approval; existing pilot data and
frozen plans were preserved.

## Latest Task 3 input preparation

Eligibility remains **0/299 verified**: observed OpenReview dates do not rule out
earlier preprints, and the pinned model card supplies no exact final publication
date for citation or adapter training. The saved December 2024 bound is unchanged;
2023 card-update notes do not establish a cutoff. Existing protocols/plans were
not weakened, regenerated or edited; no eligible subset or held-out result exists.

Prepared the first **10 benchmark claim sets (51 exact source-bound claims)** in
`analysis/task3_claims_batch_v1/`, validated with the existing importer and exact
excerpt offsets. The other 289 IDs are queued there. This is separate supplied
preprocessing, not a change to the frozen plan's zero-claim state. No benchmark
labels/ratings or numerical evaluation outputs enter the new claim packets.

Also added three genuinely new Task 2 paraphrase drafts, one per pool, in
`analysis/paraphrase_additions_v2/`. There are now 11 candidate papers and 289
without candidates. Drafts lack independent approval/scoring permission; no
embedding or metric was generated. See the Task 3 batch README for exact blockers.

## Exact next action

Continue source-bound benchmark claim extraction for the 289 IDs in
`analysis/task3_claims_batch_v1/remaining_forum_ids.json`, with exact excerpts,
abstract hashes and explicit AI/human review distinctions. In parallel, real
eligibility still requires authoritative first-publication and cutoff-policy
resolution; local card metadata and OpenReview cohort dates cannot supply it.
Do not run inference or Task 3 evaluation while its gates fail.

E6, NOTEBOOK.md, AI_LOG.md, signed artifacts, original scores, datasets and
checkpoints were not modified. Nothing was pushed.
