# Prospective A1 novelty-axiom experiment — draft, not registered

This is a separate prospective experiment proposal. It does not alter or repair
the original frozen A1 cohort, `M/PREREG.md`, or `M/frozen/A1_test_list.json`.
No generation, model scoring, or evaluation is authorized by this draft.

## Question and hypotheses

For each newly generated question, let R be exactly the papers provided in the
recorded generator prompt. The primary hypotheses are that the frozen shared
representation and novelty readouts satisfy both the partial-coverage and
concentration axioms. The primary statistic is strict signed-axiom pass
fraction, per novelty coordinate, clustered by focal paper with all
manipulations. Pass requires one same coordinate with lower 95% CI >=0.80 on
both axioms; report all other coordinates. Use the governing protocol's paired
percentile cluster bootstrap (2,000 draws, PCG64 seed 20261113); more than 5%
undefined replicates blocks inference. The prospective amendment must state
the exact signed direction and scoring implementation before generation; this
draft does not redefine either.

## Cohort and temporal rules

Use distinct, source-identified papers whose publication and source-availability
timestamps precede actual question generation. For generated questions, R is
exactly the papers actually supplied to the generator, not their full
bibliographies. Record exact IDs, URLs, source
locators, raw-source hashes, versions, retrieval timestamps, prompt, model
identity, parameters, seed, and actual UTC generation timestamp. Never backdate
generated questions or represent them as historical author questions. Keep
training and validation disjoint from held-out records; use only the frozen
temporal windows and model-selection rule approved by the prospective amendment.
Question/source identity and availability must be independently checked before
the test cohort is locked.

## Models, baselines, and normalization

Before any held-out prediction, lock the exact shared-representation model and
all required prediction heads, inference configuration, tokenizer/encoder and
source versions, code revision, seeds, and artifact hashes. Lock every required
baseline under the same information and temporal constraints. Fit feature
normalization on training data only, select configuration on validation only,
and hash/commit the resulting normalization artifact before test prediction.
No untrained quality head may emit substitute predictions.

## Conditions and manipulations

For each eligible question prepare: (1) original R; (2) explicitly empty R;
(3) shuffled R from a different eligible instance; and (4) a distinct same-topic
decoy question/input condition with independent, dated semantic validation and
source evidence. Record source-bound annotations for partial-coverage and both
concentrated and distributed coverage manipulations. Validate exact membership,
disjointness, source dates, manipulation fidelity, and decoy suitability before
freezing. Missing or disputed validation excludes the record before scoring.

## Outcomes and inference

Use the registered A1 signed axiom deltas and all required novelty coordinates.
Report per-coordinate pass fractions and paired comparisons against each
required baseline/control. Compute paired percentile cluster-bootstrap 95%
confidence intervals using the preregistered resampling unit, draw count, and
seed from the governing protocol. Do not change thresholds or resampling choices
in this draft; the prospective amendment must state them exactly before data
generation/scoring.

## Human/source validation and exclusions

Independent reviewers verify source identity, input-to-question relationship,
topic/decoy suitability, and manipulation fidelity, with reviewer identity or
code, date, evidence references, decisions, and rationale. Retain disagreements;
do not synthesize consensus or replace missing labels with model judgments.
Exclude records with missing provenance, future/undated inputs, duplicate or
development-used examples, invalid controls, incomplete annotations, or failed
temporal/model-lock gates. Document each exclusion before unblinding outcomes.

## Freeze and authorization gates

Before scoring, create a separately named cohort and amendment, include all
protocol and artifact hashes, and make a local Git commit containing the
prospective preregistration and lock artifacts. Obtain explicit execution
authorization after review. The readiness validator must reject execution until
source provenance, temporal validity, model and normalization locks, controls,
independent validation, committed preregistration, and authorization are all
present. The original frozen A1 cohort remains unchanged.
