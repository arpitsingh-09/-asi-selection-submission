# Main Problem — research report and evidence status

## Research question and hypothesis

The Main Problem asks whether one time-bounded representation of a research
question and its explicitly supplied prior-work set can support useful
readouts for identity, novelty, relevance, research quality, diversity, and
temporal behavior. The preregistered directional hypotheses are that
paraphrases preserve readouts more than near misses; novelty readouts respond
to partial-coverage and concentration manipulations; relevance and novelty
signals survive length matching; quality readouts agree with independent
expert, reviewer, or outcome evidence beyond text baselines; within-seed
preference remains after system demeaning; and models trained to adjacent
cutoffs are equivalent within the specified tolerance.

These are hypotheses, not findings. The frozen implementation uses a shared
512-bin lexical hash representation and rule-based facets, not a trained
semantic encoder. Readouts include identity, novelty, groundedness/relevance,
quality, diversity, and temporal components. `B-TF` is train-only TF-IDF;
`B-LEN` is token count. The exploratory S1 analysis has saved E5 question-baseline outputs. Original S1 has cached MiniLM vectors, but its encoder cutoff and cohort eligibility remain unresolved. The
two quality targets—peer-review quality and later community use—have no
eligible dated, question-linked labels, so their heads remain untrained and
unavailable. A missing baseline or head blocks its comparison; it is not
replaced by the lexical proxy.

## Measured supplementary outcomes

| Comparison | Observed outcome | Interpretation |
|---|---|---|
| S1-style identity versus E5, 60 focal questions | Both classified all 60 minimal paraphrases as intended. On near misses, identity classified 9/60 as intended and E5 classified 0/60. The paired improvement was 15 percentage points (95% interval 6.7 to 25). | The paraphrase tie left the joint criterion unmet. The labels reflect creator intent on previously inspected questions. [Saved comparisons](supplementary_s1_e1_exploratory/results/run_001/results.json) |
| A1-style coverage and concentration, 16 targets grouped under two focal papers | Zero of four coordinates cleared the joint criterion. Y passed the concentration ordering for both papers and the coverage ordering for one. | The effective sample for uncertainty is two papers. These measurements identify a failed ordering within the sample and leave population performance uncertain. [Saved paired statistics](a1_replication/A1_STATISTICAL_RESULTS_V1.json) |

The original battery remains 0/9 complete.

## Frozen evaluation design

The controlling protocol is [`PREREG.md`](PREREG.md), with output contracts in
[`EVALUATION.md`](EVALUATION.md) and checksums in [`frozen/`](frozen/). The
temporal split is TRAIN through 2023, VALIDATION in 2024, an excluded gap from
2025-01-01 through 2025-06-30, and TEST from 2025-07-01 onward. Questions and
input versions must be available at the time posed; labels cannot predate the
question. Publication year alone does not establish question, version, or
outcome-observation time. No frozen TEST cohort was scored, and no TEST label
was used for fitting.

The frozen interval method is a paired percentile 95% cluster bootstrap with
2,000 draws and PCG64 seed `20261113`, retaining related records and conditions
together. No such intervals exist for blocked tests. Each evaluation has its
own pass rule; the battery passes only if
all nine criteria pass. Primary criteria and present blockers are summarized
below. The full machine-readable ledger is
[`results/stage5/results.json`](results/stage5/results.json).

Input-bearing tests require separate original, empty, shuffled, and
independently verified same-topic decoy conditions. Empty scores remain
undefined; controls are not averaged into the primary condition. Each test
also requires source-linked inputs, dated annotations or outcomes as
applicable, compatible frozen model/baseline artifacts, and verified temporal
eligibility before prediction and scoring.

These gates require an original primary condition, an explicitly empty
condition whose score remains undefined, inputs shuffled from another instance,
and an independently verified same-topic decoy that is unsupported by its
supplied papers. Conditions are reported separately, never averaged. Question
and input versions must be available when posed; labels cannot predate the
question. Publication dates alone do not establish those times. No heldout
tuning, post-test normalization, or use of later outcomes as features is
permitted.

