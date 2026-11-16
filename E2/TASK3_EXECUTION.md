# Task 3: prepared execution workflow

Prepared from e8577a9 on 2026-11-13. **No model was loaded, no embeddings were
generated, and no human-check evaluation was executed.** Current authorization
is preparation/tests only. E6, Ollama and its supervisor were not accessed.

## Ready

`analysis/task3_execution_v1/plan.json` freezes the 25,186 historical papers,
299 test papers, original-abstract hashes, mean historical review targets,
source-file fingerprints, model assets, implementation files and protocol.
Every test paper has a unique forum ID, original archived abstract, novelty
label and timezone-aware public-release date: 154 positive, 145 negative.
All 25,186 historical abstracts were rejoined and checked against the existing
frozen reference manifest. No reference IDs were selected again or replaced.
History is disjoint from test IDs/titles, retains the four conservative overlap
exclusions, and precedes every test OpenReview date. Raw review labels or test
ratings are not embedding inputs. The history targets retain official-review
mean ratings, review counts, years and same-venue identity.

### Encoder and temporal evidence

Pinned local base: `3447645e1def9117997203454fa4495937bfbd83`.
Pinned local proximity adapter: `2081559630a80fc5851d8f798a05ba81e9468089`.
`model_inventory.json` records SHA-256 and byte sizes for weights, configuration,
tokenizer and adapter files, plus installed library versions. Inspection used
JSON/metadata and file hashing, without importing or initializing a model.
The architecture is 12-layer BERT, hidden size 768, 512 positions, float32;
the adapter identifies itself as `[PRX]`.

