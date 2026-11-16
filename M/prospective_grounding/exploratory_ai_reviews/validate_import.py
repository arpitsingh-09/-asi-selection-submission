"""Validate a supplementary external-AI assessment import without scoring."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
GENERATED_ROOT = BASE / "generated_v2"
TEMPLATE_PATH = Path(__file__).resolve().parent / "assessments.csv"
FIELDS = (
    "question_id", "paper_id", "rating", "evidence_text", "reviewer_type",
    "model_identity", "model_identity_source", "source_type", "experimental_status",
)
FIXED = {
    "reviewer_type": "external_ai",
    "source_type": "abstract_summary",
    "experimental_status": "exploratory_not_preregistered_human_review",
}


def expected_pairs(generated_root: Path = GENERATED_ROOT) -> set[tuple[str, str]]:
    completed = list(generated_root.glob("run_*/run_complete.json"))
    if len(completed) != 1:
        raise ValueError("expected exactly one completed prospective-grounding V2 run")
    records = []
    for path in sorted(completed[0].parent.glob("attempts/*.json")):
        import json
        record = json.loads(path.read_text())
        if record.get("status") != "SUCCEEDED":
            raise ValueError("V2 generation records must all be successful")
        records.append(record)
    by_key = {(item["family"], item["kind"]): item for item in records}
    if len(by_key) != 4:
        raise ValueError("expected exactly four unique V2 question records")
    families = {family for family, _ in by_key}
    if len(families) != 2 or any((family, kind) not in by_key
                                for family in families for kind in ("primary", "decoy")):
        raise ValueError("V2 question/family records are incomplete")
    pairs = set()
    for family in families:
        other = next(candidate for candidate in families if candidate != family)
        primary = by_key[(family, "primary")]
        decoy = by_key[(family, "decoy")]
        for paper_id in primary["input_ids"]:
            pairs.add((primary["question_id"], paper_id))
            pairs.add((decoy["question_id"], paper_id))
        for paper_id in by_key[(other, "primary")]["input_ids"]:
            pairs.add((primary["question_id"], paper_id))
    if len(pairs) != 18:
        raise ValueError(f"registered V2 review design resolved to {len(pairs)} pairs, expected 18")
    return pairs


def write_template(path: Path = TEMPLATE_PATH, generated_root: Path = GENERATED_ROOT) -> None:
    pairs = sorted(expected_pairs(generated_root))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for question_id, paper_id in pairs:
            writer.writerow({
                "question_id": question_id,
                "paper_id": paper_id,
                "rating": "",
                "evidence_text": "",
                **FIXED,
                "model_identity": "unknown",
                "model_identity_source": "",
            })


def validate(path: Path = TEMPLATE_PATH, *, require_complete: bool = False,
             generated_root: Path = GENERATED_ROOT) -> dict:
    expected = expected_pairs(generated_root)
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("assessment CSV fields do not match the required schema")
        rows = list(reader)
    pairs = [(row["question_id"], row["paper_id"]) for row in rows]
    if len(rows) != 18 or len(set(pairs)) != len(pairs):
        raise ValueError("complete/template file must have exactly 18 unique question–paper pairs")
    if set(pairs) != expected:
        raise ValueError("question/paper IDs do not exactly match the registered V2 review pairs")
    missing = 0
    for row in rows:
        for key, value in FIXED.items():
            if row.get(key) != value:
                raise ValueError(f"{key} must be {value!r}")
        identity = row.get("model_identity", "").strip()
        if not identity:
            raise ValueError("model_identity must be unknown or independently documented")
        if identity.lower() != "unknown" and not row.get("model_identity_source", "").strip():
            raise ValueError("non-unknown model identity requires an independent source reference")
        rating, evidence = row.get("rating", "").strip(), row.get("evidence_text", "").strip()
        if not rating or not evidence:
            missing += 1
            continue
        if rating not in {"0", "1", "2"}:
            raise ValueError("ratings must be exactly 0, 1, or 2")
    if require_complete and missing:
        raise ValueError(f"assessment import is incomplete: {missing} rows lack rating or evidence")
    imported = sum(bool(row.get("rating", "").strip() and row.get("evidence_text", "").strip())
                   for row in rows)
    return {"expected_pairs": len(expected), "rows": len(rows), "imported": imported,
            "incomplete_rows": missing, "complete": missing == 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--create-template", action="store_true")
    parser.add_argument("--path", type=Path, default=TEMPLATE_PATH)
    args = parser.parse_args()
    if args.create_template:
        write_template(args.path)
    result = validate(args.path, require_complete=args.require_complete)
    print(f"Validated {result['rows']} pairs; imported={result['imported']}; "
          f"incomplete={result['incomplete_rows']}; complete={result['complete']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
