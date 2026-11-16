#!/usr/bin/env python3
"""Non-destructive fixtures for E6 read-only dataset preparation."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_dataset import (  # noqa: E402
    audit_rows,
    canonicalize_arxiv_id,
    canonicalize_records,
)


def paper(pid, pool, category, abstract="An abstract.", title="Paper title"):
    return {
        "paper_id": pid,
        "title": title,
        "abstract": abstract,
        "published": "2024-01-01T00:00:00Z",
        "updated": "2024-01-01T00:00:00Z",
        "authors": ["Author"],
        "categories": [category],
        "primary_pool_category": category,
        "paper_url": "https://arxiv.org/abs/" + pid,
        "source": "arXiv API",
        "pool": pool,
    }


class CanonicalizationTests(unittest.TestCase):
    def test_version_and_url_forms_canonicalize(self):
        self.assertEqual(canonicalize_arxiv_id("2401.00001v2"), "2401.00001")
        self.assertEqual(
            canonicalize_arxiv_id("https://arxiv.org/abs/2401.00001v2"),
            "2401.00001",
        )
        self.assertEqual(
            canonicalize_arxiv_id("arXiv:2401.00001v1"),
            "2401.00001",
        )
        self.assertEqual(
            canonicalize_arxiv_id("https://arxiv.org/pdf/2401.00001v3.pdf"),
            "2401.00001",
        )

    def test_invalid_id_is_rejected(self):
        with self.assertRaises(ValueError):
            canonicalize_arxiv_id("not-an-arxiv-id")


class AuditFixtureTests(unittest.TestCase):
    def test_cross_category_membership_is_preserved_and_focal_is_excluded(self):
        raw = [
            paper("2401.00001v1", "vision", "cs.CV"),
            paper("2401.00001v1", "language", "cs.CL"),
            paper("2401.00002v1", "vision", "cs.CV"),
        ]
        aggregated = canonicalize_records(raw)
        shared = aggregated["papers"]["2401.00001"]
        self.assertEqual(shared["pool_memberships"], ["language", "vision"])
        self.assertEqual(shared["arxiv_categories"], ["cs.CL", "cs.CV"])

        report = audit_rows(
            raw,
            {"2401.00002"},
            [("vision", "2401.00001"), ("language", "2401.00001"),
             ("vision", "2401.00002")],
            expected_raw=2,
            expected_focal=1,
            expected_eligible=1,
        )
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["duplicate_canonical_id_group_count"], 1)
        self.assertEqual(report["eligible_unique_id_count_after_focal_exclusion"], 1)
        self.assertEqual(report["cross_category_paper_count"], 1)
        self.assertFalse(report["sampled"])
        self.assertFalse(report["dataset_frozen"])

    def test_exact_duplicate_records_are_reported(self):
        row = paper("2401.00001v1", "vision", "cs.CV")
        report = audit_rows([row, dict(row)], set(), None, 1, 0, 1)
        self.assertEqual(report["exact_duplicate_record_group_count"], 1)
        self.assertEqual(report["exact_duplicate_record_excess_rows"], 1)
        self.assertEqual(report["status"], "discrepancies_found")

    def test_substantive_metadata_conflict_is_not_silently_resolved(self):
        raw = [
            paper("2401.00001v1", "vision", "cs.CV", abstract="First abstract."),
            paper("2401.00001v1", "language", "cs.CL", abstract="Different abstract."),
        ]
        aggregated = canonicalize_records(raw)
        entry = aggregated["papers"]["2401.00001"]
        self.assertIn("abstract", entry["conflicting_core_fields"])
        self.assertIsNone(entry["canonical_record"])
        report = audit_rows(raw, set(), None, 1, 0, 1)
        self.assertEqual(report["conflicting_metadata_paper_count"], 1)
        self.assertEqual(report["status"], "discrepancies_found")

    def test_manifest_mismatch_and_missing_exclusion_are_reported(self):
        raw = [paper("2401.00001v1", "vision", "cs.CV")]
        report = audit_rows(
            raw,
            {"2401.00002"},
            [("language", "2401.00001")],
            expected_raw=1,
            expected_focal=1,
            expected_eligible=0,
        )
        self.assertEqual(report["missing_focal_ids_count"], 1)
        self.assertEqual(report["manifest_comparison"]["raw_only_pair_count"], 1)
        self.assertEqual(report["manifest_comparison"]["manifest_only_pair_count"], 1)
        self.assertEqual(report["status"], "discrepancies_found")

    def test_fixtures_are_temporary_and_do_not_write_to_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "raw.jsonl"
            focal_path = root / "focal.csv"
            manifest_path = root / "manifest.csv"
            raw_path.write_text(json.dumps(paper("2401.00001v1", "vision", "cs.CV")) + "\n")
            with focal_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["paper_id"])
                writer.writeheader()
                writer.writerow({"paper_id": "2401.00002v1"})
            with manifest_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["pool", "paper_id"])
                writer.writeheader()
                writer.writerow({"pool": "vision", "paper_id": "2401.00001v1"})
            self.assertTrue(raw_path.exists())
            self.assertTrue(focal_path.exists())
            self.assertTrue(manifest_path.exists())
            self.assertEqual(len(list(root.iterdir())), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
