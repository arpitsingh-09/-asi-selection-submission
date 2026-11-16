"""Mock fixtures for E6 literature-testbed eligibility and completeness."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_literature_testbed import (  # noqa: E402
    audit_manual_check_coverage,
    audit_candidate_input_sets,
    audit_raw_corpus,
    acquire_openalex_reference_candidate,
    acquire_openalex_candidate_for_e2_record,
    acquire_openalex_candidate_pool_from_e2,
    build_manual_extraction_review_worklist,
    build_orchestrator_input_manifest,
    build_candidate_input_set,
    complete_manual_extraction_review,
    extract_literature_target_annotations,
    load_orchestrator_experiment_inputs,
    validate_literature_input_set,
    write_manifest_exclusive,
)
from citation_sources import CitationApiError  # noqa: E402


CUTOFF = "2025-01-01T00:00:00Z"


def target(paper_id="2501.12345", published="2026-01-02T00:00:00Z"):
    return {"paper_id": paper_id, "abstract": "A target abstract.", "published": published}


def refs(count=10):
    return [{
        "paper_id": f"2401.{index:05d}",
        "title": f"Reference paper {index}",
        "abstract": f"Reference abstract {index}.",
    } for index in range(1, count + 1)]


def candidate(input_set_id="set-1", target_record=None, reference_records=None):
    return {
        "input_set_id": input_set_id,
        "target": target_record or target(),
        "references": reference_records if reference_records is not None else refs(),
        "reference_links_verified": True,
        "reference_link_provenance": {"source": "fixture citation graph"},
    }


class LiteratureInputEligibilityTests(unittest.TestCase):
    def test_openalex_pool_stops_on_429_instead_of_repeating_for_remaining_targets(self):
        class LimitedAdapter:
            def resolve_by_arxiv_external_id(self, value):
                raise CitationApiError("HTTP 429", [{"status_code": 429}], http_status=429)

        rows = [
            {"paper_id": "2501.12345", "abstract": "A", "published": "2025-01-01T00:00:00Z"},
            {"paper_id": "2501.12346", "abstract": "B", "published": "2025-01-02T00:00:00Z"},
        ]
        with self.assertRaises(CitationApiError) as raised:
            acquire_openalex_candidate_pool_from_e2(
                LimitedAdapter(), rows, focal_exclusion_ids=[],
                development_manifest={"reserved_development_ids": {"paper_ids": []}},
                generator_training_cutoff_utc="2024-09-01T00:00:00Z", max_targets=2,
            )
        self.assertEqual(raised.exception.http_status, 429)

    @staticmethod
    def _fixed_extraction(text):
        prompt_path = Path(__file__).resolve().parents[2] / "prompts/e6/09_target_extraction.txt"
        template = prompt_path.read_text(encoding="utf-8")
        return {
            "stage": "reference_target_extraction",
            "status": "succeeded",
            "parsed_output": {
                "research_question": "Does A affect B?", "research_question_explicit": True,
                "main_hypothesis": "A increases B.", "main_hypothesis_explicit": True,
            },
            "evaluation_input": {
                "target_paper_text": text,
                "rendered_prompt": template.replace("{{TARGET_PAPER_TEXT}}", text),
            },
            "provenance": {
                "prompt_path": "prompts/e6/09_target_extraction.txt",
                "prompt_sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
            },
        }

    def test_fixed_prompt_extraction_uses_supplied_text_and_retains_result(self):
        client_calls = []
        reply = json.dumps({
            "research_question": "Does A affect B?", "research_question_explicit": True,
            "main_hypothesis": "A increases B.", "main_hypothesis_explicit": True,
        })

        def client(stage, prompt):
            client_calls.append((stage, prompt))
            return reply

        candidate_row = candidate()
        candidate_row["target"]["full_text"] = "Full target text fixture."
        result = extract_literature_target_annotations(
            [candidate_row], client, model_configuration={"model": "mock"},
        )[0]
        self.assertEqual(result["target_extraction_source_field"], "full_text")
        self.assertEqual(result["target_extraction"]["parsed_output"]["research_question"],
                         "Does A affect B?")
        self.assertEqual(client_calls[0][0], "reference_target_extraction")
        self.assertIn("Full target text fixture.", client_calls[0][1])

    def test_review_worklist_requires_explicit_20_and_records_manual_checks(self):
        candidates = []
        for index in range(20):
            row = candidate(f"review-{index}", target(f"2501.{index + 1:05d}"))
            row["target_extraction"] = {
                "status": "succeeded", "parsed_output": {
                    "research_question": "RQ", "research_question_explicit": True,
                    "main_hypothesis": None, "main_hypothesis_explicit": False,
                },
            }
            row["target_extraction_source_field"] = "abstract"
            candidates.append(row)
        worklist = build_manual_extraction_review_worklist(
            candidates, [row["input_set_id"] for row in candidates],
        )
        self.assertEqual(len(worklist["reviews"]), 20)
        self.assertFalse(worklist["reviews"][0]["manual_check_completed"])
        completed = complete_manual_extraction_review(
            worklist["reviews"][0], reviewer_id="reviewer-1",
            reviewed_at_utc="2026-01-02T03:04:05Z",
            research_question_extraction_accurate=True,
            main_hypothesis_extraction_accurate=True,
            research_question_explicitness_accurate=True,
            main_hypothesis_explicitness_accurate=True,
            reviewer_notes="checked against paper text",
        )
        self.assertTrue(completed["manual_check_completed"])
        self.assertEqual(completed["reviewer_id"], "reviewer-1")
        self.assertEqual(audit_manual_check_coverage([completed])["completed_unique_input_sets"], 1)
        with self.assertRaisesRegex(ValueError, "exactly 20"):
            build_manual_extraction_review_worklist(candidates, ["review-0"])

    def test_orchestrator_manifest_is_deterministic_validated_and_dev_disjoint(self):
        row = candidate("manifest-set", target("2501.12345"))
        row["target_extraction"] = self._fixed_extraction(row["target"]["abstract"])
        row["target_extraction_source_field"] = "abstract"
        kwargs = {
            "candidates": [row], "generator_training_cutoff_utc": CUTOFF,
            "domain_and_task_by_input_set": {"manifest-set": "Caller supplied task."},
        }
        first = build_orchestrator_input_manifest(**kwargs)
        second = build_orchestrator_input_manifest(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["prepared_input_set_count"], 1)
        self.assertEqual(first["status"], "minimum_not_met")
        self.assertFalse(first["input_sets_selected"])
        record = first["inputs"][0]
        self.assertEqual(record["experiment_input"]["paper_id"], "2501.12345")
        self.assertEqual(len(record["experiment_input"]["reference_evidence"]), 10)
        self.assertEqual(record["experiment_input"]["evidence"],
                         "\n\n".join(ref["abstract"] for ref in record["target_references"]))
        self.assertNotIn(row["target"]["abstract"], record["experiment_input"]["evidence"])
        self.assertFalse(record["experiment_input"]["provenance"][
            "target_abstract_is_generation_input"])
        self.assertEqual(len(record["experiment_input_sha256"]), 64)
        self.assertNotIn("main_hypothesis", record["experiment_input"])
        self.assertNotIn("A increases B.", json.dumps(record["experiment_input"]))
        orchestrator_inputs = load_orchestrator_experiment_inputs(first)
        self.assertEqual(len(orchestrator_inputs), 1)
        self.assertEqual(orchestrator_inputs[0].paper_id, "2501.12345")
        self.assertEqual(orchestrator_inputs[0].split, "EVALUATION")

        tampered = dict(first)
        tampered["inputs"] = []
        with self.assertRaisesRegex(ValueError, "manifest hash"):
            load_orchestrator_experiment_inputs(tampered)

        blocked = build_orchestrator_input_manifest(
            [row], CUTOFF, domain_and_task_by_input_set={"manifest-set": "task"},
            development_manifest={"reserved_development_ids": {"paper_ids": ["2501.12345"]}},
        )
        self.assertEqual(blocked["prepared_input_set_count"], 0)
        self.assertTrue(any("reserved" in error for error in blocked["candidate_audits"][0]["errors"]))

    def test_manifest_writer_refuses_to_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "manifest.json"
            destination.write_text("previous", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                write_manifest_exclusive(destination, {"schema_version": "fixture"})
            self.assertEqual(destination.read_text(encoding="utf-8"), "previous")

    @staticmethod
    def _openalex_reference_fixture(index, *, arxiv_id=None):
        source_ids = {"doi": f"https://doi.org/10.1234/ref{index}"}
        if arxiv_id is not None:
            source_ids["arxiv"] = arxiv_id
        return {
            "id": f"https://openalex.org/W{index}",
            "title": f"Reference paper {index}",
            "publication_date": "2024-06-01",
            "ids": source_ids,
            "abstract_inverted_index": {f"abstract{index}": [0], "text.": [1]},
        }

    def test_openalex_acquisition_builds_development_only_eligible_candidate(self):
        target_response = {
            "raw_response": {
                "id": "https://openalex.org/WTARGET",
                "referenced_works": [f"https://openalex.org/W{i}" for i in range(1, 11)],
            }
        }
        records = {f"W{i}": self._openalex_reference_fixture(
            i, arxiv_id=f"2401.{i:05d}"
        ) for i in range(1, 11)}
        retrieval = {
            "records_by_openalex_id": records,
            "missing_openalex_ids": [],
            "request_count": 1,
        }
        links = {"source": "verified fixture graph", "edge_ids": ["edge-1"]}

        with patch("citation_sources.fetch_openalex_works_batched", return_value=retrieval) as fetch:
            result = acquire_openalex_reference_candidate(
                object(), target_response, target(), input_set_id="set-success",
                generator_training_cutoff_utc=CUTOFF,
                reference_links_verified=True,
                reference_link_provenance=links,
            )

        fetch.assert_called_once()
        self.assertEqual(result["status"], "development_only_not_frozen")
        self.assertEqual(result["eligibility_audit"]["status"], "eligible_candidate")
        self.assertEqual(result["eligibility_audit"]["unique_reference_with_abstract_count"], 10)
        self.assertEqual(result["retrieval"], {
            "reference_identifier_count": 10,
            "metadata_retrieved_count": 10,
            "missing_metadata_count": 0,
            "request_count": 1,
        })
        candidate_record = result["candidate"]
        self.assertEqual(candidate_record["references"][0]["citing_target_openalex_id"],
                         "https://openalex.org/WTARGET")
        self.assertEqual(candidate_record["references"][0]["citation_edge_source_field"],
                         "referenced_works")
        self.assertEqual(candidate_record["provenance"]["reference_edge_source"],
                         "OpenAlex referenced_works")
        self.assertEqual(candidate_record["reference_link_provenance"], links)
        self.assertEqual(candidate_record["target"]["source_record"], target_response["raw_response"])
        self.assertEqual(candidate_record["source_record_hashes"]["target"]["status"], "hashed")
        self.assertNotIn("source_record", target_response["raw_response"])
        self.assertFalse(candidate_record["eligibility_audit"].get("input_set_selected", False))
        self.assertFalse(candidate_record["eligibility_audit"].get("input_set_frozen", False))
        self.assertFalse(candidate_record["provenance"]["dataset_selected"])
        self.assertFalse(candidate_record["provenance"]["dataset_frozen"])

    def test_e2_to_openalex_acquisition_preserves_real_source_provenance(self):
        e2_record = {
            "paper_id": "2501.12345v2", "title": "Target fixture",
            "abstract": "A real-source-shaped target abstract.",
            "published": "2025-01-02T00:00:00Z",
            "paper_url": "https://arxiv.org/abs/2501.12345v2",
            "source": "arXiv API", "retrieved_at_utc": "2026-01-02T00:00:00Z",
        }
        openalex_target = {
            "id": "https://openalex.org/WTARGET", "title": "Target fixture",
            "publication_date": "2025-01-02",
            "ids": {"doi": "https://doi.org/10.24963/ijcai.2025/279",
                    "openalex": "https://openalex.org/WTARGET"},
            "locations": [{"landing_page_url": "https://arxiv.org/abs/2501.12345"}],
            "referenced_works": [f"https://openalex.org/W{i}" for i in range(1, 11)],
        }

        class Adapter:
            def resolve_by_arxiv_external_id(self, value):
                return {
                    "source": "OpenAlex", "api_version": "fixture-version",
                    "request_url": "https://api.openalex.org/works?filter=locations.landing_page_url:https://arxiv.org/abs/2501.12345",
                    "retrieved_at_utc": "2026-01-03T00:00:00Z", "http_status": 200,
                    "candidate_matches": [openalex_target],
                }

        source_records = {f"W{i}": self._openalex_reference_fixture(
            i, arxiv_id=f"2401.{i:05d}"
        ) for i in range(1, 11)}
        retrieval = {
            "records_by_openalex_id": source_records, "missing_openalex_ids": [],
            "request_count": 1, "responses": [{
                "source": "OpenAlex", "api_version": "fixture-version",
                "request_url": "https://api.openalex.org/works?filter=openalex:W1%7CW2",
                "retrieved_at_utc": "2026-01-03T00:01:00Z", "http_status": 200,
                "cache_hit": False,
                "raw_response": {"results": list(source_records.values())},
            }],
        }
        with patch("citation_sources.fetch_openalex_works_batched", return_value=retrieval):
            acquired = acquire_openalex_candidate_for_e2_record(
                Adapter(), e2_record, input_set_id="lit-2501.12345",
                generator_training_cutoff_utc=None,
            )

        candidate_record = acquired["candidate"]
        self.assertEqual(acquired["status"], "provisional_candidate_acquired")
        self.assertEqual(candidate_record["target"]["paper_id"], "2501.12345v2")
        self.assertEqual(candidate_record["target"]["published"], "2025-01-02T00:00:00Z")
        self.assertEqual(candidate_record["target"]["openalex_target_source_url"],
                         "https://openalex.org/WTARGET")
        self.assertEqual(candidate_record["provenance"]["target_edge_retrieval"]["request_url"],
                         "https://api.openalex.org/works?filter=locations.landing_page_url:https://arxiv.org/abs/2501.12345")
        self.assertEqual(candidate_record["references"][0]["metadata_retrieval_provenance"][
            "retrieved_at_utc"], "2026-01-03T00:01:00Z")
        self.assertTrue(candidate_record["references"][0]["abstract"].strip())
        self.assertEqual(candidate_record["source_record_hashes"]["openalex_target"]["status"],
                         "hashed")
        self.assertEqual(candidate_record["source_record_hashes"]["references"][0]["status"],
                         "hashed")
        self.assertFalse(candidate_record["reference_links_verified"])

    def test_openalex_e2_target_pool_excludes_focal_and_development_ids(self):
        rows = [
            {"paper_id": "2501.00001v1", "abstract": "A", "published": "2025-01-01T00:00:00Z"},
            {"paper_id": "2501.00002v1", "abstract": "B", "published": "2025-01-01T00:00:00Z"},
            {"paper_id": "2501.00003v1", "abstract": "C", "published": "2025-01-01T00:00:00Z"},
        ]

        class NoMatchAdapter:
            def __init__(self):
                self.lookups = []

            def resolve_by_arxiv_external_id(self, value):
                self.lookups.append(value)
                return {"candidate_matches": [], "request_url": "fixture-url"}

        adapter = NoMatchAdapter()
        pool = acquire_openalex_candidate_pool_from_e2(
            adapter, rows, focal_exclusion_ids={"2501.00003"},
            development_manifest={"reserved_development_ids": {"paper_ids": ["2501.00002"]}},
            generator_training_cutoff_utc=None, max_targets=10,
        )
        self.assertEqual(pool["candidate_target_count_after_exclusions"], 1)
        self.assertEqual(adapter.lookups, ["2501.00001"])
        self.assertEqual(pool["unresolved_target_matches"], 1)

    def test_openalex_partial_metadata_preserves_missing_ids_and_counts_only_eligible_refs(self):
        target_response = {
            "raw_response": {
                "id": "https://openalex.org/WTARGET",
                "referenced_works": [f"https://openalex.org/W{i}" for i in range(1, 12)],
            }
        }
        records = {f"W{i}": self._openalex_reference_fixture(
            i, arxiv_id=f"2401.{i:05d}"
        ) for i in range(1, 10)}
        # Retrieved DOI-only metadata and absent metadata must both remain visible,
        # but neither can satisfy the arXiv-ID-and-abstract eligibility rule.
        records["W10"] = self._openalex_reference_fixture(10)
        records["W10"].pop("abstract_inverted_index")
        retrieval = {
            "records_by_openalex_id": records,
            "missing_openalex_ids": ["W11"],
            "request_count": 1,
        }

        with patch("citation_sources.fetch_openalex_works_batched", return_value=retrieval):
            result = acquire_openalex_reference_candidate(
                object(), target_response, target(), input_set_id="set-partial",
                generator_training_cutoff_utc=CUTOFF,
                reference_links_verified=True,
                reference_link_provenance={"source": "partial fixture graph"},
            )

        candidate_record = result["candidate"]
        self.assertEqual(result["status"], "development_only_not_frozen")
        self.assertEqual(candidate_record["source_record_hashes"]["target"]["status"], "hashed")
        self.assertEqual(candidate_record["source_record_hashes"]["references"][-1]["status"],
                         "missing")
        self.assertIsNone(candidate_record["source_record_hashes"]["references"][-1]["sha256"])
        self.assertEqual(candidate_record["source_record_hashes"]["references"][0]["status"],
                         "hashed")
        self.assertEqual(result["retrieval"]["missing_metadata_count"], 1)
        self.assertEqual(candidate_record["provenance"]["missing_openalex_ids"], ["W11"])
        self.assertEqual(candidate_record["provenance"]["reference_records_retrieved"], 10)
        self.assertEqual(candidate_record["references"][-1]["metadata_status"], "not_retrieved")
        self.assertEqual(candidate_record["references"][-1]["missing_reason"],
                         "OpenAlex work record not returned")
        self.assertEqual(candidate_record["references"][-2]["metadata_status"],
                         "retrieved_without_abstract")
        audit = result["eligibility_audit"]
        self.assertEqual(audit["unique_reference_with_abstract_count"], 9)
        self.assertEqual(audit["status"], "ineligible_or_unresolved")
        self.assertTrue(any("only 9 unique references have abstracts" in error
                            for error in audit["errors"]))
        self.assertEqual(candidate_record["reference_link_provenance"],
                         {"source": "partial fixture graph"})
        self.assertFalse(candidate_record["provenance"]["dataset_selected"])
        self.assertFalse(candidate_record["provenance"]["dataset_frozen"])

    def test_complete_post_cutoff_candidate_passes_without_selection(self):
        record = candidate()
        result = validate_literature_input_set(record, CUTOFF)
        self.assertEqual(result["status"], "eligible_candidate")
        self.assertTrue(result["target_post_cutoff"])
        self.assertEqual(result["unique_reference_with_abstract_count"], 10)

    def test_openalex_work_ids_are_valid_unique_reference_ids(self):
        refs_by_openalex = [{
            "paper_id": f"openalex:W{index}",
            "abstract": f"OpenAlex reference abstract {index}",
        } for index in range(1, 11)]
        record = candidate(reference_records=refs_by_openalex)
        result = validate_literature_input_set(record, CUTOFF)
        self.assertEqual(result["status"], "eligible_candidate")
        self.assertEqual(result["unique_reference_with_abstract_count"], 10)

    def test_reference_entries_without_abstract_do_not_invalidate_10_abstract_refs(self):
        reference_rows = refs(10) + [{"paper_id": "openalex:W999", "abstract": None}]
        result = validate_literature_input_set(candidate(reference_records=reference_rows), CUTOFF)
        self.assertEqual(result["status"], "eligible_candidate")
        self.assertEqual(result["unique_reference_with_abstract_count"], 10)
        self.assertEqual(result["references_without_abstract_count"], 1)

    def test_missing_cutoff_date_or_abstract_blocks_eligibility(self):
        result = validate_literature_input_set(candidate(), None)
        self.assertEqual(result["status"], "ineligible_or_unresolved")
        self.assertTrue(any("cutoff is unresolved" in error for error in result["errors"]))

        result = validate_literature_input_set(
            candidate(target_record=target(published="2026-01-02")), CUTOFF,
        )
        self.assertTrue(any("lacks timezone" in error for error in result["errors"]))

        missing_abstract_target = target()
        missing_abstract_target["abstract"] = "  "
        result = validate_literature_input_set(candidate(target_record=missing_abstract_target), CUTOFF)
        self.assertTrue(any("target abstract" in error for error in result["errors"]))

    def test_invalid_minimum_reference_count_is_reported(self):
        for value in (0, -1, True, 1.5):
            result = validate_literature_input_set(candidate(), CUTOFF, minimum_references=value)
            self.assertEqual(result["status"], "invalid")
            self.assertIn("minimum_references must be a positive integer", result["errors"])

    def test_timestamps_with_offsets_are_compared_as_utc(self):
        record = candidate(target_record=target(published="2026-01-02T05:30:00+05:30"))
        result = validate_literature_input_set(record, "2025-01-01T05:30:00+05:30")
        self.assertEqual(result["status"], "eligible_candidate")
        self.assertTrue(result["target_post_cutoff"])
        self.assertEqual(result["target_published_utc"], "2026-01-02T00:00:00Z")
        self.assertEqual(result["training_cutoff_utc"], "2025-01-01T00:00:00Z")

    def test_duplicate_self_reference_and_empty_abstract_do_not_count(self):
        references = refs(9)
        references.append(dict(references[0]))
        references.append({"paper_id": "2401.00010", "abstract": ""})
        references.append({"paper_id": "2501.12345", "abstract": "self"})
        references.append({"paper_id": "not-an-arxiv-id", "abstract": "bad id"})
        result = validate_literature_input_set(candidate(reference_records=references), CUTOFF)
        self.assertEqual(result["unique_reference_with_abstract_count"], 9)
        self.assertEqual(result["duplicate_reference_ids"], ["2401.00001"])
        self.assertGreaterEqual(len(result["invalid_references"]), 3)
        self.assertEqual(result["status"], "ineligible_or_unresolved")

    def test_candidate_builder_retains_invalid_records_and_marks_exposure_unverified(self):
        bad_refs = refs(2)
        built = build_candidate_input_set(
            "set-x", target(), bad_refs, CUTOFF,
            source_provenance={"source": "mock"},
            reference_links_verified=True,
            reference_link_provenance={"source": "fixture citation graph"},
        )
        self.assertEqual(len(built["references"]), 2)
        self.assertIn("unverified", built["exposure_status"])
        self.assertEqual(built["eligibility_audit"]["status"], "ineligible_or_unresolved")

    def test_candidate_builder_preserves_malformed_containers_for_audit(self):
        built = build_candidate_input_set(
            "set-malformed", None, None, CUTOFF,
            source_provenance=None,
            reference_links_verified=False,
            reference_link_provenance=None,
        )
        self.assertIsNone(built["target"])
        self.assertIsNone(built["references"])
        self.assertEqual(built["source_record_hashes"]["target"],
                         {"status": "missing", "sha256": None})
        self.assertEqual(built["source_record_hashes"]["references"], [])
        self.assertEqual(built["eligibility_audit"]["status"], "ineligible_or_unresolved")
        self.assertTrue(any("target must be an object" in error
                            for error in built["eligibility_audit"]["errors"]))

    def test_candidate_builder_records_deterministic_abstract_evidence_hashes(self):
        target_record = target()
        target_record["abstract"] = "  Exact target abstract.\n"
        references = [
            {"paper_id": "2401.00001v2", "abstract": "Reference abstract."},
            {"paper_id": "not-an-arxiv-id", "abstract": None},
        ]

        built = build_candidate_input_set(
            "hash-set", target_record, references, CUTOFF,
            source_provenance={"source": "fixture"},
            reference_links_verified=True,
            reference_link_provenance={"source": "fixture graph"},
        )

        hashes = built["evidence_hashes"]
        self.assertEqual(hashes["algorithm"], "sha256")
        self.assertEqual(hashes["text_encoding"], "utf-8")
        self.assertEqual(hashes["target_abstract_sha256"], hashlib.sha256(
            b"  Exact target abstract.\n"
        ).hexdigest())
        self.assertEqual(hashes["reference_abstracts"], [
            {
                "reference_index": 0,
                "canonical_paper_id": "2401.00001",
                "abstract_sha256": hashlib.sha256(b"Reference abstract.").hexdigest(),
            },
            {
                "reference_index": 1,
                "canonical_paper_id": None,
                "abstract_sha256": None,
            },
        ])

    def test_candidate_builder_hashes_source_records_deterministically_and_detects_changes(self):
        target_record = target()
        target_source = {"z_field": "last", "a_field": "first", "unicode": "café"}
        target_record["source_record"] = target_source
        references = [{
            "paper_id": "2401.00001",
            "abstract": "Reference abstract.",
            "source_record": {"title": "Reference", "id": "W1"},
        }]
        first = build_candidate_input_set(
            "source-hash-set", target_record, references, CUTOFF,
            source_provenance={"source": "fixture"},
            reference_links_verified=True,
            reference_link_provenance={"source": "fixture graph"},
        )

        expected_target_json = json.dumps(
            target_source, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        expected_reference_json = json.dumps(
            references[0]["source_record"], ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        self.assertEqual(first["source_record_hashes"]["target"]["sha256"],
                         hashlib.sha256(expected_target_json).hexdigest())
        self.assertEqual(first["source_record_hashes"]["references"][0]["sha256"],
                         hashlib.sha256(expected_reference_json).hexdigest())
        self.assertEqual(first["source_record_hashes"]["target"]["status"], "hashed")
        self.assertEqual(first["target"]["source_record"], target_source)
        self.assertEqual(first["references"][0]["source_record"], references[0]["source_record"])

        reordered_target = target()
        reordered_target["source_record"] = {"unicode": "café", "a_field": "first", "z_field": "last"}
        reordered_reference = [{
            "paper_id": "2401.00001",
            "abstract": "Reference abstract.",
            "source_record": {"id": "W1", "title": "Reference"},
        }]
        reordered = build_candidate_input_set(
            "source-hash-set", reordered_target, reordered_reference, CUTOFF,
            source_provenance={"source": "fixture"},
            reference_links_verified=True,
            reference_link_provenance={"source": "fixture graph"},
        )
        self.assertEqual(first["source_record_hashes"], reordered["source_record_hashes"])

        changed_target = target()
        changed_target["source_record"] = {**target_source, "a_field": "changed"}
        changed_reference = [{**references[0], "source_record": {"id": "W1", "title": "Changed"}}]
        changed = build_candidate_input_set(
            "source-hash-set", changed_target, changed_reference, CUTOFF,
            source_provenance={"source": "fixture"},
            reference_links_verified=True,
            reference_link_provenance={"source": "fixture graph"},
        )
        self.assertNotEqual(first["source_record_hashes"]["target"]["sha256"],
                            changed["source_record_hashes"]["target"]["sha256"])
        self.assertNotEqual(first["source_record_hashes"]["references"][0]["sha256"],
                            changed["source_record_hashes"]["references"][0]["sha256"])

    def test_mock_pool_completeness_reports_100_without_sampling_or_freezing(self):
        rows = [candidate(f"fixture-{index}", target(f"2501.{index:05d}"))
                for index in range(1, 101)]
        report = audit_candidate_input_sets(rows, CUTOFF)
        self.assertEqual(report["eligible_candidate_input_set_count"], 100)
        self.assertEqual(report["status"], "minimum_met")
        self.assertFalse(report["input_sets_selected"])
        self.assertFalse(report["input_sets_frozen"])

    def test_duplicate_input_set_ids_do_not_inflate_unique_candidate_count(self):
        rows = [candidate("same-id"), candidate("same-id")]
        report = audit_candidate_input_sets(rows, CUTOFF)
        self.assertEqual(report["eligible_candidate_input_set_count"], 1)
        self.assertEqual(report["duplicate_input_set_ids"], ["same-id"])

    def test_candidate_pool_audit_handles_malformed_unhashable_input_set_ids(self):
        rows = [
            candidate([], target("2501.11111")),
            candidate({"unexpected": "mapping"}, target("2501.22222")),
            candidate("   ", target("2501.33333")),
            candidate("valid-id", target("2501.44444")),
            candidate("valid-id", target("2501.55555")),
        ]

        report = audit_candidate_input_sets(rows, CUTOFF)

        self.assertEqual(report["candidate_input_set_count"], 5)
        self.assertEqual(report["invalid_input_set_id_count"], 3)
        self.assertEqual(report["unique_input_set_id_count"], 1)
        self.assertEqual(report["duplicate_input_set_ids"], ["valid-id"])
        self.assertEqual(len(report["per_candidate_audits"]), 5)
        self.assertEqual(report["per_candidate_audits"][0]["status"],
                         "ineligible_or_unresolved")

    def test_duplicate_target_papers_do_not_inflate_minimum_count(self):
        rows = [candidate(f"set-{index}", target("2501.12345v2" if index % 2 else "2501.12345"))
                for index in range(100)]
        report = audit_candidate_input_sets(rows, CUTOFF)
        self.assertEqual(report["eligible_unique_input_set_id_count"], 100)
        self.assertEqual(report["eligible_unique_target_paper_count"], 1)
        self.assertEqual(report["eligible_candidate_input_set_count"], 1)
        self.assertEqual(report["status"], "minimum_not_met")

    def test_candidate_pool_reports_cross_set_reference_reuse_without_applying_policy(self):
        first = candidate("set-a", target("2501.11111"))
        second_refs = refs()
        second_refs[0]["paper_id"] = "2401.00001v2"
        for index, reference in enumerate(second_refs[1:], start=1):
            reference["paper_id"] = f"2402.{index:05d}"
        second = candidate("set-b", target("2501.22222"), second_refs)

        report = audit_candidate_input_sets([first, second], CUTOFF)

        self.assertEqual(report["eligible_candidate_input_set_count"], 2)
        self.assertEqual(report["reference_reuse_audit_status"],
                         "descriptive_only_policy_unresolved")
        self.assertEqual(report["shared_reference_paper_count"], 1)
        self.assertEqual(report["shared_reference_papers"], [{
            "paper_id": "2401.00001",
            "input_set_ids": ["set-a", "set-b"],
        }])
        self.assertFalse(report["input_sets_selected"])
        self.assertFalse(report["input_sets_frozen"])

    def test_manual_review_coverage_counts_unique_completed_cases_only(self):
        records = ([{"input_set_id": f"review-{i}", "manual_check_completed": True}
                    for i in range(19)] +
                   [{"input_set_id": "review-0", "manual_check_completed": True},
                    {"input_set_id": "pending", "manual_check_completed": False}])
        report = audit_manual_check_coverage(records)
        self.assertEqual(report["completed_unique_input_sets"], 19)
        self.assertFalse(report["manual_check_requirement_met"])
        self.assertEqual(report["duplicate_review_records_for_input_sets"], ["review-0"])

    def test_raw_corpus_audit_reports_absent_references_and_unverified_exposure(self):
        rows = [
            {"paper_id": "2401.00001v1", "title": "One", "abstract": "Abstract",
             "published": "2024-01-01T00:00:00Z", "pool": "mock"},
            {"paper_id": "2401.00002v1", "title": "Two", "abstract": "Abstract",
             "published": "2024-02-01T00:00:00Z", "pool": "mock"},
        ]
        report = audit_raw_corpus(rows, {"2401.00001"}, CUTOFF)
        self.assertEqual(report["unique_canonical_paper_count"], 2)
        self.assertEqual(report["candidate_paper_count_after_focal_exclusion"], 1)
        self.assertEqual(report["reference_like_fields"], [])
        self.assertEqual(report["records_with_reference_like_fields"], 0)
        self.assertEqual(report["eligible_papers_post_cutoff_count"], 0)
        self.assertIn("unverified", report["outside_focal_exposure_status"])
        self.assertFalse(report["sampled"])
        self.assertFalse(report["dataset_frozen"])

    def test_raw_corpus_audit_canonicalizes_focals_and_counts_malformed_rows(self):
        rows = [
            {"paper_id": "2401.00001v1", "title": "One", "abstract": "Abstract",
             "published": "2024-01-01T00:00:00Z", "pool": "mock"},
            None,
            {7: "non-string key"},
        ]
        report = audit_raw_corpus(rows, {"2401.00001v2", "not-arxiv"}, CUTOFF)
        self.assertEqual(report["unique_excluded_focal_count_present"], 1)
        self.assertEqual(report["candidate_paper_count_after_focal_exclusion"], 0)
        self.assertEqual(report["invalid_non_object_raw_row_count"], 1)
        self.assertEqual(report["invalid_focal_id_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
