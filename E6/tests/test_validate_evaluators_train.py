import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import validate_evaluators_train as v

class ValidationTests(unittest.TestCase):
    def test_actual_cases_are_TRAIN_only_and_no_0007(self):
        cases=v.build_cases()
        self.assertEqual(len(cases),16)
        self.assertEqual(sum(c['expected'] is None for c in cases),10)
        for c in cases:
            for source in c['sources']:
                self.assertIn(':TRAIN-SET:',source['unit'])
                self.assertNotIn(':TRAIN-SET:0007:',source['unit'])
            if c['expected'] is not None:self.assertEqual(c['a'],c['b'])
    def test_valid_json_is_not_semantic_validation(self):
        cases=v.build_cases()
        rows=[dict(c,status='returned_valid',prediction=c['expected']) for c in cases]
        report=v.summarize(cases,rows)
        for section in report.values():
            self.assertEqual(section['status'],'incomplete_validation')
            self.assertEqual(section['valid_response_rate'],1)
            self.assertIsNone(section['human_agreement'])
            self.assertIsNone(section['acceptance_threshold'])
    def test_network_denial_retains_real_blocker_and_no_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'run'
            with patch.object(sys,'argv',['validate','--output-dir',str(output)]),patch.object(v,'_request_json',side_effect=PermissionError('fixture denied')),patch.object(v,'make_configured_gemma_client',side_effect=AssertionError('model creation')):
                self.assertEqual(v.main(),2)
            report=json.loads((output/'report.json').read_text())
            self.assertEqual(report['validations_completed'],0)
            self.assertEqual(report['model_call_attempts'],0)
            self.assertTrue(report['preserved_sources_and_settings_unchanged'])
            self.assertIn('fixture denied',(output/'execution_blocker.json').read_text())
    def test_existing_output_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(sys,'argv',['validate','--output-dir',tmp]):
                with self.assertRaises(FileExistsError):v.main()

if __name__=='__main__':unittest.main()
