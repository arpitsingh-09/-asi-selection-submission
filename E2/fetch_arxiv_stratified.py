#!/usr/bin/env python3
"""Collect arXiv papers with balanced annual coverage for E2."""

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
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

YEARS = list(range(2020, 2027))
CURRENT_DATE = datetime.now(timezone.utc).date()


def text_of(element, tag):
    node = element.find(tag)
    return " ".join(node.itertext()).strip() if node is not None else ""


def fetch_page(category, year, start, count):
    # Restrict results to a single calendar year.
    date_start = f"{year}01010000"

    if year == CURRENT_DATE.year:
        date_end = CURRENT_DATE.strftime("%Y%m%d") + "2359"
    else:
        date_end = f"{year}12312359"

    query = (
        f"cat:{category} AND "
        f"submittedDate:[{date_start} TO {date_end}]"
    )

    params = urllib.parse.urlencode({
        "search_query": query,
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

        published = text_of(entry, f"{ATOM}published")

        # Check the returned publication date rather than trusting
        # the search query alone.
        try:
            published_date = datetime.fromisoformat(
                published.replace("Z", "+00:00")
            ).date()
        except ValueError:
            continue

        if published_date.year != year:
            continue

        records.append({
            "paper_id": paper_id,
            "title": " ".join(
                text_of(entry, f"{ATOM}title").split()
            ),
            "abstract": " ".join(
                text_of(entry, f"{ATOM}summary").split()
            ),
            "published": published,
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
    parser.add_argument("--per-pool", type=int, default=1000)
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()

    if args.per_pool < 1 or not 1 <= args.page_size <= 2000:
        parser.error("per-pool must be positive; page-size must be 1..2000")

    DATA.mkdir(parents=True, exist_ok=True)
    manifest = []
    retrieved_at = datetime.now(timezone.utc).isoformat()

    # Allocate the target approximately evenly across seven years.
    base, remainder = divmod(args.per_pool, len(YEARS))
    quotas = {
        year: base + (1 if i < remainder else 0)
        for i, year in enumerate(YEARS)
    }

    for pool_name, category in POOLS.items():
        print(f"\nFetching {pool_name} ({category})...", flush=True)
        pool_records = []
        pool_seen = set()

        for year in YEARS:
            target = quotas[year]
            year_records = []
            year_seen = set()
            start = 0

            print(f"  Year {year}: target {target}", flush=True)

            while len(year_records) < target:
                count = min(args.page_size, target - len(year_records))

                try:
                    page = fetch_page(category, year, start, count)
                except Exception as exc:
                    print(
                        f"  ERROR in {year}, offset {start}: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    break

                if not page:
                    print(f"  No more results for {year}.")
                    break

                for record in page:
                    pid = record["paper_id"]

                    if pid in year_seen or pid in pool_seen:
                        continue

                    year_seen.add(pid)
                    record["pool"] = pool_name
                    record["retrieved_at_utc"] = retrieved_at
                    year_records.append(record)

                start += len(page)

                if len(year_records) < target:
                    time.sleep(3)

            pool_records.extend(year_records)
            pool_seen.update(r["paper_id"] for r in year_records)

            print(
                f"  Year {year}: collected {len(year_records)}/{target}",
                flush=True,
            )

            time.sleep(3)

        manifest.extend(pool_records)
        print(f"  Final pool count: {len(pool_records)}")

    jsonl_path = DATA / "raw_papers.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as file:
        for record in manifest:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

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

    print("\n========== COLLECTION SUMMARY ==========")
    print("Yearly target:", dict(quotas))

    for pool_name in POOLS:
        rows = [r for r in manifest if r["pool"] == pool_name]
        print(f"\n{pool_name}: {len(rows)} records")
        print("Year counts:", dict(sorted(Counter(
            datetime.fromisoformat(
                r["published"].replace("Z", "+00:00")
            ).year
            for r in rows
        ).items())))

    print("\nTotal pool memberships:", len(manifest))
    print("Unique paper IDs across pools:",
          len({r["paper_id"] for r in manifest}))
    print("JSONL:", jsonl_path)
    print("Manifest:", csv_path)
    print("\nCollection report only; no experimental results generated.")


if __name__ == "__main__":
    main()
