"""Read-only recomputation of E1 saved-result summaries with source-cluster CIs.

Reads frozen contrast items and existing result JSON only. Writes new dated
analysis files; it does not load models or alter any original outputs.
"""
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E1 = ROOT / "E1"
BOOT = 5000
SEED = 20261116
OUT_JSON = E1 / "results_v2" / "saved_evidence_analysis_2026-11-16.json"


def load_json(path):
    return json.loads(path.read_text())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def cluster_ci(records, value_fn, cluster_field="id", seed=SEED):
    # The registered unit is a source paper. The dataset has one question item
    # per distinct arXiv source, so resampling item IDs is source-cluster resampling.
    grouped = defaultdict(list)
    for row in records:
        grouped[row[cluster_field]].append(row)
    clusters = list(grouped)
    rng = random.Random(seed)
    vals = []
    point_rows = [r for rows in grouped.values() for r in rows]
    point = value_fn(point_rows)
    if len(clusters) < 2:
        return {"estimate": point, "ci95_source_cluster_bootstrap": None,
                "n_source_clusters": len(clusters)}
    for _ in range(BOOT):
        sampled = [rng.choice(clusters) for _ in clusters]
        sample = [r for cid in sampled for r in grouped[cid]]
        val = value_fn(sample)
        if val is not None:
            vals.append(float(val))
    return {"estimate": point,
            "ci95_source_cluster_bootstrap": [percentile(vals, .025), percentile(vals, .975)],
            "n_source_clusters": len(clusters), "bootstrap_replicates": len(vals)}


def mean_field(field):
    return lambda rows: sum(float(r[field]) for r in rows) / len(rows) if rows else None


def binary_metrics(rows, pred_fn):
    tp = fp = fn = tn = 0
    for r in rows:
        pred, y = bool(pred_fn(r)), int(r["label"])
        tp += pred and y == 1
        fp += pred and y == 0
        fn += (not pred) and y == 1
        tn += (not pred) and y == 0
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * precision * recall / (precision + recall) if precision and recall else (0.0 if precision == 0 or recall == 0 else None)
    return {"precision": precision, "recall": recall, "f1": f1,
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)}


items = [json.loads(line) for line in (E1 / "contrast.jsonl").read_text().splitlines() if line.strip()]
id_to_source = {r["id"]: r["source_arxiv"] for r in items}
id_to_type = {r["id"]: r["C_type"] for r in items}
source_ids = set(id_to_source.values())
assert len(items) == 61 and len(source_ids) == len(items)

model_specs = load_json(E1 / "results_v2" / "embedding_summary.json")
models = {}
for name, spec in model_specs.items():
    records = load_json(E1 / "results_v2" / f"{name}_items.json")
    assert {r["id"] for r in records} == set(id_to_source)
    models[name] = {"model_id": spec["model_id"], "file": f"E1/results_v2/{name}_items.json", "records": records}

# The prior SentenceTransformers-default-pooling SPECTER2 run is superseded by
# the independently corrected base+proximity-adapter CLS run.
corrected_spec = load_json(E1 / "results_specter2_corrected" / "specter2_corrected_summary.json")
corrected_records = load_json(E1 / "results_specter2_corrected" / "specter2_corrected_items.json")
assert {r["id"] for r in corrected_records} == set(id_to_source)
models["specter2_corrected"] = {
    "model_id": corrected_spec["model_id"],
    "adapter": corrected_spec["adapter"],
    "embedding_method": corrected_spec["embedding_method"],
    "file": "E1/results_specter2_corrected/specter2_corrected_items.json",
    "records": corrected_records,
}

metrics = ["near_miss_error", "overlap_shortcut", "low_overlap_shortcut", "scope_order_correct", "length_only_order_correct"]
model_results = {}
for name, model in models.items():
    rows = model["records"]
    fields = metrics
    # no cross_encoder embedding item file is used; this entry is skipped below
    if name == "cross_encoder":
        continue
    out = {k: v for k, v in model.items() if k != "records"}
    out["n_items"] = len(rows)
    out["metrics"] = {m: cluster_ci(rows, mean_field(m)) for m in fields}
    flipped = [r for r in rows if r.get("length_flipped")]
    if flipped and all("scope_order_correct" in r for r in flipped):
        out["length_flipped_scope_order"] = cluster_ci(flipped, mean_field("scope_order_correct"))
        out["length_flipped_n"] = len(flipped)
    out["by_near_miss_type"] = {}
    for typ in sorted(set(r["C_type"] for r in rows)):
        subset = [r for r in rows if r["C_type"] == typ]
        out["by_near_miss_type"][typ] = {
            "n_items": len(subset),
            "metrics": {m: cluster_ci(subset, mean_field(m)) for m in metrics if m in subset[0]},
        }
    model_results[name] = out

