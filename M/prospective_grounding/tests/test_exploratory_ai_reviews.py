import csv
from pathlib import Path
import tempfile
import unittest

from M.prospective_grounding.exploratory_ai_reviews.validate_import import (
    FIELDS,
    TEMPLATE_PATH,
    validate,
)


class ExploratoryAIReviewImportTests(unittest.TestCase):
    def test_template_has_18_unique_registered_pairs_and_no_imported_reviews(self):
        result = validate(TEMPLATE_PATH)
        self.assertEqual(result, {"expected_pairs": 18, "rows": 18, "imported": 0,
                                  "incomplete_rows": 18, "complete": False})

    def test_complete_fixture_requires_valid_rating_and_evidence(self):
        with TEMPLATE_PATH.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        for row in rows:
            row["rating"] = "1"
            row["evidence_text"] = "supplied evidence text"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            self.assertTrue(validate(path, require_complete=True)["complete"])

    def test_duplicate_pairs_and_out_of_range_ratings_are_rejected(self):
        with TEMPLATE_PATH.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        rows[-1]["question_id"] = rows[0]["question_id"]
        rows[-1]["paper_id"] = rows[0]["paper_id"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "unique"):
                validate(path)

            with TEMPLATE_PATH.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            rows[0]["rating"], rows[0]["evidence_text"] = "3", "evidence"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "0, 1, or 2"):
                validate(path)


if __name__ == "__main__":
    unittest.main()
