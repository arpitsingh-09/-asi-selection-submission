"""Build an auditable corpus only from explicitly sourced question fields.

Titles, abstracts, claims, and generated annotations are never converted into
questions. The current E2 paper records do not expose a native question field,
so the default audit is expected to report a blocked empty corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCES = (
    ROOT.parent / "E2/data/raw_papers.jsonl",
    ROOT.parent / "E2/data/manipulation_papers.jsonl",
    ROOT / "data/development_manifest_v2.json",
)
SCHEMA = "e6-already-asked-question-corpus-v1"
QUESTION_FIELDS = ("research_question", "research_questions")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return _sha256_bytes(encoded)


def _question_values(value: Any) -> list[str]:
    if isinstance(value, str):
        candidates = [value]
    elif isinstance(value, list):
        candidates = value
    else:
        return []
    return [item.strip() for item in candidates
            if isinstance(item, str) and item.strip()]


def _records(path: Path):
    if path.suffix.lower() == ".jsonl":
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if isinstance(record, Mapping):
                yield line_number, record
    else:
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, Mapping):
            for line_number, record in enumerate(value.get("inputs", []), 1):
                if isinstance(record, Mapping):
                    yield line_number, record


def build_question_corpus_audit(source_paths: Sequence[Path] = DEFAULT_SOURCES) -> dict[str, Any]:
    """Build a provenance-bound corpus or explicit blocked report if none exists."""
    questions = []
    sources = []
    for source_path in source_paths:
        path = Path(source_path).resolve()
        raw_bytes = path.read_bytes()
        sources.append({
            "path": str(path.relative_to(ROOT.parent)) if path.is_relative_to(ROOT.parent) else str(path),
            "sha256": _sha256_bytes(raw_bytes),
        })
        for line_number, record in _records(path):
            paper_id = record.get("paper_id")
            for field in QUESTION_FIELDS:
                for question_index, question in enumerate(_question_values(record.get(field))):
                    question_id = _canonical_hash({
                        "source_sha256": _canonical_hash(record),
                        "field": field,
                        "question_index": question_index,
                        "question": question,
                    })
                    questions.append({
                        "question_id": "srcq-" + question_id[:24],
                        "question": question,
                        "source_paper_id": paper_id,
                        "source_file": sources[-1]["path"],
                        "source_line": line_number,
                        "source_record_sha256": _canonical_hash(record),
                        "source_field": field,
                        "question_index": question_index,
                        "source_type": "explicit_question_field_in_existing_record",
                    })
    # De-duplicate only byte-identical question strings; preserve all source links.
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in questions:
        grouped.setdefault(row["question"], []).append(row)
    corpus_rows = []
    for question in sorted(grouped):
        provenance = sorted(grouped[question], key=lambda row: (
            row["source_file"], row["source_line"], row["question_id"],
        ))
        row = {"question": question, "source_records": provenance}
        row["question_id"] = "aq-" + _canonical_hash(row)[:24]
        corpus_rows.append(row)
    unsigned = {
        "schema_version": SCHEMA,
        "status": "provisional_source_audit_only" if corpus_rows else "blocked_no_explicit_research_questions",
        "approval_required": True,
        "corpus_frozen": False,
        "question_count": len(corpus_rows),
        "source_record_count": sum(len(row["source_records"]) for row in corpus_rows),
        "question_fields_accepted": list(QUESTION_FIELDS),
        "forbidden_substitutions": ["title", "abstract", "claims", "generated_extraction"],
        "sources": sources,
        "questions": corpus_rows,
        "note": "Only explicit research_question(s) fields are admitted; no question is inferred from other text.",
    }
    result = dict(unsigned)
    result["manifest_sha256"] = _canonical_hash(unsigned)
    return result


def write_exclusive(path: Path, report: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path, action="append", dest="sources")
    args = parser.parse_args(argv)
    try:
        report = build_question_corpus_audit(args.sources or DEFAULT_SOURCES)
        write_exclusive(args.output, report)
    except (OSError, ValueError, json.JSONDecodeError, FileExistsError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "output": str(args.output), "status": report["status"],
        "question_count": report["question_count"],
        "source_record_count": report["source_record_count"],
        "manifest_sha256": report["manifest_sha256"],
    }, indent=2))
    return 0 if report["question_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
