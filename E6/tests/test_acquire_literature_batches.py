"""Offline tests for resumable, deterministic literature acquisition batches."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acquire_literature_batches import (  # noqa: E402
    eligible_source_targets,
    reconcile_openalex_cache_offline,
    run_resumable_openalex_batches,
)
from citation_sources import (  # noqa: E402
    CitationApiError,
    JsonFileCache,
    MemoryCache,
    OpenAlexAdapter,
)


CUTOFF = "2024-09-01T00:00:00Z"
DEVELOPMENT = {"reserved_development_ids": {"paper_ids": []}}


def records(count):
    return [{
        "paper_id": f"2501.{index:05d}",
        "title": f"Target {index}",
        "abstract": f"Abstract {index}",
        "published": "2025-01-02T00:00:00Z",
    } for index in range(1, count + 1)]


def eligible_candidate(source):
    target_id = source["paper_id"].split("v")[0]
    refs = [{"paper_id": f"2401.{i:05d}", "abstract": f"Reference {i}"}
            for i in range(1, 11)]
    return {
        "input_set_id": "lit-" + target_id,
        "target": dict(source),
        "references": refs,
        "reference_links_verified": True,
        "reference_link_provenance": {"source": "test verifier", "verified": True},
    }


def acquisition_for(sources, *, links_verified=True, duplicate=False):
    candidates = [eligible_candidate(source) for source in sources]
    if not links_verified:
        for candidate in candidates:
            candidate["reference_links_verified"] = False
    if duplicate and candidates:
        candidates.append(dict(candidates[0]))
    return {
        "attempts": [{"input_set_id": "lit-" + row["paper_id"],
                       "paper_id": row["paper_id"],
                       "status": "provisional_candidate_acquired"} for row in sources],
        "candidates": candidates,
        "retrieval_failures": 0,
    }


class BatchAcquisitionTests(unittest.TestCase):
    def run_batches(self, directory, source_rows, acquire, progress=None):
        return run_resumable_openalex_batches(
            adapter=object(), raw_source_records=source_rows,
            focal_exclusion_ids=[], development_manifest=DEVELOPMENT,
            cutoff_utc=CUTOFF, output_dir=directory,
            acquisition=acquire, progress=progress or (lambda _: None),
        )

    def test_batches_are_deterministic_and_report_required_progress(self):
        rows = records(51)
        calls, progress = [], []

        def acquire(adapter, batch_rows, **kwargs):
            calls.append([row["paper_id"] for row in batch_rows])
            return acquisition_for(batch_rows)

        result = self.run_batches(tempfile.mkdtemp(), list(reversed(rows)), acquire, progress.append)
        self.assertEqual([len(batch) for batch in calls], [50, 1])
        self.assertEqual(calls[0][0], "2501.00001")
        self.assertEqual(calls[1], ["2501.00051"])
        self.assertEqual(result["status"], "candidate_pool_exhausted")
        self.assertEqual(result["genuinely_eligible_candidates"], 51)
        self.assertEqual(result["candidates_with_10_abstract_references"], 51)
        self.assertEqual(progress[-1]["successful_openalex_matches"], 51)

    def test_target_preparation_applies_cutoff_focal_and_development_exclusions(self):
        source = records(4)
        source[2]["paper_id"] = "2401.12345"
        source[2]["published"] = "2024-08-31T23:59:59Z"
        selected = eligible_source_targets(
            source,
            focal_exclusion_ids=["2501.00001"],
            development_manifest={"reserved_development_ids": {
                "paper_ids": ["2501.00002v2"]}},
            cutoff_utc=CUTOFF,
        )
        self.assertEqual([row["paper_id"] for row in selected], ["2501.00004"])

    def test_resume_skips_completed_batch_and_retries_only_interrupted_batch(self):
        directory = tempfile.mkdtemp()
        rows = records(51)
        first_calls = []

        def interrupted(adapter, batch_rows, **kwargs):
            first_calls.append([row["paper_id"] for row in batch_rows])
            if len(first_calls) == 2:
                raise RuntimeError("simulated interruption")
            return acquisition_for(batch_rows)

        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.run_batches(directory, rows, interrupted)
        self.assertTrue((Path(directory) / "literature_openalex_batch_v1_0001.json").exists())
        resume_calls = []

        def resume(adapter, batch_rows, **kwargs):
            resume_calls.append([row["paper_id"] for row in batch_rows])
            return acquisition_for(batch_rows)

        result = self.run_batches(directory, rows, resume)
        self.assertEqual(len(resume_calls), 1)
        self.assertEqual(resume_calls[0], ["2501.00051"])
        self.assertEqual(result["targets_processed"], 51)

    def test_cache_reuses_existing_openalex_response_without_transport(self):
        class Transport:
            def __init__(self):
                self.calls = 0

            def get(self, url, headers, timeout):
                self.calls += 1
                return {"status_code": 200, "headers": {}, "body": '{"results":[]}',
                        "json": {"results": []}}

        with tempfile.TemporaryDirectory() as directory:
            transport = Transport()
            cache = JsonFileCache(directory)
            first = OpenAlexAdapter(cache=cache, transport=transport, max_attempts=1)
            first.resolve_by_arxiv_external_id("2501.12345")
            self.assertEqual(transport.calls, 1)

            class NoNetwork:
                def get(self, *args, **kwargs):
                    raise AssertionError("cache miss would make a network request")

            second = OpenAlexAdapter(cache=cache, transport=NoNetwork(), max_attempts=1)
            reused = second.resolve_by_arxiv_external_id("2501.12345")
            self.assertTrue(reused["cache_hit"])

    def test_offline_reconciliation_uses_cache_only_and_counts_cache_hits(self):
        class Transport:
            def __init__(self):
                self.calls = 0

            def get(self, url, headers, timeout):
                self.calls += 1
                raw = {"meta": {"count": 1}, "results": [{
                    "id": "https://openalex.org/W1",
                    "ids": {"doi": "https://doi.org/10.48550/arxiv.2501.00001"},
                    "locations": [{"landing_page_url": "https://arxiv.org/abs/2501.00001"}],
                }]}
                return {"status_code": 200, "headers": {},
                        "body": json.dumps(raw), "json": raw}

        transport = Transport()
        cache_events = []
        with tempfile.TemporaryDirectory() as directory:
            cache = JsonFileCache(directory)
            live = OpenAlexAdapter(cache=cache, transport=transport, max_attempts=1)
            live.resolve_by_arxiv_external_id("2501.00001")
            result = reconcile_openalex_cache_offline(
                OpenAlexAdapter(cache=cache, transport=object(), cache_only=True),
                records(1), focal_exclusion_ids=[],
                development_manifest=DEVELOPMENT, cutoff_utc=CUTOFF,
                progress=cache_events.append,
            )
        self.assertEqual(transport.calls, 1)
        self.assertEqual(result["counts"]["cache_hits"], 1)
        self.assertEqual(result["counts"]["exact_matches"], 1)
        self.assertTrue(cache_events[0]["cache_hit"])

    def test_rate_limit_pauses_batch_and_resume_skips_saved_batches(self):
        directory = tempfile.mkdtemp()
        rows = records(51)
        calls = []

        def rate_limited(adapter, batch_rows, **kwargs):
            calls.append([row["paper_id"] for row in batch_rows])
            if len(calls) == 2:
                raise CitationApiError(
                    "429", [{"status_code": 429, "retry_after_seconds": 17}],
                    http_status=429,
                )
            return acquisition_for(batch_rows)

        paused = self.run_batches(directory, rows, rate_limited)
        self.assertEqual(paused["status"], "rate_limited_pause")
        self.assertEqual(paused["retry_after_seconds"], 17)
        self.assertTrue((Path(directory) / "literature_openalex_batch_v1_0001.json").exists())
        resumed_calls = []

        def resumed(adapter, batch_rows, **kwargs):
            resumed_calls.append([row["paper_id"] for row in batch_rows])
            return acquisition_for(batch_rows)

        result = self.run_batches(directory, rows, resumed)
        self.assertEqual(resumed_calls, [["2501.00051"]])
        self.assertEqual(result["targets_processed"], 51)

    def test_duplicate_candidate_targets_abort_before_batch_is_written(self):
        directory = tempfile.mkdtemp()
        with self.assertRaisesRegex(ValueError, "duplicate target candidates"):
            self.run_batches(
                directory, records(1),
                lambda adapter, batch_rows, **kwargs: acquisition_for(batch_rows, duplicate=True),
            )
        self.assertFalse(list(Path(directory).glob("literature_openalex_batch*.json")))

    def test_only_strictly_eligible_candidates_count_toward_120_stop(self):
        directory = tempfile.mkdtemp()
        rows = records(250)
        calls = []

        def acquire(adapter, batch_rows, **kwargs):
            calls.append(len(batch_rows))
            # The first two batches have abstracts but unverified citation links.
            return acquisition_for(batch_rows, links_verified=len(calls) > 2)

        result = self.run_batches(directory, rows, acquire)
        self.assertEqual(calls, [50, 50, 50, 50, 50])
        self.assertEqual(result["status"], "target_met")
        self.assertEqual(result["genuinely_eligible_candidates"], 150)
        self.assertEqual(result["candidates_with_10_abstract_references"], 250)


if __name__ == "__main__":
    unittest.main()
