import unittest

from M.a1_replication.controls import ControlError, build_controls, score_control, score_with_e2


def paper(pid, date):
    return {"paper_id": pid, "published": date}


def instance(pid, date, question, inputs):
    return {"paper_id": pid, "published": date, "question": question,
            "input_paper_ids": inputs}


class A1ControlTests(unittest.TestCase):
    def setUp(self):
        self.papers = {
            "p1": paper("p1", "2024-01-01T00:00:00Z"),
            "p2": paper("p2", "2024-02-01T00:00:00Z"),
            "p3": paper("p3", "2024-03-01T00:00:00Z"),
            "p4": paper("p4", "2025-08-20T00:00:00Z"),
            "future": paper("future", "2025-10-01T00:00:00Z"),
        }
        self.focal = instance("focal", "2025-09-01T00:00:00Z", "Focal question?", ["p1", "p2"])
        self.other = [
            instance("shuffle", "2025-08-01T00:00:00Z", "Another question?", ["p2", "p3", "future"]),
            instance("decoy", "2025-08-15T00:00:00Z", "Different same-topic question?", []),
        ]

    def test_controls_filter_future_inputs_and_keep_focal_pairing(self):
        controls = build_controls(focal=self.focal, original_input_ids=["p1", "p2", "future", "focal"],
                                  papers=self.papers, other_instances=self.other)
        self.assertEqual([c["condition"] for c in controls],
                         ["original", "empty", "shuffled", "same_topic_decoy"])
        self.assertEqual([c["input_paper_ids"] for c in controls if "input_paper_ids" in c],
                         [["p1", "p2"], [], ["p2", "p3"]])
        self.assertTrue(all(c["pair_id"] == "focal" and c["focal_paper_id"] == "focal" for c in controls))
        self.assertNotIn("future", sum((c["input_paper_ids"] for c in controls
                                        if "input_paper_ids" in c), []))
        decoy = controls[3]
        self.assertEqual(decoy["status"], "unavailable")
        self.assertNotIn("question", decoy)
        self.assertNotIn("input_paper_ids", decoy)
        self.assertIn("Amendment 003", decoy["reason"])

    def test_control_ids_are_deterministic(self):
        args = dict(focal=self.focal, original_input_ids=["p1", "p2"], papers=self.papers,
                    other_instances=self.other)
        self.assertEqual([x["record_id"] for x in build_controls(**args)],
                         [x["record_id"] for x in build_controls(**args)])

    def test_empty_pool_is_explicitly_undefined_without_calling_scorer(self):
        controls = build_controls(focal=self.focal, original_input_ids=["p1", "p2"],
                                  papers=self.papers, other_instances=self.other)
        result = score_with_e2(controls[1], claims=[], cutoff=self.focal["published"])
        self.assertEqual(result["status"], "undefined")
        self.assertIn("no E2 novelty score", result["reason"])

    def test_nonempty_score_adapter_forwards_the_existing_e2_arguments(self):
        controls = build_controls(focal=self.focal, original_input_ids=["p1", "p2"],
                                  papers=self.papers, other_instances=self.other)
        called = {}
        def scorer(**kwargs):
            called.update(kwargs)
            return {"Y": .1, "density": 2.0, "N": .2, "yours": .125}
        result = score_control(controls[0], scorer, claims=["claim"], cutoff=self.focal["published"])
        self.assertEqual(result["status"], "scored")
        self.assertEqual(called, {"idea_text": "Focal question?", "claims": ["claim"],
                                  "pool_ids": ["p1", "p2"], "t": self.focal["published"]})

    def test_unavailable_decoy_cannot_be_scored(self):
        controls = build_controls(focal=self.focal, original_input_ids=["p1", "p2"],
                                  papers=self.papers, other_instances=self.other)
        with self.assertRaisesRegex(ControlError, "unavailable and cannot be scored"):
            score_control(controls[3], lambda **kwargs: self.fail("scorer must not run"),
                          claims=["claim"], cutoff=self.focal["published"])

    def test_rejects_unknown_inputs_and_requires_temporally_eligible_shuffle(self):
        with self.assertRaisesRegex(ControlError, "unknown input"):
            build_controls(focal=self.focal, original_input_ids=["missing"], papers=self.papers,
                           other_instances=self.other)
        with self.assertRaisesRegex(ControlError, "no distinct temporally eligible shuffled"):
            build_controls(focal=self.focal, original_input_ids=["p1", "p2"], papers=self.papers,
                           other_instances=[instance("only-future", "2025-08-01T00:00:00Z",
                                                     "Future-only?", ["future"])])


if __name__ == "__main__":
    unittest.main()
