"""Read-only tests for the final E6 preregistration commit gate."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_protocol import (  # noqa: E402
    PREREGISTRATION_COMMITTED_PATHS,
    validate_preregistration_git_commit,
)


class PreregistrationCommitGateTests(unittest.TestCase):
    def test_statistical_implementation_is_bound_to_preregistration(self):
        self.assertIn("E6/statistical_analysis.py", PREREGISTRATION_COMMITTED_PATHS)
        self.assertIn("E6/STATISTICAL_ANALYSIS.md", PREREGISTRATION_COMMITTED_PATHS)

    def test_current_draft_is_not_accepted_as_preregistered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "E6").mkdir()
            (root / "E6/PREREG.md").write_text("**Preregistration status:** DRAFT — NOT FINALIZED\n")
            errors = validate_preregistration_git_commit(root)
            self.assertTrue(any("not marked FINALIZED" in error for error in errors))

    def test_finalized_document_alone_cannot_bypass_explicit_approval(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "E6").mkdir()
            (root / "E6/PREREG.md").write_text("**Preregistration status:** FINALIZED\n")
            errors = validate_preregistration_git_commit(root)
            self.assertTrue(any("researcher approval" in error for error in errors))

    def test_signed_artifacts_are_required_in_head(self):
        import json
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative in PREREGISTRATION_COMMITTED_PATHS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("**Preregistration status:** FINALIZED\n" if relative == "E6/PREREG.md" else "fixture")
            extra = "E6/data/approved_additional_source.json"
            (root / extra).write_text("source fixture")
            (root / "E6/RESEARCHER_APPROVAL.json").write_text(json.dumps({
                "configuration_signoff": {"artifacts": {extra: "fixture hash"}}}))
            def show(argv, **kwargs):
                relative = argv[-1].split("HEAD:", 1)[1]
                if relative == extra:
                    return subprocess.CompletedProcess(argv, 1, stdout=b"", stderr=b"missing")
                return subprocess.CompletedProcess(argv, 0, stdout=(root / relative).read_bytes(), stderr=b"")
            with patch("validate_protocol.subprocess.run", side_effect=show), patch("researcher_approval.load_approval_errors", return_value=[]):
                errors = validate_preregistration_git_commit(root)
            self.assertTrue(any("not in HEAD: " + extra in error for error in errors))

    def test_requires_each_frozen_file_to_exist_in_head_and_match_working_tree(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative in PREREGISTRATION_COMMITTED_PATHS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                content = ("**Preregistration status:** FINALIZED\n"
                           if relative == "E6/PREREG.md" else relative + "\n")
                path.write_text(content, encoding="utf-8")

            def show(argv, **kwargs):
                relative = argv[-1].split("HEAD:", 1)[1]
                return subprocess.CompletedProcess(argv, 0,
                                                    stdout=(root / relative).read_bytes(),
                                                    stderr=b"")

            with patch("validate_protocol.subprocess.run", side_effect=show), patch("researcher_approval.load_approval_errors", return_value=[]):
                self.assertEqual(validate_preregistration_git_commit(root), [])

            changed = root / "E6/config.json"
            changed.write_text("changed after prereg commit\n", encoding="utf-8")

            def stale_head(argv, **kwargs):
                relative = argv[-1].split("HEAD:", 1)[1]
                blob = b"committed original\n" if relative == "E6/config.json" else (
                    root / relative
                ).read_bytes()
                return subprocess.CompletedProcess(argv, 0, stdout=blob, stderr=b"")

            with patch("validate_protocol.subprocess.run", side_effect=stale_head), patch("researcher_approval.load_approval_errors", return_value=[]):
                errors = validate_preregistration_git_commit(root)
            self.assertTrue(any("differs from working tree: E6/config.json" in error
                                for error in errors))


if __name__ == "__main__":
    unittest.main()
