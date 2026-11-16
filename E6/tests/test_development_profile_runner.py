"""Offline tests for the strict DEVELOPMENT-only runner and D-empty auditor."""

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from development_profile_runner import (
    CONFIG_PATH,
    DevelopmentProfileDEmptyAuditor,
    _load_verified_source_rows,
)
from profile_development_token_budget import load_development_manifest
from question_pipeline import _d_empty_audit_validation_errors


class DevelopmentProfileRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, _ = load_development_manifest()
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_all_ten_source_rows_are_verified_against_e2_records(self):
        sources = _load_verified_source_rows(self.manifest["inputs"])
        self.assertEqual(set(sources), {row["paper_id"] for row in self.manifest["inputs"]})

    def test_auditor_accepts_only_fixed_generic_task_and_binds_removed_evidence(self):
        task = self.config["generic_task_text"]
        auditor = DevelopmentProfileDEmptyAuditor(task)
        abstract = "Development source abstract."
        references = []
        abstract_hash = hashlib.sha256(abstract.encode()).hexdigest()
        references_hash = hashlib.sha256(b"[]").hexdigest()
        result = auditor.audit(
            "development-paper", task,
            {"abstract": abstract, "reference_evidence": references},
            "remove abstract and reference evidence",
        )
        self.assertEqual(result.trust_status, "trusted_development_profile")
        errors = _d_empty_audit_validation_errors(
            result.__dict__, "development-paper", task, abstract_hash,
            references_hash, development_profile_only=True,
        )
        self.assertEqual(errors, [])
        with self.assertRaisesRegex(ValueError, "exact generic task"):
            auditor.audit("development-paper", "paper-specific task", {
                "abstract": abstract, "reference_evidence": references,
            }, "remove abstract and reference evidence")


if __name__ == "__main__":
    unittest.main()
