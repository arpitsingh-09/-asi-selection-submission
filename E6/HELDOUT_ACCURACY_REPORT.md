# E6 held-out accuracy: saved data-testbed partial results

## Scope

This report reconciles the completed `heldout_accuracy` phase in
[`runs/heldout_accuracy_optimized_v1/`](runs/heldout_accuracy_optimized_v1/).
It uses saved evaluation summaries and request-cache records only. The phase
marker and summary both say accuracy execution is complete. The report does
not claim that the full E6 Task 2 is complete: these are HypoBench data-testbed
accuracy outcomes only, not literature reconstruction or the other registered
metrics.

The official Task 2 requires the seven arms on both testbeds and paired
input-set intervals for literature reconstruction, data-based outcomes,
already-asked rate, diversity, question type, and at most one optional judge.
The official rubric is in [`assignment_e6_excerpt_v1.txt`](assignment_e6_excerpt_v1.txt).
The controlling analysis uses generation input set as the paired unit,
arithmetic means, 10,000 percentile-bootstrap replicates, seed 2026, Python
MT19937/SHA-256 replicate streams, and unadjusted marginal 95% intervals.

## Cohort and cell reconciliation

The held-out manifest has 501 distinct TEST observations. The planned data
cohort has 20 TRAIN evidence-generation sets and seven arms (140 planned
generation/evaluation cells). Saved accuracy summaries cover 19 sets with at
least one completed arm; 13 of those 19 have all seven arms. Across them,
**125 arm-by-generation-set accuracy cells** have saved outcomes, each scored
on the same 501 TEST observations. That is 62,625 TEST-prediction assignments.

The 15 other planned cells have no accuracy result:

- Eight generation cells failed: `D` in three sets, `QH-sel` in three, and
  `QH-rand` in two. Their accuracy remains unavailable, not zero.
- All seven cells for TRAIN set `0007` are absent/unresolved. They remain
  missing and were not retried.

All seven arms have at least one genuine saved accuracy result. An arm-level
result means a saved 501-row evaluation record; it does not mean all 501 model
outputs were valid. Per the frozen rule, invalid predictions count as
incorrect within the fixed 501 denominator.

## Held-out accuracy by arm

Accuracy is exact label match, averaged across the available generation sets;
all cells have the same 501-row denominator. Intervals resample generation
input sets. `Invalid predictions` counts malformed, failed, or unresolved
outputs already scored as incorrect by the saved evaluation.

| Arm | Sets | Correct / TEST assignments | Accuracy (95% CI) | Invalid predictions |
|---|---:|---:|---:|---:|
| D | 16 | 401 / 8,016 | 5.00% [0.00, 10.94] | 6,748 / 8,016 (84.18%) |
| QH | 19 | 282 / 9,519 | 2.96% [0.00, 7.15] | 8,020 / 9,519 (84.25%) |
| QH-sel | 16 | 105 / 8,016 | 1.31% [0.00, 3.16] | 7,016 / 8,016 (87.52%) |
| QH-rand | 17 | 127 / 8,517 | 1.49% [0.00, 3.71] | 7,516 / 8,517 (88.25%) |
| HQ | 19 | 216 / 9,519 | 2.27% [0.00, 4.75] | 8,019 / 9,519 (84.24%) |
| D-empty | 19 | 2,641 / 9,519 | 27.74% [27.74, 27.74] | 19 / 9,519 (0.20%) |
| D-shuffled | 19 | 770 / 9,519 | 8.09% [0.00, 16.36] | 8,016 / 9,519 (84.21%) |

Across all 62,625 assignments, 45,354 outputs (72.42%) were invalid and
counted incorrect; 4,542 were correct. Saved invalid reasons are dominated by
local Ollama `connection refused` failures (45,324 assignments); the remainder
are retained missing responses, malformed JSON, missing hypothesis citations,
and one closed connection. Therefore these accuracy numbers measure the
configured workflow including its response failures. They are not a clean
measure of reasoning quality conditional on valid model responses.

## Seven-arm descriptive comparisons

The following table gives every configured pairwise accuracy difference.
Differences are `left arm − right arm` in percentage points. Each interval
uses complete paired generation sets only; `n` is that pair's available-set
count. The direct `D` arm is the ordinary evidence-conditioned baseline.
No directional accuracy hypothesis was registered: the three registered
directional hypotheses concern literature main-hypothesis similarity, so all
these data-accuracy contrasts are descriptive.