| Test | Registered endpoint and pass criterion | Status and decisive blocker |
|---|---|---|
| I1 | Near-miss minus paraphrase drift; lower CI >0.02 for every head. | BLOCKED: original input links and independently checked controls are missing; fitted Q heads and frozen normalization are unavailable. |
| I3 | Preference-ranking improvement over B-LEN; lower CI >0.02 for each claimed Q/N coordinate. | BLOCKED: no eligible dated, length-matched preference labels linked to the frozen questions; Q heads unavailable. |
| S1 | Accuracy improvement over B-Q for near-miss and minimal-paraphrase decisions; both lower CIs >0.02. | Blocked before scoring. Of 122 candidate pairs across 61 questions, zero qualified. Question timing and original inputs remain unverified, zero questions have all four verified conditions, reviewer independence is unresolved, and the pinned encoder lacks a verified training cutoff. No accuracy difference or confidence interval was estimated. [Eligibility evidence](data/s1_review_v3/recovered_evidence_2026-11-19/S1_FINAL_EVIDENCE_HANDOFF_MANIFEST_2026-11-19.json) |
| A1 | Strict novelty-axiom pass fraction; one coordinate must have lower CI ≥0.80 for both partial coverage and concentration. | BLOCKED: existing E2 work is not a prospective M cohort; no eligible new heldout cohort with verified original inputs and required controls. |
| H1 | Length-matched preference concordance over B-Q after system demeaning; lower CI >0.02. | BLOCKED: no eligible dated, source-bound battles with seed/system links; Q heads and compatible B-Q predictions are unavailable. |
| H3 | Q–review-score correlation improvement over B-Q; lower CI >0.02, with independent human-ceiling share. | BLOCKED: no post-cutoff question/review/date links, numeric reviewer outcomes, independent ceiling, Q heads, or semantic baseline. |
| O1 | Within-topic concordance over B-Q for both quality factors; both lower CIs >0.02. | BLOCKED: no eligible dated peer-review and community-use outcomes linked to questions; both Q heads unavailable. |
| O2 | Within-identical-seed outcome ranking improvement over question-text B-TF; lower CI >0.02. | BLOCKED: no verified identical supplied seed sets of at least three papers and dated outcome links; zero eligible pairs. |
| T1 | Difference between frozen ≤2022 and ≤2023 model head scores; upper CI ≤0.02 for every head. | BLOCKED: separately trained, prospectively frozen year-specific models, normalized predictions, and input controls are absent. |

## Design variables, controls, and threats

The registered design treats the question and its supplied literature at time
`t` as the unit of representation. The prespecified contrasts and cohort
dimensions are test-specific: paraphrase versus near-miss edits (I1/S1),
length-matched pairs (I3), novelty coverage and concentration manipulations
(A1), expert pair preferences (H1), dated reviewer outcomes (H3), later
quality/community-use outcomes (O1), shared input-paper sets (O2), and adjacent
training cutoffs (T1). Outcomes are the
readout-specific score, relation decision, ranking/concordance, axiom pass, or
time difference defined in the frozen protocol. Quality factors are separate;
they are not collapsed into a single target.

For input-bearing registered rows, original, empty, cross-instance shuffled,
and independently verified same-topic decoy conditions are separate
diagnostics; the empty score is undefined and conditions are never averaged.
Registered baselines are B-Q/B-ABS where applicable, B-TF, and B-LEN; unavailable
semantic vectors are a blocker, not permission to substitute lexical scores.
Uncertainty is paired percentile 95% cluster bootstrap with 2,000 draws and
PCG64 seed `20261113`, resampling the preregistered independent unit while
keeping associated conditions together. The small supplementary A1 uses two
focal-paper clusters, so its intervals are highly discrete and weakly
generalizable.

