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
`B-LEN` is token count. Semantic `B-Q`/`B-ABS` artifacts are unavailable. The
two quality targets—peer-review quality and later community use—have no
eligible dated, question-linked labels, so their heads remain untrained and
unavailable. A missing baseline or head blocks its comparison; it is not
replaced by the lexical proxy.

## Frozen evaluation design

The controlling protocol is [`PREREG.md`](../M/PREREG.md), with output contracts in
[`EVALUATION.md`](../M/EVALUATION.md) and checksums in [`frozen/`](../M/frozen/). The
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
[`results/stage5/results.json`](../M/results/stage5/results.json).

These gates require an original primary condition, an explicitly empty
condition whose score remains undefined, inputs shuffled from another instance,
and an independently verified same-topic decoy that is unsupported by its
supplied papers. Conditions are reported separately, never averaged. Question
and input versions must be available when posed; labels cannot predate the
question. Publication dates alone do not establish those times. No heldout
tuning, post-test normalization, or use of later outcomes as features is
permitted.

### Evidence status

The report separates four evidence classes. The original frozen battery is
still **0/9 eligible or executed**. The supplementary A1 run is separately
registered and amended, scored on two clusters, and fails its joint threshold;
it is exposed and partial. The E1-based S1 analysis and V2 review-response
comparison are exploratory/post-hoc and cannot satisfy original S1 or V2
scoring. The remaining core tests and the preregistered V2 outcome comparison
are blocked or incomplete. These labels do not upgrade a frozen status when a
supplement exists.

| Test | Registered endpoint and pass criterion | Status and decisive blocker |
|---|---|---|
| I1 | Near-miss minus paraphrase drift; lower CI >0.02 for every head. | BLOCKED: original input links and independently checked controls are missing; fitted Q heads and frozen normalization are unavailable. |
| I3 | Preference-ranking improvement over B-LEN; lower CI >0.02 for each claimed Q/N coordinate. | BLOCKED: no eligible dated, length-matched preference labels linked to the frozen questions; Q heads unavailable. |
| S1 | Accuracy improvement over B-Q for near-miss and minimal-paraphrase decisions; both lower CIs >0.02. | BLOCKED: alignments lack independent confirmation; question dates, original input/control links, and verified model cutoff are missing. |
| A1 | Strict novelty-axiom pass fraction; one coordinate must have lower CI ≥0.80 for both partial coverage and concentration. | BLOCKED: existing E2 work is not a prospective M cohort; no eligible new heldout cohort with verified original inputs and required controls. |
| H1 | Length-matched preference concordance over B-Q after system demeaning; lower CI >0.02. | BLOCKED: no eligible dated, source-bound battles with seed/system links; Q heads and compatible B-Q predictions are unavailable. |
| H3 | Q–review-score correlation improvement over B-Q; lower CI >0.02, with independent human-ceiling share. | BLOCKED: no post-cutoff question/review/date links, numeric reviewer outcomes, independent ceiling, Q heads, or semantic baseline. |
| O1 | Within-topic concordance over B-Q for both quality factors; both lower CIs >0.02. | BLOCKED: no eligible dated peer-review and community-use outcomes linked to questions; both Q heads unavailable. |
| O2 | Within-identical-seed outcome ranking improvement over question-text B-TF; lower CI >0.02. | BLOCKED: no verified identical supplied seed sets of at least three papers and dated outcome links; zero eligible pairs. |
| T1 | Difference between frozen ≤2022 and ≤2023 model head scores; upper CI ≤0.02 for every head. | BLOCKED: separately trained, prospectively frozen year-specific models, normalized predictions, and input controls are absent. |

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
[`data/quality_acquisition_v1/`](../M/data/quality_acquisition_v1/).

## Design decisions linked to evidence

