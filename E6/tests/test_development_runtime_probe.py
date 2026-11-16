"""Runtime-probe plumbing with mock counts; never evidence of real Gemma success."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import development_runtime_probe as probe


class FixtureRuntime:
    calls = []
    def __init__(self, **kwargs): self.generation_options = kwargs['generation_options']
    def _call(self, stage, prompt, options, limit):
        self.calls.append(('count', stage))
        count = 28500 if len(prompt) > 50000 else 150
        return {'raw_response': 'fixture', 'input_tokens': count, 'output_tokens': 1,
                'total_tokens': count + 1, 'adapter_metadata': {'done': True}}
    def call_with_token_limit(self, stage, prompt, *, max_output_tokens):
        self.calls.append(('pressure', stage))
        return {'raw_response': '{"fixture_truncation":', 'input_tokens': 28500,
                'output_tokens': 2048, 'total_tokens': 30548,
                'adapter_metadata': {'done': True, 'done_reason': 'length'}}


class DevelopmentRuntimeProbeTests(unittest.TestCase):
    def setUp(self):
        FixtureRuntime.calls = []
        self.verification = json.loads((probe.ROOT / 'data/gemma3_local_verification_v1.json').read_text())
        self.manifest = {'inputs': [{'paper_id': 'DEVELOPMENT-fixture', 'abstract': 'Fixture development evidence'}]}

    def request(self, path, payload=None):
        if path == '/api/version': return {'version': 'fixture'}
        if path == '/api/tags': return {'models': [{'name': 'gemma3:12b', 'digest': self.verification['digest_verification']['api_tags_digest_raw']}]}
        if path == '/api/show': return {'fixture': True}
        if path == '/api/ps': return {'models': [{'name': 'gemma3:12b', 'context_length': 32768}]}
        raise AssertionError(path)

    def run_fixture(self, directory, request=None):
        with patch('development_runtime_probe.load_development_manifest', return_value=(self.manifest, 'a' * 64)), \
             patch('development_runtime_probe._load_verified_source_rows'), \
             patch('development_runtime_probe.tokenizer_metadata_summary', return_value=self.verification['tokenizer']):
            return probe.run_probe(directory, request=request or self.request, client_factory=FixtureRuntime)

    def test_actual_passed_report_is_bound_to_observed_backend_without_rewriting_history(self):
        from researcher_approval import digest, file_digest
        cfg=json.loads((probe.ROOT/'config.json').read_text())
        path=probe.ROOT/'data/development_runtime_probe_v1/report_02.json'
        report=json.loads(path.read_text())
        self.assertEqual(report['report_sha256'],digest({k:v for k,v in report.items() if k!='report_sha256'}))
        self.assertEqual(cfg['generation']['development_runtime_probe_report_sha256'],file_digest(path))
        self.assertEqual(cfg['generation']['backend_version'],'0.40.16')
        self.assertEqual(probe.validate_runtime_evidence(cfg,root=probe.ROOT.parent),[])
        cfg['generation']['backend_version']='0.40.15'
        self.assertTrue(probe.validate_runtime_evidence(cfg,root=probe.ROOT.parent))

    def test_probe_counts_and_limit_pressure_are_checkpointed_and_resumable(self):
        with tempfile.TemporaryDirectory() as directory:
            report = self.run_fixture(directory)
            self.assertEqual(report['status'], 'passed')  # MOCK ONLY, stored outside the repository
            self.assertEqual(report['actual_development_prompt_tokens'], 150)
            self.assertEqual(report['actual_long_prompt_tokens'], 28500)
            self.assertEqual(report['actual_output_tokens'], 2048)
            self.assertTrue(report['context_guard_verified'])
            count = len(FixtureRuntime.calls)
            again = self.run_fixture(directory)
            self.assertEqual(again['status'], 'passed')
            self.assertEqual(len(FixtureRuntime.calls), count)
            self.assertTrue((Path(directory) / 'report_01.json').exists())
            self.assertTrue((Path(directory) / 'report_02.json').exists())

    def test_unreachable_runtime_reports_missing_counts_instead_of_success(self):
        def denied(*args): raise RuntimeError('fixture connection denied')
        with tempfile.TemporaryDirectory() as directory:
            report = self.run_fixture(directory, denied)
            self.assertEqual(report['status'], 'blocked_or_failed')
            self.assertIsNone(report['actual_development_prompt_tokens'])
            self.assertFalse(FixtureRuntime.calls)
            self.assertFalse(report['confirmatory_experiment'])

    def test_blocked_real_attempt_cannot_be_registered_as_success(self):
        from researcher_approval import file_digest
        cfg = json.loads((probe.ROOT / 'config.json').read_text())
        path = probe.ROOT / 'data/development_runtime_probe_v1/report_01.json'
        cfg['generation']['development_runtime_probe_report'] = str(path.relative_to(probe.ROOT.parent))
        cfg['generation']['development_runtime_probe_report_sha256'] = file_digest(path)
        self.assertTrue(probe.validate_runtime_evidence(cfg, root=probe.ROOT.parent))

    def test_runtime_evidence_validation_binds_source_counts_and_model_identity(self):
        from researcher_approval import digest, file_digest
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); data = root / 'E6/data'; data.mkdir(parents=True)
            manifest = data / 'development_manifest_v2.json'
            manifest.write_text(json.dumps({'inputs': [{'paper_id': 'DEVELOPMENT-fixture'}]}))
            (data / 'gemma3_local_verification_v1.json').write_text(json.dumps(self.verification))
            report = {'status': 'passed', 'scope': 'DEVELOPMENT_only_runtime_verification',
                'confirmatory_experiment': False, 'settings': probe.SETTINGS,
                'development_manifest_sha256': file_digest(manifest), 'development_input_id': 'DEVELOPMENT-fixture',
                'output_limit_verified': True, 'prompt_accounting_parity': True, 'context_guard_verified': True,
                'actual_development_prompt_tokens': 150, 'actual_long_prompt_tokens': 28500,
                'actual_output_tokens': 2048, 'context_allocation': 32768,
                'steps': {'01_identity': {'tag_digest': self.verification['digest_verification']['api_tags_digest_raw'],
                    'tokenizer_metadata_sha256': self.verification['tokenizer']['metadata_sha256'], 'ollama_version': 'fixture'},
                    '02_development_prompt_count': {'input_tokens': 150},
                    '03_long_context_count': {'input_tokens': 28500},
                    '04_output_pressure': {'input_tokens': 28500, 'output_tokens': 2048,
                                          'adapter_metadata': {'done_reason': 'length'}}}}
            report['report_sha256'] = digest(report)
            path = data / 'fixture-only.json'; path.write_text(json.dumps(report))
            cfg = {'generation': {'model': 'gemma3:12b', 'backend_version': 'fixture', 'context_limit': 32768,
                    'max_output_tokens': 2048, 'development_runtime_probe_report': 'E6/data/fixture-only.json',
                    'development_runtime_probe_report_sha256': file_digest(path)}}
            self.assertEqual(probe.validate_runtime_evidence(cfg, root=root), [])
            cfg['generation']['context_limit'] = 8192
            self.assertTrue(probe.validate_runtime_evidence(cfg, root=root))

    def test_pending_runtime_registration_cannot_authorize_final_execution(self):
        self.assertTrue(probe.validate_runtime_evidence({'generation': {}}, root=probe.ROOT.parent))
        self.assertTrue(probe.validate_runtime_evidence({'generation': []}, root=probe.ROOT.parent))