The principal threats are construct validity of lexical identity/facet proxies,
exposure and unverified creator-intended labels in S1, the two-cluster A1
sample, incomplete input/decoy controls, missing question and label observation
dates, and absent semantic/quality heads. These threats explain why the saved
supplements are descriptive/exploratory and why no positive core claim is
reported.

**Original registered result: 0/9 complete, all blocked.** This is an absence
of eligible evaluations, not a negative result about the hypotheses. The O2
cache found 41 bibliography-overlap pairs, but no pair met the preregistered
rule requiring identical, explicitly supplied input-paper IDs. Bibliography
overlap cannot recover a question’s supplied inputs. The quality archive
contains 570 recommendation values, but zero eligible question-linked labels
with verified public observation dates; no quality model was fitted.
Targeted acquisition also found no exact frozen TRAIN submission; an OpenReview
request for a frozen VALIDATION review returned HTTP 403. The checked PeerRead
records did not establish exact cohort labels, reviewer identity, or compatible
reuse licensing, so none were imported. The saved acquisition evidence is in
[`data/quality_acquisition_v1/`](data/quality_acquisition_v1/).

## Supplementary A1 partial replication

This is a separate, exposed E2-informed replication, not original A1 and not an
independent confirmatory test. It uses the SPECTER2 base model with the
proximity adapter and the existing E2 novelty implementation. Claims were
extracted from title-plus-abstract text by the amended, hash-identified
qwen3:8b `atomic-claims-v8` run; an earlier DeepSeek-R1 preflight was blocked
before inference. The two scored focal papers have claim/source judgments
from reviewer `AS-01`, dated 2026-11-14, with a separate independence
attestation. The 50-paper extraction cohort is broader: the saved validation
record marks 43 papers as lacking independently verified semantic review. The
extractor manifest, validation, reviewed forms, and readiness record are
preserved under [`a1_replication/`](a1_replication/). Its operational
input pool comes from the E2 pool manifest, not recovered author-supplied
references. The analysis retained two independently reviewed focal-paper
clusters (`2512.23709v3`, `2610.29385v1`) and 16 scored nonempty targets.

Per focal paper, scored conditions were the original-pool reference,
25/50/75/100% coverage, concentrated, distributed, and shuffled. The original
pool is an internal manipulation reference, not an external model baseline;
no B-Q/B-ABS/B-TF comparator was used. Original and shuffled targets were
scored; shuffled is diagnostic only. Empty-pool outputs remain undefined. The
same-topic decoy was unavailable and excluded under approved Amendment 003,
so the full mandatory four-condition suite is absent. The operational pool
came from the E2 manifest, not recovered author-supplied references. Analysis
used paired focal-paper cluster bootstrap (2,000 draws, PCG64 seed `20261113`).

| Coordinate | Partial-coverage strict pass fraction (95% CI) | Concentration strict pass fraction (95% CI) |
|---|---:|---:|
| Y | 0.500 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| density | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| N | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| yours | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |

The supplementary rule required a lower 95% CI bound ≥0.80 for the same
coordinate under both manipulations; none qualified. With two clusters, the
intervals are discrete and unstable. This exposed negative threshold result
does not establish broad model failure or success. Source artifacts are in
[`a1_replication/`](a1_replication/): the
[supplementary registration](a1_replication/PREREG_REPLICATION.md),
[approved partial-controls amendment](a1_replication/AMENDMENT_003_PARTIAL_CONTROLS.md),
[cohort manifest](a1_replication/cohort_manifest.json),
[saved scores](a1_replication/A1_SCORING_RESULTS_V1.json),
[statistical findings](a1_replication/A1_STATISTICAL_FINDINGS_V1.md), and
[saved statistics](a1_replication/A1_STATISTICAL_RESULTS_V1.json).

The failure is not only sample size: coverage requires four ordered decreases.
For `density`, saved mean deltas for 50-to-75% and 75-to-100%
coverage are both exactly 0.000 [0.000, 0.000], and strict coverage passes in
0/2 clusters. Its concentration direction is reversed (distributed minus
concentrated = -13.5, 95% CI [-19, -8]). `Y` passes concentration in both
clusters, but coverage in only one of two. No coordinate passes the joint rule.

