# E2 fixed-52 N/custom-only extension preregistration

Recorded 2026-11-13 before any new N or custom score on this cohort. The earlier
241-paper study and the 52-paper Y/density extension have already been inspected.
The custom measure incorporates the already-known Y values; this is not a blind
prediction exercise. This prospective record applies only to the new N/custom
computations. Existing preregistrations and completed results remain unchanged.

## Fixed inputs and scope

Use exactly the ordered 52 focal IDs and input/code bindings in
`analysis/task2_claim_extension_inputs_v1.json`, SHA-256
`c20ac0335d018290b65409b7d051f4931e46a7e593f99b93ec78db136ce37b38`.
Reuse the cohort frozen for commit 588d15b, the exact saved near/far/older/newer
condition IDs, and its saved Y values. Do not rebuild pools, re-rank references,
recompute Y/density, change the claim version, add/drop focals, or rerun the
241-paper experiment. The four new preregistration artifacts (this protocol,
input manifest, evaluator and targeted tests) must be committed unchanged before
any real evaluation. Record the actual commit with each future result.

Claims come only from `analysis/claim_completion_v2/claims_future.jsonl`;
its reviewed/recovered extraction stage differs from the earlier cohort's
original selected claims. Count eligibility does not establish independent human
validation. Preserve those limitations. This is Task 2 development evaluation,
not the held-out human check; no human-check labels select anything here.

All saved reference IDs must belong to the existing subfield manifest, exclude
the focal and normalized focal-abstract duplicates, and be strictly earlier than
the focal timestamp. Retain the existing k=min(100,floor(n_cached_prior/2)) >=2,
same sizes/order within saved pools, and disjoint members of each contrast.
Validate exact cohort/condition coverage and uniqueness. Fail on any changed
binding, invalid chronology, overlap or missing input rather than changing a
pool or inventing data.

## Vectors and authorization

Use the original SQLite cache strictly read-only plus the request-bound sidecar
prepared in `analysis/claim_sidecar_v1/`. All 93 required claim vectors must be
present, checksummed, model/text/manifest-bound, finite unit float32 CLS vectors
of dimension 768. The sidecar's fixed model identity and cached-control parity
requirements remain unchanged. Every additional paper/index claim binding is
already frozen by the sidecar source manifest. No fallback encoder, download,
Ollama, accelerator use, cache mutation or frozen-plan edit is permitted.

Require a separate future evaluation authorization with literal true permission,
a nonempty provenance source, matching protocol and input-manifest SHA-256, and
the SHA-256 of the fully populated sidecar database. Existing authorization
files do not authorize this new stage. Authorization templates remain false.
Resolve every required reference/claim vector before calculating the first new
score; partial inputs must produce no metric or result directory. Verify frozen
source/code/cache and authorized sidecar hashes again before saving output.

Actual vector generation is not part of this protocol. The bounded worker's
E6-inactive/resource/explicit-inference/parity/calibration gates remain in force.
This evaluator imports no model and only performs bounded single-thread CPU
array arithmetic after its own authorization conditions succeed.

## Formulas, predictions and pass criteria

Use the existing scoring conventions exactly, without tuning:

- N = 1 - mean over claims of max clipped cosine with condition-pool papers.
- custom (`yours` in JSON) = 0.75 * saved_Y + 0.25 * N.

Use exact stripped claim text and normalized vectors. No new idea/focal vector
is needed by these two formulas, and density is never evaluated by this driver.
Keep the same float32 einsum, clipping, mean and scalar conversion order as the
existing cached scorer. Retain the existing NumPy version bound in the manifest.

| Measure | Per-paper prediction | Cohort prediction |
|---|---|---|
| N | near < far | More than half pass |
| custom | near < far | More than half pass |
| N | newer < older | More than half pass |
| custom | newer < older | More than half pass |

For every row, pass iff left-right < -1e-8; ties within 1e-8 fail. Temporal
ordering is an empirical hypothesis, not a universal axiom. Near/far uses the
same embedding geometry as scoring and is not independent semantic validation.
Report numerator, valid denominator, ties, pass rate and mean paired difference.
Do not reverse an orientation or change claims/weights in response to outcomes.

## Bootstrap and reporting

Reuse the existing bounded paper-bootstrap implementation with a private
measure-name binding to N/custom; do not mutate the old module. The unit is one
distinct focal paper and both condition scores stay paired. Use 10,000 draws
with replacement, NumPy default_rng seed 20261113, 95% percentile intervals at
2.5/97.5 for pass rate and mean paired difference. Contrast order: near/far,
then newer/older; measure order N, then custom. Continue one RNG stream across
all four rows with index batches of 250 draws. Retain all 52 denominators and
report subfield counts. No claim resampling, condition-independent resampling,
optional stopping, numerical tuning or p-value-based reinterpretation.

Save only the new N/custom rows, reused-Y references and stage-specific summary
into a fresh directory; refuse an existing output path before computation.
Report the old 241 as previously completed and the new 52 separately. Coverage
would become 293 only after successful authorized execution. Do not pool numeric
N/custom pass rates across the differing claim-extraction stages in this
protocol. The earlier 293-paper Y/density descriptive aggregate is unchanged.

Any invalid or missing-vector test uses synthetic temporary data only. Test
outputs are never experiment results. No real N/custom metric may be produced
under the present incomplete sidecar or disabled authorization.
