# AI log
| Date | Tool | Task | What I checked | Outcome |
|------|------|------|----------------|---------|
| Date not recorded in the contemporaneous note | Claude | Read the problem set and plan phases | Compared the proposed plan with the assignment rules | Plan adopted; no date inferred |
## At least one AI error I caught
The initial SPECTER2 evaluation used automatically created mean pooling
instead of the intended proximity adapter with CLS-token embeddings.
I identified the problem and ran a corrected evaluation; the correction
and its limitations are documented below.
## E1 authorship and tool use (2026-10-22)
- Items tagged AC (23 items): written by me. Claude helped check Jaccard numbers, flagged meaning errors, and made small edits (B_min verb swaps, a method-name substitution in h032). I checked the edits.
- Items tagged AS (29 items: h030, h035-h062): authorship and extent of manual editing are not reliably established by the current record; author confirmation is required.
- Items tagged XX (9 items: h009, h010, h022-h027, h029): the meaning of XX and the reasons h009 and h022 changed from AC are not documented in the available record; author confirmation is required.
- eval_contrast.py, eval_contrast_v2.py, audit_sources.py: original authorship and review history require author confirmation. The separate E1/evaluate_specter2_corrected.py script was generated with ChatGPT assistance and executed for the corrected SPECTER2 evaluation; its outputs were checked for successful completion and expected item count.
- AI errors I caught: (1) the E1 prediction line was left as the placeholders "NN" and "XX" because a template was never filled in; (2) the v1 scope metric (dAW > 0 and dAN > 0) was true for almost every item and measured nothing, so it was replaced in v2; (3) several B_min drafts changed the meaning of A (for example "without" became "with", or a copy of A was used) and were fixed.

- SPECTER2 correction (2026-10-22): the initial SentenceTransformers loading of `allenai/specter2_base` used automatically created mean pooling. A separate evaluation used the base model with the `allenai/specter2` proximity adapter and CLS-token embeddings. Corrected outputs are in `E1/results_specter2_corrected/`; original outputs were preserved. The corrected metrics supersede the earlier SPECTER2 metrics for future comparisons.

## 2026-11-13 — E2 offline completion work

Read the original assignment PDF, pages 30–31. Reused saved E2 scores; did not
run scoring, inference, Ollama, or E6 commands. Added metadata normalization,
local history inventory with four conservative exclusions, ridge/AUROC/paired
bootstrap implementation, missing manipulation constructors, offline tests,
JSON analysis reports and an honest Task 4 interpretation. All 299 benchmark
forum IDs were supplied directly; no publication dates or human judgments
were invented. Historical reviews exist (25,186 eligible after exclusions),
but Task 3 predictions, abstract-only embeddings, item-level dates/cutoff
verification and compliant evaluation preregistration remain missing. E2 is
not submission-ready. Existing scoring files retained identical SHA-256 hashes.

E2 offline validation: 44 tests passed; no scoring files changed.

## 2026-11-13 — E2 continuation from b784a39

Committed continuation protocol a8364cd before new cache-only computations.
Recovered 57 saved excerpt-backed claim candidates; explicit Codex AI semantic
review retained 13 additions across 13 papers. Ten future sets now reach four;
48 remain short. These are AI judgments, not fabricated human reviews. Original
claims and experiment results remain untouched; recovered claims were not used
in the new comparisons. Evaluated near/far and older/newer on 241 eligible
original focal papers using only read-only cached embeddings. Wrote 964 unscored
nearest-paper replacement plans and five blocked paraphrase plans; implemented
paired cache-only paraphrase support. Located the original nested R2 YAML and
mapped all 299 titles; no test dates, novelty predictions or abstract embeddings
were recoverable. A one-record low-priority CPU embedding preflight failed at
os.nice before loading a model, and no inference ran. Task 3 remains blocked.
Task 4 preserved. Offline suite: 61 tests passed. See E2/CONTINUATION_RESULTS.md.
E6 and Ollama untouched; no push.

## 2026-11-13 — E2 targeted archive recovery from 44077c4

Found ICLR 2026 notes inside the existing iclr.tar.bz2 archive, which previous
checks had missed. Joined all 299 benchmark forums, recovering archived full
abstracts and OpenReview online dates (2025-10-08 UTC). Preserved raw dates;
did not infer first global publication or a model cutoff. Froze 25,186 earlier
same-venue reference IDs with dates, source lines and abstract hashes. The
upstream documentation confirms R2 ideas are model-edited abstracts; only 14
exactly match the archived originals. Added an original-abstract hash binding
gate to prevent their accidental substitution in the quality baseline.
Task 3 remains blocked by model cutoff evidence, missing embeddings and missing
benchmark claims/predictions; no held-out evaluation or inference was run.
Recovered three further verbatim saved claims after reviewing shared-excerpt
candidates; separate future-use sets now leave 45 below four. Review is explicit
Codex AI review, not human judgment. No original experiment records were changed.
Zero of 964 nearest-paper plans have all modified embeddings; 1,304 unique text
vectors are missing. Existing cached results were preserved. 69 offline tests
passed; all six original source hashes match. E6/Ollama untouched; no push.

