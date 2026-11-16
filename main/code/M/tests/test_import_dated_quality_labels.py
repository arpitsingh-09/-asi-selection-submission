import json
import tempfile
import unittest
from pathlib import Path

from M.import_dated_quality_labels import import_labels, verify_dated_outcome


def fixture(observed='2023-06-01T12:00:00Z'):
    return {'schema': 'M-dated-quality-label-source-v1', 'label_id': 'TEMP-STRUCTURE-ONLY',
        'paper_id': 'TEMP-PAPER', 'factor': 'peer_review', 'value': 4,
        'definition': 'temporary schema fixture, not an experimental label',
        'observed_at': observed, 'source_url': 'https://example.invalid/revision',
        'source_revision_id': 'TEMP-REVISION', 'source_locator': 'temporary locator',
        'source_quote': 'temporary quoted source text', 'public_at': observed,
        'public_date_basis': 'temporary structural fixture', 'verification_status': 'VERIFIED',
        'verifier_code': 'TEMP-TEST-ONLY', 'verified_at': '2026-01-01T00:00:00Z'}


class TestDatedQualityLabelImporter(unittest.TestCase):
    def test_imported_row_is_source_bound_and_verifiable(self):
        with tempfile.TemporaryDirectory() as d:
            source, output = Path(d) / 'source.jsonl', Path(d) / 'out.jsonl'
            source.write_text(json.dumps(fixture()) + '\n')
            self.assertEqual(import_labels(source, output), 1)
            result = json.loads(output.read_text())
            self.assertTrue(verify_dated_outcome(result))
            self.assertTrue(result['usable_for_fitting'])

    def test_unverified_or_undated_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            source, output = Path(d) / 'source.jsonl', Path(d) / 'out.jsonl'
            row = fixture(observed=None)
            source.write_text(json.dumps(row) + '\n')
            with self.assertRaises(ValueError):
                import_labels(source, output)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
