"""Deterministic, non-scoring A1 controls over source paper IDs."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys


class ControlError(ValueError):
    pass


SPECTER2_BASE_REVISION = "3447645e1def9117997203454fa4495937bfbd83"
SPECTER2_ADAPTER_REVISION = "2081559630a80fc5851d8f798a05ba81e9468089"
E2_NOVELTY_SHA256 = "30276aee4718359840fe72b143ccfccc7c166c74f5dcb5c0953fdd48fbd5215c"
_E2_MODEL_LOCK_VERIFIED = False


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_e2_snapshot(cache_root: Path) -> None:
    models = {
        "models--allenai--specter2_base": (SPECTER2_BASE_REVISION, {
            "config.json": "6d9d68ca2bfeca756fd807e7c81e8e9d3203d8a002dff19cc42b29edd48e8802",
            "pytorch_model.bin": "801eda968fad1752fe846a8e572bfdc25202be85544680dda4c99f4589646ebc",
            "tokenizer.json": "fcd3fffca5d8fcc0d5863406f5f491293c1e4658ed503f424a30324b70533c0d",
            "tokenizer_config.json": "afea6e85bb539b2c2de8847d92c2a3ae88334c280abbbdb3baaddc5fb7195242",
            "special_tokens_map.json": "b6d346be366a7d1d48332dbc9fdf3bf8960b5d879522b7799ddba59e76237ee3",
            "vocab.txt": "f0a650346e51ede8996710f79ba65d83fdb8da05b159f17037b74ba4e3a36c6f",
        }),
        "models--allenai--specter2": (SPECTER2_ADAPTER_REVISION, {
            "adapter_config.json": "1065ad610a661c5169f05d81040fe14429d2cc7ecdf83ed654dca4a62aaf9a8c",
            "pytorch_adapter.bin": "5b6105714f78b294daa7e2d181134df12f0acb7a4ec7c1e3c13e512c908db94a",
        }),
    }
    for name, (revision, files) in models.items():
        root = cache_root / name
        ref = root / "refs" / "main"
        if not ref.is_file() or ref.read_text().strip() != revision:
            raise ControlError(f"cached {name} main ref does not match the preregistered revision")
        snapshot = root / "snapshots" / revision
        for relative, expected in files.items():
            target = snapshot / relative
            if not target.is_file() or _file_sha256(target) != expected:
                raise ControlError(f"cached model artifact hash mismatch: {name}/{relative}")
    novelty_file = Path(__file__).resolve().parents[2] / "E2" / "novelty.py"
    if _file_sha256(novelty_file) != E2_NOVELTY_SHA256:
        raise ControlError("E2 novelty implementation differs from the registered code hash")


def _time(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ControlError("missing or invalid timezone-aware publication timestamp") from exc
    if result.tzinfo is None:
        raise ControlError("publication timestamp must include a timezone")
    return result.astimezone(timezone.utc)


def _digest(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _question(instance: dict) -> str:
    value = instance.get("question")
    if not value:
        value = "\n\n".join(x for x in (instance.get("title"), instance.get("abstract")) if x)
    if not isinstance(value, str) or not value.strip():
        raise ControlError("focal question text is missing")
    return value.strip()


def _prior_ids(ids: list[str], focal_id: str, cutoff: datetime, papers: dict[str, dict]) -> list[str]:
    result = []
    for pid in ids:
        if pid == focal_id:
            continue
        paper = papers.get(pid)
        if paper is None:
            raise ControlError(f"unknown input paper ID: {pid}")
        published = _time(paper.get("published"))
        if published < cutoff:
            result.append(pid)
    if len(result) != len(set(result)):
        raise ControlError("input pool contains duplicate paper IDs")
    return result


def _condition(focal_id: str, kind: str, question: str, ids: list[str], **metadata) -> dict:
    identity = {"focal_paper_id": focal_id, "condition": kind, "question": question,
                "input_paper_ids": ids, **metadata}
    return {"record_id": "a1e2-" + _digest(identity), "pair_id": focal_id,
            "focal_paper_id": focal_id, "condition": kind, "question": question,
            "input_paper_ids": ids, **metadata}


def _unavailable_condition(focal_id: str, kind: str, reason: str) -> dict:
    identity = {"focal_paper_id": focal_id, "condition": kind,
                "status": "unavailable", "reason": reason}
    return {"record_id": "a1e2-" + _digest(identity), "pair_id": focal_id,
            "focal_paper_id": focal_id, "condition": kind,
            "status": "unavailable", "reason": reason}


def build_controls(*, focal: dict, original_input_ids: list[str], papers: dict[str, dict],
                   other_instances: list[dict]) -> list[dict]:
    """Build original/empty/shuffled controls and mark the decoy unavailable."""
    focal_id = focal.get("paper_id")
    if not focal_id:
        raise ControlError("focal paper ID is required")
    focal_question = _question(focal)
    focal_cutoff = _time(focal.get("published"))
    original = _prior_ids(original_input_ids, focal_id, focal_cutoff, papers)
    if not original:
        raise ControlError("original input pool has no temporally eligible papers")

    # A shuffle is a different focal instance's supplied input set, filtered
    # again at this focal paper's publication time.
    shuffled_choices = []
    for other in other_instances:
        oid = other.get("paper_id")
        if not oid or oid == focal_id:
            continue
        candidate = _prior_ids(other.get("input_paper_ids", []), focal_id, focal_cutoff, papers)
        if candidate and set(candidate) != set(original):
            shuffled_choices.append((oid, candidate))
    if not shuffled_choices:
        raise ControlError("no distinct temporally eligible shuffled input set")
    shuffled_focal_id, shuffled = min(shuffled_choices, key=lambda x: x[0])

    return [
        _condition(focal_id, "original", focal_question, original),
        _condition(focal_id, "empty", focal_question, [], score_status="undefined",
                   score_reason="E2 novelty score is undefined for an empty eligible pool"),
        _condition(focal_id, "shuffled", focal_question, shuffled,
                   shuffled_from_focal_paper_id=shuffled_focal_id),
        _unavailable_condition(
            focal_id, "same_topic_decoy",
            "unavailable under approved Amendment 003; no decoy condition is scored",
        ),
    ]


def score_control(condition: dict, score_fn, *, claims: list[str], cutoff: str):
    """Delegate nonempty cases to E2; represent empty-pool score as undefined."""
    if condition.get("status") == "unavailable":
        raise ControlError(f"{condition.get('condition', 'condition')} is unavailable and cannot be scored")
    if condition.get("condition") == "empty":
        if condition.get("input_paper_ids") != []:
            raise ControlError("empty control must have no input IDs")
        return {"status": "undefined", "reason": "empty eligible pool has no E2 novelty score"}
    return {"status": "scored", "scores": score_fn(
        idea_text=condition["question"], claims=claims,
        pool_ids=condition["input_paper_ids"], t=cutoff)}


def score_with_e2(condition: dict, *, claims: list[str], cutoff: str):
    """Explicit adapter to the existing E2 novelty.score entry point."""
    global _E2_MODEL_LOCK_VERIFIED
    if condition.get("condition") == "empty":
        return score_control(condition, None, claims=claims, cutoff=cutoff)
    if not _E2_MODEL_LOCK_VERIFIED:
        if "E2.novelty" in sys.modules:
            from E2 import novelty
            if novelty._MODEL is not None:
                raise ControlError("E2 model was initialized before its local model lock was verified")
        hf_cache = Path(os.environ.get("HF_HUB_CACHE", Path.home() / ".cache/huggingface/hub"))
        _verify_e2_snapshot(hf_cache)
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from E2 import novelty
        if (novelty.MODEL_ID != "specter2_base+proximity-adapter+cls-v1" or
                novelty.MAX_LENGTH != 512 or novelty.RND_P != 100 or novelty.RND_Q != 50 or
                novelty.Y_WEIGHT != 0.75 or novelty.N_WEIGHT != 0.25):
            raise ControlError("E2 novelty settings differ from the registered configuration")
        if novelty._MODEL is not None:
            raise ControlError("E2 model was initialized before the lock check")
        cache_file = Path(__file__).resolve().parent / (
            f"novelty_embeddings_{SPECTER2_BASE_REVISION[:8]}_{SPECTER2_ADAPTER_REVISION[:8]}.sqlite3")
        if cache_file.exists():
            raise ControlError("revision-keyed A1 embedding cache already exists; provenance is unverified")
        novelty.CACHE_DB = cache_file
        _E2_MODEL_LOCK_VERIFIED = True
    else:
        from E2 import novelty
    return score_control(condition, novelty.score, claims=claims, cutoff=cutoff)
