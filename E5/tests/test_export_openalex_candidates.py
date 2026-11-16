import json
import tempfile
import unittest
from pathlib import Path

from E5.collect_openalex_known_groups import S2_IDS
from E5.export_openalex_candidates import candidate_rows, export


class OpenAlexCandidateExportTests(unittest.TestCase):
    def test_exports_date_window_and_keeps_semantic_scholar_unverified(self):
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / 'raw.jsonl'
            seed_oa = {sid: f'https://openalex.org/S{i}' for i, sid in enumerate(S2_IDS)}
            works = [
                {'id': f'https://openalex.org/W{i}', 'doi': f'https://doi.org/10.x/{i}',
                 'publication_date': '2021-01-01' if i < 3 else '2021-12-31',
                 'referenced_works': list(seed_oa.values())}
                for i in range(5)
            ]
            with raw.open('w') as f:
                for sid in S2_IDS:
                    f.write(json.dumps({'seed_s2_id': sid, 'seed_openalex_id': seed_oa[sid],
                                        'response': {'results': works}}) + '\n')
            rows = candidate_rows(raw)
            self.assertEqual(5, len(rows))
            self.assertTrue(all(r['semantic_scholar_status'] == 'UNVERIFIED' for r in rows))
            self.assertTrue(all(r['title'] is None and r['arxiv_id'] is None for r in rows))
            self.assertTrue(all(r['cited_seed_openalex_ids'] == sorted(seed_oa.values()) for r in rows))
            out = Path(td) / 'out'
            export(raw, out)
            self.assertEqual(5, json.loads((out / 'candidates.json').read_text())['candidate_count'])

    def test_rejects_incomplete_seed_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / 'raw.jsonl'
            raw.write_text(json.dumps({'seed_s2_id': S2_IDS[0], 'seed_openalex_id': 'W1', 'response': {}}))
            with self.assertRaisesRegex(ValueError, 'all three seeds'):
                candidate_rows(raw)


if __name__ == '__main__':
    unittest.main()
