**Status date: 2026-11-17.** This report consolidates E5 evidence already saved in the repository. It does not run model inference or make external API requests. The only completed quantitative experiment is a 200-set procedural lexical/rule baseline; results must not be interpreted as semantic diversity validation.

## Rubric status at a glance

| Requirement | Status | Evidence and remaining gap |
|---|---|---|
| Task 1: diversity measures and API | **Implemented; semantically incomplete** | `diversity.py` exposes all requested output families and the required API. The executed backend is fixed hash lexical cosine plus regex facets and lexical identity thresholds, not a same-question cross-encoder. The strict cached semantic backend is only an interface and has no qualifying cache, so semantic Task 1 is not validated/completed. |
| Task 2: four anti-gaming axioms on ≥200 sets | **Controlled baseline completed; official semantic objective partial** | 200 five-question sets, four primary manipulations, length-matched vague control, all 1,400 condition scores and cluster-bootstrap intervals are saved. Labels are synthetic construction intent; no independent semantic/human validation, and baseline is lexical/rule-based. |
| Task 3: known groups | **Incomplete / blocked** | No eligible real-paper citation groups were evaluated; candidate verification records 0 verified lookups and 0 protocol-eligible groups. No generated questions paired to the same verified seed sets and no group comparison/intervals exist. |
| Task 4: facet locality and paraphrase stability | **Baseline measurement completed; semantic reliability incomplete** | Saved regex parser results show locality and literal-string stability. Templates determine these outcomes; they cannot identify semantic facet reliability or the least reliable semantic facet. |
| Deliverable: `diversity(rqs: list[str], facets: bool = True) -> dict`, JSONL sets | **Implemented** | `diversity.py` and `data/axiom_sets_v1.jsonl`; the executed benchmark is explicitly the lexical/rule baseline, not a semantic model. |

## Diversity function and methodology

The default `LexicalBaseline` maps lowercased unigram and adjacent-bigram tokens to a fixed, nonnegative 512-dimensional hash vector (Blake2b token hash); it performs no corpus fitting. Mean pairwise cosine distance is the mean of `1 − cosine` over unordered pairs. Vendi is `exp(Shannon entropy(eigenvalues(K/n)))` for the normalized cosine Gram matrix. These are lexical surface-form measures, sensitive to wording and length; they are **not semantic diversity measures**.

Pair identity under the default baseline uses lexical cosine as a proxy: a pair is same only when both directions are at least 0.65, confidently distinct only when both are at most 0.35, otherwise uncertain. Same edges are partitioned into exact within-class cliques to avoid unsafe connected-component chaining; nontransitivity and uncertain pairs are reported. Class entropy uses class-size frequencies. Facets (purpose, mechanism, evaluation, domain) are extracted by six fixed regular expressions designed for the controlled question templates. Facet dispersion applies the same lexical hash cosine to extracted strings.

The quality-diversity count is the exact maximum subset passing all three frozen operational gates (question mark and 8–100 words, all four parsed facets present, and no listed vague terms) with every pair confidently distinct. The gates measure form and specificity, not scientific soundness. Exact subset search is bounded to 12 questions. `CachedSemanticBackend` requires text-bound embeddings, calibrated bidirectional same-question scores, facet answers, and explicit gate judgments with provenance. It fails closed when these cached artifacts are missing; no model fallback or inference was used.

## Experiment setup and evidence

The frozen dataset has 200 procedural sets (20 topic families × 10 sets), each with five base questions and condition variants: paraphrase addition, one-facet addition, clone (one original plus four rewrites), vague rewrite, length-matched vague rewrite, and decoy. It is synthetic controlled language, not real-paper questions. The saved v2 run contains 200 rows each in `results.jsonl`, `facet_reliability.jsonl`, and `controls.jsonl`, plus `summary.json`; each set has seven condition scores (1,400 total). The backend name is `fixed_hash_lexical_and_controlled_regex_baseline`; `semantic_cross_encoder` is false; `new_model_inference` is false. The preregistered pass rule is majority of sets (>50%); uncertainty intervals are 95% percentile cluster bootstrap over 20 topic families, retaining each family’s ten sets together (10,000 draws, seed 20261113). Results and intervals below are the saved values, independently checked against per-set files.

