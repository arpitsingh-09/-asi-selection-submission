# S1 independent-review and offline-baseline amendment — 2026-11-13

Parent protocol 6e21dfe; recovery amendment 59a9d40. Original `M/PREREG.md`,
configuration, candidates and hashes stay unchanged. No real S1 scoring is permitted
by this preparation amendment. Existing E1 model results were already inspected:
these questions cannot be claimed an untouched confirmatory cohort. A future
eligible lock must disclose that exposure and identify exploratory versus genuinely
independent confirmatory evidence before scoring. No heldout thresholds are tuned.

New independent annotation packet: all 61 E1 focal questions, two pairs each
(A versus B_min and A versus C), 122 pairs. Stable text hashes bind each pair to
exact source fields/bytes. Reviewer packets hide original relation proposals,
variant names, author identities and model outputs. Paper context is provided for
source alignment. No label is prefilled. Two different independent human reviewers
must explicitly annotate same-question and source alignment, with rationales,
identities and dates. Disagreements, ambiguity, duplicates and original-author/AI
self-attestations do not become consensus; retain them as unresolved/excluded.
Human identity/independence require an actual responsible human, not an AI writing
`reviewer_kind=human`. The software checks format/provenance, not real-world identity.
Any adjudication protocol requires a prospective amendment; no silent third-vote
majority is introduced. Original labels remain proposals, not human confirmation.

Recovered source metadata identifies all paper IDs and dates. It does not date
these authored questions. Original inputs, semantic alignment, shuffled-reference
provenance and independently verified same-topic decoys remain unresolved. Never
substitute paper publication for question creation or a source-ID association for
verified generation inputs. All 122 pairs remain ineligible.

Bounded baseline preparation, before scoring: use only the already cached local
`sentence-transformers/all-MiniLM-L6-v2`, revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Six layers, hidden384, ~91 MB weights;
no network, GPU, MPS, Ollama or downloads. CPU threads1, batch4, <=256 unique texts,
<=128 actual tokens (fail rather than truncate), normalized384-dimensional output,
seed20261113, 30-second encoding-loop budget. Exact weight/config/tokenizer hashes
and request hashes are recorded. This prepares 183 unique E1 question vectors in a
new M sidecar; no original embedding cache changes. Encoder construction/import may
take additional time. An explicit training-data cutoff remains unverified and is
not inferred from revision/release dates. Missing evidence continues to block S1.

Fixed S1 statistics remain original protocol: paired focal-question bootstrap,
2000 PCG64 draws seed20261113, Phi accuracy minus B-Q accuracy separately for
minimal paraphrases and near misses, lower95% CI >0.02 for both. Report absolute
accuracy and all four conditions. No changing cosine thresholds on heldout data;
threshold/model configuration must be prospectively locked once eligible annotations,
question dates, references/controls and encoder cutoff are verified. Real execution
still needs that separate committed cohort/model lock; this amendment only allows
label-free vector preparation and synthetic software tests.

Other core tests retain the exact stage4 blockers: unavailable Q/normalization,
dated outcomes, expert battles, human ceiling, original reference groups, fresh
A1 cohorts and training-year model locks. Missing human S1 verification cannot
be bypassed by running those same blocked tests or relabeling old E2 scores.