Concentration mean paired deltas (distributed minus concentrated, 95% CI) were
Y +0.0108 [0.0076, 0.0140], density -13.5 [-19, -8], N -0.0575
[-0.0594, -0.0556], and `yours` -0.0063 [-0.0092, -0.0034]. These describe
the two observed focal papers, not population-level effects. Shuffled-minus-
original diagnostic effects were positive on all four coordinates (Y +0.0339,
density +22.5, N +0.0117, `yours` +0.0284); this has no registered directional
criterion and cannot replace the missing decoy.

The scoring record identifies `specter2_base` revision
`3447645e1def9117997203454fa4495937bfbd83` with the `allenai/specter2`
proximity adapter revision `2081559630a80fc5851d8f798a05ba81e9468089`, CLS
pooling, and offline local weights. It records inference from 16:42:20Z to
16:44:52Z on 2026-11-14, but no hardware or accelerator; no compute-cost or GPU
claim is made. Full model and input hashes are in the saved scoring JSON.

## Supplementary S1 exploratory analysis (not original S1)

The separate exploratory S1 analysis used 60 source questions, giving 60
minimal-paraphrase and 60 near-miss pairs. E1 creator-intended labels have no
independent second-reader confirmation. Candidate h004 was excluded because
its source-publication date was 2025-01-22, before the supplementary cutoff of
2025-07-01; this does not establish question-posing time. Against unverified E1
author-intended labels, identity accuracy was 1.00 (60/60) for minimal
paraphrases and 0.15 (9/60) for near misses; `B-Q` accuracy was 1.00 (60/60)
and 0.00 (0/60), respectively. The paired identity-minus-`B-Q` accuracy
differences were 0.00 (95% CI [0.00, 0.00]) for minimal paraphrases and 0.15
(95% CI [0.0667, 0.25]) for near misses. Intervals use 2,000 paired
source-question bootstrap draws (PCG64 seed 20261113). The overall criterion
required both lower bounds to exceed 0.02; it failed because the
minimal-paraphrase comparison did not clear the margin. The E1 data were
exposed and labels are unverified, so this is exploratory only. Original S1
remains incomplete and is not replaced by this analysis. Its saved result is
[`supplementary_s1_e1_exploratory/results/run_001/results.json`](supplementary_s1_e1_exploratory/results/run_001/results.json).
Original A1 also remains incomplete: all 80 frozen candidates are ineligible.

For h001, M identity similarity was 0.7509 and E5 cosine 0.9736, both above
the fixed 0.65 “same” threshold, against an unverified creator-intended
“different” label. h003 shows the same error pattern (0.7593 and 0.9935).
Across the 60 near-misses,
M produced 51 false positives and E5 classified all 60 as same. This is
observed threshold behavior against unverified labels, not verified semantic
error. E5 was `intfloat/e5-base-v2`, revision
`f52bf8ec8c7124536f0efb74aca902b2995e5bcd`; the saved run used CPU, the fixed
`query: ` prefix, and L2 normalization. It remains exploratory, not evidence
that original S1 passed.

## Prospective grounding pilot: generation and exploratory reviews

Separate from the nine tests and A1, V1's first Qwen3 call returned an empty
answer after its 512-token thinking budget was exhausted; it was preserved and
not retried. Separately preregistered V2 completed four generations: two
primaries and two same-family decoys, using `qwen3:8b`, `think=false`, and
seeds 4900/4901/4910/4911. Raw calls and source provenance are in
[`prospective_grounding/generated_v2/`](prospective_grounding/generated_v2/).
Hardware/energy use was not recorded.

