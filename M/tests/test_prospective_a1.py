import unittest

from M.prospective_a1.workflow import (
    construct_controls, prepare_generation_request, validate_inputs, validate_readiness,
)


def paper(pid, published="2025-01-01T00:00:00Z", available="2025-01-02T00:00:00Z"):
    return {"paper_id": pid, "published_at": published, "available_at": available,
            "source_url": "https://example.org/" + pid, "source_sha256": "a" * 64,
            "source_locator": "record/" + pid, "text": "source abstract"}


class ProspectiveA1Tests(unittest.TestCase):
 def test_request_binds_exact_supplied_inputs_without_invoking_model(self):
    inputs = [paper("p1"), paper("p2"), paper("p3")]
    self.assertEqual(validate_inputs(inputs, "2025-02-01T00:00:00Z"), ["p1", "p2", "p3"])
    out = prepare_generation_request(papers=inputs, model_id="locked-model",
                                     parameters={"temperature": 0}, seed=7)
    self.assertEqual(out["status"], "PREPARED_NOT_GENERATED")
    self.assertNotIn("generated_at", out)
    self.assertEqual([x["paper_id"] for x in out["input_records"]], ["p1", "p2", "p3"])
    self.assertTrue(out["prompt_sha256"])

 def test_request_can_be_prepared_without_inventing_a_generator_lock(self):
    out = prepare_generation_request(papers=[paper("p1"), paper("p2"), paper("p3")])
    self.assertEqual(out["status"], "PREPARED_NOT_GENERATED")
    self.assertEqual(out["model_config_status"], "PENDING")
    self.assertIsNone(out["model_id"])
    self.assertIsNone(out["seed"])


 def test_provenance_and_temporal_gates_reject_invalid_inputs(self):
  for bad in [
    [paper("p1"), paper("p2")],
    [paper("p1"), paper("p2"), paper("p1")],
    [paper("p1", published="2025-02-01T00:00:00Z"), paper("p2"), paper("p3")],
    [paper("p1", available="2025-02-01T00:00:00Z"), paper("p2"), paper("p3")],
    [{**paper("p1"), "source_sha256": "bad"}, paper("p2"), paper("p3")],
    [{k: v for k, v in paper("p1").items() if k != "source_locator"}, paper("p2"), paper("p3")],
  ]:
   with self.subTest(bad=bad), self.assertRaises(ValueError):
    validate_inputs(bad, "2025-02-01T00:00:00Z")


 def test_control_construction_requires_distinct_controls_and_independent_validation(self):
    review = {"decision": "verified_same_topic", "reviewer_id": "reviewer-A",
              "reviewed_at": "2025-03-01T00:00:00Z", "evidence_ref": "source#topic"}
    evidence = {k: {"verified": True, "source_ref": "annotation/" + k}
                for k in ("partial_coverage", "concentrated", "distributed")}
    result = construct_controls(original_ids=["a", "b", "c"], shuffled_ids=["d", "e", "f"],
                                decoy_ids=["g", "h", "i"], decoy_question="Different question?",
                                same_topic_review=review, manipulation_evidence=evidence)
    self.assertEqual(result["empty"], [])
    self.assertEqual(result["shuffled"], ["d", "e", "f"])
    self.assertEqual(result["manipulations"], evidence)
    with self.assertRaisesRegex(ValueError, "independent"):
        construct_controls(original_ids=["a", "b", "c"], shuffled_ids=["d", "e", "f"], decoy_ids=["g", "h", "i"],
                           decoy_question="Q?", same_topic_review={}, manipulation_evidence=evidence)
    with self.assertRaisesRegex(ValueError, "verified concentrated"):
        construct_controls(original_ids=["a", "b", "c"], shuffled_ids=["d", "e", "f"], decoy_ids=["g", "h", "i"],
                           decoy_question="Q?", same_topic_review=review,
                           manipulation_evidence={**evidence, "concentrated": {}})


 def test_readiness_fails_closed_until_every_required_lock_and_authorization_exists(self):
    with self.assertRaises(ValueError) as exc:
        validate_readiness({})
    message = str(exc.exception)
    for gate in ("source provenance", "dated explicit inputs", "model lock", "normalization lock",
                 "controls and manipulations", "independent human/source validation",
                 "committed prospective preregistration", "explicit execution authorization"):
        self.assertIn(gate, message)
    reviewer = {"reviewer_id": "r1", "reviewed_at": "2025-03-01T00:00:00Z",
                "evidence_ref": "source#1", "decision": "verified"}
    validate_readiness({"source_provenance_ref": "manifest.json", "source_provenance_sha256": "a" * 64,
                        "inputs_temporally_valid": True,
                        "model_lock_sha256": "b" * 64, "baseline_lock_sha256": "c" * 64,
                        "normalization_lock_sha256": "d" * 64,
                        "controls_validated": True, "human_validation_complete": True,
                        "human_validation": [reviewer, {**reviewer, "reviewer_id": "r2"}],
                        "prereg_commit": "e" * 40, "execution_authorization_ref": "approval-record"})


if __name__ == "__main__":
    unittest.main()
