# Frozen literature experiment: future execution

No literature generation or evaluation was executed during implementation.
The existing `literature_execution.py` / `orchestrator.run_seven_arms` already
implement all seven arms, six hypotheses, frozen seed/model/token cap, common
reference evidence, empty controls and deterministic shuffled donors. The new
`run_literature_experiment.py` adds a separate cohort launcher and durable call
journal; it never reads or launches held-out TEST.

## Remaining stages

- Generation: 100 selected targets × seven arms = 700 planned cells; not executed.
  Generation uses the frozen ten-reference bundles only. Saved target extractions
  and source hashes bind the cohort but never enter generation prompts.
- Reconstruction: best question/hypothesis similarity and same-question judgments
  through `ConfiguredEvaluators.score_literature`; not executed.
- Secondary evaluation: diversity, question type and historical already-asked rate
  through existing configured evaluators; not executed. Questionless arms retain
  an explicit not-applicable record. Failed generation arms stay missing.
- Paired uncertainty summaries, 20-case end-to-end review and memo conclusions
  require actual completed outputs and actual human judgments.

Generation requires existing protocol/config/runtime/Git gates. It does not need
semantic target labels, because target annotations are excluded from its inputs.
Evaluation separately requires real evaluator validations, the configured actual
review bundle, independent source reviews/adjudications and attributed component
sidecars. Current blank reviews and pending validation statuses cannot pass.
No gate, frozen setting or prompt was changed to make evaluation pass.

## Exact future generation command

Only after the current held-out TEST workload has finished:

```sh
cd /Users/arpit/asi-selection
python3 E6/run_literature_experiment.py \
  --phase generation --execute \
  --output-dir E6/runs/literature_seven_arm_v1
```

Without `--execute`, the same entry point only prepares/verifies a plan. The
reviewable offline plan is `data/literature_seven_arm_plan_v2/experiment_plan.json`.
The future run directory is separate and was not created by preparation.

Each input set retains its original generation envelope and assignment JSONL,
including explicit failure exports. Calls, including token-count preflights,
are journaled before dispatch with frozen request/plan identities. Completed raw
replies are replayed locally; failed requests replay their recorded failure.
A started request with no terminal record blocks before orchestration and must
never be automatically reissued. Changed call sequence or corrupted evidence
aborts outside normal arm-failure handling. A cohort lock prevents two launchers
from writing the same run. Successful checkpoints are verified and reused.
Resume by the identical command and output directory only when no ambiguous
started call exists; resume is not permission to retry failed or ambiguous calls.

After genuine scoring prerequisites have been completed and bound through the
existing approved configuration process, evaluation uses:

```sh
python3 E6/run_literature_experiment.py \
  --phase evaluation --execute \
  --components E6/data/literature_components_actual.json \
  --output-dir E6/runs/literature_seven_arm_v1
```

The component filename is a required future actual artifact, not a prepared
annotation. Evaluation requires all generation checkpoints and reuses them.
Its outputs are `reconstruction.json` and `<arm>_secondary.json` per input set,
compatible with the completed-artifact index in `error_analysis_memo.py`.
Review/component file hashes bind evaluation journals. Source/settings or plan
changes fail closed and need explicit reconciliation; do not discard old journals
or choose a fresh directory to bypass an attempted-call block. No model identity
or inference requests were made by the offline preparation/tests.
