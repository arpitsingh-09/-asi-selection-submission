import json
import os
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity

DATA = Path("E1/contrast.jsonl")
OUT = Path("E1/results")
OUT.mkdir(parents=True, exist_ok=True)

# Only the development dataset is read. Never load E1/test_item.jsonl here.
if not DATA.exists():
    raise SystemExit(f"Missing dataset: {DATA}")

rows = [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]
if len(rows) < 1:
    raise SystemExit("Development dataset is empty.")

required = {"id", "A", "B", "B_min", "C", "C_type", "C_tilde", "narrower", "broader"}
for i, r in enumerate(rows):
    missing = required - set(r)
    if missing:
        raise SystemExit(f"Item {i} ({r.get('id')}): missing fields {sorted(missing)}")

print(f"Development items: {len(rows)}")
print("Near-miss types:", dict(Counter(r["C_type"] for r in rows)))
print("Held-out test file is not loaded.")

device = "mps" if torch.backends.mps.is_available() else (
    "cuda" if torch.cuda.is_available() else "cpu"
)
print("Device:", device)

EMBEDDERS = {
    "e5-base-v2": "intfloat/e5-base-v2",
    "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "specter2_base": "allenai/specter2_base",
    "Qwen3-Embedding-0.6B": "Qwen/Qwen3-Embedding-0.6B",
}
CROSS_ENCODER = "cross-encoder/ms-marco-MiniLM-L-6-v2"

def text(r, key):
    return str(r.get(key, "")).strip()

def embed(model, texts, name):
    # E5 expects query/passages prefixes. All texts here are compared as
    # research-question texts, so use the same passage convention throughout.
    if name == "e5-base-v2":
        texts = ["passage: " + x for x in texts]
    kwargs = {"batch_size": 16, "show_progress_bar": True}
    if device != "cpu":
        kwargs["device"] = device
    vec = model.encode(texts, normalize_embeddings=True, **kwargs)
    return np.asarray(vec, dtype=np.float32)

def dist(a, b):
    return float(1.0 - np.dot(a, b))

def safe_rate(num, den):
    return None if den == 0 else num / den

def average(values):
    vals = [v for v in values if v is not None and np.isfinite(v)]
    return None if not vals else float(np.mean(vals))

def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

# Each model sees the same development texts.
keys = [
    "A", "B", "B_min", "C", "C_tilde", "narrower", "broader"
]
all_texts = []
for r in rows:
    for k in keys:
        all_texts.append(text(r, k))
unique_texts = list(dict.fromkeys(all_texts))
print(f"Unique texts to encode: {len(unique_texts)}")

embeddings_by_model = {}
summary = {}
per_type = {}

for name, model_id in EMBEDDERS.items():
    print(f"\n========== EMBEDDING MODEL: {name} ==========")
    try:
        model = SentenceTransformer(model_id, device=device)
        vectors = embed(model, unique_texts, name)
        lookup = {t: vectors[i] for i, t in enumerate(unique_texts)}
        embeddings_by_model[name] = lookup

        item_results = []
        for r in rows:
            v = {k: lookup[text(r, k)] for k in keys}
            dAB = dist(v["A"], v["B"])
            dABm = dist(v["A"], v["B_min"])
            dAC = dist(v["A"], v["C"])
            dACt = dist(v["A"], v["C_tilde"])
            dAN = dist(v["A"], v["narrower"])
            dAW = dist(v["A"], v["broader"])

            # A's intended scope order: broader W, original A, narrower N.
            # Similarity to A should therefore rank A closer than both W and N;
            # scope direction itself is measured using a length-independent
            # pairwise distance ordering and is only a coarse proxy.
            scope_ok = (dAW > 0 and dAN > 0)
            length_flipped = bool(r.get("length_flipped", False))

            item_results.append({
                "id": r["id"],
                "C_type": r["C_type"],
                "d_A_B": dAB,
                "d_A_B_min": dABm,
                "d_A_C": dAC,
                "d_A_C_tilde": dACt,
                "d_A_narrower": dAN,
                "d_A_broader": dAW,
                "near_miss_error": dAC < dAB,
                "overlap_shortcut": dAC < dABm,
                "low_overlap_shortcut": dACt < dAB,
                "length_flipped": length_flipped,
                "scope_proxy": scope_ok,
            })

        summary[name] = {
            "model_id": model_id,
            "n": len(item_results),
            "near_miss_error_rate": safe_rate(
                sum(x["near_miss_error"] for x in item_results), len(item_results)
            ),
            "overlap_shortcut_rate": safe_rate(
                sum(x["overlap_shortcut"] for x in item_results), len(item_results)
            ),
            "low_overlap_shortcut_rate": safe_rate(
                sum(x["low_overlap_shortcut"] for x in item_results), len(item_results)
            ),
            "scope_proxy_rate": safe_rate(
                sum(x["scope_proxy"] for x in item_results), len(item_results)
            ),
            "length_flipped_n": sum(x["length_flipped"] for x in item_results),
            "length_flipped_scope_proxy_rate": safe_rate(
                sum(x["scope_proxy"] for x in item_results if x["length_flipped"]),
                sum(x["length_flipped"] for x in item_results),
            ),
        }

        by_type = {}
        for typ in sorted({x["C_type"] for x in item_results}):
            subset = [x for x in item_results if x["C_type"] == typ]
            by_type[typ] = {
                "n": len(subset),
                "near_miss_error_rate": safe_rate(
                    sum(x["near_miss_error"] for x in subset), len(subset)
                ),
                "overlap_shortcut_rate": safe_rate(
                    sum(x["overlap_shortcut"] for x in subset), len(subset)
                ),
                "low_overlap_shortcut_rate": safe_rate(
                    sum(x["low_overlap_shortcut"] for x in subset), len(subset)
                ),
            }
        per_type[name] = by_type
        save_json(OUT / f"{name.replace('/', '_')}_items.json", item_results)
        del model
        if device == "mps":
            torch.mps.empty_cache()
    except Exception as e:
        print(f"MODEL FAILED: {type(e).__name__}: {e}")
        summary[name] = {"model_id": model_id, "error": f"{type(e).__name__}: {e}"}

