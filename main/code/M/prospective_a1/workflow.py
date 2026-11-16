"""Fail-closed helpers for a separately preregistered prospective A1 study.

No network, model, filesystem, or scoring work occurs in these helpers.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json


def _instant(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("invalid ISO-8601 timestamp") from e
    if d.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return d.astimezone(timezone.utc)


def validate_inputs(papers: list[dict], generation_time: str) -> list[str]:
    """Validate explicitly supplied, source-bound paper records."""
    gen = _instant(generation_time)
    ids = []
    for p in papers:
        required = ("paper_id", "published_at", "available_at", "source_url", "source_sha256", "source_locator")
        if any(not p.get(k) for k in required):
            raise ValueError("input paper lacks source identity, dates, or provenance")
        if len(p["source_sha256"]) != 64 or any(c not in "0123456789abcdef" for c in p["source_sha256"].lower()):
            raise ValueError("invalid source SHA-256")
        if _instant(p["published_at"]) >= gen or _instant(p["available_at"]) >= gen:
            raise ValueError("each input must be published and available before generation")
        ids.append(p["paper_id"])
    if len(ids) < 3 or len(set(ids)) != len(ids):
        raise ValueError("at least three distinct explicit input papers are required")
    return ids


def build_prompt(papers: list[dict]) -> str:
    """Build the exact generation prompt from supplied source material."""
    if len(papers) < 3 or any(not p.get("paper_id") or not p.get("text") for p in papers):
        raise ValueError("at least three identified papers with supplied text are required")
    body = "\n\n".join(f"[{p['paper_id']}] {p['text']}" for p in papers)
    return ("Using only the explicitly supplied research papers below, propose one "
            "specific, novel, answerable research question. Do not claim it is historical.\n\n" + body)


def prepare_generation_request(*, papers: list[dict], model_id: str | None = None,
                               parameters: dict | None = None, seed: int | None = None) -> dict:
    """Prepare a request without claiming it has been generated."""
    for p in papers:
        required = ("paper_id", "published_at", "available_at", "source_url", "source_sha256", "source_locator")
        if any(not p.get(k) for k in required) or len(p["source_sha256"]) != 64:
            raise ValueError("input paper lacks valid source identity, dates, or provenance")
    prompt = build_prompt(papers)
    locked = bool(model_id) and isinstance(parameters, dict) and isinstance(seed, int) and not isinstance(seed, bool)
    if any(x is not None for x in (model_id, parameters, seed)) and not locked:
        raise ValueError("model identity, parameters, and integer seed must be supplied together")
    return {"status": "PREPARED_NOT_GENERATED", "model_config_status": "SPECIFIED" if locked else "PENDING",
            "model_id": model_id, "parameters": parameters, "seed": seed,
            "prompt": prompt, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "input_records": papers}


def generate_record(*, papers: list[dict], model_id: str,
                    parameters: dict, seed: int, generator) -> dict:
    """Call an explicitly injected model adapter and bind its output to exact inputs.

    This function is deliberately not called by CLI/tests during preparation.
    """
    request = prepare_generation_request(papers=papers, model_id=model_id, parameters=parameters, seed=seed)
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    ids = validate_inputs(papers, generated_at)
    question = generator(prompt=request["prompt"], model_id=model_id, parameters=parameters, seed=seed)
    if not isinstance(question, str) or not question.strip():
        raise ValueError("generator returned no question")
    return {"question": question.strip(), "question_kind": "prospectively_generated",
            **{k: v for k, v in request.items() if k != "status"}, "R": ids}


def construct_controls(*, original_ids: list[str], shuffled_ids: list[str],
                       decoy_ids: list[str], decoy_question: str,
                       same_topic_review: dict, manipulation_evidence: dict) -> dict:
    """Create condition specifications only after provenance-bound annotations."""
    if len(original_ids) < 3 or len(set(original_ids)) != len(original_ids):
        raise ValueError("original condition requires at least three unique inputs")
    if len(shuffled_ids) < 3 or len(set(shuffled_ids)) != len(shuffled_ids) or set(shuffled_ids) == set(original_ids):
        raise ValueError("shuffled inputs must be a distinct set of at least three papers from another instance")
    if len(decoy_ids) < 3 or set(decoy_ids) == set(original_ids):
        raise ValueError("decoy requires a distinct supplied paper set")
    if not decoy_question.strip() or same_topic_review.get("decision") != "verified_same_topic" or not all(same_topic_review.get(k) for k in ("reviewer_id", "reviewed_at", "evidence_ref")):
        raise ValueError("independent, dated same-topic validation is required")
    for key in ("partial_coverage", "concentrated", "distributed"):
        item = manipulation_evidence.get(key, {})
        if not item.get("source_ref") or not item.get("verified"):
            raise ValueError(f"verified {key} manipulation evidence is required")
    return {"original": list(original_ids), "empty": [], "shuffled": list(shuffled_ids),
            "same_topic_decoy": {"question": decoy_question, "inputs": list(decoy_ids),
                                 "review": same_topic_review},
            "manipulations": manipulation_evidence}


def validate_readiness(record: dict) -> None:
    """Raise with all missing gates; never starts evaluation."""
    def sha256(value):
        return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())

    def commit(value):
        return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value.lower())

    reviews = record.get("human_validation")
    reviews_ok = (isinstance(reviews, list) and len(reviews) >= 2 and
                  all(isinstance(r, dict) and r.get("reviewer_id") and r.get("reviewed_at")
                      and r.get("evidence_ref") and r.get("decision") == "verified" for r in reviews) and
                  len({r["reviewer_id"] for r in reviews}) == len(reviews))
    gates = {
        "source provenance": bool(record.get("source_provenance_ref")) and sha256(record.get("source_provenance_sha256")),
        "dated explicit inputs": bool(record.get("inputs_temporally_valid")),
        "model lock": sha256(record.get("model_lock_sha256")) and sha256(record.get("baseline_lock_sha256")),
        "normalization lock": sha256(record.get("normalization_lock_sha256")),
        "controls and manipulations": bool(record.get("controls_validated")),
        "independent human/source validation": reviews_ok,
        "committed prospective preregistration": commit(record.get("prereg_commit")),
        "explicit execution authorization": bool(record.get("execution_authorization_ref")),
    }
    missing = [name for name, passed in gates.items() if not passed]
    if missing:
        raise ValueError("A1 execution blocked: " + ", ".join(missing))
