import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from M.evaluation import TESTS,CONTROLS,READOUTS,UNITS,evaluate,bootstrap
from M.freeze import freeze


def fixtures(test):
    records=[]
    for i in range(8):
        r={'record_id':str(i),'unit_id':str(i),'unit_kind':UNITS[test],'question_ids':['q'+str(i)],
           'dataset_kind':'synthetic','posed_at':'2025-08-01','available_at':'2025-08-01',
           'model_trained_until':'2023-12-31','selected_on':'2024-validation-only',
           'provenance':{'source':'synthetic fixture, no real labels'},'input_versions':[],
           'control_evidence':{'original_inputs':['p1'],'empty_inputs':[],'shuffled_inputs':['p2'],'same_topic_verified':True,'topic_source':'fixture'},
           'normalization_provenance':'fixed synthetic [0,1] coordinates',
           'label_evidence':{'source':'synthetic fixture','text':'fixture','sha256':hashlib.sha256(b'fixture').hexdigest(),'observed_at':'2025-09-01'},
           'length_matched':True,'tokens_a':20,'tokens_b':20,'label':1,'same_topic_verified':True,
           'ceiling':.9,'ceiling_evidence':'synthetic fixture only','year_Y':2023,'model_Y_minus_1_until':'2022-12-31',
           'system_a':'s1','system_b':'s2','seed_ids_a':['a','b','c'],'seed_ids_b':['a','b','c'],'paper_a_date':'2025-08-01','paper_b_date':'2025-09-01'}
        if test=='I1':p={k:{'near_miss_drift':.8,'paraphrase_drift':.1} for k in READOUTS}
        if test=='I3':p={'scores':{'Q_peer_review':1,'N_Y':1},'B-LEN':-1}
        if test=='S1':
            r['task']='near_miss' if i%2 else 'minimal_paraphrase';r['label']=bool(i%2);p={'decision':r['label'],'B-Q':not r['label']}
        if test=='A1':r['axiom']='partial_coverage' if i%2 else 'concentration';p={'scores':{'Y':1,'density':1,'N':-1,'custom':1}}
        if test=='H1':p={'score_a':i+1,'score_b':8-i,'B-Q_a':8-i,'B-Q_b':i+1};r['label']=1 if i>3 else -1
        if test=='H3':p={'score':i,'B-Q':8-i};r['label']=i
        if test=='O1':r['labels']={'peer_review':1,'later_community_use':-1};p={'peer_review':1,'later_community_use':-1,'B-Q':{'peer_review':-1,'later_community_use':1}}
        if test=='O2':r['labels']={'outcome':1};p={'outcome':1,'B-TF':{'outcome':-1}}
        if test=='T1':p={k:{'Y':.5,'Y_minus_1':.501} for k in READOUTS}
        if test in ('S1','A1'):r['unit_id']=str(i//2)
        r['predictions']={c:copy.deepcopy(p) for c in CONTROLS};records.append(r)
    return records

class EvaluationTests(unittest.TestCase):
    def test_all_nine_synthetic_runners(self):
        for test in TESTS:
            with self.subTest(test=test):
                r=evaluate(test,fixtures(test),synthetic=True,draws=40)
                self.assertEqual(r['status'],'SYNTHETIC_ONLY',r)
                self.assertFalse(r['heldout_evaluated']);self.assertEqual(set(r['controls']),set(CONTROLS))

    def test_real_gate_and_missing_labels(self):
        for t in TESTS:self.assertEqual(evaluate(t,fixtures(t))['status'],'BLOCKED')
        rs=fixtures('H3');del rs[0]['label_evidence']
        self.assertEqual(evaluate('H3',rs,synthetic=True)['status'],'BLOCKED')

    def test_controls_temporal_and_bootstrap_units(self):
        for change in ('future','control','unit','real'):
            rs=fixtures('I1')
            if change=='future':rs[0]['input_versions']=[{'published':'2026-01-01','available_at':'2026-01-01'}]
            if change=='control':del rs[0]['predictions']['empty']
            if change=='unit':rs[0]['unit_kind']='independent_row'
            if change=='real':rs[0]['dataset_kind']='real'
            self.assertEqual(evaluate('I1',rs,synthetic=True)['status'],'BLOCKED')

    def test_paired_and_deterministic_intervals(self):
        rs=fixtures('O2');a=bootstrap('O2',rs,'original',50);b=bootstrap('O2',rs,'original',50)
        self.assertEqual(a,b);self.assertEqual(a['outcome']['estimate'],1)
        for r in rs:r['predictions']['original']['B-TF']['outcome']=1
        self.assertEqual(bootstrap('O2',rs,'original',50)['outcome']['ci95'],[0,0])

    def test_duplicate_and_cross_unit_shared_question(self):
        rs=fixtures('O2');rs[1]['question_ids']=rs[0]['question_ids']
        self.assertEqual(evaluate('O2',rs,synthetic=True)['status'],'BLOCKED')
        rs=fixtures('O2');rs[1]['record_id']=rs[0]['record_id']
        self.assertEqual(evaluate('O2',rs,synthetic=True)['status'],'BLOCKED')

    def test_candidate_lock_determinism(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(__file__).resolve().parents[2]
            a=Path(d)/'a';b=Path(d)/'b';freeze(root,a);freeze(root,b)
            self.assertEqual({p.name:p.read_bytes() for p in a.iterdir()},{p.name:p.read_bytes() for p in b.iterdir()})
            sums=json.loads((a/'SHA256SUMS.json').read_text())
            for name,sha in sums.items():self.assertEqual(hashlib.sha256((a/name).read_bytes()).hexdigest(),sha)

    def test_null_identity_prediction_is_not_false(self):
        rs=fixtures('S1');rs[0]['predictions']['original']['decision']=None
        self.assertEqual(evaluate('S1',rs,synthetic=True)['status'],'BLOCKED')

    def test_unknown_quality_coordinate_blocks_invariance(self):
        rs=fixtures('I1');rs[0]['predictions']['original']['Q_peer_review']['paraphrase_drift']=None
        self.assertEqual(evaluate('I1',rs,synthetic=True)['status'],'BLOCKED')
