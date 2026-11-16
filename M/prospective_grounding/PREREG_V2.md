# Main Problem prospective grounding pilot — V2 preregistration

**Status:** prospective protocol; generation has not run under V2. This is a separate prospective experiment. Its questions, decoys, raw responses, judgments, and results must be stored separately from V1 and must not be pooled with V1 or described as a repaired V1 result. No V1 output is replaced, discarded, or reclassified.

## V1 failure record and reason for V2

V1's first attempt was the video memorability primary question, seed `4900`, on 2026-11-15. The preserved Ollama response in `M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json` records model `qwen3:8b`, `done_reason="length"`, `eval_count=512`, a non-empty `thinking` field, and `response=""`. The output is unusable as a question. V1's one-shot claim and failed raw attempt remain intact; V1 is closed and will not be retried.

V2 is a new prospective cohort because its protocol is registered before any V2 inference and changes the generation request to explicitly disable Qwen3 thinking (`think: false`). The change targets the documented token-budget failure. V1's empty response remains a failure record, not a V2 question or an observation in the V2 evaluation.

## Hypothesis, scope, and data

V2 uses the same hypothesis, population, controls, frozen lexical proxy `G`, TF-IDF baseline `B-TF`, judgments, analysis, and interpretation as V1's `PREREG_DRAFT.md`. It uses exactly two independent paper families, `video_memorability` and `image_enhancement`, with the exact three versioned arXiv records per family from the frozen source manifest. There will be exactly two primary questions and two same-topic, input-unsupported decoy candidates. A failed call or invalid candidate blocks V2; no retries, replacements, substitutions, or cherry-picking are allowed.

The source manifest SHA-256 is `02c7600331b197ff8c99e75c1f1d90b54a74c29833e0191f240ed1b151c7830c`; the read-only `E2/data/raw_papers.jsonl` SHA-256 is `98036e1d99139a7fa4938362ab45f97fc12f21a91182c0ce5d22ee5be7d0c662`. Each prepared request's input IDs, per-paper source metadata, abstract hash, and primary prompt hash are checked before generation. Publication and availability times must precede each actual generation call.

## Generator and frozen settings

Use the local Ollama `qwen3:8b` artifact only: Ollama ID `sha256:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`, model-layer digest `sha256:a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f`, config digest `sha256:05a61d37b08453e59290add468e3bb2f688e23a01e967fecb0e2fa41218cea76`. Verify the local manifest, content-addressed blobs, and Ollama API digest before generation. A mismatch blocks the run.

Freeze `temperature=0.7`, `top_p=0.8`, and `num_predict=512`. Send `think=false` as the Ollama generation request parameter on every primary and decoy call. No other generation setting changes from V1.

V2 reuses V1's fixed seed schedule: video primary/decoy `4900/4901`, image primary/decoy `4910/4911`. This is intentional: the V1 primary produced no question, so reusing its seed schedule allows the V2 generation protocol to change only the explicitly registered thinking setting while retaining the prompts, model, paper inputs, and sampling settings. The schedule is frozen here before V2 inference. It does not turn V1 and V2 into a shared sample; V2 remains a separate prospective cohort.

## Prompts, provenance, and attempt preservation

Use the exact primary prompts in `M/prospective_a1/generation_requests.jsonl`. Before any inference, prepare and hash one decoy prompt per family using the existing `prepare_decoy_request`; each asks for a distinct same-topic question not substantively addressed by its supplied papers. The four exact prompts, hashes, seeds, and input IDs are saved in the V2 run plan before the first call.

Use `M/prospective_a1.workflow.generate_record` and `M.prospective_grounding.workflow.generate_decoy_record`. Preserve the exact untrimmed Ollama HTTP response body and `response` string, any thinking text returned by the service, request settings, model identity/digest, exact source records/IDs, prompt/hash, local UTC call-start timestamp, and Ollama `created_at` timestamp. A failed request is written to its attempt record and stops the run. No retry follows any error, interruption, empty response, or invalid candidate.

The V2 command creates `M/prospective_grounding/generated_v2/` as a one-shot output root with an exclusive claim file. It refuses to run if the root already contains anything or another process has claimed it. Write a `STARTED` attempt record before each call and replace it atomically with success or failure details afterward. Never overwrite or reset the root. Preserve partial runs as failures.

## Controls, reviews, and analysis

For each primary, construct the same V1 conditions: its exact original three-paper pool, an empty pool, the other family's three-paper pool as shuffled control, and the same-topic decoy paired with the original pool. Preserve the V1 empty-pool undefined-score handling. Require two independent reviewers to verify each decoy is same-topic and unsupported, and independently rate every non-empty question-paper pair using V1's 0/1/2 rubric.

Use the V1 registered primary endpoint, paired family-cluster bootstrap (2,000 draws, seed `20261113`), pass rule, failure handling, and limited two-family interpretation unchanged. Do not score until V2's preregistration is committed, complete independent reviews and all readiness gates pass, and explicit execution authorization is recorded. No scoring or evaluation is authorized by this generation preregistration alone.

## V1 preservation lock

V1 remains byte-for-byte unchanged. Before V2 inference, the V2 entry point verifies these captured SHA-256 values and stops if any differ:

| V1 file | SHA-256 |
|---|---|
| `M/PREREG.md` | `d996104d87f35435f25f1160e38ba1e7f335a35b84234dd1f43aa37b87c82bdd` |
| `M/prospective_grounding/PREREG_DRAFT.md` | `28e686939bb8eb40c1431490c9f82159aa9de67be6cc7e77d3a1ccbbcb6a8a5f` |
| `M/prospective_grounding/workflow.py` | `bc4abd5f9f54813b17c55b40ba306fa08df26994e2930e86c90b7f77810656dc` |
| `M/prospective_grounding/generate.py` | `a833a209b5c4c502f669c5a1d0f4afca283464fd418351cdd82aba0d6bc5aaac` |
| `M/prospective_grounding/tests/test_workflow_safeguards.py` | `4de253a0806f2293a75bb4be76fa032ff7267c4ac5656ffc998a8f8788d3f244` |
| `M/prospective_grounding/tests/test_generate_cli.py` | `e257c1983f4480b909a5b1f7409e2a6eb1a9728638ceac8d79f564b77b78d174` |
| `M/prospective_grounding/generated_v1/ONE_SHOT_CLAIM.json` | `961ba729c6589412d2b75c4649c1c06678f496d1e6c9dc788e6cef19e2d92d2c` |
| `M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/run.json` | `e6b28e15d38b0541775af10768b7cdc58f8e4167e23c5b76800fc3f4857ca31d` |
| `M/prospective_grounding/generated_v1/run_20261115T023429_468521Z/attempts/01_video_memorability_primary.json` | `8f12074f0cd4746a41d1c3bf56ee7455a466a76927b2f40ffca93d37fa812fbc` |

## Prospective execution gate

Commit `PREREG_V2.md`, `generate_v2.py`, and its focused offline tests locally before running the V2 command. The command independently verifies that the current committed preregistration and entry point match the working files, and that all V1 and frozen-source hashes still match. This protocol does not authorize inference before that commit, and does not authorize any evaluation or scoring.
