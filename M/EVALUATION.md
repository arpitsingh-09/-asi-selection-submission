# Core battery infrastructure

Protocol: `PREREG.md`. Frozen candidate/config hashes: `frozen/`. Result/record
schemas: `schemas/`. These are scoring runners over **frozen prediction records**,
not annotation generators. They never turn missing head predictions into labels.
Real scoring remains locked; the commands below only emit BLOCKED receipts and do
not read heldout records. Output paths must not already exist.

```sh
.venv/bin/python -B -m M.evaluation I1 --out /tmp/M-I1.json
.venv/bin/python -B -m M.evaluation I3 --out /tmp/M-I3.json
.venv/bin/python -B -m M.evaluation S1 --out /tmp/M-S1.json
.venv/bin/python -B -m M.evaluation A1 --out /tmp/M-A1.json
.venv/bin/python -B -m M.evaluation H1 --out /tmp/M-H1.json
.venv/bin/python -B -m M.evaluation H3 --out /tmp/M-H3.json
.venv/bin/python -B -m M.evaluation O1 --out /tmp/M-O1.json
.venv/bin/python -B -m M.evaluation O2 --out /tmp/M-O2.json
.venv/bin/python -B -m M.evaluation T1 --out /tmp/M-T1.json
```

Synthetic fixtures may be scored using `--synthetic --records FIXTURES.jsonl`.
Every row must declare `dataset_kind: synthetic`; mixed/real rows are refused.
Reproduce software checks: `.venv/bin/python -B -m unittest M.tests.test_evaluation`.
No synthetic statistic constitutes assignment experimental evidence.

All rows need record/question IDs, registered cluster `unit_id`/`unit_kind`, posed
and availability dates, model training cutoff, `selected_on: 2024-validation-only`,
source provenance, dated input versions, and four condition dictionaries under
`predictions`. `control_evidence` has original/empty/shuffled input IDs plus an
independently verified same-topic indicator/source. Nonempty original inputs and
different nonempty shuffled inputs are mandatory. Frozen prediction preparation
must bind actual snapshot IDs, model/config hashes, source versions, normalization
and companion IDs; the current v1 does not yet generate these annotated datasets.
Shared question IDs cannot cross clusters. Build connected components of overlapping
pairs/battles/seed groups before assigning IDs; neither arbitrary row IDs nor
independently shuffled control IDs are legitimate resampling units.

Per-condition prediction and row extensions:

| Test | Predictions per condition | Other row fields |
|---|---|---|
| I1 | Each I,N,G,Q_peer_review,Q_later_community_use,D,T maps to paraphrase_drift,near_miss_drift | Frozen normalization provenance; both edits from same focal question |
| I3 | scores maps all claimed Q/N coordinates to signed pair preference; B-LEN signed preference | Signed nonzero label; tokens_a,b; length_matched |
| S1 | decision,B-Q boolean same-question predictions | task near_miss/minimal_paraphrase; genuine boolean label |
| A1 | scores maps every N coordinate to strict signed axiom delta | axiom; all E2 conditions retained, both core axioms per focal unit |
| H1 | score_a,b and B-Q_a,b numeric endpoint scores | system_a,b; signed expert preference label; length fields |
| H3 | score,B-Q numeric scores | Numeric reviewer label, independent positive ceiling and ceiling_evidence |
| O1 | peer_review,later_community_use signed preferences; B-Q maps both factors | labels maps both factors; same_topic_verified |
| O2 | outcome signed preference; B-TF maps outcome | labels.outcome; identical seed_ids_a,b; paper_a_date,paper_b_date |
| T1 | Each head maps Y,Y_minus_1 to fixed normalized predictions | year_Y=2023, model_Y_minus_1_until in 2022, normalization provenance |

Label-bearing tests require `label_evidence` with exact text SHA-256, source and
observed_at; integrity is not independent truth verification. Human review of source
and exact question identity remains mandatory. All labels/outcomes and human ceilings
are absent from current M real manifests. I1 and T1 require every head; unavailable
Q blocks them. A1 requires valid fresh/admissible E2 manipulation annotations and
all coordinates reported; existing E2 completed results cannot be silently reused
as prospective M results. T1 needs separately locked training-year models. B-Q/B-ABS
require actual fixed semantic cached embeddings, not renamed lexical vectors.

Bootstrap recomputes metrics (including H1 system means and H3 rank correlation)
inside each cluster draw. Model and baseline predictions remain paired. Primary
comparisons report improvement and its interval; H1 additionally reports raw and
demeaned effects, H3 raw correlation and ceiling share. Each condition is reported
separately; only original enters the primary pass criterion.

`python -m M.freeze --out NEW_DIRECTORY` reproduces deterministic metadata-only
locks. Existing locks are immutable; amended candidates/models require a newly
named version and committed prospective amendment. No timestamp is inferred from a
venue year. Current lists are 80 **ineligible candidates**, not 80 verified tests.
