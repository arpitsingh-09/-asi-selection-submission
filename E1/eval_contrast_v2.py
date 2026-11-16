import json
import hashlib
import re
import time
from pathlib import Path
from collections import Counter

import numpy as np
import torch
from sentence_transformers import SentenceTransformer, CrossEncoder

# ------------------------------------------------------------
# Configuration: development data only
# ------------------------------------------------------------
DATA = Path("E1/contrast.jsonl")
OUT = Path("E1/results_v2")
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20261021
BOOTSTRAPS = 2000
TOP_K = 10
rng = np.random.default_rng(SEED)

MODELS = {
    "e5-base-v2": "intfloat/e5-base-v2",
    "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "specter2_base": "allenai/specter2_base",
    "Qwen3-Embedding-0.6B": "Qwen/Qwen3-Embedding-0.6B",
}
CROSS_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

if not DATA.exists():
    raise SystemExit(f"Missing development dataset: {DATA}")

rows = [
    json.loads(line)
    for line in DATA.read_text().splitlines()
    if line.strip()
]

required = {
    "id", "A", "B", "B_min", "C", "C_tilde",
    "C_type", "narrower", "broader"
}
for i, row in enumerate(rows):
    missing = required - set(row)
    if missing:
        raise SystemExit(
            f"Item {i}, ID={row.get('id')}: missing {sorted(missing)}"
        )

if len(rows) < 10:
    raise SystemExit("Too few development items; stopping.")

# Never read E1/test_item.jsonl here.
print("Development items:", len(rows))
print("Near-miss types:", dict(Counter(r["C_type"] for r in rows)))
print("Held-out test file: NOT OPENED")
print("Bootstrap resamples:", BOOTSTRAPS)
print("Results directory:", OUT)

device = (
    "mps" if torch.backends.mps.is_available()
    else "cuda" if torch.cuda.is_available()
    else "cpu"
)
print("Device:", device)

FIELDS = [
    "A", "B", "B_min", "C", "C_tilde", "narrower", "broader"
]

def clean_text(value):
    return str(value).strip()

def tokens(value):
    return re.findall(r"\b\w+\b", str(value).lower())

def word_count(value):
    return len(tokens(value))

def safe_rate(num, den):
    return float(num / den) if den else None

def mean_or_none(values):
    values = [x for x in values if x is not None and np.isfinite(x)]
    return float(np.mean(values)) if values else None

def bootstrap_ci(values, n_boot=BOOTSTRAPS):
    """Percentile CI for an item-level mean/rate."""
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return None
    if len(x) == 1:
        return [float(x[0]), float(x[0])]
    samples = rng.choice(x, size=(n_boot, len(x)), replace=True).mean(axis=1)
    lo, hi = np.quantile(samples, [0.025, 0.975])
    return [float(lo), float(hi)]

def bootstrap_metric(records, field):
    vals = [float(r[field]) for r in records if r.get(field) is not None]
    return {
        "estimate": mean_or_none(vals),
        "ci95_item_bootstrap": bootstrap_ci(vals),
        "n": len(vals),
    }

def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

