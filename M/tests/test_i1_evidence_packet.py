import csv
import json
import tempfile
import unittest
from pathlib import Path

from M.i1_evidence_packet import build_packet, import_reviews, validate_packet


class TestI1EvidencePacket(unittest.TestCase):
    def test_packet_has_blank_independent_review_fields(self):
        with tempfile.TemporaryDirectory() as d:
            out = build_packet('.', Path(d) / 'packet')
            packet = json.loads((out / 'packet.json').read_text())
            self.assertTrue(validate_packet(packet))
            self.assertEqual(len(packet['candidates']), 2)
            for filename in ('reviewer_1_template.csv', 'reviewer_2_template.csv'):
                with (out / filename).open(newline='') as f:
                    rows = list(csv.DictReader(f))
                self.assertEqual(len(rows), 2)
                for row in rows:
                    self.assertTrue(all(not row[name] for name in packet['reviewer_fields']))
            labels = json.loads((out / 'dated_quality_labels_template.jsonl').read_text())
            self.assertIn('observed_at', labels['required_fields'])

    def test_import_rejects_uncompleted_sheets(self):
        with tempfile.TemporaryDirectory() as d:
            out = build_packet('.', Path(d) / 'packet')
            with self.assertRaises(ValueError):
                import_reviews(out / 'reviewer_1_template.csv', out / 'packet.json', Path(d) / 'reviews.jsonl')

    def test_import_accepts_two_completed_independent_sheets(self):
        with tempfile.TemporaryDirectory() as d:
            out = build_packet('.', Path(d) / 'packet')
            packet = json.loads((out / 'packet.json').read_text())
            sheets = [out / 'reviewer_1_template.csv', out / 'reviewer_2_template.csv']
            for slot, sheet in enumerate(sheets, 1):
                with sheet.open(newline='') as f:
                    reader = csv.DictReader(f)
                    fields, rows = reader.fieldnames, list(reader)
                for index, row in enumerate(rows):
                    row.update({'reviewer_code': f'REVIEWER-{slot}', 'review_date_utc': '2026-11-14T00:00:00Z',
                        'question_input_relationship_valid': 'UNCERTAIN', 'paraphrase_equivalent': 'UNCERTAIN',
                        'near_miss_distinct': 'UNCERTAIN', 'same_topic_decoy_valid': 'UNCERTAIN',
                        'evidence_references_json': json.dumps([{'source_id': 'TEMP', 'url': 'https://example.invalid',
                            'locator': 'temporary fixture', 'quote': 'structural test only'}]),
                        'rationale': 'TEMP STRUCTURE TEST ONLY'})
                with sheet.open('w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
            target = Path(d) / 'reviews.jsonl'
            self.assertEqual(import_reviews(sheets, out / 'packet.json', target), 2)
            imported = [json.loads(line) for line in target.read_text().splitlines()]
            self.assertTrue(all(not row['review_gate_passed'] and not row['evaluation_eligible'] for row in imported))


if __name__ == '__main__':
    unittest.main()
