# E6 TRAIN evaluator pilot — independent review

Offline verification: 16/16 saved model responses verified; 6/6 logical identity controls correct. Independent human judgments completed: 0/10. Evaluator validations genuinely completed: 0/4. Identity controls are logical references, not human reviews.

Complete exactly the ten cases below using the verbatim frozen rubrics. Supply a label, your identifier, an ISO date (YYYY-MM-DD), and a short rationale for each. No labels or rationales below were supplied by a model. Saved evaluator predictions are intentionally omitted to support independent review.

After review, compare with `verified_responses.json` and record agreement (and similarity MAE). Researcher adequacy assessment remains required: no frozen numeric acceptance threshold exists. This pilot alone does not establish literature reconstruction validity or full category/score coverage.

Sources: `E6/data/evaluator_validation_train_v2/cases.json`, saved `*_result.json` records; existing forms and verified predictions in this directory. Both existing Markdown forms and the v1/v2 JSON worklists contain no completed human labels.

Rubric placeholders map directly to A/B below: similarity uses FIELD = main hypothesis, GENERATED = A, TARGET = B; same-question uses TEXT_A = A (generated research question), TEXT_B = B (TRAIN generated research question); distinctness uses HYPOTHESIS_A/B = A/B; classification uses QUESTION = A.

For diversity, null is allowed by the frozen rubric. The existing ingestion helper accepts only Boolean diversity labels; preserve any human null judgment explicitly for manual comparison rather than coercing it.

- reconstruction: reconstruction-03, reconstruction-04
- already_asked: already_asked-03, already_asked-04
- diversity: diversity-03, diversity-04
- question_type: question_type-01, question_type-02, question_type-03, question_type-04

## Frozen rubrics

### question_type

Source: `prompts/e6/10_question_type.txt`; SHA-256: `e0ebd66a009d84342f6ab6c781d3e0d42cc9a432a3bf0abeb29d91c47fca8503`

```text
ROLE
You are a classifier of scientific research questions.

TASK
Classify the supplied research question into exactly one category.

RESEARCH QUESTION
{{QUESTION}}

CATEGORIES

constructive:
The question primarily asks how to build, design, develop, create, improve, optimize or enable a system, method, intervention or capability.

analytic:
The question primarily investigates the extent, cause, mechanism, relationship, comparison, effect or explanation of an existing or observed phenomenon.

other:
The question does not clearly fit either constructive or analytic.

ambiguous:
The supplied question is too vague, underspecified or internally mixed to assign a reliable primary category.

RULES
1. Classify the central research objective, not isolated keywords.
2. Choose exactly one category.
3. Do not provide explanations or additional categories.
4. Do not use outside information.

OUTPUT
Return valid JSON only:

{"type": "constructive"}

The value of type must be exactly one of:
"constructive", "analytic", "other", "ambiguous".
```

### similarity

Source: `prompts/e6/15_reconstruction_similarity.txt`; SHA-256: `04c2dfc868e1d7054ac9cb496b0b5d8c6172965fadb37e1327047acbb33c152d`

```text
ROLE
Evaluate substantive reconstruction of a scientific research question or hypothesis.
This is a proposed rubric requiring researcher approval before use.

FIELD
{{FIELD}}

GENERATED ITEM
{{GENERATED}}

SOURCE TARGET
{{TARGET}}

Judge only these texts. Ignore writing quality, arm identity and outside knowledge.
Score the match in scientific objective, predictor/condition, outcome, scope and,
where stated, direction. Shared topic alone is not substantive equivalence.

Integer scale:
1: unrelated scientific objective or relationship.
2: shared topic only; substantive objective or relationship differs.
3: partial substantive match with important components missing or different.
4: close substantive match with a material difference in scope or relationship.
5: substantively equivalent; wording may differ.

Return exactly one JSON object, without explanation:
{"similarity": 1}
The value must be an integer from 1 through 5.
```

### same_question

Source: `prompts/e6/08_same_question.txt`; SHA-256: `ff50bc4e09ff7c97b2bc52688831fbb027df940969d6bef305c27f327dc9ca82`

```text
ROLE
You are an evaluator of semantic equivalence between scientific research statements.

TASK
Determine whether two supplied statements express substantially the same research objective.

STATEMENT A TYPE
{{TYPE_A}}

STATEMENT A
{{TEXT_A}}

STATEMENT B TYPE
{{TYPE_B}}

STATEMENT B
{{TEXT_B}}

DECISION RULE
Return true only when both statements substantially concern the same:
- phenomenon or scientific subject;
- objective, mechanism or relationship being investigated; and
- principal outcome or question being addressed.

Treat genuine paraphrases as equivalent even when wording differs.

Return false when statements merely share a topic, keywords, broad domain or research area but investigate meaningfully different mechanisms, relationships, objectives or outcomes.

Do not treat a more specific question as equivalent to a broader question unless they genuinely express the same central objective.

Do not use outside knowledge. Judge only the supplied text.

OUTPUT
Return valid JSON only:

{"same_question": true}

or

{"same_question": false}
```

