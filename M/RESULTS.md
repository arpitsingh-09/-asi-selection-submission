# Main Problem results and execution status

## Registered evaluations

**0 of 9 registered evaluations are complete.** No registered evaluation was
scored in this work. There are no registered predictions, performance metrics,
confidence intervals, or pass/fail findings. The existing frozen candidate
lists are not evidence that their candidates are eligible. The runner remains
fail-closed when required provenance, labels, models, controls, or baselines are
missing.

Accordingly, the original nine-test battery provides no evidence for or
against its hypotheses. The supplementary A1 threshold was not met in a
two-cluster exposed replication, and V2 has generations plus exploratory
review agreement but no registered scoring result. Neither supplements the
missing core-battery outcomes.

| Evaluation | Status | Current decisive evidence gap |
|---|---|---|
| I1 | BLOCKED | Two generated candidates have a review packet, but two independent reviewer responses per candidate are pending. Original input relationships and validated controls are not established. Both fitted Q heads and frozen normalization are also absent. |
| I3 | BLOCKED | No eligible dated, length-matched preference labels linked to the frozen questions; Q heads unavailable. |
| S1 | BLOCKED | Existing source alignments lack the required independent verified judgments and complete question/input provenance; required model/baseline evidence is also incomplete. |
| A1 | BLOCKED | Existing E2 material is not a prospectively eligible M test cohort; the frozen cohort lacks verified source/input relationships and the required controls. |
| H1 | BLOCKED | No eligible source-bound expert battles with dated preference labels and required generating-system evidence; Q heads unavailable. |
| H3 | BLOCKED | Frozen records lack the required post-cutoff question/review-date linkage, numeric reviewer outcomes and independent human ceiling; Q and semantic baseline artifacts are unavailable. |
| O1 | BLOCKED | No eligible question-linked, dated peer-review and later-community-use outcomes; Q heads unavailable. |
| O2 | BLOCKED | No frozen records contain explicit supplied input-paper IDs (`R`) for identical seed groups. OpenAlex bibliographies cannot stand in for supplied inputs. No pair meets the registered grouping rule. |
| T1 | BLOCKED | The separately trained and prospectively frozen 2022 and 2023 model artifacts, complete head predictions and required controls are absent. |

The per-test ledger is also in [`results/stage5/RESULTS.md`](results/stage5/RESULTS.md).
It records no experimental metrics or confidence intervals.

## Supplementary S1 exploratory result (not original S1)

The separate supplementary S1 analysis used 60 source questions (one
minimal-paraphrase and one near-miss decision per question). Both categories
were evaluated against the author-intended E1 labels, which remain unverified;
the E1 data were exposed, so this is exploratory evidence. Identity accuracy
was 60/60 (1.00) for minimal paraphrases and 9/60 (0.15) for near misses;
`B-Q` accuracy was 60/60 (1.00) and 0/60 (0.00), respectively. The paired
identity-minus-`B-Q` accuracy difference was 0.00 for minimal paraphrases
(95% CI [0.00, 0.00]) and 0.15 for near misses (95% CI [0.0667, 0.25]);
both intervals use 2,000 paired source-question bootstrap draws (PCG64 seed
20261113). The criterion required the lower CI to exceed 0.02 in both
categories. It failed because the minimal-paraphrase lower bound is 0.00,
despite the near-miss comparison exceeding the margin. This does not complete
original S1, which remains incomplete alongside original A1; all 80/80 frozen
A1 candidates are ineligible. See the saved artifact at
[`supplementary_s1_e1_exploratory/results/run_001/results.json`](supplementary_s1_e1_exploratory/results/run_001/results.json).

## O2 evidence finding

The frozen O2 list has 80 rows representing 79 unique paper identities. The
cached OpenAlex evidence resolves 72 exact identities and contains dated citing
work for 31 papers (150 dated citing works). Offline comparison found 41 pairs
with at least three shared bibliography references inside the date window, but
**zero eligible pairs**: O2 requires identical explicitly supplied input-paper
sets of at least three IDs, and the frozen rows do not record those sets. Shared
references in later bibliographies are a different relation. The collector did
not score O2; the cached evidence is marked
`EVIDENCE_ONLY_NOT_SCORED` in
[`data/openalex_o2_v4/manifest.json`](data/openalex_o2_v4/manifest.json).
No further collection or inference was performed.

## I1 evidence finding

The packet at
[`data/i1_public_evidence_v1/i1_review_packet_v1/reviewer_packet.md`](data/i1_public_evidence_v1/i1_review_packet_v1/reviewer_packet.md)
contains two generated candidates (`mgen-v1-01`, `mgen-v1-02`) and blank sheets
for two independent reviewers. Candidate paper IDs and dates are sourced from
paper metadata, but the generated question-to-input relationship and proposed
paraphrase, near-miss and same-topic controls are not yet independently
validated. No human judgments have been imported and **zero I1 records are
eligible**. The I1 adapter is implemented and tested, but refuses to return Q
predictions unless both real, provenance-bearing fitted heads are supplied.
There was no registered I1 scoring.

## Quality model status

The quality fitting pipeline is implemented and tested. The current v2 fitting
manifest has 25 TRAIN and 2 VALIDATION question passages; its saved result
reports zero publication-time labels for both peer-review and later-community-
use factors. The dated-evidence eligibility report separately examined 570
review records against its manifests and found zero eligible labels in either
split for either factor. It reports missing exact cohort identity links,
verified public observation dates, and dated community-use outcomes. The saved
[`quality_v2/validation_results.json`](results/quality_v2/validation_results.json)
reports both heads unavailable. No quality model was fitted, no validation
prediction was created, and no TEST label was used for training.

## Development-only readouts

