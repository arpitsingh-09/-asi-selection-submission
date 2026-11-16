import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import finalize_evaluator_validation as f

SOURCE=f.ROOT/'E6/data/evaluator_validation_train_v2'

class FinalizationTests(unittest.TestCase):
    def load(self,name):return json.loads((SOURCE/name).read_text())
    def verify(self,case,result):
        return f.verify_response(case,result,self.load(case['case_id']+'_started.json'),
            json.loads((f.ROOT/'E6/config.json').read_text()),
            json.loads((f.ROOT/'E6/evaluation_config.json').read_text()),f.ROOT)
    def test_all_saved_responses_verified_without_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.urlopen',side_effect=AssertionError('network prohibited')):
            report=f.finalize(SOURCE,Path(tmp)/'final')
            self.assertEqual(report['saved_responses_verified'],16)
            self.assertEqual(report['logical_identity_controls_correct'],6)
            self.assertEqual(report['validations_genuinely_completed'],0)
            self.assertEqual(report['minimum_independent_pilot_judgments'],10)
            sheet=(Path(tmp)/'final/human_review_with_outputs.md').read_text()
            blind=(Path(tmp)/'final/human_review_blind.md').read_text()
            self.assertEqual(sheet.count('Evaluator response:'),10)
            self.assertNotIn('Evaluator response:',blind)
    def test_raw_response_disagreement_rejected(self):
        case=self.load('cases.json')[0];result=self.load(case['case_id']+'_result.json')
        result['prediction']=1
        with self.assertRaisesRegex(ValueError,'saved prediction'):self.verify(case,result)
    def test_prompt_tampering_rejected(self):
        case=self.load('cases.json')[0];result=self.load(case['case_id']+'_result.json')
        result['calls'][0]['prompt']+='changed'
        with self.assertRaisesRegex(ValueError,'rendered prompt'):self.verify(case,result)
    def test_frozen_decoding_mismatch_rejected(self):
        case=self.load('cases.json')[0];result=self.load(case['case_id']+'_result.json')
        result['calls'][0]['model_metadata']['adapter_metadata']['generation_settings']['options']['seed']=0
        with self.assertRaisesRegex(ValueError,'decoding'):self.verify(case,result)
    def test_absent_references_never_become_accuracy_zero(self):
        rows=[dict(section='question_type',expected=None,prediction='analytic',case_id='q')]
        report=f.metrics(rows)['question_type']
        self.assertIsNone(report['logical_identity_accuracy'])
        self.assertIsNone(report['independent_human_agreement'])
        self.assertFalse(report['validated'])
        self.assertFalse(f.strict_equal(True,1))

if __name__=='__main__':unittest.main()
