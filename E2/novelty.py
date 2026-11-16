"""Novelty measures for ASI assignment E2.

Measures:
    Y       = 1 - max cosine similarity to an eligible prior paper
    N       = 1 - mean claim-level maximum cosine similarity
    yours   = 0.75 * Y + 0.25 * N
    density = Relative Neighbour Density (RND), on a 0--100 scale

The embedding model is fixed to allenai/specter2_base to match the
model configuration used in the existing E1 experiment.

Only papers with publication timestamps strictly earlier than t are
eligible. pool_ids must contain paper IDs, not pool names.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
from transformers import AutoTokenizer
from adapters import AutoAdapterModel


ROOT = Path(__file__).resolve().parent.parent
RAW_PAPERS = ROOT / "E2" / "data" / "raw_papers.jsonl"
CACHE_DB = ROOT / "E2" / "data" / "novelty_embeddings.sqlite3"

# SPECTER2 proximity adapter with CLS-token embeddings.
# Versioned cache key prevents reuse of earlier mean-pooled embeddings.
BASE_MODEL_ID = "allenai/specter2_base"
ADAPTER_ID = "allenai/specter2"
MODEL_ID = "specter2_base+proximity-adapter+cls-v1"

RND_P = 100
RND_Q = 50
Y_WEIGHT = 0.75
N_WEIGHT = 0.25
MAX_LENGTH = 512

_MODEL = None
_TOKENIZER = None
_PAPERS = None


def _load_model():
    """Load SPECTER2 and explicitly activate its proximity adapter."""
    global _MODEL, _TOKENIZER

    if _MODEL is None:
        _TOKENIZER = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
        model = AutoAdapterModel.from_pretrained(BASE_MODEL_ID)

        model.load_adapter(
            ADAPTER_ID,
            source="hf",
            load_as="proximity",
            set_active=True,
        )
        model.set_active_adapters("proximity")
        model.eval()

        if "proximity" not in model.adapters_config:
            raise RuntimeError("SPECTER2 proximity adapter was not loaded.")

        active = str(model.active_adapters)
        if "proximity" not in active:
            raise RuntimeError(
                f"Expected proximity adapter to be active; got {active}"
            )

        _MODEL = model

    return _MODEL


def _load_papers() -> Dict[str, dict]:
    """Load the local paper metadata, indexed by paper ID."""
    global _PAPERS
    if _PAPERS is not None:
        return _PAPERS

    if not RAW_PAPERS.exists():
        raise FileNotFoundError(f"Paper dataset not found: {RAW_PAPERS}")

    papers = {}
    with RAW_PAPERS.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at {RAW_PAPERS}:{line_number}"
                ) from exc

            paper_id = row.get("paper_id")
            if not paper_id:
                raise ValueError(
                    f"Missing paper_id at {RAW_PAPERS}:{line_number}"
                )
            papers[paper_id] = row

    # Supplemental synthetic papers are kept separate from the frozen
    # source corpus and are used only for controlled manipulation tests.
    supplemental = ROOT / "E2" / "data" / "manipulation_papers.jsonl"
    if supplemental.exists():
        with supplemental.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at {supplemental}:{line_number}"
                    ) from exc

                paper_id = row.get("paper_id")
                if not paper_id:
                    raise ValueError(
                        f"Missing paper_id at {supplemental}:{line_number}"
                    )
                if paper_id in papers:
                    raise ValueError(
                        f"Supplemental paper ID conflicts with source corpus: "
                        f"{paper_id}"
                    )
                papers[paper_id] = row

    _PAPERS = papers
    return papers


def _parse_time(value: str) -> datetime:
    """Parse an ISO timestamp/date into a timezone-aware datetime."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("t and paper publication dates must be non-empty strings")

    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date/time: {value!r}") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _paper_text(row: dict) -> str:
    """Represent a paper using its title and abstract."""
    title = (row.get("title") or "").strip()
    abstract = (row.get("abstract") or "").strip()

    if title and abstract:
        return f"{title}\n\n{abstract}"
    return title or abstract


def _normalise_text(text: str) -> str:
    return " ".join((text or "").casefold().split())


