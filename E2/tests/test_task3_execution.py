import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,Mock
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from task3_plan import sha_file,sha_text,write_rows,dump,materialize,validate_claims
from task3_execution import load_plan,status,embed,export,open_cache,put_vector,vector,authorize,model_key
from task3_novelty import novelty_scores,unit_rows
from human_check import ridge_path,ridge_predict,ALPHAS


def fixture(folder):
    source=folder/'source.jsonl'
    write_rows(source,[{'id':'h1','content':{'abstract':'abstract A','title':'DO NOT ENCODE TITLE'}},
        {'id':'h2','content':{'abstract':'abstract A'}}])
    test=folder/'benchmark.jsonl';write_rows(test,[{'forum_id':'t1','abstract':'abstract B','label':'SECRET','rating':999}])
    sources={'history':{'path':str(source),'kind':'openreview','sha256':sha_file(source)},
             'test':{'path':str(test),'kind':'prepared_test','sha256':sha_file(test)}}
    items=[{'key':pid,'forum_id':pid,'source':split,'split':split,'text_sha256':sha_text(s)}
           for pid,split,s in [('h1','history','abstract A'),('h2','history','abstract A'),('t1','test','abstract B')]]
    write_rows(folder/'embedding_items.jsonl',items);write_rows(folder/'history_targets.jsonl',[])
    write_rows(folder/'claim_requests.jsonl',[]);protocol=folder/'protocol.md';protocol.write_text('protocol')
    p={'sources':sources,'protocol_path':str(protocol),'protocol_sha256':sha_file(protocol),
       'items_sha256':sha_file(folder/'embedding_items.jsonl'),'targets_sha256':sha_file(folder/'history_targets.jsonl'),
       'claim_requests_sha256':sha_file(folder/'claim_requests.jsonl'),'claims_sha256':None,
       'benchmark_path':str(test),'history_count':2,'test_count':1,'claim_papers':0,
       'model_inventory':{'assets':{}},'provenance':{'input':'abstract_only'}}
    dump(folder/'plan.json',p);return p,items

class Task3ExecutionTests(unittest.TestCase):
    def test_unauthorized_job_never_loads_model(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);fixture(folder);auth=folder/'auth.json';dump(auth,{'authorize_inference':False})
            factory=Mock()
            with self.assertRaisesRegex(ValueError,'not authorized'):embed(folder,auth,limit=1,encoder_factory=factory)
            factory.assert_not_called();self.assertFalse((folder/'task3_vectors.sqlite3').exists())
    def test_dry_run_never_creates_cache(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);fixture(folder);factory=Mock()
            r=embed(folder,None,limit=0,encoder_factory=factory)
            self.assertEqual(r['complete_items'],0);factory.assert_not_called()
            self.assertFalse((folder/'task3_vectors.sqlite3').exists())
    def test_batch_dedup_resume_export_and_raw_cls(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);fixture(folder);calls=[]
            def encode(texts):calls.extend(texts);return np.stack([np.full(768,len(s),np.float32) for s in texts])
            factory=Mock(return_value=encode)
            with patch('task3_execution.authorize',return_value={}):
                r=embed(folder,None,limit=1,batch_size=2,encoder_factory=factory)
                self.assertEqual(r['complete_items'],2)
                r=embed(folder,None,limit=10,batch_size=2,encoder_factory=factory)
                self.assertEqual(r['complete_items'],3)
                before=factory.call_count;embed(folder,None,limit=10,encoder_factory=factory)
                self.assertEqual(factory.call_count,before)
            self.assertEqual(calls,['abstract A','abstract B'])
            export(folder,folder/'export')
            arrays=np.load(folder/'export/embeddings.npz')
            self.assertEqual(arrays['history_embeddings'].shape,(2,768))
            self.assertEqual(arrays['test_embeddings'][0,0],len('abstract B'))
            self.assertFalse(np.isclose(np.linalg.norm(arrays['test_embeddings'][0]),1))
            binding=json.loads((folder/'export/bindings.json').read_text())
            self.assertEqual(binding['ids']['history'],['h1','h2'])
    def test_missing_vectors_cannot_export_partial_matrix(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);fixture(folder)
            with self.assertRaisesRegex(ValueError,'incomplete'):export(folder,folder/'out')
            self.assertFalse((folder/'out').exists())
    def test_cache_corruption_and_conflicts_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            c=open_cache(Path(d),write=True);v=np.ones(768,np.float32)
            put_vector(c,'model','text',v);c.commit()
            with self.assertRaises(ValueError):put_vector(c,'model','text',v*2)
            c.execute("UPDATE vectors SET checksum='wrong'");c.commit()
            with self.assertRaises(ValueError):vector(c,'model','text')
            c.close()
    def test_source_changed_stops_before_encoder(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);p,items=fixture(folder);(folder/'source.jsonl').write_text('changed')
            with self.assertRaisesRegex(ValueError,'fingerprint'):materialize(items,p['sources'])
    def test_protocol_and_plan_hashes_are_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);p,_=fixture(folder)
            (folder/'protocol.md').write_text('changed')
            with self.assertRaises(ValueError):load_plan(folder)
    def test_priority_failure_before_import_or_model(self):
        from task3_execution import batched_cpu_encoder
        with patch('task3_execution.os.nice',side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):batched_cpu_encoder({})
    def test_claims_require_exact_source_and_no_duplicates(self):
        abstract='A. B. C. D.';b=[{'forum_id':'f','abstract':abstract}]
        r={'forum_id':'f','abstract_sha256':sha_text(abstract),'provenance':'saved extraction',
           'claims':[{'claim':s,'evidence':s} for s in ['A.','B.','C.','D.']]}
        self.assertEqual(len(validate_claims([r],b)),1)
        r['claims'][0]['evidence']='not present'
        with self.assertRaises(ValueError):validate_claims([r],b)
    def test_evaluation_authorization_needs_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);p,_=fixture(folder)
            auth={'authorize_evaluation':True,'plan_sha256':sha_file(folder/'plan.json'),
                  'protocol_sha256':p['protocol_sha256'],'authorization_source':'unit fixture',
                  'preregistration_verified':True,'post_cutoff_verified':True}
            dump(folder/'auth.json',auth)
            with patch('task3_execution.subprocess.check_output',return_value=b'protocol'):
                with self.assertRaisesRegex(ValueError,'eligibility evidence'):authorize(folder,p,folder/'auth.json','evaluation')

