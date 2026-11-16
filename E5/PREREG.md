# E5 prospective controlled-development preregistration

2026-11-13. This scoped PREREG.md is committed before the first tests or
experiments in E5. Root PREREG.md and active E2/E6 bindings remain unchanged.
This is a new procedural development experiment, not a held-out lockbox or
independent human validation. No learned model is loaded. No earlier E1/E2
results or model relevance scores are relabeled as E5 semantic results.

## Requirements and scope

Official pages 36–37: Task 1 (3 points) requires mean cosine distance, Vendi,
same-question-cross-encoder classes/count/entropy, four facet dispersions and
joint quality–diversity. Task 2 (3 points) requires >=200 sets of five same-topic
questions with paraphrase-addition, one-facet-addition, deep-clone and vague
rewriting tests. Task 3 (2.5 points) requires five real citing papers sharing
>=3 seeds within 12 months and five questions generated from those same seeds.
Task 4 (1.5 points) tests facet-edit locality and paraphrase stability. Deliver
`diversity(rqs: list[str], facets: bool = True) -> dict` and JSONL axiom sets.

The API supports a strict precomputed semantic backend requiring exact-text
embeddings, calibrated bidirectional identity judgments, facet answers and
explicit quality gates. Missing artifacts fail; no inference fallback. A
passage-relevance cross-encoder is not silently treated as an identity judge.
That neural backend cannot be evaluated without its genuine complete cache.

The executable initial experiment uses fixed nonnegative 512-bin unigram/bigram
hash embeddings and six explicit controlled-language regexes. Its identity
scores are lexical cosine, not a cross-encoder. It is an explicit baseline and
cannot establish semantic model validity or full Task 1 completion. The hashed
map has no fitting step or test-dependent vocabulary/IDF. Vendi uses exp entropy
of the eigenvalues of the PSD normalized Gram matrix. Entropy uses class-size
frequencies, not the log of an unweighted unique-class count.

Pair judgments: same iff both directions >=.65; confidently distinct iff both
<=.35; otherwise uncertain. Exact minimum clique partition of positive edges
creates consistent-within-class blocks and reports nontransitive chains instead
of unsafe connected-component merges. Count interpretation is approximate when
judgments are nontransitive/uncertain. Joint count is the exact maximum clique
of confident-distinct edges restricted to questions passing all three frozen
gates: question mark and 8–100 words; all four facets explicitly extracted; no
vague words `things|various|something|stuff|generally|unspecified`. These are
operational clarity/specificity gates, not scientific-soundness certification.
Exact search is bounded to sets of at most 12; do not silently use a greedy count.

## Frozen dataset

`data/axiom_sets_v1.jsonl`: 200 procedural same-topic five-question sets,
20 domain families times ten purpose/evaluation contexts, with five mechanisms.
Each has five experiment conditions plus controls: base, paraphrase-added (6),
one-facet-added (6), clone (5: one original plus four rewritten forms), vague
rewrites (5), token-length-matched vague rewrites (5), and a decoy swap (5).
Original questions and rewrites are synthetic text, not purported real papers.
Intended semantic labels come from construction and need independent validation.
Neither the lexical scorer nor parser reads the intended labels or edit metadata.

All four edited facets appear 50 times. Full synonym rewrites, not only word
reordering, supply deep paraphrases. Report actual source-word retention, not
an invented guarantee. The vague-length control has exactly the original word
counts under the fixed word tokenizer. Empty-question and question-order controls
are boundary/invariance checks; they do not substitute for empty/shuffled seed
controls on Task 3. No Task 3 held-out real/generated evaluation is permitted
without genuine citation metadata, dates, paired questions and new predictions.

Freeze dataset, generator, scorer, evaluation code and tests with SHA-256 in
`manifest_v1.json`; commit all before any test evaluation. Refuse overwrites.
No hyperparameters, thresholds, patterns or data edits after observing outcomes.
A test failure requires a separately documented version/amendment before a new
experiment, never silent replacement of predictions or results.

## Pass criteria and predictions

