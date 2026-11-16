import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from M.evidence import iter_bound,read_bound,assertion
from M.ingestion import recover_review,verify_outcome
from M.cohorts import separate_cohorts,link_question_outcome
from M.semantic_baselines import SemanticBaselines
from M.encoders import MissingEmbeddingError

class IngestionTests(unittest.TestCase):
    def setup_source(self,rows):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);p=Path(tmp.name)/'source.jsonl'
        p.write_text(''.join(json.dumps(r)+'\n' for r in rows));return p,list(iter_bound(p))

    def review(self):return {'id':'review1','forum':'p1','_paper_forum':'p1','_kind':'Official_Review','_year':2023,'cdate':1666605267423,'tmdate':1666605267423,'odate':None,'content':{'recommendation':'5: marginally below the acceptance threshold'}}

    def test_exact_source_field_and_tampering(self):
        p,rs=self.setup_source([{'value':2}]);r,b=rs[0]
        self.assertEqual(assertion(b,['value'],2)['value'],2)
        with self.assertRaises(ValueError):assertion(b,['value'],3)
        p.write_text('{"value":3}\n')
        with self.assertRaises(ValueError):read_bound(b)

    def test_genuine_rating_not_dated_by_creation(self):
        _,rs=self.setup_source([self.review()]);r,b=rs[0];o=recover_review(r,b)
        self.assertEqual(o['value'],5);self.assertIsNone(o['observed_at']);self.assertFalse(o['usable_for_fitting'])
        self.assertTrue(verify_outcome(o));o['observed_at']='2022-10-24'
        with self.assertRaises(ValueError):verify_outcome(o)

    def test_public_current_version_and_wrapped_rating(self):
        r=self.review();r['odate']=r['tmdate']+1000;r['content']={'rating':{'value':'7: Accept'}}
        _,rs=self.setup_source([r]);o=recover_review(*rs[0]);self.assertEqual(o['value'],7);self.assertIsNotNone(o['observed_at'])
        self.assertTrue(verify_outcome(o))

    def test_public_release_before_revision_not_value_date(self):
        r=self.review();r['odate']=r['tmdate']-1000
        _,rs=self.setup_source([r]);self.assertIsNone(recover_review(*rs[0])['observed_at'])

    def test_comment_and_identity_mismatch(self):
        r=self.review();r['_kind']='Official_Comment';_,rs=self.setup_source([r]);self.assertIsNone(recover_review(*rs[0]))
        r=self.review();r['_paper_forum']='different';_,rs=self.setup_source([r])
        with self.assertRaises(ValueError):recover_review(*rs[0])

    def test_cohorts_independent_missing_evidence_rejected(self):
        r=separate_cohorts([{'test':'S1','candidate_id':'c1','assertions':{}}])
        self.assertEqual(r['cohorts']['S1'],[]);self.assertEqual(len(r['excluded']['S1']),1)
        self.assertEqual(r['excluded']['H3'],[])

    def test_outcome_cross_paper_and_no_date_rejected(self):
        _,rs=self.setup_source([self.review()]);o=recover_review(*rs[0])
        q={'paper_id':'different','question':'Does x improve y?','published':'2022-01-01','available_at':'2022-01-01','input_paper_ids':[]}
        _,qs=self.setup_source([q]);r,b=qs[0];question={k+'_evidence':assertion(b,[k],v) for k,v in q.items()};question['question_id']='q'
        with self.assertRaises(ValueError):link_question_outcome(question,o)

    def test_semantic_cache_exact_no_inference(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);p=Path(tmp.name)/'cache.json'
        text='Does x improve y?';obj={'model_id':'fixture-model','revision':'fixed','dimension':2,'records':[{'text':text,'sha256':hashlib.sha256(text.encode()).hexdigest(),'vector':[1.,0.]}]};p.write_text(json.dumps(obj));before=p.read_bytes()
        reader=SemanticBaselines(p)
        self.assertFalse(reader.vector(text)['training_cutoff_verified']);self.assertEqual(reader.similarity(text,text)['cosine'],1)
        with self.assertRaises(MissingEmbeddingError):reader.vector('missing')
        reader.close();self.assertEqual(p.read_bytes(),before)

    def test_recovered_all_values_source_verified(self):
        p=Path(__file__).resolve().parents[1]/'data/ingestion_v2/review_outcomes.jsonl'
        if not p.exists():self.skipTest('local recovery artifact absent')
        count=0
        with p.open() as f:
            for line in f:
                self.assertTrue(verify_outcome(json.loads(line)));count+=1
        self.assertEqual(count,570)

    def test_source_bound_false_near_miss_label_is_valid(self):
        d={'question_id':'q','question':'Does x improve y?','paper_id':'p',
           'posed_at':'2025-08-01','available_at':'2025-08-01','original_inputs':['a'],
           'shuffled_inputs':['b'],'decoy_question':'Does z improve y?',
           'topic_verified':True,'human_verified':True,'minimal_paraphrase_label':True,
           'near_miss_label':False,'semantic_model_cutoff_verified':True}
        _,rs=self.setup_source([d]);r,b=rs[0]
        c={'test':'S1','candidate_id':'synthetic-admission-only','assertions':{k:assertion(b,[k],v) for k,v in d.items()}}
        out=separate_cohorts([c]);self.assertEqual(len(out['cohorts']['S1']),1)
        self.assertEqual(out['cohorts']['H3'],[])
