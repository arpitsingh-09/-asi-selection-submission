# M core battery — prospective infrastructure preregistration v1

This registers hypotheses and analysis before any M real heldout evaluation.
Existing E1/E2 results and the already inspected candidate metadata are development
material, not new prospective evidence. No unseen-list or model-performance claim
is made. All real execution is disabled. Synthetic software tests are permitted.

## Frozen design and hypotheses

One shared Phi v1 supplies all heads. Current model is fixed 512-bin lexical hashing,
not a learned semantic encoder. Quality factors remain unavailable: zero verified
labels. No cached frozen semantic B-Q/B-ABS is available by default. Their absence
blocks a comparison, never licenses replacing them with the lexical proxy. B-TF is
train-only TF-IDF; B-LEN is token count. Optional B-JUDGE is excluded.
`frozen/config.json` identifies source hashes, partitions, alpha grid and settings;
its SHA-256 is in `frozen/SHA256SUMS.json`. No trained quality model is frozen or
claimed. A later fitted model requires a new prospective model-lock amendment
using train<=2023 and validation2024 only, committed before heldout prediction.

Directional hypotheses: paraphrases preserve each head more than near misses;
identity separates minimal paraphrases from near misses beyond B-Q; novelty obeys
partial-coverage and concentration manipulations; Q/N signals survive length
matching; quality agrees with expert/reviewer/outcome labels beyond text baselines;
within-seed preference survives system demeaning; frozen training-year models are
equivalent within tolerance. These are hypotheses, not established findings.
The lexical identity head may fail to beat a semantic B-Q; no guaranteed success
or positive outcome is predicted. Quality hypotheses cannot currently be tested.

## Primary tests, metrics, resampling, criteria

All intervals are paired percentile 95% cluster bootstrap, 2,000 draws, PCG64 seed
20261113. Identical draws serve Phi, baselines and controls. Resample independent
units with replacement and keep all associated records/pairs/conditions together;
never independently resample model/baseline, paraphrases, reviews or manipulations.
At least two independent units are required; >5% undefined replicates blocks the
analysis. Report units, records, valid draws, point estimates and intervals.
Insufficient power is not a pass. All confirmatory claims require their own stated
criteria; the battery passes only if every core criterion passes. No claim of a
familywise-adjusted discovery is made from the marginal intervals.

| Test | Primary statistic | Bootstrap unit | Pass |
|---|---|---|---|
| I1 | Mean near-miss drift minus paraphrase drift for I,N,G,Q1,Q2,D,T | Focal-question/paper cluster | Lower CI >0.02 for every head |
| I3 | Paired ranking concordance improvement over B-LEN, per claimed Q/N coordinate | Connected paper-pair component | Lower CI >0.02 for every claimed coordinate |
| S1 | Accuracy improvement over B-Q, separately near-miss and minimal paraphrase | Focal-question cluster | Both lower CIs >0.02 |
| A1 | Strict signed-axiom pass fraction, per novelty coordinate and E2 axiom | Focal paper (all manipulations) | One same coordinate has lower CI >=0.80 on both partial coverage and concentration; report all others |
| H1 | Length-matched preference concordance improvement over B-Q, raw and system-demeaned | Shared-seed/connected battle component | Demeaned lower CI >0.02; raw always reported |
| H3 | Spearman Q–review-score correlation minus B-Q correlation; Q correlation / human ceiling | Paper, keeping all reviews | Improvement lower CI >0.02; share of independent ceiling reported |
| O1 | Within-topic pair concordance improvement over B-Q, separately both Q factors | Topic cluster (all related pairs) | Lower CI >0.02 for both factors |
| O2 | Within-identical-seed ranking concordance improvement over question-text B-TF | Seed-set/connected overlapping-paper component | Lower CI >0.02 |
| T1 | Mean absolute head-score difference for frozen train<=2022 versus train<=2023 models | Later focal paper | Upper CI <=0.02 for every head |

Drifts use L1 mean of a head's shared coordinates after fixed documented [0,1]
normalization; cosine novelty uses distance/2, signed scope uses (x+1)/2. Q needs
train-only fixed normalization; absent scales/predictions block I1/T1. D uses a
fixed companion set per focal item; T uses identical later snapshots, not the
calendar timestamp itself. Head dimensions/scales/companion IDs must be recorded
with predictions; no post-test normalization. T1 requires separately locked 2022
and 2023 fits (currently absent). H1 demeaning subtracts each generating system's
endpoint mean separately for Phi and B-Q on the same eligible cohort, recomputed
inside each bootstrap. It is the registered nuisance adjustment, not model fitting.
H3 requires an independently measured human-agreement ceiling with provenance;
no ceiling is inferred from model correlation. Signed ranking labels cannot be ties;
prediction ties receive half credit. S1 uses previously frozen boolean decisions.

## Controls and time validity

Every input-bearing evaluation must provide original, explicitly empty, shuffled
from another instance, and independently verified same-topic decoy conditions.
The implementation requires all four. Decoy uses original inputs and a distinct
question; same-topic judgment needs provenance. Control results are diagnostic,
not additional positive hypotheses: original labels may not describe decoy text.
No averaged mixture of controls is allowed. Original-input references must be
recovered for a real input-bearing claim; empty-only development manifests do not
satisfy this requirement. Length-matched pairs differ by <=5% or one token.
O2 requires identical seed IDs (at least three), publications <=365 days apart.

Train publications and observed training labels precede 2024-01-01. Selection uses
2024 publications/labels only; gap 2025-01-01 through 2025-06-30 is excluded.
Heldout publications start 2025-07-01. All question/text versions must be available
at posing time; all inputs/literature are strictly earlier and versions available
by posing time. Label observations must be dated no earlier than posing; subsequent
outcomes may be observed later but never enter features. No tuning on heldout.

## Candidate lock, missing data and execution gate

`frozen/heldout_candidates.jsonl` is a deterministic metadata/ID-only candidate
list derived from Stage 2, not an eligible annotated test cohort. Nine test lists
bind those candidates and their absent dependencies; exact bytes have SHA-256s.
All candidates remain ineligible pending question-intent/date, input/control and
annotation checks. E1 authored contrasts have unknown question-creation dates.
Counts and exclusions are reported; no unknown date is imputed, no paper title
substitutes a question, and no label is synthesized. Null heads never become zero.
Raw review averages without dated source reviews cannot train Q or supply a human
ceiling. Each test returns BLOCKED if its requisite annotations, predictions,
controls, model or baseline are absent. Synthetic-only results carry that label.

Before real execution: finish genuine annotations and verified eligibility; freeze
an independently valid test-specific list and exact model/baseline artifacts in a
new version, record all changes prospectively, commit it and this protocol, obtain
explicit authorization, and only then enable real prediction/scoring. Metadata
candidate hashing is not eligibility authorization. Do not silently amend these
files or claim earlier E1/E2 analyses as prospective M tests. Any previously seen
items must be disclosed or replaced with fresh eligible examples for confirmation.