The publisher's [base revision page](https://huggingface.co/allenai/specter2_base/commit/3447645e1def9117997203454fa4495937bfbd83)
and [adapter revision page](https://huggingface.co/allenai/specter2/commit/2081559630a80fc5851d8f798a05ba81e9468089)
both date the pinned revisions to **December 4, 2024**. This resolves a
**weights-existence upper bound**, not the exact training-data cutoff. The plan
uses end-of-December 2024 UTC as a conservative bound. October 2025 OpenReview
release dates are later. First publication elsewhere, including earlier
preprints, remains unverified; archived abstract versions can also differ from
first-release text. Eligibility review is still required before post-cutoff
claims. No cache modification timestamp was treated as a training date.

Only these read-only publisher pages were consulted online; model execution is
local-files-only/offline. The old no-network execution protocol was not edited.

### CPU embedding preparation

`task3_execution.py` supports bounded batched preparation for **both** history
and test abstracts, plus supplied claim text. The old historical-only helper
remains available but is not the recommended Task 3 driver.

The new worker uses a separate `task3_vectors.sqlite3` beside the plan, raw
float32 CLS vectors, batch size 2 by default, a 512-token cap, dynamic padding,
length-ordered batches, one CPU/intra-op/inter-op/BLAS thread, eval/inference mode,
and pinned local files. Each unique exact text/model fingerprint is encoded once;
resumption validates checksums, dimensions, finite values and source hashes.
Each batch is transactional. No existing cache or scoring output is opened for
writing. Complete cache resumption does not initialize a model.

It checks explicit future authorization **before** model loading, and lowers
CPU priority before importing torch. Failure to lower priority stops the job.
That operation was denied in a previous sandboxed preparation attempt; no new
priority or model-loading attempt was made here. Local loader/forward execution
compatibility is deliberately untested under the current no-inference rule.

`export` produces raw historical/test/claim matrices and ID/text/model/plan
bindings. It refuses missing vectors or an existing output directory. The
legacy evaluator also checks original-abstract hash alignment for history and
test, and earlier same-venue review dates before fitting a baseline.

### Claims and novelty

`claim_requests.jsonl` contains **299 source-bound empty requests** with original
abstract text and hashes, without novelty labels, ratings or contribution fields.
No text is represented as a generated or human-approved claim. Supply saved or
reviewed claim records in this format (schema illustration, not a real result):

```json
{"forum_id":"...","abstract_sha256":"...","provenance":"source/review record","claims":[{"claim":"...","evidence":"exact original excerpt"}]}
```

Run `task3_plan.py --claims PATH` into a **new** plan directory to import them.
The importer requires 4–10 nonduplicate supplied claims, exact excerpts and source
hash/provenance binding; semantic/atomicity review remains a substantive task.
The current plan has zero supplied claim papers. It never turns reviewer
novelty comments or rating fields into atomic research claims. A new plan changes
authorization fingerprints; do not silently append claims to the frozen plan.

`task3_novelty.py` implements all four fixed formulas using original-abstract
vectors normalized only for cosine calculations. Density uses blocked distance
rows and a memoized reference-neighbor density, avoiding a 25,186-square matrix.
It matches the existing formulas on synthetic fixtures. RND P=100/Q=50 and
small-pool caps remain unchanged. Primary human-check novelty text is now fixed
to original abstract only, explicitly different from the old manipulation
experiment's title-plus-abstract input. Edited R2 ideas remain preserved but
are not silently substituted for the baseline or this prepared primary analysis.

### Ridge and uncertainty

The quality-only baseline uses **raw original-abstract CLS**, historical mean
review ratings, training-fold standardization and intercepts, and the existing
nine-alpha grid. Expanding folds remain 2022->2023, 2022–23->2024, and
2022–24->2025. Alpha selection uses pooled validation MSE; test labels, ratings,
contribution and novelty predictions never select it. Each fold now reuses its
Gram matrix/eigendecomposition across alphas; fixture results agree with
independent ridge solves. The final refit uses all eligible history.

The existing report computes AUROCs, paired novelty-minus-quality differences,
and class-stratified paired 95% percentile bootstrap intervals (10,000 draws,
seed 20261113). A separate prediction file is frozen before baseline fitting or metric calculation.
Output carries its hash, the plan/model fingerprint, representation choice
and prior-test-exposure disclosure. Existing scoring files are preserved.

## Commands and execution boundary

Read-only status is safe now:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B E2/task3_execution.py status --plan E2/analysis/task3_execution_v1
```

The following are **future commands**, not authorization to execute them now:

```sh
# Small bounded batch, only after an explicit new inference authorization:
.venv/bin/python -B E2/task3_execution.py embed --plan PLAN_DIR --authorization AUTH.json --limit 100 --batch-size 2
# Export only after all required vectors are present:
.venv/bin/python -B E2/task3_execution.py export --plan PLAN_DIR --output NEW_EXPORT_DIR
# Metrics only after complete claims, embeddings, eligibility and evaluation approval:
.venv/bin/python -B E2/task3_execution.py evaluate --plan PLAN_DIR --authorization AUTH.json --output NEW_REPORT.json
```

`authorization.template.json` has inference/evaluation/preregistration/eligibility
flags **false**. Future authorization must identify its source, match the frozen
plan/protocol, and use a committed unchanged protocol. Evaluation additionally
requires a hashed 299-forum eligibility review with verified first-publication
dates later than the declared cutoff/bound. The template does not fabricate that
evidence. The older retrospective protocol and prior benchmark exposure cannot
be relabeled blind prospective validation. `TASK3_EXECUTION_PROTOCOL.md` freezes
the new preparation choices before any future Task 3 numerical computation.

## Exact remaining blockers

1. Current user instructions prohibit inference and large jobs; no new execution
   grant exists. The scheduling precondition previously failed in this sandbox,
   and available RAM while E6 runs is not established.
2. All **25,485 historical/test embeddings** and the future claim embeddings are
   still absent. Full local assets are available, but no model was loaded to
   prove runtime compatibility or measure throughput.
3. All **299 source-supported benchmark claim sets** are still required; no
   extraction LLM was launched. Four novelty prediction vectors therefore remain
   unavailable until the prepared scorer can run on complete inputs.
4. The exact training cutoff is unknown. Pinned revision release-bound evidence
   is now available, but first-global-publication/preprint eligibility and
   protocol/representation sign-off remain unverified for numerical evaluation.

The **next status/preparation step can run safely**. An embedding or evaluation
job cannot execute under current authorization. After explicit future approval,
resource checks and completed evidence, use a small bounded calibration batch
before any full job; do not auto-start it alongside E6.

## Estimated resources, not measurements

- One CPU thread; default batch 2, capped at 8. No GPU/MPS/Ollama use.
- Embedding process: budget **2–4 GiB RAM** (weights, CPU runtime, load peaks and
  activations). The model must have headroom independently of the active E6 job.
- All historical/test float32 vectors: **78,289,920 bytes (~74.7 MiB)**, excluding
  claims, cache indexes and exports; budget a few hundred MiB disk for artifacts.
- Separate scoring/ridge process: roughly **1–2 GiB RAM**, with bounded RND
  distance blocks and no loaded encoder. Actual library workspace can vary.
- Throughput is unmeasured. Illustrative 0.25/1/5 seconds per abstract implies
  approximately **1.8/7.1/35.4 CPU hours** for 25,485 abstracts alone. Claims,
  density computation, ridge and bootstraps add time. These are scenarios, not
  measured predictions; calibrate after future authorization.

## Offline validation

**87 tests passed.** New coverage includes source/ID/hash binding, unauthorized
and zero-limit no-model-load boundaries, batch deduplication/resumption, cache
corruption/conflict rejection, raw CLS export, complete-matrix requirements,
protocol/code changes, exact claim evidence, blocked RND parity, ridge-path
parity, earlier same-venue enforcement, and test-rating independence.
Only synthetic test fixtures were numerically evaluated. No experiment was run.
