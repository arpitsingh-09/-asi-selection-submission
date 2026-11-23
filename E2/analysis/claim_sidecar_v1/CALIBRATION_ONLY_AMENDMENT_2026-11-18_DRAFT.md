# Prospective E2 claim-sidecar calibration-only amendment — DRAFT

**Date:** 2026-11-18  
**Status:** Approved for execution by user on 2026-11-18 (per conversation)  
**Scope:** Supplementary calibration measurement for the existing E2 claim-sidecar bundle only. This amendment does not authorize the remaining 89 vectors, scoring, or writes to any result store.

## 1. Reason and disclosure

The sidecar currently contains four of 93 claim vectors. Their exact request bindings, stored checksums, dimensions, and unit-L2 normalization were inspected. The persisted parity metadata records three passing controls with maximum absolute differences `0.0`, `1.1920928955078125e-07`, and `0.0`.

The original four-vector encoder run did **not** preserve `elapsed_seconds` or process peak RSS. Those measurements are unavailable and must not be attributed to that original run or reconstructed from current process/system state. This proposed procedure would measure a new, separately identified calibration-only run. Its timing and memory results describe only that supplementary run.

Frozen identity at drafting:

- Bundle manifest: `E2/analysis/claim_sidecar_v1/manifest.json`
- Manifest SHA-256: `a33e042bc0defaa72f658e421dc3e2ad8f0ad3fbcdf4c04b250604353d50998f`
- Model key: `85d28c921a5d7ab3bddaefbc4c10581ac90d3415b4c2df0990485d604fcdd1d2`
- Model: SPECTER2 base revision `3447645e1def9117997203454fa4495937bfbd83` plus proximity adapter revision `2081559630a80fc5851d8f798a05ba81e9468089`
- Representation: final CLS, float32, dimension 768, L2-normalized; CPU only; maximum sequence length 512; single-thread CPU/BLAS configuration; batch size no greater than 2.
- Frozen parity tolerances: `atol=1e-5`, `rtol=1e-4`.

These identities must be rechecked against the actual frozen manifest and its bound files immediately before any later execution. Any mismatch means stop.

## 2. Proposed calibration-only run

If, and only if, this amendment is separately approved before execution and a fresh run-specific inference authorization is supplied, run a new isolated process that:

1. Verifies the manifest SHA-256 and every frozen source/code/model asset hash without editing any of them.
2. Opens the existing sidecar read-only, records its SHA-256, row count, and the four existing row hashes/checksums, and verifies the count is exactly four.
3. Initializes the same pinned CPU model and adapter with the frozen inference implementation, dtype, normalization, tokenization, maximum length, and one-thread settings.
4. Encodes the same four exact claim request texts already present in the sidecar, identified by text hashes:
   - `0898df02c4eb78a67cb2b8b5d615e73fd94963f353ddd9ee6c15faac2d408fba`
   - `0b38c37f6df3cf3dda2732030afc6287aacfc927172385b388fe495206b02678`
   - `0c4bc6e27997c779d6eb5326880f9b50bc58ec604f46b45a38d0d0537829ed3f`
   - `0cca22c3fb951b60aaa223cbc73e3fc671ffd973924f29df283ddd41a3b9780c`
5. Rechecks all three frozen parity controls against the original novelty cache, reporting each control text SHA-256 and maximum absolute difference.
6. Compares each transient normalized output with its corresponding saved vector. It writes no vector payloads and performs no insert/update/delete against either SQLite database.
7. Records results only in a new, exclusive run directory. It then reopens the sidecar read-only and verifies that its SHA-256, four-row count, row text hashes, and checksums are unchanged.

This run recomputes four embeddings transiently for measurement and reproducibility checking. In its report, `new_vectors_generated: 4` means four output vectors were computed by this *supplementary run*; `persisted_vectors: 0` must make clear none were added or replaced in the sidecar. The report must not describe these as the measurements of the original run.

### Fresh output paths

Use a new, non-existing directory for each run, for example:

`E2/analysis/claim_sidecar_v1/calibration_only_2026-11-18_<unique-run-id>/`

Write only new files there, at minimum `calibration_report.json`, `stdout.log`, and `stderr.log`. Never reuse or overwrite an existing run directory. Do not write to `claim_vectors_v1.sqlite3`, the original novelty cache, scoring outputs, or the authorization JSON.

### Proposed measurement command (not execution-approved)

The calibration-only driver is implemented as a separate file, but has not been independently reviewed or executed. The following invocation must **not be run** until the driver is reviewed and this amendment and a fresh run-specific authorization are approved:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
.venv/bin/python -B E2/claim_sidecar_calibration_only.py run \
  --folder E2/analysis/claim_sidecar_v1 \
  --amendment E2/analysis/claim_sidecar_v1/CALIBRATION_ONLY_AMENDMENT_2026-11-18_DRAFT.md \
  --authorization E2/analysis/claim_sidecar_v1/calibration_authorization.json \
  --claim-count 4 --batch-size 2 --device cpu --dtype float32 \
  --output-dir E2/analysis/claim_sidecar_v1/calibration_only_2026-11-18_<unique-run-id>
