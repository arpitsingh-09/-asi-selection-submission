import unittest

from M.prospective_grounding.workflow import _validate_control_pools, _valid_hash, _time


def _fixture():
    questions = [
        {"question_id": "a", "R": ["a1", "a2", "a3"]},
        {"question_id": "b", "R": ["b1", "b2", "b3"]},
    ]
    decoys = [
        {"question_id": "da", "R": questions[0]["R"]},
        {"question_id": "db", "R": questions[1]["R"]},
    ]
    conditions = []
    for q, other, decoy in ((questions[0], questions[1], decoys[0]),
                            (questions[1], questions[0], decoys[1])):
        qid = q["question_id"]
        conditions.extend([
            {"question_id": qid, "condition": "original", "paper_ids": q["R"]},
            {"question_id": qid, "condition": "empty", "paper_ids": []},
            {"question_id": qid, "condition": "shuffled", "paper_ids": other["R"]},
            {"question_id": qid, "condition": "same_topic_decoy", "paper_ids": q["R"],
             "source_question_id": decoy["question_id"]},
        ])
    return questions, decoys, conditions


class WorkflowSafeguardTests(unittest.TestCase):
    def test_controls_are_bound_to_original_empty_shuffled_and_decoy_pools(self):
        _validate_control_pools(*_fixture())


    def test_wrong_control_pools_are_rejected(self):
        for condition in ("original", "shuffled", "same_topic_decoy"):
            questions, decoys, rows = _fixture()
            row = next(row for row in rows if row["question_id"] == "a" and row["condition"] == condition)
            row["paper_ids"] = ["unregistered-1", "unregistered-2", "unregistered-3"]
            with self.assertRaises(ValueError):
                _validate_control_pools(questions, decoys, rows)


    def test_empty_control_rejects_papers(self):
        questions, decoys, rows = _fixture()
        next(row for row in rows if row["question_id"] == "a" and row["condition"] == "empty")["paper_ids"] = ["a1"]
        with self.assertRaises(ValueError):
            _validate_control_pools(questions, decoys, rows)


    def test_timestamp_and_hash_safeguards(self):
        self.assertIsNotNone(_time("2026-01-01T00:00:00Z").tzinfo)
        self.assertTrue(_valid_hash("sha256:" + "a" * 64))
        with self.assertRaises(ValueError):
            _time("2026-01-01T00:00:00")
        self.assertFalse(_valid_hash("a" * 63))


if __name__ == "__main__":
    unittest.main()
