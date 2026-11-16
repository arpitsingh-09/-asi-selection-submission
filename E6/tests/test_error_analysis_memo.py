import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import error_analysis_memo as m
from evaluation import ARMS

class ErrorAnalysisMemoTests(unittest.TestCase):
    def settings(self):
        config=json.loads((m.ROOT/'E6/config.json').read_text());evaluation=json.loads((m.ROOT/'E6/evaluation_config.json').read_text())
        # Small synthetic test run only; actual execution uses frozen 10,000.
        evaluation['paired_bootstrap']['replicates']=25
        return config,evaluation
    def test_frozen_sample_includes_0007_and_both_testbeds(self):
        config,_=self.settings();train=json.loads((m.ROOT/config['dataset']['data_generation_proposal']).read_text())
        lit=json.loads((m.ROOT/config['dataset']['literature_selected_manifest']).read_text())
        chosen=m.frozen_sample(config,{'data':[r['input_set_id'] for r in train['input_sets']],'literature':lit['selected_input_set_ids']})
        self.assertEqual(len(chosen['data']),10);self.assertEqual(len(chosen['literature']),10)
        self.assertTrue(any(':TRAIN-SET:0007:' in u for u in chosen['data']))
    def sources(self,bed):
        if bed=='data':return [{'generation_input_set_id':f'fixture:TRAIN-SET:{i}','evaluations':{a:{'status':'evaluated','metrics':{'fixture':i+j/10}} for j,a in enumerate(ARMS)}} for i in range(3)]
        return [{'input_set_id':f'fixture-lit:{i}','records':[{'input_set_id':f'fixture-lit:{i}','stage':'verified_input_set_scalar','evaluation_input':{'field':'fixture'},'provenance':{'arm':a},'status':'succeeded','parsed_output':{'value':i+j/10}} for j,a in enumerate(ARMS)]} for i in range(3)]
    def test_frozen_statistical_adapter_both_beds_all_21_contrasts(self):
        config,evaluation=self.settings()
        for bed in ('data','literature'):
            r=m.summarize_metric(self.sources(bed),bed,'fixture',config,evaluation)
            self.assertEqual(len(r['comparisons']),21);self.assertEqual(len(r['arm_estimates']),7)
            difference=r['comparisons']['D-minus-QH']
            self.assertAlmostEqual(difference['point_estimate'],-.1)
            self.assertAlmostEqual(difference['interval'][0],-.1)
    def test_missing_failed_observations_never_zero(self):
        config,evaluation=self.settings();sources=self.sources('data')
        sources[0]['evaluations']['D']={'status':'generation_missing_or_failed'}
        r=m.summarize_metric(sources,'data','fixture',config,evaluation)
        self.assertEqual(r['comparisons']['D-minus-QH']['included_count'],2)
        cell=next(c for c in r['cells'] if c['input_set_id']=='fixture:TRAIN-SET:0' and c['arm']=='D')
        self.assertIsNone(cell['value'])
    def packet(self):
        packet={'testbed':'data','input_set_id':'fixture:TRAIN-SET:0007','packet_sha256':'fixture','source_evidence':{'text':'actual fixture source'},'arms':{a:{'generation_status':'missing','generation_entry':None} for a in ARMS}}
        return packet
    def review(self):
        return {'testbed':'data','input_set_id':'fixture:TRAIN-SET:0007','packet_sha256':'fixture','reviewer_id':'fixture-human','reviewed_at_utc':'2020-01-01T00:00:00Z','end_to_end_review_completed':True,'notes':'fixture inspection only',
            'arms':{a:{'status':'missing_not_evaluable','notes':'fixture missing cell',**{i:None for i in m.ISSUES},'examples':[]} for a in ARMS}}
    def test_missing_review_cells_stay_not_evaluable(self):
        r=m.review_status([self.packet()],[self.review()])
        self.assertEqual(r['reviewed_input_sets'],1);self.assertEqual(r['coded_arm_cells'],0)
        self.assertFalse(r['human_error_analysis_complete'])
        review=self.review();review['arms']['D']['redundancy']=False
        with self.assertRaisesRegex(ValueError,'not evaluable'):m.review_status([self.packet()],[review])
    def test_review_examples_must_be_source_grounded(self):
        packet=self.packet();packet['arms']['D']['generation_status']='succeeded'
        review=self.review();review['arms']['D'].update(status='reviewed',**{i:False for i in m.ISSUES})
        review['arms']['D']['redundancy']=True;review['arms']['D']['examples']=[{'quote':'fabricated example','explanation':'fixture'}]
        with self.assertRaisesRegex(ValueError,'grounded'):m.review_status([packet],[review])
    def test_unavailable_native_metrics_and_questionless_denominators(self):
        self.assertIsNone(m.scalar({'status':'failed','parsed_output':{'value':0}},['parsed_output','value']))
        self.assertIsNone(m.scalar({'status':'succeeded','parsed_output':{'value':float('nan')}},['parsed_output','value']))
        self.assertEqual(m.secondary_metrics({}, {'output':{'hypotheses':[]}},'fixture')['already_asked_rate'],None)
    def test_memo_keeps_missing_results_pending_and_renders_reverse_contrast(self):
        config,evaluation=self.settings();analyses={}
        for bed in ('data','literature'):
            for metric in m.METRICS[bed]:analyses[bed,metric]=m.summarize_metric(self.sources(bed),bed,'fixture',config,evaluation)
        summary={'human_review':{'reviewed_input_sets':0}}
        text=m.memo_text(summary,analyses)
        self.assertIn('QH − D',text);self.assertIn('0.1 [0.1, 0.1]',text)
        self.assertIn('0/20',text)

if __name__=='__main__':unittest.main()
