# E2 Coverage Manipulation Audit — Version 1

## Purpose

Document the realized claim coverage of the existing synthetic E2
manipulation conditions. This is a post hoc implementation audit, not
a prospective preregistration and not a new scoring run.

## Implementation inspected

In `E2/generate_manipulations.py`, the number of planted claims is
calculated as:

    count = max(1, math.ceil(len(claims) * percent / 100))
    planted = claims[:count]

Claims retain their audited extraction order. They are not ranked by
relevance. The minimum-one-claim rule and ceiling operation mean that
realized coverage may exceed the nominal target, particularly when a
focal paper has few extracted claims.

## Realized coverage

The existing `E2/data/manipulation_plan.jsonl` was inspected read-only.
The existing score outputs were not regenerated for this audit.

| Nominal condition | Cases | Exact-target cases | Exact-target rate | Full-coverage cases | Full-coverage rate | Mean realized coverage |
|---|---:|---:|---:|---:|---:|---:|
| 25% | 300 | 104 | 34.67% | 2 | 0.67% | 32.47% |
| 50% | 300 | 162 | 54.00% | 2 | 0.67% | 55.41% |
| 75% | 300 | 104 | 34.67% | 58 | 19.33% | 82.89% |
| 100% | 300 | 300 | 100.00% | 300 | 100.00% | 100.00% |

Median realized coverage was 33.3%, 50.0%, 80.0%, and 100.0% for the
nominal 25%, 50%, 75%, and 100% conditions, respectively.

## Interpretation

1. All four conditions contain 300 cases.
2. The nominal 100% condition plants every extracted claim in all 300 cases.
3. The lower nominal conditions are minimum coverage targets, not exact
   realized percentages for every focal paper.
4. The ceiling rule can produce realized coverage above the nominal
   target. With small claim sets, it can produce 100% coverage even in
   a nominal partial-coverage condition.
5. The coverage generator selects the first N claims in audited
   extraction order. This does not establish that the selected claims
   are the most relevant or representative claims.

The previously observed score trends should therefore be described as
responses to the nominal synthetic manipulation conditions, alongside
the realized coverage distribution. These results alone do not establish
semantic novelty validity or agreement with independent human judgments.

## Scope and preservation

- This note documents an audit of existing artifacts.
- No scoring was run as part of this audit.
- `E2/data/scoring_results.jsonl` was not modified.
- `E2/data/scoring_results.matmul_pilot.jsonl` was not modified.
- `PREREG.md` was not modified.
- No existing analysis note was overwritten.