def _connect_cache():
    CACHE_DB.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(CACHE_DB)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            model_id TEXT NOT NULL,
            text_hash TEXT NOT NULL,
            text_value TEXT NOT NULL,
            vector_json TEXT NOT NULL,
            PRIMARY KEY (model_id, text_hash)
        )
        """
    )
    return connection


def _hash_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _encode(texts: Sequence[str], batch_size: int = 16) -> np.ndarray:
    """Encode text using normalised SPECTER2 proximity-adapter CLS vectors."""
    if not texts:
        return np.empty((0, 768), dtype=np.float32)

    import hashlib

    unique_texts = list(dict.fromkeys(texts))
    connection = _connect_cache()
    vectors_by_text = {}
    missing = []

    try:
        for text in unique_texts:
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            record = connection.execute(
                """
                SELECT vector_json FROM embeddings
                WHERE model_id = ? AND text_hash = ?
                """,
                (MODEL_ID, digest),
            ).fetchone()

            if record is None:
                missing.append((text, digest))
                continue

            vector = np.asarray(json.loads(record[0]), dtype=np.float32)
            if vector.shape != (768,) or not np.isfinite(vector).all():
                missing.append((text, digest))
            else:
                vectors_by_text[text] = vector

        if missing:
            model = _load_model()
            generated = []

            for offset in range(0, len(missing), batch_size):
                batch = missing[offset:offset + batch_size]
                batch_texts = [item[0] for item in batch]

                inputs = _TOKENIZER(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=MAX_LENGTH,
                    return_tensors="pt",
                )

                with torch.no_grad():
                    outputs = model(**inputs)
                    vectors = outputs.last_hidden_state[:, 0, :]

                vectors = torch.nn.functional.normalize(
                    vectors.float(), p=2, dim=1
                )
                generated.extend(vectors.cpu().numpy().astype(np.float32))

            for (text, digest), vector in zip(missing, generated):
                if vector.shape != (768,) or not np.isfinite(vector).all():
                    raise RuntimeError("SPECTER2 produced an invalid vector.")

                vectors_by_text[text] = vector
                connection.execute(
                    """
                    INSERT OR REPLACE INTO embeddings
                    (model_id, text_hash, text_value, vector_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        MODEL_ID,
                        digest,
                        text,
                        json.dumps(vector.tolist(), separators=(",", ":")),
                    ),
                )

            connection.commit()

        result = np.vstack([vectors_by_text[text] for text in texts])
        norms = np.linalg.norm(result, axis=1)

        if not np.isfinite(result).all() or not np.allclose(
            norms, 1.0, atol=1e-4
        ):
            raise RuntimeError("Embedding validation failed.")

        return result.astype(np.float32)
    finally:
        connection.close()


def _eligible_papers(
    pool_ids: Sequence[str],
    cutoff: datetime,
    idea_text: str,
) -> List[dict]:
    """Return requested pool papers published strictly before cutoff."""
    papers = _load_papers()

    if isinstance(pool_ids, (str, bytes)):
        raise TypeError("pool_ids must be a sequence of paper IDs, not a string")

    ids = list(dict.fromkeys(pool_ids))
    unknown = [paper_id for paper_id in ids if paper_id not in papers]
    if unknown:
        preview = ", ".join(map(str, unknown[:5]))
        raise ValueError(
            f"{len(unknown)} unknown paper ID(s), including: {preview}"
        )

    idea_key = _normalise_text(idea_text)
    eligible = []

    for paper_id in ids:
        row = papers[paper_id]
        published = row.get("published")

        if not published:
            continue

        try:
            publication_time = _parse_time(published)
        except ValueError:
            continue

        if publication_time >= cutoff:
            continue

        text = _paper_text(row)
        if not text:
            continue

        # Safety check: avoid an exact title/abstract text match being
        # treated as its own prior paper. Callers should still exclude
        # the focal paper from pool_ids explicitly.
        if (
            idea_key
            and not row.get("synthetic_manipulation", False)
            and idea_key in {
                _normalise_text(row.get("abstract", "")),
                _normalise_text(row.get("title", "")),
                _normalise_text(text),
            }
        ):
            continue

        eligible.append(
            {
                "paper_id": paper_id,
                "published": published,
                "text": text,
            }
        )

    return eligible


