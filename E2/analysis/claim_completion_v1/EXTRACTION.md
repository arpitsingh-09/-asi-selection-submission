# New source-bound claim extraction

This run extracted 27 additional claims for 22 of the 45 remaining short focal
sets, using the current Codex language-model session and cached source abstracts.
These are new extractions, not recovered earlier model responses. The exact
serving model revision is not exposed. No local model, GPU or Ollama ran.

Extraction instruction: add only the minimum missing substantive atomic
assertions needed to reach four; retain an exact source excerpt; check each
addition against all existing claims for overlap; preserve old claims and every
original audit/review limitation. Do not use paper organization, code release
or paraphrased restatements just to reach a count. Record AI extraction and
review explicitly, without implying independent human approval.

The 27 retained additions and specific distinctness decisions are saved in
`additions.jsonl` and `review.jsonl`. Every excerpt matched the original abstract.
The latter binds each addition to source filename, line, file SHA-256 and abstract
SHA-256. This extraction instruction is documented after the extraction; it is
not a prospective experiment preregistration.

`claims_future.jsonl` is the cumulative 300-paper future-use artifact. It now
contains **277 sets with 4–10 claims by count; 23 remain below four**, listed in
`remaining_short_sets.jsonl`. Count completion does not validate every inherited
claim's atomicity/support. Old audit limitations remain attached. Original
selected/scored claims and prior recovery artifacts were not rewritten.

No new claim has an exact matching vector in the read-only existing embedding
cache: **0/27**. No new score, pass rate or human-check metric is asserted.
Future scoring must separately freeze the accepted claim version and new plan;
the original 241-paper experiment excluded recovered claims and stays unchanged.

Materialization uses `E2/complete_claim_additions.py` with a new directory
containing a copy of `additions.jsonl`. It validates before writing final files
and refuses to overwrite an already materialized output. It handles identical
cross-pool copies of raw paper records while rejecting conflicting source text.

Validation: 27/27 exact source excerpts; cumulative count/ID checks; protected
source hashes unchanged. Six targeted merge tests passed. The pre-existing E2
test suite and experiments were not rerun.
