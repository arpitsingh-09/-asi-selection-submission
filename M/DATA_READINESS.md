# Main Problem data readiness (Step 2)

Read against the committed protocol `M/PREREG.md` (parent commit `6e21dfe`) and the Main Problem summary in `M/SPECIFICATION.md`. Counts distinguish source/development records from evaluation-eligible examples. No evaluation was run. **No registered core test is ready to freeze and evaluate.**

| Test | Available dataset / sample count | Eligible now | Missing requirement | Smallest next action | Status |
|---|---|---:|---|---|---|
| I1 | E1: 61 focal questions / 122 A–B-min/C pairs; 0 independent confirmations. M generated set: 6 questions, with original/empty/shuffled snapshots prepared. | 0 | E1 pairs remain pending source/human confirmation; question-time and original inputs are unverified. I1 also requires normalized predictions for all seven readouts; both Q heads are unavailable. | Obtain independent source/identity annotations and dated question/input provenance; fit/verify Q or formally supply its preregistered normalization before eligibility review. | BLOCKED |
| I3 | E1: 61 pairs; 43 have `length_flipped=true` in source metadata. | 0 | No verified length-matched preference labels or trained Q heads; existing E1 alignment review is pending. | Independently verify pairs and labels, then produce length-matched predictions for each claimed Q/N coordinate and B-LEN. | BLOCKED |
| S1 | E1: 61 focal questions / 122 pairs. Two-reviewer workflow exists; 0 consensus labels. | 0 | Human confirmation, authored-question dates, input/control provenance and semantic model cutoff are unresolved. | Complete two independent human reviews, then verify question availability, original inputs and model cutoff. | BLOCKED |
| A1 | E2 has prior novelty manipulation/scoring results (300 focal-paper development cases; see `E2/RESUME_STATE.md` and `E2/data/scoring_results.jsonl`). | 0 | Those results are development evidence, not a new M cohort. No fresh prospective cohort with verified original inputs and all required controls. | Obtain source-verified eligible questions and input links, then prospectively lock partial-coverage/concentration manipulations and controls. | BLOCKED |
| H1 | E1 has 61 generated question pairs, but 0 recorded second-reader agreements; local ICLR review archives are not expert battles on generated ideas. | 0 | No source-bound expert preference battles, system/seed identities or complete Q predictions. | Collect dated, length-matched expert battles with system and shared-seed IDs. | BLOCKED |
| H3 | Local ingestion recovered 570 numeric ICLR review values and 277 paper identity links. | 0 | 0 verified public observation dates for the current score versions; 0 question-linked usable labels; no human ceiling, Q head or exact semantic B-Q cohort. | Recover dated public review versions linked to eligible post-cutoff questions and an independently measured human ceiling. | BLOCKED |
| O1 | 25 train / 2 validation / 80 metadata-only heldout candidates; 0 usable outcome labels. | 0 | Both separately defined dated quality outcomes and within-topic question pairs/Q heads are absent. | Link genuine dated peer-review and later-use outcomes to eligible question records; keep factors separate. | BLOCKED |
| O2 | E2 includes prior near/far pool comparisons; no verified M cohort of repeated identical seed-paper sets with dated outcomes. | 0 | No verified ≥3-paper identical seed groups, within-year paper pairs, or linked outcomes/Q predictions. | Recover paper citation/input groups and dated outcome labels for a new eligible cohort. | BLOCKED |
| T1 | No frozen 2022 and 2023 M quality-head artifacts. | 0 | Separate year-specific models, complete-head normalization and matched later-paper predictions are missing. | Obtain train labels and fit/lock both year-specific models using only their permitted train windows. | BLOCKED |

## Reusable records and limitations

`M/data/manifests_v2/` contains 25 source-date-valid train passages, 2 validation passages and 80 heldout candidates, but the heldout records are not eligible and have no dated quality labels. The 20 source passages in `M/data/local_preparation_v1/test.jsonl` are from the already-used E2 development pool and cannot be reused as fresh heldout examples. Original input links are missing in those records.

`M/data/generated_questions_v1/` contains six newly generated 2026 questions with explicit two-paper generation inputs and source dates. Original, empty and shuffled controls are recorded; two generated decoy questions have been prepared, with human review pending, and four rows remain unresolved. These are development records and do not supply genuine labels or a ready core-test cohort.

The 183 local MiniLM B-Q vectors are preparation artifacts; the exact training-data cutoff is unverified. `M/data/ingestion_v2/` preserves the 570 source review values, but none has a verified public observation date linked to an eligible question. `M/results/quality_v2/validation_results.json` therefore correctly leaves both Q heads unavailable.

## Decision

Ready: **none**. All nine registered tests are blocked. Existing E1/E2 measurements remain reusable only as development evidence where their provenance supports it; they are not promoted to prospective M results.
