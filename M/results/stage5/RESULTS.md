# Stage 5 results ledger

No experimental evaluation was eligible or executed. Every numerical value below is an artifact count or offline preparation measurement, not a scientific performance result. No confidence intervals are available.

| Test | Status | Eligible | Metrics / CI | Exact blockers |
|---|---|---:|---|---|
| I1 | BLOCKED | 0 | None | No verified original input links, shuffled/independently verified decoy controls.; No fitted Q heads or frozen normalization for every readout. |
| I3 | BLOCKED | 0 | None | No length-matched dated Q/N preference labels linked to M questions.; Q heads unavailable. |
| S1 | BLOCKED | 0 | None | E1 source-alignment/second-reader annotations are unverified.; Question creation dates and original input/control links unavailable.; No verified cache model training cutoff. |
| A1 | BLOCKED | 0 | None | Existing E2 results are previously evaluated development evidence, not prospective M tests.; No new heldout partial-coverage/concentration cohort with original inputs and four controls. |
| H1 | BLOCKED | 0 | None | No local source-bound expert battles linked to seed IDs and generating systems with dated labels.; Q heads unavailable. |
| H3 | BLOCKED | 0 | None | No post-July-2025 original question/version and review-observation-date linkage.; Q heads, semantic B-Q and independently estimated human ceiling unavailable. |
| O1 | BLOCKED | 0 | None | No dated peer-review AND community-use outcomes linked to postcutoff question versions within topic.; Both Q heads unavailable. |
| O2 | BLOCKED | 0 | None | No verified identical >=3-seed citation groups, within-year dates and dated outcome linkage.; Q outcome prediction unavailable. |
| T1 | BLOCKED | 0 | None | No separately trained and prospectively frozen 2022 and 2023 head artifacts.; No complete-head normalized predictions and original input controls. |

## Reproducible descriptive results

- S1: 122 source-bound pairs across 61 questions; 0 human-confirmed.
- E1: 61 alignment labels remain pending manual confirmation.
- Review archive: 570 genuine recommendation values and 277 paper identity links recovered; zero public observation dates and zero usable question-linked labels.
- Cached MiniLM preparation: 183 CPU vectors, dimension 384; 0.807s encode loop. These were not used to score an evaluation.
- Quality training: 0 heads fit from 25 train and 2 validation records; no genuine outcome labels.
- Heldout: 80 metadata candidates only; zero eligible/evaluated.

## Illustrative error-analysis example

E1 item h001 (2610.26863) pairs “Is language pretraining necessary for strong text-to-image generation?” with minimal paraphrase “Is language pretraining required for strong text-to-image generation?” and near-miss proposal “Is language pretraining harmful to strong text-to-image generation?”. The source alignment audit marks this item pending manual confirmation. It illustrates the annotation question only; it is not a verified label, model error, or scored example.

## Reproduction

From repository root:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -B M/results/stage5/build_report.py
.venv/bin/python -B -m unittest M.tests.test_space M.tests.test_training M.tests.test_evaluation M.tests.test_ingestion M.tests.test_s1_workflow -q
```

The first command reads committed manifests/results and writes the deterministic ledger. The second runs the existing focused M tests; it does not run evaluations or model inference.
