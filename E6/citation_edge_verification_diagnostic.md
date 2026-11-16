# E6 citation edge verification diagnostic

**Status:** exploratory diagnostic only; not confirmatory research data  
**Verified:** 2026-11-07  
**Scope:** five fixed diagnostic targets only. No corpus-wide candidate processing or final E6 set selection was performed.

## Exact arXiv records

Each record below was resolved by exact arXiv ID through `https://export.arxiv.org/api/query`. Values shown are source-native; versions, title case, and timestamps are preserved as returned.

| arXiv ID | Version | Title | arXiv `published` | DOI |
|---|---|---|---|---|
| `2012.15259` | `2012.15259v1` | A Maximal Correlation Approach to Imposing Fairness in Machine Learning | `2020-12-30T18:15:05Z` | unavailable |
| `2401.00416` | `2401.00416v2` | SVFAP: Self-supervised Video Facial Affect Perceiver | `2023-12-31T07:44:05Z` | `10.1109/TAFFC.2024.3436913` |
| `2112.15025` | `2112.15025v3` | Constructing a Good Behavior Basis for Transfer using Generalized Policy Updates | `2021-12-30T12:20:46Z` | unavailable |
| `2601.00888` | `2601.00888v1` | Comparative Evaluation of CNN Architectures for Neural Style Transfer in Indonesian Batik Motif Generation: A Comprehensive Study | `2025-12-31T11:06:09Z` | unavailable |
| `2012.15838` | `2012.15838v2` | Neural Body: Implicit Neural Representations with Structured Latent Codes for Novel View Synthesis of Dynamic Humans | `2020-12-31T18:55:38Z` | unavailable |

The previously observed OpenAlex exact arXiv landing-page queries yielded no records for all five targets. The new OpenAlex `ids.arxiv` exact external-ID query was rejected with HTTP 400 in this run, so it established no identities. OpenAlex title search remains candidate generation only; no DOI or identity is inferred from text search.

## DOI-confirmed target: `2401.00416`

The DOI comes from the exact arXiv record. OpenAlex exact DOI lookup returned one work (`W4401328604`) carrying the same normalized DOI and an arXiv location for `2401.00416`; this verifies the work identity even though the landing-page filter missed it. Crossref direct DOI lookup returned a work with the same DOI and title `SVFAP: Self-Supervised Video Facial Affect Perceiver`; its deposited reference list has 106 entries, of which 83 carry DOI identifiers. OpenCitations returned 83 outgoing edge records for the same DOI.

Crossref and OpenCitations agree on all **83 DOI-identified cited works** after exact DOI normalization: 83 shared edges, zero source-specific DOI edges, and zero edge conflicts. The remaining 23 Crossref references have no DOI identifier and cannot be compared by stable identifier under this diagnostic. This is an agreement between these two indexes, not proof that either index is complete.

## Four DOI-unavailable targets

For `2012.15259`, `2112.15025`, `2601.00888`, and `2012.15838`, arXiv metadata has no DOI. OpenAlex exact landing-page lookups returned no works. The previous exact landing-page filtering produced zero results; the new arXiv external-ID query capability is covered by mocks but has not produced verified identities for these four targets. No DOI was assigned from title search, and no OpenCitations or Crossref edge request was made for them.

## Edge interpretation and provenance

The DOI-confirmed target's identity is grounded in the exact arXiv record and direct Crossref/OpenCitations DOI queries. Edge comparison was restricted to Crossref-deposited DOI references and OpenCitations cited DOI PIDs. Other references are unresolved for comparison, rather than conflicts. For the four DOI-unavailable records, target identity in the citation indexes and source edge provenance are not established, so their edge conflicts remain **not estimable**. Missing records or edges in any index are not treated as evidence of no citation.

The earlier OpenAlex/Semantic Scholar experiment's per-target edge export is not present in the repository. Thus no crosswalk to that experiment's reported totals (228 references, 213 resolved records, 188 abstracts) is possible, and those totals are not used as edge evidence here.

## Implementation and limitations

`citation_sources.py` now includes a reusable exact-ID arXiv Atom API resolver that preserves the returned versioned ID, title, published/updated strings, DOI, entry XML, raw response, retrieval timestamp, and request provenance. OpenAlex can also query its arXiv external-ID field while retaining candidates without automatic selection. Mock tests cover both paths.

This remains a five-target feasibility diagnostic. Crossref references are publisher-deposited and may be incomplete; OpenCitations covers only indexed edges. The 83 DOI edge agreements therefore describe the overlap of these two source snapshots, not exhaustive citation truth.
