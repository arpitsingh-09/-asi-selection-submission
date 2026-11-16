# I1 human review guide

Six prospective generated questions are listed in `i1_review.csv`. Original inputs are explicit generation inputs, not claims about the original authors’ inputs. Source IDs, versions, dates, URLs and source-record bindings are included in the CSV.

For each row, independently judge whether the question is coherent/intended, whether any supplied paraphrase preserves the same question, whether a near miss changes identity, and whether a proposed decoy addresses the same specific topic. Enter YES/NO only with a cited source/evidence locator and rationale. Record reviewer identity, independence from the question author, and review timestamp. Leave judgments blank when evidence is insufficient.

Decoy status is copied from the existing candidate file. `UNRESOLVED` or `GENERATED_DEC0Y_PENDING_HUMAN_REVIEW` means the decoy cannot be treated as verified. Blank proposed decoy fields mean no candidate is available. No judgments have been prefilled.
