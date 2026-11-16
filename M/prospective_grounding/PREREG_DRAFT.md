# Prospective grounding pilot — preregistration draft

**Status:** draft only; no questions generated, judgments collected, scores computed, or held-out evaluation run. This is a new supplementary pilot and is not one of the nine original registered evaluations. It does not alter `M/PREREG.md` or `M/frozen/`.

## Hypothesis and scope

For prospectively generated research questions, the existing shared-Phi groundedness relevance proxy (`G`) will have lower absolute error against independent human input-relevance judgments than the frozen lexical TF-IDF baseline (`B-TF`). `G` measures text relevance, not entailment, answerability, or scientific validity; results will be described only as grounding/relevance evidence for this small pilot.

## Dataset and sample size

Use exactly the two source families already documented in `M/prospective_a1/source_manifest.json`: `video_memorability` and `image_enhancement`, three explicit arXiv version IDs per family. The manifest and every paper record are source-hash bound. Generate one primary question and one same-topic-but-input-unsupported decoy question per family after this draft is committed. This gives **2 independent question families, 2 primary questions, and 2 decoy questions**. Do not replace a failed question or input family. Inputs must have original publication and availability timestamps earlier than the actual generation timestamp. A missing or invalid family blocks the pilot rather than shrinking or substituting the cohort.

The two families are distinct subjects; the decoy is therefore generated within each family from its own supplied papers with an instruction to pose a different, topically related question not grounded by those specific papers. Two independent reviewers must verify that it is same-topic and not supported by that input set. If they cannot, the pilot is blocked; do not relabel or substitute it.

## Generation and provenance

Use `M/prospective_a1/workflow.py` to bind the exact supplied input IDs, source URLs, locators, source hashes, prompt, model ID, parameters, seed, and real UTC generation time. The primary prompt is the existing prepared prompt in `M/prospective_a1/generation_requests.jsonl`. The decoy prompt must be separately fixed and hashed before generation, and must explicitly request a same-topic question not specifically grounded in the supplied papers. Preserve raw model output. Never backdate or describe these questions as historical or author-written.

## Locked representation and baseline

The generator is locked to the local `qwen3:8b` artifact recorded in `M/a1_replication/claim_extraction_qwen3_v1_manifest.json`: Ollama ID `sha256:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`, model-layer digest `sha256:a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f`, config digest `sha256:05a61d37b08453e59290add468e3bb2f688e23a01e967fecb0e2fa41218cea76`. Freeze Ollama options `temperature=0.7`, `top_p=0.8`, `num_predict=512`; seeds are 4900/4901 for video memorability primary/decoy and 4910/4911 for image enhancement primary/decoy. Verify the local artifact still has this exact digest before generation; otherwise stop and amend prospectively before generation.

The existing source manifest SHA-256 at draft preparation is `02c7600331b197ff8c99e75c1f1d90b54a74c29833e0191f240ed1b151c7830c`.
The exact local metadata corpus for `PaperStore`/B-TF is `E2/data/raw_papers.jsonl`, SHA-256 `98036e1d99139a7fa4938362ab45f97fc12f21a91182c0ce5d22ee5be7d0c662` as recorded by the source manifest. It is read-only; the model's training-text subset is determined only by the existing Phi temporal cutoff.

Use the existing `M.engine.ResearchSpace` and default `M.encoders.HashEncoder`: `e5-fixed-nonnegative-word-bigram-hash-512-v1`, 512 dimensions. This is a deterministic lexical proxy, not a frozen sentence encoder. Freeze the encoder implementation, `M/engine.py`, `M/readouts.py`, and baseline implementation by their SHA-256 values at the preregistration commit. Values verified when this draft was prepared:

| Component | SHA-256 |
|---|---|
| `M/encoders.py` | `e24306ec9a7662e2915ae7f58c6591dde9b5359b5b84cecc8c9e64e8dace35f5` |
| `M/engine.py` | `8312503384ccb495125b0dee33a7fdf7db981ccb46de08a34b4a8bba6bed4aec` |
| `M/readouts.py` | `72c64c9bedb0238d683b82863892f7a077e9eca6b51fbd98a56a7db74a367ff1` |
| `M/baselines.py` | `c82589223f3b101e0889814da8b3f6911414b64a9cb12e2fe8dbf3089133675d` |

`G` is the existing `groundedness(phi)` score: mean nonnegative cosine similarity between question and supplied-paper vectors, with its existing exact-copy/already-answered penalty. Empty input produces `None`/undefined and is never assigned an invented numeric prediction. `B-TF` is the existing frozen-vocabulary TF-IDF transform from `M.baselines.tfidf`, applied to the question and each supplied paper using the Phi training documents (only documents available before the question date and published before 2024); its score is mean nonnegative cosine over the supplied set. Both scores are on [0,1]. No fitted normalization is used.

