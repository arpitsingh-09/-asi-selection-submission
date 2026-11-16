import sys
import unittest
import tempfile
import json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from human_check import historical, normalize, resolve, auc, comparison, ridge_predict, quality_scores, eligibility
from evaluate_human_check import evaluate

class HumanCheckTests(unittest.TestCase):
    def record(self):
        return {'id':0,'idea':'abstract','label':'POSITIVE','metadata':{'title':'A title','rating':6,'contribution':3}}
    def test_nested(self):
        self.assertEqual(normalize(self.record())['title'],'A title')
        r=self.record();r['title']='conflict'
        with self.assertRaises(ValueError):normalize(r)
    def test_historical_schema_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            for year in range(2022,2026):
                p=Path(tmp)/f'iclr_{year}';p.mkdir()
                paper={'id':str(year),'content':{'title':'Paper '+str(year),'abstract':'text'}}
                (p/'papers.jsonl').write_text(json.dumps(paper)+'\n')
                reviews=[]
                for i in range(2):
                    r={'id':str(i),'forum':str(year),'content':{'recommendation' if year<2024 else 'rating':{'value':'6: accept'}}}
                    r.update({'invitation':'ICLR/-/Official_Review'} if year<2024 else {'invitations':['ICLR/-/Official_Review']})
                    reviews.append(r)
                (p/'reviews.jsonl').write_text('\n'.join(map(json.dumps,reviews)))
            records,excluded=historical(tmp,[])
            self.assertEqual(len(records),4)
            self.assertTrue(all(r['mean_rating']==6 for r in records))

    def test_auc_ties_and_orientation(self):
        self.assertEqual(auc([0,1],[1,1]),.5)
        self.assertEqual(auc([0,1],[0,1]),1)
        self.assertEqual(auc([0,1],[1,0]),0)
        with self.assertRaises(ValueError):auc([0,1],[0,np.nan])
    def test_paired_bootstrap(self):
        r=comparison([0,0,1,1],{'Y':[0,1,2,3],'quality':[0,1,2,3]},replicates=50)
        self.assertEqual(r['measures']['Y']['difference_ci95'],[0,0])
    def test_ridge_training_only(self):
        x=np.array([[0.,1],[1,1],[2,1]])
        p=ridge_predict(x,np.array([1,3,5]),np.array([[3.,1]]),1)
        # standardized x has sum of squares 3; ridge slope shrinks by 3/4
        np.testing.assert_allclose(p,[6.])
        p2=ridge_predict(x,np.array([1,3,5]),np.array([[3.,1],[1000,1]]),1)
        self.assertAlmostEqual(p[0],p2[0])
    def test_chronological_ridge_selection(self):
        records=[{'forum_id':str(i),'year':2022+i//2,'mean_rating':float(i%3)} for i in range(8)]
        x=np.arange(16,dtype=float).reshape(8,2)
        predictions,selection=quality_scores(records,x,['new'],np.array([[3.,4.]]))
        self.assertEqual(predictions.shape,(1,))
        self.assertEqual(len(selection['validation_mse']),9)
        self.assertTrue(np.isfinite(predictions).all())

    def test_test_overlap_rejected(self):
        with self.assertRaises(ValueError):
            quality_scores([{'forum_id':'test'}],np.zeros((1,2)),['test'],np.zeros((1,2)))
    def test_mapping_ambiguity(self):
        papers=[{'id':s,'content':{'title':'A TITLE'}} for s in ['a','b']]
        self.assertIsNone(resolve([normalize(self.record())],papers)[0]['forum_id'])
        self.assertEqual(resolve([normalize(self.record())],papers[:1])[0]['forum_id'],'a')
    def test_dates_not_inferred(self):
        self.assertTrue(eligibility({},'2024-01-01T00:00:00Z').startswith('unknown'))
        self.assertEqual(eligibility({'published':'2025-01-01T00:00:00Z'},'2024-01-01T00:00:00Z'),'eligible')
    def test_prereg_gate_before_inputs(self):
        with self.assertRaisesRegex(ValueError,'preregistration'):
            evaluate({'authorization':{}},{},Path('unused'))

if __name__=='__main__':unittest.main()