# E5 — Final report: saved diversity experiments

## Scope and status

This report summarizes the saved run in
[`results/controlled_baseline_v2/`](results/controlled_baseline_v2/). It does
not rerun the scorer, call a model, regenerate the dataset, or change the
preregistration. The run scored 200 procedural five-question sets from 20
topic families (ten sets per family), with 1,400 set-condition scores. The
backend was `fixed_hash_lexical_and_controlled_regex_baseline`; no learned
model inference was performed.

**Controlled-baseline experiment:** complete for the preregistered 200-set
baseline run, including all four primary manipulations, the length-matched
vague control, saved facet records, and cluster-bootstrap intervals.
**Official Task 2:** partially satisfied. The requested conditions and
pass-rate reporting exist, but intended semantic labels are construction
labels without independent human validation, and the tested scorer is a
lexical/rule baseline rather than a validated semantic diversity system.
**Official Task 4:** partially satisfied. The saved baseline shows intended
facet locality and exact-string stability outcomes, but cannot determine
semantic facet reliability or rank a least reliable facet. These limits are
not repaired by the controlled results.

## Task 2: anti-gaming axioms

The preregistered decision is whether more than half of the 200 sets pass an
axiom for a measure. `P`/`F` below is the prediction in `PREREG.md`; the
reported rate is the observed set-level pass fraction, with its 95% interval.
`✓` means the majority outcome (rate > 0.5) agreed with the prediction;
`✗` means it did not. An exact 0.5 would count as a failure under this rule.
Intervals use 10,000 percentile bootstrap draws, seed 20261113, resampling 20
topic families and retaining each sampled family's ten sets together. Counts
are out of 200. For B, class count and quality-diversity count require an
increase of exactly one; the other measures require a strict increase. The
vague-rewrite result for measures other than quality-diversity is a
preregistered response surrogate, not a claim that those measures count
quality-filtered distinct questions.