## Conditions

For each primary question, pair the same question with:

1. **Original:** its exact three supplied papers.
2. **Empty:** no supplied papers; G and B-TF are undefined, reported as such, and retained as a structural negative control only.
3. **Shuffled:** the other family’s three supplied papers. Every paper must predate and be available by the primary question’s generation time. This is a deliberately cross-family pool swap, not a claim that the subjects are matched.
4. **Same-topic decoy:** the independently generated decoy question paired with its family’s original three-paper set. Two reviewers must verify same-topic status and lack of direct support from that set.

All condition IDs derive deterministically from question ID, condition name, and sorted input IDs. Preserve pairing by primary question family. No other manipulations or conditions are added.

## Independent judgments

Two reviewers, independently and blind to G/B-TF scores, rate every non-empty question-paper pair: **0** unrelated/no grounding, **1** topical but not directly grounding the question premise, **2** directly relevant evidence for the premise. Keep each reviewer’s original rating, identity/code, date, and evidence note; do not adjudicate away disagreement. The analysis label is the mean of the two ratings, scaled by 2 to [0,1]. Reviewers separately mark each decoy as same-topic and unsupported by its supplied set. Distinct reviewer identities are required for every item. The empty condition has no paper-level judgment and remains undefined for both automated scores.

## Primary metric, inference, and pass rule

Primary endpoint: paired improvement `MAE(B-TF) - MAE(G)` over all non-empty original, shuffled, and decoy question-paper pairs. Positive values favor G. Compute a percentile 95% paired cluster-bootstrap interval with 2,000 draws and seed `20261113`, resampling the two question families and keeping all conditions and labels within each sampled family together. This matches the existing M bootstrap seed/draw convention. Report the point estimate, interval, per-condition errors, raw reviewer ratings, and all undefined values.

**Pass:** point estimate is positive and the 95% interval lower bound is above zero; both decoy validations pass; at least 90% of required non-empty scores are finite; no temporal/provenance violation occurs. Otherwise report a negative or inconclusive pilot, not a system failure claim. With only two clusters, the bootstrap interval has very low resolution and supports no broad generalization; this limitation is part of the registered interpretation.

## Exclusions and missing data

Exclude nothing post hoc. A family with failed generation, invalid source/hash, missing score, incomplete independent reviews, or invalid decoy makes the pilot ineligible to score. Report the failure and retain all raw artifacts. No replacement, imputation, claim extraction, trained Q head, or held-out original-cohort substitution is allowed. Empty-pool scores remain undefined.

## Leakage prevention and execution gate

The question generation time is recorded at the actual generation call. Every input’s publication and source-availability timestamp must be strictly earlier. Shuffled inputs are checked against each primary generation time. No evaluation labels are used to select or tune questions, encoder, score thresholds, or baseline. Commit this protocol before generation; then freeze source manifest hash and code locks. Obtain complete independent judgments, validate condition construction, and record explicit execution authorization before any scoring. `M/prospective_grounding/workflow.py::validate_readiness` is fail-closed on these gates.

## Reproduction procedure (after approval and all gates)

1. Verify the source manifest, code SHA-256 values, and local generator digest above; commit this draft before generating any questions.
2. Load the exact `E2/data/raw_papers.jsonl` source records into `M.store.PaperStore`; use the two existing prepared request records, without changing their source paper IDs.
3. Generate primary questions with `M.prospective_a1.workflow.generate_record`; prepare/generate decoys with `prepare_decoy_request`/`generate_decoy_record`. Attach deterministic primary IDs (`primary-video_memorability`, `primary-image_enhancement`) and the locked model digest. Apply the fixed seed schedule above so actual UTC timestamps, prompts, settings, and exact `R` are captured. Save raw responses and provenance in a new, versioned subdirectory; do not overwrite prior data.
4. Build original/empty/shuffled/decoy pairs with `build_conditions`; collect and validate two independent blind reviews per non-empty question-paper pair.
5. After explicit execution authorization, call `validate_readiness`, then `score_conditions` with `ResearchSpace(PaperStore.load('E2/data/raw_papers.jsonl'))`. Save each Phi ID, G/B-TF values, condition/input IDs, human ratings, source/code hashes, and timestamps to a new output directory.
6. Compute the registered primary endpoint and interval with `paired_cluster_bootstrap`; report the small two-cluster limitation and do not merge the result with the original registered battery.
