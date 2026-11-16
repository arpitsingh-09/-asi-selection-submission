"""Offline integrity checks for blinded V2 reviewer materials."""
from __future__ import annotations

import json
import re
from pathlib import Path

from M.prospective_grounding.human_review_v2.prepare_packet import (
    OUTPUT_ROOT,
    _question_only,
    load_successful_v2,
)


def validate(root: Path = OUTPUT_ROOT) -> None:
    if not root.is_dir():
        raise ValueError("review packet directory is missing")
    packet = json.loads((root / "blinded_packet_data.json").read_text())
    private = json.loads((root / "private_mapping.json").read_text())
    generated = load_successful_v2()
    questions = packet["questions"]
    if len(questions) != 4 or len({q["question_id"] for q in questions}) != 4:
        raise ValueError("packet must contain all four questions exactly once")
    if any(not re.fullmatch(r"Q-[A-F0-9]{6}", q["question_id"]) for q in questions):
        raise ValueError("question identifiers are not neutral randomized IDs")
    expected_texts = {
        item["question_id"]: _question_only(item["raw_model_output"])
        for item in generated
    }
    mapping = private["questions"]
    if set(mapping) != {question["question_id"] for question in questions}:
        raise ValueError("private mapping does not cover all blinded questions")
    reverse = {entry["v2_question_id"]: blind_id for blind_id, entry in mapping.items()}
    if len(reverse) != 4:
        raise ValueError("private question mapping is not one-to-one")
    for question in questions:
        original_id = mapping[question["question_id"]]["v2_question_id"]
        if question["question_text"] != expected_texts[original_id]:
            raise ValueError("review question text differs from the exact generated question section")

    if len(packet["collections"]) != 2 or any(len(c["papers"]) != 3 for c in packet["collections"]):
        raise ValueError("packet must include two collections with three source papers each")
    if len(packet["associations"]) != 6 or len(packet["rating_rows"]) != 18:
        raise ValueError("review assignments do not match the registered non-empty pairs")
    if len(packet["association_review_rows"]) != 6:
        raise ValueError("topic/unsupported checks must cover every blinded association")
    if any("condition" in row or "kind" in row for row in packet["associations"]):
        raise ValueError("condition labels leaked into blinded assignments")

    generated_by_key = {(item["family"], item["kind"]): item for item in generated}
    family_by_collection = {key: value["source_family"] for key, value in private["collections"].items()}
    collection_by_family = {family: collection for collection, family in family_by_collection.items()}
    for collection in packet["collections"]:
        family = family_by_collection[collection["collection_id"]]
        expected_papers = generated_by_key[(family, "primary")]["input_records"]
        shown = [(paper["title"], paper["abstract"]) for paper in collection["papers"]]
        expected = [(paper["title"], paper["abstract"]) for paper in expected_papers]
        if shown != expected:
            raise ValueError("source-paper title or abstract differs from the exact generated source record")

    question_blind_by_original = {value["v2_question_id"]: blind for blind, value in mapping.items()}
    expected_associations = set()
    for (family, kind), generated_record in generated_by_key.items():
        blind_id = question_blind_by_original[generated_record["question_id"]]
        expected_associations.add((blind_id, collection_by_family[family]))
        if kind == "primary":
            other = next(f for f in ("video_memorability", "image_enhancement") if f != family)
            expected_associations.add((blind_id, collection_by_family[other]))
    actual_associations = {(row["question_id"], row["collection_id"]) for row in packet["associations"]}
    if actual_associations != expected_associations:
        raise ValueError("question-to-paper-pool assignments differ from registered non-empty conditions")

    original_question_ids = {item["question_id"] for item in generated}
    original_paper_ids = {paper_id for item in generated for paper_id in item["input_ids"]}
    forbidden_mapping_text = original_question_ids | original_paper_ids
    if set(private["questions"]) & original_question_ids:
        raise ValueError("private mapping uses unblinded question IDs as blinded IDs")

    reviewer_files = []
    for reviewer in ("reviewer_1", "reviewer_2"):
        directory = root / reviewer
        packet_path, form_path = directory / "review_packet.md", directory / "review_form.json"
        if not packet_path.is_file() or not form_path.is_file():
            raise ValueError(f"missing review materials for {reviewer}")
        reviewer_files.extend((packet_path, form_path))
        packet_text = packet_path.read_text()
        form = json.loads(form_path.read_text())
        if sum(packet_text.count(question["question_text"]) for question in questions) != 4:
            raise ValueError("review packet does not contain each exact question once")
        for question in questions:
            if packet_text.count(question["question_text"]) != 1:
                raise ValueError("question is missing or duplicated in reviewer packet")
        if "**Rationale:**" in packet_text or "model_digest" in packet_text or "question_kind" in packet_text:
            raise ValueError("model rationale or generation labels leaked into reviewer packet")
        if re.search(r"(?im)^\s*(primary|decoy)(?:\s+question)?\s*[:#]", packet_text):
            raise ValueError("primary/decoy label leaked into reviewer packet")
        if any(score in packet_text for score in ("G =", "B-TF =", "model_score", "model scores")):
            raise ValueError("model score leaked into reviewer packet")
        if set(form) != {"reviewer_code", "review_date_utc", "independent_review_confirmed",
                         "paper_ratings", "association_checks"}:
            raise ValueError("review form contains unexpected fields")
        form_text = json.dumps(form, ensure_ascii=False)
        if any(token in form_text for token in ("primary", "decoy", "condition", "G", "B-TF", "model_score")):
            raise ValueError("review form includes unblinded labels, conditions, or score fields")
        if any(form[key] != "" for key in ("reviewer_code", "review_date_utc", "independent_review_confirmed")):
            raise ValueError("reviewer identity/date/independence fields are not blank")
        if len(form["paper_ratings"]) != 18 or len(form["association_checks"]) != 6:
            raise ValueError("review form has an incorrect number of blank response rows")
        if any(row["rating_0_1_2"] != "" or row["evidence_note"] != "" for row in form["paper_ratings"]):
            raise ValueError("paper-rating form is not initially blank")
        if any(row["same_broad_topic"] != "" or row["unsupported_by_supplied_papers"] != "" or
               row["evidence_note"] != "" for row in form["association_checks"]):
            raise ValueError("association-check form is not initially blank")

    rationale_segments = []
    for item in generated:
        raw = item["raw_model_output"]
        rationale_segments.append(raw[raw.index("**Rationale:**"):])
    for path in reviewer_files:
        content = path.read_text()
        if any(value in content for value in forbidden_mapping_text):
            raise ValueError("unblinded question or source ID leaked into reviewer materials")
        if any(rationale.strip() in content for rationale in rationale_segments):
            raise ValueError("model-generated rationale leaked into reviewer materials")

    if (root / "private_mapping.json").stat().st_mode & 0o077:
        raise ValueError("private mapping file permissions are too broad")


if __name__ == "__main__":
    validate()
    print("V2 human-review packet validation passed")
