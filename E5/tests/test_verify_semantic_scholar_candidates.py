import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from E5.collect_known_group_candidates import SemanticScholarHTTPError
from E5.verify_semantic_scholar_candidates import collect


SEEDS = ['s1', 's2', 's3']


class SemanticScholarCandidateVerificationTests(unittest.TestCase):
    def make_candidates(self, directory, count=5):
        path = Path(directory) / 'candidates.json'
        path.write_text(json.dumps({'candidates': [
            {'doi': f'https://doi.org/10.1234/p{i}'} for i in range(count)
        ]}))
        return path

    def test_exact_doi_lookup_saves_raw_and_verifies_three_seed_references(self):
        with tempfile.TemporaryDirectory() as td:
            candidates = self.make_candidates(td)
            calls = []
            def fake(url):
                calls.append(url)
                return {'paperId': f'p{len(calls)}', 'title': f'Title {len(calls)}',
                        'publicationDate': '2021-06-01',
                        'externalIds': {'DOI': f'10.1234/p{len(calls)-1}'},
                        'references': [{'paperId': sid} for sid in SEEDS]}
            out = Path(td) / 'out'
            report = collect(candidates, out, SEEDS, fetch=fake, sleep=lambda _: None, max_candidates=5)
            self.assertEqual(len(calls), 5)
            self.assertTrue(all('/DOI:10.1234%2Fp' in c and 'references.paperId' in c for c in calls))
            self.assertEqual(report['all_three_citations_verified_count'], 5)
            self.assertEqual(len(report['citation_window_candidate_groups']), 1)
            self.assertEqual(report['protocol_eligible_groups'], [])
            self.assertEqual(len((out / 'raw_semantic_scholar.jsonl').read_text().splitlines()), 5)
            self.assertTrue(all(r['source'] == 'Semantic Scholar' for r in report['records']))

    def test_429_stops_and_preserves_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            candidates = self.make_candidates(td, 10)
            calls = []
            def fake(url):
                calls.append(url)
                if len(calls) == 2:
                    raise SemanticScholarHTTPError(429, 'rate limited')
                return {'paperId': 'p1', 'title': 'Title', 'publicationDate': '2021-01-01',
                        'externalIds': {'DOI': '10.1234/p0'},
                        'references': []}
            out = Path(td) / 'out'
            report = collect(candidates, out, SEEDS, fetch=fake, sleep=lambda _: None, max_candidates=5)
            checkpoint = json.loads((out / 'checkpoint.json').read_text())
            self.assertEqual(len(calls), 2)
            self.assertEqual(report['lookup_verified_count'], 1)
            self.assertEqual(checkpoint['last_error']['status'], 429)
            raw = [json.loads(x) for x in (out / 'raw_semantic_scholar.jsonl').read_text().splitlines()]
            self.assertEqual(len(raw), 2)
            self.assertEqual(raw[-1]['response_status'], 429)

    def test_network_failure_is_checkpointed_without_retry(self):
        with tempfile.TemporaryDirectory() as td:
            candidates = self.make_candidates(td, 10)
            calls = []
            def fail(url):
                calls.append(url)
                raise urllib.error.URLError('DNS unavailable')
            out = Path(td) / 'out'
            report = collect(candidates, out, SEEDS, fetch=fail, sleep=lambda _: None, max_candidates=5)
            checkpoint = json.loads((out / 'checkpoint.json').read_text())
            self.assertEqual(len(calls), 1)
            self.assertEqual(report['last_error']['status'], 'NETWORK_ERROR')
            self.assertEqual(checkpoint['last_error']['body'], 'DNS unavailable')
            self.assertEqual(report['lookup_verified_count'], 0)

    def test_rejects_unbounded_or_wrong_seed_count(self):
        with tempfile.TemporaryDirectory() as td:
            candidates = self.make_candidates(td)
            with self.assertRaises(ValueError):
                collect(candidates, Path(td) / 'out', ['s1', 's2'], fetch=lambda _: self.fail('no API'))
            with self.assertRaises(ValueError):
                collect(candidates, Path(td) / 'out', SEEDS, fetch=lambda _: self.fail('no API'), max_candidates=11)

    def test_checkpointed_doi_404_resumes_at_acl_without_repeating_doi(self):
        with tempfile.TemporaryDirectory() as td:
            candidates = Path(td) / 'candidates.json'
            candidates.write_text(json.dumps({'candidates': [{'doi': 'https://doi.org/10.18653/v1/2021.eacl-main.86'}]}))
            out = Path(td) / 'out'; out.mkdir()
            (out / 'checkpoint.json').write_text(json.dumps({
                'completed_dois': [], 'verified_records': {},
                'last_error': {'doi': '10.18653/v1/2021.eacl-main.86', 'status': 404,
                               'body': '{"error":"not found"}'}}))
            calls = []
            def fake(url):
                calls.append(url)
                self.assertIn('/ACL:2021.eacl-main.86?', url)
                return {'paperId': 'acl-paper', 'title': 'Verified title', 'publicationDate': '2021-01-01',
                        'externalIds': {'ACL': '2021.eacl-main.86'},
                        'references': [{'paperId': sid} for sid in SEEDS]}
            report = collect(candidates, out, SEEDS, fetch=fake, sleep=lambda _: None, max_candidates=1)
            self.assertEqual(len(calls), 1)
            self.assertEqual(report['all_three_citations_verified_count'], 1)
            saved = json.loads((out / 'checkpoint.json').read_text())
            self.assertEqual(saved['completed_dois'], ['10.18653/v1/2021.eacl-main.86'])
            raw = [json.loads(x) for x in (out / 'raw_semantic_scholar.jsonl').read_text().splitlines()]
            self.assertEqual([r['method'] for r in raw], ['DOI', 'ACL'])

    def test_title_fallback_requires_source_backed_exact_title_and_identity(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'candidates.json'
            path.write_text(json.dumps({'candidates': [{
                'doi': '10.18653/v1/2021.eacl-main.86', 'title': 'Exact Title',
                'title_source_url': 'https://aclanthology.org/2021.eacl-main.86/'}]}))
            calls = []
            def fake(url):
                calls.append(url)
                if '/DOI:' in url or '/ACL:' in url:
                    raise SemanticScholarHTTPError(404, 'not found')
                return {'data': [{'paperId': 'p1', 'title': 'Exact Title', 'publicationDate': '2021-01-01',
                                  'externalIds': {'ACL': '2021.eacl-main.86'},
                                  'references': [{'paperId': sid} for sid in SEEDS]}]}
            report = collect(path, Path(td) / 'out', SEEDS, fetch=fake, sleep=lambda _: None, max_candidates=1)
            self.assertIn('/paper/search?', calls[-1])
            self.assertEqual(report['all_three_citations_verified_count'], 1)
            self.assertEqual(report['records'][0]['lookup_method'], 'EXACT_TITLE')

            # A title hit without matching external identity must never be accepted.
            path.write_text(json.dumps({'candidates': [{
                'doi': '10.18653/v1/2021.eacl-main.86', 'title': 'Exact Title',
                'title_source_url': 'https://aclanthology.org/2021.eacl-main.86/'}]}))
            def bad_identity(url):
                if '/paper/search?' in url:
                    return {'data': [{'paperId': 'wrong', 'title': 'Exact Title',
                                      'externalIds': {'ACL': 'different.id'}}]}
                raise SemanticScholarHTTPError(404, 'not found')
            report = collect(path, Path(td) / 'bad', SEEDS, fetch=bad_identity, sleep=lambda _: None, max_candidates=1)
            self.assertEqual(report['lookup_verified_count'], 0)


if __name__ == '__main__':
    unittest.main()
