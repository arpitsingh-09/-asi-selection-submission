#!/usr/bin/env python3

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path("E2/data")
INPUT_JSONL = DATA_DIR / "raw_papers.jsonl"
OUTPUT_CSV = DATA_DIR / "focal_papers.csv"

POOLS = [
    "computer_vision",
    "computation_language",
    "machine_learning",
]

YEARS = list(range(2020, 2027))
TARGET_PER_POOL = 100
SEED = "E2-focal-selection-v1"

FIELDS = [
    "pool",
    "paper_id",
    "published",
    "updated",
    "title",
    "primary_pool_category",
    "categories",
    "paper_url",
    "selection_seed",
]


def stable_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main():
    if not INPUT_JSONL.exists():
        raise SystemExit(f"Missing input: {INPUT_JSONL}")

    papers_by_pool_year = defaultdict(list)
    seen_pool_ids = set()

    with INPUT_JSONL.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            paper = json.loads(line)

            pool = paper.get("pool")
            paper_id = paper.get("paper_id")
            published = paper.get("published", "")

            if pool not in POOLS:
                continue

            if not paper_id or not published:
                raise SystemExit(
                    f"Missing paper ID or date on JSONL line {line_number}"
                )

            key = (pool, paper_id)
            if key in seen_pool_ids:
                raise SystemExit(f"Duplicate paper within pool: {key}")
            seen_pool_ids.add(key)

            year = int(published[:4])
            if year not in YEARS:
                raise SystemExit(
                    f"Unexpected publication year {year}: {paper_id}"
                )

            papers_by_pool_year[(pool, year)].append(paper)

    selected = []

    # Distribute 100 selections as evenly as possible across seven years.
    base = TARGET_PER_POOL // len(YEARS)
    remainder = TARGET_PER_POOL % len(YEARS)

    yearly_targets = {
        year: base + (1 if index < remainder else 0)
        for index, year in enumerate(YEARS)
    }

    for pool in POOLS:
        pool_selected = []

        for year in YEARS:
            candidates = papers_by_pool_year[(pool, year)]
            candidates = sorted(
                candidates,
                key=lambda p: stable_hash(
                    f"{SEED}|{pool}|{p['paper_id']}"
                ),
            )

            target = yearly_targets[year]

            if len(candidates) < target:
                raise SystemExit(
                    f"Not enough papers for {pool}, {year}: "
                    f"need {target}, have {len(candidates)}"
                )

            pool_selected.extend(candidates[:target])

        if len(pool_selected) != TARGET_PER_POOL:
            raise SystemExit(
                f"Incorrect selection size for {pool}: "
                f"{len(pool_selected)}"
            )

        selected.extend(
            {**paper, "selection_seed": SEED}
            for paper in pool_selected
        )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for paper in selected:
            writer.writerow({
                field: paper.get(field, "")
                for field in FIELDS
            })

    # Verify the saved file rather than relying only on in-memory results.
    with OUTPUT_CSV.open(newline="", encoding="utf-8") as f:
        saved = list(csv.DictReader(f))

    pool_counts = Counter(row["pool"] for row in saved)
    year_counts = Counter(
        (row["pool"], row["published"][:4]) for row in saved
    )

    assert len(saved) == 300, f"Expected 300 rows, found {len(saved)}"
    assert all(pool_counts[p] == 100 for p in POOLS), pool_counts
    assert len({
        (row["pool"], row["paper_id"]) for row in saved
    }) == 300, "Duplicate focal papers within a pool"

    print("FOCAL PAPER SELECTION VERIFIED")
    print(f"Output: {OUTPUT_CSV}")
    print(f"Total focal-paper selections: {len(saved)}")

    print("\nSelections per pool:")
    for pool in POOLS:
        print(f"  {pool}: {pool_counts[pool]}")

    print("\nSelections by year:")
    for pool in POOLS:
        print(f"  {pool}")
        for year in YEARS:
            print(f"    {year}: {year_counts[(pool, str(year))]}")

    unique_papers = len({row["paper_id"] for row in saved})
    print(f"\nUnique paper IDs across all pools: {unique_papers}")
    print(
        "Note: a paper may appear in more than one pool if it belongs "
        "to multiple categories."
    )


if __name__ == "__main__":
    main()
