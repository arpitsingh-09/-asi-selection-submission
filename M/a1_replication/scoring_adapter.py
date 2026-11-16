#!/usr/bin/env python3
"""Prepare validated A1 inputs for the locked E2 scorer without scoring."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import timedelta
from pathlib import Path
from typing import Any

from M.a1_replication import controls
from M.a1_replication.generate_authorized_manipulations import (
    MANIPULATION_SEED,
    parse_time,
    stable_id,
)


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INPUTS_FILE = HERE / "A1_AUTHORIZED_MANIPULATIONS_V1.json"
VALIDATION_FILE = HERE / "A1_AUTHORIZED_MANIPULATIONS_VALIDATION_V1.json"
MANIFEST_FILE = HERE / "A1_SCORING_INPUT_MANIFEST_V1.json"
EXPECTED_AUTHORIZATION = "42770a2db1d6978c52b8c95e288fa769df7bc10c"
EXPECTED_FOCALS = ("2512.23709v3", "2610.29385v1")
EXPECTED_CONDITIONS = (
    "baseline", "coverage_25", "coverage_50", "coverage_75",
    "coverage_100", "concentrated", "distributed",
)


class ScoringInputError(ValueError):
    pass


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_sha256(value: dict) -> str:
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _bound_input_path(relative: str) -> Path:
    local_path = HERE / relative
    if local_path.is_file():
        return local_path
    e2_path = ROOT / "E2" / "data" / relative
    if e2_path.is_file():
        return e2_path
    root_path = ROOT / relative
    return root_path


def _read_inputs(inputs_path: Path, validation_path: Path) -> tuple[dict, dict]:
    try:
        inputs = json.loads(inputs_path.read_text(encoding="utf-8"))
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScoringInputError(f"Unable to read validated manipulation artifacts: {exc}") from exc

    actual_hash = _file_sha256(inputs_path)
    if validation.get("inputs_file") != inputs_path.name:
        raise ScoringInputError("Validation report does not name this manipulation input file")
    if validation.get("inputs_sha256") != actual_hash:
        raise ScoringInputError("Manipulation input SHA-256 differs from validation report")
    if inputs.get("schema") != "M-A1-authorized-manipulation-inputs-v1":
        raise ScoringInputError("Unexpected manipulation input schema")
    if inputs.get("authorization_commit") != EXPECTED_AUTHORIZATION:
        raise ScoringInputError("Manipulation input is not bound to the approved authorization")
    if inputs.get("authorized_focals") != list(EXPECTED_FOCALS):
        raise ScoringInputError("Authorized focal scope differs from the authorization")
    if validation.get("validation_status") != "passed":
        raise ScoringInputError("Manipulation validation report does not say passed")
    if any((inputs.get("scores_generated"), inputs.get("model_inference_run"),
            inputs.get("bootstrap_run"))):
        raise ScoringInputError("Preparation inputs unexpectedly record scoring or inference")

    for relative, expected in inputs.get("input_sha256", {}).items():
        path = Path(relative) if Path(relative).is_absolute() else _bound_input_path(relative)
        if not path.is_file() or _file_sha256(path) != expected:
            raise ScoringInputError(f"Bound input hash mismatch: {relative}")
    return inputs, validation


def _validate_control(focal_id: str, control: dict, papers: dict[str, dict],
                      focal: dict) -> None:
    if control.get("pair_id") != focal_id or control.get("focal_paper_id") != focal_id:
        raise ScoringInputError(f"Control identity mismatch for {focal_id}")
    condition = control.get("condition")
    if condition == "same_topic_decoy":
        if control.get("status") != "unavailable":
            raise ScoringInputError(f"Decoy is not marked unavailable for {focal_id}")
        if "input_paper_ids" in control or "question" in control:
            raise ScoringInputError(f"Unavailable decoy contains scoreable data for {focal_id}")
        identity = {
            "focal_paper_id": focal_id,
            "condition": condition,
            "status": "unavailable",
            "reason": control.get("reason"),
        }
    elif condition == "empty":
        if control.get("input_paper_ids") != [] or control.get("score_status") != "undefined":
            raise ScoringInputError(f"Empty control must remain undefined for {focal_id}")
        identity = {
            "focal_paper_id": focal_id,
            "condition": condition,
            "question": control.get("question"),
            "input_paper_ids": [],
            "score_status": control["score_status"],
            "score_reason": control.get("score_reason"),
        }
    elif condition in {"original", "shuffled"}:
        ids = control.get("input_paper_ids")
        if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
            raise ScoringInputError(f"{condition} control has invalid pool IDs for {focal_id}")
        if focal_id in ids:
            raise ScoringInputError(f"{condition} control contains its focal paper")
        if condition == "shuffled" and set(ids) == set(focal["original_input_ids"]):
            raise ScoringInputError(f"Shuffled pool is not distinct for {focal_id}")
        for paper_id in ids:
            paper = papers.get(paper_id)
            if paper is None:
                raise ScoringInputError(f"Unknown control source paper: {paper_id}")
            if parse_time(paper.get("published")) >= parse_time(focal["published"]):
                raise ScoringInputError(f"Future-dated control source: {paper_id}")
        identity = {
            "focal_paper_id": focal_id,
            "condition": condition,
            "question": control.get("question"),
            "input_paper_ids": ids,
        }
        if "shuffled_from_focal_paper_id" in control:
            identity["shuffled_from_focal_paper_id"] = control["shuffled_from_focal_paper_id"]
    else:
        raise ScoringInputError(f"Unexpected control condition: {condition}")
    if control.get("record_id") != "a1e2-" + controls._digest(identity):
        raise ScoringInputError(f"Control record ID hash mismatch for {focal_id}/{condition}")


def validate_scoring_inputs(inputs: dict, validation: dict,
                            papers: dict[str, dict]) -> dict:
    """Validate all records and return a manifest; this does not score."""
    if validation.get("inputs_sha256") != _json_sha256(inputs):
        raise ScoringInputError("In-memory manipulation input SHA-256 mismatch")
    focal_records = inputs.get("focals")
    if not isinstance(focal_records, list) or [row.get("paper_id") for row in focal_records] != list(EXPECTED_FOCALS):
        raise ScoringInputError("Focal records do not match the authorized order")
    cases = inputs.get("manipulation_cases")
    synthetic_records = inputs.get("synthetic_papers")
    if not isinstance(cases, list) or len(cases) != 14:
        raise ScoringInputError("Expected exactly 14 authorized manipulation cases")
    if not isinstance(synthetic_records, list) or len(synthetic_records) != 26:
        raise ScoringInputError("Expected exactly 26 versioned synthetic records")

    synthetic_by_id = {row.get("paper_id"): row for row in synthetic_records}
    if None in synthetic_by_id or len(synthetic_by_id) != len(synthetic_records):
        raise ScoringInputError("Synthetic record IDs are missing or duplicated")

    case_ids = set()
    manifest_focals = []
    scoring_targets = []
    focal_by_id = {row["paper_id"]: row for row in focal_records}
    for focal in focal_records:
        focal_id = focal["paper_id"]
        cutoff = parse_time(focal["published"])
        if focal_id not in papers:
            raise ScoringInputError(f"Focal source is absent from E2 source corpus: {focal_id}")
        source_focal = papers[focal_id]
        if source_focal.get("published") != focal["published"]:
            raise ScoringInputError(f"Focal timestamp differs from source corpus: {focal_id}")
        abstract = source_focal.get("abstract") or ""
        if hashlib.sha256(abstract.encode("utf-8")).hexdigest() != focal["abstract_sha256"]:
            raise ScoringInputError(f"Focal abstract differs from source corpus: {focal_id}")
        claims = focal.get("human_approved_claims")
        if not isinstance(claims, list) or not 4 <= len(claims) <= 10:
            raise ScoringInputError(f"Invalid retained claim count for {focal_id}")
        claim_numbers = [row.get("claim_number") for row in claims]
        claim_texts = [row.get("claim") for row in claims]
        if not all(isinstance(text, str) and text.strip() for text in claim_texts):
            raise ScoringInputError(f"Invalid approved claim text for {focal_id}")
        if len(set(claim_numbers)) != len(claim_numbers) or len(set(claim_texts)) != len(claim_texts):
            raise ScoringInputError(f"Duplicate approved claims for {focal_id}")
        if any(not row.get("evidence") or row["evidence"] not in abstract for row in claims):
            raise ScoringInputError(f"Claim/source span mismatch for {focal_id}")

        controls_by_condition = {row.get("condition"): row for row in focal.get("control_records", [])}
        if set(controls_by_condition) != {"original", "empty", "shuffled", "same_topic_decoy"}:
            raise ScoringInputError(f"Unexpected controls for {focal_id}")
        for control in focal["control_records"]:
            _validate_control(focal_id, control, papers, focal)
        if controls_by_condition["original"]["input_paper_ids"] != focal["original_input_ids"]:
            raise ScoringInputError(f"Original control IDs changed for {focal_id}")
        original_ids = focal["original_input_ids"]
        if not original_ids or len(original_ids) != len(set(original_ids)):
            raise ScoringInputError(f"Invalid original pool IDs for {focal_id}")

        focal_cases = [row for row in cases if row.get("focal_paper_id") == focal_id]
        if [row.get("manipulation") for row in focal_cases] != list(EXPECTED_CONDITIONS):
            raise ScoringInputError(f"Condition set or ordering mismatch for {focal_id}")
        if [row.get("case_id") for row in focal_cases] != focal.get("case_ids"):
            raise ScoringInputError(f"Case identities differ from focal manifest for {focal_id}")

        focal_targets = []
        for case in focal_cases:
            case_id = case.get("case_id")
            if not case_id or case_id in case_ids:
                raise ScoringInputError(f"Case ID is missing or duplicated: {case_id}")
            case_ids.add(case_id)
            level = case.get("coverage_percent")
            expected_case_id = stable_id(
                "case-v1", focal["pool"], focal_id,
                case["manipulation"], level or "",
            )
            if case_id != expected_case_id:
                raise ScoringInputError(f"Case ID hash mismatch: {case_id}")
            if case.get("control_record_id") != controls_by_condition["original"]["record_id"]:
                raise ScoringInputError(f"Case is paired with wrong original control: {case_id}")
            if case.get("published") != focal["published"] or case.get("t") != focal["published"]:
                raise ScoringInputError(f"Case cutoff mismatch: {case_id}")
            if case.get("idea_text") != f"{source_focal['title']}\n\n{abstract}":
                raise ScoringInputError(f"Focal text mismatch: {case_id}")
            if case.get("claims") != claim_texts:
                raise ScoringInputError(f"Human-retained claim ordering mismatch: {case_id}")
            expected_source_claims = [
                {"claim_number": row["claim_number"], "claim": row["claim"],
                 "evidence": row["evidence"]}
                for row in claims
            ]
            if case.get("source_claims") != expected_source_claims:
                raise ScoringInputError(f"Human claim/source mapping mismatch: {case_id}")
            if focal_id in case.get("pool_ids", []):
                raise ScoringInputError(f"Focal paper leakage in {case_id}")
            if len(case.get("pool_ids", [])) != len(set(case["pool_ids"])):
                raise ScoringInputError(f"Duplicate pool membership in {case_id}")
            if case.get("scoring_status") != "not_scored":
                raise ScoringInputError(f"Case is not marked unscored: {case_id}")
            synthetic_ids = case.get("metadata", {}).get("synthetic_paper_ids", [])
            if case["pool_ids"] != original_ids + synthetic_ids:
                raise ScoringInputError(f"Pool membership changed for {case_id}")
            condition = case["manipulation"]
            if condition == "baseline":
                selected_claim_numbers, synthetic_abstracts, slots = [], [], []
            elif condition.startswith("coverage_"):
                percent = int(condition.removeprefix("coverage_"))
                if level != percent:
                    raise ScoringInputError(f"Coverage level mismatch: {case_id}")
                count = max(1, math.ceil(len(claims) * percent / 100))
                selected_claim_numbers = claim_numbers[:count]
                synthetic_abstracts = ["\n".join(claim_texts[:count])]
                slots = ["planted"]
            elif condition == "concentrated":
                if level is not None:
                    raise ScoringInputError(f"Unexpected coverage level for {case_id}")
                selected_claim_numbers = claim_numbers
                synthetic_abstracts = ["\n".join(claim_texts)]
                slots = ["all_claims"]
            else:
                if level is not None:
                    raise ScoringInputError(f"Unexpected coverage level for {case_id}")
                selected_claim_numbers = claim_numbers
                synthetic_abstracts = claim_texts
                slots = [f"claim_{index}" for index in range(1, len(claims) + 1)]
            if case.get("metadata", {}).get("selected_claim_numbers") != selected_claim_numbers:
                raise ScoringInputError(f"Claim selection/order mismatch: {case_id}")
            if len(synthetic_ids) != len(synthetic_abstracts):
                raise ScoringInputError(f"Synthetic count mismatch: {case_id}")
            for pool_id in case["pool_ids"]:
                record = synthetic_by_id.get(pool_id) or papers.get(pool_id)
                if record is None:
                    raise ScoringInputError(f"Unknown pool paper ID: {pool_id}")
                if parse_time(record.get("published")) >= cutoff:
                    raise ScoringInputError(f"Future-dated pool paper in {case_id}: {pool_id}")
                if pool_id in synthetic_by_id and pool_id not in synthetic_ids:
                    raise ScoringInputError(f"Synthetic record leaked into an unrelated pool: {case_id}")
            for synthetic_id, slot, expected_abstract in zip(
                synthetic_ids, slots, synthetic_abstracts
            ):
                record = synthetic_by_id.get(synthetic_id)
                if record is None:
                    raise ScoringInputError(f"Case references unknown synthetic paper: {synthetic_id}")
                expected_synthetic_id = stable_id(
                    MANIPULATION_SEED, focal["pool"], focal_id, condition, slot
                )
                if synthetic_id != expected_synthetic_id:
                    raise ScoringInputError(f"Synthetic paper ID mismatch: {synthetic_id}")
                if (
                    record.get("pool") != focal["pool"]
                    or not record.get("synthetic_manipulation")
                    or record.get("synthetic_condition") != condition
                    or record.get("synthetic_seed") != MANIPULATION_SEED
                    or record.get("abstract") != expected_abstract
                    or record.get("updated") != record.get("published")
                ):
                    raise ScoringInputError(f"Synthetic metadata mismatch: {synthetic_id}")
                if parse_time(record["published"]) != cutoff - timedelta(seconds=1):
                    raise ScoringInputError(f"Synthetic timestamp mismatch: {synthetic_id}")
            target = {
                "target_id": case_id,
                "focal_paper_id": focal_id,
                "kind": "manipulation",
                "condition": case["manipulation"],
                "question": case["idea_text"],
                "claims": claim_texts,
                "pool_ids": case["pool_ids"],
                "cutoff": case["t"],
            }
            focal_targets.append(target)
            scoring_targets.append(target)

        shuffled = controls_by_condition["shuffled"]
        shuffled_from = shuffled.get("shuffled_from_focal_paper_id")
        if shuffled_from not in focal_by_id or shuffled_from == focal_id:
            raise ScoringInputError(f"Shuffled control source identity is invalid for {focal_id}")
        source_pool = focal_by_id[shuffled_from]["original_input_ids"]
        expected_shuffle_ids = [
            source_id for source_id in source_pool
            if source_id != focal_id
            and parse_time(papers[source_id]["published"]) < cutoff
        ]
        if shuffled["input_paper_ids"] != expected_shuffle_ids:
            raise ScoringInputError(f"Shuffled pool membership differs from source focal for {focal_id}")
        scoring_targets.append({
            "target_id": shuffled["record_id"],
            "focal_paper_id": focal_id,
            "kind": "control",
            "condition": "shuffled",
            "question": shuffled["question"],
            "claims": claim_texts,
            "pool_ids": shuffled["input_paper_ids"],
            "cutoff": focal["published"],
        })
        manifest_focals.append({
            "paper_id": focal_id,
            "claim_count": len(claims),
            "claim_numbers": claim_numbers,
            "original_control_record_id": controls_by_condition["original"]["record_id"],
            "empty_control_record_id": controls_by_condition["empty"]["record_id"],
            "empty_control_status": "undefined",
            "shuffled_control_record_id": shuffled["record_id"],
            "shuffled_input_ids": shuffled["input_paper_ids"],
            "decoy_control_record_id": controls_by_condition["same_topic_decoy"]["record_id"],
            "decoy_status": "unavailable",
            "case_ids": [target["target_id"] for target in focal_targets],
        })

    all_used_synthetic = {
        synthetic_id
        for case in cases
        for synthetic_id in case.get("metadata", {}).get("synthetic_paper_ids", [])
    }
    if all_used_synthetic != set(synthetic_by_id):
        raise ScoringInputError("Synthetic records do not exactly match case memberships")
    return {
        "schema": "M-A1-scoring-input-manifest-v1",
        "authorization_commit": inputs["authorization_commit"],
        "manipulation_inputs_sha256": validation["inputs_sha256"],
        "validation_report_sha256": _file_sha256(VALIDATION_FILE),
        "e2_novelty_sha256": controls.E2_NOVELTY_SHA256,
        "scoring_adapter_sha256": _file_sha256(Path(__file__).resolve()),
        "control_adapter_sha256": _file_sha256(HERE / "controls.py"),
        "scoring_method": "E2.novelty.score; unchanged implementation; not executed during preparation",
        "focal_records": manifest_focals,
        "manipulation_case_count": len(cases),
        "shuffled_control_score_target_count": len(manifest_focals),
        "empty_controls": "undefined; excluded from numeric scoring",
        "same_topic_decoys": "unavailable; never scored",
        "scoring_targets": scoring_targets,
        "validated": True,
        "scores_generated": False,
        "model_inference_run": False,
        "bootstrap_run": False,
    }


def install_synthetic_overlay(novelty_module: Any, inputs: dict,
                              manifest: dict) -> dict[str, dict]:
    """Add versioned synthetic papers to an in-memory E2 corpus copy only."""
    if getattr(novelty_module, "_MODEL", None) is not None:
        raise ScoringInputError("E2 model is already initialized; refusing late input installation")
    base_papers = novelty_module._load_papers()
    merged = dict(base_papers)
    for paper in inputs["synthetic_papers"]:
        paper_id = paper["paper_id"]
        if paper_id in merged:
            raise ScoringInputError(f"Synthetic ID collides with E2 corpus: {paper_id}")
        merged[paper_id] = paper
    expected_pool_ids = {
        paper_id
        for target in manifest["scoring_targets"]
        for paper_id in target["pool_ids"]
    }
    missing = expected_pool_ids - set(merged)
    if missing:
        raise ScoringInputError(f"Scoring inputs are absent from E2 overlay: {sorted(missing)[:5]}")
    novelty_module._PAPERS = merged
    if novelty_module._PAPERS is base_papers:
        raise ScoringInputError("E2 in-memory source corpus was mutated instead of copied")
    if novelty_module._MODEL is not None:
        raise ScoringInputError("Model inference unexpectedly initialized during preparation")
    return merged


def prepare_scoring_inputs(*, novelty_module: Any,
                           inputs_path: Path = INPUTS_FILE,
                           validation_path: Path = VALIDATION_FILE) -> dict:
    inputs, validation = _read_inputs(inputs_path, validation_path)
    novelty_path = ROOT / "E2" / "novelty.py"
    if _file_sha256(novelty_path) != controls.E2_NOVELTY_SHA256:
        raise ScoringInputError("E2 novelty implementation does not match registered SHA-256")
    if (
        novelty_module.MODEL_ID != "specter2_base+proximity-adapter+cls-v1"
        or novelty_module.MAX_LENGTH != 512
        or novelty_module.RND_P != 100
        or novelty_module.RND_Q != 50
        or novelty_module.Y_WEIGHT != 0.75
        or novelty_module.N_WEIGHT != 0.25
    ):
        raise ScoringInputError("Imported E2 novelty configuration differs from registration")
    if getattr(novelty_module, "_MODEL", None) is not None:
        raise ScoringInputError("E2 model was initialized before scoring inputs were prepared")
    papers = novelty_module._load_papers()
    manifest = validate_scoring_inputs(inputs, validation, papers)
    install_synthetic_overlay(novelty_module, inputs, manifest)
    return manifest


def score_target(target: dict) -> dict:
    """Score one prepared nonempty target through the locked E2 adapter.

    This function is intentionally not called by the preparation command.
    """
    if target.get("condition") in {"same_topic_decoy", "empty"}:
        raise ScoringInputError(f"{target.get('condition')} is not a numeric scoring target")
    condition = {
        "condition": target["condition"],
        "question": target["question"],
        "input_paper_ids": target["pool_ids"],
    }
    return controls.score_with_e2(
        condition,
        claims=target["claims"],
        cutoff=target["cutoff"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepare-only", action="store_true",
        help="validate and install in-memory inputs, save manifest, and exit without scoring",
    )
    args = parser.parse_args()
    if not args.prepare_only:
        parser.error("Only --prepare-only is implemented; scoring is intentionally disabled.")
    if MANIFEST_FILE.exists():
        raise SystemExit(f"Refusing to overwrite existing manifest: {MANIFEST_FILE}")

    # Importing the module does not initialize its tokenizer or model.
    from E2 import novelty

    manifest = prepare_scoring_inputs(novelty_module=novelty)
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Validated {manifest['manipulation_case_count']} cases.")
    print(f"Saved scoring-input manifest: {MANIFEST_FILE}")
    print("No model inference, scoring, or bootstrap analysis was run.")


if __name__ == "__main__":
    main()
