"""Mock-only tests for OpenAlex and Semantic Scholar citation adapters."""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from citation_sources import (  # noqa: E402
    CitationApiError,
    CitationCacheMiss,
    CitationRetryDeferred,
    ArxivApiAdapter,
    CrossrefAdapter,
    JsonFileCache,
    MemoryCache,
    OpenCitationsAdapter,
    OpenAlexAdapter,
    SemanticScholarAdapter,
    compare_reference_sets,
    fetch_openalex_works_batched,
    metadata_coverage,
    openalex_reference_records,
    openalex_arxiv_identifiers,
    openalex_record_matches_arxiv_id,
    reconstruct_openalex_abstract,
    select_diagnostic_sample,
    verify_cross_source_reference_edges,
)


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, headers, timeout):
        self.calls.append((url, dict(headers), timeout))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def response(body, status=200, headers=None):
    text = json.dumps(body)
    return {"status_code": status, "headers": headers or {}, "body": text, "json": body}


class CitationAdapterTests(unittest.TestCase):
    def test_arxiv_exact_id_resolver_preserves_version_metadata_and_doi(self):
        atom = '''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom"><entry><id>https://arxiv.org/abs/2401.00416v2</id><title>SVFAP: Self-supervised Video Facial Affect Perceiver</title><published>2023-12-31T07:44:05Z</published><updated>2024-07-31T10:00:00Z</updated><arxiv:doi>10.1109/TAFFC.2024.3436913</arxiv:doi></entry></feed>'''
        class AtomTransport:
            def get(self, url, headers, timeout):
                return {"status_code": 200, "headers": {}, "body": atom, "json": None}
        result = ArxivApiAdapter(transport=AtomTransport()).get_paper("2401.00416")
        entry = result["entries"][0]
        self.assertEqual(result["exact_identity_match_count"], 1)
        self.assertEqual(entry["versioned_arxiv_id"], "2401.00416v2")
        self.assertEqual(entry["title"], "SVFAP: Self-supervised Video Facial Affect Perceiver")
        self.assertEqual(entry["published"], "2023-12-31T07:44:05Z")
        self.assertEqual(entry["doi"], "10.1109/TAFFC.2024.3436913")
        self.assertIn(":entry", entry["raw_entry_xml"])

    def test_openalex_external_arxiv_query_uses_supported_filter_after_400_regression(self):
        class RejectUnsupportedFilterTransport:
            def __init__(self):
                self.calls = []

            def get(self, url, headers, timeout):
                self.calls.append((url, dict(headers), timeout))
                query = parse_qs(urlparse(url).query)
                filter_value = query.get("filter", [""])[0]
                if filter_value.startswith("ids.arxiv:"):
                    return response({"error": "ids.arxiv is not a valid field"}, status=400)
                if filter_value != (
                    "locations.landing_page_url:https://arxiv.org/abs/2401.00416"
                ):
                    return response({"error": "unexpected filter"}, status=400)
                return response({"results": [{
                    "id": "https://openalex.org/W1",
                    "ids": {"arxiv": "2401.00416v2"},
                }]})

        transport = RejectUnsupportedFilterTransport()
        rejected = transport.get(
            "https://api.openalex.org/works?filter=ids.arxiv%3A2401.00416",
            {}, 30,
        )
        self.assertEqual(rejected["status_code"], 400)
        self.assertIn("ids.arxiv is not a valid field", rejected["json"]["error"])
        result = OpenAlexAdapter(transport=transport).resolve_by_arxiv_external_id("2401.00416")
        query = parse_qs(urlparse(transport.calls[1][0]).query)
        self.assertEqual(query["filter"], [
            "locations.landing_page_url:https://arxiv.org/abs/2401.00416"
        ])
        self.assertFalse(result["automatic_match_selected"])
        self.assertEqual(len(result["candidate_matches"]), 1)
        self.assertEqual(result["candidate_matches"][0]["ids"]["arxiv"], "2401.00416v2")
        self.assertEqual(
            result["match_method"],
            "arxiv_landing_page_filter_exact_id_confirmed_by_caller",
        )

    def test_real_openalex_omits_arxiv_ids_but_exact_arxiv_location_is_authoritative(self):
        # Representative current OpenAlex record structure: DOI and OpenAlex
        # IDs only; the arXiv identifier is in the location URL.
        record = {
            "id": "https://openalex.org/W4414359959",
            "ids": {"doi": "https://doi.org/10.24963/ijcai.2025/279",
                    "openalex": "https://openalex.org/W4414359959"},
            "locations": [
                {"landing_page_url": "https://doi.org/10.24963/ijcai.2025/279"},
                {"landing_page_url": "https://arxiv.org/abs/2412.20662"},
            ],
        }
        self.assertEqual(openalex_arxiv_identifiers(record), {"2412.20662"})
        self.assertTrue(openalex_record_matches_arxiv_id(record, "2412.20662v1"))
        self.assertFalse(openalex_record_matches_arxiv_id(record, "2412.20663"))

    def test_arxiv_doi_identifier_is_exact_but_conflicting_ids_are_ambiguous(self):
        doi_record = {
            "ids": {"doi": "https://doi.org/10.48550/arXiv.2610.29922"},
            "locations": [{"landing_page_url": "https://arxiv.org/abs/2610.29922"}],
        }
        self.assertEqual(openalex_arxiv_identifiers(doi_record), {"2610.29922"})
        self.assertTrue(openalex_record_matches_arxiv_id(doi_record, "2610.29922"))
        conflicting = {
            "ids": {"arxiv": "2610.29922"},
            "locations": [{"landing_page_url": "https://arxiv.org/abs/2610.29923"}],
        }
        self.assertFalse(openalex_record_matches_arxiv_id(conflicting, "2610.29922"))
        self.assertFalse(openalex_record_matches_arxiv_id(
            {"locations": [{"landing_page_url": "https://example.org/abs/2610.29922"}]},
            "2610.29922",
        ))

    def test_opencitations_requires_doi_and_preserves_edge_rows(self):
        edges = [{"oci": "1-2", "citing": "doi:10.1234/a", "cited": "doi:10.1234/b"}]
        transport = FakeTransport([response(edges)])
        result = OpenCitationsAdapter(transport=transport).get_references("https://doi.org/10.1234/A")
        self.assertEqual(result["edge_records"], edges)
        self.assertIn("/references/doi:10.1234%2Fa", transport.calls[0][0])
        with self.assertRaises(ValueError):
            OpenCitationsAdapter(transport=FakeTransport([])).get_references("2401.00416")

    def test_crossref_requires_doi_and_reads_deposited_reference_list(self):
        work = {"DOI": "10.1234/a", "reference": [{"DOI": "10.1234/b"}, {"unstructured": "Unmatched citation"}]}
        result = CrossrefAdapter(transport=FakeTransport([response({"message": work})])).get_work("10.1234/a")
        self.assertEqual(result["reference_records"], work["reference"])
        with self.assertRaises(ValueError):
            CrossrefAdapter(transport=FakeTransport([])).get_work("arXiv:2401.00416")

    def test_openalex_arxiv_resolver_preserves_candidates_without_auto_selecting(self):
        body = {"results": [{"id": "https://openalex.org/W1", "title": "Title",
                             "referenced_works": []}]}
        transport = FakeTransport([response(body)])
        result = OpenAlexAdapter(transport=transport).resolve_by_arxiv_id("2401.00001v2")
        query = parse_qs(urlparse(transport.calls[0][0]).query)
        self.assertIn("locations.landing_page_url:https://arxiv.org/abs/2401.00001v2", query["filter"][0])
        self.assertFalse(result["automatic_match_selected"])
        self.assertEqual(len(result["candidate_matches"]), 1)
        self.assertEqual(result["api_version"], "public REST API; unversioned endpoint")

    def test_openalex_title_and_doi_queries_keep_ambiguous_matches(self):
        body = {"results": [{"id": "W1", "title": "exact title"},
                             {"id": "W2", "title": "similar title"}]}
        transport = FakeTransport([response(body), response({"results": []})])
        adapter = OpenAlexAdapter(transport=transport)
        matches = adapter.search_by_title("Exact Title")
        self.assertEqual([r["normalized_title_exact_match"] for r in matches["candidate_matches"]], [True, False])
        self.assertTrue(all(not r["automatic_match_selected"] for r in matches["candidate_matches"]))
        doi = adapter.search_by_doi("https://doi.org/10.1234/ABC")
        self.assertEqual(doi["match_method"], "doi_filter")
        self.assertFalse(doi["automatic_match_selected"])

    def test_s2_uses_arxiv_namespace_and_keeps_api_key_out_of_url(self):
        transport = FakeTransport([response({"paperId": "s2id", "externalIds": {"ArXiv": "2401.00001"}})])
        adapter = SemanticScholarAdapter(transport=transport, api_key="test-secret")
        result = adapter.get_paper_by_arxiv("2401.00001")
        url, headers, _ = transport.calls[0]
        self.assertIn("ARXIV%3A2401.00001", url)
        self.assertNotIn("test-secret", url)
        self.assertEqual(headers["x-api-key"], "test-secret")
        self.assertEqual(result["api_version"], "Academic Graph API graph/v1")

    def test_retry_after_cache_and_request_provenance(self):
        transport = FakeTransport([
            response({"error": "rate limited"}, status=429, headers={"Retry-After": "0"}),
            response({"results": []}, headers={"Date": "fixture-date", "ETag": "fixture-etag"}),
        ])
        sleeps = []
        cache = MemoryCache()
        adapter = OpenAlexAdapter(transport=transport, cache=cache, sleep=sleeps.append,
                                  min_request_interval_seconds=0)
        result = adapter.search_by_title("some title")
        self.assertEqual([row["status"] for row in result["attempt_history"]],
                         ["retryable_http_error", "ok"])
        self.assertEqual(sleeps, [0.0])
        self.assertIn("retrieved_at_utc", result)
        self.assertEqual(result["response_headers"]["ETag"], "fixture-etag")
        again = adapter.search_by_title("some title")
        self.assertTrue(again["cache_hit"])
        self.assertEqual(len(transport.calls), 2)

    def test_nonretryable_failure_preserves_attempt(self):
        adapter = OpenAlexAdapter(transport=FakeTransport([
            response({"error": "not found"}, status=404)
        ]), max_attempts=3, sleep=lambda _: None)
        with self.assertRaises(CitationApiError) as raised:
            adapter.search_by_title("missing title")
        self.assertEqual(raised.exception.attempts[0]["status"], "non_retryable_http_error")

    def test_http_400_error_preserves_url_status_body_timestamp_and_attempt(self):
        body = {"error": "Invalid query parameters", "message": "unknown field"}
        transport = FakeTransport([response(body, status=400, headers={"Date": "fixture-date"})])
        adapter = OpenAlexAdapter(transport=transport, max_attempts=1)

        with self.assertRaises(CitationApiError) as raised:
            adapter.resolve_by_arxiv_external_id("2401.00416")

        error = raised.exception
        attempt = error.attempts[0]
        self.assertEqual(error.request_url, transport.calls[0][0])
        self.assertEqual(error.http_status, 400)
        self.assertEqual(json.loads(error.raw_body), body)
        self.assertTrue(error.retrieved_at_utc)
        self.assertEqual(attempt["request_url"], error.request_url)
        self.assertEqual(attempt["retrieved_at_utc"], error.retrieved_at_utc)
        self.assertEqual(attempt["raw_body"], error.raw_body)
        self.assertEqual(attempt["status_code"], 400)
        self.assertEqual(len(transport.calls), 1)

    def test_http_429_error_preserves_url_status_body_timestamp_and_attempt(self):
        body = {"message": "Too Many Requests", "code": "429"}
        transport = FakeTransport([response(
            body, status=429, headers={"Date": "fixture-date", "Retry-After": "7"},
        )])
        adapter = SemanticScholarAdapter(
            transport=transport, max_attempts=1, min_request_interval_seconds=0,
        )

        with self.assertRaises(CitationApiError) as raised:
            adapter.get_paper_by_arxiv("2401.00416")

        error = raised.exception
        attempt = error.attempts[0]
        self.assertEqual(error.request_url, transport.calls[0][0])
        self.assertEqual(error.http_status, 429)
        self.assertEqual(json.loads(error.raw_body), body)
        self.assertTrue(error.retrieved_at_utc)
        self.assertEqual(attempt["request_url"], error.request_url)
        self.assertEqual(attempt["retrieved_at_utc"], error.retrieved_at_utc)
        self.assertEqual(attempt["raw_body"], error.raw_body)
        self.assertEqual(attempt["status_code"], 429)
        self.assertEqual(attempt["retry_after"], "7")
        self.assertEqual(len(transport.calls), 1)

    def test_retry_exhaustion_preserves_rate_limit_headers_and_body(self):
        transport = FakeTransport([
            response({"message": "slow down"}, status=429, headers={"Retry-After": "3"}),
            response({"message": "still limited"}, status=429, headers={"Retry-After": "4"}),
        ])
        waits = []
        adapter = OpenAlexAdapter(transport=transport, max_attempts=2,
                                  min_request_interval_seconds=0, sleep=waits.append)
        with self.assertRaises(CitationApiError) as raised:
            adapter.search_by_title("limited title")
        self.assertEqual(waits, [3.0])
        self.assertEqual(raised.exception.attempts[-1]["retry_after"], "4")
        self.assertEqual(json.loads(raised.exception.attempts[-1]["error_body"]),
                         {"message": "still limited"})

    def test_http_date_retry_after_is_respected(self):
        retry_date = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=3), usegmt=True)
        transport = FakeTransport([
            response({"message": "slow down"}, status=429,
                     headers={"Retry-After": retry_date, "RateLimit-Remaining": "0"}),
            response({"results": []}),
        ])
        waits = []
        adapter = OpenAlexAdapter(transport=transport, max_attempts=2,
                                  min_request_interval_seconds=0, sleep=waits.append)
        result = adapter.search_by_title("retry-date")
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(len(waits), 1)
        self.assertGreater(waits[0], 0)
        self.assertLessEqual(waits[0], 3)

    def test_long_retry_after_defers_without_sleeping_or_retrying_early(self):
        transport = FakeTransport([response(
            {"message": "slow down"}, status=429,
            headers={"Retry-After": "120", "X-RateLimit-Remaining": "0"},
        )])
        waits = []
        adapter = OpenAlexAdapter(transport=transport, max_attempts=3,
                                  min_request_interval_seconds=0, sleep=waits.append,
                                  max_inline_retry_wait_seconds=10)
        with self.assertRaises(CitationRetryDeferred) as raised:
            adapter.search_by_title("retry-later")
        self.assertEqual(raised.exception.http_status, 429)
        self.assertEqual(raised.exception.retry_after_seconds, 120.0)
        self.assertEqual(waits, [])
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(raised.exception.attempts[0]["status"], "retry_deferred")

    def test_rate_limit_reset_header_is_respected(self):
        transport = FakeTransport([
            response({"message": "slow down"}, status=429,
                     headers={"RateLimit-Reset": "4", "RateLimit-Remaining": "0"}),
            response({"results": []}),
        ])
        waits = []
        adapter = OpenAlexAdapter(transport=transport, max_attempts=2,
                                  min_request_interval_seconds=0, sleep=waits.append)
        result = adapter.search_by_title("reset-header")
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(waits, [4.0])

    def test_http_timeout_and_attempt_count_are_bounded(self):
        with self.assertRaises(ValueError):
            OpenAlexAdapter(timeout_seconds=31)
        with self.assertRaises(ValueError):
            OpenAlexAdapter(max_attempts=6)

    def test_cache_only_mode_raises_without_network_fallback(self):
        class NoNetwork:
            def get(self, *args, **kwargs):
                raise AssertionError("offline cache miss attempted a network request")

        with tempfile.TemporaryDirectory() as directory:
            adapter = OpenAlexAdapter(cache=JsonFileCache(directory), cache_only=True,
                                      transport=NoNetwork())
            with self.assertRaises(CitationCacheMiss):
                adapter.resolve_by_arxiv_external_id("2501.12345")

    def test_s2_reference_endpoint_is_paginated_and_preserves_each_page(self):
        transport = FakeTransport([
            response({"data": [{"citedPaper": {"paperId": "r1"}}], "next": 1}),
            response({"data": [{"citedPaper": {"paperId": "r2"}}], "next": 0}),
        ])
        result = SemanticScholarAdapter(transport=transport, min_request_interval_seconds=0).get_all_paper_references(
            "s2target", page_size=1
        )
        self.assertEqual(result["reference_count"], 2)
        self.assertEqual(len(result["pages"]), 2)
        self.assertEqual(len(transport.calls), 2)

    def test_openalex_reference_ids_batch_and_keep_missing_ids(self):
        transport = FakeTransport([response({"results": [
            {"id": "https://openalex.org/W1", "title": "Ref 1"}
        ]})])
        result = fetch_openalex_works_batched(OpenAlexAdapter(transport=transport), ["W1", "W2"])
        self.assertEqual(set(result["records_by_openalex_id"]), {"W1"})
        self.assertEqual(result["missing_openalex_ids"], ["W2"])
        self.assertEqual(result["request_count"], 1)

    def test_abstract_reconstruction_and_source_coverage(self):
        index = {"Second": [1], "First": [0], "sentence.": [2]}
        self.assertEqual(reconstruct_openalex_abstract(index), "First Second sentence.")
        oa = metadata_coverage([{
            "id": "W1", "title": "Title", "abstract_inverted_index": index,
            "publication_date": "2024-01-01",
        }], source="OpenAlex")
        s2 = metadata_coverage([{
            "citedPaper": {"paperId": "S1", "title": "Title", "abstract": "Text", "year": 2024}
        }], source="Semantic Scholar Academic Graph")
        self.assertEqual([oa[k] for k in ("identifier_present", "resolvable_identifier", "title", "abstract", "publication_date")],
                         [1, 1, 1, 1, 1])
        self.assertEqual([s2[k] for k in ("identifier_present", "resolvable_identifier", "title", "abstract", "publication_date")],
                         [1, 1, 1, 1, 0])

    def test_cross_source_edges_require_stable_shared_identifiers(self):
        oa_refs = [{"id": "Wref", "title": "Same title", "ids": {"doi": "https://doi.org/10.1234/x"}}]
        s2_refs = [{"citedPaper": {"paperId": "Sref", "title": "Same title",
                                    "externalIds": {"DOI": "10.1234/x"}}}]
        cross = compare_reference_sets(oa_refs, s2_refs)
        self.assertEqual(cross["shared_stable_identifier_count"], 1)
        oa_target = {"id": "Wtarget", "ids": {}, "locations": [
            {"landing_page_url": "https://arxiv.org/abs/2401.00001v1"}
        ]}
        s2_target = {"paperId": "Starget", "externalIds": {"ArXiv": "2401.00001"}}
        result = verify_cross_source_reference_edges(
            "2401.00001", oa_target, s2_target, oa_refs, s2_refs,
        )
        self.assertTrue(result["target_identity_cross_checked_by_arxiv_id"])
        self.assertEqual(result["independently_verified_shared_reference_edge_count"], 1)
        title_only = compare_reference_sets([{"id": "W1", "title": "Same title"}],
                                            [{"citedPaper": {"paperId": "S1", "title": "Same title"}}])
        self.assertEqual(title_only["shared_stable_identifier_count"], 0)
        self.assertFalse(title_only["title_only_matches_are_verified"])

        oa_target_doi = {"id": "Wdoi", "doi": "https://doi.org/10.48550/arxiv.2401.00001",
                         "ids": {"doi": "https://doi.org/10.48550/arxiv.2401.00001"}}
        s2_target_doi = {"paperId": "Sdoi", "externalIds": {
            "ArXiv": "2401.00001", "DOI": "10.48550/arxiv.2401.00001"}}
        doi_result = verify_cross_source_reference_edges(
            "2401.00001", oa_target_doi, s2_target_doi, [], [],
        )
        self.assertTrue(doi_result["target_identity_cross_checked_by_shared_doi"])
        self.assertTrue(doi_result["independent_edge_verification_possible"])
        self.assertEqual(doi_result["independently_verified_shared_reference_edge_count"], 0)

    def test_append_only_file_cache_does_not_overwrite_existing_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = JsonFileCache(directory)
            cache.put("key", {"value": "original"})
            cache.put("key", {"value": "replacement"})
            self.assertEqual(cache.get("key"), {"value": "original"})

    def test_diagnostic_ids_are_deterministic_and_exclude_focal_ids(self):
        rows = [{"paper_id": f"2401.{i:05d}v1", "title": f"Paper {i}",
                 "abstract": f"Abstract {i}", "published": "2024-01-01T00:00:00Z",
                 "pool": "mock"} for i in range(1, 8)]
        one = select_diagnostic_sample(rows, ["2401.00001v2"], size=5)
        two = select_diagnostic_sample(rows, ["2401.00001"], size=5)
        self.assertEqual([row["canonical_paper_id"] for row in one],
                         [row["canonical_paper_id"] for row in two])
        self.assertEqual(len(one), 5)
        self.assertNotIn("2401.00001", [row["canonical_paper_id"] for row in one])
        self.assertTrue(all(row["diagnostic_only"] for row in one))


if __name__ == "__main__":
    unittest.main(verbosity=2)
