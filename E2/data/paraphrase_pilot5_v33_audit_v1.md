# Paraphrase Pilot v33 — Data-Quality Audit

**Audit date:** 2026-10-27  
**Input:** `E2/data/paraphrase_pilot5_v33.jsonl`  
**Status:** Post hoc audit; not authorization for scoring.

## 1. Structural checks

The read-only audit reported:

- Records: 5
- Unique paper IDs: 5
- `manual_validation_status`: `accepted` for all 5 records
- `generation_status`: `accepted_manual_validation` for all 5 records
- `scoring_authorized`: `false` for all 5 records
- Required fields checked by the audit: no missing fields in any record

These checks establish basic structural consistency only. They do not independently establish semantic claim preservation or complete manual validation.

## 2. Evidence defect

**Affected paper:** `2012.14371v3`  
**Affected item:** source claim 9

The stored evidence ends prematurely at:

`...metric endowed with binom(Z*,`

The supplied source abstract contains the complete statement, ending with the Tensor Power Normalization metric being endowed with `binom(Z*,r)` detectors.

The candidate abstract retains the corresponding central claim: coupling EPN with an order-r tensor produces a metric with `binom(Z*,r)` detectors associated with r-dimensional subspaces, and detects whether at least one higher-order occurrence is projected into such a subspace.

The candidate wording appears consistent with the supplied source abstract on this point. However, the stored evidence field is incomplete and should not be treated as complete supporting evidence.

The audit's truncation heuristic did not flag this record because the evidence ends with a comma rather than one of the checked suffixes. Manual inspection identified the defect.

## 3. Interpretation and limitations

- This is a data-quality defect in the stored evidence for claim 9.
- The finding does not, by itself, establish that the candidate abstract is semantically incorrect.
- The five `accepted` statuses were observed in the JSONL, but this audit did not independently reconstruct or verify the full manual-review process.
- Existing review documentation should be reconciled before treating the pilot as fully validated.
- No records were edited or regenerated during this audit.

## 4. Handling decision

- Preserve `paraphrase_pilot5_v33.jsonl` unchanged.
- Keep all `scoring_authorized` values `false`.
- Do not run scoring or bulk generation based on this audit.
- Any future correction should be made in a new versioned file, with the complete source evidence verified against the source text and the review decision documented separately.

