# Main Problem (`M/`)

This package implements a shared research-question representation and evaluation
infrastructure for the Main Problem. It is **not a completed experimental
submission**: the software is implemented and tested, but quality heads are not
trained and none of the nine registered evaluations has eligible evidence or
results.

## Setup and CPU checks

The core CLI, software tests, and saved-statistic analyses use the Python standard
library and NumPy. The minimal core dependency is pinned in
[`requirements-core.txt`](requirements-core.txt). The environment observed during
the 2026-11-19 submission audit was CPython 3.9.6, NumPy 2.0.2, macOS arm64. This
is a current audit environment record, **not** proof that every historical result
was produced with these versions. The model-backed supplementary runs have
separate model provenance; their complete Python dependency and hardware locks
were not retained. Core CLI and unit tests do not need model downloads, API
access, GPU inference, or Ollama. From the repository root:

```sh
python3 -m pip install -r M/requirements-core.txt
PYTHONPYCACHEPREFIX=/tmp/asi-m-pycache OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -m unittest discover -s M/tests -p 'test_*.py'
python3 -B -m M --help
python3 -B -m M.training --help
```

The last recorded focused full suite passed **92 tests**. This report update did
not rerun them. These are software tests, not experimental evidence. Existing
train/validation fitting commands write only
to a new output directory and fail closed if eligible dated labels are absent:

```sh
python3 -B -m M.training build --root . --out M/data/manifests_NEXT
python3 -B -m M.training fit \
  --train M/data/manifests_v2/train.jsonl \
  --validation M/data/manifests_v2/validation.jsonl \
  --out M/results/quality_NEXT
```

Do not reuse an existing output directory. The current frozen manifests and
eligibility report contain **0 eligible TRAIN and 0 eligible VALIDATION labels**
for both quality factors, so the current fit command records a blocked status and
does not create model predictions.

The metadata/cache CLI is available via `python3 -B -m M --help`. It produces
representations and readouts; it does not establish accuracy. The registered
evaluation commands and frozen prediction-record contract are documented in
[EVALUATION.md](EVALUATION.md). The runners currently produce blocked receipts
without reading held-out records. Synthetic fixtures, where explicitly marked,
are for software validation only.

## Architecture

`ResearchSpace` creates one time-bounded, fingerprinted representation `Phi` for
each question and supplied input-paper set. It combines question/context,
residual and four facet blocks with bounded-context scalars and a provenance-aware
prior-literature snapshot. Readouts consume that same representation:

| Readout | Implemented behavior | Current boundary |
|---|---|---|
| I | Similarity and scope proxy | Not a validated identity classifier |
| N | Prior-literature novelty and supplied-claim coverage | Claim-based coordinates require source-backed claims |
| G | Input relevance and available source-bound answer evidence | Similarity is not entailment; missing annotation is unknown |
| Q | Separate peer-review and later-community-use prediction heads | Both remain untrained; predictions stay unavailable |
| D | Set distance, Vendi, class/entropy and facet dispersion | Descriptive metrics; no registered result |
| T | Forward-only store update with snapshot linkage | Caller-provided metadata provenance is not independently established |

The default encoder is a deterministic lexical/rule prototype, not a trained
sentence model or a research-quality judge. Exact semantic cache misses fail
without inference. Baselines include cache-bound semantic baselines when valid
vectors exist, TF-IDF, and length controls; unavailable semantic baseline vectors
are reported unavailable rather than replaced by lexical scores. `I1QualityBundle`
integrates the two independently fitted Q artifacts with `ResearchSpace` and
checks shared feature schema, training provenance, and the pre-2024 cutoff. It
rejects missing or untrained heads; it never invents substitute predictions.

Temporal partitions are frozen: TRAIN through 2023, VALIDATION in 2024, a
2025-01-01 through 2025-06-30 gap, and TEST from 2025-07-01 onward. Feature and
label dates are checked separately. Quality fitting uses TRAIN normalization and
does not fit on validation or held-out labels.

## Reproducibility and data safety

The frozen lists and configuration are under [`frozen/`](frozen/), and their
`SHA256SUMS.json` verifies all listed files. Frozen candidates are ineligible
unless the required source provenance, dates, labels, controls, baselines and
model artifacts are present. A checksum establishes file integrity, not the
truth of an annotation. Read [PREREG.md](PREREG.md) and
[EVALUATION.md](EVALUATION.md) before any future registered run. A new prospective
protocol, if permitted, must be versioned and committed before scoring; never
edit the existing frozen protocol to make a cohort eligible.

Data collection, training, report consolidation and evaluation scripts use
versioned outputs. Preserve existing evidence/results and choose a new output
path for any authorized operation. No command in this README runs inference or
scores the registered TEST lockbox.

### Reproduce the reported result tables

