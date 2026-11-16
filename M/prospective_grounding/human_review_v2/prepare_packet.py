"""Build the blinded V2 human-review packet from immutable generation records."""
from __future__ import annotations

import json
import os
from pathlib import Path
import secrets

BASE = Path(__file__).resolve().parents[1]
GENERATION_ROOT = BASE / "generated_v2"
OUTPUT_ROOT = BASE / "human_review_v2"
FAMILY_ORDER = ("video_memorability", "image_enhancement")


def _new_id(prefix: str, used: set[str]) -> str:
    while True:
        value = f"{prefix}-{secrets.token_hex(3).upper()}"
        if value not in used:
            used.add(value)
            return value


def _question_only(raw: str) -> str:
    marker = "**Research Question:**"
    rationale = "**Rationale:**"
    if not raw.startswith(marker) or rationale not in raw:
        raise ValueError("generation output must have an explicit question section before its rationale")
    body = raw[len(marker):raw.index(rationale)]
    # Remove only separator newlines, retaining all characters in the question itself.
    return body.strip("\r\n")


def load_successful_v2() -> list[dict]:
    complete_runs = sorted(GENERATION_ROOT.glob("run_*/run_complete.json"))
    if len(complete_runs) != 1:
        raise ValueError("expected exactly one completed V2 run")
    complete = json.loads(complete_runs[0].read_text())
    if complete.get("status") != "COMPLETE_4_OF_4":
        raise ValueError("V2 run is not complete")
    attempt_paths = sorted(complete_runs[0].parent.glob("attempts/*.json"))
    records = [json.loads(path.read_text()) for path in attempt_paths]
    if len(records) != 4 or any(record.get("status") != "SUCCEEDED" for record in records):
        raise ValueError("V2 must contain exactly four successful generation records")
    expected = {(family, kind) for family in FAMILY_ORDER for kind in ("primary", "decoy")}
    actual = [(record.get("family"), record.get("kind")) for record in records]
    if len(set(actual)) != 4 or set(actual) != expected:
        raise ValueError("V2 records do not match the two-family, primary/decoy cohort")
    for record in records:
        if not record.get("question_id") or not record.get("raw_model_output"):
            raise ValueError("successful generation lacks an ID or raw model output")
        if record.get("raw_model_output") != record["ollama_response"]["parsed"].get("response"):
            raise ValueError("raw model output differs from the preserved Ollama response")
        if not record.get("generated_at") or not record.get("model_digest") or not record.get("prompt_sha256"):
            raise ValueError("generation provenance is incomplete")
    return records


def build_packet(records: list[dict]) -> tuple[dict, dict]:
    by_key = {(item["family"], item["kind"]): item for item in records}
    source_by_family = {}
    for family in FAMILY_ORDER:
        primary = by_key[(family, "primary")]
        source_by_family[family] = primary["input_records"]
        for kind in ("primary", "decoy"):
            if [p["paper_id"] for p in by_key[(family, kind)]["input_records"]] != \
                    [p["paper_id"] for p in primary["input_records"]]:
                raise ValueError("primary and decoy input pools differ within a family")

    used_question_ids: set[str] = set()
    used_collection_ids: set[str] = set()
    used_document_ids: set[str] = set()
    blind_question_by_key = {
        key: _new_id("Q", used_question_ids) for key in by_key
    }
    blind_collection_by_family = {
        family: _new_id("C", used_collection_ids) for family in FAMILY_ORDER
    }
    blind_document_by_paper = {}
    private_questions = {}
    questions = []
    for key, record in by_key.items():
        blinded_id = blind_question_by_key[key]
        text = _question_only(record["raw_model_output"])
        questions.append({"question_id": blinded_id, "question_text": text})
        private_questions[blinded_id] = {
            "v2_question_id": record["question_id"], "family": record["family"],
            "generation_kind": record["kind"], "seed": record["seed"],
            "source_paper_ids": list(record["input_ids"]),
        }

    collections = []
    for family in FAMILY_ORDER:
        papers = []
        for source in source_by_family[family]:
            paper_id = source["paper_id"]
            document_id = blind_document_by_paper.setdefault(
                paper_id, _new_id("D", used_document_ids))
            papers.append({"document_id": document_id, "title": source["title"],
                           "abstract": source["abstract"]})
        collections.append({"collection_id": blind_collection_by_family[family], "papers": papers})

    assignments = []
    for family in FAMILY_ORDER:
        own_collection = blind_collection_by_family[family]
        other_family = next(candidate for candidate in FAMILY_ORDER if candidate != family)
        other_collection = blind_collection_by_family[other_family]
        primary_id = blind_question_by_key[(family, "primary")]
        decoy_id = blind_question_by_key[(family, "decoy")]
        assignments.extend([
            {"question_id": primary_id, "collection_id": own_collection},
            {"question_id": primary_id, "collection_id": other_collection},
            {"question_id": decoy_id, "collection_id": own_collection},
        ])
    secrets.SystemRandom().shuffle(questions)
    secrets.SystemRandom().shuffle(collections)
    secrets.SystemRandom().shuffle(assignments)

    collection_by_id = {item["collection_id"]: item for item in collections}
    rating_rows, association_rows = [], []
    for assignment in assignments:
        association_rows.append(dict(assignment))
        for paper in collection_by_id[assignment["collection_id"]]["papers"]:
            rating_rows.append({**assignment, "document_id": paper["document_id"]})
    secrets.SystemRandom().shuffle(rating_rows)

    packet_data = {"questions": questions, "collections": collections,
                   "associations": assignments, "rating_rows": rating_rows,
                   "association_review_rows": association_rows}
    private_map = {"questions": private_questions,
                   "collections": {blind_collection_by_family[family]: {
                       "source_family": family,
                       "paper_ids": [paper["paper_id"] for paper in source_by_family[family]]}
                       for family in FAMILY_ORDER},
                   "documents": {blind_document_by_paper[paper_id]: paper_id
                                 for paper_id in blind_document_by_paper}}
    return packet_data, private_map


