#!/usr/bin/env python3
"""Read-only E6 candidate-pool audit; never samples, splits, freezes, or infers."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "E2" / "data" / "raw_papers.jsonl"
DEFAULT_FOCAL = ROOT / "E2" / "data" / "focal_papers.csv"
DEFAULT_MANIFEST = ROOT / "E2" / "data" / "pool_manifest.csv"

EXPECTED_RAW_UNIQUE = 2680
EXPECTED_FOCAL_UNIQUE = 300
EXPECTED_ELIGIBLE_UNIQUE = 2380
CORE_FIELDS = ("title", "abstract", "published", "updated", "authors", "paper_url", "source")
NEW_ARXIV_ID = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$", re.IGNORECASE)
OLD_ARXIV_ID = re.compile(r"^[a-z][a-z.-]*/\d{7}(?:v\d+)?$", re.IGNORECASE)


def canonicalize_arxiv_id(value: str) -> str:
    """Return the version-independent arXiv ID; preserve original IDs separately."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("paper ID is empty or not a string")

    candidate = value.strip()
    if "://" in candidate:
        parsed = urlparse(candidate)
        parts = [part for part in parsed.path.split("/") if part]
        if not parts:
            raise ValueError(f"URL has no arXiv ID: {value!r}")
        candidate = unquote(parts[-1])
        if candidate.lower().endswith(".pdf"):
            candidate = candidate[:-4]
    else:
        candidate = unquote(candidate)

    candidate = re.sub(r"^arxiv\s*:\s*", "", candidate, flags=re.IGNORECASE)
    candidate = candidate.strip().strip("/")
    if not (NEW_ARXIV_ID.fullmatch(candidate) or OLD_ARXIV_ID.fullmatch(candidate)):
        raise ValueError(f"unrecognized arXiv ID: {value!r}")

    return re.sub(r"v\d+$", "", candidate, flags=re.IGNORECASE)


def _stable_value(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonicalize_records(raw_rows):
    """Aggregate pool/category memberships and detect same-ID duplicate conflicts."""
    grouped = defaultdict(list)
    invalid_rows = []

    for row_number, row in enumerate(raw_rows, start=1):
        try:
            canonical_id = canonicalize_arxiv_id(row.get("paper_id"))
        except (AttributeError, ValueError) as exc:
            invalid_rows.append({"row": row_number, "error": str(exc)})
            continue
        grouped[canonical_id].append(row)

    papers = {}
    duplicate_groups = []
    exact_record_counts = Counter(_stable_value(row) for row in raw_rows)
    exact_duplicate_groups = sum(count > 1 for count in exact_record_counts.values())
    exact_duplicate_extra_rows = sum(count - 1 for count in exact_record_counts.values() if count > 1)
    same_pool_duplicates = []

    for canonical_id, rows in grouped.items():
        pools = sorted({row.get("pool") for row in rows if row.get("pool")})
        categories = set()
        source_ids = sorted({str(row.get("paper_id", "")) for row in rows})
        for row in rows:
            if row.get("primary_pool_category"):
                categories.add(str(row["primary_pool_category"]))
            raw_categories = row.get("categories") or []
            if isinstance(raw_categories, list):
                categories.update(str(value) for value in raw_categories if value)
            elif isinstance(raw_categories, str) and raw_categories.strip():
                categories.add(raw_categories.strip())

        conflicts = []
        core_signatures = {}
        for field in CORE_FIELDS:
            variants = {_stable_value(row.get(field)) for row in rows}
            if len(variants) > 1:
                conflicts.append(field)
                core_signatures[field] = sorted(variants)

        per_pool = Counter(row.get("pool") for row in rows if row.get("pool"))
        if any(count > 1 for count in per_pool.values()):
            same_pool_duplicates.append(canonical_id)
        if len(rows) > 1:
            duplicate_groups.append(canonical_id)

        papers[canonical_id] = {
            "canonical_id": canonical_id,
            "source_ids": source_ids,
            "pool_memberships": pools,
            "arxiv_categories": sorted(categories),
            "record_count": len(rows),
            "conflicting_core_fields": conflicts,
            "conflict_variants": core_signatures,
            # Do not choose arbitrarily when substantive metadata conflicts.
            "canonical_record": dict(rows[0]) if not conflicts else None,
            "has_nonempty_abstract": any(
                isinstance(row.get("abstract"), str) and row["abstract"].strip()
                for row in rows
            ),
        }

    return {
        "papers": papers,
        "invalid_rows": invalid_rows,
        "duplicate_id_groups": sorted(duplicate_groups),
        "same_pool_duplicate_ids": sorted(same_pool_duplicates),
        "exact_duplicate_record_groups": exact_duplicate_groups,
        "exact_duplicate_extra_rows": exact_duplicate_extra_rows,
    }


def _read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path}, line {line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object in {path}, line {line_number}")
            rows.append(row)
    return rows


def _read_ids_csv(path):
    ids = []
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "paper_id" not in reader.fieldnames:
            raise ValueError(f"{path} must contain a paper_id column")
        for line_number, row in enumerate(reader, start=2):
            try:
                ids.append(canonicalize_arxiv_id(row.get("paper_id")))
            except ValueError as exc:
                raise ValueError(f"Invalid paper ID in {path}, line {line_number}: {exc}") from exc
    return ids


def _read_manifest_pairs(path):
    if path is None:
        return None
    pairs = []
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"pool", "paper_id"}.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain pool and paper_id columns")
        for line_number, row in enumerate(reader, start=2):
            try:
                canonical_id = canonicalize_arxiv_id(row.get("paper_id"))
            except ValueError as exc:
                raise ValueError(f"Invalid paper ID in {path}, line {line_number}: {exc}") from exc
            pairs.append((str(row.get("pool", "")).strip(), canonical_id))
    return pairs


