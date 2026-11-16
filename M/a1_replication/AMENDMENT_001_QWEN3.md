# Prospective amendment 001 — claim extractor model substitution

**Date:** 2026-11-14 UTC  
**Base registration commit:** `281595fac1280a855cd67d71cf7f357e0a440d0e`  
**Cohort manifest SHA-256:** `2577e78a37f951785c577a0a045cc69a264d575ea1c82dc20f310c2fa2bd7702`

This amendment applies only to the supplementary A1 replication in this
directory. It does not alter the original frozen A1 registration or cohort.
No claim extraction had occurred before this amendment.

## Change and reason

The base registration named `deepseek-r1:8b` and required its local digest to
be recorded before extraction. That model is unavailable in the local Ollama
service. The locally installed `qwen3:8b` model is substituted prospectively
before any extraction. This changes the claim-generation model and is disclosed
as a design deviation; outputs must not be described as produced by DeepSeek.

## Locked extractor

* Ollama tag: `qwen3:8b`
* Ollama model identifier shown locally: `500a1f067a9f`
* Full referenced manifest layer digest:
  `sha256:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
* Model-weight layer digest:
  `sha256:a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f`
* Config digest: `sha256:05a61d37b08453e59290add468e3bb2f688e23a01e967fecb0e2fa41218cea76`
* Local Ollama manifest SHA-256:
  `b3d9ba7c899cfd112df2574c6a91458a70b724c5e4e50dfffd75574b2d1648e7`

Use `E2/extract_claims_v8.py` unchanged (source SHA-256
`032835cc770217ae6024c5e6784275675ce80421cfd18f35c1f13ebb48b778ba`). At
runtime, override only the imported module's `MODEL` value to
`qwen3:8b`. Preserve the complete v8 prompt, JSON response format, `think=false`,
`stream=false`, `temperature=0`, `num_predict=2800`, and existing one-retry
validation behavior. No prompt or validation edits are permitted.

Process exactly the 50 IDs in the committed cohort manifest. Do not replace
failures or alter cohort membership. Store raw responses, parsed accepted and
rejected claims, exact submitted prompts and their hashes, per-record UTC
timestamps, failures and claim counts under this directory. This amendment
authorizes claim extraction only; it does not authorize manipulation
construction, novelty scoring, or evaluation.

## Pre-extraction validation

Before the first model request, verify this amendment is committed, the current
cohort manifest hash equals the value above, and the local Ollama manifest and
model-weight digest match the recorded values. If any check fails, stop without
inference. Record the committed amendment hash in every output manifest.
