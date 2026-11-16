# Draft Amendment 002 — Same-topic decoy fallback

**Status: DRAFT FOR REVIEW — not approved, committed, or authorization to score.**
Prepared 2026-11-14. This amendment applies only to the supplementary A1
replication. It does not change `M/PREREG.md`, the frozen A1 cohort, or any
existing decoy proposal or Copilot review record.

## Reason

The registered deterministic category/hash rule selected one proposed decoy
per focal record. Independent human decisions are still absent, and the saved
Copilot suggestions are triage only. The protocol says to log a missing control
before scoring and forbids replacement based on model outcomes, but does not
specify a fallback after a candidate is rejected before scoring. A replacement
rule therefore needs approval before use.

## Proposed outcome-blind fallback

1. Retain each original proposal and its review record unchanged.
2. If an independent reviewer rejects a proposal as not same-topic, consider
   only distinct focal questions already in the selected 50-paper cohort,
   with the same primary pool category and a source timestamp no later than
   the target focal timestamp. Exclude all previously scored focal IDs.
3. Rank alternatives by ascending
   `SHA-256("49|focal_id|candidate_id")`. Consider them in that order; do not
   use model scores or evaluation outcomes in selection.
4. Require a real independent reviewer to affirm topical suitability and
   question distinctness, with reviewer identity/code, date, and evidence
   reference. Copilot suggestions and embedding similarity may prioritize
   human review but cannot satisfy this gate.
5. For the decoy condition, use the focal's original eligible pool with the
   decoy question's own source paper excluded. Verify that every remaining
   input paper was published strictly before the decoy source timestamp. If
   any other input is not earlier, the candidate is ineligible; do not silently
   truncate the registered pool.
6. If no candidate passes, mark the focal as a control failure and do not
   replace the focal paper.

This is a prospective rule change to the supplementary registration and
requires explicit approval and a separate local registration commit before
any fallback is accepted or any scoring begins. All other registered
conditions, frozen focal IDs, model settings, and analysis rules remain
unchanged.

## Current evidence status

The saved Copilot review found 36 proposed decoys unsuitable, 3 unclear, and 4
suggested as topical matches; all 43 require human confirmation. Those are not
independent judgments. A read-only check of the existing selected cohort found
one pair that passed the temporal check after excluding the decoy paper's own
exact-text self-match; its titles concern stress detection in social-media
text and fine-tuning language models on bioinformatics literature, so it is
not established as topically suitable. No replacement is currently verified
or eligible. The existing `controls.py` temporal gate also needs an approved,
tested adjustment to omit only the decoy question's own source paper from that
check; it must continue rejecting every other input dated at or after the
decoy timestamp.

**No inference, manipulation evaluation, or novelty scoring is authorized by
this draft.**
