import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from recover_claims import recover
from cached_extensions import Cache,calculate,summarize,MODEL
import novelty

class ContinuationTests(unittest.TestCase):
    def test_recover_no_invention_and_source_unchanged(self):
        selected=[{'paper_id':'p','pool':'x','claims':[{'claim':'Original','evidence':'original quote'}]}]
        raw={'p':{'abstract':'original quote. second quote. third quote.'}}
        source={'paper_id':'p','claims':[{'claim':'Saved additional claim','evidence':'second quote'},
                {'claim':'Fabricated evidence','evidence':'not in abstract'}]}
        before=json.dumps(selected)
        records,rejected=recover(selected,raw,[('saved.jsonl',7,source)])
        self.assertEqual(records[0]['recovered_additions'][0]['claim'],'Saved additional claim')
        self.assertEqual(records[0]['recovered_additions'][0]['line'],7)
        self.assertEqual(json.dumps(selected),before)
        self.assertEqual(rejected['nonexact_or_empty_evidence'],1)
    def test_recovery_same_evidence_not_extra_claim(self):
        s=[{'paper_id':'p','pool':'x','claims':[{'claim':'One','evidence':'quote'}]}]
        r,_=recover(s,{'p':{'abstract':'quote'}},[('f',1,{'paper_id':'p','claims':[{'claim':'Restated','evidence':'quote'}]})])
        self.assertEqual(r[0]['candidate_count'],1)
    def test_saved_raw_response_provenance(self):
        s=[{'paper_id':'p','pool':'x','claims':[]}]
        record={'paper_id':'p','raw_responses':['```json\n{"claims":[{"claim":"Saved","evidence":"exact quote"}]}\n```']}
        r,_=recover(s,{'p':{'abstract':'exact quote'}},[('f',1,record)])
        self.assertEqual(r[0]['recovered_additions'][0]['source_kind'],'raw_response')
    def test_cache_readonly_and_missing(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'cache.sqlite';c=sqlite3.connect(path)
            c.execute('CREATE TABLE embeddings(model_id,text_hash,text_value,vector_json)')
            v=np.zeros(768);v[0]=1
            c.execute('INSERT INTO embeddings VALUES(?,?,?,?)',(MODEL,hashlib.sha256(b'text').hexdigest(),'text',json.dumps(v.tolist())))
            c.commit();c.close();before=path.read_bytes()
            cache=Cache(path)
            self.assertEqual(cache.get('text')[0],1)
            with self.assertRaises(KeyError):cache.get('missing')
            with self.assertRaises(sqlite3.OperationalError):cache.connection.execute('DELETE FROM embeddings')
            cache.close();self.assertEqual(before,path.read_bytes())
    def test_formula_matches_existing_interface(self):
        rng=np.random.default_rng(41)
        x=rng.normal(size=(8,7)).astype(np.float32);x/=np.linalg.norm(x,axis=1)[:,None]
        idea=x[0];claims=x[1:3];pool=x[3:]
        texts={'idea':idea,'a':claims[0],'b':claims[1],**{str(i):v for i,v in enumerate(pool)}}
        with patch.object(novelty,'_eligible_papers',return_value=[{'text':str(i)} for i in range(5)]),patch.object(novelty,'_encode',side_effect=lambda ss:np.stack([texts[s] for s in ss])):
            actual=novelty.score('idea',['a','b'],['p'],'2020-01-01T00:00:00Z')
        self.assertEqual(actual,calculate(idea,claims,pool))
    def test_summary_direction_ties_and_pairing(self):
        scores={k:{m:v for m in ('Y','N','yours','density')} for k,v in [('near',0),('far',1),('older',1),('newer',1)]}
        r=summarize([{'scores':scores}],replicates=20)
        self.assertTrue(all(x['passes']==1 for x in r if x['left']=='near'))
        self.assertTrue(all(x['ties']==1 and x['passes']==0 for x in r if x['left']=='newer'))

class GeneratedArtifactTests(unittest.TestCase):
    def test_reviewed_claims_verbatim_and_source_supported(self):
        root=Path(__file__).resolve().parents[1]
        candidate_file=root/'analysis/claim_recovery_v1/candidates.jsonl'
        if not candidate_file.exists():self.skipTest('recovery artifact absent')
        records=list(map(json.loads,candidate_file.read_text().splitlines()))
        raw={r['paper_id']:r for r in map(json.loads,(root/'data/raw_papers.jsonl').read_text().splitlines())}
        for r in records:
            for c in r['all_additional_candidates']:
                self.assertIn(c['evidence'],raw[r['paper_id']]['abstract'])
                path=root/c['source'];record=json.loads(path.read_text().splitlines()[c['line']-1])
                from recover_claims import candidates
                self.assertTrue(any(x=={'claim':c['claim'],'evidence':c['evidence']} or
                    isinstance(x,dict) and x.get('claim')==c['claim'] and x.get('evidence')==c['evidence']
                    for x,_ in candidates(record)))
    def test_nearest_plan_replaces_originals_and_is_prior(self):
        root=Path(__file__).resolve().parents[1]
        path=root/'analysis/cached_extensions_v1/nearest_planting_plan.jsonl'
        if not path.exists():self.skipTest('nearest plan absent')
        from manipulation_extensions import parse
        for r in map(json.loads,path.read_text().splitlines()):
            self.assertFalse(set(r['replacement_map'])&set(r['pool_ids']))
            self.assertNotIn(r['paper_id'],r['pool_ids'])
            self.assertTrue(set(r['replacement_map'].values())<=set(r['pool_ids']))
            for p in r['synthetic_papers']:self.assertLess(parse(p['published']),parse(r['cutoff']))

class ParaphraseSupportTests(unittest.TestCase):
    def test_missing_vector_is_not_a_score(self):
        from cached_extensions import evaluate_paraphrase
        cache=type('Missing',(),{'get':lambda self,text:(_ for _ in ()).throw(KeyError('missing'))})()
        r=evaluate_paraphrase(None,None,None,'candidate',cache,'accepted')
        self.assertEqual(r['status'],'blocked_missing_candidate_embedding')
        self.assertNotIn('baseline',r)
    def test_paired_paraphrase_uses_cache_only(self):
        from cached_extensions import evaluate_paraphrase
        rng=np.random.default_rng(14);x=rng.normal(size=(9,5)).astype(np.float32)
        x/=np.linalg.norm(x,axis=1)[:,None]
        cache=type('Cached',(),{'get':lambda self,text:x[8]})()
        result=evaluate_paraphrase(x[0],x[1:3],x[3:8],'candidate',cache,'accepted')
        self.assertEqual(result['status'],'ok')
        self.assertLessEqual(result['difference']['Y'],1e-8)
        self.assertLessEqual(result['difference']['N'],1e-8)
    def test_review_missing_does_not_score(self):
        from cached_extensions import evaluate_paraphrase
        self.assertTrue(evaluate_paraphrase(None,None,None,'',None,'unreviewed')['status'].startswith('blocked'))

class FutureClaimArtifactTests(unittest.TestCase):
    def test_original_prefix_and_saved_additions_only(self):
        root=Path(__file__).resolve().parents[1]
        future=root/'analysis/claim_review_v1/claims_future.jsonl'
        if not future.exists():self.skipTest('future claim artifact absent')
        originals={r['paper_id']:r for r in map(json.loads,(root/'data/claims_v8_selected.jsonl').read_text().splitlines())}
        for r in map(json.loads,future.read_text().splitlines()):
            old=originals[r['paper_id']];n=len(old['claims'])
            self.assertEqual(r['claims'][:n],old['claims'])
            if 'continuation_review' not in r:self.assertEqual(r,old);continue
            review=r['continuation_review'];self.assertFalse(review['human_review'])
            self.assertEqual(r['claims'][n:],[{'claim':c['claim'],'evidence':c['evidence']} for c in review['additions']])
            self.assertEqual(review['original_audit'],{k:v for k,v in old.items() if k.startswith('audit_')})
