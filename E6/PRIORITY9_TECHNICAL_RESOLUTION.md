# Priority 9 technical resolution — proposed Gemma draft

Status: DRAFT, no approvals or confirmatory execution. The current Gemma-based
protocol is the proposed governing draft; the older protocol is preserved.

R44 evidence: the original assignment requires held-out data-based scoring and
synthetic recovery. HypoBench §3 defines practical utility as hypothesis-guided
prediction on test samples; its official evaluation page names accuracy/F1.
Sources: https://arxiv.org/html/2504.11524v1 and
https://chicagohai.github.io/HypoBench/evaluations/ . The local source config
`data/HypoBench-datasets/synthetic/election/level2/config.yaml` supplies labelled
observations to hypothesis generation. No OpenAlex access was used.

The legacy E6 design supplied each TEST observation to generation and scored the
resulting hypotheses on that same observation. Hiding its label did not establish
held-out generalization. It cannot be the confirmatory inductive utility design.
The preserved 501-row manifest remains valid as evaluation data, not as generation
inputs. Its legacy conversion interface is retained for compatibility, while
final-mode safeguards reject TEST evidence generation.

`prepare_hypobench_inductive.py` implements a source-hash-bound, TRAIN-only proposal:
20 disjoint sets × 20 labelled TRAIN observations, seed 2026, deterministic hash
sampling without stratification. TRAIN outcome labels are observed evidence;
TEST labels and dataset ground truth are excluded from generation. Each of the
seven arms generates one unchanged six-hypothesis set per evidence set. Label-blind
prediction jobs apply it to all 501 TEST rows. The statistical unit is the TRAIN
evidence input set, not the repeated TEST observation. Unbatched prediction cost is
20 × 7 × 501 = 70,140 calls; recovery/judges are additional. Counts, sampling and
primary aggregation still require approval. No Normal/Counterfactual condition or
missing third-party examples are invented. NOTEBOOK.md records prior researcher
inspection of all split labels; TEST is isolated from this new generation pipeline,
not claimed never historically inspected.

Accuracy scoring and the source-backed 14-reference recovery remain supported.
Fourteen-reference recall is explicitly not paper HDR. `score_reference_hdr`
implements FDR × relationship correctness from explicitly supplied reference
feature IDs, discovered IDs, bounded relationship scores and provenance. Actual
source-grounded feature mapping and judge results are absent; no HDR was computed.
Bootstrap inference would be conditional on the shared fixed TEST set.

Token feasibility: 8192 GENERATED tokens remains the numeric proposal, unset in
active configuration. At 2048 output tokens/call, the current single-attempt
workflows have 1 direct/control call, 3 QH-rand calls and 4 QH-sel calls, counting
shared preparation per participating arm. Four full outputs plus four one-token
count probes request 8196 tokens: the final call must respect the remaining budget,
and completion is not guaranteed. Prompt tokens affect context/compute, not this
cap. Prior total-token profiles do not estimate generated-cap adequacy.

Saved runtime evidence verifies model/tokenizer and a 32-token output probe; model
metadata reports 131072 context. It does not validate the proposed 2048 output
limit or larger context performance. Full-reference candidates contain 10–121
abstracts; fixed initial prompts reach 178471 characters (178483 UTF-8 bytes).
The separately proposed first-ten-reference policy reduces maximum fixed initial
prompt size to 23123 characters (23132 bytes). Length reports use the existing
generic DEVELOPMENT task only for feasibility; exact final task wording is unapproved.
No exact offline tokenizer is installed and no new model call was made. Character
counts are not token counts and do not prove context fit. Dynamic prompts remain
subject to exact runtime checks.

`fixed_token_cap_proposal_v3.json` therefore proposes context 32768, output 2048,
and counting-probe context 131072, with the same 8192 generated-token cap. All are
unapproved. At the old 8192 context, reserving 2048 output allows only 6144 prompt
tokens. At 32768 it allows 30720. A byte admission guard rejects oversized counting
probes; near-window counts fail closed. Count probes use the larger explicit
context, then the controller checks exact measured prompt + requested output
against the generation context. It blocks rather than truncate evidence or quietly
reduce a context-driven output request. Backend prompt-count parity remains
required. This is a safeguard, not a certificate of runtime memory/performance or
independent proof that the backend never truncates; development verification of
the chosen context/output settings remains necessary before execution.

Priority 10 preparation: data/literature plans are saved with source hashes,
unapproved status and execution disabled. `execution_preparation.py` exports real
successful normalized hypotheses to assignment JSONL names, keeps failed cells in
a separate ledger and refuses overwrites. Arm workflow generated-token cost is
explicitly repeated/non-additive across its six hypothesis lines; no per-hypothesis
token allocation is fabricated. Historical total-token envelopes are rejected.

Remaining decisions are the ten existing checklist groups, now with these exact
replacements: adopt the proposed governing draft; TRAIN-only sampling 20×20;
first-ten-reference evidence selection; 32768 context / 2048 output / 8192 generated
cap; exact tasks, donor cohorts, run order, retry/failure denominators, primary
contrasts/evaluators and recovery definition, real prior-question corpus, review
policy, predictions/magnitudes, bootstrap/multiplicity and error-analysis sampling.
No numeric limit, sampling method, reviewer count or metric choice was approved.

Readiness: the held-out adaptation, context safeguards, export and execution plans
are reviewable. Priority 9 is ready for researcher decisions, NOT a clean final
preregistration sign-off: operational choices, genuine prior-question data,
annotations/reviews, grounded HDR inputs if required, chosen-limit development
verification and frozen final execution/donor/analysis integration remain. The
seven-arm final runner still deliberately blocks execution. No commit was made.

Validation: complete E6 discovery passes 303 tests and all ten protocol validator
self-tests pass. Source/proposal tests include actual-source identity, split
isolation, fixed hypotheses across TEST jobs, mixed-cohort rejection, HDR algebra,
context blocking without cap reduction, seed/provenance export checks and exclusive
writes. No model client was run. Feasibility-report prompt hashes use canonical
JSON-string hashing; runtime prompt hashes use raw UTF-8 hashing.

## Runtime/integration continuation

The minimal live attempt was blocked by environment loopback permissions before
any model inference or actual prompt count. This is an environment failure, not
evidence that Gemma lacks capacity. See `RUNTIME_INTEGRATION.md` and the retained
attempt report. The production counting context now equals generation context
32768, avoiding an unverified larger allocation; cap proposal v4 supersedes v3
without lowering the 8192 generated-token allowance.

TRAIN all-seven-arm execution, source-bound empty/shuffled controls, explicit
seed/run-order validation, independent prediction transport batches, genuine HDR
input binding, mandatory JSONL and integrity-checked resumable checkpoints are
implemented and mock-tested. Final config/researcher/runtime/source/Git gates
still block all real callbacks. Same-task TRAIN shuffling shares the underlying
mechanism; its scientific interpretation remains an approval decision. Genuine
HDR/corpus/review data are not supplied by software. Latest verification:
321 E6 tests and all ten validator self-tests pass; approvals remain pending.
