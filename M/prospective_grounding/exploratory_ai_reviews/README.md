# Exploratory external-AI review import

No completed external-AI relevance assessments were found in the available
local records when this template was prepared. `assessments.csv` therefore
contains 18 registered question–paper pair slots with rating and evidence text
left blank; it is not an assessment dataset.

If source assessments are later supplied, import their rating and evidence
text verbatim. The importer accepts one JSON array of exactly 18 objects, each
with these four fields:

```json
[
  {
    "question_id": "paste exact ID from assessments.csv",
    "paper_id": "paste exact ID from assessments.csv",
    "rating": null,
    "evidence_text": ""
  }
]
```

Replace the placeholder values and repeat the object for every row/pair in
`assessments.csv`; do not omit pairs or add extra fields. Ratings must be
integer `0`, `1`, or `2`. Evidence strings
are preserved exactly as decoded (including whitespace and line breaks).
The importer adds `reviewer_type=external_ai`, `model_identity=unknown`
unless an independent source documents the model, `source_type=abstract_summary`,
and `experimental_status=exploratory_not_preregistered_human_review`.

Save the full array as JSON and run:

```sh
python3 -m M.prospective_grounding.exploratory_ai_reviews.import_batch /path/to/batch.json
python3 -m M.prospective_grounding.exploratory_ai_reviews.validate_import --path M/prospective_grounding/exploratory_ai_reviews/assessments_imported.csv --require-complete
```

The importer creates `assessments_imported.csv` and refuses to overwrite it.
It rejects missing or duplicate pairs, invalid ratings, and blank evidence
before writing the file. It then validates the completed CSV with the existing
validator.

These assessments came from an external AI assistant, not independent human
reviewers. They cannot replace the registered independent human-review forms.
They were based on supplied abstract summaries, not a full-text evidence
review. Their collection does not establish experimental results and must not
be used as a registered outcome or represented as human judgments.

Validate the template from the repository root:

```sh
python3 -m M.prospective_grounding.exploratory_ai_reviews.validate_import
```

Require a complete import after source text is supplied:

```sh
python3 -m M.prospective_grounding.exploratory_ai_reviews.validate_import --require-complete
```
