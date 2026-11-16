"""Synthetic checks only; new 52-paper outcomes are not inspected by tests."""
import ast
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from task2_cache_extension import score,summarize,select_fixed,check_commit


class CacheExtensionTests(unittest.TestCase):
    def test_original_formula_parity_without_importing_model_modules(self):
        root=Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'novelty.py').read_text())
        funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('_cosine_distance_matrix','_rnd_score')]
        scope={'np':np,'RND_P':100,'RND_Q':50}
        exec(compile(ast.Module(body=funcs,type_ignores=[]),'original_pure_RND','exec'),scope)
        tree=ast.parse((root/'cached_extensions.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='calculate')
        fn.body=[n for n in fn.body if not isinstance(n,ast.ImportFrom)]
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'original_cached_calculate','exec'),scope)
        rng=np.random.default_rng(123)
        for n in (2,7,100):
            pool=rng.normal(size=(n,768)).astype(np.float32);pool/=np.linalg.norm(pool,axis=1,keepdims=True)
            idea=rng.normal(size=768).astype(np.float32);idea/=np.linalg.norm(idea)
            expected=scope['calculate'](idea,idea.reshape(1,-1),pool)
            self.assertEqual(score(idea,pool),{k:expected[k] for k in ('Y','density')})

    def test_strict_ties_fail_and_bootstrap_is_paper_level(self):
        rows=[]
        for pid in ('a','b'):
            rows.append({'paper_id':pid,'scores':{c:{'Y':1.,'density':20.} for c in ('near','far','newer','older')}})
        for r in summarize(rows,100):
            self.assertEqual((r['valid'],r['passes'],r['ties']),(2,0,2))
            self.assertEqual(r['pass_rate_ci95'],[0.,0.])

    def test_deterministic_bootstrap_and_duplicate_guard(self):
        r={'paper_id':'a','scores':{c:{'Y':i,'density':float(i)} for i,c in enumerate(('near','far','newer','older'))}}
        self.assertEqual(summarize([r],50),summarize([r],50))
        with self.assertRaisesRegex(ValueError,'duplicate'):summarize([r,r],50)

    def fixture(self):
        raw={'f':{'paper_id':'f','published':'2025-01-01T00:00:00Z','abstract':'f'}}
        for i in range(4):raw[str(i)]={'paper_id':str(i),'published':'2024-01-01T00:00:00Z','abstract':str(i)}
        row={'paper_id':'f','cutoff':raw['f']['published'],'cached_reference_ids':[str(i) for i in range(4)],'eligible_cached_prior_count':4,'pair_size':2}
        return raw,row

    def test_date_focal_duplicate_abstract_and_manifest_guards(self):
        for mutation in ('date','focal','abstract','manifest'):
            raw,r=self.fixture();allowed=set(raw)
            if mutation=='date':raw['0']['published']=raw['f']['published']
            if mutation=='focal':r['cached_reference_ids'][0]='f'
            if mutation=='abstract':raw['0']['abstract']=' F '
            if mutation=='manifest':allowed.remove('0')
            with self.assertRaisesRegex(ValueError,'eligibility'):select_fixed(r,raw,allowed)

    def test_duplicate_refs_rejected(self):
        raw,r=self.fixture();r['cached_reference_ids'][0]='1'
        with self.assertRaisesRegex(ValueError,'duplicate'):select_fixed(r,raw,set(raw))

    def test_uncommitted_protocol_rejected(self):
        with patch('task2_cache_extension.subprocess.check_output',return_value=b'changed'), patch('task2_cache_extension.sha',return_value='0'*64):
            with self.assertRaisesRegex(ValueError,'committed unchanged'):check_commit()
