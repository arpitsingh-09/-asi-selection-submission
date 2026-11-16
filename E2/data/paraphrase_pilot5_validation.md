# E2 five-paper paraphrase pilot

- Created (UTC): 2026-10-25T14:28:29.077647+00:00
- Model: `qwen3:8b`
- Prompt: `semantic_preservation_v1`
- Status: generated outputs require manual validation
- Bulk generation authorized: no
- Scoring authorized: no
- Original experiment results modified: no

## Results

| Paper ID | Pool | Generation status | Manual validation |
|---|---|---|---|
| 2012.14359v1 | computer_vision | generation_or_json_parse_failed | not reviewed |
| 2012.14371v3 | computer_vision | generation_or_json_parse_failed | not reviewed |
| 2012.13915v2 | computation_language | generation_or_json_parse_failed | not reviewed |
| 2012.14271v3 | computation_language | generation_or_json_parse_failed | not reviewed |
| 2012.14961v1 | machine_learning | generation_or_json_parse_failed | not reviewed |

## Review checklist

For every paper, verify:

1. The candidate title retains the source paper's subject and scope.
2. Every original claim remains supported by the candidate abstract.
3. Named components, methods, and their relationships are unchanged.
4. No unsupported result, dataset, contribution, or performance claim appears.
5. The reported conclusion retains its original strength.
6. Any uncertain wording is marked for revision or rejection.

Lexical similarity alone is not evidence of semantic preservation.
Do not score any candidate until it has passed manual validation.

## Output files

- `E2/data/paraphrase_pilot5.jsonl` — parsed candidates and review status
- `E2/data/paraphrase_pilot5_raw.jsonl` — raw model output and execution details
- `E2/data/paraphrase_pilot5_validation.md` — this validation checklist

Original focal-paper data, claim records, manipulation plans, and existing
scoring results were read but not modified by this script.