class Task3NumericalTests(unittest.TestCase):
    def test_ridge_path_matches_independent_solve(self):
        rng=np.random.default_rng(321);x=rng.normal(size=(21,5));v=rng.normal(size=(8,5));y=rng.normal(size=21)
        x[:,4]=1;v[:,4]=1
        path=ridge_path(x,y,v)
        for alpha in ALPHAS:np.testing.assert_allclose(path[alpha],ridge_predict(x,y,v,alpha),rtol=1e-8,atol=1e-9)
    def test_blocked_novelty_matches_existing_formulas(self):
        from novelty import _rnd_score
        rng=np.random.default_rng(27);r=unit_rows(rng.normal(size=(18,7)));t=unit_rows(rng.normal(size=(3,7)))
        claims=[unit_rows(rng.normal(size=(4,7))) for _ in t]
        result=novelty_scores(t,r,claims,block_size=2)
        # Align normalization with new abstract-only raw-CLS path.
        r=unit_rows(r);t=unit_rows(t);claims=[unit_rows(c) for c in claims]
        for i,q in enumerate(t):
            y=float(1-np.clip(np.einsum('ik,k->i',r,q),-1,1).max())
            n=float(1-np.clip(np.einsum('ik,jk->ij',claims[i],r),-1,1).max(axis=1).mean())
            self.assertAlmostEqual(result['Y'][i],y,places=6);self.assertAlmostEqual(result['N'][i],n,places=6)
            self.assertAlmostEqual(result['yours'][i],.75*y+.25*n,places=6)
            self.assertAlmostEqual(result['density'][i],_rnd_score(q,r),places=6)
    def test_bad_novelty_inputs_fail_closed(self):
        with self.assertRaises(ValueError):unit_rows(np.zeros((2,3)))
        with self.assertRaises(ValueError):novelty_scores(np.ones((1,3)),np.ones((2,3)),[],block_size=1)

