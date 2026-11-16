# Five-paper paraphrase pilot — v2

Generated UTC: 2026-10-25T14:38:08.159313+00:00
Model: `qwen3:8b`
Prompt: `semantic_preservation_v2`
Status: candidates require manual claim-preservation review.
Bulk generation authorized: no.
Scoring authorized: no.
Original experiment data modified: no.

| Paper ID | Pool | Generation status | Verbatim title | Verbatim abstract |
|---|---|---|---|---|
| 2012.14359v1 | computer_vision | generated_pending_manual_validation | True | False |
| 2012.14371v3 | computer_vision | generated_pending_manual_validation | True | True |
| 2012.13915v2 | computation_language | generated_pending_manual_validation | True | True |
| 2012.14271v3 | computation_language | generated_pending_manual_validation | True | False |
| 2012.14961v1 | machine_learning | generated_pending_manual_validation | True | True |

## Manual review required

For each candidate, compare every source claim against the abstract.
Check named methods, component relationships, application scope,
benchmark tasks, and conclusion strength. Record additions, omissions,
ambiguities, and a final accept/revise/reject decision before scoring.

These generated candidates are not validated merely because the JSON parses.

## Output files

- `E2/data/paraphrase_pilot5_v2.jsonl` — parsed candidate records
- `E2/data/paraphrase_pilot5_v2_raw.jsonl` — raw responses
- `E2/data/paraphrase_pilot5_v2_validation.md` — this review checklist
