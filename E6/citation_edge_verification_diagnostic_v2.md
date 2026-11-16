# E6 citation edge verification diagnostic — v2

**Status:** exploratory diagnostic only; not confirmatory research data  
**Updated:** 2026-11-07  
**Scope:** the same five fixed diagnostic targets as v1. No corpus-wide candidate processing, final E6 selection, or inference was performed. The original `citation_edge_verification_diagnostic.md` is preserved unchanged.

## Identity evidence

The arXiv API records in v1 remain the primary exact-ID records. The OpenAlex external-ID filter was retried for these five IDs, but all five requests returned HTTP 400 because the current OpenAlex API rejects `ids.arxiv` as an invalid filter field. The error body identified that field as unsupported. These 400 responses do not mean the papers are absent. The adapter-generated requests were of the form `https://api.openalex.org/works?filter=ids.arxiv%3A<canonical-arXiv-ID>&per_page=5&select=...`.

OpenAlex title searches were then used only to generate candidates. Identity is considered established only when the candidate record also contains the exact arXiv landing-page URL; title similarity alone is insufficient.

| arXiv ID | Exact source record (from v1) | OpenAlex title candidate | Identity result |
|---|---|---|---|
| `2012.15259` | Exact arXiv record; arXiv DOI unavailable | `W3117663098`; exact normalized title; DOI `10.1109/icassp43922.2022.9747263`; no arXiv ID or matching arXiv landing page in the returned record | **Unresolved.** Title and DOI metadata do not establish the arXiv-ID-to-DOI link. Semantic Scholar lookup was rate-limited. |
| `2401.00416` | Exact arXiv record `2401.00416v2`; DOI `10.1109/TAFFC.2024.3436913` | Existing v1 exact DOI lookup returned `W4401328604` with that DOI and an arXiv location for `2401.00416` | **Verified** by exact arXiv ID and matching DOI evidence. |
| `2112.15025` | Exact arXiv record; no DOI reported by arXiv | `W4226016088`; exact normalized title; DOI `10.48550/arxiv.2112.15025`; location `http://arxiv.org/abs/2112.15025` | **Verified** by exact arXiv landing-page identifier. The DOI is OpenAlex metadata; arXiv itself did not report it. |
| `2601.00888` | Exact arXiv record; no DOI reported by arXiv | `W7118743140`; exact normalized title; DOI `10.48550/arxiv.2601.00888`; location `http://arxiv.org/abs/2601.00888` | **Verified** by exact arXiv landing-page identifier. The DOI is OpenAlex metadata; arXiv itself did not report it. |
| `2012.15838` | Exact arXiv record `2012.15838v2`; arXiv DOI unavailable | `W3176327543`; exact normalized title; DOI `10.1109/cvpr46437.2021.00894`; location `http://arxiv.org/abs/2012.15838` | **Verified** by exact arXiv landing-page identifier and DOI. |

### OpenAlex exact-ID query provenance

All five external-ID filter requests returned HTTP 400 on 2026-11-07. The captured batch retrieval window was approximately `14:17:09Z`–`14:17:15Z`; the original adapter error path did not retain per-error timestamps in a durable result. The captured error stated: `ids.arxiv is not a valid field`. No source identity or edge conclusion is drawn from these failed requests.

### OpenAlex title-search provenance

All four title searches returned HTTP 200 from the OpenAlex public REST API, with `cache_hit: false`. The adapter retained the full request URLs and timestamps in the inspection results:

| arXiv ID | Request URL | Retrieved at (UTC) | OpenAlex work |
|---|---|---|---|
| `2012.15259` | `https://api.openalex.org/works?search=A+Maximal+Correlation+Approach+to+Imposing+Fairness+in+Machine+Learning&per_page=5&select=...` | `2026-11-07T14:18:08.125916Z` | `W3117663098` |
| `2112.15025` | `https://api.openalex.org/works?search=Constructing+a+Good+Behavior+Basis+for+Transfer+using+Generalized+Policy+Updates&per_page=5&select=...` | `2026-11-07T14:18:09.314940Z` | `W4226016088` |
| `2601.00888` | `https://api.openalex.org/works?search=Comparative+Evaluation+of+CNN+Architectures+for+Neural+Style+Transfer+in+Indonesian+Batik+Motif+Generation%3A+A+Comprehensive+Study&per_page=5&select=...` | `2026-11-07T14:18:10.265641Z` | `W7118743140` |
| `2012.15838` | `https://api.openalex.org/works?search=Neural+Body%3A+Implicit+Neural+Representations+with+Structured+Latent+Codes+for+Novel+View+Synthesis+of+Dynamic+Humans&per_page=5&select=...` | `2026-11-07T14:18:12.968945Z` | `W3176327543` |

The `select=...` above abbreviates the adapter's fixed field list (`id,doi,title,publication_date,referenced_works,ids,abstract_inverted_index,updated_date,locations`). Candidate records were inspected for exact arXiv URLs; no title-only result was auto-selected.

## Crossref and OpenCitations DOI-edge checks

Only DOI-confirmed targets were considered for edge comparison. DOI strings were normalized exactly; a source-only edge is an unresolved coverage difference, not a conflict or proof that the edge does not exist.

