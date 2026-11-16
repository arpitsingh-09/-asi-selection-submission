"""Fail-closed helpers for the prospective grounding pilot.

Nothing in this module runs unless a caller explicitly invokes score_conditions;
that function requires all provenance, review, registration, and authorization
gates to pass first.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from M.baselines import tfidf
from M.readouts import groundedness, cosine
from M.prospective_a1.workflow import validate_inputs

GENERATOR_MODEL_ID = "qwen3:8b"
GENERATOR_MODEL_DIGEST = "sha256:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41"
GENERATOR_PARAMETERS = {"temperature": 0.7, "top_p": 0.8, "num_predict": 512}
PRIMARY_SEEDS = {"primary-video_memorability": 4900, "primary-image_enhancement": 4910}
SOURCE_MANIFEST_SHA256 = "02c7600331b197ff8c99e75c1f1d90b54a74c29833e0191f240ed1b151c7830c"
DATASET_SHA256 = "98036e1d99139a7fa4938362ab45f97fc12f21a91182c0ce5d22ee5be7d0c662"


def _time(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be ISO-8601 text")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid ISO-8601 timestamp") from exc
    if result.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return result.astimezone(timezone.utc)


def _valid_hash(value: str) -> bool:
    if isinstance(value, str) and value.startswith("sha256:"):
        value = value[7:]
    return (isinstance(value, str) and len(value) == 64 and
            all(ch in "0123456789abcdef" for ch in value.lower()))


def _validate_control_pools(questions: list[dict], decoys: list[dict], conditions: list[dict]) -> None:
    """Require each labeled condition to use its preregistered family pool."""
    primary_by_id = {item["question_id"]: item for item in questions}
    decoy_by_id = {item["question_id"]: item for item in decoys}
    rows = {(row["question_id"], row["condition"]): row for row in conditions}
    for qid, primary in primary_by_id.items():
        original = rows[(qid, "original")]
        empty = rows[(qid, "empty")]
        shuffled = rows[(qid, "shuffled")]
        decoy = rows[(qid, "same_topic_decoy")]
        if original["paper_ids"] != primary["R"]:
            raise ValueError("original condition must use exactly the primary supplied papers")
        if empty["paper_ids"]:
            raise ValueError("empty control must have no input papers")
        if decoy["paper_ids"] != primary["R"]:
            raise ValueError("decoy condition must use exactly the primary supplied papers")
        decoy_id = decoy.get("source_question_id")
        if decoy_id not in decoy_by_id:
            raise ValueError("same-topic condition is not bound to its generated decoy question")
        other_ids = set(primary_by_id) - {qid}
        if len(other_ids) != 1 or shuffled["paper_ids"] != primary_by_id[other_ids.pop()]["R"]:
            raise ValueError("shuffled condition must use exactly the other family’s supplied papers")
        if decoy_by_id[decoy_id]["R"] != primary["R"]:
            raise ValueError("decoy question must be bound to its family’s original paper pool")


def validate_question(record: dict) -> None:
    """Require the real generation record and its exact supplied source set."""
    for key in ("question_id", "question", "generated_at", "model_id", "model_digest", "prompt_sha256",
                "parameters", "seed", "R", "input_records"):
        if key not in record or record[key] is None:
            raise ValueError(f"question record missing {key}")
    if not record["question"].strip() or not _valid_hash(record["prompt_sha256"]):
        raise ValueError("question text or prompt hash is invalid")
    if record.get("question_kind") not in ("prospectively_generated", "prospectively_generated_decoy"):
        raise ValueError("only prospectively timestamped questions are allowed")
    if not _valid_hash(record["model_digest"]):
        raise ValueError("exact generator model digest is required")
    generated = _time(record["generated_at"])
    inputs = record["input_records"]
    ids = [p.get("paper_id") for p in inputs]
    if len(ids) < 3 or len(set(ids)) != len(ids) or set(ids) != set(record["R"]):
        raise ValueError("R must exactly match at least three distinct supplied papers")
    for paper in inputs:
        for key in ("published_at", "available_at", "source_url", "source_locator", "source_sha256"):
            if not paper.get(key):
                raise ValueError(f"input paper missing {key}")
        if not _valid_hash(paper["source_sha256"]):
            raise ValueError("input source hash is invalid")
        if _time(paper["published_at"]) >= generated or _time(paper["available_at"]) >= generated:
            raise ValueError("input must be published and available before question generation")


def prepare_decoy_request(*, papers: list[dict], model_id: str, model_digest: str,
                          parameters: dict, seed: int) -> dict:
    """Prepare (but do not call) a source-bound same-topic decoy request."""
    if not model_id or not _valid_hash(model_digest) or not isinstance(parameters, dict) or type(seed) is not int:
        raise ValueError("locked model, parameters, and integer seed are required")
    if len(papers) < 3 or any(not p.get("paper_id") or not p.get("text") for p in papers):
        raise ValueError("decoy request needs at least three identified source papers")
    body = "\n\n".join(f"[{p['paper_id']}] {p['text']}" for p in papers)
    prompt = ("Using only the explicitly supplied research papers below, propose one specific, "
              "answerable research question in the same broad topic area, but about a distinct "
              "issue that these papers do not substantively address. Do not invent historical "
              "provenance or claim the question was previously asked.\n\n" + body)
    records = [{key: p.get(key) for key in ("paper_id", "published_at", "available_at", "source_url",
                                               "source_locator", "source_sha256")} for p in papers]
    return {"status": "PREPARED_NOT_GENERATED", "model_id": model_id, "model_digest": model_digest, "parameters": parameters,
            "seed": seed, "prompt": prompt,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "input_records": records,
            "R": [p["paper_id"] for p in papers]}


def generate_decoy_record(*, papers: list[dict], model_id: str, model_digest: str,
                           parameters: dict, seed: int, generator) -> dict:
    """Explicitly injectable generation adapter; never invoked during preparation."""
    request = prepare_decoy_request(papers=papers, model_id=model_id, model_digest=model_digest,
                                    parameters=parameters, seed=seed)
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    validate_inputs(papers, generated_at)
    question = generator(prompt=request["prompt"], model_id=model_id, parameters=parameters, seed=seed)
    if not isinstance(question, str) or not question.strip():
        raise ValueError("generator returned no decoy question")
    return {"question_id": f"decoy-{hashlib.sha256((question + generated_at).encode()).hexdigest()[:16]}",
            "question": question.strip(), "question_kind": "prospectively_generated_decoy",
            "generated_at": generated_at, "model_id": model_id, "model_digest": model_digest, "parameters": parameters,
            "seed": seed, "prompt": request["prompt"], "prompt_sha256": request["prompt_sha256"],
            "input_records": papers, "R": request["R"]}


def build_conditions(primary: dict, shuffled_source: dict, decoy: dict,
                     same_topic_reviews: list[dict]) -> dict:
    """Specify paired conditions; reviewers must certify the decoy relation."""
    for item in (primary, shuffled_source, decoy):
        validate_question(item)
    if primary["question_id"] == shuffled_source["question_id"]:
        raise ValueError("shuffled source must be a different question family")
    if set(primary["R"]) == set(shuffled_source["R"]):
        raise ValueError("shuffled condition must use a different supplied input set")
    primary_time = _time(primary["generated_at"])
    source_by_id = {p["paper_id"]: p for p in shuffled_source["input_records"]}
    if any(_time(source_by_id[pid]["published_at"]) >= primary_time or
           _time(source_by_id[pid]["available_at"]) >= primary_time
           for pid in shuffled_source["R"]):
        raise ValueError("shuffled papers must predate and be available at primary generation")
    if set(decoy["R"]) != set(primary["R"]):
        raise ValueError("same-topic decoy question must be paired with the primary supplied pool")
    valid_reviews = [r for r in same_topic_reviews
                     if r.get("decision") == "verified_same_topic_decoy"
                     and r.get("question_id") == primary["question_id"]
                     and r.get("decoy_question_id") == decoy["question_id"]
                     and r.get("evidence_ref") and r.get("reviewed_at")
                     and r.get("reviewer_id")]
    for review in valid_reviews:
        _time(review["reviewed_at"])
    reviewer_ids = {r["reviewer_id"] for r in valid_reviews}
    if len(reviewer_ids) < 2:
        raise ValueError("two independent dated reviews must verify the same-topic decoy")
    return {
        "original": {"question_id": primary["question_id"], "source_question_id": primary["question_id"],
                     "question": primary["question"], "R": list(primary["R"]), "as_of": primary["generated_at"]},
        "empty": {"question_id": primary["question_id"], "source_question_id": primary["question_id"],
                  "question": primary["question"], "R": [], "as_of": primary["generated_at"]},
        "shuffled": {"question_id": primary["question_id"], "source_question_id": primary["question_id"],
                     "question": primary["question"], "R": list(shuffled_source["R"]), "as_of": primary["generated_at"]},
        "same_topic_decoy": {"question_id": primary["question_id"], "source_question_id": decoy["question_id"],
                             "question": decoy["question"], "R": list(primary["R"]), "as_of": decoy["generated_at"],
                             "reviewers": sorted(reviewer_ids), "review_evidence": valid_reviews},
    }


def validate_readiness(record: dict) -> None:
    """Block scoring until the predeclared evidence and execution gates pass."""
    questions = record.get("question_records", [])
    if len(questions) < 2:
        raise ValueError("at least two independent question families are required")
    decoys = record.get("decoy_records", [])
    if len(decoys) != len(questions):
        raise ValueError("one prospectively generated decoy is required per question family")
    for question in questions + decoys:
        validate_question(question)
    if (any(q.get("question_kind") != "prospectively_generated" for q in questions) or
            any(q.get("question_kind") != "prospectively_generated_decoy" for q in decoys)):
        raise ValueError("primary and decoy generation records are mislabeled")
    if (record.get("generator_model_id") != GENERATOR_MODEL_ID or
            record.get("generator_model_digest") != GENERATOR_MODEL_DIGEST or
            record.get("generator_parameters") != GENERATOR_PARAMETERS):
        raise ValueError("prospective question generator lock is missing")
    if any(q["model_id"] != record["generator_model_id"] or
           q["model_digest"] != record["generator_model_digest"] or
           q["parameters"] != record["generator_parameters"] for q in questions + decoys):
        raise ValueError("generated records differ from the locked model/settings")
    root = Path(__file__).resolve().parents[1]
    def file_hash(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    if (record.get("source_manifest_sha256") != SOURCE_MANIFEST_SHA256 or
            file_hash(root / "prospective_a1/source_manifest.json") != SOURCE_MANIFEST_SHA256):
        raise ValueError("source manifest differs from the locked manifest")
    corpus = root.parent / "E2/data/raw_papers.jsonl"
    if record.get("dataset_sha256") != DATASET_SHA256 or file_hash(corpus) != DATASET_SHA256:
        raise ValueError("source corpus differs from the preregistered read-only dataset")
    if record.get("encoder_id") != "e5-fixed-nonnegative-word-bigram-hash-512-v1":
        raise ValueError("unexpected or unlocked question encoder")
    if (record.get("encoder_code_sha256") != file_hash(root / "encoders.py") or
            record.get("engine_code_sha256") != file_hash(root / "engine.py") or
            record.get("readout_code_sha256") != file_hash(root / "readouts.py")):
        raise ValueError("encoder/readout code locks are missing")
    if record.get("baseline_code_sha256") != file_hash(root / "baselines.py"):
        raise ValueError("B-TF baseline code lock is missing")
    conditions = record.get("condition_rows", [])
    required_conditions = {"original", "empty", "shuffled", "same_topic_decoy"}
    by_question = {}; condition_keys = set()
    for condition in conditions:
        qid, name = condition.get("question_id"), condition.get("condition")
        key = (qid, name)
        if not qid or name not in required_conditions or key in condition_keys:
            raise ValueError("condition row has a missing or duplicate ID")
        condition_keys.add(key)
        if not isinstance(condition.get("paper_ids"), list) or len(set(condition["paper_ids"])) != len(condition["paper_ids"]):
            raise ValueError("condition row has invalid input IDs")
        if name == "empty" and condition["paper_ids"]:
            raise ValueError("empty control must have no input papers")
        if name != "empty" and len(condition["paper_ids"]) < 3:
            raise ValueError("non-empty condition requires at least three inputs")
        by_question.setdefault(qid, set()).add(name)
    if (set(by_question) != {q["question_id"] for q in questions} or len(by_question) < 2 or
            any(value != required_conditions for value in by_question.values())):
        raise ValueError("all four paired conditions are required for every question family")
    if set(by_question) != set(PRIMARY_SEEDS):
        raise ValueError("primary question cohort differs from the frozen two-family pilot")
    decoy_by_id = {item["question_id"]: item for item in decoys}
    for row in conditions:
        if row["condition"] == "same_topic_decoy" and row.get("source_question_id") not in decoy_by_id:
            raise ValueError("same-topic condition is not bound to its generated decoy question")
    primary_by_id = {item["question_id"]: item for item in questions}
    _validate_control_pools(questions, decoys, conditions)
    for qid, seed in PRIMARY_SEEDS.items():
        if primary_by_id[qid]["seed"] != seed:
            raise ValueError("primary generation seed differs from preregistration")
        decoy_id = next(row["source_question_id"] for row in conditions
                        if row["question_id"] == qid and row["condition"] == "same_topic_decoy")
        if decoy_by_id[decoy_id]["seed"] != seed + 1:
            raise ValueError("decoy generation seed differs from preregistration")
    judgments = record.get("human_judgments", [])
    grouped = {}
    for item in judgments:
        if (item.get("condition") == "empty" or type(item.get("score")) is not int or item.get("score") not in (0, 1, 2) or
                not item.get("reviewer_id") or not item.get("evidence_ref")):
            raise ValueError("invalid independent grounding judgment")
        _time(item.get("reviewed_at"))
        key = (item.get("question_id"), item.get("condition"), item.get("paper_id"))
        grouped.setdefault(key, set()).add(item["reviewer_id"])
    required_pairs = {(c["question_id"], c["condition"], pid)
                      for c in conditions if c["condition"] != "empty" for pid in c.get("paper_ids", [])}
    if not required_pairs or any(len(grouped.get(key, set())) < 2 for key in required_pairs):
        raise ValueError("two independent dated judgments are required for every non-empty question-paper pair")
    decoy_reviews = record.get("same_topic_decoy_reviews", [])
    for qid in by_question:
        expected_decoy = next(row["source_question_id"] for row in conditions
                              if row["question_id"] == qid and row["condition"] == "same_topic_decoy")
        reviews = [r for r in decoy_reviews if r.get("question_id") == qid
                   and r.get("decoy_question_id") == expected_decoy
                   and r.get("decision") == "verified_same_topic_decoy"
                   and r.get("reviewer_id") and r.get("evidence_ref") and r.get("reviewed_at")]
        for review in reviews:
            _time(review["reviewed_at"])
        if len({r["reviewer_id"] for r in reviews}) < 2:
            raise ValueError("two independent same-topic decoy reviews are required per family")
    commit = record.get("prereg_commit")
    if (not isinstance(commit, str) or len(commit) != 40 or
            any(ch not in "0123456789abcdef" for ch in commit.lower())):
        raise ValueError("prospective preregistration is not committed")
    for rel in ("prospective_grounding/PREREG_DRAFT.md", "prospective_grounding/workflow.py"):
        try:
            frozen = subprocess.run(["git", "show", f"{commit}:M/{rel}"], cwd=root.parent,
                                    check=True, capture_output=True).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError("registration commit does not contain the required grounding files") from exc
        if frozen != (root / rel).read_bytes():
            raise ValueError("working registration/code differs from the committed version")
    if not record.get("execution_authorization_ref"):
        raise ValueError("explicit execution authorization is missing")


def score_conditions(space, conditions: list[dict], readiness_record: dict) -> list[dict]:
    """Score only after gates pass, reusing M's Phi grounding and B-TF code."""
    validate_readiness(readiness_record)
    if (space.encoder.space_id != readiness_record["encoder_id"] or
            space.max_literature != 128 or space.retrieval_k != 3):
        raise ValueError("ResearchSpace encoder or frozen configuration mismatch")
    registered = {(c.get("question_id"), c.get("condition"), tuple(sorted(c.get("paper_ids", []))))
                  for c in readiness_record["condition_rows"]}
    if len(conditions) != len(registered):
        raise ValueError("scoring conditions contain duplicate or missing rows")
    supplied = {(c.get("question_id"), c.get("condition"), tuple(sorted(c.get("R", []))))
                for c in conditions}
    if supplied != registered:
        raise ValueError("scoring conditions do not match the reviewed, registered condition rows")
    results = []
    for condition in conditions:
        phi = space.encode(condition["question"], condition["R"], condition["as_of"])
        g = groundedness(phi)
        base = tfidf(phi.q, phi.tfidf_training_documents)
        baseline_scores = []
        if base.get("available"):
            for paper in phi.inputs:
                candidate = tfidf(paper.paper.text, phi.tfidf_training_documents)
                baseline_scores.append(cosine(base["vector"], candidate["vector"]))
        baseline = float(np.mean([max(0.0, x) for x in baseline_scores])) if baseline_scores else None
        results.append({"snapshot_id": phi.snapshot_id, "as_of": phi.as_of, "space_id": phi.space_id,
                        "feature_schema": phi.feature_schema,
                        "question_id": condition["question_id"], "source_question_id": condition.get("source_question_id"),
                        "condition": condition["condition"],
                        "input_ids": [p.paper.paper_id for p in phi.inputs],
                        "G": g["score"], "G_status": "undefined_empty_pool" if not phi.inputs else "scored",
                        "B-TF": baseline, "B-TF_status": "undefined_empty_pool" if not phi.inputs else
                        ("scored" if baseline is not None else "unavailable_no_frozen_training_text"),
                        "scope": g["scope"]})
    return results


