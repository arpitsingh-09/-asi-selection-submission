"""Only synthetic vectors and temporary caches. No model assets are loaded."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from claim_sidecar import (prepare,load,status,encode,Overlay,Sidecar,binding,normalized,
                           validate_requests,sha,text_hash,MODEL,DIM,BASE_REV,ADAPTER_REV,SIDECAR)


class ClaimSidecarTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.original=self.root/'original.sqlite3';con=sqlite3.connect(self.original)
        con.execute('CREATE TABLE embeddings(model_id TEXT,text_hash TEXT,text_value TEXT,vector_json TEXT,PRIMARY KEY(model_id,text_hash))')
        self.controls=[]
        for i in range(3):
            text='control '+str(i);v=self.vector(text)
            con.execute('INSERT INTO embeddings VALUES(?,?,?,?)',(MODEL,text_hash(text),text,json.dumps(v.tolist())))
            self.controls.append({'text':text,'text_sha256':text_hash(text),
                'normalized_float32_vector_sha256':hashlib.sha256(v.astype('<f4').tobytes()).hexdigest()})
        con.commit();con.close()
        self.claims=[{'paper_id':str(i),'claims':[]} for i in range(52)];self.requests=[]
        for i in range(93):
            pid=i%52;text='claim '+str(i);index=len(self.claims[pid]['claims'])
            self.claims[pid]['claims'].append({'claim':text})
            self.requests.append({'text':text,'text_sha256':text_hash(text),'model_id':MODEL,
                'uses':[{'paper_id':str(pid),'claim_index':index,'currently_pool_ready':True}]})
        def write(name,obj,jsonl=False):
            p=self.root/name
            p.write_text(''.join(json.dumps(r)+'\n' for r in obj) if jsonl else json.dumps(obj));return p
        paths={'requests':write('requests.jsonl',self.requests,True),
               'claim_source':write('claims.jsonl',self.claims,True),
               'fixed_condition_pools':write('pools.jsonl',[{'paper_id':str(i)} for i in range(52)],True),
               'parity_controls':write('controls.json',self.controls),
               'model_inventory':write('inventory.json',{'base_revision':BASE_REV,'adapter_revision':ADAPTER_REV,'assets':{}})}
        self.plan={'existing_cache':str(self.original),'existing_cache_sha256':sha(self.original),
            'base_revision':BASE_REV,'adapter_revision':ADAPTER_REV,'unique_required_claim_texts':93,
            'representation':{'model_id':MODEL,'dimension':768,'max_length':512,'dtype':'float32'}}
        for k,p in paths.items():self.plan[k+'_path']=str(p);self.plan[k+'_sha256']=sha(p)
        self.planpath=write('plan.json',self.plan);self.folder=self.root/'sidecar_v1'
        prepare(self.planpath,self.folder)
        self.original_hash=sha(self.original)
        self.auth=self.root/'auth.json'
        self.auth.write_text(json.dumps({'manifest_sha256':sha(self.folder/'manifest.json'),
            'authorize_inference':True,'e6_inactive_verified':True,'resource_headroom_verified':True,
            'authorization_source':'synthetic unit test only'}))

    def tearDown(self):
        self.assertEqual(sha(self.original),self.original_hash)
        self.tmp.cleanup()

    @staticmethod
    def vector(text):
        v=np.zeros(DIM,dtype=np.float32);v[int(text_hash(text)[:8],16)%DIM]=1
        return v

    def factory(self,inventory):
        return lambda texts:np.stack([self.vector(text)*3 for text in texts])

    def run_small(self):return encode(self.folder,self.auth,limit=2,encoder_factory=self.factory)

    def test_exact_request_matching_and_indices(self):
        r=copy.deepcopy(self.requests);r[0]['uses'][0]['claim_index']=99
        with self.assertRaisesRegex(ValueError,'paper/index'):validate_requests(r,self.claims)
        r=copy.deepcopy(self.requests);r[0]['uses'][0]['paper_id']='unknown'
        with self.assertRaisesRegex(ValueError,'paper/index'):validate_requests(r,self.claims)

    def test_hash_model_and_duplicate_requests(self):
        for kind in ('hash','model','duplicate','count'):
            r=copy.deepcopy(self.requests)
            if kind=='hash':r[0]['text']='altered'
            elif kind=='model':r[0]['model_id']='another model'
            elif kind=='duplicate':r[1]=r[0]
            else:r.pop()
            with self.assertRaises(ValueError):validate_requests(r,self.claims)

    def test_default_status_never_calls_encoder_or_creates_cache(self):
        def forbidden(*a):raise AssertionError('model must not load')
        r=encode(self.folder,limit=0,encoder_factory=forbidden)
        self.assertEqual(r['missing_vectors'],93)
        self.assertFalse((self.folder/SIDECAR).exists())

    def test_authorization_and_e6_gate_precede_loading(self):
        for path in (None,self.folder/'authorization.template.json'):
            with self.assertRaises(ValueError):encode(self.folder,path,1,encoder_factory=lambda _:self.fail('loaded'))
        a=json.loads(self.auth.read_text());a['e6_inactive_verified']=False;self.auth.write_text(json.dumps(a))
        with self.assertRaisesRegex(ValueError,'E6 authorization'):encode(self.folder,self.auth,1,encoder_factory=lambda _:self.fail('loaded'))

    def test_bounded_batches_and_overlay_loading(self):
        calls=[]
        def factory(_):
            def f(texts):calls.append(texts);return np.stack([self.vector(s)*2 for s in texts])
            return f
        r=encode(self.folder,self.auth,limit=3,batch_size=2,encoder_factory=factory)
        self.assertEqual((r['complete_vectors'],r['new_vectors_generated']),(3,3))
        self.assertEqual([len(c) for c in calls],[1,1,1,2,1])
        with Overlay(self.folder) as overlay:
            np.testing.assert_array_equal(overlay.get('control 0'),self.vector('control 0'))
            np.testing.assert_array_equal(overlay.get('claim 0'),self.vector('claim 0'))
            self.assertEqual(overlay.encode(['claim 0','claim 0']).shape,(2,DIM))
            with self.assertRaisesRegex(KeyError,'inference disabled'):overlay.get('claim 20')
            with self.assertRaises(sqlite3.OperationalError):overlay.sidecar.connection.execute('DELETE FROM vectors')

    def test_calibration_boundary(self):
        self.run_small()
        with self.assertRaisesRegex(ValueError,'calibration review'):encode(self.folder,self.auth,limit=3,encoder_factory=lambda _:self.fail('loaded'))

    def test_parity_failure_leaves_no_vector_cache(self):
        def bad(_):return lambda texts:np.ones((len(texts),DIM),dtype=np.float32)
        with self.assertRaisesRegex(ValueError,'parity failed'):encode(self.folder,self.auth,limit=1,encoder_factory=bad)
        self.assertFalse((self.folder/SIDECAR).exists())

    def test_checksum_integrity_and_model_binding(self):
        self.run_small()
        con=sqlite3.connect(self.folder/SIDECAR)
        con.execute("UPDATE vectors SET vector=? WHERE text_hash=?",(b'bad',self.requests[0]['text_sha256']));con.commit();con.close()
        with self.assertRaisesRegex(ValueError,'corruption'):Overlay(self.folder)

    def test_source_manifest_changes_fail_closed(self):
        p=Path(self.plan['requests_path']);p.write_text(p.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'binding changed'):status(self.folder)

    def test_shape_finite_and_zero_norm(self):
        for bad in (np.zeros(DIM),np.ones(DIM-1),np.full(DIM,np.nan),np.full(DIM,np.inf)):
            with self.assertRaises(ValueError):normalized(bad)

    def test_reproducibility_and_complete_resume_no_model(self):
        # A complete synthetic cache resumes with no factory call, even limit>0.
        m,p,allowed=load(self.folder)
        c=Sidecar(self.folder/SIDECAR,binding(self.folder,m),allowed,m['model_key'],write=True,parity={'passed':True})
        c.put_batch([(h,self.vector(r['text'])) for h,r in allowed.items()]);c.close()
        r=encode(self.folder,self.auth,limit=93,encoder_factory=lambda _:self.fail('loaded'))
        self.assertEqual(r['complete_vectors'],93);self.assertFalse(r['model_loaded'])
        with Overlay(self.folder) as overlay:
            a=overlay.encode(['claim 1','claim 0']);b=overlay.encode(['claim 1','claim 0'])
            np.testing.assert_array_equal(a,b)

    def test_conflict_rejection_and_transactional_batch_validation(self):
        self.run_small();m,_,allowed=load(self.folder)
        c=Sidecar(self.folder/SIDECAR,binding(self.folder,m),allowed,m['model_key'],write=True)
        try:
            with self.assertRaisesRegex(ValueError,'conflicting'):
                c.put_batch([(self.requests[0]['text_sha256'],np.ones(DIM,dtype=np.float32)/np.sqrt(DIM))])
            with self.assertRaises(ValueError):c.put_batch([(self.requests[2]['text_sha256'],self.vector('claim 2')),('unknown',self.vector('x'))])
            self.assertIsNone(c.get_hash(self.requests[2]['text_sha256']))
        finally:c.close()

    def test_original_novelty_score_uses_overlay_without_global_mutation(self):
        self.run_small();root=Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'novelty.py').read_text())
        funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('score','_rnd_score','_cosine_distance_matrix')]
        def forbidden(*a,**k):raise AssertionError('legacy encoder invoked')
        scope={'np':np,'RND_P':100,'RND_Q':50,'Y_WEIGHT':.75,'N_WEIGHT':.25,
            '_parse_time':lambda s:s,'_eligible_papers':lambda *a:[{'text':'control 0'},{'text':'control 1'}], '_encode':forbidden}
        exec(compile(ast.Module(body=funcs,type_ignores=[]),'original_novelty_pure','exec'),scope)
        module=types.SimpleNamespace(score=scope['score'])
        with Overlay(self.folder) as overlay:
            r=overlay.score(module,'control 2',['claim 0','claim 1'],['p','q'],'2025-01-01')
            self.assertEqual(set(r),{'Y','density','N','yours'})
            self.assertEqual(r['yours'],.75*r['Y']+.25*r['N'])
            self.assertIs(scope['_encode'],forbidden)
            with self.assertRaises(KeyError):overlay.score(module,'control 2',['missing'],['p','q'],'2025-01-01')

    def test_wrong_model_row_rejected(self):
        self.run_small();con=sqlite3.connect(self.folder/SIDECAR)
        con.execute("UPDATE vectors SET model_key='wrong'");con.commit();con.close()
        with self.assertRaisesRegex(ValueError,'model binding'):Overlay(self.folder)

    def test_nonfinite_vector_rejected_even_with_valid_checksum(self):
        self.run_small();con=sqlite3.connect(self.folder/SIDECAR)
        blob=np.full(DIM,np.nan,dtype='<f4').tobytes()
        con.execute('UPDATE vectors SET vector=?,checksum=?',(blob,hashlib.sha256(blob).hexdigest()));con.commit();con.close()
        with self.assertRaisesRegex(ValueError,'invalid normalized'):Overlay(self.folder)

    def test_model_metadata_mismatch_rejected(self):
        self.run_small();con=sqlite3.connect(self.folder/SIDECAR)
        con.execute("UPDATE metadata SET value='other-model' WHERE key='binding'");con.commit();con.close()
        with self.assertRaisesRegex(ValueError,'provenance'):Overlay(self.folder)

    def test_resume_generates_only_remaining_unique_requests(self):
        first=self.run_small();self.assertEqual(first['complete_vectors'],2)
        seen=[]
        def factory(_):
            def f(texts):seen.extend(texts);return np.stack([self.vector(s)*3 for s in texts])
            return f
        second=encode(self.folder,self.auth,limit=2,encoder_factory=factory)
        self.assertEqual(second['complete_vectors'],4)
        self.assertNotIn('claim 0',seen);self.assertNotIn('claim 1',seen)
        self.assertEqual(seen[-2:],['claim 2','claim 3'])

    def test_reviewed_calibration_can_continue_bounded_encoding(self):
        report=self.run_small();reportpath=self.root/'calibration.json';reportpath.write_text(json.dumps(report))
        reviewpath=self.root/'review.json';reviewpath.write_text(json.dumps({
            'manifest_sha256':sha(self.folder/'manifest.json'),'accepted':True,'review_source':'synthetic test review',
            'calibration_report_path':str(reportpath),'calibration_report_sha256':sha(reportpath)}))
        a=json.loads(self.auth.read_text());a.update(calibration_review_path=str(reviewpath),calibration_review_sha256=sha(reviewpath))
        self.auth.write_text(json.dumps(a))
        r=encode(self.folder,self.auth,limit=4,encoder_factory=self.factory)
        self.assertEqual(r['complete_vectors'],6)

    def test_independent_synthetic_worker_runs_reproduce_identical_vectors(self):
        self.run_small()
        other=self.root/'sidecar_v2';prepare(self.planpath,other)
        a=json.loads(self.auth.read_text());a['manifest_sha256']=sha(other/'manifest.json')
        auth=self.root/'other_auth.json';auth.write_text(json.dumps(a))
        encode(other,auth,limit=2,encoder_factory=self.factory)
        contents=[]
        for folder in (self.folder,other):
            con=sqlite3.connect((folder/SIDECAR).resolve().as_uri()+'?mode=ro',uri=True)
            contents.append(con.execute('SELECT text_hash,checksum,vector FROM vectors ORDER BY text_hash').fetchall());con.close()
        self.assertEqual(contents[0],contents[1])
