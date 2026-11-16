# E2 Five-Paper Paraphrase Pilot — Manual Review Draft

- Candidate version: `E2/data/paraphrase_pilot5_v23.jsonl`
- Review type: preliminary abstract-level semantic-preservation review
- Status: DRAFT — NOT FINAL VALIDATION
- Review date: 2026-10-26
- Scoring authorized: no
- Dataset statuses changed: no

## Important limitations

These notes record preliminary comparisons of candidate titles and abstracts
against the source abstracts and the recorded source claims. They are not final
accept/revise/reject decisions. Any unresolved wording or claim must be checked
against the source before a final decision.

The original generation failures and subsequent manual revision drafts remain
part of the provenance. This review does not retroactively change that history.

## Checklist applied to every paper

1. Candidate title preserves the source subject and scope.
2. Every original claim remains supported by the candidate abstract.
3. Named components, methods, and relationships are preserved.
4. No unsupported result, dataset, contribution, or performance claim appears.
5. Conclusion strength is preserved.
6. Uncertain wording is identified for further review.

## Paper 1 — 2012.14359v1

**Topic:** Neurosymbolic visual sensemaking for autonomous driving.

- Title: provisionally consistent with the source subject and scope.
- Claims: the candidate retains ASP-based neurosymbolic sensemaking,
  integration of vision and semantics, the modular framework, benchmarks,
  human-centred use cases, and domain independence.
- Methods and relationships: no clear mismatch identified in the abstract-level
  comparison.
- Unsupported additions: none identified in the preliminary comparison.
- Conclusion strength: appears preserved.
- Follow-up: verify that the shortened title does not materially narrow or
  distort the source's emphasis on vision and semantics.

**Status:** Pending full manual validation.

## Paper 2 — 2012.14371v3

**Topic:** Tensor representations for action recognition.

- Title: provisionally consistent with the source subject and scope.
- Claims: SCK, DCK, SCK(+), multimodal inputs, linearized descriptors,
  evaluation settings, higher-order feature relationships, EPN, and TPN are
  represented in the candidate abstract.
- Methods and relationships: the candidate preserves the stated roles of SCK
  and DCK and their relationship to action recognition.
- Theorem wording: the candidate describes the order-r tensor, Z*-dimensional
  features, the binomial detector count, r-dimensional subspaces, and the
  higher-order-occurrence detection condition.
- Unsupported additions: none identified in the preliminary comparison.
- Conclusion strength: appears preserved.
- Follow-up: verify the theorem's wording against the source paper, not only
  the source abstract.

**Status:** Pending full manual validation.

## Paper 3 — 2012.13915v2

**Topic:** Syntax-guided Transformer language representation.

- Title: provisionally consistent with the source subject and scope.
- Claims: syntax-guided attention, SDOI-SAN, the original Transformer SAN,
  the dual-context architecture, application to typical Transformer encoders,
  and all three benchmark task types are retained.
- Methods and relationships: the two SAN components and their relationship
  appear preserved.
- Unsupported additions: none identified in the preliminary comparison.
- Conclusion strength: appears preserved.
- Follow-up: confirm that “dual-context” accurately conveys the source's
  “dual contextual architecture.”

**Status:** Pending full manual validation.

## Paper 4 — 2012.14271v3

**Topic:** Fully automated manga translation.

- Title: provisionally consistent with the source subject and scope.
- Claims: all four contributions are represented: the multimodal
  context-aware framework, automatic corpus construction, an evaluation
  benchmark, and a comprehensive fully automated system.
- Methods and relationships: image-derived context, speech-bubble context,
  corpus construction without manual labeling, and evaluation are retained.
- Novelty: the candidate retains the source's first-to-incorporate-image-context
  and first-comprehensive-system claims.
- Unsupported additions: none identified in the preliminary comparison.
- Conclusion strength: appears preserved.
- Follow-up: verify the novelty claims against the source paper. The correction
  to `source_claims` in v23 is an inventory correction, not validation.

**Status:** Pending full manual validation.

## Paper 5 — 2012.14961v1

**Topic:** Fair deep anomaly detection.

- Title: provisionally consistent with the source subject and scope.
- Claims: adversarial training to reduce the relationship between sensitive
  attributes and learned representations, two fairness measures, unfairness
  in existing methods, and the reported fairness/performance trade-off are
  represented.
- Methods and relationships: Deep Fair SVDD and adversarial training are
  correctly associated in the candidate abstract.
- Unsupported additions: none identified in the preliminary comparison.
- Conclusion strength: the qualified claim of largely removing unfairness with
  minimal performance loss is retained.
- Follow-up: confirm that “reduce the association” faithfully represents the
  source's “de-correlate the relationships” without implying a stronger
  mathematical guarantee.

**Status:** Pending full manual validation.

## Overall state

- Five preliminary abstract-level comparisons documented.
- No final accept/revise/reject decisions recorded.
- No `manual_validation_status` fields changed.
- No `scoring_authorized` fields changed.
- No scoring run.
- `E2/data/scoring_results.jsonl` remains untouched.

## Next steps

1. Complete source-grounded checks for each candidate, including the source
   paper where a claim or method requires more detail than the abstract gives.
2. Resolve the follow-up wording checks above.
3. Record explicit final decisions only after all six checklist items are
   addressed for each paper.
4. Keep scoring disabled until validation is complete and the required
   authorization is explicitly granted.
