# Main Problem (`M/`)

This package implements a shared research-question representation and evaluation
infrastructure for the Main Problem. It is **not a completed experimental
submission**: the software is implemented and tested, but quality heads are not
trained and none of the nine registered evaluations has eligible evidence or
results.

## Setup and CPU checks

The implementation targets Python 3 and uses NumPy for vector operations and
training. The CLI and unit tests run locally without model downloads, API access,
GPU inference, or Ollama. From the repository root:

```sh
PYTHONPYCACHEPREFIX=/tmp/asi-m-pycache OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -m unittest discover -s M/tests -p 'test_*.py'
python3 -B -m M --help
python3 -B -m M.training --help
```

The focused full suite currently passes **92 tests**. These are software tests,
not experimental evidence. Existing train/validation fitting commands write only
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
