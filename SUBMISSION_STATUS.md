# Submission status and remaining work

This index describes the evidence present in this package. It does not elevate
development baselines, blocked runs, or AI-assisted reviews into completed
official evaluations.

| Requested task | Current evidence | Remaining requirement / limitation |
|---|---|---|
| T1–T5 | Worked answer files and answer-sheet entries in `theory/` | Candidate review and correction of all answers before submission. |
| E1 | 61-item contrast set; mechanical validator passes; saved outputs for five embedding models; cluster-bootstrap report; `python3 E1/verify_e1.py` passes | Saved cross-encoder is a generic relevance scorer, not an instructed same-question judge; source/manual-edit provenance and historical 24-hour review are incomplete. See `E1/COMPLETION_REPORT.md`. |
| E2 | Three source-paper pools and saved novelty scores; nearest-paper planting has now scored all 964 fixed conditions across 241 focals; a separate 52-paper N/yours extension has saved results using the 93 existing claim vectors. | E2 remains partial: several focal claim sets are short; paraphrase candidates lack independent review and scoring; the historical Task 3 cohort remains blocked by first-publication/version and model-cutoff evidence. Later results supplement the earlier task summary in `E2/COMPLETION_REPORT.md`; see `E2/REVIEW_AFTER_PLANTING.md`, `E2/analysis/nearest_planting_results_v1/REPORT.md`, and `E2/analysis/task2_n_custom_52_v1_eval_2026-11-18/REPORT.md`. |
| E5 | 200 controlled five-question sets; 36 unit tests pass; saved lexical/rule-baseline scores and cluster intervals | Does not validate semantic measures; Task 3 has no protocol-eligible Semantic Scholar groups; semantic facet reliability is unmeasured. See `E5/FINAL_REPORT.md`. |
| E6 | Seven-arm implementation, prompts, partial saved HypoBench outputs and paired analysis, one-page memo | No literature-arm generations; substantial invalid outputs and missing cells; 0/20 independent human error reviews. See `E6/COMPLETION_REPORT.md` and `E6/TASK3_ERROR_ANALYSIS.md`. |
| Main Problem M | Shared-space design, code, baselines/contracts, provenance, supplementary analyses, and report | Original registered battery remains 0/9 complete; all nine core tests remain blocked. The 2026-11-19 exact-version source recovery found one Cramming TRAIN review candidate but could not verify the historical abstract revision, and found no exact-linked VALIDATION review records; no labels were admitted. See `M/data/quality_recovery_2026-11-19/RECOVERY_AUDIT.md`, `main/REPORT.md`, and `M/FINAL_REPORT.md`. |

## Reproducibility checks during consolidation

- Original Git provenance: 138 commit objects and parent links verified.
- E1 mechanical data/integrity checks: 25 checks pass after updating the
  validator wrapper to invoke the active Python interpreter.
- E5 unit tests: 36 pass.
- Main Problem software tests: all 123 pass with
  `python3 tools/test_main_without_model_deps.py`. That runner provides
  import-only sentinels for unavailable PyTorch/Transformers/Adapters and
  raises if inference is attempted; it validates software logic only. Model
  inference and registered experiments remain unrun. An attempted lazy-import
  edit to the frozen E2 scorer was reverted because its registered hash check
  correctly rejected the changed file.

## Remaining execution blockers

- Pinned `torch==2.8.0`, `transformers==4.57.6`, and `adapters==1.3.0` could
  not be installed in an isolated Python 3.12 environment because PyPI
  resolution/network access is unavailable. The available Python 3.9 has no
  inference packages.
- Local Ollama model assets exist, including `gemma3:12b`, but starting the
  local inference service fails with `bind: operation not permitted`; the
  sandbox also blocks direct localhost connections. No generation was run.
- Direct Semantic Scholar API and paper pages are inaccessible from the
  available web tool. Existing E5 attempts therefore do not establish the
  required citation groups.
- Candidate/manual-review fields remain incomplete where the assignment
  requires the candidate's own 24-hour item review, source decisions, signed
  researcher approvals, or human-coded error review. They are not backfilled
  by AI.

## Scope history

The current requested set is T1–T5, E1, E2, E5, E6, and M. The original root
preregistration named E4 instead of E5. The dated scope amendment records this
as retrospective; E5 has a separate scoped preregistration for its controlled
baseline. See `PREREG.md` and
`PROVENANCE/experiment-selection-clarification-2026-11-16.md`.
