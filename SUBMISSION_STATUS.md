# Submission status and remaining work

This index describes the evidence present in this package. It does not elevate
development baselines, blocked runs, or AI-assisted reviews into completed
official evaluations.

| Requested task | Current evidence | Remaining requirement / limitation |
|---|---|---|
| T1–T5 | Worked answer files and answer-sheet entries in `theory/` | Candidate review and correction of all answers before submission. |
| E1 | 61-item contrast set; mechanical validator passes; saved outputs for five embedding models; cluster-bootstrap report; `python3 E1/verify_e1.py` passes | Saved cross-encoder is a generic relevance scorer, not an instructed same-question judge; source/manual-edit provenance and historical 24-hour review are incomplete. See `E1/COMPLETION_REPORT.md`. |
| E2 | Three source-paper pools, focal-paper and claim records, saved time-filtered novelty scores, and analysis/report code | Some focal sets have too few claims; paraphrase/concentrated/near-far/temporal manipulations and required nearest-paper planting are incomplete; Task 3 AUROC/quality-baseline comparison is blocked by publication-date, cutoff, embedding, and claim evidence gaps. See `E2/COMPLETION_REPORT.md`. |
| E5 | 200 controlled five-question sets; 36 unit tests pass; saved lexical/rule-baseline scores and cluster intervals | Does not validate semantic measures; Task 3 has no protocol-eligible Semantic Scholar groups; semantic facet reliability is unmeasured. See `E5/FINAL_REPORT.md`. |
| E6 | Seven-arm implementation, prompts, partial saved HypoBench outputs and paired analysis, one-page memo | No literature-arm generations; substantial invalid outputs and missing cells; 0/20 independent human error reviews. See `E6/COMPLETION_REPORT.md` and `E6/TASK3_ERROR_ANALYSIS.md`. |
| Main Problem M | Shared-space design, code, baselines/contracts, provenance, supplementary analyses, and report | Original registered battery reports 0/9 complete; all nine core tests remain blocked. See `main/REPORT.md` and `M/FINAL_REPORT.md`. |

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
