"""Tests for source-explicit already-asked question corpus preparation."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_already_asked_corpus import build_question_corpus_audit


class AlreadyAskedCorpusTests(unittest.TestCase):
    def test_accepts_only_explicit_question_fields_and_retains_source_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.jsonl"
            source.write_text(json.dumps({
                "paper_id": "2301.12345",
                "research_question": "Does X affect Y?",
                "title": "Not an asked question",
                "abstract": "This abstract must never be converted into a question.",
            }) + "\n", encoding="utf-8")
            result = build_question_corpus_audit([source])
        self.assertEqual(result["question_count"], 1)
        row = result["questions"][0]
        self.assertEqual(row["question"], "Does X affect Y?")
        provenance = row["source_records"][0]
        self.assertEqual(provenance["source_paper_id"], "2301.12345")
        self.assertEqual(provenance["source_field"], "research_question")
        self.assertEqual(len(provenance["source_record_sha256"]), 64)
        self.assertNotIn("abstract", row["question"])

    def test_titles_abstracts_and_claims_do_not_produce_questions(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.jsonl"
            source.write_text(json.dumps({
                "paper_id": "2301.12345",
                "title": "Does X affect Y?",
                "abstract": "We ask whether X affects Y.",
                "claims": ["Does treatment cause improvement?"],
            }) + "\n", encoding="utf-8")
            result = build_question_corpus_audit([source])
        self.assertEqual(result["question_count"], 0)
        self.assertEqual(result["status"], "blocked_no_explicit_research_questions")
        self.assertEqual(result["questions"], [])

    def test_current_e2_and_development_sources_contain_no_native_questions(self):
        result = build_question_corpus_audit()
        self.assertEqual(result["question_count"], 0)
        self.assertEqual(result["source_record_count"], 0)
        self.assertEqual(len(result["sources"]), 3)
        self.assertTrue(all(len(item["sha256"]) == 64 for item in result["sources"]))
        unsigned = {key: value for key, value in result.items() if key != "manifest_sha256"}
        self.assertEqual(result["manifest_sha256"], __import__(
            "prepare_already_asked_corpus"
        )._canonical_hash(unsigned))


if __name__ == "__main__":
    unittest.main()
