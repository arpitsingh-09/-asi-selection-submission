# Stage 4 — recovered evidence; real core evaluations blocked

Implemented exact-byte/field evidence assertions (`evidence.py`), genuine review
and paper-ID ingestion (`ingestion.py`), independently checked question/outcome
linking and per-test cohort admission (`cohorts.py`), and cache-only semantic
baselines (`semantic_baselines.py`). Original protocol and frozen locks remain
unchanged. No model inference, cache writes or heldout scoring occurred.

Reproduce bounded import into a new output directory:

```sh
.venv/bin/python -B -m M.ingestion --out M/data/ingestion_NEXT
.venv/bin/python -B -m unittest M.tests.test_ingestion
```

Canonical recovery is `data/ingestion_v2/`; v1 is the earlier import before paper
identity links were added. Both preserve source bytes/offsets/hashes. The imported
570 genuine numeric recommendations are not 570 usable quality labels: public
observation dates and original question-version links remain unverified. 277
paper identities were joined; nine abstracts include possible question passages.
Neither numeric score nor question intent is invented. A source hash establishes
integrity, not independent truth. Ingestion output is development data only.

| Core test | Eligible | Specific blockers |
|---|---:|---|
| I1 | 0 | Full-head predictions/normalization, original references and verified controls; Q unavailable |
| I3 | 0 | Dated length-matched Q/N preference labels and fitted quality heads |
| S1 | 0 | E1 human/source confirmations, question-creation dates, original references/controls, exact semantic vectors/cutoff |
| A1 | 0 | Fresh prospective partial-coverage/concentration cohort and four controls; old E2 results are development evidence |
| H1 | 0 | Source-bound expert battles, system/seed identities, dated length-matched labels; Q unavailable |
| H3 | 0 | Postcutoff question/version–review linkage, public score-version dates, human ceiling, Q/B-Q |
| O1 | 0 | Both dated quality factors, within-topic question pairs and fitted heads |
| O2 | 0 | Identical >=3-reference seed groups, within-year paper links, dated outcomes and predictions |
| T1 | 0 | Separately locked 2022/2023 models and complete normalized predictions/controls |

All per-test machine receipts have `status: BLOCKED`, `metrics: null`, `ci95: null`.
No real effect sizes, bootstrap intervals or baseline gains exist to report.
The cache-only adapter was implemented and tested, but all 80 exact candidate
question texts are absent from the existing E2 vector cache; no score-only E1
output is treated as a vector. Adding a cache adapter cannot create missing vectors.

Next: source-backed human verification and original-input recovery for a small S1
cohort, plus genuine cached semantic vectors/cutoff evidence. Commit that amended
cohort/model lock before generating real prediction records. This session does
not request heavy inference or relax any date/annotation requirement.