## 2026-11-13 — E2 Task 3 execution preparation from e8577a9

Verified all 299 test records have original abstracts, labels, public dates and
forum IDs. Rejoined 25,186 historical abstracts against the frozen reference
manifest and bound source/text/model/code hashes in a prepared execution plan.
Inspected local SPECTER2 config, tokenizer/adapter metadata and weight hashes
without loading a model. Official publisher commit pages date both pinned
revisions to 2024-12-04; recorded a conservative end-2024 weights-existence bound,
not an invented training cutoff or first-global-publication guarantee.
Added batched, resumable CPU history/test/claim embedding preparation, complete
matrix export, empty source-bound claim requests and supplied-claim validation,
bounded-memory four-measure novelty scoring and strict authorization/eligibility
checks. Optimized chronological ridge to reuse fold calculations across alphas;
kept raw original-abstract features, historical-only targets and paired bootstrap
reporting. Actual plan status: zero embeddings and zero supplied claim sets;
execution flags remain false. No inference, model loading or actual human-check
evaluation occurred. Prior scheduling denial and unknown E6 resource headroom
remain constraints. 87 offline tests passed; current source/scoring artifacts,
E6 and Ollama preserved. No push. See E2/TASK3_EXECUTION.md.

## 2026-11-16 — Main Problem assistance and supplements

- Codex helped implement and document the Main Problem representation, gates,
  and evidence audit; scope is in `M/AI_USAGE.md`. A real implementation error
  caught was assigning a future paper an arrival time before publication. A
  separate leakage issue left unavailable answers in the representation after
  hiding them from the groundedness readout. Both were corrected and checked
  with synthetic tests, which validate software only.
- Supplementary A1 claim extraction used local `qwen3:8b`
  (`sha256:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`);
  reviewer `AS-01` reviewed two focal-paper claim/source sets. A1 is an exposed
  two-cluster supplement, not original A1. Exploratory S1 used exposed E1
  contrasts and unverified creator-intended labels; its joint criterion failure
  is not original S1 evidence.
- Grounding V1's first Qwen3 call returned an empty answer after thinking used
  the 512-token budget; it was preserved and not retried. Separately registered
  V2 set `think=false` and generated four questions. Exploratory reviewer 2
  disclosed AI assistance and non-independence; reviewer 1's independence is
  unverified. No V2 scoring or grounding conclusion exists. See `M/FINAL_REPORT.md`.
- Codex made documentation-only edits to this log, `NOTEBOOK.md`, and
  `M/FINAL_REPORT.md`; no inference, scoring, training, protocol, result, or
  dataset was changed.

## 2026-11-16 — T1 theory answer

- Codex read T1 on official PDF pages 8–11 and checked the relation and
  near-miss definitions on pages 4–5. It drafted the derivations, examples,
  controls, geometry proposal, and answer-sheet entries in `theory/T1.md`.
- Threshold-vector dot products, box volumes/intersection, and answer-set
  inclusion were checked against the PDF. The length-shortcut argument
  distinguishes a mean association from pairwise ordering. No experiments,
  model runs, or empirical results were added.


## 2026-11-16 — Theory T1–T5 completion

- Codex checked the official assignment’s theory questions and answer-sheet fields (T1–T5, PDF pp. 8–25) against `theory/T1.md`–`theory/T5.md`, independently recalculated the displayed numeric results, and edited theory explanations and consolidated answer sheets. T3’s two-generator leaderboard and T2–T4 answer-sheet coverage were added; proposed checks remain explicitly designs, not empirical findings.
- Arithmetic checks included T2 reliability/partial correlation, T3 Bayes/power/interval, T4 attenuation angle, and T5 entropy/mutual information. No Main Problem protocols, data, results, inference, training, or experiments were touched.

## 2026-11-16 — E1 saved-evidence completion analysis

- Codex read official E1 requirements (PDF pp. 28–29), the frozen E1 protocol,
  item validators, saved model outputs, source-date inventory, and review notes.
  It added a read-only standard-library analysis script and supplemental report
  using existing outputs only. The script recomputes overall/per-type metrics
  and 95% source-paper-cluster bootstrap intervals (5,000 resamples), plus
  deduplication intervals that keep each query's four variants together.
