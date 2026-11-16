# E2 Paraphrase Pilot v33 — Provenance Reconciliation

**Audit date:** 2026-10-27  
**Current dataset:** `E2/data/paraphrase_pilot5_v33.jsonl`  
**Purpose:** Reconcile acceptance-status provenance and record remaining data-quality concerns.  
**Status:** Post hoc audit; not scoring authorization.

## 1. Acceptance decisions and supporting records

The following review records explicitly document acceptance decisions:

| Paper ID | Acceptance record | Documented decision |
|---|---|---|
| `2012.14359v1` | `paraphrase_pilot5_v33_review.md` | ACCEPT; recorded following the user's explicit instruction |
| `2012.14371v3` | `paraphrase_pilot5_v26_review.md` | ACCEPT; review documents claim-preservation criteria and a theorem check against Section D |
| `2012.13915v2` | `paraphrase_pilot5_v28_review.md` | ACCEPT; recorded following the user's explicit approval |
| `2012.14271v3` | `paraphrase_pilot5_v30_review.md` | ACCEPT; recorded following the user's explicit approval |
| `2012.14961v1` | `paraphrase_pilot5_v32_review.md` | ACCEPT; recorded following the user's explicit approval |

The v33 review states that Paper 1's title was revised and accepted, while the other records were unchanged from v32. The v32 review states that Paper 5 was accepted in v32 and the other records were unchanged from v31.

The earlier `paraphrase_pilot5_v23_manual_review_draft.md` documented a preliminary state in which all five records were pending full validation. Later versioned acceptance records document subsequent decisions. The earlier draft remains part of the chronology and has not been rewritten.

## 2. Current v33 status consistency

A read-only audit reported:

- Five records and five unique paper IDs.
- `manual_validation_status` is `accepted` for all five records.
- `generation_status` is `accepted_manual_validation` for all five records.
- `scoring_authorized` is `false` for all five records.
- No missing required fields among those checked by the structural audit.

These checks establish status and structural consistency. They do not independently reproduce the manual reviews or establish that every evidence field is complete.

## 3. Outstanding data-quality findings

### Finding A — Truncated evidence for Paper 2

**Paper ID:** `2012.14371v3`  
**Item:** source claim 9

The evidence field in v33 ends at `binom(Z*,`, truncating the source statement about the `binom(Z*,r)` detectors.

The supplied source abstract contains the complete statement, and the candidate abstract retains the central claim. The candidate therefore appears consistent with the supplied abstract on this point, but the stored evidence field is incomplete.

The acceptance record in v26 documents a theorem check against Section D. This provenance finding does not reverse that recorded decision; it identifies a defect in the current data record.

### Finding B — Missing generation timestamps

The v33 JSONL has no `generation_timestamp` field in any of the five records.

Earlier terminal output had shown a timestamp in a v33 record, so the provenance of that earlier output and the current file should not be assumed identical. The current file's missing timestamps are recorded here as a metadata limitation. This audit does not infer when the current records were generated.

## 4. Interpretation

- The five acceptance decisions have corresponding versioned review records.
- The v23 draft reflects an earlier stage and is not a final acceptance record.
- Paper 2's stored evidence field is incomplete despite the documented acceptance decision.
- The missing timestamps reduce the completeness of current generation metadata.
- No source data or candidate records were edited during this reconciliation.
- This reconciliation does not independently rerun the semantic review checklist.

## 5. Handling decision

1. Preserve `paraphrase_pilot5_v33.jsonl` and all earlier versions unchanged.
2. Preserve all review and validation records as historical artifacts.
3. If the evidence defect is corrected, create a new versioned data file and verify the full evidence against the source text.
4. Record any metadata repair in a separate versioned review note; do not invent timestamps.
5. Keep all `scoring_authorized` fields `false`.
6. Do not run scoring or bulk generation based on this audit.

**This note documents provenance and data quality only. It does not authorize scoring.**
