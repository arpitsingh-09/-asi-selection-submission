# Fixed-52 N/custom-only evaluator

Implemented in `task2_claim_extension.py` and prospectively registered in commit
`77a409191e345b612a933c745583a0a2213a064f` before real N/custom computations.
The new `TASK2_N_CUSTOM_52_PROTOCOL.md` and
`analysis/task2_claim_extension_inputs_v1.json` bind the exact existing cohort,
claim version, saved condition pools, saved Y results, sidecar manifest,
representation, code and original input/result hashes. Existing preregistrations
and frozen plans are unchanged. Prior Y/density results were exposed; the new
stage is not blind and does not change that history.

The driver computes only N and custom (`yours`): existing float32 clipped-cosine
claim coverage, and 0.75*saved_Y + 0.25*N. It never recalculates Y/density or
re-ranks pools. It reuses the exact existing paired-bootstrap implementation
with private N/custom measure labels: 10,000 paper resamples, seed 20261113,
95% percentile intervals, paired conditions, ties fail at tolerance 1e-8.
No module globals are changed. Numerical summaries remain stage-specific;
N/custom estimates are not pooled across differing claim-extraction stages.

Before real scoring, the gate requires committed unchanged protocol/code/input
bindings, exact 52-paper coverage, unique IDs, valid original manifest membership,
strict chronology and focal/duplicate-abstract exclusion, fixed disjoint pairs,
all 93 complete sidecar vectors and explicit evaluation authorization bound to
the input manifest, protocol and finished sidecar checksum. Every required vector
is resolved before the first new metric. Missing vectors/authorization produce
no result directory. Existing output paths are rejected before computation.
The original cache and sidecar are read-only, all source hashes are checked
again before output, and there is no encoder/model fallback.

## Actual status

- Real claim sidecar: **0/93 complete**.
- Evaluation authorization: **false**.
- New real N/custom scores: **0**.
- Existing coverage remains Y/density **293**, N/custom **241**.
- Original scores, cache, E6 files/processes, root notebook/AI log and frozen
  plans were not modified.

The disabled authorization template and validation record are in
`analysis/task2_claim_extension_preparation_v1/`. The real read-only status was
checked after preregistration. **16 new targeted synthetic tests passed**;
previous test suites and experiments were not rerun. Tests cover original-formula
parity, saved-Y reuse, finite/unit vectors, chronology and focal exclusion,
cohort/condition duplicates and overlap, missing-vector fail-before-score,
bootstrap parity/reproducibility/ties, authorization and committed-code gates,
output overwrite refusal, alternate-manifest rejection, and an authorized
52-paper synthetic output path. Temporary synthetic outputs are not experiments.

Safe current command:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -B E2/task2_claim_extension.py status
```

Future execution syntax, **not authorized or executed now**:

```sh
.venv/bin/python -B E2/task2_claim_extension.py evaluate --authorization FUTURE_AUTH.json --output E2/analysis/NEW_N_CUSTOM_RESULTS
```

## Further mandatory progress without inference

Created three new full-abstract paraphrase drafts for previously uncovered
focals in `analysis/paraphrase_additions_v1/candidates.jsonl`. Exact source
abstract/claim hashes, source lines, candidate hashes, claim-to-passage coverage
and explicit Codex AI review are preserved. Their original five pilot records
and frozen plans are unchanged. There are now **8 candidate papers**, leaving
**292 without candidates**. The three drafts have no independent meaning review,
no scoring permission and no cached vectors; they are not scored or approved
manipulations. No local generation model or Ollama was invoked.

## Next action

Continue independent meaning-preservation review and source-supported paraphrase
preparation while E6 is active. The eventual numerical N/custom step is now
implemented and preregistered; it can run only after the 93-vector worker passes
its separate E6-inactive/resource/inference/parity/calibration gates, all vectors
exist, and the new evaluation authorization is supplied. Do not bypass that
boundary to obtain results. Nearest planting retains 1,304 missing modified-paper
vectors, six focal claim sets need stronger evidence, one focal lacks sufficient
prior cached references, and Task 3 remains gated.
