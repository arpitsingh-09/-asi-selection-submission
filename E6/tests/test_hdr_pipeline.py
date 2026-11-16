import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hdr_pipeline as h
from researcher_approval import digest

class HDRPipelineTests(unittest.TestCase):
    def fixture(self):
        truth=['Fixture source rule A.','Fixture source rule B.'];sha='fixture-source-sha'
        features={name:{'ground_truth_indices':[i],'source_texts':[truth[i]]} for i,name in enumerate(('f1','f2'))}
        mapping={'approved_HDR_denominator':True,'reference_feature_ids':['f1','f2'],'feature_mapping':features,
            'feature_mapping_sha256':digest(features),'ground_truth_source_sha256':sha,
            'definition_provenance':{'author_id':'fixture-only','defined_at_utc':'2020-01-01T00:00:00Z','source_supported_justification':'synthetic test fixture'}}
        hypotheses=['Fixture generated rule.']*6
        form={'generation_input_set_id':'fixture:TRAIN-SET:0000','arm':'D','hypotheses':hypotheses,'hypotheses_sha256':digest(hypotheses)}
        payload={'generation_input_set_id':form['generation_input_set_id'],'arm':'D','hypotheses_sha256':form['hypotheses_sha256'],
            'reference_feature_ids':mapping['reference_feature_ids'],'feature_mapping':features,
            'discovered_feature_ids':['f1'],'relationship_scores':{'f1':0.5},
            'provenance':{'ground_truth_source_sha256':sha,'feature_mapping_sha256':digest(features),
                'judge_provenance':{'method':'fixture-only','judge_id':'fixture-judge','judged_at_utc':'2020-01-01T00:00:00Z','evidence':'synthetic fixture only'}}}
        return form,mapping,payload,truth,sha
    def test_true_HDR_formula_not_fourteen_reference_recall(self):
        form,mapping,payload,truth,sha=self.fixture()
        _,score,_=h.score_cell(form,mapping,payload,truth,sha)
        self.assertEqual(score['feature_discovery_rate'],0.5)
        self.assertEqual(score['relationship_correctness'],0.5)
        self.assertEqual(score['hypothesis_discovery_rate'],0.25)
    def test_absent_mapping_and_nonmatches_never_become_zero(self):
        form,mapping,payload,truth,sha=self.fixture()
        self.assertIsNone(h.score_cell(form,None,None,truth,sha)[1])
        _,score,evidence=h.score_cell(form,mapping,None,truth,sha)
        self.assertIsNone(score);self.assertIn('unknown',evidence['nonmatch_interpretation'])
    def test_full_literal_source_support_scores_objectively_with_justified_mapping(self):
        form,mapping,payload,truth,sha=self.fixture()
        form['hypotheses']=truth+['unrelated']*4;form['hypotheses_sha256']=digest(form['hypotheses'])
        _,score,_=h.score_cell(form,mapping,None,truth,sha)
        self.assertEqual(score['hypothesis_discovery_rate'],1)
    def test_pending_mapping_rejected(self):
        form,mapping,payload,truth,sha=self.fixture();mapping['approved_HDR_denominator']=False
        with self.assertRaisesRegex(ValueError,'pending'):h.score_cell(form,mapping,payload,truth,sha)
    def test_fabricated_objective_judgment_rejected(self):
        form,mapping,payload,truth,sha=self.fixture()
        payload['provenance']['judge_provenance']['method']='all_mapped_full_source_rules_literal_equality'
        with self.assertRaisesRegex(ValueError,'exact source support'):h.score_cell(form,mapping,payload,truth,sha)
    def test_foreign_hypotheses_and_missing_judge_provenance_rejected(self):
        form,mapping,payload,truth,sha=self.fixture();payload['hypotheses_sha256']='wrong'
        with self.assertRaisesRegex(ValueError,'bind'):h.score_cell(form,mapping,payload,truth,sha)
        payload['hypotheses_sha256']=form['hypotheses_sha256'];payload['provenance']['judge_provenance']['evidence']=None
        with self.assertRaisesRegex(ValueError,'evidence'):h.score_cell(form,mapping,payload,truth,sha)
    def test_actual_compilation_readiness_export_and_checkpoint_replay_no_network(self):
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.urlopen',side_effect=AssertionError('network prohibited')):
            output=Path(tmp)/'compile';report=h.compile_hdr(output)
            self.assertEqual(report['HDR_cells_required'],125);self.assertEqual(report['HDR_cells_scored'],0)
            self.assertEqual(len(report['terminal_missing_cells']),15)
            self.assertEqual(h.load_compilation(output),{})
            self.assertEqual(h.compile_hdr(output),report)
            checkpoint=next(p for p in output.glob('*.json') if len(p.stem)==20)
            row=json.loads(checkpoint.read_text());row['identity']='changed';checkpoint.write_text(json.dumps(row))
            with self.assertRaisesRegex(ValueError,'integrity'):h.load_compilation(output)
    def test_blind_review_groups_only_exact_sets_and_preserves_all_records(self):
        with tempfile.TemporaryDirectory() as tmp,patch('urllib.request.urlopen',side_effect=AssertionError('network prohibited')):
            output=Path(tmp)/'review';report=h.prepare_independent_review(output)
            groups=json.loads((output/'coordinator_case_mapping.json').read_text())
            forms,_=h.checked_forms()
            expected={(f['generation_input_set_id'],f['arm']):f['hypotheses'] for f in forms}
            seen=set()
            for group in groups:
                self.assertEqual(group['hypotheses_sha256'],digest(group['hypotheses']))
                for record in group['records']:
                    key=(record['generation_input_set_id'],record['arm'])
                    self.assertNotIn(key,seen);seen.add(key)
                    self.assertEqual(group['hypotheses'],expected[key])
            self.assertEqual(seen,set(expected))
            self.assertEqual(report['unique_review_sets'],107)
            self.assertIsNone(report['denominator'])
            self.assertEqual(report['human_judgments_created'],0)
            sheet=(output/'independent_review.md').read_text()
            self.assertEqual(sheet.count('Reviewer / UTC time:'),107)
            self.assertNotIn('TRAIN-SET:',sheet)

    def test_frozen_recovery_policy_is_not_an_HDR_semantic_policy(self):
        ev=json.loads((h.ROOT/'E6/evaluation_config.json').read_text())
        self.assertTrue(h.frozen_hdr_policy_errors({},ev))

if __name__=='__main__':unittest.main()
