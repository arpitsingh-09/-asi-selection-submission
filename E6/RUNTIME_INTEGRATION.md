# Essential runtime and TRAIN integration — current result

**Live runtime: NOT VERIFIED at the new settings.** The environment denies
`127.0.0.1:11434` with `Operation not permitted`, including the read-only version
request. No new model inference or actual prompt-token count was obtained.
The genuine failed attempt is `data/development_runtime_probe_v1/report_01.json`.
The original Gemma verification remains preserved; it does not certify 32768/2048.
Mock test results are never registered as real runtime evidence.

Run in a normal Mac terminal with Ollama already running:

```sh
cd ~/asi-selection
python3 E6/development_runtime_probe.py --output-dir E6/data/development_runtime_probe_v1
```

This accepts only the existing DEVELOPMENT manifest, verifies original source
rows/model digest/tokenizer identity, and uses one development abstract. It makes
two bounded token-count calls (normal prompt and controlled long padding), then
one 2048-token pressure call; API identity/allocation checks are read-only.
No seven-arm experiment, held-out prediction or HDR judgment is run. It preserves
step checkpoints and versioned attempt reports; a resume rechecks live identity
and rejects changed source/settings/code. It reports inconclusive rather than
claiming support when the actual count, allocation or length-pressure test fails.

The output/context software guard is exercised using the measured prompt count
without a further model call. Generation/counting use the SAME 32768 context,
avoiding an extra unverified 131072 allocation. 131072 remains metadata. Actual
per-call output is capped; context overflow blocks rather than silently shrinking
scientific limits. The 8192 generated-token proposal is unchanged and still null
in active config. Successful evidence must be registered by path/file hash; the
final gate binds it to source, model/tokenizer/backend, actual counts and frozen
context/output settings. A passed probe certifies only this runtime check, not
completion of all arms or every input. Registration never approves methodology.

TRAIN integration implemented:

- `prepare_train_execution_context`: validate original source files, exact cohorts,
  common generic task, and deterministic no-self/no-reuse donor mapping.
- `run_train_generation` / orchestrator: all seven arms, TRAIN controls, exact
  generated-token accounting, runtime/source/config/researcher/Git gates.
- `execute_train_input_set`: gated generation → prediction → HDR → mandatory JSONL,
  with cohort generation and per-batch prediction checkpoints.
- `evaluate_train_envelope`: reuse unchanged hypotheses across all TEST rows;
  source-bound accuracy, actual HDR inputs, JSONL and failed-cell ledgers.
- Prediction `predict_many`: bounded parallel independent requests where the client
  supports them, serial fallback otherwise. Identical single-observation prompts,
  seeds, caps, result order and invalid-prediction handling; no combined-example
  prompting and no claim that the local server actually accelerates requests.
- Checkpoints bind source/context/envelope/policy; changed inputs are rejected.
  New HDR inputs can reuse prediction checkpoints and preserve prior summaries.
  Missing HDR data stays blocked and overall required-metric status stays incomplete.

The real-source TRAIN execution plan v2 is saved. No real envelope, held-out
prediction, HDR score or scientific generation was produced. All approval fields
remain pending; config remains DRAFT, limits unset and datasets unfrozen.

Tests: 321 E6 tests and 10 validator self-tests pass, using toy data/mock clients
for execution. Real pending gates invoke no model/predictor. Precommit validation
correctly remains blocked (including missing runtime evidence).

Remaining blockers: obtain actual local runtime evidence; approve/freeze the ten
method groups and relevant source/code artifacts; provide genuine HDR feature
mapping/judgments and prior-question sources; complete target extraction/reviews
before scoring. Same-dataset TRAIN donor swaps preserve the global mechanism:
they are implemented as specified but do not establish a negative mismatched-task
control without an approved interpretation or changed donor policy. Literature
final execution and final statistical-analysis scheduling are still outside the
integrated TRAIN path and remain gated/unimplemented. No approval is inferred.

Final integration also validates explicit frozen numeric generation seed and
arm-output scheduling (`fixed_configured_arm_order_v1` or
`sha256_seeded_arm_order_v1`, with shared preparation first). Unresolved or
unsupported schedules block before callbacks; checkpoints cannot change cap,
model/decoding, source, donor policy or run order silently. Seed remains null in
active config, not approved. Generation checkpoints are hash-sealed, and HDR
updates create new summaries while reusing predictions. Required-metric completion
is scoped to TRAIN accuracy/HDR, not all E6 outcomes.