The registered blinded review forms remain blank. Separate exploratory response
files contain 18 ratings and six association checks each: six primary/original
pairs, six cross-family shuffled pairs, six decoy pairs; empty has no score or
rating. These are not two independent human reviews: reviewer 1's independence
is unverified and reviewer 2 disclosed AI assistance/non-independence. Their
17/18 rating agreement (κ=.912 unweighted, .927 weighted) and 6/6 association
agreement are descriptive only. Both marked both decoys same-topic, but only
the video decoy unsupported; the image decoy was marked supported by its papers.
V2's planned `MAE(B-TF)-MAE(G)` endpoint, 2,000-family-bootstrap interval, and
pass rule were never computed. No registered V2 evaluation was completed; it
still needs independent dated ratings, valid decoys/conditions, and scoring
authorization. Sources are preserved in
[`prospective_grounding/exploratory_evidence/`](prospective_grounding/exploratory_evidence/).

## Scientific interpretation and limitations

The evidence supports narrow conclusions about the measured artifacts, not a
general claim that the representation identifies good research questions:

* In the exposed S1-style sample, identity matched the creator-intended labels
  on near-misses more often than `B-Q` (difference +0.15, 95% CI [0.0667,
  0.25]), but tied `B-Q` on minimal paraphrases (difference 0.00, [0.00,
  0.00]). The registered-style two-category rule therefore failed. Since the
  labels are unverified and the examples were exposed, this is a diagnostic of
  threshold behavior, not verified semantic performance.
* In the two-paper A1 partial replication, no novelty coordinate met the joint
  coverage-and-concentration criterion. `Y` passed concentration on both
  papers but coverage on only one; density had two zero late-coverage changes
  and a concentration effect opposite the expected direction. This suggests
  different coordinates respond differently to pool construction in these
  examples; it does not establish population behavior.
* The grounding pilot has no eligible model-versus-baseline outcome comparison.
  The exploratory review responses agree descriptively, but one reviewer was
  AI-assisted and declared non-independence; both also judged the image decoy
  supported by its supplied papers. The review evidence therefore does not
  validate that decoy or satisfy the independent-review gate.
* In the six-question development readout, mean pairwise cosine distance,
  Vendi, and class entropy were identical across the saved original, empty,
  and shuffled-input conditions (0.64548, 4.69981, and 1.79176,
  respectively). This is a warning that these lexical diversity statistics
  did not respond to those input changes in that small fixture; there was no
  same-topic decoy or human validation. See
  [`results/generated_development_v4/summary.md`](results/generated_development_v4/summary.md).

No feature of a “good question” has been validated on held-out years. The
registered battery has no eligible results, so it cannot establish either
success or failure of the six readouts. Software tests validate implementation
paths, not the hypotheses. Paper publication dates cannot substitute for
question, input-version, or outcome-observation dates. No dates or labels were
imputed, and exposed E2 evidence was not promoted into original A1. The
two-cluster A1 and two-family grounding sample sharply limit generalization.

### Cross-experiment interpretation of the saved diagnostics

The supplementary artifacts suggest specific failure checks for a future
eligible study. These are post hoc lessons from exposed or small samples; they
do not revise the frozen hypotheses or count as held-out validation.

| Observed evidence | Narrow inference | What it does not establish |
|---|---|---|
| In exploratory S1, M tied `B-Q` on the 60 minimal paraphrases and exceeded it by 0.15 on the 60 near-misses, against exposed, unverified E1 intent labels. | Keep paraphrase stability and near-miss discrimination as separate outcomes; a good near-miss contrast cannot compensate for a failed paraphrase criterion. | Verified semantic accuracy, prospective generalization, or original S1 completion. Source: [`supplementary_s1_e1_exploratory/results/run_001/results.json`](supplementary_s1_e1_exploratory/results/run_001/results.json). |
| In A1, `density` had zero change in the final two coverage steps and a reverse concentration effect; `Y` passed concentration on both papers but coverage on one. | Report novelty coordinates separately and inspect saturation and direction reversals instead of pooling coordinates. | Population-level coordinate behavior; there are only two focal-paper clusters and the full control suite is incomplete. Source: [`a1_replication/A1_STATISTICAL_RESULTS_V1.json`](a1_replication/A1_STATISTICAL_RESULTS_V1.json). |
| The six-question development fixture had identical saved diversity values across original, empty, and shuffled conditions. | Test explicitly whether each diversity readout responds to input changes; identical values are a sensitivity warning in this fixture. | General input insensitivity or a registered negative result. Source: [`results/generated_development_v4/results.json`](results/generated_development_v4/results.json). |
| In exploratory grounding review, both reviewers marked the image decoy as same-topic and supported by its supplied papers. Reviewer independence was not established for both. | Same-topic relevance and unsupportedness must be checked as separate control properties. | Valid independent human confirmation or satisfaction of the registered decoy gate. Source: [`prospective_grounding/exploratory_evidence/analysis_2026-11-15/results.json`](prospective_grounding/exploratory_evidence/analysis_2026-11-15/results.json). |

