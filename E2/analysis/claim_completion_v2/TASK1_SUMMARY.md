# Task 1 remaining-short-set review

Reviewed exactly the 23 pending focal papers from `claim_completion_v1`.
No completed focal was re-extracted or changed. The cumulative artifact is
`claims_future.jsonl`; the original scoring inputs remain unchanged.

| Result | Count |
|---|---:|
| Papers completed in this run | 17 |
| Papers still incomplete, with evidence limitations | 6 |
| Total focal papers meeting the 4–10 count requirement | 294/300 |
| Accepted claims in the 17 reviewed sets | 73 |
| Claims reused verbatim with the same evidence | 22 |
| Explicitly labeled background assertions | 5 |

The other 51 accepted claim records are source-bound additions or atomic/qualified
revisions. Compound lists were separated only where they assert independent
operations, mathematical relationships or measured outcomes. Generic introduction
statements were not counted again alongside their components. In particular,
medical-report claims now retain the actual radiologist-judgment qualifications
and reported exceptions; no clinical-efficacy claim is inferred. Five background
assertions are labeled as background, not as new contributions.

Each completed set received a Codex AI source-support, distinctness and atomicity
review. `decisions.jsonl` retains the review reasons. `review.jsonl` binds each
accepted claim to an exact excerpt, source filename/line, file SHA-256, abstract
SHA-256 and character offsets. Prior claims and audit values remain in each
revised record. No independent human approval is implied. The previous 277
count-complete sets were left byte-for-object unchanged in the cumulative data;
this run does not certify their inherited semantic limitations away. Thus 294
is count eligibility, not an independent validity certification of all 294 sets.

## Evidence-limited papers

| Paper | Why four substantive claims cannot be supported locally |
|---|---|
| 2012.15515v1 — NMT review | Review scope and adoption background; no technical findings. Topic-list splitting would pad the count. |
| 2112.13634v1 — non-English QA survey | Existing scope claims overlap; no dataset-specific comparisons or findings. |
| 2501.00244v1 — structural knowledge prompting | Benchmark and evaluation scope stated, but no conclusions for the four generalization axes. |
| 2101.10815v1 — loss ensembles | One ensemble method and first-place challenge result; code availability is not a scientific claim. |
| 2112.15568v1 — actor loss explained | No actual equations, gradient identities or estimator comparison conclusions in the abstract. |
| 2312.17525v1 — approximate computing | One RL strategy and qualitative trade-off result; no additional technical findings. |

No matching local full text for these IDs was found in the inspected repository,
Downloads and cache paths. Existing `E2/paper_review` full-text files concern
other paper IDs. No paper was downloaded, inferred from general knowledge, or
silently substituted by another version. The six short records remain excluded
from four-claim-compliant analyses; `remaining_short_sets.jsonl` records why.
They need genuine full-paper passages before further completion. Task 1's
all-300 claim requirement therefore remains incomplete.

## Validation and preservation

All 73 accepted excerpts passed exact substring and offset checks. All revised
sets have 4–10 nonduplicate claim strings; substantive correctness/independence
was reviewed explicitly by Codex AI, rather than inferred from string matching.
Seven targeted revision tests passed; no previous suite or experiment was rerun.
Hashes of original scores, original selected claims, previous completion data,
raw sources and the frozen Task 3 plan were unchanged. No E6, notebook, AI log,
model, embedding cache, held-out evaluation or existing scoring output was altered.

## Immediate Task 2 continuation

`task2_reuse_readiness.json` identifies 53 count-eligible focals outside the
previously scored 241. **52** have cached focal vectors and at least four strictly
prior, nonfocal, nonduplicate-abstract reference papers. One lacks enough eligible
cached prior papers for disjoint pairs. Y and density are independent of claim
vectors and can run for those 52 using existing embeddings only. **Zero** of the
53 has all vectors needed for all four measures. Nearest-planting and paraphrase
vectors remain missing, so those conditions cannot yet produce scores.

Exact next action: freeze a separate development-only cache-only extension for
Y and density on the 52 ready IDs, with equal-sized near/far and older/newer
pairs and disclosed cache availability, then compute only those new contrasts.
Reuse the existing 241-paper results unchanged. Do not imply that two-measure
results complete the four-measure requirement; N and yours need the missing
claim vectors. The readiness file is not a frozen protocol or evaluation grant.
No numerical scores were computed in this run.
