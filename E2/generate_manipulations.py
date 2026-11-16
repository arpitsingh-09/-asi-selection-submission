#!/usr/bin/env python3
"""Generate reproducible synthetic manipulation cases for E2.

Original source papers and claim-extraction records are never modified.
This script generates an experiment plan; it does not score any cases.
"""

import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "E2" / "data"

CLAIMS_FILE = DATA / "claims_v8_selected.jsonl"
RAW_FILE = DATA / "raw_papers.jsonl"
POOL_FILE = DATA / "pool_manifest.csv"

SYNTHETIC_OUT = DATA / "manipulation_papers.jsonl"
PLAN_OUT = DATA / "manipulation_plan.jsonl"
SUMMARY_OUT = DATA / "manipulation_plan_summary.json"

SEED_DESCRIPTION = "sha256:E2-manipulations-v1"
COVERAGE_LEVELS = (25, 50, 75, 100)


def read_jsonl(path):
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at {path}:{line_number}"
                ) from exc
    return rows


def parse_date(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing publication timestamp: {value!r}")
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def isoformat(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_id(*parts):
    value = "|".join(map(str, parts))
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]
    return f"e2synthetic:{digest}"


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    for path in (CLAIMS_FILE, RAW_FILE, POOL_FILE):
        if not path.exists():
            raise SystemExit(f"Required input missing: {path}")

    claim_rows = read_jsonl(CLAIMS_FILE)
    raw_rows = read_jsonl(RAW_FILE)

    raw_by_id = {}
    core_fields = ("title", "abstract", "published", "updated", "paper_url")
    for row in raw_rows:
        paper_id = row.get("paper_id")
        if not paper_id:
            raise SystemExit("A raw-paper record has no paper_id.")

        if paper_id in raw_by_id:
            previous = raw_by_id[paper_id]
            conflicts = [
                field for field in core_fields
                if previous.get(field) != row.get(field)
            ]
            if conflicts:
                raise SystemExit(
                    f"Conflicting metadata for duplicate paper ID "
                    f"{paper_id}: {conflicts}"
                )
            # Identical metadata across pools is expected. Keep one
            # canonical metadata record; pool membership is preserved
            # independently from pool_manifest.csv.
            continue

        raw_by_id[paper_id] = row

    with POOL_FILE.open(newline="", encoding="utf-8") as handle:
        pool_rows = list(csv.DictReader(handle))

    pool_ids_by_name = {}
    for row in pool_rows:
        pool = row["pool"]
        paper_id = row["paper_id"]
        pool_ids_by_name.setdefault(pool, set()).add(paper_id)

    focal_keys = [(r["pool"], r["paper_id"]) for r in claim_rows]
    if len(claim_rows) != 300 or len(set(focal_keys)) != 300:
        raise SystemExit(
            f"Expected 300 unique focal records; found {len(claim_rows)}."
        )

    synthetic = {}
    cases = []
    condition_counts = Counter()
    skipped = Counter()

    def add_synthetic(focal, condition, slot, title, abstract, timestamp):
        paper_id = stable_id(
            SEED_DESCRIPTION, focal["pool"], focal["paper_id"],
            condition, slot
        )
        record = {
            "paper_id": paper_id,
            "title": title,
            "abstract": abstract,
            "published": timestamp,
            "updated": timestamp,
            "authors": [],
            "categories": [],
            "primary_pool_category": focal["pool"],
            "paper_url": "",
            "source": "E2 synthetic manipulation; not a real publication",
            "pool": focal["pool"],
            "synthetic_manipulation": True,
            "synthetic_condition": condition,
            "synthetic_seed": SEED_DESCRIPTION,
        }

        if paper_id in synthetic and synthetic[paper_id] != record:
            raise SystemExit(f"Synthetic ID collision: {paper_id}")

        synthetic[paper_id] = record
        return paper_id

    for focal in claim_rows:
        pool = focal["pool"]
        focal_id = focal["paper_id"]

        if focal_id not in raw_by_id:
            raise SystemExit(f"Focal paper absent from raw corpus: {focal_id}")

        paper = raw_by_id[focal_id]
        title = (paper.get("title") or focal.get("title") or "").strip()
        abstract = (paper.get("abstract") or "").strip()
        published = paper.get("published") or focal.get("published")

        if not title or not abstract:
            skipped["missing_title_or_abstract"] += 1
            continue

        cutoff = parse_date(published)
        claims = [
            item["claim"].strip()
            for item in focal.get("claims", [])
            if isinstance(item, dict)
            and isinstance(item.get("claim"), str)
            and item["claim"].strip()
        ]

        if not claims:
            skipped["no_valid_claims"] += 1
            continue

        available_ids = pool_ids_by_name.get(pool)
        if not available_ids:
            raise SystemExit(f"No pool-manifest entries for pool {pool!r}")

        # Exclude the focal paper explicitly. The scorer separately enforces
        # strict publication-before-cutoff filtering.
        base_pool = sorted(available_ids - {focal_id})

        base_eligible = [
            pid for pid in base_pool
            if pid in raw_by_id
            and raw_by_id[pid].get("published")
            and parse_date(raw_by_id[pid]["published"]) < cutoff
            and (raw_by_id[pid].get("title") or raw_by_id[pid].get("abstract"))
        ]

        if len(base_eligible) < 2:
            skipped["fewer_than_two_eligible_source_papers"] += 1
            continue

        idea_text = f"{title}\n\n{abstract}"
        synthetic_timestamp = isoformat(cutoff - timedelta(seconds=1))

        def add_case(condition, condition_pool, level=None, metadata=None):
            case_id = stable_id(
                "case-v1", pool, focal_id, condition, level or ""
            )
            cases.append({
                "case_id": case_id,
                "pool": pool,
                "focal_paper_id": focal_id,
                "published": isoformat(cutoff),
                "t": isoformat(cutoff),
                "idea_text": idea_text,
                "claims": claims,
                "pool_ids": condition_pool,
                "manipulation": condition,
                "coverage_percent": level,
                "expected_direction": {
                    "Y": "decrease",
                    "N": "decrease",
                    "yours": "decrease",
                    "density": "decrease",
                } if condition != "baseline" else {
                    "Y": "reference",
                    "N": "reference",
                    "yours": "reference",
                    "density": "reference",
                },
                "metadata": metadata or {},
                "scoring_status": "not_scored",
            })
            condition_counts[condition] += 1

        add_case("baseline", base_eligible)

        exact_id = add_synthetic(
            focal, "exact_copy", "all",
            title, abstract, synthetic_timestamp
        )
        add_case(
            "exact_copy", base_eligible + [exact_id],
            metadata={"synthetic_paper_ids": [exact_id]},
        )

        # Deterministic claim order is preserved from the audited extraction.
        for percent in COVERAGE_LEVELS:
            count = max(1, math.ceil(len(claims) * percent / 100))
            planted = claims[:count]
            condition = f"coverage_{percent}"
            synthetic_id = add_synthetic(
                focal, condition, "planted",
                f"Synthetic prior work: {percent}% claim coverage",
                "\n".join(planted),
                synthetic_timestamp,
            )
            add_case(
                condition, base_eligible + [synthetic_id], level=percent,
                metadata={
                    "synthetic_paper_ids": [synthetic_id],
                    "planted_claim_count": count,
                    "total_claim_count": len(claims),
                    "claim_selection": "first_n_in_audited_extraction_order",
                },
            )

        # Both conditions contain the same complete claim set.
        concentrated_id = add_synthetic(
            focal, "concentrated", "all_claims",
            "Synthetic prior work: concentrated claim coverage",
            "\n".join(claims),
            synthetic_timestamp,
        )
        add_case(
            "concentrated", base_eligible + [concentrated_id],
            metadata={
                "synthetic_paper_ids": [concentrated_id],
                "planted_claim_count": len(claims),
            },
        )

        distributed_ids = []
        for index, claim in enumerate(claims):
            distributed_ids.append(add_synthetic(
                focal, "distributed", f"claim_{index + 1}",
                f"Synthetic prior work: claim {index + 1}",
                claim,
                synthetic_timestamp,
            ))
        add_case(
            "distributed", base_eligible + distributed_ids,
            metadata={
                "synthetic_paper_ids": distributed_ids,
                "planted_claim_count": len(claims),
            },
        )

    # Validate all referenced source IDs and synthetic timestamps.
    for case in cases:
        cutoff = parse_date(case["t"])
        if case["focal_paper_id"] in case["pool_ids"]:
            raise SystemExit(
                f"Focal paper accidentally included in its own pool: "
                f"{case['case_id']}"
            )

        for paper_id in case["pool_ids"]:
            if paper_id in synthetic:
                timestamp = parse_date(synthetic[paper_id]["published"])
            elif paper_id in raw_by_id:
                date_value = raw_by_id[paper_id].get("published")
                if not date_value:
                    raise SystemExit(
                        f"Missing source date for pool paper {paper_id}"
                    )
                timestamp = parse_date(date_value)
            else:
                raise SystemExit(
                    f"Unknown pool paper ID in case {case['case_id']}: "
                    f"{paper_id}"
                )

            if timestamp >= cutoff:
                raise SystemExit(
                    f"Non-prior paper in case {case['case_id']}: {paper_id}"
                )

    # Protect existing outputs from accidental overwrite.
    for path in (SYNTHETIC_OUT, PLAN_OUT, SUMMARY_OUT):
        if path.exists():
            raise SystemExit(
                f"Output already exists: {path}\n"
                "Inspect it first; this script will not overwrite it."
            )

    write_jsonl(SYNTHETIC_OUT, list(synthetic.values()))
    write_jsonl(PLAN_OUT, cases)

    summary = {
        "seed_description": SEED_DESCRIPTION,
        "focal_records_read": len(claim_rows),
        "cases_generated": len(cases),
        "synthetic_records_generated": len(synthetic),
        "condition_counts": dict(sorted(condition_counts.items())),
        "claim_count_distribution": dict(sorted(Counter(
            len([
                item for item in row.get("claims", [])
                if isinstance(item, dict)
                and isinstance(item.get("claim"), str)
                and item["claim"].strip()
            ])
            for row in claim_rows
        ).items())),
        "skipped": dict(skipped),
        "source_pool_manifest_rows": len(pool_rows),
        "source_raw_papers": len(raw_rows),
        "strict_prior_date_validation": "passed",
        "focal_self_exclusion_validation": "passed",
        "scoring_performed": False,
        "limitations": [
            "Synthetic papers are experimental interventions, not real publications.",
            "Paraphrase, near/far pool, older/newer pool, and R2 benchmark evaluation are not generated here.",
            "Coverage uses the first N claims in the audited extraction order; claim order is not a relevance ranking.",
            "For focal papers with few claims, 25/50/75/100 percent may map to identical integer claim counts.",
            "Automated claim audits do not establish semantic correctness.",
        ],
    }

    SUMMARY_OUT.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Manipulation generation completed; nothing was scored.")
    print(f"Focal records read: {len(claim_rows)}")
    print(f"Cases generated: {len(cases)}")
    print(f"Synthetic records generated: {len(synthetic)}")
    print(f"Conditions: {dict(sorted(condition_counts.items()))}")
    print(f"Skipped focal records: {dict(skipped)}")
    print(f"Strict prior-date validation: passed")
    print(f"Focal self-exclusion validation: passed")
    print(f"Experiment plan: {PLAN_OUT}")
    print(f"Synthetic papers: {SYNTHETIC_OUT}")
    print(f"Summary: {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