| Contrast | n | Difference, pp (95% CI) |
|---|---:|---:|
| D − QH | 16 | +2.32 [0.00, 5.70] |
| D − QH-sel | 13 | +2.13 [0.00, 6.19] |
| D − QH-rand | 14 | +1.94 [0.00, 5.66] |
| D − HQ | 16 | +3.31 [0.00, 7.98] |
| D − D-empty | 16 | −22.74 [−27.74, −16.80] |
| D − D-shuffled | 16 | −1.47 [−7.82, 4.04] |
| QH − QH-sel | 16 | −0.02 [−0.97, 0.90] |
| QH − QH-rand | 17 | −0.28 [−1.02, 0.18] |
| QH − HQ | 19 | +0.69 [−0.96, 3.17] |
| QH − D-empty | 19 | −24.78 [−27.74, −20.59] |
| QH − D-shuffled | 19 | −5.13 [−11.51, 0.00] |
| QH-sel − QH-rand | 16 | −0.27 [−0.79, 0.00] |
| QH-sel − HQ | 16 | −0.46 [−1.38, 0.00] |
| QH-sel − D-empty | 16 | −26.43 [−27.74, −24.59] |
| QH-sel − D-shuffled | 16 | −5.16 [−12.90, 0.00] |
| QH-rand − HQ | 17 | −0.18 [−0.63, 0.11] |
| QH-rand − D-empty | 17 | −26.25 [−27.74, −24.03] |
| QH-rand − D-shuffled | 17 | −4.60 [−11.42, 0.00] |
| HQ − D-empty | 19 | −25.48 [−27.74, −23.00] |
| HQ − D-shuffled | 19 | −5.82 [−12.07, 0.00] |
| D-empty − D-shuffled | 19 | +19.66 [11.39, 27.74] |

The empty-input control scored higher than `D`, while the shuffled-input
control also scored higher by point estimate and its interval includes zero.
Neither behaves as the assignment's expected worse-than-input control. The
very different invalid-output rates matter: `D-empty` had 0.20% invalid
outputs, compared with roughly 84–88% for the other arms. This control contrast
is therefore strongly confounded by response validity and cannot establish
that removing evidence improves the scientific quality of hypotheses. The
selection-vs-random contrast is −0.27 pp [−0.79, 0.00] on the 16 complete
paired sets; it is descriptive for data accuracy and is not the preregistered
literature H2 result.

The intervals are conditional on the same fixed 501-observation TEST
benchmark. Resampling was over the available TRAIN evidence-generation sets,
as registered; it does not estimate uncertainty from drawing a new TEST
benchmark. Historical researcher exposure to TEST labels is disclosed in the
preregistration, so these observations are not described as historically
unseen.

## Compute and cost evidence

- The saved runtime identity is local `gemma3:12b`, 11.8B parameters,
  Q4_K_M quantization, llama.cpp/Ollama, with a recorded model digest. The
  held-out prediction request used a 32-token output ceiling, temperature 0,
  top-p 1, seed 2026. Execution binding records one worker.
- Deduplicating repeated per-hypothesis token rows by `token_accounting_id`,
  the 125 successful generation cells report **90,833 generated tokens**.
  This excludes failed generation-cell charges, which are not complete in the
  saved successful-generation records.
- The exact-request cache contains 53,607 unique request keys: 8,279 finished
  replies, 45,325 failed requests, and 3 unresolved retained-invalid entries.
  Finished replies contain 4,907,623 prompt-evaluation tokens and 195,806
  output tokens (5,103,429 total). Failed requests have no complete usage
  record, so this is recorded successful-reply usage, not total attempted
  compute. Reused request replies are not counted as additional model calls.
- The artifacts do not provide a reliable total wall-clock runtime or GPU
  utilization figure; neither is inferred here.

## What remains incomplete for official Task 2

This completes reporting of the saved data-testbed held-out accuracy metric,
not E6 Task 2 as a whole.

- **Literature testbed:** no completed seven-arm literature generations and
  metric outputs are present. The required 20 hand checks remain incomplete;
  the stricter frozen source-review package has 40 reviews/280 checks pending,
  and evaluator validation remains 0/4 complete.
- **Other metric families:** no complete literature reconstruction scores,
  already-asked rates, diversity scores, question-type comparison, or
  validated judge results. The optional judge is not required to be used.
- **Planted-hypothesis recovery/HDR:** 0/125 data cells are scored; source
  feature mapping and grounded recovery judgments are missing.
- **Missing data cells:** eight failed generations and seven unresolved
  set-0007 arms remain missing. They must not be rerun or imputed under this
  report.
- **Task 3/4:** actual 20-set end-to-end human error review is still pending;
  the existing one-page memo remains provisional until required outcomes and
  reviews exist.

## Read-only reproduction

Run from the repository root. This command validates each completed evaluation
hash, the exact 501-row manifest order and stored accuracy counts, reconstructs
the 20-unit source list from the readiness ledger (including the entirely
missing set), and recomputes arm means and all 21 paired intervals from saved
summary records. It performs no inference, writes no files, and does not touch
the locked source run.

