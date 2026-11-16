import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import literature_review_documents as r

SOURCE=r.ROOT/'E6/data/literature_evidence_finalized_v1'
DOCS=r.ROOT/'E6/data/literature_reviewer_documents_v1'

class ReviewDocumentsTests(unittest.TestCase):
    def paths(self):return [DOCS/name/'review.md' for name in ('reviewer_A','reviewer_B')]
    def test_blank_documents_and_source_evidence(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('network prohibited')):
            report=r.ingest(SOURCE,*self.paths())
        self.assertEqual(report['human_reviews_completed'],0)
        self.assertEqual(report['checks_pending'],280)
        self.assertEqual(report['adjudication_required'],[])
        for slot,path in enumerate(self.paths(),1):
            rows=r.read_responses(path)
            self.assertEqual(len(rows),20)
            self.assertEqual({row['reviewer_slot'] for row in rows},{slot})
            for row in rows:
                packet=r.load(SOURCE/'packets'/(row['input_set_id']+'.json'))
                self.assertIn(packet['target_source_text'],path.read_text())
                self.assertEqual(set(row['check_evidence']),set(r.CHECKS))
    def fixture(self,folder,*,disagree=False,same_identity=False,tamper=False,positive_component=False):
        paths=[]
        for slot,path in enumerate(self.paths(),1):
            rows=r.read_responses(path)
            # Synthetic test data only, confined to temporary directory.
            for row in rows:
                row.update(reviewer_id='fixture-A' if slot==1 or same_identity else 'fixture-B',
                    reviewed_at_utc='2020-01-01T00:00:00Z',manual_check_completed=True,
                    reviewer_notes='Synthetic test absence finding.',extraction_errors=['fixture omission'],corrections=[])
                for key in r.CHECKS:
                    row[key]=False
                    row['check_evidence'][key]={'rationale':'Synthetic test only.','source_quote_or_location':'Synthetic absence finding.'}
            if slot==2 and disagree:rows[0][r.CHECKS[0]]=True
            if slot==2 and tamper:rows[0]['extraction_sha256']='changed'
            if positive_component:rows[0]['problem_extraction_accurate']=True
            dest=Path(folder)/f'{slot}.md'
            dest.write_text('\n\n'.join('```review-response\n'+json.dumps(row)+'\n```' for row in rows))
            paths.append(dest)
        return paths
    def test_disagreement_and_negative_agreement_are_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=r.ingest(SOURCE,*self.fixture(tmp,disagree=True))
        self.assertEqual(report['human_reviews_completed'],40)
        self.assertEqual(len(report['adjudication_required']),1)
        self.assertEqual(report['adjudication_required'][0]['disputed_checks'],[r.CHECKS[0]])
        self.assertEqual(len(report['matching_negative_cases_require_correction']),19)
        pair=[row for row in report['records'] if row['input_set_id']==report['adjudication_required'][0]['input_set_id']]
        self.assertEqual(report['adjudication_required'][0]['review_records_sha256'],r.digest(sorted(pair,key=lambda row:row['reviewer_id'])))
        self.assertFalse(report['annotations_usable'])
    def test_same_reviewer_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'distinct independent'):
                r.ingest(SOURCE,*self.fixture(tmp,same_identity=True))
    def test_binding_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'binding changed'):
                r.ingest(SOURCE,*self.fixture(tmp,tamper=True))
    def test_missing_components_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=r.ingest(SOURCE,*self.fixture(tmp,positive_component=True))
        self.assertEqual(report['human_reviews_completed'],38)
        self.assertTrue(any('missing annotation cannot pass' in error for issue in report['issues'] for error in issue['errors']))

if __name__=='__main__':unittest.main()
