# Held-out TEST: exact-request continuation

The original TEST is stopped. Offline verification recovered 1,258 completed
responses and identified one interrupted request, explicitly retained as
missing/incorrect and never reissued. Frozen integrity and researcher approval
pass; held-out accuracy readiness is READY. The optimized continuation has not
started. This is a continuation in a new directory, preserving prior evidence.

## Evidence and performance limit

The current launcher requests one observation at a time (`batch_size=1`, one
worker). A sample of 100 saved responses averaged 8.54 seconds HTTP latency.
A later 100-request server-log sample averaged 5.37 seconds prompt evaluation,
2.56 seconds decoding and 7.93 seconds total. Thus inference, especially prefill,
is the main measured cost. These samples are not identical windows. Logs show
one inference slot, 32768 slot context and 45/49 layers offloaded to GPU. Direct
CPU/GPU utilization tools were permission-denied, so no utilization percentage
is asserted. GPU offload is not evidence of full GPU saturation.

The frozen request places observations before hypotheses, limiting common-prefix
reuse. Changing its order, prompt contents, model quantization, context limits,
decoding, seeds, output cap, sampling only part of TEST, or changing server
parallel allocation is not included. Four HTTP workers against one inference
slot cannot be assumed to yield fourfold speedup. One worker remains the default;
1–4 are supported under the existing bounded independent-request policy. Every
request still contains exactly one observation. Batches of four reduce checkpoint
and transport-management overhead; they do not reduce the required 501 outcomes.

Offline protected-source validation confirms disjoint TRAIN/TEST observation
text and unchanged source/manifest hashes. TRAIN generation uses labelled TRAIN
observations; prediction strips TEST labels. Each fixed generated hypothesis set
is scored on all 501 source TEST rows by explicit PREREG requirements, not by a
convenient default. Historical researcher exposure to TEST labels is already
disclosed; these data must not be described as historically unseen.

125 evaluable arm cells contain 107 exact ordered hypothesis sets; all 501 TEST
observations are distinct. Therefore 62,625 scoring assignments require at most
53,607 unique identical prediction requests. The other 15 planned cells remain
8 generation failures and 7 unresolved set-0007 arms, never rerun. Exact reuse
avoids 9,018 requests (14.4%), an ideal request-count speedup of 1.168× before
retaining completed old responses. At roughly 8 seconds per request this avoids
about 20 hours; it does not turn a multi-day workload into hours. Actual gains
and any concurrency gain require post-approval measurement. No inference
benchmark has been run for this proposal.

## Implementation and scientific scope

`run_heldout_optimized.py` reuses the existing prediction policy, TRAIN-context
validation, scoring, JSONL export and arm evaluation pipeline. It preserves the
model, rendered prompts, all request options, seed, output cap, row output order,
invalid-prediction rule and fixed 501 denominators. No TRAIN predictions are used.

The exact-request cache key binds model, full rendered prompt, all options,
stage and output cap. The source and current runtime identities must match.
Only literal equality qualifies; no semantic or approximate cache is present.
Reused raw responses, including malformed/truncated predictions, are preserved
rather than regenerated. Conflicting replies for one identical deterministic
request block import. Duplicate assignments remain separate statistical arm/set
observations; cache hits are not new independent model samples. This reuse
assumes the frozen zero-temperature, fixed-seed inference is intended as the same
deterministic mapping; hardware-level reproducibility is not newly benchmarked.

The source launcher holds an exclusive lock. Continuation requires a read-only
shared lock on that same file and holds it throughout, preventing the old
launcher from being started again. The new run has its own exclusive lock.
Every imported attempt includes original path/hash provenance. New request intent
is fsynced before dispatch; responses and failures are content-bound. Threads
coalesce identical requests, preserve result order and never repeat failed calls.
Existing new-run completed responses replay on resume. An ambiguous interrupted
new-run request aborts; it is never retried. Cache usage records retain historical
backend token counts as provenance, not new token expenditure.

Default `--unresolved-policy block` stops on an old started request with no
terminal response. If the user explicitly elects `retain-invalid`, that old
attempt is carried forward as missing/incorrect under the frozen invalid/missing
prediction rule; it is never reissued. This is an intentionally incomplete
prediction, not a claim that the model predicted incorrectly. Disclose its count.
A Ctrl-C during inference is likely to leave one such attempt. There is no
lossless handoff guarantee for an in-flight nonstreaming request.

## Continuation command

Commit the optimized runner, its focused tests and this documentation locally
before launch. The required offline checks must pass. The runner rechecks
readiness, holds the stopped source lock, and verifies live runtime identity
before prediction. Full E6 evaluation remains subject to its separate scoring
requirements.

No inference or TEST launch is part of this local commit task. The command for
a subsequent authorized launch uses one worker and the accepted interrupted
request policy; it preserves the original directory and every request marker:

```sh
python3 E6/run_heldout_optimized.py \
  --source E6/runs/heldout_accuracy_v1 \
  --output-dir E6/runs/heldout_accuracy_optimized_v1 \
  --workers 1 --unresolved-policy retain-invalid --execute
```

To require complete resolution instead, use `--unresolved-policy block`; it
will not silently retry an unresolved request. Do not alter old records to make
that gate pass. Concurrency can be selected before the first new run with
`--workers 2` through `4`, but its speed benefit on the observed single-slot
server is unproven. Run settings bind the new directory and cannot be silently
changed on resume. Removing `--execute` only verifies the split/context and
prints the offline reuse plan; it creates no experiment output directory.

A genuinely fresh run that discards completed predictions and reissues attempted
requests conflicts with the no-retry requirement. The scientifically defensible
proposal here retains evidence and continues unchanged prediction assignments.
