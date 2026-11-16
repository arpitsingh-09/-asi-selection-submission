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

The separate S1-style exploration used 60 source questions, yielding 60
minimal-paraphrase pairs and 60 near-miss pairs (120 decisions). One candidate,
h004, was excluded because its source publication date was 2025-01-22, before
the 2025-07-01 source-date cutoff. This date filter does not establish when a
question was posed. Labels are E1 creator-intended assignments; the saved
records have no independent second-reader confirmation. E1 and its predictions
were already exposed, so these are not human-ground-truth or confirmatory
results. Identity accuracy was 60/60 (1.00) for minimal paraphrases and 9/60
(0.15) for near misses; semantic `B-Q` (`intfloat/e5-base-v2`) was 60/60 (1.00)
and 0/60 (0.00). Paired identity-minus-B-Q differences were 0.00 (95% CI
[0.00, 0.00]) and +0.15 (95% CI [0.0667, 0.25]), respectively. Intervals use
2,000 paired source-question bootstrap draws (PCG64 seed 20261113). The
two-category rule failed because the minimal-paraphrase lower bound did not
exceed 0.02. Original S1 remains incomplete; all 80 frozen A1 candidates remain
ineligible. See the saved artifact at
[`supplementary_s1_e1_exploratory/results/run_001/results.json`](supplementary_s1_e1_exploratory/results/run_001/results.json).

Representative label-relative errors: on h001, identity similarity was
0.7509 and E5 cosine 0.9736, both above the fixed 0.65 “same” threshold, while
the creator-intended label was “different.” On h003 the corresponding scores
were 0.7593 and 0.9935 with the same intended label. Across the 60 near misses,
identity produced 51 false positives and E5 labeled all 60 “same.” These are
errors against unverified author intent, not independently established semantic
errors. E5 used revision `f52bf8ec8c7124536f0efb74aca902b2995e5bcd`, CPU
execution, the fixed `query: ` prefix, and L2 normalization.

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
and shuffled. The original full pool is the within-focal reference condition,
not an external model baseline; no B-Q/B-ABS/B-TF model comparison was run for
these novelty axioms. The E2 novelty implementation and SPECTER2 proximity
adapter produced the saved scores. Each focal paper had one scored target per
condition (16 total). Empty-pool scores remained undefined. The shuffled
condition was scored once per focal paper and is diagnostic only. The
same-topic decoy was unavailable and unscored under approved Amendment 003.
Thus original and shuffled observations exist, empty is correctly undefined,
but the complete mandatory four-condition suite is not present. The pool was
operationally sourced from the E2 pool manifest, not recovered author-supplied
references. Analysis used paired focal-paper cluster bootstrap (2,000 draws,
PCG64 seed `20261113`).

| Coordinate | Coverage pass fraction (95% CI) | Concentration pass fraction (95% CI) |
|---|---:|---:|
| Y | 0.500 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| density | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| N | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| yours | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |

The saved paired effect estimates (left score minus right score; positive is
the registered direction) show where the coverage rule failed:

| Coordinate | Full pool→25% | 25→50% | 50→75% | 75→100% |
|---|---:|---:|---:|---:|
| Y | +0.0251 [0.0150, 0.0353] | +0.0007 [-0.0017, 0.0032] | +0.0071 [0.0049, 0.0093] | +0.0008 [-0.0013, 0.0028] |
| density | +2.5 [1, 4] | +0.5 [0, 1] | 0 [0, 0] | 0 [0, 0] |
| N | +0.0101 [0.0085, 0.0116] | -0.0003 [-0.0030, 0.0025] | +0.0011 [-0.0015, 0.0038] | +0.0008 [-0.0012, 0.0027] |
| yours | +0.0214 [0.0134, 0.0294] | +0.0005 [-0.0021, 0.0030] | +0.0056 [0.0033, 0.0079] | +0.0008 [-0.0012, 0.0028] |

Concentration mean paired deltas (distributed minus concentrated, 95% CI) were
Y +0.0108 [0.0076, 0.0140], density -13.5 [-19, -8], N -0.0575
[-0.0594, -0.0556], and `yours` -0.0063 [-0.0092, -0.0034]. Strict
concentration passes were respectively 2/2, 0/2, 0/2, and 0/2. The saved
original-versus-shuffled mean diagnostic deltas were Y +0.0339 [0.0323,
0.0355], density +22.5 [9, 36], N +0.0117 [0.0107, 0.0127], and `yours`
+0.0284 [0.0269, 0.0298]; this comparison has no registered directional
criterion and is not evidence of control success.

No coordinate met the supplementary threshold: the same coordinate needed a
lower 95% confidence bound ≥0.80 for both coverage and concentration. For
example, density's last two coverage deltas were exactly zero and its
concentration effect was in the reverse direction in both focal papers. Y
passed concentration in both papers but its coverage strict-pass fraction was
1/2. The bootstrap resamples only two clusters, so intervals are discrete and
cannot support broad population inference; the negative threshold finding is
limited to this exposed supplementary partial analysis. It does not complete
or replace original A1. See
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
`a87b631bc1b4237e950cbaf8abe4e1e4524cc652`. Its saved `run_complete.json`
records `COMPLETE_4_OF_4`: two primary and two same-family decoy generations,
using frozen Qwen3 digest
`sha256:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`,
`temperature=0.7`, `top_p=0.8`, `num_predict=512`, and `think=false`.

| Question ID | Seed | Generation timestamp (UTC) |
|---|---:|---|
| `primary-video_memorability-v2` | 4900 | 2026-11-15T02:48:32.535975Z |
| `decoy-video_memorability-v2` | 4901 | 2026-11-15T02:48:41.246271Z |
| `primary-image_enhancement-v2` | 4910 | 2026-11-15T02:48:48.738181Z |
| `decoy-image_enhancement-v2` | 4911 | 2026-11-15T02:48:57.648800Z |

Raw generations and source provenance are preserved under
[`prospective_grounding/generated_v2/`](prospective_grounding/generated_v2/).
The registered blinded packets have two blank forms with 18 rating rows and
six association rows each. Separately supplied exploratory responses fill
those rows. Their 18 pairs per reviewer comprise six primary/original pairs,
six cross-family shuffled pairs for the two primaries, and six same-family
decoy pairs. The empty condition has no numeric score or paper-rating
observation. These are reviewer observations, not model scores.

Reviewer 1 self-declared independence, which is not externally verified;
reviewer 2's form is AI-assisted and declares non-independence. Their 17/18
rating agreement (unweighted κ=0.912, linear-weighted κ=0.927) and 6/6
association agreement are descriptive only, not two independent human
judgments. The single rating disagreement is for
`primary-image_enhancement-v2` / `2412.20916v1` (2 vs. 1). Both responses judge
both decoys same-topic, but both judge the image-enhancement decoy as supported
by its supplied papers (unsupported=false); only the video-memorability decoy
is marked unsupported by both. Thus the image decoy fails its registered
unsupportedness check even descriptively. No condition-level G/B-TF scores,
MAE comparison, interval, or V2 pass/fail result exists; registered scoring
was not authorized or run.

For registered scoring, V2 still needs two independent dated, evidence-noted
ratings per nonempty pair, two independent same-topic/unsupported checks per
decoy, validated conditions, and explicit authorization. With two question
families, any interval would have very low resolution. V2 does not complete or
amend original A1 and is not pooled with V1.

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