| Measure | A: add paraphrase | B: add one-facet edit | C: clone set | D: vague rewrite | D-length: length-matched vague |
|---|---|---|---|---|---|
| Mean pairwise cosine distance | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 165/200 (0.825; [0.770, 0.880]) ✗ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 200/200 (1.000; [1.000, 1.000]) ✗ |
| Vendi score | F → 0/200 (0.000; [0.000, 0.000]) ✓ | P → 200/200 (1.000; [1.000, 1.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 200/200 (1.000; [1.000, 1.000]) ✗ |
| Distinct-question count | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 60/200 (0.300; [0.260, 0.340]) ✓ | P → 183/200 (0.915; [0.875, 0.955]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ |
| Class entropy | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 60/200 (0.300; [0.260, 0.340]) ✓ | P → 183/200 (0.915; [0.875, 0.955]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ |
| Quality-diversity count | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | P → 200/200 (1.000; [1.000, 1.000]) ✓ | P → 200/200 (1.000; [1.000, 1.000]) ✓ | P → 200/200 (1.000; [1.000, 1.000]) ✓ |
| Purpose dispersion | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 50/200 (0.250; [0.230, 0.270]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ |
| Mechanism dispersion | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 20/200 (0.100; [0.060, 0.140]) ✓ | P → 200/200 (1.000; [1.000, 1.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ |
| Evaluation dispersion | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 50/200 (0.250; [0.230, 0.270]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ |
| Domain dispersion | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 50/200 (0.250; [0.230, 0.270]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ | F → 0/200 (0.000; [0.000, 0.000]) ✓ |

The four primary outcomes all match their majority-level predictions for this
baseline: A changes the lexical representation instead of preserving the
measures; B has mixed responses, with Vendi most often increasing; C is
usually bounded by two classes and by two on quality-diversity, while raw
distance and Vendi often rise; D always lowers the operational
quality-diversity count, while most other measures do not satisfy their
strict-decrease rule. Length-matched D also lowers quality-diversity in all
sets, but increases cosine distance and Vendi in all sets; this demonstrates
that those two metrics respond strongly to the rewritten wording. Prediction
agreement is about the preregistered majority outcome, not evidence that the
baseline is semantically valid.

### Examples from saved set `e5-000`

These are actual rows from the frozen controlled dataset and saved output;
they are synthetic procedural examples, not real research questions.

- **A, paraphrase addition:** base question “For medical image
  classification, does data augmentation help reduce predictive error,
  measured by held-out error?”; added rewrite “In assigning diagnostic labels
  to clinical pictures, can make fewer incorrect predictions be achieved
  through synthetic transformations of training examples, assessed using the
  error rate on unseen labelled instances?” The saved distinct count changes
  from 1 to 2 and mean cosine distance from 0.144 to 0.383, so this set fails
  A's invariance criterion.
- **B, purpose edit:** the saved edit is “For medical image classification,
  does data augmentation help improve noise robustness, measured by held-out
  error?” The controlled parser changed only the purpose facet; the saved
  locality flag is true. The six-question set's quality-diversity count stays
  at 1 rather than increasing by one, illustrating that facet locality and
  the distinct-count axiom are separate outcomes.
- **C, clone:** `e5-000` contains one original and four deep rewrites of that
  question. Saved distinct count and quality-diversity count are both 2
  (pass); mean pairwise cosine distance is 0.509 versus 0.144 for base
  (fail), showing the lexical baseline is sensitive to wording.
- **D, vague rewrite:** the saved variants include “How might various
  approaches improve things in general?” The quality-diversity count falls
  from 1 to 0. Under the length-matched vague condition it also falls to 0,
  while the distinct count stays 1 and cosine distance is 0.000 for this set.

## Task 4: facet locality and paraphrase stability

| Saved baseline measurement | Result |
|---|---:|
| Intended edited facet changes, and no other extracted facet changes | 200/200 (1.000; 95% CI [1.000, 1.000]) |
| Purpose edit localized | 50/50 (1.000; [1.000, 1.000]) |
| Mechanism edit localized | 50/50 (1.000; [1.000, 1.000]) |
| Evaluation edit localized | 50/50 (1.000; [1.000, 1.000]) |
| Domain edit localized | 50/50 (1.000; [1.000, 1.000]) |
| Exact extracted facet string stable under paraphrase: purpose | 0/200 (0.000; [0.000, 0.000]) |
| Exact extracted facet string stable under paraphrase: mechanism | 0/200 (0.000; [0.000, 0.000]) |
| Exact extracted facet string stable under paraphrase: evaluation | 0/200 (0.000; [0.000, 0.000]) |
| Exact extracted facet string stable under paraphrase: domain | 0/200 (0.000; [0.000, 0.000]) |

All 200 constructed one-facet edits moved their intended facet without moving
the other three under the fixed regex parser. The saved records therefore
show a four-way tie in edit locality. Exact extracted strings were stable on
0/200 paraphrases for every facet; all 200 paraphrases had less than 75%
source unique-word retention, and none met the preregistered 0.9–1.1
length-ratio condition. On these literal-string measures, no facet is the
least reliable: all tie. This does **not** establish that all facets are
equally reliable semantically. The templates deliberately replace facet
wording, and the regex parser returns those literal spans; no independent
semantic facet annotations were collected. A claim that purpose or evaluation
is least reliable would go beyond these saved results.

## Limitations and remaining blockers

- The 512-bin unigram/bigram hash vector makes cosine distance and Vendi
  lexical/length sensitive. It is not an embedding-based semantic measure.
- The identity judgments use symmetric lexical cosine thresholds (same at
  0.65, distinct at 0.35), not a trained or calibrated same-question
  cross-encoder. Paraphrases can therefore be split into separate classes;
  uncertain and nontransitive pair judgments are only approximated by the
  preregistered clique partition.
- Six fixed regex templates extract facets from controlled question forms.
  The 100% edit-locality rate partly reflects that templated construction;
  exact-string stability of zero is not a semantic fidelity test.
- Quality gates measure question form, complete extracted facets, and absence
  of a short list of vague words. They do not measure scientific quality.
- Intended labels are construction metadata, not independent human
  judgments. No semantic validation was performed. Therefore this report
  completes saved baseline reporting, not semantic validation or the full
  official semantic objectives.
- Task 3 remains blocked: no protocol-eligible paired real-paper and
  generated-question citation groups were scored. Existing candidate
  verification found no groups meeting the required seed/date evidence.

## Reproduction and saved-artifact consistency

The following read-only command recomputes the reported pass rates and
cluster-bootstrap intervals from the saved per-set results, checks the Task 4
summaries, confirms 200 rows in each artifact, and verifies the frozen input
hashes in `manifest_v1.json`. It imports the statistical helper only; it does
not call `evaluate()`, score questions, load a model, or write files.

Run from the repository root:

```sh
python3 - <<'PY'
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'E5')
from evaluate import MEASURES, bootstrap_cluster, rows

root = Path('.')
out = root / 'E5/results/controlled_baseline_v2'
manifest = json.loads((root / 'E5/manifest_v1.json').read_text())
for rel, expected in manifest['committed_sha256'].items():
    actual = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    assert actual == expected, f'frozen input hash mismatch: {rel}'
results = rows(out / 'results.jsonl')
facets = rows(out / 'facet_reliability.jsonl')
summary = json.loads((out / 'summary.json').read_text())
assert len(results) == len(facets) == summary['sets'] == 200
assert len({r['id'] for r in results}) == len({r['id'] for r in facets}) == 200
assert summary['new_model_inference'] is False
for saved in summary['rates']:
    values = [r['passes'][saved['axiom']][saved['measure']] for r in results]
    clusters = [r['topic_family'] for r in results]
    rate = sum(values) / len(values)
    ci = bootstrap_cluster(values, clusters)
    assert sum(values) == saved['passes'] and len(values) == saved['valid']
    assert abs(rate - saved['rate']) < 1e-12
    assert all(abs(a-b) < 1e-12 for a,b in zip(ci, saved['ci95']))
for saved in summary['facet_paraphrase_stability']:
    values = [r['paraphrase_stable'][saved['facet']] for r in facets]
    assert sum(values) == saved['stable'] and len(values) == saved['valid']
    assert all(abs(a-b) < 1e-12 for a,b in zip(bootstrap_cluster(values, [r['topic_family'] for r in facets]), saved['ci95']))
for saved in summary['edit_by_intended_facet']:
    selected = [r for r in facets if r['intended_edit'] == saved['facet']]
    values = [r['edit_moves'][saved['facet']] and all(not r['edit_moves'][f] for f in ('purpose','mechanism','evaluation','domain') if f != saved['facet']) for r in selected]
    assert sum(values) == saved['local_moves'] and len(values) == saved['valid']
    assert all(abs(a-b) < 1e-12 for a,b in zip(bootstrap_cluster(values, [r['topic_family'] for r in selected]), saved['ci95']))
local = [r['edit_locality_pass'] for r in facets]
assert sum(local) == summary['facet_edit_locality']['passes']
assert all(abs(a-b) < 1e-12 for a,b in zip(bootstrap_cluster(local, [r['topic_family'] for r in facets]), summary['facet_edit_locality']['ci95']))
print('PASS: saved T2/T4 tables, intervals, row counts, and frozen input hashes are consistent')
PY
```

The saved result tables are in `results/controlled_baseline_v2/summary.json`,
`results.jsonl`, `facet_reliability.jsonl`, and `controls.jsonl`. The failed
export attempt in `results/controlled_baseline_v1/` is historical and is not
used as a result.
