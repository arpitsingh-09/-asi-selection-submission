import hashlib
import tempfile
import unittest
from pathlib import Path

from M.supplementary_s1_e1_exploratory.run_s1 import (
    COHORT_SHA256,
    IntegrityError,
    author_intended_label,
    canonical_cohort_bytes,
    paired_cluster_bootstrap,
    run,
    select_records,
    verify_hash,
    verify_prereg_table,
)


class SupplementaryS1RunnerTests(unittest.TestCase):
    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.txt"
            path.write_text("changed", encoding="utf-8")
            with self.assertRaises(IntegrityError):
                verify_hash(path, hashlib.sha256(b"original").hexdigest())

    def test_selection_applies_date_fields_and_order(self):
        contrasts = [
            {"id": "h002", "A": "a", "B": "b", "B_min": "bm", "C": "c", "source_arxiv": "p2"},
            {"id": "h001", "A": "a", "B": "b", "B_min": "bm", "C": "c", "source_arxiv": "p1"},
            {"id": "h003", "A": "a", "B": "b", "B_min": "bm", "C": "c", "source_arxiv": "p3"},
        ]
        audit = [
            {"item_id": "h001", "date": "2025-07-01"},
            {"item_id": "h002", "date": "2025-06-30"},
            {"item_id": "h003", "date": "2025-07-02"},
        ]
        selected = select_records(contrasts, audit)
        self.assertEqual([r["id"] for r in selected], ["h001", "h003"])
        self.assertEqual(len({r["source_arxiv"] for r in selected}), 2)
        self.assertEqual(
            hashlib.sha256(canonical_cohort_bytes(selected)).hexdigest(),
            hashlib.sha256(b"h001\tp1\t2025-07-01\nh003\tp3\t2025-07-02\n").hexdigest(),
        )

    def test_frozen_selection_matches_preregistration(self):
        root = Path(__file__).resolve().parents[2]
        contrasts = [
            __import__("json").loads(line)
            for line in (root / "E1/contrast.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        import csv

        with (root / "E1/results_v2/source_alignment_audit.csv").open(encoding="utf-8", newline="") as f:
            audit = list(csv.DictReader(f))
        selected = select_records(contrasts, audit)
        self.assertEqual(len(selected), 60)
        self.assertEqual(hashlib.sha256(canonical_cohort_bytes(selected)).hexdigest(), COHORT_SHA256)
        verify_prereg_table(root / "M/supplementary_s1_e1_exploratory/PREREG.md", selected)

    def test_author_intended_label_mapping(self):
        self.assertEqual(author_intended_label("minimal_paraphrase"), 1)
        self.assertEqual(author_intended_label("near_miss"), 0)
        with self.assertRaises(ValueError):
            author_intended_label("other")

    def test_paired_bootstrap_is_deterministic_and_keeps_pairing(self):
        identity_minimal = [1, 1, 0, 1]
        bq_minimal = [1, 0, 0, 1]
        identity_near = [1, 0, 0, 0]
        bq_near = [0, 0, 0, 0]
        a = paired_cluster_bootstrap(identity_minimal, bq_minimal, identity_near, bq_near)
        b = paired_cluster_bootstrap(identity_minimal, bq_minimal, identity_near, bq_near)
        self.assertEqual(a, b)
        self.assertEqual(a["minimal_paraphrase"]["estimate"], 0.25)
        self.assertEqual(a["near_miss"]["estimate"], 0.25)
        self.assertEqual(a["minimal_paraphrase"]["draws"], 2000)

    def test_no_overwrite_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "existing"
            existing.mkdir()
            marker = existing / "results.json"
            marker.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                run(Path(tmp), existing)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
