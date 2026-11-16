"""Offline tests for citation-edge-based literature preparation."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prepare_openalex_literature_manifest import (  # noqa: E402
    build_verified_literature_manifest,
    cached_reference_records_from_targets,
    load_reference_metadata_batch_files,
    load_source_edge_targets,
    retrieve_reference_metadata_batches,
)
from citation_sources import CitationApiError  # noqa: E402


CUTOFF = "2024-09-01T00:00:00Z"
DEV = {"reserved_development_ids": {"paper_ids": []}}


def source_record(paper_id="2501.12345"):
    return {"paper_id": paper_id, "title": "Target title",
            "abstract": "Target abstract", "published": "2025-01-01T00:00:00Z",
            "source": "arXiv API", "paper_url": "https://arxiv.org/abs/" + paper_id}


def target_openalex(ref_count=11, *, title="Target title"):
    return {
        "id": "https://openalex.org/W900000",
        "title": title,
        "ids": {"doi": "https://doi.org/10.48550/arxiv.2501.12345"},
        "locations": [{"landing_page_url": "https://arxiv.org/abs/2501.12345"}],
        "referenced_works": [f"https://openalex.org/W{i}" for i in range(1, ref_count + 1)],
    }


def target_inputs(ref_count=11):
    recon = {"rows": [{
        "target_arxiv_id": "2501.12345",
        "status": "exact_match",
        "exact_openalex_records": [target_openalex(ref_count)],
        "request_url": "https://api.openalex.org/works?fixture=target",
        "retrieved_at_utc": "2026-01-01T00:00:00Z",
        "http_status": 200,
        "raw_response_sha256": "f" * 64,
    }]}
    return load_source_edge_targets(
        recon, [source_record()], focal_exclusion_ids=[],
        development_manifest=DEV, cutoff_utc=CUTOFF,
    )


class ReferenceMetadataBatchTests(unittest.TestCase):
    def test_edges_come_only_from_exact_target_referenced_works(self):
        targets, ref_ids, audit = target_inputs(12)
        self.assertEqual(len(targets), 1)
        self.assertEqual(len(ref_ids), 12)
        self.assertEqual(audit["source_citation_edge_count"], 12)
        self.assertEqual(targets[0]["referenced_works_ids"][0], "https://openalex.org/W1")

        # Similar titles and unlinked work rows cannot create edges.
        empty_recon = {"rows": [{
            "target_arxiv_id": "2501.12345", "status": "exact_match",
            "exact_openalex_records": [{**target_openalex(0), "title": "Different title"}],
        }]}
        no_edges, ids, _ = load_source_edge_targets(
            empty_recon, [source_record()], focal_exclusion_ids=[],
            development_manifest=DEV, cutoff_utc=CUTOFF,
        )
        self.assertEqual(len(no_edges), 1)
        self.assertEqual(ids, [])

    def test_reference_retrieval_batches_are_stable_and_resume_completed_files(self):
        ids = [f"https://openalex.org/W{i}" for i in range(1, 203)]
        calls = []

        class Adapter:
            def get_works(self, batch_ids, *, per_page):
                calls.append(list(batch_ids))
                return {
                    "source": "OpenAlex", "api_version": "test", "request_url": "fixture-url",
                    "retrieved_at_utc": "2026-01-01T00:00:00Z", "http_status": 200,
                    "cache_hit": False,
                    "raw_response": {"results": [{"id": row, "title": row} for row in batch_ids]},
                }

        with tempfile.TemporaryDirectory() as directory:
            result = retrieve_reference_metadata_batches(
                Adapter(), list(reversed(ids)), output_dir=directory,
                run_sha256="a" * 64,
            )
            self.assertEqual([len(row) for row in calls], [100, 100, 2])
            self.assertEqual(result["reference_id_count"], 202)
            calls.clear()
            loaded = load_reference_metadata_batch_files(
                directory, ids, run_sha256="a" * 64,
            )
            self.assertEqual(calls, [])
            self.assertEqual(len(loaded["records_by_openalex_id"]), 202)

    def test_exact_target_cache_records_are_reused_for_reference_ids(self):
        targets, ref_ids, _ = target_inputs(2)
        # Make one cited ID an already retrieved exact target work. The ID is
        # reused only by exact OpenAlex ID and retains its original provenance.
        record = {"id": ref_ids[0], "abstract_inverted_index": {"cached": [0]}}
        targets[0]["target_openalex_record"] = record
        targets[0]["target_openalex_id"] = ref_ids[0]
        targets[0]["target_resolution_provenance"]["request_url"] = "cached-target-query"
        targets[0]["target_resolution_provenance"]["retrieved_at_utc"] = "2026-01-01T00:00:00Z"
        cached, provenance = cached_reference_records_from_targets(targets)
        calls = []

        class Adapter:
            def get_works(self, batch_ids, *, per_page):
                calls.append(list(batch_ids))
                return {"source": "OpenAlex", "api_version": "test", "request_url": "live",
                        "retrieved_at_utc": "2026-01-02T00:00:00Z", "http_status": 200,
                        "cache_hit": False,
                        "raw_response": {"results": [{"id": value} for value in batch_ids]}}

        with tempfile.TemporaryDirectory() as directory:
            result = retrieve_reference_metadata_batches(
                Adapter(), ref_ids, output_dir=directory, run_sha256="d" * 64,
                cached_records_by_openalex_id=cached,
                cached_provenance_by_openalex_id=provenance,
            )
            self.assertEqual(result["records_by_openalex_id"][ref_ids[0]], record)
            self.assertEqual(result["provenance_by_openalex_id"][ref_ids[0]]["request_url"],
                             "cached-target-query")
            self.assertEqual(calls, [[ref_ids[1]]])

    def test_interrupted_reference_retrieval_resumes_without_refetching_saved_batch(self):
        ids = [f"https://openalex.org/W{i}" for i in range(1, 102)]
        calls = []

        class FailsSecondBatch:
            def get_works(self, batch_ids, *, per_page):
                calls.append(list(batch_ids))
                if len(calls) == 2:
                    raise RuntimeError("simulated interruption")
                return {"source": "OpenAlex", "api_version": "test", "request_url": "fixture",
                        "retrieved_at_utc": "2026-01-01T00:00:00Z", "http_status": 200,
                        "cache_hit": False,
                        "raw_response": {"results": [{"id": row} for row in batch_ids]}}

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
                retrieve_reference_metadata_batches(
                    FailsSecondBatch(), ids, output_dir=directory, run_sha256="b" * 64,
                )
            self.assertTrue((Path(directory) /
                             "openalex_reference_metadata_batch_v1_0001.json").exists())

            class Resume:
                def get_works(self, batch_ids, *, per_page):
                    calls.append(list(batch_ids))
                    return {"source": "OpenAlex", "api_version": "test", "request_url": "fixture",
                            "retrieved_at_utc": "2026-01-01T00:00:00Z", "http_status": 200,
                            "cache_hit": True,
                            "raw_response": {"results": [{"id": row} for row in batch_ids]}}

            result = retrieve_reference_metadata_batches(
                Resume(), ids, output_dir=directory, run_sha256="b" * 64,
            )
            self.assertEqual(len(calls), 3)
            self.assertEqual(result["batch_count"], 2)
            self.assertEqual(len(result["records_by_openalex_id"]), 101)

    def test_429_after_completed_reference_batch_preserves_checkpoint_for_resume(self):
        ids = [f"https://openalex.org/W{i}" for i in range(1, 102)]

        class RateLimited:
            def __init__(self):
                self.calls = 0

            def get_works(self, batch_ids, *, per_page):
                self.calls += 1
                if self.calls == 2:
                    raise CitationApiError("429", [{"status_code": 429}], http_status=429)
                return {"source": "OpenAlex", "api_version": "test", "request_url": "fixture",
                        "retrieved_at_utc": "2026-01-01T00:00:00Z", "http_status": 200,
                        "cache_hit": False,
                        "raw_response": {"results": [{"id": row} for row in batch_ids]}}

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(CitationApiError):
                retrieve_reference_metadata_batches(
                    RateLimited(), ids, output_dir=directory, run_sha256="c" * 64,
                )
            checkpoint = Path(directory) / "openalex_reference_metadata_batch_v1_0001.json"
            self.assertTrue(checkpoint.exists())

            calls = []

            class Resume:
                def get_works(self, batch_ids, *, per_page):
                    calls.append(list(batch_ids))
                    return {"source": "OpenAlex", "api_version": "test", "request_url": "fixture",
                            "retrieved_at_utc": "2026-01-01T00:00:00Z", "http_status": 200,
                            "cache_hit": False,
                            "raw_response": {"results": [{"id": row} for row in batch_ids]}}

            result = retrieve_reference_metadata_batches(
                Resume(), ids, output_dir=directory, run_sha256="c" * 64,
            )
            self.assertEqual(len(calls), 1)
            self.assertEqual(len(result["records_by_openalex_id"]), 101)

    def test_manifest_includes_only_eligible_sets_with_10_abstracts_and_source_edges(self):
        targets, _, _ = target_inputs(11)
        records = {}
        provenance = {}
        for index in range(1, 12):
            work_id = f"https://openalex.org/W{index}"
            records[work_id] = {
                "id": work_id,
                "doi": f"https://doi.org/10.48550/arxiv.2401.{index:05d}",
                "ids": {"doi": f"https://doi.org/10.48550/arxiv.2401.{index:05d}"},
                "abstract_inverted_index": {f"Reference{index}": [0], "abstract": [1]},
            }
            provenance[work_id] = {"request_url": "fixture-ref-batch", "cache_hit": True}
        manifest = build_verified_literature_manifest(
            targets, {"records_by_openalex_id": records,
                      "provenance_by_openalex_id": provenance},
            cutoff_utc=CUTOFF, excluded_arxiv_ids=["2401.00001"],
        )
        self.assertEqual(manifest["eligible_input_set_count"], 1)
        row = manifest["input_sets"][0]
        self.assertEqual(row["input_set_id"], "lit-2501.12345")
        self.assertTrue(row["reference_links_verified"])
        self.assertEqual(row["reference_link_provenance"]["edge_source_field"], "referenced_works")
        self.assertEqual(row["eligibility_audit"]["unique_reference_with_abstract_count"], 10)
        self.assertEqual(len(row["citation_edges"]), 11)
        self.assertTrue(any(edge["metadata_status"] == "excluded_reference"
                            for edge in row["citation_edges"]))
        self.assertNotIn("question", row)

    def test_manifest_excludes_target_with_fewer_than_ten_retrieved_abstracts(self):
        targets, _, _ = target_inputs(11)
        records = {}
        for index in range(1, 12):
            work_id = f"https://openalex.org/W{index}"
            records[work_id] = {"id": work_id}
            if index < 10:
                records[work_id]["abstract_inverted_index"] = {"abstract": [0]}
        manifest = build_verified_literature_manifest(
            targets, {"records_by_openalex_id": records,
                      "provenance_by_openalex_id": {}},
            cutoff_utc=CUTOFF, excluded_arxiv_ids=[],
        )
        self.assertEqual(manifest["eligible_input_set_count"], 0)
        self.assertEqual(manifest["input_sets"], [])


if __name__ == "__main__":
    unittest.main()