def _cosine_distance_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine distance for already-normalised embeddings."""
    similarities = np.clip(np.einsum("ik,jk->ij", a, b), -1.0, 1.0)
    return 1.0 - similarities


def _rnd_score(
    idea_vector: np.ndarray,
    pool_vectors: np.ndarray,
    p: int = RND_P,
    q: int = RND_Q,
) -> float:
    """Calculate Relative Neighbour Density novelty on a 0--100 scale.

    P is the number of nearest pool papers used in the rank comparison.
    Q is the number of neighbours used to estimate local density.

    The query's density is its mean cosine distance to its Q nearest
    pool papers. Each of the query's P nearest papers receives a density
    estimate from its Q nearest *other* pool papers; self-distance is
    excluded. The result is the percentage of those P papers whose
    estimated density is <= the query's density.

    For small pools, P and Q are reduced to the available sample size.
    This is a practical small-pool convention, not the paper's reported
    P=100, Q=50 configuration.
    """
    n = len(pool_vectors)
    if n < 2:
        raise ValueError("RND requires at least two eligible pool papers")

    p = min(max(1, int(p)), n)
    q = min(max(1, int(q)), n - 1)

    query_distances = _cosine_distance_matrix(
        idea_vector.reshape(1, -1), pool_vectors
    )[0]

    # P nearest papers define the distribution used for the rank.
    first_indices = np.argsort(query_distances, kind="stable")[:p]

    # Q nearest papers define the query's local density.
    query_nearest = np.argsort(query_distances, kind="stable")[:q]
    idea_density = float(np.mean(query_distances[query_nearest]))

    # Compute each pool paper's local density once from pairwise distances.
    pool_distances = _cosine_distance_matrix(pool_vectors, pool_vectors)

    neighbour_densities = []
    for neighbour_index in first_indices:
        distances = pool_distances[neighbour_index].copy()

        # Exclude the paper itself from its own density estimate.
        distances[neighbour_index] = np.inf

        nearest = np.argsort(distances, kind="stable")[:q]
        neighbour_densities.append(float(np.mean(distances[nearest])))

    neighbour_densities = np.asarray(
        neighbour_densities, dtype=np.float64
    )
    return float(
        100.0 * np.mean(neighbour_densities <= idea_density)
    )


def score(
    idea_text: str,
    claims: list[str],
    pool_ids: list[str],
    t: str,
) -> dict:
    """Return {'Y': ..., 'density': ..., 'N': ..., 'yours': ...}.

    Args:
        idea_text: Text describing the focal research idea.
        claims: Atomic claims extracted from the focal idea.
        pool_ids: IDs of papers eligible to be considered as prior work.
        t: ISO cutoff date/time. Only papers published strictly before t
           are used.

    Returns:
        A dictionary containing Y, density, N and yours. Y, N and yours
        are cosine-distance-based scores; density is on a 0--100 scale.

    Raises:
        ValueError for empty text, missing claims, or an empty eligible pool.
        ValueError for an unknown paper ID or an invalid timestamp.
    """
    if not isinstance(idea_text, str) or not idea_text.strip():
        raise ValueError("idea_text must be a non-empty string")

    if not claims or any(
        not isinstance(claim, str) or not claim.strip() for claim in claims
    ):
        raise ValueError("claims must contain at least one non-empty string")

    cutoff = _parse_time(t)
    eligible = _eligible_papers(pool_ids, cutoff, idea_text)

    if not eligible:
        raise ValueError(
            "No eligible prior papers remain after ID and date filtering"
        )

    paper_texts = [row["text"] for row in eligible]
    paper_vectors = _encode(paper_texts)

    # The model returns unit-normalised vectors, so dot products are
    # cosine similarities.
    idea_vector = _encode([idea_text])[0]
    claim_vectors = _encode([claim.strip() for claim in claims])

    paper_similarities = np.clip(np.einsum("ij,j->i", paper_vectors, idea_vector), -1.0, 1.0)
    claim_similarities = np.clip(np.einsum("ik,jk->ij", claim_vectors, paper_vectors), -1.0, 1.0)

    Y = float(1.0 - np.max(paper_similarities))
    N = float(1.0 - np.mean(np.max(claim_similarities, axis=1)))
    yours = float(Y_WEIGHT * Y + N_WEIGHT * N)
    density = _rnd_score(idea_vector, paper_vectors)

    return {
        "Y": Y,
        "density": density,
        "N": N,
        "yours": yours,
    }