### distinctness

Source: `prompts/e6/16_hypothesis_distinctness.txt`; SHA-256: `eeca6fcbb7f8a8f7a294b0fd9c9d31c91b671fd1d395ab36139c2f9a99b217e8`

```text
ROLE
Judge whether two scientific hypotheses make substantively distinct claims.
This is a proposed rubric requiring researcher approval before use.

HYPOTHESIS A
{{HYPOTHESIS_A}}

HYPOTHESIS B
{{HYPOTHESIS_B}}

Use only the supplied texts. Return false for paraphrases of the same substantive
predictor/condition, outcome, relationship and direction. Return true when at
least one of those components makes the central scientific claim materially
different. Wording differences alone are insufficient. A broad claim and its
narrow restatement are not distinct unless the narrower claim adds a materially
different testable condition or relationship. Judge scientific content, not quality.
If the texts do not permit a reliable Boolean judgment, return null; the input-set
diversity metric must then remain unavailable rather than treating null as false.

Return exactly one JSON object, without explanation:
{"distinct": true}
The value must be true, false, or null.
```

## question_type-01

Rubric: `prompts/e6/10_question_type.txt`

A: To what extent does explicit criticism of political institutions (e.g., Supreme Court, government shutdowns) correlate with predicted voting preference?

Source: `E6/runs/priority10_train_batch002/aa367e4423af8dc3_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`; SHA-256: `7340af8c3df91e969ef4060271247f91799584276e5b506298ae3f2162454032`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## question_type-02

Rubric: `prompts/e6/10_question_type.txt`

A: How do endorsements of specific policies (e.g., gun rights, universal healthcare, climate change initiatives) influence the predicted voting preference, considering potential ideological contradictions?

Source: `E6/runs/priority10_train_batch002/aa367e4423af8dc3_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H3`; SHA-256: `7340af8c3df91e969ef4060271247f91799584276e5b506298ae3f2162454032`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## reconstruction-03

Rubric: `prompts/e6/15_reconstruction_similarity.txt`

A: Expressing frustration over the lack of third-party debate presence is more likely to correlate with a Democratic voting preference.

B: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## already_asked-03

Rubric: `prompts/e6/08_same_question.txt`

A: Does the expression of frustration regarding the lack of third-party debate presence correlate with a specific predicted voting preference?

B: To what extent does reaction to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference?

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## diversity-03

Rubric: `prompts/e6/16_hypothesis_distinctness.txt`

A: Expressing frustration over the lack of third-party debate presence is more likely to correlate with a Democratic voting preference.

B: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## question_type-03

Rubric: `prompts/e6/10_question_type.txt`

A: Does the expression of frustration regarding the lack of third-party debate presence correlate with a specific predicted voting preference?

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H5`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## reconstruction-04

Rubric: `prompts/e6/15_reconstruction_similarity.txt`

A: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

B: Tweets explicitly criticizing political institutions are more likely to be associated with a third-party or non-voting preference.

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Source: `E6/runs/priority10_train_batch002/aa367e4423af8dc3_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`; SHA-256: `7340af8c3df91e969ef4060271247f91799584276e5b506298ae3f2162454032`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## already_asked-04

Rubric: `prompts/e6/08_same_question.txt`

A: To what extent does reaction to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference?

B: To what extent does explicit criticism of political institutions (e.g., Supreme Court, government shutdowns) correlate with predicted voting preference?

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Source: `E6/runs/priority10_train_batch002/aa367e4423af8dc3_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`; SHA-256: `7340af8c3df91e969ef4060271247f91799584276e5b506298ae3f2162454032`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## diversity-04

Rubric: `prompts/e6/16_hypothesis_distinctness.txt`

A: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

B: Tweets explicitly criticizing political institutions are more likely to be associated with a third-party or non-voting preference.

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Source: `E6/runs/priority10_train_batch002/aa367e4423af8dc3_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0001:f4dd50eb316a` / `QH:H1`; SHA-256: `7340af8c3df91e969ef4060271247f91799584276e5b506298ae3f2162454032`

Independent label: ______  Reviewer/date: ______
Rationale: ______

## question_type-04

Rubric: `prompts/e6/10_question_type.txt`

A: To what extent does reaction to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference?

Source: `E6/runs/priority10_train_batch001/b90d71ea502c100a_generation_envelope.json` — `hypobench-synthetic-election-level2:TRAIN-SET:0000:4b44593d53e3` / `QH:H3`; SHA-256: `37a1f47e90f743086a5fa24a05af828ca6dbccaa04ecda57f24b973e1db0d926`

Independent label: ______  Reviewer/date: ______
Rationale: ______
