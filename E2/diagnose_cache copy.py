#!/usr/bin/env python3
"""Read-only diagnostic for E2/data/novelty_embeddings.sqlite3.

Schema: embeddings(model_id TEXT, text_hash TEXT, text_value TEXT, vector_json TEXT)
Primary key: (model_id, text_hash)

Run from the repo root:
    python E2/diagnose_cache.py

Nothing in this script writes to the database or modifies any file.
Root-cause conclusions are deferred until the output supports them.
"""
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np

# ── configuration ─────────────────────────────────────────────────────────────
DB = Path("E2/data/novelty_embeddings.sqlite3")
MODEL_ID = "specter2_base+proximity-adapter+cls-v1"
EXPECTED_DIM = 768
NORM_TOL = 0.01      # flag vectors with |norm - 1| > this
ZERO_TOL = 1e-8      # flag vectors with norm < this
SNIPPET = 60         # characters of text_value shown in reports

# ── helpers ───────────────────────────────────────────────────────────────────
def snip(text):
    if text is None:
        return "<NULL>"
    s = str(text)
    return s[:SNIPPET] + "…" if len(s) > SNIPPET else s

def hash_snip(h):
    if h is None:
        return "<NULL>"
    return str(h)[:16]

# ── open database (read-only) ─────────────────────────────────────────────────
if not DB.exists():
    sys.exit(f"ERROR: database not found at {DB}")

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

# ═════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("1. SCHEMA")
print("=" * 70)
for (tbl,) in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall():
    print(f"\n  table: {tbl}")
    for col in con.execute(f"PRAGMA table_info({tbl})").fetchall():
        print(f"    {col}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. ROW COUNTS PER MODEL ID")
print("=" * 70)
for row in con.execute(
    "SELECT model_id, COUNT(*) n FROM embeddings GROUP BY model_id ORDER BY n DESC"
).fetchall():
    marker = "  <-- TARGET" if row[0] == MODEL_ID else ""
    print(f"  {row[1]:>6}  {row[0]}{marker}")

