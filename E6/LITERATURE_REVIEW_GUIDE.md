# Literature target-extraction review guide v2 — Decision 24 procedure approved

Review the preserved source field and exact extraction, not generated arm outputs.
Record the target ID, source-text SHA-256, extraction SHA-256, this guide's file
SHA-256, reviewer identity and UTC completion time. Work independently before
comparing judgments. A software validator cannot establish reviewer independence.

Answer each check with true or false:

- `research_question_extraction_accurate`: the extracted question faithfully
  represents the source's research question; it adds no unsupported claim.
- `main_hypothesis_extraction_accurate`: the extracted hypothesis faithfully
  represents the main hypothesis supported by the source's stated research aim.
- `research_question_explicitness_accurate`: the extracted explicitness flag
  correctly distinguishes a question expressly stated from one inferred.
- `main_hypothesis_explicitness_accurate`: the analogous flag is correct for the
  main hypothesis.

A null extracted field is accurate only if that field cannot be supported by
this exact source. Do not infer unavailable full text from an abstract. Record
source quotations/locations and the reason for negative judgments in notes.
Null fields do not become usable nonempty references merely because the null is
accurate; apply the separately approved missing-annotation scoring policy.

The existing two-independent-reviewer procedure is retained: two independent reviewers for each of the 20 fixed
cases. An independent third adjudicator resolves any disagreement, records four
final Boolean judgments and a rationale, and binds the sorted reviewer records
by SHA-256. The adjudicator must differ from the case's reviewers. Matching
negative judgments are still negative. Corrections require a new version of the
annotation and renewed checks; never overwrite the original annotation or mark
all cases accepted merely to reach 20. Report disagreement and completion counts.

Decision 24 additionally requires checking the extracted problem, method and
result against original source evidence. Record Boolean
`problem_extraction_accurate`, `method_extraction_accurate` and
`result_extraction_accurate`, with source quotations/locations in reviewer_notes.
Do not infer a missing extracted method or result from the generated hypotheses.
If an extraction does not contain a required component, record the omission and
a negative check; do not synthesize text or mark the component verified.
Record `extraction_errors` and `corrections` as explicit lists (empty only if
actually none). Corrections must name the original annotation, corrected text and
source location; preserve original records and re-review corrected versions.
Disagreements on any of the seven checks require independent adjudication.
All 20 deterministic cases must be reviewed before literature scoring. Approval
of this procedure is not evidence of a completed extraction or human review.
