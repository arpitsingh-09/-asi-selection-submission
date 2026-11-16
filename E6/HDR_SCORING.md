# TRAIN-only HDR compilation

Implemented `E6/hdr_pipeline.py`; executed offline into
`E6/data/hdr_scoring_v2/`. No model server, literature extraction outputs,
process state, locks, or checkpoints were accessed. Existing TRAIN checkpoints
were read only. Frozen settings and Git HEAD were unchanged.

The compiler verifies all 125 prepared cells against their source generation
checkpoints, verifies the frozen ground-truth file, and scans six generated
hypotheses per cell against all 14 original source rules for exact full-rule
identity. There are **0 exact matches**. Nonmatching text is unknown, not an
incorrect judgment. **0/125 HDR cells are scored**. All eight failed generation
cells and seven unresolved set-0007 arm cells are preserved separately.

Implemented scoring:
- Uses existing source-bound `bound_hdr_score` and FDR × relationship-correctness
  scoring; never replaces HDR with 14-rule recall.
- Accepts a source-grounded feature mapping with actual definition provenance;
  rejects the existing unapproved three-field grouping proposal as a denominator.
- Accepts actual discovered-feature/relationship judgments with judge identity,
  time and supporting evidence; prevents failed/foreign/0007 cells from scoring.
- Can objectively assign discovery and correctness 1 only when all original
  rules mapped to every reference feature are reproduced literally. Partial
  identity cannot justify absent features or an invented aggregation rule.
- Uses immutable input/implementation identities, per-cell checkpoint hashes,
  exclusive outputs and locking; replays scoring checkpoints without inference.
- Exports only genuine complete payloads into `hdr_inputs_actual.json` in the
  format accepted by existing TEST readiness. The current export is `{}`.
- Readiness can consume the compilation with `--hdr-compilation`; pending cells
  remain blocked. No full readiness audit was repeated.

Semantic-call blocker: frozen `evaluation_config.json` specifies no HDR discovery
or relationship judgment prompt/policy. Prompt 14's full-hypothesis equivalence
matrix is the separately defined planted-recovery metric. It cannot establish
feature discovery or relationship correctness. Inventing another prompt,
selecting a feature denominator, or treating recovery recall as HDR would change
methods; none was done. `--execute-judgments` therefore blocks before client
construction. No TRAIN model judgment was attempted or repeated.

Eight focused HDR tests plus six readiness safety tests pass. Tests include
known-value HDR arithmetic, exact-identity scoring, absent-value handling,
rejection of fabricated objective claims, checkpoint replay, and network denial.

Next required evidence:
1. A domain-justified feature definition/mapping supported by the original source,
   with actual author/time/justification, not automatic promotion of the pending
   three-field source grouping.
2. Actual per-cell discovery/relationship judgments from an attributable source.
   Existing pending forms provide the exact hypotheses and ground-truth quotes.
   The frozen files do not supply an executable HDR semantic judging policy.

Once those actual files exist, the exact offline scoring command is:

```sh
cd /Users/arpit/asi-selection
python3 E6/hdr_pipeline.py --output-dir E6/data/hdr_scoring_completed_v1 --mapping E6/data/HDR_mapping_actual.json --judgments E6/data/HDR_judgments_actual.json
```

`HDR_mapping_actual.json` has `approved_HDR_denominator: true` only after actual
justification, `reference_feature_ids`, `feature_mapping` with original
`ground_truth_indices`/`source_texts`, `ground_truth_source_sha256`,
`feature_mapping_sha256`, and `definition_provenance` containing real `author_id`,
`defined_at_utc`, `source_supported_justification`. This is evidence of a grounded
definition, not permission for a new unregistered feature convention.

`HDR_judgments_actual.json` maps generation input-set ID → arm → existing
`bound_hdr_score` payload. Each judgment's `provenance.judge_provenance` must
include actual `method`, `judge_id`, `judged_at_utc`, and `evidence`. Empty
`discovered_feature_ids` is an explicit negative judgment only with genuine
support, never the default for missing annotation. No actual input file,
reviewer identity, semantic label or score is fabricated by this documentation.

## Current offline assessment and reduced human worklist

`E6/data/hdr_scoring_v3/report.json` rechecks all 125 source-bound TRAIN records:
0 objective full-rule identities, 0 genuine HDR scores. Its
`hdr_inputs_actual.json` remains `{}` and is accepted by the existing readiness
loader (`--hdr-compilation E6/data/hdr_scoring_v3`); all 125 HDR cells remain
blocked. No held-out accuracy process or outputs were used.

`E6/data/hdr_independent_review_v1/independent_review.md` contains one shared
14-rule source inventory, one denominator-definition decision, and 107 blinded
set-level review cases. The coordinator mapping preserves all 125 original
records and avoids 18 repeated exact-set reviews. No human labels are supplied.

The original assignment requires R44 data-based scores but supplies no feature
unit. R44 section 3 defines HDR over true features, separately from relationship
correctness; Appendix A matches input variables separately from outcomes.
Source: https://arxiv.org/html/2504.11524v1#S3 . Locally, metadata lists four
feature categories; the 14 ground-truth rules have three predicate-field groups,
including four template rules. None of these counts by itself specifies the
required source-grounded denominator or how multiple rules become one feature
relationship score. The existing three-group proposal remains unapproved.

Next: an independent domain reviewer documents the source-supported feature
unit, exact rule mapping and multiple-rule/claim interpretation, with identity,
UTC time and rationale; unresolved methodological choices need researcher
resolution rather than silent defaults. Then review discovery and relationship
correctness for the 107 distinct sets and expand source-bound payloads to the
125 records using the coordinator map. Existing `compile_hdr` and
`bound_hdr_score` perform the arithmetic and readiness export once actual
judgments exist. Absent exact matches are unknown, never zero judgments.