def normalized_cosine(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def cosine_distance(a, b):
    return 1.0 - normalized_cosine(a, b)

def encode(model, texts, model_name, normalize):
    inputs = texts
    if model_name == "e5-base-v2":
        inputs = ["passage: " + x for x in texts]
    return np.asarray(
        model.encode(
            inputs,
            batch_size=16,
            show_progress_bar=True,
            normalize_embeddings=normalize,
            device=device,
        ),
        dtype=np.float32,
    )

# ------------------------------------------------------------
# Build a unique text inventory for all embeddings
# ------------------------------------------------------------
all_texts = []
for r in rows:
    for field in FIELDS:
        all_texts.append(clean_text(r[field]))

unique_texts = list(dict.fromkeys(all_texts))
text_to_idx = {text: i for i, text in enumerate(unique_texts)}
print("Unique texts:", len(unique_texts))

all_model_results = {}
all_model_items = {}
all_vectors = {}
all_norms = {}

# ------------------------------------------------------------
# Embedding evaluation
# ------------------------------------------------------------
for name, model_id in MODELS.items():
    print(f"\n{'=' * 65}\nEMBEDDING MODEL: {name}\n{'=' * 65}")

    try:
        model = SentenceTransformer(model_id, device=device)

        # Unnormalized embeddings are required for the norm-based scope
        # experiment. Cosine metrics are computed independently from them.
        vectors = encode(model, unique_texts, name, normalize=False)
        norms = np.linalg.norm(vectors, axis=1)

        all_vectors[name] = vectors
        all_norms[name] = norms
        lookup = {
            text: vectors[i]
            for i, text in enumerate(unique_texts)
        }
        norm_lookup = {
            text: float(norms[i])
            for i, text in enumerate(unique_texts)
        }

        records = []
        for r in rows:
            v = {k: lookup[clean_text(r[k])] for k in FIELDS}
            n = {k: norm_lookup[clean_text(r[k])] for k in FIELDS}

            d_ab = cosine_distance(v["A"], v["B"])
            d_abm = cosine_distance(v["A"], v["B_min"])
            d_ac = cosine_distance(v["A"], v["C"])
            d_act = cosine_distance(v["A"], v["C_tilde"])

            # Required identity metrics.
            near_error = float(d_ac < d_ab)
            overlap_shortcut = float(d_ac < d_abm)
            low_overlap_shortcut = float(d_act < d_ab)

            # Scope representation follows the norm proposal:
            # broader W should have smaller norm than A; narrower N
            # should have larger norm than A.
            scope_ok = float(n["broader"] < n["A"] < n["narrower"])

            # Length-only baseline uses token count as the scope score:
            # broader is predicted shorter, narrower longer.
            lengths = {k: word_count(r[k]) for k in FIELDS}
            length_scope_ok = float(
                lengths["broader"] < lengths["A"] < lengths["narrower"]
            )

            # The assignment specifically asks for length-flipped items.
            length_flipped = lengths["broader"] > lengths["narrower"]

            records.append({
                "id": r["id"],
                "C_type": r["C_type"],
                "d_A_B": d_ab,
                "d_A_B_min": d_abm,
                "d_A_C": d_ac,
                "d_A_C_tilde": d_act,
                "norm_A": n["A"],
                "norm_W": n["broader"],
                "norm_N": n["narrower"],
                "scope_order_correct": scope_ok,
                "length_only_order_correct": length_scope_ok,
                "length_flipped": bool(length_flipped),
                "near_miss_error": near_error,
                "overlap_shortcut": overlap_shortcut,
                "low_overlap_shortcut": low_overlap_shortcut,
            })

        all_model_items[name] = records

        summary = {
            "model_id": model_id,
            "n": len(records),
            "scope_method": "unnormalized embedding norm; expected norm(W) < norm(A) < norm(N)",
            "scope_order": bootstrap_metric(records, "scope_order_correct"),
            "length_only_scope_baseline": bootstrap_metric(
                records, "length_only_order_correct"
            ),
            "near_miss_error": bootstrap_metric(records, "near_miss_error"),
            "overlap_shortcut": bootstrap_metric(records, "overlap_shortcut"),
            "low_overlap_shortcut": bootstrap_metric(records, "low_overlap_shortcut"),
        }

        flipped = [r for r in records if r["length_flipped"]]
        summary["length_flipped_n"] = len(flipped)
        summary["scope_order_length_flipped"] = bootstrap_metric(
            flipped, "scope_order_correct"
        )
        summary["length_baseline_length_flipped"] = bootstrap_metric(
            flipped, "length_only_order_correct"
        )

        by_type = {}
        for typ in sorted({r["C_type"] for r in records}):
            subset = [r for r in records if r["C_type"] == typ]
            by_type[typ] = {
                "n": len(subset),
                "near_miss_error": bootstrap_metric(subset, "near_miss_error"),
                "overlap_shortcut": bootstrap_metric(subset, "overlap_shortcut"),
                "low_overlap_shortcut": bootstrap_metric(
                    subset, "low_overlap_shortcut"
                ),
                "scope_order": bootstrap_metric(subset, "scope_order_correct"),
            }

        all_model_results[name] = summary
        save_json(
            OUT / f"{name.replace('/', '_')}_items.json",
            records
        )
        save_json(
            OUT / f"{name.replace('/', '_')}_by_type.json",
            by_type
        )

        print(json.dumps(summary, indent=2))

        del model
        if device == "mps":
            torch.mps.empty_cache()

    except Exception as e:
        all_model_results[name] = {
            "model_id": model_id,
            "error": f"{type(e).__name__}: {e}",
        }
        print("MODEL FAILED:", type(e).__name__, e)

save_json(OUT / "embedding_summary.json", all_model_results)

# ------------------------------------------------------------
# Cross-encoder identity contrasts
# ------------------------------------------------------------
print(f"\n{'=' * 65}\nCROSS-ENCODER CONTRASTS\n{'=' * 65}")
cross_summary = {}
cross_item_records = []

try:
    cross = CrossEncoder(CROSS_MODEL, device=device)

    # Run on paired research-question texts. This model is a passage-relevance
    # baseline, not an instruction-following identity judge; its limitation is
    # explicitly reported.
    pairs = []
    pair_meta = []

    for r in rows:
        for field in ["B", "B_min", "C", "C_tilde"]:
            pairs.append((clean_text(r["A"]), clean_text(r[field])))
            pair_meta.append({
                "id": r["id"],
                "C_type": r["C_type"],
                "field": field,
                "label_same_question": 1 if field in ("B", "B_min") else 0,
            })

    scores = np.asarray(
        cross.predict(pairs, show_progress_bar=True),
        dtype=np.float64
    ).reshape(-1)

    by_id = {}
    for meta, score in zip(pair_meta, scores):
        by_id.setdefault(meta["id"], {})[meta["field"]] = float(score)

    for r in rows:
        s = by_id[r["id"]]
        # d=1-score, as required by the assignment. The inequalities below
        # are equivalent to comparing those distances.
        cross_item_records.append({
            "id": r["id"],
            "C_type": r["C_type"],
            "score_A_B": s["B"],
            "score_A_B_min": s["B_min"],
            "score_A_C": s["C"],
            "score_A_C_tilde": s["C_tilde"],
            "near_miss_error": float(s["C"] > s["B"]),
            "overlap_shortcut": float(s["C"] > s["B_min"]),
            "low_overlap_shortcut": float(s["C_tilde"] > s["B"]),
        })

    cross_summary = {
        "model_id": CROSS_MODEL,
        "interpretation": (
            "Passage-relevance baseline; not a purpose-trained or "
            "instruction-following research-question identity judge."
        ),
        "n": len(cross_item_records),
        "near_miss_error": bootstrap_metric(
            cross_item_records, "near_miss_error"
        ),
        "overlap_shortcut": bootstrap_metric(
            cross_item_records, "overlap_shortcut"
        ),
        "low_overlap_shortcut": bootstrap_metric(
            cross_item_records, "low_overlap_shortcut"
        ),
        "by_type": {},
    }

    for typ in sorted({r["C_type"] for r in cross_item_records}):
        subset = [r for r in cross_item_records if r["C_type"] == typ]
        cross_summary["by_type"][typ] = {
            "n": len(subset),
            "near_miss_error": bootstrap_metric(subset, "near_miss_error"),
            "overlap_shortcut": bootstrap_metric(subset, "overlap_shortcut"),
            "low_overlap_shortcut": bootstrap_metric(
                subset, "low_overlap_shortcut"
            ),
        }

    save_json(OUT / "cross_encoder_items.json", cross_item_records)

except Exception as e:
    cross_summary = {"model_id": CROSS_MODEL, "error": f"{type(e).__name__}: {e}"}
    print("CROSS-ENCODER FAILED:", cross_summary["error"])

save_json(OUT / "cross_encoder_summary.json", cross_summary)

# ------------------------------------------------------------
# Retrieval: full pool, top 10, and target-pair accounting
# ------------------------------------------------------------
print(f"\n{'=' * 65}\nRETRIEVAL EVALUATION\n{'=' * 65}")

retrieval_summary = {}
retrieval_details = []

try:
    # Fix the retrieval embedder in advance: E5 if available, otherwise
    # first successful model in a predeclared order.
    preferred = [
        "e5-base-v2",
        "bge-base-en-v1.5",
        "all-MiniLM-L6-v2",
        "specter2_base",
        "Qwen3-Embedding-0.6B",
    ]
    retrieval_model = next(
        (m for m in preferred if m in all_model_results and
         "error" not in all_model_results[m]),
        None
    )
    if retrieval_model is None:
        raise RuntimeError("No embedding model completed successfully.")

    vectors = all_vectors[retrieval_model]
    idx = text_to_idx

    # Pool every distinct text from all fields and all items.
    pool = []
    seen = set()
    for r in rows:
        for field in FIELDS:
            t = clean_text(r[field])
            if t in seen:
                continue
            seen.add(t)
            pool.append({
                "text": t,
                "source_id": r["id"],
                "field": field,
            })

    # The cross-encoder is applied to each query's top 10 nearest pool texts.
    # Missing positive targets are counted as retrieval misses/FNs.
    retrieval_pairs = []
    retrieval_meta = []
    top_by_query = {}

    for r in rows:
        query = clean_text(r["A"])
        qvec = vectors[idx[query]]

        candidates = []
        for c in pool:
            if c["text"] == query:
                continue
            cvec = vectors[idx[c["text"]]]
            d = cosine_distance(qvec, cvec)
            candidates.append((d, c))

        candidates.sort(key=lambda z: z[0])
        top = candidates[:TOP_K]
        top_by_query[r["id"]] = top

        for rank, (d, c) in enumerate(top, start=1):
            retrieval_pairs.append((query, c["text"]))
            retrieval_meta.append({
                "query_id": r["id"],
                "candidate_source_id": c["source_id"],
                "candidate_field": c["field"],
                "rank": rank,
                "embedding_distance": d,
                "is_target_pair": c["source_id"] == r["id"] and
                    c["field"] in ("B", "B_min", "C", "C_tilde"),
            })

    ce_scores = np.asarray(
        cross.predict(retrieval_pairs, show_progress_bar=True),
        dtype=np.float64
    ).reshape(-1)

    for meta, score in zip(retrieval_meta, ce_scores):
        meta["cross_encoder_score"] = float(score)
        retrieval_details.append(meta)

    # For a transparent target-only end-to-end evaluation, the four known
    # candidate variants per A define the scored target set:
    # B/B_min are positives, C/C_tilde are negatives.
    # Candidates not in top 10 are rejected by the retrieval pipeline.
    target_pairs = []
    for r in rows:
        top_texts = {
            c["text"] for _, c in top_by_query[r["id"]]
        }
        for field in ("B", "B_min", "C", "C_tilde"):
            target_pairs.append({
                "id": r["id"],
                "C_type": r["C_type"],
                "field": field,
                "label": 1 if field in ("B", "B_min") else 0,
                "retrieved": clean_text(r[field]) in top_texts,
                "distance": cosine_distance(
                    vectors[idx[clean_text(r["A"])]],
                    vectors[idx[clean_text(r[field])]]
                ),
            })

    # Obtain cross-encoder scores for all target pairs so that each target
    # has a score. Pairs outside top 10 are not accepted by the pipeline.
    target_score_pairs = [
        (clean_text(next(r for r in rows if r["id"] == t["id"])["A"]),
         clean_text(next(r for r in rows if r["id"] == t["id"])[t["field"]]))
        for t in target_pairs
    ]
    target_scores = np.asarray(
        cross.predict(target_score_pairs, show_progress_bar=True),
        dtype=np.float64
    ).reshape(-1)

    for t, score in zip(target_pairs, target_scores):
        t["cross_encoder_score"] = float(score)

    def binary_metrics(labels, predictions):
        labels = np.asarray(labels, dtype=int)
        predictions = np.asarray(predictions, dtype=int)
        tp = int(np.sum((labels == 1) & (predictions == 1)))
        fp = int(np.sum((labels == 0) & (predictions == 1)))
        fn = int(np.sum((labels == 1) & (predictions == 0)))
        tn = int(np.sum((labels == 0) & (predictions == 0)))
        return {
            "precision": safe_rate(tp, tp + fp),
            "recall": safe_rate(tp, tp + fn),
            "f1": safe_rate(2 * tp, 2 * tp + fp + fn),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        }

    labels = [t["label"] for t in target_pairs]
    distances = [t["distance"] for t in target_pairs]
    ce_scores = [t["cross_encoder_score"] for t in target_pairs]

    # Thresholds are selected with hindsight on development target pairs;
    # this is explicitly optimistic, not a held-out estimate.
    cosine_thresholds = sorted(set(distances))
    best_cosine = None
    for threshold in cosine_thresholds:
        pred = [int(d <= threshold) for d in distances]
        metrics = binary_metrics(labels, pred)
        f1 = metrics["f1"] if metrics["f1"] is not None else 0
        if best_cosine is None or f1 > best_cosine["metrics"]["f1"]:
            best_cosine = {
                "threshold_hindsight": float(threshold),
                "metrics": metrics,
            }

    score_thresholds = sorted(set(ce_scores))
    best_ce = None
    for threshold in score_thresholds:
        pred = [
            int(t["retrieved"] and t["cross_encoder_score"] >= threshold)
            for t in target_pairs
        ]
        metrics = binary_metrics(labels, pred)
        f1 = metrics["f1"] if metrics["f1"] is not None else 0
        if best_ce is None or f1 > best_ce["metrics"]["f1"]:
            best_ce = {
                "threshold_hindsight": float(threshold),
                "metrics": metrics,
            }

    # Retrieval-only recall of the known positives, before cross-encoder.
    positives = [t for t in target_pairs if t["label"] == 1]
    retrieval_hit_rate = safe_rate(
        sum(t["retrieved"] for t in positives), len(positives)
    )

    retrieval_summary = {
        "retrieval_embedding_model": retrieval_model,
        "cross_encoder_model": CROSS_MODEL,
        "candidate_pool_size": len(pool),
        "top_k": TOP_K,
        "number_of_queries": len(rows),
        "known_target_pairs": len(target_pairs),
        "known_positive_pairs": len(positives),
        "positive_retrieval_recall_before_cross_encoder": retrieval_hit_rate,
        "cross_encoder_top10_pipeline": best_ce,
        "cosine_threshold_baseline_hindsight": best_cosine,
        "threshold_warning": (
            "Both thresholds were chosen with hindsight on the same development "
            "items. These are optimistic descriptive comparisons, not held-out estimates."
        ),
        "evaluation_scope_warning": (
            "Precision/recall are computed on the four known target variants "
            "(B, B_min, C, C_tilde) per query. This is a targeted contrast set, "
            "not a fully labelled pool of every retrieved text."
        ),
    }

    save_json(OUT / "retrieval_candidates.json", retrieval_details)
    save_json(OUT / "retrieval_target_pairs.json", target_pairs)

except Exception as e:
    retrieval_summary = {"error": f"{type(e).__name__}: {e}"}
    print("RETRIEVAL FAILED:", retrieval_summary["error"])

save_json(OUT / "retrieval_summary.json", retrieval_summary)

# ------------------------------------------------------------
# Report all metrics and caveats
# ------------------------------------------------------------
lines = [
    "# E1 Corrected Development Evaluation",
    "",
    "## Protocol and limitations",
    "",
    "- Dataset: `E1/contrast.jsonl` only.",
    "- Held-out file `E1/test_item.jsonl` was not opened by this script.",
    "- Confidence intervals are 95% percentile bootstrap intervals over items.",
    "- The five embedding models are evaluated using cosine distance for identity metrics.",
    "- Scope order is evaluated separately using unnormalized embedding norms: norm(W) < norm(A) < norm(N).",
    "- The length-only baseline uses word count as a proxy for scope.",
    "- The MS MARCO cross-encoder is a passage-relevance baseline, not a purpose-trained identity judge.",
    "- Retrieval threshold metrics are hindsight-tuned on the development set and are optimistic.",
    "",
    "## Embedding results",
    "",
    "| Model | Near-miss error | Overlap shortcut | Low-overlap shortcut | Norm scope order | Length-only scope |",
    "|---|---:|---:|---:|---:|---:|",
]

def fmt(metric):
    if not metric or metric.get("estimate") is None:
        return "N/A"
    est = metric["estimate"]
    ci = metric.get("ci95_item_bootstrap")
    if ci:
        return f"{est:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"
    return f"{est:.3f}"

for model, s in all_model_results.items():
    if "error" in s:
        lines.append(f"| {model} | ERROR | ERROR | ERROR | ERROR | ERROR |")
        continue
    lines.append(
        f"| {model} | {fmt(s['near_miss_error'])} | "
        f"{fmt(s['overlap_shortcut'])} | {fmt(s['low_overlap_shortcut'])} | "
        f"{fmt(s['scope_order'])} | {fmt(s['length_only_scope_baseline'])} |"
    )

lines += [
    "",
    "## Cross-encoder contrast results",
    "",
    "```json",
    json.dumps(cross_summary, indent=2),
    "```",
    "",
    "## Retrieval results",
    "",
    "```json",
    json.dumps(retrieval_summary, indent=2),
    "```",
    "",
    "## Interpretation cautions",
    "",
    "1. A high near-miss error rate means the model places C closer to A than B under this constructed test; it does not establish general failure on all research questions.",
    "2. Embedding norms may reflect length, pooling, or model-specific scaling rather than scope. The length-flipped subset is therefore important.",
    "3. The cross-encoder is a relevance baseline. Its scores are not calibrated probabilities of question identity.",
    "4. The retrieval metrics cover the four hand-constructed target variants per query, not a fully annotated set of every candidate in the pool.",
    "5. Inspect the source papers and all manually edited items before claiming the dataset is semantically valid.",
    "",
]

(OUT / "report.md").write_text("\n".join(lines) + "\n")

print("\n" + "=" * 72)
print("CORRECTED DEVELOPMENT RESULTS")
print("=" * 72)
for model, result in all_model_results.items():
    print("\n", model)
    print(json.dumps(result, indent=2))
print("\nCROSS-ENCODER")
print(json.dumps(cross_summary, indent=2))
print("\nRETRIEVAL")
print(json.dumps(retrieval_summary, indent=2))
print("\nSaved corrected results to:", OUT)
print("Report:", OUT / "report.md")
