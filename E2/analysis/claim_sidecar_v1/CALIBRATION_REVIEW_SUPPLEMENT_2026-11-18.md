# E2 calibration review supplement — human review required

**Prepared:** 2026-11-18  
**Status:** Evidence summary only. No human acceptance or gate clearance is recorded.

## Existing output and path-reuse error

- Earlier sandbox attempt: `calibration_only_2026-11-18_user_approval_1441Z/` contains only an empty `stdout.log` and `stderr.log` ending at `PermissionError` on `os.nice(15)`. That attempt stopped before model loading.
- Existing completed run: `calibration_only_2026-11-18_terminal_retry/`. It contains `stdout.log`, `stderr.log`, and `calibration_report.json`. Preserve these files. The `ValueError: refusing to reuse an existing calibration output path` is expected when the completed output directory is passed again.
- Report SHA-256: `dbc20c4bc2dfaba335c1d254eda9f77fa2d6d11c095cb57300ceea9ef31df013`.

## Recorded run results

- Run ID: `73cf33f6-f0cc-4411-9cb9-f1e378283c91`; start `2026-11-18T14:43:21.981377+00:00`; exit status `0`.
- Frozen manifest SHA-256: `a33e042bc0defaa72f658e421dc3e2ad8f0ad3fbcdf4c04b250604353d50998f`; driver SHA-256: `e5e3aeaf53a9505be05eb0fec8b305a0eba54c7c684c3e4f4c1383158ae564a0`; amendment SHA-256: `8f182b046351ca57aa8bc34a0bd79878432e10f7018a8a5f6738ef30cc399cd3`.
- Authorization SHA-256: `f61310a7531aae44575140bef4f1e07f87e6eb82aadc6a1c991aa0b54ce9f187`. At run start, its manifest/amendment/driver bindings matched. The recorded E6/resource checks were `2026-11-18T14:40:03+00:00`; this was about 3m19s before the run start, within the driver’s ten-minute limit.
- Model: base `3447645e1def9117997203454fa4495937bfbd83` plus proximity adapter `2081559630a80fc5851d8f798a05ba81e9468089`; CPU float32, CLS 768, L2-normalized.
- Four request hashes were recomputed transiently (`new_vectors_generated=4`, `persisted_vectors=0`). All four recomputed vectors exactly matched their saved vectors (max absolute difference 0 for each).
- All three parity controls passed at the frozen tolerances. Max absolute differences: `[0.0, 1.1920928955078125e-07, 0.0]`.
- Elapsed time: `2.221014584` seconds. Process peak RSS: `775028736` bytes.
- Sidecar SHA-256 before/after: `161f6dde297a53ff8cd688eddd01f12a35e9982ff0add77c4624d93e47e382e0` / `161f6dde297a53ff8cd688eddd01f12a35e9982ff0add77c4624d93e47e382e0`; row count remained `4`. Original-cache before/after hashes match: `True`.

## Unresolved adapter warning

The captured `stdout.log` contains:

> There are adapters available but none are activated for the forward pass.

In the installed `adapters` package, `adapters/model_mixin.py` logs this warning in `forward_context` when `active_adapters` is empty while adapters are present (lines 1417–1422). The frozen encoder calls `model.load_adapter(..., set_active=True)` and `model.set_active_adapters('proximity')` (`E2/task3_execution.py`, lines 113–114). The saved run record does not identify which forward call emitted the warning or prove that the proximity adapter was active for all seven control/claim forward calls. Matching parity and saved claim vectors is strong reproducibility evidence, but this warning leaves adapter activation unresolved. No inference was repeated to investigate it.

Human reviewer: inspect the warning and decide whether the run can be accepted under the approved amendment. If adapter activation cannot be established from existing evidence, leave the calibration gate blocked; resolving it would require a separately approved, uniquely pathed diagnostic/calibration run.

## Review decision — intentionally blank

- Accept/reject: ____________________
- Reviewer/source: ____________________
- Date: ____________________
- Adapter-warning disposition and evidence: ____________________
- Confirm four claims, three parity controls, timing/RSS, and unchanged cache: ____________________

The report itself has `human_accepted: False`. This supplement does not change authorization, vectors, scores, or the calibration report.