| Target | Crossref | OpenCitations | Comparable DOI-edge result |
|---|---|---|---|
| `2401.00416` | Existing v1 record: exact DOI; 106 reference entries, 83 DOI-identified | Existing v1 record: 83 DOI edges | **83 matched; 0 Crossref-only; 0 OpenCitations-only; 0 conflicts.** The remaining 23 Crossref entries lacked DOI identifiers and were not comparable. |
| `2012.15259` candidate DOI `10.1109/icassp43922.2022.9747263` | HTTP 200; returned DOI and title match the candidate; 22 references, 9 with DOI | HTTP 200; 9 edges, all citing the queried DOI; retrieved DOI-bearing cited set has 9 entries | **Candidate-level only: 9/9 DOI edges matched.** Not attributed to the arXiv target because its exact identity link remains unresolved. Crossref had 13 reference entries without DOI. |
| `2112.15025` DOI `10.48550/arxiv.2112.15025` | HTTP 404 | HTTP 200; zero edge records | **Not estimable.** Missing source records/edges are not genuine conflicts and do not establish absence of citations. |
| `2601.00888` DOI `10.48550/arxiv.2601.00888` | HTTP 404 | HTTP 200; zero edge records | **Not estimable.** Missing source records/edges are not genuine conflicts and do not establish absence of citations. |
| `2012.15838` DOI `10.1109/cvpr46437.2021.00894` | HTTP 200; exact returned DOI and title; 67 reference entries, 49 with DOI | HTTP 200; 49 edges, all citing the queried DOI | **49 matched; 0 Crossref-only; 0 OpenCitations-only; 0 conflicts.** The remaining 18 Crossref entries lacked DOI identifiers and were not comparable. |

The v1 `2401.00416` checks were reused; no requests were repeated for that completed target. For new confirmed comparisons, Crossref and OpenCitations retrievals were recorded on 2026-11-07:

| Target | Source | Retrieved at (UTC) | HTTP | Request |
|---|---|---|---:|---|
| `2012.15259` candidate DOI | Crossref | `2026-11-07T14:20:51.100819Z` | 200 | `https://api.crossref.org/works/10.1109%2Ficassp43922.2022.9747263` |
| `2012.15259` candidate DOI | OpenCitations | `2026-11-07T14:20:52.225433Z` | 200 | `https://api.opencitations.net/index/v2/references/doi:10.1109%2Ficassp43922.2022.9747263` |
| `2112.15025` | OpenCitations | `2026-11-07T14:20:53.657143Z` | 200 | `https://api.opencitations.net/index/v2/references/doi:10.48550%2Farxiv.2112.15025` |
| `2601.00888` | OpenCitations | `2026-11-07T14:20:54.783664Z` | 200 | `https://api.opencitations.net/index/v2/references/doi:10.48550%2Farxiv.2601.00888` |
| `2012.15838` | Crossref | `2026-11-07T14:20:56.427532Z` | 200 | `https://api.crossref.org/works/10.1109%2Fcvpr46437.2021.00894` |
| `2012.15838` | OpenCitations | `2026-11-07T14:20:58.062670Z` | 200 | `https://api.opencitations.net/index/v2/references/doi:10.1109%2Fcvpr46437.2021.00894` |

Crossref returned HTTP 404 for the two `10.48550/arxiv...` DOI lookups. The earlier adapter error envelope did not retain those calls' retrieval timestamps or raw bodies. This missing provenance was not reconstructed by repeating requests.

## Semantic Scholar results

Exact arXiv-ID lookups were attempted for the five fixed targets only. All five returned HTTP 429 with response body `{"message":"Too Many Requests...","code":"429"}`. The response `Date` headers ranged from `Sat, 07 Nov 2026 14:21:42 GMT` through `14:21:46 GMT`. The adapter's `max_attempts` was set to 1 for these diagnostic calls; no retry was made while rate-limited. Semantic Scholar therefore contributes no identity or edge evidence here.

## Edge classifications and limitations

- **Matched DOI edges:** 83 for `2401.00416`; 49 for `2012.15838`. The 9 matching edges for the `2012.15259` DOI candidate are reported separately and are not credited to that arXiv target.
- **Genuine conflicts:** none among the DOI-comparable edges for identity-confirmed targets.
- **Unresolved:** the target identity for `2012.15259`; the DOI edges for `2112.15025` and `2601.00888`; and all Semantic Scholar checks affected by HTTP 429.
- **Missing metadata:** Crossref references without DOI (23 for `2401.00416`, 13 for the `2012.15259` candidate, and 18 for `2012.15838`); Crossref's HTTP 404 records for two arXiv DOIs; and OpenCitations' empty indexed results for those two DOIs. These are not conflicts or evidence of no citation.
- The OpenAlex external-ID method in the current adapter uses an unsupported filter field (`ids.arxiv`). Title search produced useful candidates but does not establish identity absent an exact arXiv identifier/link.
- The original diagnostic reports prior raw source results, including the `2401.00416` DOI comparison, but does not retain per-request retrieval timestamps. Those timestamps are reported as unavailable rather than inferred.
- No persistent API cache was present. New checks used the existing adapters with in-memory caching. During this inspection, the Crossref and OpenCitations DOI queries for `2012.15259` and `2012.15838` were repeated once after an initial DOI extraction bug was identified; the final counts and timestamps above come from the corrected extraction run. No requests were made after those final results.

This remains a five-target API feasibility diagnostic. It does not establish complete citation truth, select E6 evaluation inputs, or authorize larger-scale acquisition.