All scalar tolerances 1e-8; missing facet scores fail, not silently disappear.
A: absolute change <= tolerance. B: class count/joint count must add exactly 1;
other scalars must strictly increase. C: class/joint/Vendi <=2; class entropy
<=ln(2); raw distance/facet dispersion <=base. D: strict decrease from base.
Only joint count is the figure's primary vague-rewrite target. Raw-distance and
facet B/C/D criteria are explicitly response surrogates because they are not
numbers of distinct questions; do not claim unit equivalence.

Predict pass/fail below means whether >50% of these controlled baseline sets
meet the stated criterion, not a null-hypothesis significance decision.

| Measure | A paraphrase | B facet edit | C clone | D vague |
|---|---|---|---|---|
| Mean pairwise cosine distance | fail | fail | fail | fail |
| Vendi | fail | pass | fail | fail |
| Class count | fail | fail | pass | fail |
| Class entropy | fail | fail | pass | fail |
| Joint quality–diversity count | fail | fail | pass | pass |
| Purpose dispersion | fail | fail | fail | fail |
| Mechanism dispersion | fail | fail | pass | fail |
| Evaluation dispersion | fail | fail | fail | fail |
| Domain dispersion | fail | fail | fail | fail |

The same predictions apply to length-matched D. Class entropy may change after
adding even a correctly clustered paraphrase because its class frequency changes;
that failure is not automatically an implementation bug. Expect perfect question
order invariance, zero empty-question counts, and specificity-gate rejection of
vague questions even after length matching. Decoys may increase distance without
failing structural quality: this baseline does not certify input grounding.

Task 4: expect intended edit locality >50% for every facet, but literal extracted
answer strings stable on <50% of deep paraphrases for every facet. Purpose and
evaluation may be hardest to distinguish semantically; a measured tie must be
reported as a tie, never a fabricated ranking. Literal-string stability is not
an independent semantic reliability estimate. Report that limitation.

## Statistics and outputs

Report every measure/axiom numerator, valid denominator (all 200), pass rate and
95% percentile bootstrap interval. Resample the 20 domain/topic families, keeping
all ten dependent sets in a sampled family together; 10,000 draws, default_rng
seed 20261113, batches of 250. Bootstrap numerator/denominator together for
unequal-sized subgroup counts. Do not treat question pairs as independent.
Report facet-stability/locality intervals with the same family clustering.
Fewer than two independent clusters yields no inferential interval.

Save one row per original set and raw condition metrics, manipulation pass flags,
length/word-overlap diagnostics, facet-reliability rows, control rows and summary
in a fresh versioned output directory. No held-out evaluation, real/model
separation, semantic accuracy, training-cutoff or scientific-quality claim is
inferred from this procedural benchmark. No old E1/E2/E6 experiment is rerun.

## Task 3 deferred prerequisites

A constructor validates Semantic Scholar source provenance, exact dates,
>=3 shared seed IDs and a calendar-12-month window for five unique real papers.
Never infer shared citations from titles or similarities. Actual real questions
need source passages, and five generated questions must identify the same seeds
and generator provenance. Bootstrap dependent seed/paper-connected groups as
clusters. Compare paired generated-minus-real metrics/facets with intervals only
when enough independent groups exist. Dates/length, field/venue, author selection,
RQ extraction, generator and quality gates can all confound source separation.
The attempted Semantic Scholar graph endpoint was inaccessible via the browser
in this session; no cached complete group was located among inspected valid
E1/E2 sources. Do not fabricate a known-group experiment to fill this gap.

## Protected work and logs

CPU NumPy/text processing only, one thread; no Ollama/GPU/model loading, original
cache writes or E2/E6 edits. Root NOTEBOOK.md and AI_LOG.md remain protected per
user instructions. Substantive assistant use and decisions are recorded in
E5/AI_USAGE.md and E5/SESSION_NOTES.md for later authorized root-log integration.
This scoped-log deviation is disclosed, not a claim that root submission logs
are already complete. Existing history is preserved; no push.
