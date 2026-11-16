import json
import re
from pathlib import Path
from collections import Counter

import numpy as np
import torch
from adapters import AutoAdapterModel
from transformers import AutoTokenizer

DATA = Path("E1/contrast.jsonl")
OUT = Path("E1/results_specter2_corrected")
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20261021
BOOTSTRAPS = 2000
rng = np.random.default_rng(SEED)

FIELDS = ["A", "B", "B_min", "C", "C_tilde", "narrower", "broader"]

if not DATA.exists():
    raise SystemExit(f"Dataset not found: {DATA}")

rows = [
    json.loads(line)
    for line in DATA.read_text().splitlines()
    if line.strip()
]

required = {
    "id", "A", "B", "B_min", "C", "C_tilde",
    "C_type", "narrower", "broader"
}
for row in rows:
    missing = required - set(row)
    if missing:
        raise SystemExit(f"{row.get('id')}: missing {sorted(missing)}")

def clean_text(value):
    return str(value).strip()

def tokens(value):
    return re.findall(r"\b\w+\b", str(value).lower())

def word_count(value):
    return len(tokens(value))

def cosine_distance(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 1.0
    return float(1.0 - np.dot(a, b) / denom)

def bootstrap_metric(records, field):
    values = np.asarray(
        [float(r[field]) for r in records if r.get(field) is not None],
        dtype=float
    )
    if len(values) == 0:
        return {
            "estimate": None,
            "ci95_item_bootstrap": None,
            "n": 0
        }

    samples = rng.choice(
        values, size=(BOOTSTRAPS, len(values)), replace=True
    ).mean(axis=1)

    lo, hi = np.quantile(samples, [0.025, 0.975])

    return {
        "estimate": float(values.mean()),
        "ci95_item_bootstrap": [float(lo), float(hi)],
        "n": int(len(values))
    }

print("Development items:", len(rows))
print("Types:", dict(Counter(r["C_type"] for r in rows)))
print("Loading SPECTER2 base and proximity adapter...")

base = "allenai/specter2_base"
tokenizer = AutoTokenizer.from_pretrained(base)
model = AutoAdapterModel.from_pretrained(base)

model.load_adapter(
    "allenai/specter2",
    source="hf",
    load_as="proximity",
    set_active=True
)

# CPU keeps this independent evaluation on the known-working device.
device = torch.device("cpu")
model.to(device)
model.eval()

unique_texts = list(dict.fromkeys(
    clean_text(row[field])
    for row in rows
    for field in FIELDS
))
vectors = {}

print("Unique texts:", len(unique_texts))
print("Encoding with CLS-token embeddings...")

with torch.no_grad():
    for start in range(0, len(unique_texts), 16):
        batch_texts = unique_texts[start:start + 16]
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        outputs = model(**inputs)

        # SPECTER2 paper embeddings use the CLS representation.
        batch_vectors = outputs.last_hidden_state[:, 0, :].cpu().numpy()

        for text, vector in zip(batch_texts, batch_vectors):
            vectors[text] = vector.astype(np.float32)

if not all(np.isfinite(v).all() for v in vectors.values()):
    raise SystemExit("Non-finite embedding detected; stopping.")

records = []

for row in rows:
    v = {
        field: vectors[clean_text(row[field])]
        for field in FIELDS
    }
    norms = {field: float(np.linalg.norm(v[field])) for field in FIELDS}

    d_ab = cosine_distance(v["A"], v["B"])
    d_abm = cosine_distance(v["A"], v["B_min"])
    d_ac = cosine_distance(v["A"], v["C"])
    d_act = cosine_distance(v["A"], v["C_tilde"])

    lengths = {field: word_count(row[field]) for field in FIELDS}

    records.append({
        "id": row["id"],
        "C_type": row["C_type"],
        "d_A_B": d_ab,
        "d_A_B_min": d_abm,
        "d_A_C": d_ac,
        "d_A_C_tilde": d_act,
        "norm_A": norms["A"],
        "norm_W": norms["broader"],
        "norm_N": norms["narrower"],
        "scope_order_correct": float(
            norms["broader"] < norms["A"] < norms["narrower"]
        ),
        "length_only_order_correct": float(
            lengths["broader"] < lengths["A"] < lengths["narrower"]
        ),
        "length_flipped": bool(
            lengths["broader"] > lengths["narrower"]
        ),
        "near_miss_error": float(d_ac < d_ab),
        "overlap_shortcut": float(d_ac < d_abm),
        "low_overlap_shortcut": float(d_act < d_ab)
    })

metrics = [
    "scope_order_correct",
    "length_only_order_correct",
    "near_miss_error",
    "overlap_shortcut",
    "low_overlap_shortcut"
]

summary = {
    "model_id": base,
    "adapter": "allenai/specter2",
    "embedding_method": "last_hidden_state[:, 0, :] (CLS token)",
    "n": len(records),
    "scope_method": (
        "Unnormalized CLS embedding norm; exploratory only. "
        "Expected norm(W) < norm(A) < norm(N)."
    )
}

for metric in metrics:
    summary[metric] = bootstrap_metric(records, metric)

summary["length_flipped_n"] = sum(
    r["length_flipped"] for r in records
)
flipped = [r for r in records if r["length_flipped"]]

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
        "scope_order": bootstrap_metric(subset, "scope_order_correct")
    }

(OUT / "specter2_corrected_items.json").write_text(
    json.dumps(records, indent=2, ensure_ascii=False) + "\n"
)
(OUT / "specter2_corrected_summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
)
(OUT / "specter2_corrected_by_type.json").write_text(
    json.dumps(by_type, indent=2, ensure_ascii=False) + "\n"
)

print("\nCORRECTED SPECTER2 SUMMARY")
print(json.dumps(summary, indent=2))
print("\nSaved corrected results to:", OUT)
print("Original results were not overwritten.")