| Architecture decision | Mathematical or protocol rationale | Control / implementation check | Evidence and observed limit |
|---|---|---|---|
| One immutable shared snapshot `Phi` feeds all heads. | The stored feature is `[q, c, q−c, f_p, f_m, f_e, f_d, s]` (dimension `7d+7`): question, mean input context, their difference, four facets, and seven scalars. This makes readouts share evidence and permits snapshot hashing. | Original, empty, shuffled, and decoy inputs remain separate; snapshot validation rejects a changed fingerprint. | [`M/engine.py`](../M/engine.py), [`M/schema.py`](../M/schema.py), [`M/tests/test_space.py`](../M/tests/test_space.py). This is a lexical hash representation with rule-based facets; shared construction is not semantic-accuracy evidence. |
| Every snapshot is bounded by its as-of time. | A reference is usable only when `published < t` and `available_at ≤ t`; training text is also capped at the frozen cutoff. This represents the information available then rather than inferring it from venue year. | Synthetic checks cover future/equal-date inputs, later versions, future answer annotations, and immutable old snapshots. | `test_explicit_future_equal_date_and_unavailable_inputs_rejected`, `test_future_answer_annotation_is_removed_not_just_hidden_by_head`, and `test_temporal_update_preserves_old_snapshot_and_has_no_later_leakage`. These tests do not verify historical source dates. |
| Retrieval is bounded and explicit. | If `R` is absent, the implementation retrieves at most three cosine-nearest eligible local papers; the snapshot records a top-128 literature scope. This bounds cost but cannot support a full-corpus novelty claim. | Explicit IDs are checked for duplicate, focal, future, and mismatched-version inputs. Empty `R` stays empty. | [`M/controls.py`](../M/controls.py), [`M/engine.py`](../M/engine.py). Original records lack author-supplied input lists, so retrieval cannot stand in for historical `R`. |
| Quality heads require dated, source-bound labels. | Train-only feature standardization and closed-form ridge are selected on validation MSE; no labels means no fitted head. | Label evidence hashes, observation times, split membership, and target definitions are validated before fitting. | [`M/training.py`](../M/training.py), [`M/results/stage5/RESULTS.md`](../M/results/stage5/RESULTS.md): 25 train and 2 validation records, zero usable quality labels, zero fitted heads. |
| Missing evidence stays unavailable. | Without claims, N/custom coordinates are undefined; without eligible inputs, grounding/answeredness cannot be inferred. Missing B-Q/B-ABS is not substituted by B-TF/B-LEN. | Readouts preserve undefined values and baseline availability reasons. | [`M/baselines.py`](../M/baselines.py), [`M/results/stage5/results.json`](../M/results/stage5/results.json). This improves auditability but leaves most registered comparisons unestimable. |

## Where Phi fails

No eligible held-out evaluation of Phi exists. The cases below are failures in
the current evidence chain and adjacent exploratory analyses, not measured
test-set error rates for Phi.

| Reproducible example | Saved evidence | What it shows |
|---|---|---|
| A1 density stops responding at higher coverage. | In supplementary A1, density deltas for 50→75% and 75→100% are both `0.000 [0.000, 0.000]`; concentration is reversed, distributed−concentrated `−13.5 [−19, −8]`. | The measure misses the manipulation direction in this two-cluster sample. No coordinate met the joint threshold. See [`A1_STATISTICAL_FINDINGS_V1.md`](../M/a1_replication/A1_STATISTICAL_FINDINGS_V1.md) and [`A1_STATISTICAL_RESULTS_V1.json`](../M/a1_replication/A1_STATISTICAL_RESULTS_V1.json). |
| Identity threshold calls near-misses “same.” | Exploratory S1 reports 51/60 M false positives among near-misses; E5 calls all 60 same. For h001, M similarity is 0.7509 and E5 cosine 0.9736, both above the fixed 0.65 threshold. | This is poor separation against creator-intended labels, but those labels are unverified; it is a diagnostic warning, not validated error. See [`S1_exploratory_results.json`](../M/supplementary_s1_e1_exploratory/results/run_001/results.json). |
| A generated decoy can still be supported by its supplied papers. | In the V2 exploratory review, both reviewers marked both decoys same-topic, but only the video decoy unsupported; the image decoy was marked supported. Agreement was 17/18 (κ=.912), with one AI-assisted review and the other independence self-declared but not externally verified. | Topic match and unsupportedness are distinct controls; agreement does not establish correctness or independence. The V2 registered baseline-comparison endpoint was not computed. See [`grounding_exploratory_comparison.json`](../M/prospective_grounding/exploratory_evidence/analysis_2026-11-15/results.json). |
| Temporal leakage was possible in early implementation drafts. | Codex recorded and corrected an arrival-before-publication error and a future-answer leak; the latter now removes the annotation from `Phi`, not only from the G readout. | Synthetic tests exercise both cases but do not verify real-world source dates. See [`M/AI_USAGE.md`](../M/AI_USAGE.md), [`M/tests/test_space.py`](../M/tests/test_space.py), and [`AI_LOG.md`](../AI_LOG.md). |

These cases motivate stronger source-time validation, calibrated identity
thresholds, and explicit unsupported-decoy checks. They do not establish that
the proposed architecture passes or fails the original frozen battery.

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
preserved under [`a1_replication/`](../M/a1_replication/). Its operational
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
[`a1_replication/`](../M/a1_replication/): the
[supplementary registration](../M/a1_replication/PREREG_REPLICATION.md),
[approved partial-controls amendment](../M/a1_replication/AMENDMENT_003_PARTIAL_CONTROLS.md),
[cohort manifest](../M/a1_replication/cohort_manifest.json),
[saved scores](../M/a1_replication/A1_SCORING_RESULTS_V1.json),
[statistical findings](../M/a1_replication/A1_STATISTICAL_FINDINGS_V1.md), and
[saved statistics](../M/a1_replication/A1_STATISTICAL_RESULTS_V1.json).

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
[`supplementary_s1_e1_exploratory/results/run_001/results.json`](../M/supplementary_s1_e1_exploratory/results/run_001/results.json).
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
[`prospective_grounding/generated_v2/`](../M/prospective_grounding/generated_v2/).
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
[`prospective_grounding/exploratory_evidence/`](../M/prospective_grounding/exploratory_evidence/).