```

The driver is a new separate file; it must not edit `claim_sidecar.py`, the manifest, source plans, saved results, or existing vectors. Its own SHA-256 and the amendment SHA-256 must be captured in the report. A reviewer must inspect that implementation before execution. It must fail closed on any missing hash, resource, E6, parity, read-only, or output-path precondition.

The driver requires a **separate** run-specific authorization JSON; the existing
general E2 inference authorization is not sufficient. The future authorization
must bind the exact manifest, approved amendment, and calibration-driver SHA-256
and set `scope` to `calibration_only`, `authorize_calibration_only` to `true`,
`amendment_approved` to `true`, `e6_inactive_verified` to `true`, and
`resource_headroom_verified` to `true`. It must include a nonempty
`authorization_source` and timezone-aware `e6_check_utc` and
`resource_check_utc` timestamps no more than ten minutes old when execution
starts. The authorization JSON must contain exactly those required fields and
no additional permission/scope fields. Any broader scope, missing binding,
stale check, or mismatch is a hard stop. Authorization is not created by this
amendment.

## 3. Measurement definitions

- **Elapsed time:** use `time.monotonic_ns()` in the calibration-only process. Start immediately before model initialization and stop after the three parity checks, four claim encodings, vector comparisons, and post-run read-only integrity checks. Store the difference in seconds as `elapsed_seconds`. Also record separate model-load, parity, and four-claim batch durations for diagnosis; do not substitute any of them for the total.
- **Peak RSS:** record `resource.getrusage(resource.RUSAGE_SELF).ru_maxrss` from that same process at completion. On macOS, record the returned value as bytes; include OS/platform and the unit conversion rule in the report. It is a process high-water mark, not a measurement of system-wide free memory.
- Record UTC start/end timestamps, Python/package versions, CPU/thread configuration, process ID, run ID, invocation, exit status, and wall-clock source. Do not infer or backdate these values.
- The report must include the run's `manifest_sha256`, amendment path and SHA-256, calibration-driver path and SHA-256, model revisions/key, request hashes, all three parity-control records, transient vector comparison results, `new_vectors_generated: 4`, `persisted_vectors: 0`, and before/after sidecar integrity fingerprints.

## 4. Preconditions and acceptance criteria

Before a later execution, all of these are required:

- A human has approved this amendment and the separate calibration-only driver. Approval is not implied by this draft.
- A new, explicit, run-specific authorization permits only the calibration-only measurement; E6 inactivity and resource headroom are reverified immediately before launch.
- The frozen manifest, source/code bindings, model and adapter assets, request text hashes, parity-control hashes, and existing four sidecar rows validate exactly. The output directory is fresh and outside all frozen/result paths.
- The three fixed parity controls each pass `numpy.allclose` with the frozen `atol=1e-5` and `rtol=1e-4`; report per-control maximum absolute differences. Any failed control is a hard stop.
- All four transient outputs have shape `(768,)`, finite float32 values, and unit L2 norm under the existing normalization check. Each normalized output agrees with its corresponding stored vector at `atol=1e-5`, `rtol=1e-4`. Any mismatch is a hard stop and is reported; no stored row is repaired or replaced.
- The report contains finite positive `elapsed_seconds` and positive `process_peak_rss_bytes`; all required hashes and measurements are present. Never supply guessed estimates.
- The sidecar and original cache are unchanged after the run; the sidecar still has exactly the same four rows and row checksums. `persisted_vectors` must equal zero.
- The report is independently reviewed after execution. Only after that review may a separate genuine review JSON be created and hash-bound to the report and manifest. This amendment itself does not record acceptance.

If any precondition or acceptance check fails, stop. Preserve the failure log in that run's fresh output directory, do not create an accepted report, do not touch existing results, and do not proceed to the remaining 89 vectors.

## 5. Relationship to the existing calibration gate

This amendment is prospective and does not turn missing original-run measurements into known facts. It can support the existing gate **only if** it is approved before execution, the supplementary run actually meets every criterion above, the report clearly identifies itself as supplementary, and a human reviewer accepts that evidence as satisfying the purpose of calibration. The four transient vectors count as `new_vectors_generated` for the supplementary run but are not persisted or represented as original-run outputs.

Until those conditions hold, the existing gate remains blocked. The existing authorization has null calibration-review path/hash; this draft does not change them. Even after a qualifying report exists, the separate human review JSON and its hash binding are still required by `claim_sidecar.py` before any continuation. The current code mechanically checks report fields but does not itself verify elapsed-time validity, parity tolerance, supplementary-run provenance, or that the sidecar was unchanged; the reviewer/driver must establish these facts from the report and logs.

## 6. Integrity and scope limits

- This document does not amend or replace the original preregistration. It is a proposed supplementary protocol only.
- No inference, report generation, authorization update, scoring, vector write, or Git operation is authorized or performed by this draft.
- The calibration-only driver is implemented separately, but it has not been independently reviewed or executed. Review its code before any later approval; it must preserve all frozen hashes.
- The manifest and authorization use absolute paths under `/Users/arpit/asi-selection`; execution must confirm those exact frozen inputs remain available and hash-identical. Do not silently redirect bindings to this submission copy.
- Repeated inference can still consume resources and may not be bitwise deterministic. The stated tolerance comparison and hard-stop policy address drift; they do not prove identical runtime behavior to the original run.
- A supplementary measurement establishes the supplementary run's resource profile only. It cannot retroactively establish the first run's elapsed time or peak RSS.