total_target = con.execute(
    "SELECT COUNT(*) FROM embeddings WHERE model_id=?", (MODEL_ID,)
).fetchone()[0]
print(f"\n  Rows for target model_id: {total_target}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"3. VECTOR DIAGNOSTICS — all {total_target} rows for target model_id")
print("=" * 70)

cursor = con.execute(
    "SELECT text_hash, text_value, vector_json FROM embeddings WHERE model_id=?",
    (MODEL_ID,),
)

bad_parse  = []   # (hash_snip, text_snip, error)
bad_dim    = []   # (hash_snip, text_snip, actual_shape)
has_null   = []   # (hash_snip, text_snip)
bad_finite = []   # (hash_snip, text_snip, n_nan, n_inf)
bad_zero   = []   # (hash_snip, text_snip, norm)
bad_norm   = []   # (hash_snip, text_snip, norm)
good_norms = []

inspected = 0
for text_hash, text_value, vector_json in cursor:
    inspected += 1
    hs = hash_snip(text_hash)
    ts = snip(text_value)

    # JSON parsing
    try:
        lst = json.loads(vector_json)
    except Exception as exc:
        bad_parse.append((hs, ts, str(exc)))
        continue

    # null elements (JSON null → Python None)
    if any(x is None for x in lst):
        has_null.append((hs, ts))

    try:
        v = np.array(lst, dtype=np.float64)
    except Exception as exc:
        bad_parse.append((hs, ts, f"np.array conversion: {exc}"))
        continue

    # dimension check
    if v.shape != (EXPECTED_DIM,):
        bad_dim.append((hs, ts, v.shape))
        continue

    # finite check
    n_nan = int(np.sum(np.isnan(v)))
    n_inf = int(np.sum(np.isinf(v)))
    if n_nan or n_inf:
        bad_finite.append((hs, ts, n_nan, n_inf))
        continue

    norm = float(np.linalg.norm(v))

    if norm < ZERO_TOL:
        bad_zero.append((hs, ts, norm))
    elif abs(norm - 1.0) > NORM_TOL:
        bad_norm.append((hs, ts, round(norm, 8)))
    else:
        good_norms.append(norm)

print(f"  Rows inspected       : {inspected}")

print(f"\n  JSON parse errors    : {len(bad_parse)}")
for item in bad_parse[:5]:
    print(f"    hash={item[0]}  text={item[1]}")
    print(f"      error: {item[2]}")

print(f"\n  Wrong dimension      : {len(bad_dim)}")
for item in bad_dim[:5]:
    print(f"    hash={item[0]}  text={item[1]}  shape={item[2]}")

print(f"\n  JSON null elements   : {len(has_null)}")
for item in has_null[:5]:
    print(f"    hash={item[0]}  text={item[1]}")

print(f"\n  Non-finite (NaN/Inf) : {len(bad_finite)}")
for item in bad_finite[:5]:
    print(f"    hash={item[0]}  text={item[1]}  nan={item[2]} inf={item[3]}")

print(f"\n  Zero vectors         : {len(bad_zero)}")
for item in bad_zero[:5]:
    print(f"    hash={item[0]}  text={item[1]}  norm={item[2]:.2e}")

print(f"\n  Bad norm |n-1|>{NORM_TOL} : {len(bad_norm)}")
for item in bad_norm[:10]:
    print(f"    hash={item[0]}  text={item[1]}  norm={item[2]}")

if good_norms:
    arr = np.array(good_norms)
    print(f"\n  Good-norm vectors    : {len(arr)}")
    print(f"    min={arr.min():.8f}  mean={arr.mean():.8f}  max={arr.max():.8f}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. DUPLICATE TEXT-HASH CHECK (same model_id)")
print("=" * 70)
dups = con.execute(
    """SELECT text_hash, COUNT(*) n
       FROM embeddings
       WHERE model_id=?
       GROUP BY text_hash
       HAVING n > 1
       LIMIT 20""",
    (MODEL_ID,),
).fetchall()
print(f"  Duplicate text hashes: {len(dups)}")
for h, n in dups[:5]:
    print(f"    hash={hash_snip(h)}  count={n}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. MATMUL SAFETY TEST (cached vectors only, no model load)")
print("=" * 70)
sample_rows = con.execute(
    "SELECT vector_json FROM embeddings WHERE model_id=? LIMIT 100",
    (MODEL_ID,),
).fetchall()

sample_vecs = []
for (vj,) in sample_rows:
    try:
        lst = json.loads(vj)
        v = np.array(lst, dtype=np.float64)
        if v.shape == (EXPECTED_DIM,) and np.all(np.isfinite(v)):
            sample_vecs.append(v)
    except Exception:
        pass

if len(sample_vecs) >= 2:
    A = np.stack(sample_vecs)
    with np.errstate(divide="raise", over="raise", invalid="raise"):
        try:
            _ = A @ A.T
            print("  matmul on cached sample: no floating-point errors raised")
            print("  If NumPy warnings appeared in your run, they originated")
            print("  from freshly generated embeddings or pool assembly,")
            print("  not from these cached vectors.")
        except FloatingPointError as exc:
            print(f"  matmul raised FloatingPointError: {exc}")
            print("  At least some cached vectors cause numerical errors.")
            print("  Do not delete or overwrite entries until the root cause")
            print("  is confirmed and the deviation is logged in NOTEBOOK.md.")
else:
    print(f"  Only {len(sample_vecs)} valid cached vectors found; skipping test.")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. FRESH EMBEDDING PROBE (model load; no cache write)")
print("=" * 70)
print("  _encode() normalises the raw CLS vector after retrieval.")
print("  A raw norm != 1.0 is therefore expected and is not an error.")
print("  This section checks only that the adapter activates and that")
print("  the raw CLS output is finite and non-zero before normalisation.")
print()

try:
    import torch
    from transformers import AutoTokenizer
    from adapters import AutoAdapterModel

    tok = AutoTokenizer.from_pretrained("allenai/specter2_base")
    mdl = AutoAdapterModel.from_pretrained("allenai/specter2_base")
    mdl.load_adapter(
        "allenai/specter2", source="hf", load_as="proximity", set_active=True
    )
    mdl.set_active_adapters("proximity")
    mdl.eval()

    active = str(mdl.active_adapters)
    print(f"  active adapters string : {active}")
    print(f"  'proximity' present    : {'proximity' in active}")
    print()

    probes = [
        ("normal",    "How does data augmentation affect contrastive learning?"),
        ("one char",  "A"),
        ("very long", "word " * 200),
    ]
    for label, txt in probes:
        inp = tok(
            txt, return_tensors="pt",
            max_length=512, truncation=True, padding=True,
        )
        with torch.no_grad():
            out = mdl(**inp)
        raw = out.last_hidden_state[:, 0, :].squeeze().float().numpy()
        raw_norm   = float(np.linalg.norm(raw))
        raw_finite = bool(np.all(np.isfinite(raw)))
        raw_zero   = raw_norm < ZERO_TOL
        # simulate _encode() normalisation
        normed_norm = float(np.linalg.norm(raw / raw_norm)) if not raw_zero else 0.0
        print(
            f"  [{label:10s}]  dim={raw.shape[0]}"
            f"  raw_norm={raw_norm:.4f}"
            f"  raw_finite={raw_finite}"
            f"  raw_zero={raw_zero}"
            f"  normed_norm={normed_norm:.6f}"
        )

except Exception as exc:
    print(f"  Skipped (model load or forward pass failed): {exc}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. PRELIMINARY INTERPRETATION")
print("=" * 70)
total_bad = (
    len(bad_parse) + len(bad_dim) + len(has_null) +
    len(bad_finite) + len(bad_zero)
)
print(f"  Vectors with definite problems : {total_bad}")
print(f"  Vectors with non-unit norm     : {len(bad_norm)}")
print()
if total_bad == 0 and len(bad_norm) == 0:
    print("  All cached vectors passed every check.")
    print("  The NumPy warnings likely originate from freshly generated")
    print("  embeddings or the pool-assembly step in score(), not the cache.")
    print("  Run section 6 and inspect _encode() normalisation to continue.")
elif total_bad > 0:
    print("  Problematic cached vectors were found (see section 3).")
    print("  These are candidate causes of the matmul warnings.")
    print("  Confirm by checking whether the bad entries are actually loaded")
    print("  during the failing run before concluding the cache is the cause.")
elif len(bad_norm) > 0:
    print("  No corrupt vectors, but non-unit norms found.")
    print("  If _encode() stores raw (unnormalised) vectors and normalises")
    print("  at retrieval time, this is expected — not an error.")
    print("  If _encode() is supposed to store normalised vectors, these")
    print("  entries are stale and should be regenerated.")

con.close()
print("\n=== DIAGNOSTIC COMPLETE — database not modified ===")
