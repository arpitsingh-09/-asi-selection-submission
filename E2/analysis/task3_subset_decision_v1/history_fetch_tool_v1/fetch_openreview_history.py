#!/usr/bin/env python3
"""Read-only fetch of Task 3's queued OpenReview note/edit histories.

The script preserves each raw JSON response, records its URL, retrieval time,
and SHA-256, and refuses to reuse an output directory. It does not alter any
protocol, ledger, review decision, or OpenReview record.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api2.openreview.net"
EXPECTED = 28


def request_json(url: str, timeout: int) -> tuple[bytes, Any]:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "ASI-Task3-history-audit/1.0"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = response.read()
    return payload, json.loads(payload)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_response(path: Path, payload: bytes) -> dict[str, str | int]:
    path.write_bytes(payload)
    return {
        "path": path.name,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def fetch_edits(forum_id: str, paper_dir: Path, timeout: int) -> list[dict[str, Any]]:
    edits: list[dict[str, Any]] = []
    after: str | None = None
    page = 0
    while True:
        query: dict[str, str] = {
            "note.id": forum_id,
            "sort": "tcdate:asc",
            "limit": "100",
        }
        if after:
            query["after"] = after
        url = f"{API}/notes/edits?{urllib.parse.urlencode(query)}"
        payload, body = request_json(url, timeout)
        rows = body.get("edits") if isinstance(body, dict) else None
        if not isinstance(rows, list):
            raise ValueError(f"Unexpected edits response for {forum_id}: missing edits list")
        save_response(paper_dir / f"edits_page_{page:03d}.json", payload)
        edits.extend(rows)
        if len(rows) < 100:
            break
        last_id = rows[-1].get("id")
        if not last_id or last_id == after:
            raise ValueError(f"Edit pagination stalled for {forum_id}")
        after = str(last_id)
        page += 1
    return edits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True,
                        help="New, unused directory for raw API responses and manifest")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    with args.queue.open(newline="", encoding="utf-8") as handle:
        queue = list(csv.DictReader(handle))
    if len(queue) != EXPECTED:
        raise SystemExit(f"Expected exactly {EXPECTED} queue rows; found {len(queue)}")
    forum_ids = [row.get("forum_id", "") for row in queue]
    if any(not x for x in forum_ids) or len(set(forum_ids)) != EXPECTED:
        raise SystemExit("Queue has missing or duplicate forum IDs")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(exist_ok=False)
    manifest: dict[str, Any] = {
        "retrieval_started_utc": utc_now(),
        "api_base": API,
        "queue_path": str(args.queue.resolve()),
        "queue_sha256": hashlib.sha256(args.queue.read_bytes()).hexdigest(),
        "read_only": True,
        "records": [],
        "errors": [],
    }

    for row in queue:
        forum_id = row["forum_id"]
        paper_dir = output / forum_id
        paper_dir.mkdir()
        entry: dict[str, Any] = {
            "forum_id": forum_id,
            "title": row["title"],
            "retrieved_at_utc": utc_now(),
            "requests": [],
            "edit_count": None,
        }
        note_query = urllib.parse.urlencode({"id": forum_id, "details": "revisions"})
        note_url = f"{API}/notes?{note_query}"
        try:
            payload, body = request_json(note_url, args.timeout)
            saved = save_response(paper_dir / "note_with_revisions.json", payload)
            entry["requests"].append({"url": note_url, **saved})
            notes = body.get("notes") if isinstance(body, dict) else None
            if not isinstance(notes, list) or len(notes) != 1:
                raise ValueError(f"Expected one note for {forum_id}; got {len(notes) if isinstance(notes, list) else 'invalid response'}")
            edits = fetch_edits(forum_id, paper_dir, args.timeout)
            entry["edit_count"] = len(edits)
            entry["edits"] = edits
            entry["status"] = "fetched"
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = f"{type(exc).__name__}: {exc}"
            manifest["errors"].append({"forum_id": forum_id, "error": entry["error"]})
        (paper_dir / "record.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        manifest["records"].append({k: v for k, v in entry.items() if k != "edits"})
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{forum_id}: {entry['status']}" + (f" ({entry.get('edit_count')} edits)" if entry.get("edit_count") is not None else ""), flush=True)

    manifest["retrieval_finished_utc"] = utc_now()
    manifest["completed_records"] = sum(r.get("status") == "fetched" for r in manifest["records"])
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved history snapshot: {output}")
    print(f"Fetched: {manifest['completed_records']}/{EXPECTED}; errors: {len(manifest['errors'])}")
    return 0 if not manifest["errors"] else 2


if __name__ == "__main__":
    sys.exit(main())
