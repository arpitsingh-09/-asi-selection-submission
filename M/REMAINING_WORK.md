# Minimum remaining work for the nine registered evaluations

Current state from `results/consolidated_v1/summary.json`: **0/9 completed**. The protocol in `PREREG.md` remains frozen; no evaluation should run until its eligible cohort, predictions, and required authorization are locked.

## Shared blockers and minimum actions

| Dependency group | Tests unlocked | Minimum action | Where it can be done |
|---|---|---|---|
| Prospective source-bound question cohort: exact question/version, creation/availability time, original input IDs and versions strictly earlier, shuffled inputs, and independently verified same-topic decoy | I1, I3, S1, A1, H3, O1, O2, T1 (as applicable) | Complete source provenance and controls for a cohort; retain evidence bindings and hashes. Existing generated questions contain generation records and input IDs, but decoy/human checks and I1 contrasts remain incomplete. | Local validation and manifest construction are executable; missing source disclosures and independent judgments require authors/reviewers. |
| Independent human semantic/identity labels | I1, S1; preference/battle labels for I3/H1; human ceiling for H3 | Obtain blinded, independent annotations with reviewer IDs, evidence/rationale, timestamps, and consensus per the existing workflows. Current review sheets are blank; do not import templates as labels. | Human reviewers required. |
| Verified dated quality outcomes for both separate factors | Train and validate both Q heads; then I1, I3, H3, O1, O2, T1 | Recover exact question-to-paper identity plus source-version public observation dates and source-backed peer-review and later-community-use labels. Prepare train-through-2023 and 2024-only validation sets; fit with TRAIN-only normalization and freeze artifacts. | Existing local review values are insufficient (570 values, 0 verified observation dates, 0 usable question-linked labels); source-version evidence/outcome acquisition is external. Training and validation fitting are local once eligible labels exist. |
| Frozen semantic baseline provenance and inputs | I1/I3/S1/H1/H3/O1 comparisons as specified | Verify the encoder's training cutoff and exact cache/model identity; construct frozen baseline predictions on eligible questions without heldout tuning. | Local cache inspection/encoding may be possible; authoritative cutoff evidence may require external model documentation. |
| Expert/within-seed/outcome cohort annotations | H1, O1, O2 | Collect source-bound expert battles with systems/seeds (H1); paired dated outcomes among human-verified same-topic questions (O1); identical >=3-paper seed groups with outcomes and papers <=365 days apart (O2). | Requires genuine external expert or publication/outcome evidence; local runner and validation code are ready. |
| Training-year snapshots | T1 | Fit and freeze separate train-through-2022 and train-through-2023 models on eligible genuine labels, then produce matched later-paper predictions. | Local fitting/prediction once the shared label dependency is resolved. |

## Test mapping

- **I1:** prospective paraphrase and near-miss pairs, independent labels, all readouts including both Q heads, normalization, four input conditions.
- **I3:** independently labeled length-matched preference pairs, Q/N coordinates, B-LEN and four conditions.
- **S1:** independent near-miss and minimal-paraphrase decisions, B-Q, and four conditions.
- **A1:** fresh eligible cohort, operational manipulation records for both frozen axioms, all four novelty coordinates and four conditions. Existing E2 scores remain development-only; do not guess missing manipulation definitions.
- **H1:** dated length-matched expert battles, system identities, shared seeds, B-Q, and four conditions.
- **H3:** dated public review scores, both Q heads, semantic B-Q, independent human ceiling, and four conditions.
- **O1:** verified same-topic pairs and dated peer-review plus later-use outcomes for both factors, Q/B-Q, and four conditions.
- **O2:** identical seed-paper groups (at least three), eligible paper dates within one year, dated outcome labels, Q/B-TF and four conditions.
- **T1:** locked 2022 and 2023 model snapshots, normalized head predictions on eligible later papers, and four conditions.

## Execution order

1. **External evidence first:** obtain exact question/input provenance, human annotations, and public dated outcomes. This is the current critical path; local scripts cannot infer these fields.
2. **Local preparation:** validate evidence, enforce date/split rules, prepare eligible manifests, fit/freeze quality heads and baselines, and generate predictions without looking at heldout outcomes.
3. **Prospective lock and authorization:** freeze exact test lists and artifacts under the existing protocol, commit required materials, and obtain explicit evaluation authorization.
4. **Run only newly eligible tests:** report per-test metrics and paired 95% intervals; keep tests blocked when dependencies are absent.

**Next single actionable task:** obtain independently verifiable, exact question-to-input provenance and dated public review/outcome evidence for candidate records, beginning with source records already linked to the six generated questions and local review identities. Current minimum remaining work cannot be completed from local M artifacts alone.

**Effort estimate:** external source recovery and human review are unbounded and likely dominate. Once sufficient evidence is supplied, allow roughly 1–3 focused engineering days for cohort validation, model/baseline locks, predictions, per-test execution, and final reporting; this assumes evidence meets the frozen eligibility rules.

## Step 4 quality-label evidence blocker

`M/data/quality_training_v1/eligibility_report.json` examined 570 review values against 29 train and 4 validation manifest records and found 0 eligible labels in either split. No alternative local records currently meet the same gate. The local OpenReview exports bind values to note/forum IDs and raw source lines, but have no verified public-observation timestamp for the exact value (`observed_at` is null; current visibility and note creation/version timestamps do not prove historical public visibility). Review forum IDs also do not map directly to manifest paper/question IDs, and no dated `later_community_use` labels are present.

External requirement: obtain source-verifiable historical review versions binding exact note ID, forum/paper ID, recommendation value, version ID, public visibility/readers, and defensible public-at time; provide exact question-to-paper/version links for eligible train and validation questions and distinct dated later-community-use outcomes. Until then Q fitting remains blocked.