cross_rows = load_json(E1 / "results_v2" / "cross_encoder_items.json")
assert {r["id"] for r in cross_rows} == set(id_to_source)
for row in cross_rows:
    row["label"] = 1
cross_summary = load_json(E1 / "results_v2" / "cross_encoder_summary.json")
model_results["cross_encoder_ms_marco"] = {
    "model_id": cross_summary["model_id"],
    "interpretation": cross_summary["interpretation"],
    "n_items": len(cross_rows),
    "metrics": {m: cluster_ci(cross_rows, mean_field(m)) for m in metrics[:3]},
    "by_near_miss_type": {},
}
for typ in sorted(set(r["C_type"] for r in cross_rows)):
    subset = [r for r in cross_rows if r["C_type"] == typ]
    model_results["cross_encoder_ms_marco"]["by_near_miss_type"][typ] = {
        "n_items": len(subset),
        "metrics": {m: cluster_ci(subset, mean_field(m)) for m in metrics[:3]},
    }

# Task 4: saved top-10 candidate/target records. Intervals condition on the
# already selected hindsight thresholds; they do not correct threshold optimism.
targets = load_json(E1 / "results_v2" / "retrieval_target_pairs.json")
assert len(targets) == 244 and {r["id"] for r in targets} == set(id_to_source)
retrieval_summary = load_json(E1 / "results_v2" / "retrieval_summary.json")
ce_t = retrieval_summary["cross_encoder_top10_pipeline"]["threshold_hindsight"]
cos_t = retrieval_summary["cosine_threshold_baseline_hindsight"]["threshold_hindsight"]

def clustered_metric(rows, fn):
    # Cluster CI requires retaining all four target variants for each sampled query.
    return cluster_ci(rows, fn)

def metric_fn(name, threshold):
    if name == "cross":
        return lambda rs: binary_metrics(rs, lambda r: r["retrieved"] and r["cross_encoder_score"] >= threshold)
    return lambda rs: binary_metrics(rs, lambda r: r["distance"] <= threshold)

retrieval = {
    "source_clusters": len(source_ids),
    "known_target_variants": len(targets),
    "positive_retrieval_recall_top10": cluster_ci(
        targets, lambda rs: sum(int(r["retrieved"]) for r in rs if r["label"] == 1) / sum(1 for r in rs if r["label"] == 1)
    ),
    "cross_encoder_top10_threshold_fixed": {"threshold": ce_t},
    "cosine_hindsight_threshold_fixed": {"threshold": cos_t},
}
for key, threshold, which in [("cross_encoder_top10_threshold_fixed", ce_t, "cross"), ("cosine_hindsight_threshold_fixed", cos_t, "cosine")]:
    for metric in ("precision", "recall", "f1"):
        fn = lambda rs, m=metric, th=threshold, w=which: metric_fn(w, th)(rs)[m]
        retrieval[key][metric] = clustered_metric(targets, fn)
    retrieval[key]["confusion_counts"] = metric_fn(which, threshold)(targets)
    retrieval[key]["threshold_interpretation"] = "Hindsight-selected on these same development examples; CI is conditional on the fixed reported threshold and does not remove optimism."

# Hashes bind this report to exact available source/result artifacts.
hash_paths = [E1 / "contrast.jsonl", E1 / "eval_contrast_v2.py",
              E1 / "results_v2" / "embedding_summary.json",
              E1 / "results_v2" / "cross_encoder_summary.json",
              E1 / "results_v2" / "retrieval_summary.json",
              E1 / "results_v2" / "retrieval_target_pairs.json"]
result = {
    "analysis_date": "2026-11-16",
    "method": "Read-only recomputation from existing per-item outputs; percentile bootstrap resamples source-paper clusters (arXiv IDs). There is exactly one item per source paper, so item and source clusters coincide for item-level metrics.",
    "n_items": len(items),
    "n_source_clusters": len(source_ids),
    "bootstrap_replicates": BOOT,
    "seed": SEED,
    "models": model_results,
    "deduplication": retrieval,
    "sha256": {str(p.relative_to(ROOT)): sha256(p) for p in hash_paths},
    "limitations": [
        "All model scores are exploratory development outputs, not confirmatory held-out results.",
        "The saved MS MARCO cross-encoder is a generic passage-relevance scorer, not the instructed same-research-question classifier required by the assignment.",
        "Deduplication labels cover only B/B_min positives and C/C_tilde negatives for each query, not every candidate in the retrieval pool.",
        "Hindsight-threshold confidence intervals condition on thresholds selected on these same examples and therefore do not remove selection optimism.",
    ],
}
OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
print("items/source clusters:", len(items), len(source_ids))
for k, v in model_results.items():
    print(k, v["metrics"])
print("deduplication:", retrieval)
