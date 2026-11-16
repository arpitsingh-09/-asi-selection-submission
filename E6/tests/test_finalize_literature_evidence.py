import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import finalize_literature_evidence as f
from researcher_approval import digest

SOURCE=f.ROOT/'E6/data/literature_extraction_run_v1'
OUTPUT=f.ROOT/'E6/data/literature_evidence_finalized_v1'

class LiteratureEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((SOURCE/'extraction_plan.json').read_text())
        cls.extracted=json.loads((SOURCE/'extraction_manifest.json').read_text())['target_extractions'][0]
        cls.original={k:v for k,v in cls.extracted.items() if k not in ('target_extraction','target_extraction_source_field')}
        directory=SOURCE/digest(cls.original['input_set_id'])[:16]
        cls.saved={name:json.loads((directory/name).read_text()) for name in ('extraction_checkpoint.json','request_started.json','response.json')}
    def check(self,original=None,saved=None):
        saved=saved or copy.deepcopy(self.saved)
        return f.check_one(original or self.original,self.extracted,saved['extraction_checkpoint.json'],saved['request_started.json'],saved['response.json'],self.plan)
    def test_all_100_verified_without_network_or_client(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('network prohibited')),patch('run_literature_extraction.make_configured_gemma_client',side_effect=AssertionError('client prohibited')):
            result=f.verify_run(SOURCE)
        self.assertEqual(len(result['verified']),100)
        self.assertEqual(len(result['worklist']['selected_input_set_ids']),20)
    def test_source_binding_corruption_rejected(self):
        original=copy.deepcopy(self.original);original['target']['abstract']+=' changed'
        with self.assertRaisesRegex(ValueError,'identity'):self.check(original=original)
    def test_checkpoint_checksum_corruption_rejected(self):
        saved=copy.deepcopy(self.saved);saved['extraction_checkpoint.json']['checkpoint_sha256']='bad'
        with self.assertRaisesRegex(ValueError,'checksum'):self.check(saved=saved)
    def test_response_usage_or_decoding_corruption_rejected(self):
        saved=copy.deepcopy(self.saved);response=saved['response.json'];response['reply']['adapter_metadata']['generation_settings']['options']['seed']=0
        response['reply_sha256']=digest(response['reply'])
        with self.assertRaisesRegex(ValueError,'decoding'):self.check(saved=saved)
    def test_consistency_flags_are_not_human_checks(self):
        result=self.check()
        self.assertFalse(result['automatic_checks']['human_checks_completed'])
        self.assertEqual(result['automatic_checks']['literal_source_checks']['research_question']['semantic_support'],'requires_independent_review')
    def test_backend_RFC3339_precision_is_parsed_without_altering_evidence(self):
        for digits in ('1','12','123','1234','12345','123456','123456789'):
            self.assertTrue(f.valid_backend_utc('2020-01-01T00:00:00.'+digits+'Z'))
        self.assertFalse(f.valid_backend_utc('missing timestamp'))
    def test_prepared_forms_never_claim_completed_reviews(self):
        bundle=f.verify_bundle(OUTPUT/'evidence_bundle.json')
        forms=json.loads((OUTPUT/'independent_review_forms.json').read_text())
        self.assertEqual(len(forms),40);self.assertEqual(bundle['human_reviews_completed'],0)
        for row in forms:
            self.assertIsNone(row['reviewer_id']);self.assertFalse(row['manual_check_completed'])
            self.assertIsNone(row['source_component_sidecar_sha256'])
            for key in f.CATEGORIES:self.assertIsNone(row[key])
    def test_readiness_uses_completed_extractions_not_human_validation(self):
        from test_readiness import literature_evidence_gates
        result=literature_evidence_gates(OUTPUT/'evidence_bundle.json')
        self.assertEqual(result['verified_extractions'],100)
        self.assertEqual(result['review_packets_completed'],20)
        self.assertFalse(result['annotations_usable'])
        self.assertTrue(result['blockers'])

if __name__=='__main__':unittest.main()
