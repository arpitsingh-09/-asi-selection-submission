# E6 — minimum researcher approval checklist

Applied components are recorded in RESEARCHER_APPROVAL.json; remaining choices below are proposals. Assignment constraints and technical facts do not need
separate approval. Use these **10 grouped choices**, linked to the original IDs,
instead of treating every unresolved configuration field as a new decision.
The JSON record retains all 26 IDs and all existing approval fields.

**Governing protocol:** the current Gemma-based protocol has been adopted by explicit researcher instruction and supersedes the older Qwen draft. Remaining methods and full artifact sign-off are pending. The older
protocol and its unauthenticated approval label are preserved; no prior approval
has been inferred or erased. Protocol precedence is settled; predictions in the first choice remain pending.

| Choice (original IDs) | Proposed value | Why needed | Consequence | Recommendation |
|---|---|---|---|---|
| 1. Governing plan and predictions (1) | Current Gemma E6 is adopted as governing; prior work remains development. Predict QH-sel > QH-rand, D > empty/shuffled; record directions and expected magnitudes for every required testbed/metric. | Reconcile the older approval claim and meet “predict first.” | Current study can proceed prospectively; older protocol is superseded and preserved. Magnitudes are still missing. | Ratify prospectively after resolving the remaining methods; retain honest predictions, never infer approval from a document title. |
| 2. Scope and sample (2,3,5) | Both testbeds, separate summaries; 20 disjoint TRAIN evidence sets × 20 labelled observations; each generated set scored on all 501 TEST rows; the proposed hash-ranked 100 literature targets, seed 2026, no strata. | Assignment fixes both testbeds and minimum 100, but not these exact sources/IDs or strata. | Minimum literature cost; no pooled score; TRAIN sampling is proposed; TEST rows are evaluation items, not experimental units. | Use the prepared 100; approve the implemented inductive sampling proposal before freezing. |
| 3. Task and controls (4,14,15) | Fixed generic task per testbed, evidence-only source fields; first ten cited abstracts in preserved manifest order for literature; audit empty tasks; one seeded no-self/no-reuse evidence derangement within each testbed. | Exact task wording and donor cohorts affect what the controls measure. | Avoids target/label leakage. Within-task TRAIN swaps share the global mechanism and are not guaranteed negative controls. | Approve exact task strings, donor cohorts and control interpretation; a different-mechanism donor policy requires adaptation. |
| 4. Model and runs (8,9,10) | Verified Gemma 3 12B; temperature 0, top_p 1, seed 2026; one replicate; hash-seeded arm order; 2048 output/32768 context limits, with 32768 counting-probe context. | Assignment mandates common model/settings, not their values. | Low cost and reproducible ordering; limits remain unmeasured and context must fit prompts independently. | Use saved Gemma evidence if current plan governs; check proposed limits on DEVELOPMENT only if needed. |
| 5. Numeric budget (16) | **8192 generated tokens per input set/arm**, intermediate/discarded/retry/probe outputs charged, prompt tokens recorded separately. | Unit is mandated; numeric cap is a cost choice. | Selection may exhaust its cap; historical total-token profiles are not comparable estimates. | Use the v4 proposal as a prospective cost limit; do not wait for ten profiles. |
| 6. Selection policy (13) | Keep existing Boolean duplicate decisions, complete-link/earliest representative, configured weighted selector and seed-2026 random rule; block when fewer than three remain. | Assignment requires a fixed same-question/ranking rule; exact mechanics and fallback are choices. | Keeps existing code; differs from the older protocol's equal-weight selector and random arm without deduplication. | Retain current implementation only with explicit methodological approval. |
| 7. Failures and retries (11,12) | One content attempt, no quality regeneration or replacement; retain failed cells; no transport/timeout retry unless explicitly specified. | Missingness affects estimands and budget equality. | Failures remain visible; literature/diversity failure scores still need exact definitions. | Approve outcome-specific failure/denominator rules; never substitute a 1–5 score of zero silently. |
| 8. Outcomes and evaluators (18–23) | Separate per-TRAIN-set held-out accuracy and literature reconstruction; same Gemma judge, 1–5 best similarity plus Boolean same-question; 15-pair hypothesis diversity; one type judgment/question; optional pairwise judge disabled. Formal R44 HDR requires real feature mapping/scores; 14-reference recall is a separate metric. Prior-question rate uses genuine sourced questions and a fixed binary matcher. | Required metric families are mandated; scales, models, primaries, corpus scope and aggregation are not. | Shared-model bias; questionless arms N/A; prior-question rate stays blocked without real sources. | Prefer minimal evaluator family and no optional judge; approve exact rubrics, primary contrasts and missing-annotation rules. Supply/identify the real corpus. |
| 9. Extraction and manual checks (24) | Fixed extraction prompt; first 20 hash-ranked targets; two independent reviewers with independent adjudication; proposed review guide. | Fixed extraction and 20 hand checks are mandated; reviewer count and sampling/adjudication are not. | Requires real reviewers; negative checks require correction/review before use. | Keep prepared cases; two reviewers is the current recommendation, not an assignment requirement. A one-reviewer replacement is possible with a specified quality-control rule. |
| 10. Analysis and error review (25,26) | Paired input-set bootstrap, 10000 replicates, seed 2026, percentile 95% CIs; all 21 applicable arm contrasts with unadjusted marginal intervals and no adjusted significance claims; review 20 input sets end to end across seven arms, seed-fixed before inspecting outcomes. | 95% paired bootstrap and 20-case error analysis are mandated; contrast family, RNG/statistic, missingness and case selection require choices. | Broad multiplicity correction reduces power; human error review is distinct from target-extraction checks. | Keep simple paired analysis; explicitly choose primary family, RNG/statistic, failure handling and 20-case sampling. Freeze library versions before analysis. |

Administrative work needs no extra scientific choice: compute hashes, preserve IDs,
export the assignment JSONL schema, and sign the final artifact set. Original IDs
6, 7 and 17 remain in the record as implementation/sign-off items; their pending
status is not changed into an approval. Other IDs contain mixed mandated and
judgment components; only the latter are being asked here. Final artifact sign-off
and all execution gates still apply.

Implementation can resolve hash schema integration, donor/evaluator configuration,
source-safe generation inputs, JSONL export and run/analysis commands after the
chosen policies are known. Genuine dependencies are the protocol-precedence
answer, researcher choices/predictions, a sourced prior-question corpus, real
extractions and actual hand reviews. No additional OpenAlex retrieval is required
merely to approve the already prepared sample. No confirmatory execution is needed
to finish these decisions.

Runtime/integration update: `RUNTIME_INTEGRATION.md` records the actual blocked
local-runtime attempt and exact DEVELOPMENT-only command. No new actual prompt
counts or 32768/2048 verification exist yet. Generation/counting share 32768;
metadata 131072 is not an extra runtime allocation. The proposed numeric seed is
now represented explicitly as null until approved. TRAIN orchestration, controls,
independent transport batching, checkpointed HDR/accuracy scoring and JSONL export
are integrated behind real gates. None of these implementation facts approve a
method. Literature execution and final analysis scheduling remain separate work.
