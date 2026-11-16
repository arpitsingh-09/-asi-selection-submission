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

Per focal paper, the scored conditions were the original-pool reference,
25/50/75/100% claim coverage, concentrated claims, distributed claims, and a
shuffled pool. The empty-pool output remained undefined and was not imputed.
The same-topic decoy was unavailable and was excluded under approved
Amendment 003; no decoy effect is estimated. Scoring used paired focal-paper
cluster bootstrap intervals (2,000 draws, PCG64 seed `20261113`).

| Coordinate | Partial-coverage strict pass fraction (95% CI) | Concentration strict pass fraction (95% CI) |
|---|---:|---:|
| Y | 0.500 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| density | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| N | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| yours | 0.500 [0.000, 1.000] | 0.000 [0.000, 0.000] |

The registered supplementary rule required the same coordinate’s lower
confidence bound to be at least 0.80 for both manipulation families. None
qualified. Y passed the concentration ordering in both focal clusters, but
its partial-coverage pass fraction was 0.5 with a [0, 1] interval. Density,
N, and `yours` failed concentration; density also failed every strict
coverage ordering. The effects therefore show a limited, coordinate-specific
response, not consistent novelty behavior across manipulations. With only two
clusters, intervals are highly discrete and unstable; this negative threshold
result does not establish broad model failure or success. The analysis and
source artifacts are in [`a1_replication/`](a1_replication/): the
[supplementary registration](a1_replication/PREREG_REPLICATION.md),
[approved partial-controls amendment](a1_replication/AMENDMENT_003_PARTIAL_CONTROLS.md),
[cohort manifest](a1_replication/cohort_manifest.json),
[saved scores](a1_replication/A1_SCORING_RESULTS_V1.json),
[statistical findings](a1_replication/A1_STATISTICAL_FINDINGS_V1.md), and
[saved statistics](a1_replication/A1_STATISTICAL_RESULTS_V1.json).

## Supplementary S1 exploratory analysis (not original S1)

The separate exploratory S1 analysis used 60 source questions, each with a
minimal-paraphrase and near-miss decision. Against unverified E1
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

## Prospective grounding pilot: generation and exploratory reviews

The grounding pilot is supplementary and separate from the nine tests and A1.
V1’s first qwen3:8b call exhausted the 512-token budget in its `thinking`
field and returned an empty response (`done_reason="length"`,
`eval_count=512`). The one-shot stopped and the raw failure was preserved; V1
was not retried. The raw attempt is
[`01_video_memorability_primary.json`](prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json).

V2 was separately preregistered before inference and sent `think=false` to
address that failure. It retained the locked qwen3:8b digest and settings
(`temperature=0.7`, `top_p=0.8`, `num_predict=512`). All four calls succeeded:
two primary and two same-family decoy questions across the video-memorability
and image-enhancement families. Prompts, responses, inputs, timestamps, and
model provenance are preserved in
[`prospective_grounding/generated_v2/`](prospective_grounding/generated_v2/).

V2’s registered evaluation would compare groundedness proxy `G` with frozen
train-only TF-IDF baseline `B-TF` against the independent human relevance
ratings on original, shuffled, and decoy question-paper pairs; empty-pool
scores remain undefined. The primary endpoint is `MAE(B-TF) - MAE(G)`, with a
paired family-cluster bootstrap (2,000 draws, seed `20261113`). Passing also
requires a positive estimate, a lower interval
bound above zero, both decoy checks passing, at least 90% finite required
scores, and no temporal/provenance violation. No such scores were calculated:
the preregistered review and explicit authorization gates remain unmet.

Two response files were compared for exploratory purposes only. Both cover 18
paper ratings and six association checks. Exact rating agreement is 17/18
(94.4%); unweighted nominal Cohen’s κ is 0.912 and linear-weighted κ is 0.927.
The one rating difference is for `primary-image_enhancement-v2` /
`2412.20916v1` (2 versus 1). The two responses agree on both decisions for all
six association records. Cohen’s κ is chance-corrected agreement, not a
validity measure. Here it is descriptive only: reviewer 2 used AI assistance
and declares non-independence, and reviewer 1’s independence is unverified.
It cannot be presented as agreement between two independent human reviewers.
Reviewer 1 declares independence, but identity and independence were not
externally verified. Reviewer 2 declares `independent_review_confirmed=no`
and the response is identified as AI-assisted. Therefore this pair is not two
independent human reviews and does not pass V2’s review gate. No G/B-TF metric,
baseline comparison, interval, or grounding conclusion is claimed. Details
and byte-preserved responses are in
[`prospective_grounding/exploratory_evidence/`](prospective_grounding/exploratory_evidence/).

## Scientific interpretation and limitations

The implementation and fail-closed evaluation machinery are software outputs;
tests do not validate the scientific hypotheses. The core battery supplies no
eligible empirical result. The supplementary A1 analysis meets one Y
concentration ordering in two cases but misses its combined threshold, while
the other coordinates do not show consistent expected behavior. V2 shows that
the registered generation change yielded four preserved questions after
V1’s generation failure; it has not tested whether `G` outperforms `B-TF`.
The review agreement is exploratory and ineligible as independent validation.

Temporal conclusions are also limited: publication and cached review dates do
not substitute for verified question-posing, source-availability, and
outcome-observation dates. No test result can be recovered by imputing these
dates, filling absent labels, or reusing exposed E2 evidence as the original
prospective A1 cohort. The two-family V2 design and two-cluster A1 sample are
too small for broad generalization even if their gates were otherwise met.

## Reproducibility

The original evaluation ledger and all statistical claims above refer to
saved artifacts; no experiment or inference was rerun for this report. From
the repository root, the following commands reproduce saved calculations or
check offline materials:

```sh
# Reproduce the saved supplementary A1 statistics in memory; writes no files.
python3 -B -c 'import json,pathlib; from M.a1_replication.analyze_a1_results import analyze; p=pathlib.Path("M/a1_replication"); r=json.loads((p/"A1_SCORING_RESULTS_V1.json").read_text()); s=json.loads((p/"A1_STATISTICAL_RESULTS_V1.json").read_text()); assert {k:v for k,v in s.items() if k!="provenance"} == analyze(r)'

# Reproduce the exploratory V2 review comparison in its exploratory output directory.
python3 -m M.prospective_grounding.exploratory_evidence.compare_review_responses

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
implementation behavior and fixtures, not scientific performance.

## AI use and submission status

Codex assisted with implementation, documentation, and blinded packet
preparation. The local qwen3:8b model generated the V2 questions under the
registered settings. Reviewer 2’s exploratory response is explicitly
AI-assisted; its ratings are not treated as independent human evidence. The
V1 empty-response failure is reported with its raw record, and no question,
label, score, date, or interval has been substituted or fabricated. Additional
AI-use details are recorded in [`AI_LOG.md`](AI_LOG.md) and
[`AI_USAGE.md`](AI_USAGE.md).

The submission currently contains implemented software, nine blocked core
evaluations, a small supplementary A1 negative threshold result, and a V2
generation cohort without an evaluation result. To claim a core result,
complete each test’s source, temporal, label, control, model, and baseline
requirements under the frozen protocol. For V2, obtain two eligible
independent blinded reviews for all registered pairs and decoy checks, validate
conditions, then obtain explicit scoring authorization. Do not pool A1 or V2
with the original nine-test battery.
