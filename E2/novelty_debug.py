"""
novelty_debug.py — drop-in diagnostic wrapper for E2/novelty.py

Usage
-----
Run from ~/asi-selection:

    python E2/novelty_debug.py

This module imports novelty.py, monkey-patches _encode() and score() with
instrumented versions, runs a single three-condition pilot, and prints
exactly where any numerical problem occurs.

Nothing is written to the cache, the database, or the model weights.
The original novelty.py is not modified.
"""

from __future__ import annotations

import importlib
import json
import sys
import traceback
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_array(arr: np.ndarray, label: str) -> None:
    """Assert shape, finiteness and approximate unit norm. Raises on failure."""
    if arr.ndim not in (1, 2):
        raise ValueError(f"[DIAG] {label}: unexpected ndim={arr.ndim}")
    if not np.all(np.isfinite(arr)):
        n_nan = int(np.sum(np.isnan(arr)))
        n_inf = int(np.sum(np.isinf(arr)))
        raise ValueError(
            f"[DIAG] {label}: non-finite values — nan={n_nan} inf={n_inf}\n"
            f"  shape={arr.shape} dtype={arr.dtype}\n"
            f"  first bad index: {np.argwhere(~np.isfinite(arr))[0]}"
        )
    if arr.ndim == 2:
        norms = np.linalg.norm(arr, axis=1)
    else:
        norms = np.array([np.linalg.norm(arr)])
    bad = np.abs(norms - 1.0) > 0.01
    if np.any(bad):
        raise ValueError(
            f"[DIAG] {label}: {int(bad.sum())} vector(s) not unit-norm\n"
            f"  norms min={norms.min():.6f} mean={norms.mean():.6f} max={norms.max():.6f}\n"
            f"  shape={arr.shape} dtype={arr.dtype}"
        )
    print(
        f"[DIAG] OK  {label}: shape={arr.shape} dtype={arr.dtype} "
        f"norm_range=[{norms.min():.6f}, {norms.max():.6f}]"
    )


def _safe_matmul(a: np.ndarray, b: np.ndarray, label: str) -> np.ndarray:
    """Run a @ b with errstate=raise and print context on failure."""
    print(f"[DIAG] matmul {label}: {a.shape} @ {b.shape}")
    with np.errstate(divide="raise", over="raise", invalid="raise"):
        try:
            result = a @ b
        except FloatingPointError as exc:
            raise FloatingPointError(
                f"[DIAG] matmul FAILED at {label}: {exc}\n"
                f"  a: shape={a.shape} dtype={a.dtype} "
                f"finite={np.all(np.isfinite(a))}\n"
                f"  b: shape={b.shape} dtype={b.dtype} "
                f"finite={np.all(np.isfinite(b))}"
            ) from exc
    return result


# ---------------------------------------------------------------------------
# Patch factory
# ---------------------------------------------------------------------------

