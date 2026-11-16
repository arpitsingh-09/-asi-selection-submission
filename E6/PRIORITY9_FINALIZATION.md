# Priority 9 finalization — 2026-11-11

Status: prepared further; not finalized, frozen, committed, or authorized.
No confirmatory experiments or new development inference were executed.
No OpenAlex contact, commit, push, or changes to existing source/result data.

Completed in this pass:

- Inspected the E6 configuration, methods, gate, preparation interfaces and saved
  runtime/development evidence. Preserved unrelated working-tree changes.
- Reviewed all 26 recommendation groups. Preserved established values and
  approval-pending choices. Corrected stale deduplication and runtime statements.
- Prepared `data/fixed_token_cap_proposal_v1.json`: 8192 total tokens per
  input-set/arm, explicitly a cost-constrained proposal with unknown empirical
  completion rate; associated 2048 output / 8192 context limits also unapproved.
  No ten-record profile prerequisite, and no claim of measured adequacy.
- Added partial DEVELOPMENT profiling (`--limit`) and exclusive per-record
  checkpoints (`--checkpoint-dir`). No running process was started or stopped.
  Existing checkpoints reject a rerun before inference; no automatic resume.
- Strengthened sample verification to recompute deterministic selection and
  review policy, even when an altered artifact has a newly computed hash.
  Legacy proposals lacking exclusion hashes remain supported while current
  source/exclusion validation is enforced.
- Revalidated the original 100-paper proposal and prepared two approval CSVs:
  `data/literature_sample_approval_v1.csv` and
  `data/literature_manual_review_proposed_v1.csv`. Nothing is selected/frozen.
- Specified legitimate source requirements in
  `ALREADY_ASKED_SOURCE_REQUIREMENTS.md`. The zero-question source audit is
  preserved and no fabricated corpus was created.

Researcher approval:

Use `DECISION_SHEET.md` groups 1–22, 24 and methods in 26 to record actual
choices or replacements. Groups 9/16 now have a concrete cap/limit proposal.
The optional judge decision and later error-analysis/dependency choices retain
the timing stated in that sheet. None is approved by this preparation.

Exact remaining blockers:

1. Scientific decisions/sign-off: study status, hypotheses, outcome hierarchy,
   contrasts, model/decoding/limits/replication, retry/failure/denominator rules,
   controls, evaluators, schema, review and statistical policies are unapproved.
2. Data: approve the 100 IDs and sampling/review rules; create a separate selected
   manifest and freeze per-testbed hashes; perform real target extraction and
   20 human checks before literature scoring. No extractions/reviews exist here.
3. Already-asked metric: obtain a genuine question-bearing source with verified
   provenance and approve its scope, frozen corpus and matching policy.
4. Implementation dependent on those decisions: per-testbed hash schema/gate
   integration, held-out donor settings, evaluator/analysis settings and
   runnable run/analysis entry points remain unfinished. Existing interfaces
   are not a finalized executable protocol. No choices were invented to fill them.
5. Prospective record: finalize PREREG and freeze configuration only after
   approval; a later separately authorized commit must satisfy the Git gate.
   This request explicitly prohibits committing.

Verification: complete E6 unittest discovery passes 258 tests; validator's ten
self-tests pass. Non-inference protocol validation returns BLOCKED (exit 2),
with 64 unresolved/invalid items including the finalized-record Git gate.
This expected gate result is not an experiment failure or a passing finalization.

Next action: researcher reviews and records the 26-group decisions using the
concrete cap and sample materials. In parallel, supply the genuine prior-question
source. Then implement the approved configuration/freeze changes and complete
extraction review; a full ten-record development profile is not a prerequisite.

## Continuation: consolidated approval and freeze/review implementation

Implemented `RESEARCHER_APPROVAL.json` with all 26 proposed decisions, evidence
file hashes, unresolved operational-detail fields and empty approval fields.
`researcher_approval.py` requires explicit researcher identity/time/value and
payload binding for every decision; finalization additionally binds configuration
and selected-sample artifacts. Approval never follows from a default or a
recommendation. It validates recorded attestations, not human identity.

Implemented `literature_finalization.py` with a deterministic 100-target freeze
plan and exact 20-case list, an approval-gated future freeze API, source/prompt/
model/raw-output validation for extraction records, and source-bound human-review
bundle validation. The saved plan has 100 jobs, zero completed extractions and
zero completed reviews. Only source selection may be frozen by that API;
annotations remain unvalidated and no experiment is authorized. Replacements to
scope/sampling/ID policies require adapted code rather than silent reuse.

Prepared `LITERATURE_REVIEW_GUIDE.md` (unapproved) and a review/adjudication format
file containing no actual reviews. Review validation requires all exact cases,
independent reviewer IDs, valid times, four Boolean checks and source/extraction/
guide hashes. Disagreements require independent adjudication; completed negative
checks do not make annotations usable.

