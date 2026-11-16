# A1 supplementary scoring readiness — 2026-11-14

Deterministic manipulation generation was run for the two authorized papers.
No model inference, novelty scoring, or bootstrap analysis was run.

| Mandatory gate | Status | Evidence |
|---|---|---|
| Extractor identity and digest | PASS | `claim_extraction_qwen3_v1_manifest.json` records Qwen3 `ollama_id` `sha256:500a1f...b41`, model-layer digest `sha256:a3de86...686f`, and config digest `sha256:05a61d...ea76`. The local Ollama manifest and both blobs match those digests. The extraction-code, source-corpus, output, and cohort SHA-256 values match the recorded values. |
| Human claim/source review | PASS | For both reviewed IDs, the displayed complete abstract matches the original source record; all 18 claim and evidence strings match the extraction output, and each evidence excerpt is an exact substring of the original abstract. All decisions and rationales are present. Retained supported-atomic counts are 9 and 7, respectively, within the registered 4–10 range. |
| Reviewer identity/date | PASS | The review form records reviewer `AS-01` and date `2026-11-14`. |
| Durable independence attestation | PASS | [A1_REVIEWER_INDEPENDENCE_ADDENDUM.md](./A1_REVIEWER_INDEPENDENCE_ADDENDUM.md) records the reviewer’s previously confirmed declaration that they did not produce or contribute to either extraction. It identifies both paper IDs and links the original review form. |
| Frozen cohort integrity | PASS | The cohort file hash matches both the extraction manifest and validation report; the committed cohort remains unchanged. |
| Supplementary registration versioning | PASS | Registration commit `281595fac1280a855cd67d71cf7f357e0a440d0e` contains the registration and cohort. The registration text still says scoring is not authorized. |
| Amendment 003 versioning | PASS | Approved Amendment 003 is committed separately as `c73df33a663ce9e648b12524703fd2f255b8097d`. The extraction manifest's `c7be68...` reference is the earlier Qwen3 extraction amendment, not Amendment 003. |
| Amended control implementation | PASS | Updated `controls.py` implements original and temporally eligible shuffled controls, undefined empty-pool scores, and a non-scorable unavailable decoy. All 6 focused tests pass; implementation and tests are included in the local authorization-evidence commit. |
| Focal source/version and temporal pools | PASS | Both focal IDs resolve to versioned source records with matching focal publication timestamps and abstract hashes. The generated inputs contain 716 and 896 strictly prior original-pool IDs; shuffled controls draw from the other authorized focal’s original pool, re-filtered at the current focal cutoff, yielding 715 and 716 IDs. Each shuffled set differs from its paired original set. |
| Prior-scoring exclusion | PASS | Both focal IDs are in the frozen 50-paper cohort and absent from its previous-scored focal IDs, the E2 manipulation plan, and E2 scoring results. |
| Minimum independent clusters | PASS | The two authorized focal papers meet the preregistered minimum of two independent focal clusters; estimates remain severely small-sample-limited. |
| Manipulation readiness | PASS | [A1_AUTHORIZED_MANIPULATIONS_V1.json](./A1_AUTHORIZED_MANIPULATIONS_V1.json) contains 14 deterministic baseline/coverage/concentration cases and 26 synthetic items built only from AS-01-retained claims. The validation report confirms exact source spans, claim order, stable identities, original and cross-focal shuffled-pool temporal filtering, undefined empty scores, and unavailable decoys. Five focused generator tests pass. |
| Scoring authorization | PASS | [A1_SCORING_AUTHORIZATION_2026-11-14.md](./A1_SCORING_AUTHORIZATION_2026-11-14.md) records the responsible researcher’s explicit authorization, limited to `2512.23709v3` and `2610.29385v1`, under Amendment 003. This does not amend the registration or authorize the original A1 evaluation. |
| Scoring input integration | PASS | [scoring_adapter.py](./scoring_adapter.py) verifies the manipulation SHA-256 against its validation manifest, revalidates the 14 cases and all 26 synthetic records, and installs them only in a copied in-memory E2 paper map. It preserves source/control identities, rejects future or focal leakage, and never submits empty or unavailable-decoy targets. [A1_SCORING_INPUT_MANIFEST_V1.json](./A1_SCORING_INPUT_MANIFEST_V1.json) records 14 manipulation cases plus two shuffled diagnostic targets. Focused adapter tests pass. |

## Unresolved requirements and next action

1. Run the authorized, nonempty scoring targets through `scoring_adapter.score_target`
   and save real outputs. Keep the two empty diagnostics undefined and omit the
   unavailable decoys; then perform the registered paired bootstrap analysis.