def _make_instrumented_score(original_score, original_encode):
    """Return a score() that instruments every matmul and encode call."""

    def instrumented_score(
        idea_text: str,
        claims: list[str],
        pool_ids: list[str],
        t: str,
    ) -> dict:
        print("\n[DIAG] ── score() called ──────────────────────────────────")
        print(f"[DIAG]   idea_text length : {len(idea_text)}")
        print(f"[DIAG]   claims           : {len(claims)}")
        print(f"[DIAG]   pool_ids         : {len(pool_ids)}")

        # ── encode pool papers ────────────────────────────────────────────
        print("\n[DIAG] Encoding pool papers ...")
        # call original encode via the module so the cache is used normally
        import E2.novelty as _nov
        cutoff = _nov._parse_time(t)
        eligible = _nov._eligible_papers(pool_ids, cutoff, idea_text)
        print(f"[DIAG]   eligible papers  : {len(eligible)}")
        if not eligible:
            raise ValueError("[DIAG] No eligible papers after filtering.")

        paper_texts = [row["text"] for row in eligible]
        paper_vectors = _nov._encode(paper_texts)
        paper_vectors = np.array(paper_vectors, dtype=np.float64)
        _check_array(paper_vectors, "paper_vectors")

        # ── encode idea ───────────────────────────────────────────────────
        print("\n[DIAG] Encoding idea ...")
        idea_vector = _nov._encode([idea_text])[0]
        idea_vector = np.array(idea_vector, dtype=np.float64)
        _check_array(idea_vector, "idea_vector")

        # ── encode claims ─────────────────────────────────────────────────
        print("\n[DIAG] Encoding claims ...")
        claim_vectors = _nov._encode([c.strip() for c in claims])
        claim_vectors = np.array(claim_vectors, dtype=np.float64)
        _check_array(claim_vectors, "claim_vectors")

        # ── matmul 1: paper_vectors @ idea_vector ─────────────────────────
        print("\n[DIAG] Computing paper_similarities ...")
        paper_sims_raw = _safe_matmul(
            paper_vectors, idea_vector, "paper_vectors @ idea_vector"
        )
        paper_similarities = np.clip(paper_sims_raw, -1.0, 1.0)
        print(f"[DIAG]   raw  range [{paper_sims_raw.min():.6f}, {paper_sims_raw.max():.6f}]")
        print(f"[DIAG]   clip range [{paper_similarities.min():.6f}, {paper_similarities.max():.6f}]")
        out_of_range = np.sum((paper_sims_raw < -1.0) | (paper_sims_raw > 1.0))
        if out_of_range:
            print(f"[DIAG]   WARNING: {out_of_range} raw values outside [-1, 1] before clip")

        # ── matmul 2: claim_vectors @ paper_vectors.T ─────────────────────
        print("\n[DIAG] Computing claim_similarities ...")
        claim_sims_raw = _safe_matmul(
            claim_vectors, paper_vectors.T, "claim_vectors @ paper_vectors.T"
        )
        claim_similarities = np.clip(claim_sims_raw, -1.0, 1.0)
        print(f"[DIAG]   raw  range [{claim_sims_raw.min():.6f}, {claim_sims_raw.max():.6f}]")
        print(f"[DIAG]   clip range [{claim_similarities.min():.6f}, {claim_similarities.max():.6f}]")
        out_of_range = np.sum((claim_sims_raw < -1.0) | (claim_sims_raw > 1.0))
        if out_of_range:
            print(f"[DIAG]   WARNING: {out_of_range} raw values outside [-1, 1] before clip")

        # ── cosine distance matrix ────────────────────────────────────────
        print("\n[DIAG] Computing _cosine_distance_matrix (pool x pool) ...")
        _check_array(paper_vectors, "paper_vectors (for RND)")
        pool_sims_raw = _safe_matmul(
            paper_vectors, paper_vectors.T,
            "_cosine_distance_matrix: paper_vectors @ paper_vectors.T"
        )
        print(f"[DIAG]   pool sims range [{pool_sims_raw.min():.6f}, {pool_sims_raw.max():.6f}]")

        # ── scores ────────────────────────────────────────────────────────
        Y = float(1.0 - np.max(paper_similarities))
        N = float(1.0 - np.mean(np.max(claim_similarities, axis=1)))
        print(f"\n[DIAG] Y={Y:.6f}  N={N:.6f}")

        # call the real score() to get density (RND) — let it use its own path
        result = original_score(idea_text, claims, pool_ids, t)
        print(f"[DIAG] Final result: {result}")
        return result

    return instrumented_score


# ---------------------------------------------------------------------------
# Adapter verification
# ---------------------------------------------------------------------------

