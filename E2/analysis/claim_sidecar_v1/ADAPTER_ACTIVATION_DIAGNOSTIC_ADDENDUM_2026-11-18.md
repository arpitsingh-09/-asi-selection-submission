# Prospective E2 adapter-activation diagnostic addendum

**Date:** 2026-11-18  
**Status:** Approved for execution by user on 2026-11-18 for this diagnostic-only scope (per conversation)  
**Scope:** One read-only diagnostic run for the existing first four claim vectors and the three frozen parity controls. This addendum permits no remaining claim vectors, scoring, vector writes, database changes, or changes to the original preregistration.

## Purpose and warning disposition

The existing supplementary calibration report records an adapter-library warning: `There are adapters available but none are activated for the forward pass.` The installed `adapters` implementation emits this warning when its effective adapter setup is empty in `forward_context`. The existing log does not identify the affected forward call. Treat the warning as unresolved; do not accept the existing report as proof that the proximity adapter was active.

This addendum authorizes a separately identified diagnostic to record the effective adapter setup at each adapters forward-context entry. The diagnostic must fail before model computation whenever the effective active adapter set is not exactly `['proximity']`. It runs the same three parity controls and four existing claims only, with claim batch size one so each request has an individually attributable forward context. It uses the existing frozen CPU float32 encoder loader and model assets.

## Bound inputs and outputs

- Existing manifest and source/model bindings remain unchanged and must pass their frozen hashes.
- Exactly three frozen parity controls and the four already-saved requests are permitted.
- The existing sidecar and original cache are opened read-only, fingerprinted before and after, and must remain byte-identical.
- A fresh, unused `adapter_diagnostic_*` directory is required. Preserve all prior calibration and diagnostic outputs.
- The driver writes a supplementary calibration report plus `adapter_activation_diagnostic.json`, which lists each forward-context entry, associated request hash(es), effective active adapters, pass/fail, and the final count. No human acceptance field may be set true.
- The active-adapter state is recorded immediately before the frozen adapter library's forward-context logic. An empty or non-`proximity` setup is recorded and causes a hard stop before that forward computation.

## Execution requirements

Execution requires a new, run-specific authorization JSON with exactly these fields: `scope`, `authorize_adapter_diagnostic_only`, `amendment_approved`, `e6_inactive_verified`, `resource_headroom_verified`, `manifest_sha256`, `amendment_sha256`, `calibration_driver_sha256`, `diagnostic_driver_sha256`, `authorization_source`, `e6_check_utc`, and `resource_check_utc`. It must bind the current SHA-256 of the manifest, this addendum, the existing calibration driver, and the diagnostic driver. Both environmental checks must be genuine, timezone-aware UTC measurements no more than ten minutes old at launch. Authorization must not be copied from or written over either earlier authorization.

The diagnostic driver must pass its hash-bound checks before model loading; it then reuses the existing calibration worker's frozen identity checks, three parity controls at `atol=1e-5`, `rtol=1e-4`, four transient claim comparisons, elapsed-time and peak-RSS measurement, and read-only before/after integrity checks. Any failed activation, parity, vector comparison, hash, resource, E6, authorization, or output-path check stops the run. A failed run may preserve logs and partial diagnostic observations in its fresh directory but must not produce an accepted report or write vectors.

Proposed command after a fresh authorization is created through the documented procedure:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
.venv/bin/python -B E2/claim_sidecar_adapter_diagnostic.py \
  --folder E2/analysis/claim_sidecar_v1 \
  --amendment E2/analysis/claim_sidecar_v1/ADAPTER_ACTIVATION_DIAGNOSTIC_ADDENDUM_2026-11-18.md \
  --authorization E2/analysis/claim_sidecar_v1/adapter_diagnostic_authorization.json \
  --output-dir E2/analysis/claim_sidecar_v1/adapter_diagnostic_2026-11-18_<unique-run-id>
```

Do not run this command unless all hash bindings and fresh E6/resource checks pass.

## Interpretation and gate status

A complete diagnostic must record exactly seven forward contexts: one for each parity control and one for each of the four claim texts. Every record must report exactly `['proximity']`; all three parity checks and four saved-vector comparisons must pass; both databases must remain unchanged; elapsed time and peak RSS must be present and positive. Any missing record or any different active setup is a failure and identifies the affected request(s).

A successful diagnostic establishes the adapter state during this supplementary run only. It does not retroactively prove adapter activation in the earlier run, and it does not automatically satisfy the human-review requirement. The calibration gate stays blocked until the report is reviewed and a human records a truthful disposition through the existing review protocol. This addendum creates no acceptance record.

## Integrity limits

This addendum does not modify the original preregistration, frozen manifest, model/input hashes, existing vectors, databases, calibration report, or prior authorization JSON. It does not authorize `E2/run_scoring.py`, the remaining 89 vectors, or any GitHub operation. The diagnostic's user approval does not substitute for fresh environmental checks or the run-specific authorization described above.