These diagnostics make the limitations concrete, but none validates a named
feature of “good questions” on held-out years—the rubric’s stronger insight
criterion remains unmet.

## Rubric coverage and evidence boundary

The assignment rubric awards marks across six categories. This table maps the
submission evidence to those requirements; it is not a prediction of the
marker’s score.

| Rubric category | Requirements supported by this submission | Status and material gap |
|---|---|---|
| Research design (15) | A clear question and directional hypotheses; one shared, time-bounded `Φ(q,R,t)`; separate readout contracts; temporal splits, controls, baselines, cluster units, bootstrap method, and frozen thresholds are specified in [`PREREG.md`](PREREG.md) and [`EVALUATION.md`](EVALUATION.md). | Documented, but the report does not trace every design choice to findings from T1–T5/E1–E6; most readouts lack eligible held-out validation. The current implementation is a lexical/rule prototype rather than a validated semantic representation. |
| Evaluation battery (25) | All nine required core tests are individually listed with their criteria and blockers; time, leakage, controls, and resampling requirements are documented. | **0/9 complete.** No extended test was completed. Each blocker is reported rather than replaced with a proxy. |
| Experimental results (20) | Saved supplementary A1 and exposed S1-style analyses include observed outcomes, baselines where applicable, paired confidence intervals, and failure cases; the exploratory grounding review comparison is labeled non-independent. | No registered core result or well-powered held-out result exists. The supplements do not meet the rubric’s demand for eligible held-out post-cutoff results or a decisive, well-powered negative result. |
| Research insights (20) | The report names where identity and `B-Q` agree or differ, where novelty coordinates fail their joint rule, and where the decoy review exposed a control weakness. | These are limited, exposed examples. No good-question feature is validated on held-out years, and no broad system-quality conclusion is supported. |
| Reproducibility and reuse (10) | The README describes setup, interfaces, schemas, frozen files, and offline checks; this report links saved outputs, hashes, and analysis scripts. | Reproduction is strongest for software and saved supplementary statistics. Missing eligible cohorts and model artifacts prevent reproducing any registered evaluation; hardware/energy metadata are incomplete for some supplementary runs. |
| Integrity (10) | The preregistration and amendments are identified; AI assistance and a caught implementation error are disclosed in [`AI_USAGE.md`](AI_USAGE.md); the failed V1 generation and unresolved review evidence are retained in [`NOTEBOOK.md`](NOTEBOOK.md). Deviations and non-independent judgments are labeled. | The report cannot claim every rubric item is satisfied: human reviews and historical links remain missing, and the core battery was not run. No score or admission outcome is inferred. |

The strongest supported submission is therefore the implementation, its
reproducible software checks, transparent failure accounting, and narrowly
bounded supplementary findings. The evidence does not establish the Main
Problem’s required core empirical claims or guarantee the 45-point admission
threshold.

## R1–R5 integrity crosswalk