- The saved MS MARCO cross-encoder was identified as a generic passage-relevance
  scorer, not the assignment's instructed identity judge. No inference or model
  training was run; no held-out test file was opened; no existing outputs,
  frozen data, or preregistration were changed. Task 3 is described as
  retrospective because the numeric predictions cannot be verified as
  pre-evaluation under the conservative frozen chronology.

## 2026-11-16 — E1 source alignment review and protocol check

- Codex inspected official E1 pages 28–29, the frozen E1 model/configuration
  entries, evaluator, and saved source metadata. It performed a new retrospective
  AI-assisted comparison of each of the 61 A questions with its locally saved
  arXiv abstract and recorded item-level evidence locators and review dates in
  `E1/source_question_review_2026-11-16.csv`. This verifies semantic support from
  the saved abstract only; exact author-question provenance, the fixed prompt,
  manual-edit history, independent human review, and historical 24-hour rereads
  are not claimed.
- The only frozen cross-encoder is explicitly a generic MS MARCO passage-
  relevance scorer, whereas the assignment requires an instructed same-question
  judge. No compliant alternative model/prompt configuration is recorded, so no
  new model inference was run. Existing model outputs and frozen files were
  preserved; no held-out file was opened.

## 2026-11-16 — E2 saved-evidence completion report

- Codex read the official E2 instructions and consolidated existing saved
  Task 1/2 reports, cache-only extension summaries, Task 3 provenance evidence,
  and the Task 4 interpretation into `E2/COMPLETION_REPORT.md`. It added a
  current-status pointer to the E2 README while retaining earlier reports.
- Codex created a blank 299-row first-publication source-review form from
  existing forum IDs, titles, abstract hashes, and observed OpenReview dates.
  Reviewer fields, first-publication dates, eligibility decisions, novelty
  judgments, and results remain blank. This form is for retrospective source
  provenance review, not independent human labeling.
- Existing protected score-file hashes were checked against the saved report.
  No scoring, inference, training, experiment, or test suite was run; protected
  results and frozen datasets were not modified.

## 2026-11-16 — E5 task completion review

- Codex read the official E5 pages 36–37 and reviewed the frozen E5
  preregistration, diversity API, controlled dataset, saved baseline outputs,
  cluster-bootstrap code, and Semantic Scholar candidate verification.
  It added an explicit Task 1 and Task 3 accounting to `E5/RESULTS.md`,
  distinguishing implemented lexical/rule baselines from missing semantic
  evidence and documenting why the OpenAlex candidates do not meet the frozen
  Semantic Scholar requirement.
- Codex executed the existing read-only saved-results consistency command
  logic: 200 per-set rows, Task 2/4 interval summaries, controls, and frozen
  input hashes matched. No scorer, inference, training, or experiment was run;
  existing results, datasets, and preregistration were not changed.


## 2026-11-16 — E6 finalization from locked saved outputs

- Codex read official E6 Tasks 1–4 (PDF pp. 38–40), the E6 preregistration,
  protocol, seven-arm implementation, saved development artifacts, and the
  completed held-out accuracy report. It found the raw held-out result files
  were absent from the submission copy but present in the original repository.
  It copied the 19 saved per-set evaluation JSON files and five run-provenance
  files byte-for-byte into a new submission path and recorded SHA-256 hashes;
  the original run, request cache, execution lock, generations, and labels were
  not modified.
- Codex created a read-only summary reproducer, updated the one-page E6 memo,
  and documented the preregistration, coverage, control, error-analysis, and
  missing-literature limitations. It checked one saved TRAIN example: a D-arm
  directional claim said third-party-debate frustration was more frequent
  among Republican-labelled users, while the four matching source examples
  split two per label. This is AI-assisted review, not a human judgment.
- The saved accuracy summary and all paired intervals were recomputed from the
  copied records; hashes, 501-row alignment, and per-cell counts matched. No
  held-out run, generation, inference, training, or human review was performed.

## 2026-11-16 — E6 frozen-sample error evidence inventory

- Codex joined all 20 frozen Task 3 sample IDs to the saved source packets,
  generation rows, and existing per-set held-out evaluation JSONs, then wrote
  `E6/TASK3_ERROR_ANALYSIS.md` and updated the Task 3 section of
  `E6/COMPLETION_REPORT.md`. It distinguished saved-output/schema inspection
  from independent human review, which remains 0/20, and did not change the
  sample, protocols, generations, labels, or results. No inference, generation,
  scoring, or human judgments were performed.
