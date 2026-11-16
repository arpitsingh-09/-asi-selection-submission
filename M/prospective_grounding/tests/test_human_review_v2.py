import json
from pathlib import Path
import unittest

from M.prospective_grounding.human_review_v2.prepare_packet import OUTPUT_ROOT
from M.prospective_grounding.human_review_v2.validate_packet import validate


class HumanReviewPacketV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        validate(OUTPUT_ROOT)

    def test_both_reviewer_copies_contain_registered_scale(self):
        for reviewer in ("reviewer_1", "reviewer_2"):
            packet = (OUTPUT_ROOT / reviewer / "review_packet.md").read_text()
            self.assertIn("0 — Unrelated/no grounding", packet)
            self.assertIn("1 — Topical, not directly grounding", packet)
            self.assertIn("2 — Directly relevant evidence", packet)

    def test_blinded_packet_data_has_four_questions_and_six_associations(self):
        packet = json.loads((OUTPUT_ROOT / "blinded_packet_data.json").read_text())
        self.assertEqual(len(packet["questions"]), 4)
        self.assertEqual(len(packet["associations"]), 6)
        self.assertEqual(len(packet["rating_rows"]), 18)

    def test_private_mapping_is_separate_from_reviewer_folders(self):
        mapping_path = OUTPUT_ROOT / "private_mapping.json"
        mapping = json.loads(mapping_path.read_text())
        self.assertEqual(len(mapping["questions"]), 4)
        for reviewer in ("reviewer_1", "reviewer_2"):
            for path in (OUTPUT_ROOT / reviewer).iterdir():
                self.assertNotEqual(path.resolve(), mapping_path.resolve())
                self.assertNotIn("private_mapping", path.read_text())


if __name__ == "__main__":
    unittest.main()
