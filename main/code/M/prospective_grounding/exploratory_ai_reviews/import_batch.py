"""Import one exact JSON batch of 18 external-AI assessments without inference."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import sys
import tempfile

from M.prospective_grounding.exploratory_ai_reviews.validate_import import (
    FIELDS,
    FIXED,
    TEMPLATE_PATH,
    expected_pairs,
    validate,
)

OUTPUT_PATH = TEMPLATE_PATH.with_name("assessments_imported.csv")
INPUT_FIELDS = {"question_id", "paper_id", "rating", "evidence_text"}


def import_batch(payload: object, *, output_path: Path = OUTPUT_PATH) -> dict:
    if not isinstance(payload, list) or len(payload) != 18:
        raise ValueError("input must be one JSON array containing exactly 18 assessment objects")
    expected = expected_pairs()
    seen = set()
    rows = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict) or set(item) != INPUT_FIELDS:
            raise ValueError(f"item {index} must contain exactly question_id, paper_id, rating, evidence_text")
        question_id, paper_id = item["question_id"], item["paper_id"]
        if not isinstance(question_id, str) or not isinstance(paper_id, str):
            raise ValueError(f"item {index} question_id and paper_id must be exact strings")
        pair = (question_id, paper_id)
        if pair not in expected:
            raise ValueError(f"item {index} contains an unknown question–paper pair: {pair}")
        if pair in seen:
            raise ValueError(f"item {index} duplicates question–paper pair: {pair}")
        seen.add(pair)
        rating, evidence = item["rating"], item["evidence_text"]
        if type(rating) is not int or rating not in (0, 1, 2):
            raise ValueError(f"item {index} rating must be integer 0, 1, or 2")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError(f"item {index} evidence_text must be a nonempty string")
        rows.append({
            "question_id": question_id,
            "paper_id": paper_id,
            "rating": str(rating),
            "evidence_text": evidence,
            **FIXED,
            "model_identity": "unknown",
            "model_identity_source": "",
        })
    if seen != expected:
        missing = sorted(expected - seen)
        raise ValueError(f"batch is missing {len(missing)} required question–paper pairs")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite imported assessments: {output_path}")
    with tempfile.TemporaryDirectory() as temporary:
        candidate = Path(temporary) / "assessments.csv"
        with candidate.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        result = validate(candidate, require_complete=True)
        data = candidate.read_bytes()
    fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON array file, or - to read the batch from stdin")
    args = parser.parse_args()
    raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    result = import_batch(json.loads(raw))
    print(f"Imported and validated {result['imported']} assessments to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