## Scientific interpretation and limitations

Software tests validate implementation, not the hypotheses. The core battery
has no eligible results. Supplementary A1 misses its joint threshold;
exploratory S1 fails its joint criterion on minimal paraphrases; V2 has no
outcome comparison. Publication dates cannot replace question, input-version,
or outcome-observation dates. No dates or labels were imputed, and exposed E2
was not promoted into original A1. The two-cluster A1 and two-family V2 samples
limit generalization.

## Reproducibility

The ledger and reported statistics refer to saved artifacts; this report work
reran no experiment or inference. Key SHA-256s: stage-5 ledger
`3e169c4179b7a786fd1e2a0da919184e76a4d0fb4426dd29b23f9caafc681474`; A1
scores `40f564c94801395fd327b1849d457515dab6e7d4f0901fb3960d91c9f358b4ff`;
A1 statistics `7aff25e53986a78145610b3bc0e9a352364987adccac1cf9003b48310a991c4c`;
exploratory S1 result `edd827ff7dd8cfebde154ac156834e50a2e9a0e40f9d5357d8caa181b86d71e5`.
Frozen-file checksums are in `frozen/SHA256SUMS.json` (file SHA-256
`e7ec110b355e9107f65a02e63c371d0342c24d3c1798c40c126bdd385cc06178`).
Report-package snapshots are [`registered_core_status.json`](results/registered_core_status.json),
[`A1_SCORING_RESULTS_V1.json`](results/A1_SCORING_RESULTS_V1.json),
[`A1_STATISTICAL_RESULTS_V1.json`](results/A1_STATISTICAL_RESULTS_V1.json),
[`S1_exploratory_results.json`](results/S1_exploratory_results.json), and
[`grounding_exploratory_comparison.json`](results/grounding_exploratory_comparison.json).
Their hashes match the canonical evidence files listed above. From the
repository root, these commands read saved inputs and reproduce descriptive
summaries only:

```sh
# Verify frozen nine-test status and eligible counts from the saved ledger.
python3 -c 'import json; r=json.load(open("main/results/registered_core_status.json")); print(r["blocked_count"], [(x["test"],x["status"],x["eligible_records"]) for x in r["tests"]])'

# Reproduce the saved supplementary A1 statistics in memory; writes no files.
python3 -B -c 'import json,pathlib; from M.a1_replication.analyze_a1_results import analyze; p=pathlib.Path("M/a1_replication"); r=json.loads((p/"A1_SCORING_RESULTS_V1.json").read_text()); s=json.loads((p/"A1_STATISTICAL_RESULTS_V1.json").read_text()); assert {k:v for k,v in s.items() if k!="provenance"} == analyze(r)'

# Recompute V2 exploratory review agreement in memory; no model calls.
python3 -B -c 'from M.prospective_grounding.exploratory_evidence.compare_review_responses import validate_and_compare; r, _, _ = validate_and_compare(); a=r["rating_agreement"]; b=r["association_agreement"]; assert (a["exact_agreement_n"],b["joint_decision_agreement_n"])==(17,6) and abs(a["cohen_kappa_unweighted"]-0.912)<0.0005 and abs(a["cohen_kappa_linear_weighted"]-0.927)<0.0005'

# Read the saved exploratory S1 criterion and pair counts.
python3 -c 'import json; r=json.load(open("main/results/S1_exploratory_results.json")); print(r["status"], r["metrics"], r["provenance"]["sample_count"])'
```

The original nine-test protocol is [`PREREG.md`](../M/PREREG.md); the separate V2
generation and scoring protocol is
[`prospective_grounding/PREREG_V2.md`](../M/prospective_grounding/PREREG_V2.md).
The previously recorded CPU suite result of 92 passing tests validates
implementation behavior and fixtures, not scientific performance. The frozen
M implementation has no trained Q head. S1 records CPU execution and E5
revision/file hashes; A1 records local model revisions and weight hashes but
not hardware. V2 records its Qwen3 digest/settings but not hardware or energy.
No compute use is inferred where the artifacts do not report it. The commands
above were not run during this documentation review.

## AI use and submission status

AI assistance, caught errors, Qwen3 use, and the AI-assisted review are
disclosed in [`AI_LOG.md`](../M/AI_LOG.md) and [`AI_USAGE.md`](../M/AI_USAGE.md). The V1
empty response is preserved; no question, label, date, or result was invented.

The submission contains nine blocked core evaluations, the limited A1 negative
threshold result, and V2 generations without a scored result. These supplements
remain separate from the original battery. The table above gives each original
test's remaining source, time, label, control, model, or baseline blocker.