The commands below print the already saved inputs to the report tables. They
do not run inference, scoring, fitting, or bootstrap analysis, and they do not
write files. For the supplementary A1 confidence intervals, the in-memory
recomputation command in [`FINAL_REPORT.md`](FINAL_REPORT.md) checks the saved
statistics against the saved score file without overwriting either.

| Report table | Command | Saved source |
|---|---|---|
| Registered evaluation status and blockers | `python3 -B -c 'import json; print(json.dumps(json.load(open("M/results/stage5/results.json"))["tests"], indent=2))'` | `M/results/stage5/results.json` |
| Supplementary A1 coverage and concentration pass fractions | `python3 -B -c 'import json; d=json.load(open("M/a1_replication/A1_STATISTICAL_RESULTS_V1.json")); print(json.dumps({"coverage":d["partial_coverage"]["registered_axiom_pass_fraction"], "concentration":{k:v["strict_axiom_pass_fraction"] for k,v in d["concentration"]["coordinate_results"].items()}, "overall":d["registered_pass_assessment"]}, indent=2))'` | `M/a1_replication/A1_STATISTICAL_RESULTS_V1.json` |
| Exploratory S1-style accuracy and paired intervals | `python3 -B -c 'import json; print(json.dumps(json.load(open("M/supplementary_s1_e1_exploratory/results/run_001/results.json"))["metrics"], indent=2))'` | `M/supplementary_s1_e1_exploratory/results/run_001/results.json` |
| Development diversity by input condition | `python3 -B -c 'import json; print(json.dumps(json.load(open("M/results/generated_development_v4/results.json"))["set_diversity_by_control"], indent=2))'` | `M/results/generated_development_v4/results.json` |
| Exploratory grounding reviewer agreement and disagreements | `python3 -B -c 'import json; d=json.load(open("M/prospective_grounding/exploratory_evidence/analysis_2026-11-15/results.json")); print(json.dumps({k:d[k] for k in ("rating_agreement", "association_agreement", "rating_disagreements", "association_disagreements", "limitations")}, indent=2))'` | `M/prospective_grounding/exploratory_evidence/analysis_2026-11-15/results.json` |

These are saved-artifact display commands, not substitutes for reproducing an
experiment. The supplementary model-backed results still lack complete
historical dependency and hardware locks, as described in the final report.

## Current scientific status

* **Implemented:** shared representation, readouts, controls, baseline adapters,
  temporal/ingestion checks, quality fitting entry point, I1 Q-head adapter, and
  registered evaluation/statistics infrastructure.
* **Software-tested:** 92 CPU unit tests pass. This establishes code behavior on
  fixtures and blocked-evidence paths only.
* **Trained models:** none. Both quality factors lack eligible TRAIN/VALIDATION
  labels, so no Q model or validation prediction is available.
* **Registered experiments:** 0/9 completed. There are no registered metrics,
  confidence intervals, or pass/fail findings.
* **Supplementary A1:** a separate, exposed partial replication was scored on
  two focal-paper clusters. Its registered threshold was not met; it does not
  change original A1 or the 0/9 count. See [FINAL_REPORT.md](FINAL_REPORT.md)
  and [RESULTS.md](RESULTS.md).

See [RESULTS.md](RESULTS.md) for the actual development-only readouts and
registered-test blockers, and [LIMITATIONS.md](LIMITATIONS.md) for unresolved
evidence requirements. `M/results/generated_development_v4/` is explicitly
development-only and must not be represented as registered evidence.

## Integrity records

The submission-level AI log is at [`../AI_LOG.md`](../AI_LOG.md); the scoped
Main Problem account and named regression-test evidence are in
[`AI_USAGE.md`](AI_USAGE.md). Dated execution failures and evidence limitations
are kept in [`NOTEBOOK.md`](NOTEBOOK.md). The log identifies a caught
future-annotation leak and its direct synthetic regression test, while
distinguishing a related availability crash that has no dedicated regression
test. Original M preregistration and amendment
commit objects are preserved in [`main_problem_git_history.bundle`](main_problem_git_history.bundle),
with commit IDs, parent links, chronology caveats, and A1 status reconciliation
in [`GIT_HISTORY_EVIDENCE.md`](GIT_HISTORY_EVIDENCE.md) and
[`a1_replication/A1_PREREG_STATUS_CLARIFICATION_2026-11-19.md`](a1_replication/A1_PREREG_STATUS_CLARIFICATION_2026-11-19.md).
From the repository root, verify the bundle with:

```sh
git bundle verify M/main_problem_git_history.bundle
```

This checks Git object/ref integrity; it does not independently authenticate
commit timestamps, author identity, or public availability.

The M core is a CPU-only lexical/rule path; cached MiniLM preparation and the
exploratory E5 S1-style run record CPU execution. The A1 score file identifies model
revisions and weight hashes but does not record the hardware used. The Qwen3
grounding generation records model digest and generation settings but no
hardware or energy use. Those latter runs therefore have no evidenced compute
tier claim; the submission does not infer a GPU or small-tier run from model
size alone.