def paired_cluster_bootstrap(rows: list[dict], draws: int = 2000, seed: int = 20261113) -> dict:
    """CI for B-TF MAE minus G MAE, resampling question families as clusters."""
    if draws < 1000 or not rows:
        raise ValueError("at least 1000 draws and nonempty paired data are required")
    groups = {}
    for row in rows:
        if row.get("condition") == "empty":
            continue
        unit = row.get("question_id")
        human, g, baseline = row.get("human_score"), row.get("G"), row.get("B-TF")
        if not unit or any(not isinstance(x, (int, float)) or not np.isfinite(x) for x in (human, g, baseline)):
            raise ValueError("paired finite human, G and B-TF scores are required")
        if not 0 <= human <= 2 or not 0 <= g <= 1 or not 0 <= baseline <= 1:
            raise ValueError("human/G/B-TF score outside registered scale")
        groups.setdefault(unit, []).append((human / 2.0, g, baseline))
    if len(groups) < 2:
        raise ValueError("at least two independent question clusters are required")

    def estimate(sample):
        values = [item for unit in sample for item in groups[unit]]
        return float(np.mean([abs(y - b) - abs(y - g) for y, g, b in values]))

    ids = sorted(groups)
    point = estimate(ids)
    rng = np.random.default_rng(seed)
    draws_out = [estimate([ids[i] for i in rng.integers(0, len(ids), len(ids))]) for _ in range(draws)]
    return {"metric": "B-TF MAE minus G MAE (positive favors G)", "estimate": point,
            "ci95_percentile": [float(x) for x in np.percentile(draws_out, [2.5, 97.5])],
            "clusters": len(ids), "draws": draws, "seed": seed,
            "warning": "Two-cluster pilot; interval is descriptive and has very low resolution."}
