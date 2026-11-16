"""Synthetic tests for the N/custom-only stage; no actual cohort evaluation."""
import ast
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import task2_claim_extension as e
from task2_cache_extension import summarize as previous_bootstrap


def unit(i):
    v=np.zeros(768,dtype=np.float32);v[i]=1.;return v


class ClaimExtensionTests(unittest.TestCase):
    def fixture(self):
        raw={'f':{'paper_id':'f','title':'F','abstract':'Focal','published':'2025-01-01T00:00:00Z'}}
        for pid in 'abcd':raw[pid]={'paper_id':pid,'title':pid,'abstract':pid,'published':'2024-01-01T00:00:00Z'}
        r={'paper_id':'f','pool':'ml','cutoff':raw['f']['published'],'cached_reference_ids':list('abcd'),
           'eligible_cached_prior_count':4,'pair_size':2}
        conditions={'near':list('ab'),'far':list('cd'),'older':list('ab'),'newer':list('cd')}
        pools=[{'paper_id':'f','pool':'ml','cutoff':r['cutoff'],'conditions':conditions}]
        saved=[{'paper_id':'f','pool':'ml','k':2,'scores':{c:{'Y':.8,'density':10.} for c in e.CONDITIONS}}]
        claims=[{'paper_id':'f','pool':'ml','claims':[{'claim':'claim '+str(i)} for i in range(4)]}]
        return [r],pools,saved,claims,raw,{'ml':set('abcd')}

    def validate(self,parts):return e.validate_fixed(*parts,expected_count=1)

    def test_exact_original_N_custom_formula_parity(self):
        root=Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'cached_extensions.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='calculate')
        fn.body=[n for n in fn.body if not isinstance(n,ast.ImportFrom)]
        scope={'np':np,'_rnd_score':lambda *a:0.}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'old_pure_formula','exec'),scope)
        c=np.stack([unit(0),unit(1)]);p=np.stack([unit(0),unit(2)])
        old=scope['calculate'](unit(3),c,p)
        self.assertEqual(e.claim_scores(c,p,old['Y']),{k:old[k] for k in ('N','yours')})
        self.assertEqual(old['N'],.5)

    def test_custom_reuses_given_Y_without_recalculating_it(self):
        c=np.stack([unit(0),unit(1)]);p=np.stack([unit(0),unit(2)])
        a=e.claim_scores(c,p,.8);b=e.claim_scores(c,p,.4)
        self.assertEqual(a['N'],b['N']);self.assertAlmostEqual(a['yours']-b['yours'],.3)

    def test_invalid_vectors_and_saved_Y_rejected(self):
        valid=np.stack([unit(0)])
        for c,p,y in [(valid,valid,float('nan')),(valid,valid,3.),(valid*2,valid,0.),
                      (np.empty((0,768)),valid,0.),(np.ones((1,767)),valid,0.),(np.full((1,768),np.nan),valid,0.)]:
            with self.assertRaises(ValueError):e.claim_scores(c,p,y)

    def test_frozen_inputs_are_valid_and_not_mutated(self):
        parts=self.fixture();before=copy.deepcopy(parts);specs=self.validate(parts)
        self.assertEqual(specs[0]['conditions'],parts[1][0]['conditions']);self.assertEqual(parts,before)

    def test_chronology_and_focal_exclusion(self):
        parts=self.fixture();parts[4]['a']['published']=parts[4]['f']['published']
        with self.assertRaisesRegex(ValueError,'eligibility'):self.validate(parts)
        parts=self.fixture();parts[0][0]['cached_reference_ids'][0]='f';parts[5]['ml'].add('f')
        with self.assertRaisesRegex(ValueError,'eligibility'):self.validate(parts)

    def test_cohort_duplicates_and_wrong_coverage(self):
        parts=self.fixture();parts[2].append(copy.deepcopy(parts[2][0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):self.validate(parts)
        parts=self.fixture();parts[1].clear()
        with self.assertRaisesRegex(ValueError,'coverage'):self.validate(parts)

    def test_pool_overlap_and_reselection_rejected(self):
        parts=self.fixture();parts[1][0]['conditions']['far']=list('ab')
        with self.assertRaisesRegex(ValueError,'overlap'):self.validate(parts)
        parts=self.fixture();parts[1][0]['conditions']['near'][0]='unknown'
        with self.assertRaisesRegex(ValueError,'membership'):self.validate(parts)

    def specs(self):
        spec=self.validate(self.fixture())[0]
        spec['condition_texts']={c:['ref0','ref1'] for c in e.CONDITIONS}
        return [spec]

    def test_missing_vector_fails_before_any_numerical_score(self):
        class Missing:
            def get(self,text):raise KeyError(text)
        with patch.object(e,'claim_scores',side_effect=AssertionError('score before complete inputs')):
            with self.assertRaises(KeyError):e.compute_records(self.specs(),Missing())

    def test_complete_synthetic_scoring_has_only_N_custom(self):
        class Synthetic:
            def get(self,text):return unit(0)
        result=e.compute_records(self.specs(),Synthetic())
        self.assertEqual(len(result),1)
        for scores in result[0]['scores'].values():
            self.assertEqual(scores,{'N':0.,'yours':.75*.8})
        self.assertEqual(set(result[0]['scores']['near']),{'N','yours'})

    def test_bootstrap_matches_prior_method_and_ties_fail(self):
        class Synthetic:
            def get(self,text):return unit(0)
        records=e.compute_records(self.specs(),Synthetic())
        old=[{'paper_id':r['paper_id'],'scores':{c:{'Y':v['N'],'density':v['yours']} for c,v in r['scores'].items()}} for r in records]
        expected=previous_bootstrap(old,100)
        for r in expected:r['measure']={'Y':'N','density':'yours'}[r['measure']]
        actual=e.summarize(records,100);self.assertEqual(actual,expected)
        self.assertTrue(all(r['ties']==1 and r['passes']==0 and r['pass_rate_ci95']==[0.,0.] for r in actual))
        self.assertEqual(actual,e.summarize(records,100))

    def test_preregistration_rejects_changed_code(self):
        with patch.object(e.subprocess,'check_output',return_value=b'changed'),patch.object(e,'sha',return_value='0'*64):
            with self.assertRaisesRegex(ValueError,'committed unchanged'):e.check_committed()

    def test_partial_sidecar_prevents_output_or_metric_computation(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'new-results'
            with patch.object(e,'check_committed',return_value='commit'),patch.object(e,'load_inputs',return_value=({},[])),\
                 patch.object(e,'authorize',return_value=({},Path(d)/'db')),patch.object(e,'sidecar_status',return_value={'complete_vectors':2}),\
                 patch.object(e,'compute_records',side_effect=AssertionError('should not calculate')):
                # load_inputs is synthetic, so supply only the required location here.
                with patch.object(e,'load_inputs',return_value=({'sidecar_folder':d},[])):
                    with self.assertRaisesRegex(ValueError,'all 93'):e.evaluate(out)
            self.assertFalse(out.exists())

    def test_no_authorization_and_existing_output_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'explicit evaluation'):e.authorize(e.MANIFEST,{},None)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileExistsError):e.evaluate(Path(d))

    def test_alternate_uncommitted_manifest_cannot_evaluate(self):
        with self.assertRaisesRegex(ValueError,'preregistered manifest'):
            e.evaluate('/nonexistent/unused',manifest_path='/different/manifest.json')

    def test_authorized_synthetic_52_writes_only_new_N_custom_results(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);manifest=root/'manifest.json';manifest.write_text('{}')
            protocol=root/'protocol.md';protocol.write_text('Synthetic test protocol only')
            db=root/'claim_vectors_v1.sqlite3';db.write_bytes(b'synthetic fixture, overlay is injected')
            auth=root/'auth.json';auth.write_text(json.dumps({'authorize_evaluation':True,
                'authorization_source':'synthetic unit test','manifest_sha256':e.sha(manifest),
                'protocol_sha256':e.sha(protocol),'sidecar_sha256':e.sha(db)}))
            m={'sidecar_folder':d,'source_sha256':{},'code_sha256':{}}
            specs=[]
            for i in range(52):
                s=copy.deepcopy(self.specs()[0]);s['paper_id']=str(i);specs.append(s)
            class Synthetic:
                def __init__(self,*a):pass
                def __enter__(self):return self
                def __exit__(self,*a):pass
                def get(self,text):return unit(0)
            out=root/'results'
            with patch.object(e,'MANIFEST',manifest),patch.object(e,'PROTOCOL',protocol),\
                 patch.object(e,'check_committed',return_value='synthetic'),patch.object(e,'load_inputs',return_value=(m,specs)),\
                 patch.object(e,'sidecar_status',return_value={'complete_vectors':93}),patch.object(e,'Overlay',Synthetic):
                result=e.evaluate(out,auth,manifest)
            self.assertEqual(result['new_focals'],52)
            self.assertFalse(result['Y_density_recomputed']);self.assertFalse(result['previous_results_recomputed'])
            rows=[json.loads(line) for line in (out/'results.jsonl').read_text().splitlines()]
            self.assertEqual(len({r['paper_id'] for r in rows}),52)
            self.assertTrue(all(set(v)=={'N','yours'} for r in rows for v in r['scores'].values()))

    def test_false_evaluation_flag_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            auth=Path(d)/'auth.json';auth.write_text(json.dumps({'authorize_evaluation':False,'authorization_source':'test'}))
            with self.assertRaisesRegex(ValueError,'not authorized'):e.authorize(e.MANIFEST,{},auth)
