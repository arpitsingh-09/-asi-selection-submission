#!/usr/bin/env python3
"""Data-integrity checks for the reserved E6 development manifest."""

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_dataset import _read_ids_csv, _read_jsonl, canonicalize_records

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "E6/data/development_manifest_v1.json"
MANIFEST_V2_PATH = ROOT / "E6/data/development_manifest_v2.json"
RAW_PATH = ROOT / "E2/data/raw_papers.jsonl"
FOCAL_PATH = ROOT / "E2/data/focal_papers.csv"
POOL_MANIFEST_PATH = ROOT / "E2/data/pool_manifest.csv"
SELECTION_PREFIX = "E6-DEV-PILOT-v1|"


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def source_record_hash(record):
    encoded = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(encoded.encode("utf-8"))


def assert_disjoint(development_ids, evaluation_candidate_ids):
    overlap = set(development_ids).intersection(evaluation_candidate_ids)
    if overlap:
        raise AssertionError(f"development/evaluation ID overlap: {sorted(overlap)}")


class DevelopmentManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.raw_rows = _read_jsonl(RAW_PATH)
        cls.focal_ids = set(_read_ids_csv(FOCAL_PATH))
        cls.papers = canonicalize_records(cls.raw_rows)["papers"]

    def test_manifest_source_hashes_match_current_source_files(self):
        sources = {
            "raw_corpus": (RAW_PATH, self.manifest["source_files"]["raw_corpus"]),
            "focal_exclusions": (FOCAL_PATH, self.manifest["source_files"]["focal_exclusions"]),
            "pool_manifest": (POOL_MANIFEST_PATH, self.manifest["source_files"]["pool_manifest"]),
        }
        for _, (path, recorded) in sources.items():
            with self.subTest(source=path.name):
                self.assertEqual(sha256_bytes(path.read_bytes()), recorded["sha256"])

    def test_inputs_revalidate_identity_eligibility_and_record_hashes(self):
        inputs = self.manifest["inputs"]
        self.assertEqual(len(inputs), 10)
        self.assertEqual(self.manifest["split"], "DEVELOPMENT")
        self.assertTrue(all(row["split"] == "DEVELOPMENT" for row in inputs))
        self.assertFalse(self.manifest["final_evaluation_inputs_selected"])
        self.assertFalse(self.manifest["final_evaluation_inputs_frozen"])

        for row in inputs:
            paper_id = row["paper_id"]
            with self.subTest(paper_id=paper_id):
                self.assertNotIn(paper_id, self.focal_ids)
                source = self.papers[paper_id]
                record = source["canonical_record"]
                self.assertIsNotNone(record)
                self.assertTrue(record["abstract"].strip())
                self.assertEqual(row["source_version_ids"], source["source_ids"])
                self.assertEqual(row["pool_memberships"], source["pool_memberships"])
                self.assertEqual(row["paper_url"], record["paper_url"])
                self.assertEqual(row["source"], record["source"])
                self.assertEqual(row["title"], record["title"])
                self.assertEqual(row["abstract"], record["abstract"])
                self.assertEqual(row["source_record_sha256"], source_record_hash(record))
                self.assertEqual(row["abstract_sha256"], sha256_bytes(record["abstract"].encode("utf-8")))
                expected_selection_key = sha256_bytes((SELECTION_PREFIX + paper_id).encode("utf-8"))
                self.assertEqual(row["selection_key_sha256"], expected_selection_key)

    def test_selected_ids_are_the_first_ten_by_the_recorded_hash_rule(self):
        candidates = []
        for paper_id, paper in self.papers.items():
            record = paper["canonical_record"]
            if paper_id in self.focal_ids or record is None:
                continue
            if not isinstance(record.get("abstract"), str) or not record["abstract"].strip():
                continue
            key = sha256_bytes((SELECTION_PREFIX + paper_id).encode("utf-8"))
            candidates.append((key, paper_id))
        candidates.sort(key=lambda item: (item[0], item[1]))

        selected = [row["paper_id"] for row in self.manifest["inputs"]]
        self.assertEqual(len(candidates), 2380)
        self.assertEqual(self.manifest["selection_rule"]["eligible_candidate_count"], len(candidates))
        self.assertEqual(selected, [paper_id for _, paper_id in candidates[:10]])
        self.assertEqual(
            self.manifest["reserved_development_ids"]["paper_ids"], selected,
        )

    def test_future_evaluation_candidate_pool_is_disjoint_and_overlap_is_rejected(self):
        reserved = self.manifest["reserved_development_ids"]["paper_ids"]
        eligible_ids = {
            paper_id for paper_id, paper in self.papers.items()
            if paper_id not in self.focal_ids
            and paper["canonical_record"] is not None
            and bool((paper["canonical_record"].get("abstract") or "").strip())
        }
        future_evaluation_candidates = eligible_ids - set(reserved)

        assert_disjoint(reserved, future_evaluation_candidates)
        self.assertEqual(len(future_evaluation_candidates), 2370)
        self.assertFalse(self.manifest["future_evaluation_disjointness"]["future_evaluation_candidates_selected"])
        self.assertEqual(
            self.manifest["future_evaluation_disjointness"]["eligible_count_after_reserving_development_ids"],
            len(future_evaluation_candidates),
        )
        with self.assertRaisesRegex(AssertionError, "development/evaluation ID overlap"):
            assert_disjoint(reserved, [reserved[0]])

    def test_v2_eligible_pool_hash_is_reproducible_and_count_matches(self):
        manifest_v2 = json.loads(MANIFEST_V2_PATH.read_text(encoding="utf-8"))
        pool = manifest_v2["eligible_candidate_pool"]
        eligible_ids = sorted(
            paper_id
            for paper_id, paper in self.papers.items()
            if paper_id not in self.focal_ids
            and paper["canonical_record"] is not None
            and isinstance(paper["canonical_record"].get("abstract"), str)
            and paper["canonical_record"]["abstract"].strip()
        )
        joined_ids = "\n".join(eligible_ids).encode("utf-8")

        self.assertEqual(pool["eligible_candidate_count"], 2380)
        self.assertEqual(pool["eligible_candidate_count"], len(eligible_ids))
        self.assertEqual(pool["sha256"], sha256_bytes(joined_ids))
        self.assertEqual(pool["hash_specification"]["algorithm"], "SHA256")
        self.assertEqual(pool["hash_specification"]["encoding"], "UTF-8")
        self.assertEqual(pool["hash_specification"]["delimiter"], "LF (U+000A) between IDs")
        self.assertEqual(pool["hash_specification"]["trailing_newline"], "none")

    def test_v2_preserves_v1_inputs_and_does_not_claim_evaluation_disjointness(self):
        manifest_v2 = json.loads(MANIFEST_V2_PATH.read_text(encoding="utf-8"))
        self.assertEqual(manifest_v2["inputs"], self.manifest["inputs"])
        self.assertEqual(manifest_v2["source_files"], self.manifest["source_files"])
        self.assertEqual(manifest_v2["selection_rule"], self.manifest["selection_rule"])
        self.assertEqual(manifest_v2["reserved_development_ids"], self.manifest["reserved_development_ids"])
        self.assertEqual(manifest_v2["future_evaluation_disjointness"]["status"], "NOT_ESTABLISHED")
        self.assertFalse(manifest_v2["future_evaluation_disjointness"]["future_evaluation_candidates_selected"])
        self.assertFalse(manifest_v2["final_evaluation_inputs_selected"])
        self.assertFalse(manifest_v2["final_evaluation_inputs_frozen"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