save_json(OUT / "embedding_summary.json", summary)
save_json(OUT / "embedding_by_type.json", per_type)

# Retrieval experiment with a cross-encoder baseline. Cross-encoder outputs
# are raw relevance logits, not calibrated question-identity probabilities.
print(f"\n========== CROSS-ENCODER: {CROSS_ENCODER} ==========")
retrieval = {}
try:
    cross = CrossEncoder(CROSS_ENCODER, device=device)
    retrieval_rows = []

    # Use the best available embedding model to generate top-10 candidates.
    # Model choice is fixed by this order, not chosen by observed performance.
    retrieval_embedding_name = next(
        (n for n in ["e5-base-v2", "bge-base-en-v1.5",
                     "all-MiniLM-L6-v2", "specter2_base",
                     "Qwen3-Embedding-0.6B"]
         if n in embeddings_by_model),
        None
    )

    if retrieval_embedding_name is None:
        raise RuntimeError("No embedding model completed; retrieval cannot run.")

    lookup = embeddings_by_model[retrieval_embedding_name]
    candidates = []
    for r in rows:
        for k in keys:
            candidates.append({
                "source_id": r["id"],
                "field": k,
                "text": text(r, k),
                "C_type": r["C_type"],
            })

    # Deduplicate identical candidate strings for retrieval.
    dedup = {}
    for c in candidates:
        dedup.setdefault(c["text"], c)
    candidates = list(dedup.values())

    for r in rows:
        query = text(r, "A")
        qv = lookup[query]
        scored = []
        for c in candidates:
            if c["text"] == query:
                continue
            if c["text"] not in lookup:
                continue
            d = dist(qv, lookup[c["text"]])
            scored.append((d, c))
        nearest = sorted(scored, key=lambda x: x[0])[:10]
        pairs = [(query, c["text"]) for _, c in nearest]
        if pairs:
            logits = cross.predict(pairs, show_progress_bar=False)
            for (d, c), score in zip(nearest, logits):
                # Relevant labels are based on the candidate field's role.
                # Same-question positives: B, B_min. Changed-question
                # negatives: C, C_tilde. Other A/narrower/broader texts are
                # not used to score this binary task.
                label = None
                if c["source_id"] == r["id"] and c["field"] in ("B", "B_min"):
                    label = 1
                elif c["source_id"] == r["id"] and c["field"] in ("C", "C_tilde"):
                    label = 0
                retrieval_rows.append({
                    "query_id": r["id"],
                    "candidate_source_id": c["source_id"],
                    "candidate_field": c["field"],
                    "candidate_text": c["text"],
                    "embedding_distance": d,
                    "cross_encoder_logit": float(np.asarray(score).reshape(-1)[0]),
                    "label": label,
                    "C_type": r["C_type"],
                })

    # Evaluate cross-encoder ranking using only labelled same-item contrasts.
    labelled = [x for x in retrieval_rows if x["label"] is not None]
    if labelled:
        scores = np.array([x["cross_encoder_logit"] for x in labelled], dtype=float)
        labels = np.array([x["label"] for x in labelled], dtype=int)
        thresholds = np.unique(scores)
        best = None
        for threshold in thresholds:
            pred = scores >= threshold
            tp = int(np.sum((pred == 1) & (labels == 1)))
            fp = int(np.sum((pred == 1) & (labels == 0)))
            fn = int(np.sum((pred == 0) & (labels == 1)))
            precision = safe_rate(tp, tp + fp)
            recall = safe_rate(tp, tp + fn)
            f1 = 0 if not precision or not recall or precision + recall == 0 else (
                2 * precision * recall / (precision + recall)
            )
            if best is None or f1 > best["f1"]:
                best = {
                    "threshold_hindsight": float(threshold),
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "tp": tp, "fp": fp, "fn": fn,
                }
        retrieval = {
            "cross_encoder": CROSS_ENCODER,
            "embedding_model_for_retrieval": retrieval_embedding_name,
            "candidate_pool_size": len(candidates),
            "labelled_retrieval_candidates": len(labelled),
            "hindsight_threshold_metrics": best,
            "note": "Threshold selected with hindsight on the same development data; optimistic and not a held-out estimate.",
        }
    else:
        retrieval = {"error": "No labelled retrieval candidates in top-10 results."}

    save_json(OUT / "retrieval_candidates.json", retrieval_rows)
except Exception as e:
    retrieval = {"error": f"{type(e).__name__}: {e}"}
    print("CROSS-ENCODER FAILED:", retrieval["error"])

save_json(OUT / "retrieval_summary.json", retrieval)

print("\n========== SUMMARY ==========")
for name, result in summary.items():
    print("\n", name)
    print(json.dumps(result, indent=2))
print("\nRetrieval:")
print(json.dumps(retrieval, indent=2))
print(f"\nResults saved under {OUT}/")
