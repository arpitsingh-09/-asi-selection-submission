# Minimum compliant route to held-out TEST prediction

This timing interpretation uses the frozen approvals; it changes no model,
prompt, threshold, sample, outcome, failure rule, or analysis setting.

| Requirement | Assignment / frozen requirement | Actual deadline |
|---|---|---|
| Literature extraction hand check | Assignment: 20 targets. Decision 24 retains two independent reviewers and seven checks for each of those 20. | Before literature scoring; not before independent HypoBench prediction. |
| 40 review records / 280 Boolean checks | Mandatory under Decision 24, although the assignment alone does not prescribe this count. Two people may review all 20 cases independently; 40 different people are not required. | Before accepting/using literature reference annotations for scoring. |
| Third adjudicator | Required only for actual disagreement; distinct from that case's reviewers, with source-bound rationale. | Resolve affected reviews before literature scoring; never fabricate agreement. |
| Problem/method/result | Decision 24 requires genuine source checks in addition to the four model extraction fields. | Before literature scoring. The sidecar format is an implementation mechanism, not 60 additional independent reviewer appointments. |
| Four semantic evaluator validations | Configured evaluators check validation before their scoring callbacks (reconstruction, already-asked, diversity, question type). | Before using each affected evaluator. They are not invoked by the held-out prediction policy. |
| Ten independent pilot labels | An internal pilot design, not an assignment/frozen ten-label quota or an approved acceptance threshold. | A prepared route to validation evidence, not permission to mark unperformed validation complete. Actual independent evidence/adequacy assessment still required. |
| Grounded HDR definition and judgments | PREREG explicitly requires these before any HDR value; planted recovery is a different measure. | Before computing/reporting HDR; no frozen condition makes them a prerequisite for independent accuracy predictions. |
| 20-set end-to-end error analysis | Assignment Task 3 / Decision 25; fixed sample already selected prospectively, 10 per testbed. | After outputs are available; retain all seven arms, real examples, failed/missing cells and 0007. Do not reselect after outcomes. |
| Bootstrap summaries and one-page memo | Assignment Tasks 2/4 and Decision 26; fixed 10,000 input-set resamples and descriptive intervals. | After genuine evaluations, before final submission. Dependencies frozen before analysis. |
| Global scientific/source/model/runtime/Git gates | Frozen protocol and final-mode entry points. | Before every real phase's callbacks, including TEST prediction. |

Primary evidence:
- `E6/assignment_e6_excerpt_v1.txt`: literature hand check and Tasks 2–4.
- `E6/RESEARCHER_APPROVAL.json`: Decisions 19–22, 24–26; Decision 24
  `must_complete_before = literature_scoring`, two reviewers/seven fields.
- `E6/PREREG.md`: source reviews before literature scoring; source-grounded HDR
  before computation; finalization supersedes historical draft status text.
- `E6/configured_evaluators.py`: `_require_execution` checks validation at the
  affected scoring entry point.
- `E6/inductive_execution.py`: `evaluate_train_envelope` authorizes prediction
  before invoking the predictor, then records unavailable HDR without fabricating
  scores. This existing frozen function already separates these requirements.

## Justified implementation correction

The full all-metric launcher previously promoted metric-specific requirements
into global prerequisites for every TEST call. Added explicit
`--phase heldout_accuracy`; default `full` keeps all existing checks. Only unused
literature/semantic/HDR scoring gates are deferred. They are reported as deferred,
never passed or completed. The mode cannot call literature generation/scoring,
recovery, diversity, question-type, historical-question, HDR model judgments or
TRAIN regeneration. It uses unchanged TRAIN hypotheses, the frozen single-row
prediction prompt/settings, all 501 observations per evaluable cell, and the
existing invalid-prediction denominator and checkpointing.

Saved failures and unresolved 0007 remain missing; no replacement. The phase
has 125 evaluable arm cells, so a full new run entails 62,625 prediction requests.
No such request was executed during preparation. Recorded readiness is
`E6/data/heldout_accuracy_readiness_v1.json`: scientific/source/runtime-evidence/
preregistration gates PASS, no phase-specific blockers, full evaluation still
not ready. Live model/backend identity is rechecked without generation at launch.
The code-commit guard remains mandatory. Eleven focused non-inference tests pass.

## Ordered minimum remaining actions

1. Freeze the corrected launcher/readiness implementation in a local commit;
   preserve original preregistration/configuration and every existing history.
2. Once explicitly instructed to start TEST, run only the held-out accuracy phase
   below. The current task expressly forbids executing it now.
3. In parallel or after accuracy prediction, complete the actual source reviews
   and evaluator validation before their respective scorers; obtain grounded HDR
   inputs before HDR calculation. Keep prompts/methods fixed and do not tune them
   using TEST outcomes. Record unavailable results honestly.
4. Finish the 20-set error analysis, fixed bootstrap summaries and memo after
   the necessary outcomes exist. A successful accuracy phase is not completion
   of full E6.

After the local implementation commit, the exact separate Terminal command is:

```sh
cd /Users/arpit/asi-selection
python3 E6/run_confirmatory_test.py --phase heldout_accuracy --output-dir E6/runs/heldout_accuracy_v1
```

Do not run the default full launcher blindly afterwards: its prediction stage
must reuse these source/policy-bound batch checkpoints. The existing native
`evaluate_train_envelope` supports that reuse when adding genuine HDR inputs;
never reissue previously attempted prediction calls. The exclusive launch marker
continues to block automatic restarts of an interrupted invocation.