Prepared `FINALIZATION_WORKFLOW.md`. The Git gate now checks explicit approvals
and every signed artifact against HEAD. `validate_protocol.py --non-inference
--precommit` provides read-only local readiness validation without requiring a
commit and cannot authorize execution. No finalization/Git-mutating workflow was
executed; PREREG remains DRAFT. Existing data/results and proposal bytes remain
unchanged; no model inference or OpenAlex requests were made.

Verification: **277 E6 tests passed** (258 previous plus 19 new); all ten validator
self-tests passed. Approval-only validation correctly blocks all 26 pending
decisions plus configuration sign-off. Precommit readiness correctly reports
91 unresolved/invalid items, including the original configuration gaps and new
explicit approval checks. The count is validation messages, not new scientific
decisions.

Remaining blockers: researcher resolves/signs all decisions and operational
details; actual prior-question source; approved per-testbed configuration/hash,
donor/evaluator/statistical integration and run/analysis entry points; approved
sample freeze; actual target extraction and 20 human checks before literature
scoring; final artifact sign-off and a later separately authorized preregistration
commit. The freeze/review/approval mechanisms are implemented; approved scientific
settings and real annotation/review data are not supplied by software.

Exact next action: researcher edits `E6/RESEARCHER_APPROVAL.json` using the
proposals/evidence and `FINALIZATION_WORKFLOW.md`, explicitly resolving the
required detail keys. Supply genuine prior-question source data for decision 20.
Then run `python3 E6/researcher_approval.py` to identify any remaining unsigned
or incomplete decisions; do not mark FINALIZED or freeze data before approval.

## Assignment-based minimum decisions pass

Read the original assignment from the local saved source and preserved the
experiment/E6 excerpts in `assignment_e6_excerpt_v1.txt`. `DECISION_CLASSIFICATION.json`
classifies A/B/C components within all 26 groups; mixed decisions are not falsely
labelled wholly mandated. Verified facts and implemented settings are not called
researcher approvals. No explicitly signed row was present. The older local
protocol's “approved” claim and conflicting Qwen/Normal–Counterfactual/Macro-F1/
selection settings are preserved verbatim in `prior_protocol_2026-11-04.md` for
researcher reconciliation; nothing establishes its supersession or approver.

Implemented assignment constraints in the appropriate configurations:

- Common **generated-token** cap, with prompt usage recorded separately. Added
  actual generated-token enforcement in the budget controller and final-mode
  orchestrator. Intermediate/discarded/retry/probe outputs count; unknown usage
  locks the affected arm. Historical DEVELOPMENT accounting stays unchanged.
- Empty-control evidence exclusion, other-instance shuffled control, required
  question evaluation and fixed target extraction.
- Both existing literature minimum constraints and 20 target-extraction checks
  retained. Added the separate mandatory 20-input-set end-to-end error-analysis
  requirement, 95% paired input-set bootstrap uncertainty, mandatory JSONL fields
  and external labels, prospective predictions and one-page memo requirements.
- Reconstruction and question-type requirements and optional pairwise-judge
  safeguards retained/recorded. Config validation rejects incorrect mandate values.

No numeric cap, model selection, decoding, sample freeze, reviewer count, metric
scale or bootstrap replicate count was silently chosen. K=6/M=3 remains the
existing E6 contract; the assignment presents it as an example, not a requirement.
The v1 cap proposal remains unchanged; `fixed_token_cap_proposal_v2.json` proposes
8192 **generated** tokens and explains why historical total-token profiles do not
estimate adequacy for this unit.

`APPROVAL_CHECKLIST.md` is one concise checklist of ten grouped choices, each with
proposed value, need, consequence and recommendation. Scientific components remain
in 23 original groups. IDs 6/7/17 (hashes, preserved IDs, schema compatibility) are
implementation/final artifact-sign-off work; their row statuses are still pending,
not approved. The validator uses its fixed scientific-ID set, so editing an
untrusted classification flag cannot bypass a scientific approval. Evidence hashes
in pending rows are refreshed after changes, and prior snapshots are retained;
signed approvals, if any, would remain untouched.

Implementation blockers: integrate chosen per-testbed hash/donor/evaluator/analysis
settings; build approved source-safe inputs; add required JSONL export and run/
analysis entry points; compute final versions/hashes and complete the final Git
workflow when authorized. These are coding/mechanical work, not extra researcher
choices. Genuine external/human dependencies: governing-protocol precedence,
scientific choices and expected magnitudes, actual prior-question source data,
real extraction results and 20 human extraction checks, and the eventual
20-input-set end-to-end error analysis. The extraction checks and error analysis
are different activities and may overlap cases if the approved sampling permits.

Verification: **287 E6 tests pass**, plus all ten validator self-tests. No pending
approval was changed to approved. PREREG remains DRAFT, cap remains null, sample
remains unfrozen, and no inference, external retrieval, commit or push occurred.

Exact next action: resolve the governing protocol and answer the ten rows of
`APPROVAL_CHECKLIST.md`; identify the real prior-question corpus. Record actual
choices and their necessary details in `RESEARCHER_APPROVAL.json`. Mechanical
hashing/schema work does not require separate scientific approval.
