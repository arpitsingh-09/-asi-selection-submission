#!/usr/bin/env python3
"""Validate the preserved S1 E1 question-history documentation offline."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTER = HERE / "E1_QUESTION_HISTORY.csv"
VERSION_MAP = HERE / "E1_FIRST_COMMITTED_QUESTION_VERSIONS.csv"
QUESTION_SOURCE = HERE / "E1_contrast.jsonl"
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
REQUIRED = {
    "question_id", "exact_question_text", "question_version",
    "creation_timestamp", "sharing_timestamp", "timestamp_timezone",
    "original_source_path", "source_sha256", "timestamp_evidence_path",
    "evidence_reference", "verification_status",
    "creation_timestamp_status", "sharing_timestamp_status",
}
TEXT_KEYS = ("A", "B", "B_min", "C", "C_tilde", "narrower", "broader")
EXPECTED_IDS = {f"h{i:03d}" for i in range(1, 63)} - {"h028"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    errors: list[str] = []
    if not REGISTER.is_file():
        print(f"FAIL: missing {REGISTER}", file=sys.stderr)
        return 1
    rows = read_csv(REGISTER)
    with REGISTER.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
    missing = sorted(REQUIRED - columns)
    if missing:
        errors.append("missing required columns: " + ", ".join(missing))
    ids = [r.get("question_id", "") for r in rows]
    if len(rows) != 61:
        errors.append(f"expected 61 records, found {len(rows)}")
    if len(set(ids)) != len(ids):
        errors.append("duplicate question IDs")
    if set(ids) != EXPECTED_IDS:
        errors.append(f"question ID set mismatch: missing={sorted(EXPECTED_IDS-set(ids))}; unexpected={sorted(set(ids)-EXPECTED_IDS)}")

    for r in rows:
        qid = r.get("question_id", "<blank>")
        if not HASH_RE.fullmatch(r.get("source_sha256", "")):
            errors.append(f"{qid}: source_sha256 is not 64 hexadecimal characters")
        if r.get("verification_status") not in {"VERIFIED", "PARTIAL", "MISSING", "UNVERIFIED"}:
            errors.append(f"{qid}: invalid verification_status")
        if r.get("creation_timestamp_status") not in {"VERIFIED", "PARTIAL", "MISSING", "UNVERIFIED"}:
            errors.append(f"{qid}: invalid creation_timestamp_status")
        if r.get("sharing_timestamp_status") not in {"VERIFIED", "PARTIAL", "MISSING", "UNVERIFIED"}:
            errors.append(f"{qid}: invalid sharing_timestamp_status")
        for field, status in (("creation_timestamp", "creation_timestamp_status"), ("sharing_timestamp", "sharing_timestamp_status")):
            if r.get(status) == "VERIFIED":
                ev = r.get("timestamp_evidence_path", "").strip()
                if not r.get(field, "").strip():
                    errors.append(f"{qid}: {status}=VERIFIED but {field} is blank")
                if not ev:
                    errors.append(f"{qid}: {status}=VERIFIED without timestamp evidence path")
                else:
                    candidate = Path(ev)
                    if not candidate.is_absolute():
                        candidate = HERE / candidate
                    if not candidate.is_file():
                        errors.append(f"{qid}: timestamp evidence path does not resolve to a file: {ev}")
        if r.get("verification_status") == "VERIFIED":
            for field, status in (("creation_timestamp", "creation_timestamp_status"), ("sharing_timestamp", "sharing_timestamp_status")):
                if r.get(status) != "VERIFIED":
                    errors.append(f"{qid}: overall VERIFIED but {status} is not VERIFIED")

    if VERSION_MAP.is_file() and QUESTION_SOURCE.is_file():
        versions = {r["question_id"]: r for r in read_csv(VERSION_MAP)}
        source = {}
        with QUESTION_SOURCE.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    source[item["id"]] = item
        for r in rows:
            qid = r.get("question_id", "")
            v = versions.get(qid)
            if not v:
                errors.append(f"{qid}: no first-observed Git version mapping")
                continue
            if v.get("record_sha256") != r.get("source_sha256"):
                errors.append(f"{qid}: register hash differs from version-map record hash")
            if v.get("first_observed_commit_sha", "") not in r.get("question_version", ""):
                errors.append(f"{qid}: question_version does not cite mapped Git commit")
            try:
                text = json.loads(r.get("exact_question_text", ""))
            except json.JSONDecodeError:
                errors.append(f"{qid}: exact_question_text is not valid JSON")
                continue
            expected = {k: source.get(qid, {}).get(k, "") for k in TEXT_KEYS}
            if text != expected:
                errors.append(f"{qid}: preserved wording differs from E1 source snapshot")
    else:
        errors.append("version map or preserved E1 source copy is missing; cannot check hashes/text")

    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for e in errors:
            print("- " + e)
        return 1
    print("PASS: 61 unique question IDs; required fields present; source hashes formatted and match version map; wording matches preserved E1 snapshot; no timestamp is marked VERIFIED without a timestamp and existing evidence file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
