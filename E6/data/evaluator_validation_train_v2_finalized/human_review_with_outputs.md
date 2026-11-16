# TRAIN evaluator pilot: examples and model outputs

Ten independent judgments are required for this pilot. These are not existing human labels.
Use the linked frozen rubric. Record a label, reviewer identity, date and short rationale.
Prefer labeling the blind sheet before opening the model-output sheet; disclosure of model outputs can bias agreement.
No passing threshold or adequacy decision is supplied by this sheet.

## question_type-01

Rubric: `prompts/e6/10_question_type.txt`

A: To what extent does explicit criticism of political institutions (e.g., Supreme Court, government shutdowns) correlate with predicted voting preference?

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`

Evaluator response: `{"type": "analytic"}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## question_type-02

Rubric: `prompts/e6/10_question_type.txt`

A: How do endorsements of specific policies (e.g., gun rights, universal healthcare, climate change initiatives) influence the predicted voting preference, considering potential ideological contradictions?

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H3`

Evaluator response: `{"type": "analytic"}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## reconstruction-03

Rubric: `prompts/e6/15_reconstruction_similarity.txt`

A: Expressing frustration over the lack of third-party debate presence is more likely to correlate with a Democratic voting preference.

B: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`, `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`

Evaluator response: `{"similarity": 3}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## already_asked-03

Rubric: `prompts/e6/08_same_question.txt`

A: Does the expression of frustration regarding the lack of third-party debate presence correlate with a specific predicted voting preference?

B: To what extent does reaction to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference?

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`, `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`

Evaluator response: `{"same_question": false}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## diversity-03

Rubric: `prompts/e6/16_hypothesis_distinctness.txt`

A: Expressing frustration over the lack of third-party debate presence is more likely to correlate with a Democratic voting preference.

B: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`, `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`

Evaluator response: `{"distinct": true}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## question_type-03

Rubric: `prompts/e6/10_question_type.txt`

A: Does the expression of frustration regarding the lack of third-party debate presence correlate with a specific predicted voting preference?

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`

Evaluator response: `{"type": "analytic"}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## reconstruction-04

Rubric: `prompts/e6/15_reconstruction_similarity.txt`

A: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

B: Tweets explicitly criticizing political institutions are more likely to be associated with a third-party or non-voting preference.

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`, `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`

Evaluator response: `{"similarity": 1}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## already_asked-04

Rubric: `prompts/e6/08_same_question.txt`

A: To what extent does reaction to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference?

B: To what extent does explicit criticism of political institutions (e.g., Supreme Court, government shutdowns) correlate with predicted voting preference?

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`, `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`

Evaluator response: `{"same_question": true}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## diversity-04

Rubric: `prompts/e6/16_hypothesis_distinctness.txt`

A: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

B: Tweets explicitly criticizing political institutions are more likely to be associated with a third-party or non-voting preference.

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`, `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`

Evaluator response: `{"distinct": true}`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## question_type-04

Rubric: `prompts/e6/10_question_type.txt`

A: To what extent does reaction to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference?

Source: `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`

Evaluator response: `{"type": "analytic"}`

Independent label: ______  Reviewer/date: ______
Rationale: ______