[`results/generated_development_v4/summary.md`](results/generated_development_v4/summary.md)
records one descriptive development run over six generated questions. It had no
failures and used original, empty, and shuffled input conditions. Each condition
reported mean pairwise cosine distance `0.6454798664494539`, Vendi
`4.699807081751871`, and class entropy `1.7917594692280547`. The identical values
across those conditions do not establish sensitivity to input changes. The run
had no human labels, registered pass criterion, confidence interval, or same-topic
decoy condition; Q was unavailable and claim-based N was unavailable. These
numbers are **descriptive development output only**, not results for any of the
nine registered tests and not evidence of system quality.

## Supplementary A1 partial replication (not original A1)

A separately versioned, exposed E2-informed supplementary analysis scored 16
nonempty targets over two independently reviewed focal-paper clusters
(`2512.23709v3`, `2610.29385v1`), with eight scored conditions per focal paper:
original-pool reference, 25/50/75/100% coverage, concentrated, distributed,
and shuffled. Empty-pool scores remained undefined. Same-topic decoys were
unavailable and excluded under approved Amendment 003. Analysis used paired
focal-paper cluster bootstrap (2,000 draws, PCG64 seed 20261113).

| Coordinate | Coverage pass fraction (95% CI) | Concentration pass fraction (95% CI) |
|---|---:|---:|
| Y | 0.500 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| density | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| N | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| yours | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |

No coordinate met the supplementary threshold: the same coordinate needed a
lower 95% confidence bound ≥0.80 for both coverage and concentration. Y met
the concentration ordering for both focal papers, but not the coverage rule;
the other coordinates did not show consistent ordering across both
manipulations. With n=2, intervals are discrete and unstable. This is a
negative threshold result for this exposed partial supplementary analysis
only; it does not complete or replace original A1. See
[`FINAL_REPORT.md`](FINAL_REPORT.md) and the exact outputs in
[`a1_replication/A1_STATISTICAL_RESULTS_V1.json`](a1_replication/A1_STATISTICAL_RESULTS_V1.json)
and [`a1_replication/A1_SCORING_RESULTS_V1.json`](a1_replication/A1_SCORING_RESULTS_V1.json).

## Prospective grounding V1/V2 (supplementary; no evaluation scored)

This pilot is separate from the nine original registered evaluations. V1's
first qwen3:8b call used the 512-token budget in thinking and returned
`response=""` (`done_reason="length"`) at
`2026-11-15T02:34:53.471933Z` (Ollama `created_at`). Its failed raw attempt is
preserved at
[`prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json`](prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json).
The V1 one-shot was closed; it produced no valid question or evaluation.

V2's separate preregistration and entry point were committed before inference:
`a87b631bc1b4237e950cbaf8abe4e1e4524cc652`. It used the same frozen qwen3:8b
digest (`sha256:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`),
`temperature=0.7`, `top_p=0.8`, `num_predict=512`, and explicit `think=false`.
The four registered calls succeeded:

| Question ID | Seed | Generation timestamp (UTC) |
|---|---:|---|
| `primary-video_memorability-v2` | 4900 | 2026-11-15T02:48:32.535975Z |
| `decoy-video_memorability-v2` | 4901 | 2026-11-15T02:48:41.246271Z |
| `primary-image_enhancement-v2` | 4910 | 2026-11-15T02:48:48.738181Z |
| `decoy-image_enhancement-v2` | 4911 | 2026-11-15T02:48:57.648800Z |

Raw generations, prompts, model/source provenance and attempt records are
preserved in
[`prospective_grounding/generated_v2/`](prospective_grounding/generated_v2/).
Two blinded packets and initially blank forms are in
[`prospective_grounding/human_review_v2/reviewer_1/`](prospective_grounding/human_review_v2/reviewer_1/review_packet.md)
and [`reviewer_2/`](prospective_grounding/human_review_v2/reviewer_2/review_packet.md);
the private mapping is not reviewer-facing. The packet forms remain unfilled.
Two separately supplied response files have since been preserved and compared
as exploratory evidence in
[`prospective_grounding/exploratory_evidence/`](prospective_grounding/exploratory_evidence/).
Each contains 18 ratings and six association checks. Reviewer 1 declares
independence, which is not externally verified; reviewer 2 declares
independence=false and the response is identified as AI-assisted. Ratings
agree on 17/18 pairs (unweighted κ=0.912); association decisions agree on all
six checks, with no field-level association disagreements. The only rating
difference is `primary-image_enhancement-v2` / `2412.20916v1` (reviewer 1: 2;
reviewer 2: 1). These responses do not satisfy the two-independent-review gate.
No registered V2 scores, baseline comparison, confidence interval or pass/fail
result exists. The registered original/empty/shuffled/decoy controls and `G`
versus `B-TF` comparison have not been scored.

For registered scoring, V2 still requires (a) two independent dated,
evidence-noted 0/1/2 ratings for every registered non-empty question-paper
pair, (b) two independent same-topic/unsupported validations for each decoy,
(c) validated construction of all registered conditions, and (d) explicit
scoring authorization. With only two question families, any eventual interval
will have very low resolution. V2 is not a completion or amendment of original
A1 and must not be pooled with V1.

Offline review-packet reproduction/checks, from the repository root:

```sh
python3 -m unittest M.prospective_grounding.tests.test_human_review_v2 -v
python3 -m M.prospective_grounding.human_review_v2.validate_packet
```

## Software verification

The full CPU test suite passed: **92 tests**. It checks implementation behavior,
data validation, failure gates, and fixture-level computations. It does not
validate scientific hypotheses or convert blocked data into experimental
evidence. See [`README.md`](README.md) for commands and
[`LIMITATIONS.md`](LIMITATIONS.md) for unresolved requirements.