def _verify_adapter():
    print("\n[DIAG] ── Adapter verification ────────────────────────────────")
    try:
        import E2.novelty as _nov
        model = _nov._load_model()

        # adapters package API
        cfg = model.adapters_config
        print(f"[DIAG]   adapters_config keys : {list(cfg)}")

        active = model.active_adapters
        print(f"[DIAG]   active_adapters       : {active}")
        print(f"[DIAG]   str(active_adapters)  : {str(active)}")

        # check 'proximity' is in the config
        if "proximity" in cfg:
            print("[DIAG]   'proximity' loaded    : YES")
        else:
            print("[DIAG]   'proximity' loaded    : NO — adapter not in config")

        # run a single forward pass and check the output
        import torch
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(_nov.BASE_MODEL_ID)
        txt = "test input for adapter verification"
        inp = tok(txt, return_tensors="pt", max_length=64,
                  truncation=True, padding=True)
        with torch.no_grad():
            out = model(**inp)
        cls = out.last_hidden_state[:, 0, :].squeeze().float().numpy()
        raw_norm = float(np.linalg.norm(cls))
        print(f"[DIAG]   forward pass CLS norm : {raw_norm:.4f}  "
              f"(expected ~20; near 0 would indicate adapter inactive)")
        if raw_norm < 1.0:
            print("[DIAG]   WARNING: very small CLS norm — adapter may be inactive")

    except Exception as exc:
        print(f"[DIAG]   adapter verification failed: {exc}")
        traceback.print_exc()


# ---------------------------------------------------------------------------
# Main: three-condition pilot
# ---------------------------------------------------------------------------

def main():
    # add repo root to path so 'import E2.novelty' works
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    print("[DIAG] Importing E2.novelty ...")
    import E2.novelty as _nov  # noqa: F401  (side-effect: loads constants)

    _verify_adapter()

    # ── load a real baseline experiment case ───────────────────────────
    plan_path = Path("E2/data/manipulation_plan.jsonl")

    if not plan_path.exists():
        sys.exit(f"[DIAG] ERROR: {plan_path} not found.")

    records = [
        json.loads(line)
        for line in plan_path.read_text().splitlines()
        if line.strip()
    ]

    baseline_cases = [
        record for record in records
        if record.get("manipulation") == "baseline"
    ]

    if not baseline_cases:
        sys.exit("[DIAG] ERROR: No baseline cases found.")

    fp = baseline_cases[0]
    idea_text = fp.get("idea_text", "")
    claims = fp.get("claims", [])
    pool_ids = fp.get("pool_ids", [])
    t = fp.get("t")

    if not isinstance(idea_text, str) or not idea_text.strip():
        sys.exit("[DIAG] ERROR: Baseline idea_text is empty.")
    if not isinstance(claims, list) or not claims:
        sys.exit("[DIAG] ERROR: Baseline claims are missing.")
    if not isinstance(pool_ids, list) or not pool_ids:
        sys.exit("[DIAG] ERROR: Baseline pool_ids are missing.")
    if not t:
        sys.exit("[DIAG] ERROR: Baseline cutoff is missing.")

    print(f"\\n[DIAG] Case ID         : {fp.get('case_id', '?')}")
    print(f"[DIAG] Pool            : {fp.get('pool', '?')}")
    print(f"[DIAG] Manipulation    : {fp.get('manipulation', '?')}")
    print(f"[DIAG] Focal paper id  : {fp.get('focal_paper_id', '?')}")
    print(f"[DIAG] idea_text[:80] : {idea_text[:80]}")
    print(f"[DIAG] claims          : {len(claims)}")
    print(f"[DIAG] cutoff t        : {t}")
    print(f"[DIAG] pool size       : {len(pool_ids)}")

    # ── patch score() ─────────────────────────────────────────────────────
    import E2.novelty as _nov2
    original_score  = _nov2.score
    original_encode = _nov2._encode
    _nov2.score = _make_instrumented_score(original_score, original_encode)

    # ── run baseline condition ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("[DIAG] CONDITION: baseline (no manipulation)")
    print("=" * 60)
    try:
        result = _nov2.score(idea_text, claims, pool_ids, t)
        print(f"[DIAG] baseline result: {result}")
    except Exception as exc:
        print(f"[DIAG] baseline FAILED: {exc}")
        traceback.print_exc()

    print("\n[DIAG] ── Done ────────────────────────────────────────────────")
    print("[DIAG] If no FloatingPointError appeared, the warnings come from")
    print("[DIAG] a code path not exercised above (e.g. _rnd_score internals).")
    print("[DIAG] In that case, add np.errstate(divide='raise', invalid='raise')")
    print("[DIAG] around the pool_distances matmul inside _rnd_score and rerun.")


if __name__ == "__main__":
    main()
