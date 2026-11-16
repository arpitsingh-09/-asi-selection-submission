import csv
from pathlib import Path
import tempfile
import unittest

from M.prospective_grounding.exploratory_ai_reviews.import_batch import import_batch
from M.prospective_grounding.exploratory_ai_reviews.validate_import import (
    TEMPLATE_PATH,
    expected_pairs,
    validate,
)


class ExploratoryAIBatchImportTests(unittest.TestCase):
    def _batch(self):
        return [{"question_id": qid, "paper_id": pid, "rating": i % 3,
                 "evidence_text": f"  verbatim evidence {i}\nline 2  "}
                for i, (qid, pid) in enumerate(sorted(expected_pairs()))]

    def test_full_batch_imports_verbatim_and_existing_validator_accepts_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "assessments_imported.csv"
            result = import_batch(self._batch(), output_path=output)
            self.assertEqual(result["imported"], 18)
            self.assertTrue(validate(output, require_complete=True)["complete"])
            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["evidence_text"], self._batch()[0]["evidence_text"])
            self.assertEqual(rows[0]["reviewer_type"], "external_ai")
            self.assertEqual(rows[0]["model_identity"], "unknown")

    def test_incomplete_or_duplicate_batch_writes_nothing(self):
        batch = self._batch()[:-1]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "assessments_imported.csv"
            with self.assertRaisesRegex(ValueError, "exactly 18"):
                import_batch(batch, output_path=output)
            self.assertFalse(output.exists())
            batch = self._batch()
            batch[-1] = dict(batch[0])
            with self.assertRaisesRegex(ValueError, "duplicates"):
                import_batch(batch, output_path=output)
            self.assertFalse(output.exists())

    def test_template_itself_remains_blank(self):
        with TEMPLATE_PATH.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 18)
        self.assertTrue(all(row["rating"] == "" and row["evidence_text"] == "" for row in rows))


if __name__ == "__main__":
    unittest.main()