```sh
python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, 'E6')
from evaluation import ARMS, _hash_json
from statistical_analysis import analyze_evaluations

root = Path('.')
run = root / 'E6/runs/heldout_accuracy_optimized_v1'
manifest = json.loads((root / 'E6/data/hypobench_election_level2_test_manifest_v1.json').read_text())
test_ids = [r['input_set_id'] for r in manifest['records']]
assert len(test_ids) == 501 and len(set(test_ids)) == 501
sources, seen = [], set()
from collections import Counter
arm_totals = Counter()
for path in sorted(run.glob('*/*_evaluation.json')):
    row = json.loads(path.read_text())
    assert row['result_sha256'] == _hash_json({k:v for k,v in row.items() if k != 'result_sha256'})
    unit = row['generation_input_set_id']; seen.add(unit)
    for arm, cell in row['evaluations'].items():
        if cell.get('status') != 'evaluated': continue
        record = cell['heldout']['heldout_accuracy']
        assert record['status'] == 'succeeded'
        assert record['evaluation_input']['input_set_ids'] == test_ids
        scored = record['parsed_output']
        assert scored['denominator'] == 501
        assert scored['correct'] == sum(a == b for a,b in zip(record['evaluation_input']['true_labels'], record['evaluation_input']['predicted_labels']))
        arm_totals[(arm,'sets')] += 1
        arm_totals[(arm,'correct')] += scored['correct']
        arm_totals[(arm,'rows')] += scored['denominator']
        arm_totals[(arm,'invalid')] += scored['invalid_prediction_count']
    sources.append({'generation_input_set_id':unit, 'evaluations':row['evaluations']})
readiness = json.loads((root / 'E6/data/heldout_accuracy_readiness_v1.json').read_text())
planned = sorted({j['input_set_id'] for j in readiness['jobs'] if ':TRAIN-SET:' in j.get('input_set_id','')})
for unit in planned:
    if unit not in seen:
        sources.append({'generation_input_set_id':unit, 'evaluations':{a:{'status':'missing'} for a in ARMS}})
config = json.loads((root / 'E6/evaluation_config.json').read_text())['paired_bootstrap']
result = analyze_evaluations(sources, testbed='data', metric='heldout_accuracy',
    value_path=['heldout','heldout_accuracy','parsed_output','accuracy'],
    comparisons=[tuple(p) for p in config['comparisons']],
    replicates=config['replicates'], seed=config['seed'], missing_policy='complete_pairs')
print('arm means / 95% CIs')
for arm, value in result['arm_estimates'].items():
    print(arm, 'sets', value['included_count'], 'accuracy', value['point_estimate'], 'CI', value['interval'],
          'correct', arm_totals[(arm,'correct')], 'rows', arm_totals[(arm,'rows')],
          'invalid', arm_totals[(arm,'invalid')])
print('paired contrasts / 95% CIs')
for name, value in result['comparisons'].items():
    print(name, value['included_count'], value['point_estimate'], value['interval'])
PY
```

This second read-only command verifies the unique request-cache entry/reply
hashes, totals known prompt/output tokens from finished replies, and deduplicates
the saved generation-token rows by their registered accounting IDs. It never
calls the model or writes files:

```sh
python3 - <<'PY'
import json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, 'E6')
from evaluation import _hash_json

run = Path('E6/runs/heldout_accuracy_optimized_v1')
cache_counts = Counter(); prompt = output = total = 0
for path in (run/'request_cache').glob('*.json'):
    if path.name.endswith('.started.json'): continue
    row = json.loads(path.read_text()); assert row['entry_sha256'] == _hash_json({k:v for k,v in row.items() if k != 'entry_sha256'})
    terminal = row['terminal']; cache_counts[terminal['status']] += 1
    if terminal['status'] == 'finished':
        reply = terminal['reply']; assert terminal['reply_sha256'] == _hash_json(reply)
        prompt += reply.get('input_tokens', 0); output += reply.get('output_tokens', 0); total += reply.get('total_tokens', 0)
generation_cost = {}
for path in run.glob('*/*_evaluation.json'):
    row = json.loads(path.read_text())
    for item in row.get('generation_records', []):
        key = item.get('token_accounting_id'); value = item.get('tokens_generated')
        if key and isinstance(value, int):
            assert key not in generation_cost or generation_cost[key] == value
            generation_cost[key] = value
assert cache_counts == {'finished':8279, 'failed':45325, 'unresolved_retained_invalid':3}
assert (prompt, output, total) == (4907623, 195806, 5103429)
assert len(generation_cost) == 125 and sum(generation_cost.values()) == 90833
print('unique request keys:', sum(cache_counts.values()), dict(cache_counts))
print('finished-reply prompt/output/total tokens:', prompt, output, total)
print('successful-generation workflow token total:', sum(generation_cost.values()))
PY
```

Request-cache `*.started.json` intent markers are not terminal responses and
must not be counted as completed calls.