def _packet_markdown(packet: dict, reviewer: str) -> str:
    lines = [
        "# Independent input-relevance review — blinded packet",
        "",
        f"Reviewer copy: {reviewer}",
        "",
        "## Instructions",
        "",
        "Complete this review independently. Do not discuss questions or ratings with the other reviewer. "
        "Use only the question text and source papers in this packet; do not look up generation records or scores.",
        "Question IDs and collection IDs are neutral identifiers. Evaluate every assigned question–paper pair "
        "in the blank form. The form also asks uniformly about topic fit and whether the supplied papers "
        "substantively support each question premise. Do not infer expected outcomes from the identifiers or order.",
        "",
        "For each question–paper pair, assign one relevance rating:",
        "",
        "- **0 — Unrelated/no grounding:** the paper is unrelated to the question premise or offers no grounding.",
        "- **1 — Topical, not directly grounding:** the paper is on-topic but does not directly ground the question premise.",
        "- **2 — Directly relevant evidence:** the paper provides directly relevant evidence for the question premise.",
        "",
        "For each assigned question–collection association, independently answer whether it is in the same broad topic area "
        "and whether the supplied collection substantively supports the question premise. Add a short evidence note for "
        "each paper rating and association check. Use the form's reviewer code and UTC date fields; retain your original "
        "ratings and do not adjudicate with the other reviewer.",
        "",
        "## Source collections",
        "",
    ]
    for collection in packet["collections"]:
        lines.extend([f"### Collection {collection['collection_id']}", ""])
        for paper in collection["papers"]:
            lines.extend([f"#### Document {paper['document_id']}", "",
                          f"**Title:** {paper['title']}", "", "**Abstract:**", "",
                          "```text", paper["abstract"], "```", ""])
    lines.extend(["## Questions", ""])
    for question in packet["questions"]:
        lines.extend([f"### {question['question_id']}", "", "```text",
                      question["question_text"], "```", ""])
    lines.extend(["## Assigned question–collection associations", "",
                  "Use these neutral IDs to locate the question and source collection in the sections above.", ""])
    for association in packet["associations"]:
        lines.append(f"- Question {association['question_id']} — Collection {association['collection_id']}")
    lines.append("")
    return "\n".join(lines)


def _blank_form(packet: dict, reviewer: str) -> dict:
    return {
        "reviewer_code": "",
        "review_date_utc": "",
        "independent_review_confirmed": "",
        "paper_ratings": [{**row, "rating_0_1_2": "", "evidence_note": ""}
                          for row in packet["rating_rows"]],
        "association_checks": [{**row, "same_broad_topic": "",
                                 "unsupported_by_supplied_papers": "", "evidence_note": ""}
                               for row in packet["association_review_rows"]],
    }


def _write_exclusive(path: Path, content: str, mode: int = 0o644) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(content)
        stream.flush()
        __import__("os").fsync(stream.fileno())


def prepare() -> Path:
    records = load_successful_v2()
    packet, private_map = build_packet(records)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    allowed_existing = {"prepare_packet.py", "validate_packet.py", "__pycache__"}
    unexpected = {path.name for path in OUTPUT_ROOT.iterdir()} - allowed_existing
    if unexpected:
        raise FileExistsError(f"review materials already exist; refusing overwrite: {sorted(unexpected)}")
    _write_exclusive(OUTPUT_ROOT / "blinded_packet_data.json",
                     json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    _write_exclusive(OUTPUT_ROOT / "private_mapping.json",
                     json.dumps(private_map, ensure_ascii=False, indent=2) + "\n", mode=0o600)
    for reviewer in ("reviewer_1", "reviewer_2"):
        directory = OUTPUT_ROOT / reviewer
        directory.mkdir(exist_ok=False)
        _write_exclusive(directory / "review_packet.md", _packet_markdown(packet, reviewer))
        _write_exclusive(directory / "review_form.json",
                         json.dumps(_blank_form(packet, reviewer), ensure_ascii=False, indent=2) + "\n")
    return OUTPUT_ROOT


if __name__ == "__main__":
    print(prepare())
