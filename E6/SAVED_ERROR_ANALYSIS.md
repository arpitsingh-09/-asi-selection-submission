# Saved-record error analysis: available evidence only

The frozen review sample in `data/error_analysis_memo_v2/analysis.json` has 20
input sets: ten HypoBench TRAIN sets and ten literature targets. Existing
generation rows cover seven data sets completely, two with one failed arm,
and none for one set. No seven-arm literature generations exist. The saved
human review status is 0/20; review forms remain blank. This is therefore a
partial, AI-assisted record analysis, not a completed 20-set review or an
independent human judgment exercise.

## Concrete saved example

For `hypobench-synthetic-election-level2:TRAIN-SET:0011:a26c8c80a830`, the
direct arm emitted: “Expressions of frustration regarding third-party debate
presence are more frequent among users likely to vote Republican.” In the 20
saved TRAIN observations, four texts contain the third-party debate-presence
phrase: two are labelled likely Republican and two likely Democratic. The
directional “more frequent” clause is not supported by those observations.
This is an AI-assisted content check of an existing output, not a new model
score or independent label.

For the same input, QH asked whether stances such as gun rights and tax policy
jointly predict voter preference and emitted a matching combined-feature
hypothesis. This illustrates the extra explicit question step; it does not
establish that decomposition improves accuracy. D-empty instead proposed
generic claims about positive candidate language and partisan hashtags. The
latter is an expected no-evidence control behavior, not an independent failure
label.

## What saved outcomes establish

- On the data testbed, D exceeded QH by 2.32 percentage points on complete
  pairs (n=16; 95% CI 0.00 to 5.70); uncertainty includes no difference.
- QH-sel did not exceed QH-rand: QH-sel minus QH-rand was −0.27 pp (n=16;
  95% CI −0.79 to 0.00). This is descriptive accuracy, not the primary
  literature reconstruction test.
- D-empty and D-shuffled both scored above D by point estimate, contrary to
  the expected control direction. Their response-validity rates differ
  sharply, so these contrasts do not isolate the value of evidence.
- The most common logged failure was operational: 45,324 of 62,625 TEST
  prediction assignments had local Ollama connection refusal; 45,354 total
  predictions were invalid. These should be detected as transport failures
  before parsing, counted as invalid under the frozen rule, and kept separate
  from semantic error categories.

The missing literature outputs prevent comparison of where decomposition
helps or hurts on target reconstruction. The absent set-0007 generations,
failed cells, and pending qualitative coding also preclude a defensible
most-common *linguistic* failure claim across 20 end-to-end cases. No such
claim is inferred from the transport-error majority.