| Requirement | Evidence in `M/` | Assessment |
|---|---|---|
| R1 — log AI use and a genuine error caught | The submission-level [`AI_LOG.md`](../AI_LOG.md) incorporates Main Problem assistance and errors. The scoped [`AI_USAGE.md`](AI_USAGE.md) records the future-paper availability error and future-annotation leak; it links the latter to `test_future_answer_annotation_is_removed_not_just_hidden_by_head`. [`NOTEBOOK.md`](NOTEBOOK.md) records execution failures and recovery attempts. | Documented across linked records. The exact earlier-arrival crash has no dedicated regression test, and the cited 92-test suite was not rerun during this report work. The errors are not represented as scientific validation. |
| R2 — preregister before evaluation; preserve prior Git evidence | [`GIT_HISTORY_EVIDENCE.md`](GIT_HISTORY_EVIDENCE.md) records the original M preregistration commit, amendment commits, parent links, and bundle verification. The original nine-test battery was not executed. The supplementary A1 commit timestamp precedes its saved inference start by about 4 hours 16 minutes. | Internally supported, with caveats: the A1 registration retains a contradictory status sentence. The dated [A1 status clarification](a1_replication/A1_PREREG_STATUS_CLARIFICATION_2026-11-19.md) reconciles it with the committed authorization and run record without changing them. Git timestamps and author identity are not externally attested. The bundle supports commit-object chronology, not public availability or scientific adherence. |
| R3 — report negative results honestly | The original battery is reported as 0/9; supplementary S1 and A1 fail their joint criteria; V2 has no scored outcome comparison; the development diversity measures are identical across recorded input conditions. | Documented. No blocked outcome is recast as a negative registered test. |
| R4 — respect temporal cutoffs | [`PREREG.md`](PREREG.md) specifies TRAIN through 2023, VALIDATION in 2024, the first-half 2025 gap, and TEST from 2025-07-01. Unknown question, version, and label dates remain blockers. | Rules are explicit and unknown dates were not imputed. Since no original held-out evaluation ran, empirical temporal validity is not demonstrated; supplements are separately labeled. |
| R5 — respect and report small-compute use | The default M representation and cached MiniLM preparation use recorded CPU paths; the MiniLM cache records one thread, batch size 4, PyTorch 2.8.0, and 0.8069 seconds for its encoding loop. The exploratory E5 run records CPU execution. | Partial. The MiniLM timing is vector preparation, not a full question evaluation or the assignment’s one-GPU target. A1 hardware details are absent; V2 hardware and energy were not recorded. No tier is inferred for those runs. |

These requirements are reported separately because a transparent limitation is
not evidence that the corresponding requirement was fully satisfied.

## Reproducibility

The ledger and reported statistics refer to saved artifacts; this report work
reran no experiment or inference. Key SHA-256s: stage-5 ledger
`3e169c4179b7a786fd1e2a0da919184e76a4d0fb4426dd29b23f9caafc681474`; A1
scores `40f564c94801395fd327b1849d457515dab6e7d4f0901fb3960d91c9f358b4ff`;
A1 statistics `7aff25e53986a78145610b3bc0e9a352364987adccac1cf9003b48310a991c4c`;
exploratory S1 result `edd827ff7dd8cfebde154ac156834e50a2e9a0e40f9d5357d8caa181b86d71e5`.
Frozen-file checksums are in `frozen/SHA256SUMS.json` (file SHA-256
`e7ec110b355e9107f65a02e63c371d0342c24d3c1798c40c126bdd385cc06178`).
From the repository root, these commands reproduce saved calculations or
check offline materials:

