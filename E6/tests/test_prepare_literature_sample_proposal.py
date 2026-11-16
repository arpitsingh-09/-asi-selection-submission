"""Offline tests for approval-pending literature sample and review preparation."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_literature_sample_proposal import (
    build_literature_extraction_manifest,
    build_literature_sample_proposal,
    build_proposed_manual_review_worklist,
    canonical_hash,
    extract_proposed_literature_sample,
    verify_sample_proposal,
)


CUTOFF = "2024-09-01T00:00:00Z"


def candidate(index):
    paper_id = f"2501.{index:05d}"
    target_openalex_id = f"https://openalex.org/W{900000 + index}"
    references = []
    edges = []
    for ref_index in range(10):
        openalex_id = f"https://openalex.org/W{index * 100 + ref_index}"
        abstract = f"Reference evidence {index}-{ref_index}."
        source_record = {
            "id": openalex_id,
            "abstract_inverted_index": {
                "Reference": [0], "evidence": [1], f"{index}-{ref_index}.": [2],
            },
        }
        retrieval = {
            "request_url": f"https://api.openalex.org/works/{openalex_id.rsplit('/', 1)[1]}",
            "retrieved_at_utc": "2026-01-01T00:00:00Z",
            "response_sha256": "a" * 64,
        }
        references.append({
            "paper_id": f"openalex:{openalex_id.rsplit('/', 1)[1]}",
            "openalex_id": openalex_id,
            "title": f"Reference {ref_index}",
            "abstract": abstract,
            "source_record": source_record,
            "metadata_retrieval_provenance": retrieval,
        })
        edges.append({
            "openalex_id": openalex_id,
            "edge_verified": True,
            "edge_source_field": "referenced_works",
            "edge_source_target_openalex_id": target_openalex_id,
            "abstract_available": True,
            "metadata_status": "retrieved_with_abstract",
            "source_record_sha256": canonical_hash(source_record),
        })
    target_record = {
        "id": target_openalex_id,
        "ids": {"arxiv": f"https://arxiv.org/abs/{paper_id}"},
        "referenced_works": [edge["openalex_id"] for edge in edges],
    }
    return {
        "input_set_id": "lit-" + paper_id,
        "reference_links_verified": True,
        "reference_link_provenance": {
            "source": "OpenAlex",
            "edge_source_field": "referenced_works",
            "target_openalex_id": target_openalex_id,
        },
        "provenance": {"source": "fixture"},
        "target": {
            "paper_id": paper_id,
            "title": f"Target {index}",
            "abstract": f"Target-only answer text {index}.",
            "published": "2025-01-01T00:00:00Z",
            "paper_url": f"https://arxiv.org/abs/{paper_id}",
            "openalex_target_record": target_record,
        },
        "references": references,
        "citation_edges": edges,
        "excluded_reference_paper_ids": [],
    }


def candidate_manifest(count=120):
    unsigned = {
        "schema_version": "e6-literature-citation-verified-manifest-v1",
        "status": "minimum_met",
        "generator_training_cutoff_utc": CUTOFF,
        "minimum_references_with_abstracts_per_input_set": 10,
        "eligible_input_set_count": count,
        "source_exact_target_count": count,
        "input_sets_selected": False,
        "input_sets_frozen": False,
        "input_sets": [candidate(i) for i in range(1, count + 1)],
    }
    result = dict(unsigned)
    result["manifest_sha256"] = canonical_hash(unsigned)
    return result


class LiteratureSampleProposalTests(unittest.TestCase):
    def test_legacy_proposal_without_exclusion_hashes_is_revalidated(self):
        manifest = candidate_manifest()
        proposal = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
        proposal.pop("exclusion_hashes")
        proposal["proposal_sha256"] = canonical_hash({
            key: value for key, value in proposal.items() if key != "proposal_sha256"})
        self.assertEqual(len(verify_sample_proposal(manifest, proposal)), 100)

    def test_rehashed_policy_or_review_list_changes_are_rejected(self):
        manifest = candidate_manifest()
        for field, value in (("selection_rule_id", "arbitrary"),
                             ("proposed_manual_review_input_set_ids", []),
                             ("proposed_sample_size", 101)):
            proposal = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
            proposal[field] = value
            proposal["proposal_sha256"] = canonical_hash({
                key: item for key, item in proposal.items() if key != "proposal_sha256"})
            with self.assertRaises(ValueError):
                verify_sample_proposal(manifest, proposal)

    def test_proposal_is_deterministic_revalidates_candidates_and_stays_unapproved(self):
        manifest = candidate_manifest()
        first = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
        second = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
        self.assertEqual(first, second)
        self.assertEqual(first["proposal_status"], "pending_researcher_approval")
        self.assertFalse(first["sample_selected"])
        self.assertFalse(first["sample_frozen"])
        self.assertEqual(len(first["proposed_input_set_ids"]), 100)
        self.assertEqual(len(first["proposed_manual_review_input_set_ids"]), 20)
        resolved = verify_sample_proposal(manifest, first)
        self.assertEqual(len(resolved), 100)
        self.assertEqual([row["input_set_id"] for row in resolved],
                         first["proposed_input_set_ids"])

    def test_proposal_is_independent_of_candidate_manifest_row_order(self):
        manifest = candidate_manifest()
        reversed_manifest = dict(manifest)
        reversed_manifest["input_sets"] = list(reversed(manifest["input_sets"]))
        unsigned = {key: value for key, value in reversed_manifest.items()
                    if key != "manifest_sha256"}
        reversed_manifest["manifest_sha256"] = canonical_hash(unsigned)
        first = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
        second = build_literature_sample_proposal(reversed_manifest, sample_size=100, seed=2026)
        self.assertEqual(first["proposed_input_set_ids"], second["proposed_input_set_ids"])

    def test_tampered_or_ineligible_candidate_manifest_is_rejected(self):
        manifest = candidate_manifest()
        manifest["input_sets"][0]["target"]["published"] = "2024-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "manifest hash mismatch"):
            build_literature_sample_proposal(manifest, sample_size=100, seed=2026)

        manifest = candidate_manifest()
        unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        unsigned["input_sets"][0]["target"]["published"] = "2024-01-01T00:00:00Z"
        manifest = dict(unsigned, manifest_sha256=canonical_hash(unsigned))
        with self.assertRaisesRegex(ValueError, "fails eligibility"):
            build_literature_sample_proposal(manifest, sample_size=100, seed=2026)

    def test_mock_extractions_feed_exactly_20_source_preserving_review_forms(self):
        manifest = candidate_manifest()
        proposal = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
        calls = []
        raw = json.dumps({
            "research_question": "Does the treatment change the outcome?",
            "research_question_explicit": True,
            "main_hypothesis": "The treatment increases the outcome.",
            "main_hypothesis_explicit": True,
        })

        def mock_client(stage, prompt):
            calls.append((stage, prompt))
            return raw

        extracted = extract_proposed_literature_sample(
            manifest, proposal, mock_client, model_configuration={"model": "offline-mock"},
        )
        self.assertEqual(len(extracted), 100)
        self.assertEqual(len(calls), 100)
        self.assertTrue(all(row["target_extraction"]["status"] == "succeeded"
                            for row in extracted))
        self.assertTrue(all("Target-only answer text" in prompt for _, prompt in calls))
        extraction_manifest = build_literature_extraction_manifest(
            proposal, extracted, model_configuration={"model": "offline-mock"},
        )
        self.assertEqual(extraction_manifest["status"], "pending_manual_validation")
        self.assertEqual(extraction_manifest["successful_extraction_count"], 100)
        self.assertFalse(extraction_manifest["target_extractions_are_gold_truth"])
        worklist = build_proposed_manual_review_worklist(extracted, proposal)
        self.assertEqual(worklist["status"], "pending_manual_review_and_policy_approval")
        self.assertEqual(len(worklist["reviews"]), 20)
        self.assertTrue(all(not row["manual_check_completed"] for row in worklist["reviews"]))
        self.assertTrue(all(row["target_source_text_sha256"] for row in worklist["reviews"]))
        self.assertEqual(worklist["selection_proposal_sha256"], proposal["proposal_sha256"])

    def test_extraction_and_review_packaging_reject_tampered_proposal(self):
        manifest = candidate_manifest()
        proposal = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
        extracted = [{
            "input_set_id": input_id,
            "target_extraction": {"status": "succeeded", "parsed_output": {}},
            "target_extraction_source_field": "abstract",
            "target": {"paper_id": input_id.removeprefix("lit-") ,
                       "abstract": "Fixture target text."},
        } for input_id in proposal["proposed_input_set_ids"]]
        altered = dict(proposal)
        altered["proposed_input_set_ids"] = list(reversed(proposal["proposed_input_set_ids"]))
        with self.assertRaisesRegex(ValueError, "proposal hash mismatch"):
            build_literature_extraction_manifest(
                altered, extracted, model_configuration={"model": "offline-mock"},
            )
        with self.assertRaisesRegex(ValueError, "proposal hash mismatch"):
            build_proposed_manual_review_worklist(extracted, altered)

    def test_review_worklist_requires_extractions_for_entire_approved_proposal(self):
        manifest = candidate_manifest()
        proposal = build_literature_sample_proposal(manifest, sample_size=100, seed=2026)
        extracted = [{
            "input_set_id": input_id,
            "target_extraction": {"status": "succeeded", "parsed_output": {}},
            "target_extraction_source_field": "abstract",
            "target": {"paper_id": input_id.removeprefix("lit-"),
                       "abstract": "Fixture target text."},
        } for input_id in proposal["proposed_input_set_ids"][:20]]
        with self.assertRaisesRegex(ValueError, "exactly match the proposed sample"):
            build_proposed_manual_review_worklist(extracted, proposal)


if __name__ == "__main__":
    unittest.main()
