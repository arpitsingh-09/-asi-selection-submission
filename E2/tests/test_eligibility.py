"""Tests for E2 paper eligibility and timestamp handling.

Uses in-memory paper records. Does not modify the source dataset,
preregistration, embedding cache, or completed scoring results.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from E2 import novelty


UTC = timezone.utc
CUTOFF = datetime(2025, 1, 1, tzinfo=UTC)


def paper(
    paper_id,
    published="2024-06-01T12:00:00Z",
    title="A research paper",
    abstract="A research abstract",
    **extra,
):
    """Create a minimal paper record for testing."""
    return {
        "paper_id": paper_id,
        "published": published,
        "title": title,
        "abstract": abstract,
        **extra,
    }


class TestTimestampParsing(unittest.TestCase):

    def test_z_timestamp_is_utc(self):
        result = novelty._parse_time("2025-01-01T00:00:00Z")
        self.assertEqual(result, CUTOFF)

    def test_timezone_offset_is_converted_to_utc(self):
        result = novelty._parse_time("2025-01-01T05:30:00+05:30")
        self.assertEqual(result, CUTOFF)

    def test_timezone_naive_timestamp_is_interpreted_as_utc(self):
        result = novelty._parse_time("2025-01-01T00:00:00")
        self.assertEqual(result, CUTOFF)

    def test_date_only_string_is_interpreted_as_utc(self):
        result = novelty._parse_time("2025-01-01")
        self.assertEqual(result, CUTOFF)

    def test_invalid_timestamp_raises_value_error(self):
        with self.assertRaises(ValueError):
            novelty._parse_time("not-a-date")


class TestEligiblePapers(unittest.TestCase):

    def get_eligible(self, records, pool_ids, idea_text="An unrelated idea"):
        # Isolate each test from the real paper corpus and cache.
        with patch.object(novelty, "_PAPERS", records):
            return novelty._eligible_papers(pool_ids, CUTOFF, idea_text)

    def test_paper_before_cutoff_is_included(self):
        records = {
            "before": paper("before", "2024-12-31T23:59:59Z")
        }
        result = self.get_eligible(records, ["before"])
        self.assertEqual([p["paper_id"] for p in result], ["before"])

    def test_paper_exactly_at_cutoff_is_excluded(self):
        records = {
            "at": paper("at", "2025-01-01T00:00:00Z")
        }
        self.assertEqual(self.get_eligible(records, ["at"]), [])

    def test_paper_after_cutoff_is_excluded(self):
        records = {
            "after": paper("after", "2025-01-02T00:00:00Z")
        }
        self.assertEqual(self.get_eligible(records, ["after"]), [])

    def test_duplicate_ids_are_returned_only_once(self):
        records = {
            "paper-1": paper("paper-1")
        }
        result = self.get_eligible(
            records, ["paper-1", "paper-1", "paper-1"]
        )
        self.assertEqual(len(result), 1)

    def test_unknown_paper_id_raises_value_error(self):
        with patch.object(novelty, "_PAPERS", {}):
            with self.assertRaises(ValueError):
                novelty._eligible_papers(["missing"], CUTOFF, "An idea")

    def test_missing_publication_date_is_excluded(self):
        records = {
            "missing-date": paper("missing-date", published="")
        }
        self.assertEqual(
            self.get_eligible(records, ["missing-date"]), []
        )

    def test_invalid_publication_date_is_excluded(self):
        records = {
            "invalid-date": paper("invalid-date", published="not-a-date")
        }
        self.assertEqual(
            self.get_eligible(records, ["invalid-date"]), []
        )

    def test_exact_abstract_match_is_excluded_for_real_paper(self):
        idea = "A study of scientific discovery"
        records = {
            "real": paper(
                "real",
                title="A different title",
                abstract=idea,
            )
        }
        self.assertEqual(
            self.get_eligible(records, ["real"], idea_text=idea), []
        )

    def test_exact_text_match_is_allowed_for_synthetic_paper(self):
        idea = "A study of scientific discovery"
        records = {
            "synthetic": paper(
                "synthetic",
                title="A different title",
                abstract=idea,
                synthetic_manipulation=True,
            )
        }
        result = self.get_eligible(
            records, ["synthetic"], idea_text=idea
        )
        self.assertEqual(
            [p["paper_id"] for p in result], ["synthetic"]
        )

    def test_paper_without_usable_text_is_excluded(self):
        records = {
            "empty": paper("empty", title="", abstract="")
        }
        self.assertEqual(self.get_eligible(records, ["empty"]), [])

    def test_pool_ids_must_not_be_a_string(self):
        with patch.object(novelty, "_PAPERS", {}):
            with self.assertRaises(TypeError):
                novelty._eligible_papers("paper-1", CUTOFF, "An idea")


if __name__ == "__main__":
    unittest.main(verbosity=2)