```sh
# Reproduce the saved supplementary A1 statistics in memory; writes no files.
python3 -B -c 'import json,pathlib; from M.a1_replication.analyze_a1_results import analyze; p=pathlib.Path("M/a1_replication"); r=json.loads((p/"A1_SCORING_RESULTS_V1.json").read_text()); s=json.loads((p/"A1_STATISTICAL_RESULTS_V1.json").read_text()); assert {k:v for k,v in s.items() if k!="provenance"} == analyze(r)'

# Recompute the V2 exploratory comparison in memory; writes no files.
python3 -B -c 'from M.prospective_grounding.exploratory_evidence.compare_review_responses import validate_and_compare; r, _, _ = validate_and_compare(); a=r["rating_agreement"]; b=r["association_agreement"]; assert (a["exact_agreement_n"],b["joint_decision_agreement_n"])==(17,6) and abs(a["cohen_kappa_unweighted"]-0.912)<0.0005 and abs(a["cohen_kappa_linear_weighted"]-0.927)<0.0005'

# Display the exact saved S1-style metrics; this reads results and does no inference.
python3 -B -c 'import json; from pathlib import Path; p=Path("M/supplementary_s1_e1_exploratory/results/run_001/results.json"); print(json.dumps(json.loads(p.read_text())["metrics"], indent=2))'

# Focused offline validation of the exploratory comparison.
python3 -B -m unittest M.prospective_grounding.tests.test_exploratory_review_pair -v

# Check the frozen V2 reviewer packet (this does not score the evaluation).
python3 -m unittest M.prospective_grounding.tests.test_human_review_v2 -v
python3 -m M.prospective_grounding.human_review_v2.validate_packet
```

The original nine-test protocol is [`PREREG.md`](PREREG.md); the separate V2
generation and scoring protocol is
[`prospective_grounding/PREREG_V2.md`](prospective_grounding/PREREG_V2.md).
The full CPU suite’s previously recorded 92 passing tests validate
implementation behavior and fixtures, not scientific performance. The frozen
M implementation has no trained Q head. S1 records CPU execution and E5
revision/file hashes; A1 records local model revisions and weight hashes but
not hardware. V2 records its Qwen3 digest/settings but not hardware or energy.
No compute use is inferred where the artifacts do not report it.

During this submission audit on 2026-11-19 the available environment was CPython
3.9.6, macOS arm64, and NumPy 2.0.2. [`requirements-core.txt`](requirements-core.txt)
pins NumPy for the standard-library/NumPy core paths; it does not recreate the
historical model-run environments. The 11 entries in
[`frozen/SHA256SUMS.json`](frozen/SHA256SUMS.json) were checked against their
current files and all matched. The saved B-Q preparation record
[`data/s1_review_v3/minilm_vectors.json`](data/s1_review_v3/minilm_vectors.json)
binds 183 384-dimensional vectors to model revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41` and model-file hashes; it explicitly
marks the model training cutoff unverified, so these vectors do not unlock S1.
The dated manifest summary is
[`data/manifests_v2/manifest_report.json`](data/manifests_v2/manifest_report.json)
(25 TRAIN, 2 VALIDATION, 80 metadata-only TEST candidates; SHA-256
`b2fb0bb6aa4f69118465306f117e2ecde7456d2acc3660d20ede26d3a87572cf`). Its
zero eligible label counts are consistent with the frozen quality-readiness
report. The supplied checkout does not contain the historical commit objects
referenced by its amendments; content hashes establish present-byte integrity,
not commit chronology.

## AI use and submission status

AI assistance and the caught Main Problem implementation errors are recorded
in the submission-level [`AI_LOG.md`](../AI_LOG.md) and scoped
[`AI_USAGE.md`](AI_USAGE.md); dated failures and evidence-recovery limits are
also retained in [`NOTEBOOK.md`](NOTEBOOK.md). Qwen3 use and the AI-assisted
exploratory review are disclosed in those records and in the grounding report.
The V1 empty response is preserved; no question, label, date, or result was
invented.

The submission contains nine blocked core evaluations, the limited A1 negative
threshold result, and V2 generations without a scored result. These supplements
remain separate from the original battery. The table above gives each original
test's remaining source, time, label, control, model, or baseline blocker.
The assignment's admission rule is at least 45/100 overall and at least 6/10
for Integrity; its core tests are required, and an unrun test must be listed
with its reason. The planning totals supplied by the applicant are not earned
marks or evidence that either threshold has been met.