def audit_rows(raw_rows, focal_ids, manifest_pairs=None,
               expected_raw=EXPECTED_RAW_UNIQUE,
               expected_focal=EXPECTED_FOCAL_UNIQUE,
               expected_eligible=EXPECTED_ELIGIBLE_UNIQUE):
    aggregated = canonicalize_records(raw_rows)
    papers = aggregated["papers"]
    raw_ids = set(papers)
    focal_set = set(focal_ids)
    excluded_present = raw_ids & focal_set
    eligible_ids = raw_ids - focal_set
    missing_focal = focal_set - raw_ids

    conflicts = {
        paper_id: papers[paper_id]["conflicting_core_fields"]
        for paper_id in raw_ids
        if papers[paper_id]["conflicting_core_fields"]
    }
    empty_abstract_ids = sorted(
        paper_id for paper_id in raw_ids
        if not papers[paper_id]["has_nonempty_abstract"]
    )

    pool_membership_counts = Counter()
    category_membership_counts = Counter()
    cross_category_ids = []
    for paper_id, paper in papers.items():
        pool_membership_counts.update(paper["pool_memberships"])
        category_membership_counts.update(paper["arxiv_categories"])
        if len(paper["pool_memberships"]) > 1 or len(paper["arxiv_categories"]) > 1:
            cross_category_ids.append(paper_id)

    manifest_report = None
    if manifest_pairs is not None:
        raw_pair_counts = Counter(
            (str(row.get("pool", "")).strip(), papers[canonicalize_arxiv_id(row["paper_id"])]["canonical_id"])
            for row in raw_rows
            if row.get("pool") and row.get("paper_id")
            and canonicalize_arxiv_id(row["paper_id"]) in papers
        )
        manifest_pair_counts = Counter(manifest_pairs)
        raw_pairs = set(raw_pair_counts)
        manifest_pair_set = set(manifest_pair_counts)
        manifest_report = {
            "raw_pool_paper_pair_rows": sum(raw_pair_counts.values()),
            "manifest_pool_paper_pair_rows": len(manifest_pairs),
            "raw_only_pair_count": len(raw_pairs - manifest_pair_set),
            "manifest_only_pair_count": len(manifest_pair_set - raw_pairs),
            "duplicate_manifest_pair_rows": sum(v - 1 for v in manifest_pair_counts.values() if v > 1),
            "raw_duplicate_pool_pair_rows": sum(v - 1 for v in raw_pair_counts.values() if v > 1),
        }

    discrepancies = []

    def flag(code, count, examples=None):
        if count:
            item = {"code": code, "count": count}
            if examples:
                item["examples"] = examples[:10]
            discrepancies.append(item)

    if expected_raw is not None and len(raw_ids) != expected_raw:
        flag("raw_unique_count_mismatch", abs(len(raw_ids) - expected_raw),
             [f"observed={len(raw_ids)}", f"expected={expected_raw}"])
    if expected_focal is not None and len(focal_set) != expected_focal:
        flag("focal_unique_count_mismatch", abs(len(focal_set) - expected_focal),
             [f"observed={len(focal_set)}", f"expected={expected_focal}"])
    if expected_eligible is not None and len(eligible_ids) != expected_eligible:
        flag("eligible_unique_count_mismatch", abs(len(eligible_ids) - expected_eligible),
             [f"observed={len(eligible_ids)}", f"expected={expected_eligible}"])
    flag("focal_ids_missing_from_raw", len(missing_focal), sorted(missing_focal))
    flag("invalid_raw_paper_ids", len(aggregated["invalid_rows"]),
         [f"row={x['row']}: {x['error']}" for x in aggregated["invalid_rows"]])
    flag("same_pool_duplicate_ids", len(aggregated["same_pool_duplicate_ids"]),
         aggregated["same_pool_duplicate_ids"])
    flag("substantive_metadata_conflicts", len(conflicts),
         [f"{paper_id}: {fields}" for paper_id, fields in sorted(conflicts.items())])
    flag("canonical_papers_without_abstract", len(empty_abstract_ids), empty_abstract_ids)
    flag("exact_duplicate_record_groups", aggregated["exact_duplicate_record_groups"])
    if manifest_report:
        flag("raw_manifest_pool_pair_mismatch",
             manifest_report["raw_only_pair_count"] + manifest_report["manifest_only_pair_count"])
        flag("duplicate_manifest_pool_paper_pairs", manifest_report["duplicate_manifest_pair_rows"])

    return {
        "status": "pass" if not discrepancies else "discrepancies_found",
        "read_only": True,
        "sampled": False,
        "development_evaluation_split_created": False,
        "dataset_frozen": False,
        "raw_record_count": len(raw_rows),
        "raw_unique_canonical_id_count": len(raw_ids),
        "expected_raw_unique_id_count": expected_raw,
        "focal_csv_unique_canonical_id_count": len(focal_set),
        "focal_ids_present_in_raw_count": len(excluded_present),
        "expected_focal_unique_id_count": expected_focal,
        "eligible_unique_id_count_after_focal_exclusion": len(eligible_ids),
        "expected_eligible_unique_id_count": expected_eligible,
        "duplicate_canonical_id_group_count": len(aggregated["duplicate_id_groups"]),
        "duplicate_raw_rows_excess": sum(
            papers[paper_id]["record_count"] - 1
            for paper_id in aggregated["duplicate_id_groups"]
        ),
        "exact_duplicate_record_group_count": aggregated["exact_duplicate_record_groups"],
        "exact_duplicate_record_excess_rows": aggregated["exact_duplicate_extra_rows"],
        "same_pool_duplicate_id_count": len(aggregated["same_pool_duplicate_ids"]),
        "cross_category_paper_count": len(cross_category_ids),
        "pool_membership_counts": dict(sorted(pool_membership_counts.items())),
        "arxiv_category_membership_counts": dict(sorted(category_membership_counts.items())),
        "cross_category_examples": [
            {
                "canonical_id": paper_id,
                "pool_memberships": papers[paper_id]["pool_memberships"],
                "arxiv_categories": papers[paper_id]["arxiv_categories"],
            }
            for paper_id in sorted(cross_category_ids)[:10]
        ],
        "canonical_papers_without_nonempty_abstract_count": len(empty_abstract_ids),
        "conflicting_metadata_paper_count": len(conflicts),
        "conflicting_metadata_field_counts": dict(sorted(Counter(
            field for fields in conflicts.values() for field in fields
        ).items())),
        "missing_focal_ids_count": len(missing_focal),
        "manifest_comparison": manifest_report,
        "discrepancies": discrepancies,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--focal", type=Path, default=DEFAULT_FOCAL)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--expected-raw", type=int, default=EXPECTED_RAW_UNIQUE)
    parser.add_argument("--expected-focal", type=int, default=EXPECTED_FOCAL_UNIQUE)
    parser.add_argument("--expected-eligible", type=int, default=EXPECTED_ELIGIBLE_UNIQUE)
    args = parser.parse_args()

    try:
        raw_rows = _read_jsonl(args.raw)
        focal_ids = _read_ids_csv(args.focal)
        manifest_pairs = _read_manifest_pairs(args.manifest)
        report = audit_rows(
            raw_rows, focal_ids, manifest_pairs,
            args.expected_raw, args.expected_focal, args.expected_eligible,
        )
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "input_error", "error": str(exc)}, indent=2))
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
