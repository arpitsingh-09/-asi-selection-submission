# Bounded Task 2 claim-vector sidecar

Implemented in `claim_sidecar.py`. The actual immutable request/worker bundle is
`analysis/claim_sidecar_v1/`; its source is the existing 93-request execution plan.
That original plan, original novelty cache and frozen experiment plans were not
modified. The prepared bundle currently has **0/93 vectors** and no SQLite vector
file. `authorization.template.json` disables inference and resource authorization.

The worker reuses `task3_execution.batched_cpu_encoder` and the pinned local
SPECTER2 base/proximity-adapter inventory. It verifies every exact stripped claim
text, SHA-256 and paper/index use against the saved 52-paper claim source, along
with source/code/model fingerprints. Only the fixed 93 unique requests can be
written. CPU float32 final CLS is L2-normalized to match the original novelty
representation; there is no title/abstract prefix on claim inputs.

`encode` defaults to `--limit 0`, which performs read-only status and cannot load
a model. Positive limits require a new explicit authorization bound to the
manifest, confirmation that E6 is inactive, and verified resource headroom.
The shared loader must lower process priority and validate local asset hashes
before importing/loading the model; failure stops execution. CPU/BLAS threading
is limited to one, batches to one or two, and limits to at most 93 requests.
No download, GPU, MPS or Ollama path is provided.

Every new encoder instance must reproduce all three fixed cached parity controls
within the originally specified atol=1e-5/rtol=1e-4 before a sidecar is created.
At most four claim vectors may be generated before a separately reviewed,
hash-bound calibration report is required. The report includes timing, process
peak RSS, manifest identity and parity results. No model compatibility, runtime,
RAM or scheduling success has been measured in this implementation run.

Vectors live only in a new `claim_vectors_v1.sqlite3` beside the prepared
manifest. Provenance includes model/representation and manifest identity. Each
row binds exact text, request hash, model key, normalized 768-dimensional
float32 data and a checksum. Entire batches are validated before transactional
insertion. Existing rows are immutable; resumption skips completed requests,
and a complete cache resume never initializes a model. Corruption, unknown
rows, conflicts, nonfinite/wrong-shape data and missing source bindings fail.

## Read-only overlay and the existing novelty interface

`Overlay` opens the original and sidecar caches in SQLite read-only mode and
validates sidecar contents immediately. Missing vectors raise `KeyError`; there
is no fallback to the old writable encoder. It supports `.get(text)` and
`.encode(texts)`. Existing code can use the original `novelty.score` function via:

```python
# Future authorized scoring integration; not an evaluation command for now.
with Overlay(bundle_directory) as overlay:
    result = overlay.score(novelty, idea_text, claims, pool_ids, cutoff)
```

The adapter creates a private function-global binding for `_encode`; it does
not monkeypatch the module, edit `novelty.py`, call the legacy `_encode`, or
change the original database. The original scoring function still performs its
existing chronology and focal/duplicate filtering. For the future 52-paper
N/yours extension, calculate only those missing measures using the saved pools
and saved Y, rather than rerunning all four measures through this convenience
interface. A separate committed N/yours protocol is still required before new
numerical evaluation.

Safe current command:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B E2/claim_sidecar.py status --folder E2/analysis/claim_sidecar_v1
```

Future inference syntax, **not authorized or executed now**:

```sh
.venv/bin/python -B E2/claim_sidecar.py encode --folder E2/analysis/claim_sidecar_v1 --authorization FUTURE_AUTH.json --limit 4 --batch-size 2
```

Do not enable template flags without genuine new authorization and a safe
resource window. Keep E6 undisturbed. Changed worker/source fingerprints require
a new prepared bundle, not editing the existing manifest's hashes.

## Validation

**19 targeted tests passed**, exclusively using synthetic vectors and temporary
caches. Coverage includes exact requests/indices, hashes/model IDs, duplicate
requests, authorization/no-load boundaries, dimensions/finite values, fixed
parity failure, calibration review, bounded batches, transactional rejection,
immutable rows, resume, independently reproducible synthetic runs, read-only
loading, corruption and model-binding failures, and original `novelty.score`
integration with no writable fallback or module mutation. All original protected
source and embedding-cache hashes from the completed 52-paper experiment still
match. The real bundle remains at 0/93; test vectors are not experiment embeddings.
No existing experiment or earlier test suite was rerun.

## Additional mandatory work completed without inference

Materialized the exact deduplicated synthetic title-plus-abstract payloads needed
by the **existing 964 nearest-planting plans** into
`analysis/nearest_planting_vector_requests_v1/requests.jsonl`: **1,304 missing
modified-paper vectors**, with source-plan hashes/lines, source-paper identities,
synthetic IDs and coverage levels. This reuses the plans without changing or
rebuilding them. It does not generate embeddings or scores. These are deliberately
not accepted as claim requests by the 93-request worker; a separate modified-text
bundle will be needed later.

Y/density coverage remains 293 focals and N/yours remains 241. Nearest planting,
paraphrase, six evidence-limited claim sets, one insufficient-reference focal,
and the gated Task 3 evaluation remain unfinished. The next safe implementation
step is a N/yours-only cache-overlay evaluation driver and a separate prospective
protocol bound to the fixed 52 IDs, saved condition pools, claims and sidecar
manifest. It must refuse partial caches; no metric can be computed until the
93 vectors are available. Their actual generation waits for E6 inactivity,
explicit authorization and successful resource/parity/calibration checks.