class RidgeBaselineIntegrationTests(unittest.TestCase):
    def test_chronological_path_selection_matches_fold_solves(self):
        from human_check import quality_scores
        rng=np.random.default_rng(52);x=rng.normal(size=(12,4));y=rng.normal(size=12)
        years=np.repeat([2022,2023,2024,2025],3)
        records=[{'forum_id':str(i),'year':int(years[i]),'mean_rating':y[i]} for i in range(12)]
        _,selection=quality_scores(records,x,['test'],np.ones((1,4)))
        losses={}
        for a in ALPHAS:
            sq=[]
            for year in (2023,2024,2025):
                train=years<year;valid=years==year
                sq.extend((ridge_predict(x[train],y[train],x[valid],a)-y[valid])**2)
            losses[a]=np.mean(sq)
            self.assertAlmostEqual(selection['validation_mse'][a],losses[a],places=7)
        self.assertEqual(selection['alpha'],min(ALPHAS,key=lambda a:losses[a]))
    def bundle(self,tmp):
        from abstract_embeddings import PROVENANCE
        protocol=tmp/'protocol.md';protocol.write_text('fixture')
        hist=[{'forum_id':str(i),'year':2022+i//2,'title':'History '+str(i),'review_count':2,
            'mean_rating':float(i%3),'published':f'{2021+i//2}-09-01T00:00:00Z',
            'venue':'ICLR','abstract_sha256':sha_text(str(i))} for i in range(8)]
        bench=[{'id':i,'forum_id':'test'+str(i),'title':'Test '+str(i),'label':['NEGATIVE','POSITIVE'][i],
            'idea':'edited','abstract':'original '+str(i),'published':'2025-10-08T00:00:00Z','rating':2+i,'contribution':2+i} for i in range(2)]
        bundle={'history':hist,'history_ids':[r['forum_id'] for r in hist],'benchmark':bench,
            'test_ids':[r['forum_id'] for r in bench], 'embedding_provenance':PROVENANCE,
            'history_abstract_sha256':[r['abstract_sha256'] for r in hist],
            'test_abstract_sha256':[sha_text(r['abstract']) for r in bench],
            'novelty_scores':{m:[0.,1.] for m in ('Y','N','yours','density')},
            'authorization':{'prospective_preregistration_verified':True,'post_cutoff_verified':True,
                'protocol_sha256':sha_file(protocol),'encoder_cutoff':'2024-12-31T23:59:59Z'}}
        rng=np.random.default_rng(61);arrays={'history_embeddings':rng.normal(size=(8,3)),'test_embeddings':rng.normal(size=(2,3))}
        return bundle,arrays,protocol
    def test_test_ratings_are_not_baseline_inputs(self):
        from evaluate_human_check import evaluate
        from human_check import quality_scores
        with tempfile.TemporaryDirectory() as d:
            b,a,p=self.bundle(Path(d));predictions=[]
            def capture(*args):
                result=quality_scores(*args);predictions.append(result[0]);return result
            with patch('evaluate_human_check.quality_scores',side_effect=capture),patch('evaluate_human_check.comparison',return_value={}):
                evaluate(b,a,p)
                for r in b['benchmark']:r['rating']=999;r['contribution']=-999
                evaluate(b,a,p)
            np.testing.assert_array_equal(predictions[0],predictions[1])
    def test_later_review_paper_cannot_enter_baseline(self):
        from evaluate_human_check import evaluate
        with tempfile.TemporaryDirectory() as d:
            b,a,p=self.bundle(Path(d));b['history'][0]['published']=b['benchmark'][0]['published']
            with patch('evaluate_human_check.quality_scores') as fit:
                with self.assertRaisesRegex(ValueError,'earlier same-venue'):evaluate(b,a,p)
                fit.assert_not_called()
    def test_wrong_historical_abstract_binding_rejected(self):
        from evaluate_human_check import evaluate
        with tempfile.TemporaryDirectory() as d:
            b,a,p=self.bundle(Path(d));b['history_abstract_sha256'][0]='wrong'
            with self.assertRaisesRegex(ValueError,'history abstract'):evaluate(b,a,p)
    def test_code_fingerprint_invalidates_stale_plan(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);p,_=fixture(folder);code=folder/'code.py';code.write_text('original')
            p['code_sha256']={str(code):sha_file(code)};dump(folder/'plan.json',p);code.write_text('changed')
            with self.assertRaisesRegex(ValueError,'execution code changed'):load_plan(folder)
