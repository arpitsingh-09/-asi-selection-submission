#!/usr/bin/env python3
"""Fetch reproducible arXiv metadata for the E2 novelty experiment."""

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
API = "https://export.arxiv.org/api/query"

POOLS = {
    "computer_vision": "cs.CV",
    "computation_language": "cs.CL",
    "machine_learning": "cs.LG",
}

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"


def text_of(element, tag):
    node = element.find(tag)
    return " ".join(node.itertext()).strip() if node is not None else ""


def fetch_page(category, start, count):
    params = urllib.parse.urlencode({
        "search_query": f"cat:{category}",
        "start": start,
        "max_results": count,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    request = urllib.request.Request(
        f"{API}?{params}",
        headers={"User-Agent": "ASI-E2-Novelty-Research/1.0"},
    )

    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read()

    root = ET.fromstring(payload)
    records = []

    for entry in root.findall(f"{ATOM}entry"):
        raw_id = text_of(entry, f"{ATOM}id")
        paper_id = raw_id.rstrip("/").split("/")[-1]

        # Skip API error entries and malformed identifiers.
        if not paper_id or "error" in raw_id.lower():
            continue

        categories = [
            item.attrib.get("term", "")
            for item in entry.findall(f"{ARXIV}primary_category")
        ]
        categories += [
            item.attrib.get("term", "")
            for item in entry.findall(f"{ATOM}category")
        ]

        records.append({
            "paper_id": paper_id,
            "title": " ".join(
                text_of(entry, f"{ATOM}title").split()
            ),
            "abstract": " ".join(
                text_of(entry, f"{ATOM}summary").split()
            ),
            "published": text_of(entry, f"{ATOM}published"),
            "updated": text_of(entry, f"{ATOM}updated"),
            "authors": [
                text_of(author, f"{ATOM}name")
                for author in entry.findall(f"{ATOM}author")
            ],
            "categories": sorted(set(categories)),
            "primary_pool_category": category,
            "paper_url": f"https://arxiv.org/abs/{paper_id}",
            "source": "arXiv API",
        })

    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--per-pool", type=int, default=20,
        help="Number of papers to fetch per category for this run.",
    )
    parser.add_argument(
        "--page-size", type=int, default=20,
        help="Number of papers requested per API call (maximum 2000).",
    )
    args = parser.parse_args()

    if args.per_pool < 1 or args.page_size < 1 or args.page_size > 2000:
        parser.error("per-pool must be positive; page-size must be 1..2000")

    DATA.mkdir(parents=True, exist_ok=True)
    manifest = []
    retrieved_at = datetime.now(timezone.utc).isoformat()

    for pool_name, category in POOLS.items():
        print(f"\nFetching {pool_name} ({category})...", flush=True)
        records = []
        seen = set()
        start = 0

        while len(records) < args.per_pool:
            count = min(args.page_size, args.per_pool - len(records))
            try:
                page = fetch_page(category, start, count)
            except Exception as exc:
                print(
                    f"ERROR fetching {category} at offset {start}: "
                    f"{type(exc).__name__}: {exc}"
                )
                print("Stopping without claiming the pool is complete.")
                break

            if not page:
                print("No more records returned.")
                break

            for record in page:
                if record["paper_id"] in seen:
                    continue
                seen.add(record["paper_id"])
                record["pool"] = pool_name
                record["retrieved_at_utc"] = retrieved_at
                records.append(record)

            print(f"  Retrieved {len(records)}/{args.per_pool}", flush=True)
            start += len(page)

            if len(records) < args.per_pool:
                time.sleep(3)

        manifest.extend(records)
        print(f"  Final count: {len(records)}")

    # One JSONL record per paper-pool membership.
    jsonl_path = DATA / "raw_papers.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as file:
        for record in manifest:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    # CSV manifest for convenient inspection.
    csv_path = DATA / "pool_manifest.csv"
    columns = [
        "pool", "paper_id", "published", "updated", "title",
        "primary_pool_category", "categories", "paper_url",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for record in manifest:
            row = {key: record.get(key, "") for key in columns}
            row["categories"] = ";".join(record["categories"])
            writer.writerow(row)

    # Report both membership counts and unique papers across all pools.
    unique_ids = {row["paper_id"] for row in manifest}
    print("\n========== DATASET SUMMARY ==========")
    for pool_name in POOLS:
        count = sum(row["pool"] == pool_name for row in manifest)
        print(f"{pool_name}: {count} papers")
    print(f"Total pool memberships: {len(manifest)}")
    print(f"Unique paper IDs across pools: {len(unique_ids)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Manifest: {csv_path}")
    print("\nThis is a collection report, not an experimental result.")


if __name__ == "__main__":
    main()
