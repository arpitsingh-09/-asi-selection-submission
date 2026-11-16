import copy
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import warnings
import math
import numpy as np
from M import (ResearchSpace,PaperStore,Phi,LeakageError,MissingInputError,HashEncoder,
               CachedEncoder,MissingEmbeddingError,QualityModels,split_for,validate_split,controls,
               sample_same_topic_decoy)
from M.schema import fingerprint
from M.readouts import diversity_readout,novelty

Q='For image classification, does data augmentation help reduce error, measured by held-out error?'
OTHER='For image classification, does model ensembling help reduce error, measured by held-out error?'


def fixture():
    return [
      {'paper_id':'p1','published':'2022-01-01','title':'Augmentation','abstract':'Augmentation reduces image classification error.',
       'question':Q,'topic':'images','answers':[{'question':Q,'excerpt':'reduces image classification error','verified':True}]},
      {'paper_id':'p2','published':'2023-01-01','title':'Calibration','abstract':'Calibration improves class probability estimates.','question':OTHER,'topic':'images'},
      {'paper_id':'p3','published':'2023-06-01','title':'Speech','abstract':'Pronunciation models recognize speech.','topic':'speech'},
      {'paper_id':'future','published':'2026-01-01','title':'Future evidence','abstract':'An unavailable future result.'}]


class SpaceTests(unittest.TestCase):
    def setUp(self):self.space=ResearchSpace(fixture());self.t='2024-06-01'

    def test_shared_representation_all_six_heads_and_schema_round_trip(self):
        phi=self.space.encode(Q,['p1'],self.t);r=self.space.readouts(phi)
        self.assertTrue(set('INGQDT')<=set(r))
        self.assertEqual(r['snapshot_id'],phi.snapshot_id)
        self.assertEqual(r['shared_space_id'],phi.space_id)
        self.assertEqual(phi,Phi.from_dict(json.loads(json.dumps(phi.to_dict()))))
        self.assertEqual(len(phi.vector),7*512+7)
        self.assertIsNone(r['Q']['factors']['peer_review']['prediction'])
        self.assertIsNone(r['Q']['factors']['later_community_use']['prediction'])

    def test_future_literature_and_ids_do_not_enter_representation(self):
        a=self.space.encode(Q,['p1'],self.t)
        other=ResearchSpace(fixture()[:-1]);b=other.encode(Q,['p1'],self.t)
        self.assertEqual(a,b)
        self.assertNotIn('future',[p.paper.paper_id for p in a.literature])
        self.assertEqual(a.excluded_future_ids,())

    def test_explicit_future_equal_date_and_unavailable_inputs_rejected(self):
        for p in [{'paper_id':'x','published':self.t,'title':'same date'},
                  {'paper_id':'x','published':'2023-01-01','available_at':'2025-01-01','title':'later revision'}]:
            with self.assertRaises(LeakageError):self.space.encode(Q,[p],self.t)
        with self.assertRaises(LeakageError):self.space.encode(Q,['future'],self.t)

    def test_missing_unknown_and_duplicate_inputs(self):
        with self.assertRaises(MissingInputError):self.space.encode(Q,['unknown'],self.t)
        with self.assertRaises(ValueError):self.space.encode(Q,['p1','p1'],self.t)
        empty=self.space.encode(Q,[],self.t);retrieved=self.space.encode(Q,None,self.t)
        self.assertEqual(empty.inputs,());self.assertGreater(len(retrieved.inputs),0)
        self.assertEqual(empty.input_mode,'provided_empty')
        self.assertEqual(retrieved.input_mode,'retrieved_local_prior_cosine')

    def test_input_order_and_missing_controls(self):
        self.assertEqual(self.space.encode(Q,['p1','p2'],self.t),self.space.encode(Q,['p2','p1'],self.t))
        with self.assertRaises(ValueError):controls(self.space,Q,['p1'],self.t,shuffled_R=['p1'],decoy_q=OTHER)
        r=controls(self.space,Q,['p1'],self.t,shuffled_R=['p3'],decoy_q=OTHER)
        self.assertEqual(set(r['controls']),{'original','empty','shuffled','decoy'})
        self.assertIsNone(r['controls']['empty']['G']['score'])
        self.assertEqual(r['controls']['decoy']['G']['input_mode'],'provided')
        self.assertNotEqual(r['snapshot_ids']['original'],r['snapshot_ids']['shuffled'])

    def test_grounding_copy_and_explicit_answer_evidence(self):
        r=self.space.readouts(self.space.encode(Q,['p1'],self.t))['G']
        self.assertEqual(r['copied_question_input_ids'],['p1']);self.assertTrue(r['already_answered'])
        other=self.space.readouts(self.space.encode(OTHER,['p1'],self.t))['G']
        self.assertIsNone(other['already_answered'])

    def test_future_answer_annotation_is_removed_not_just_hidden_by_head(self):
        papers=fixture();papers[0]['answers'][0]['available_at']='2025-01-01'
        space=ResearchSpace(papers);phi=space.encode(Q,['p1'],self.t)
        self.assertEqual(phi.inputs[0].paper.answers,())
        self.assertIsNone(space.readouts(phi)['G']['already_answered'])
        future,new=space.update(phi,[],'2025-02-01')
        self.assertTrue(future.readouts(new)['G']['already_answered'])
        self.assertEqual(phi.inputs[0].paper.answers,())

    def test_unsupported_answer_quotes_rejected(self):
        p=fixture()[0];p['answers'][0]['excerpt']='Invented result'
        with self.assertRaises(ValueError):ResearchSpace([p])

    def test_novelty_cosine_is_finite_and_emits_no_blas_warnings(self):
        phi=self.space.encode(Q,['p1'],self.t)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            result=novelty(phi)
        self.assertEqual(caught,[])
        self.assertTrue(math.isfinite(result['Y']))
        q=phi.question_vector
        scores=[]
        for paper in phi.literature:
            a=paper.text_vector
            dot=sum(float(x)*float(y) for x,y in zip(a,q))
            na=math.sqrt(sum(float(x)*float(x) for x in a));nq=math.sqrt(sum(float(x)*float(x) for x in q))
            scores.append(max(-1.,min(1.,dot/(na*nq))))
        self.assertAlmostEqual(result['Y'],1-max(scores),places=12)

    def test_novelty_empty_reference_set_returns_unavailable_coordinates(self):
        empty=ResearchSpace([]).encode(Q,[],'2024-06-01')
        result=novelty(empty)
        self.assertIsNone(result['Y']);self.assertIsNone(result['density'])
        self.assertEqual(result['reference_ids'],[])
        self.assertEqual(result['status'],'no eligible prior literature')

    def test_claim_based_novelty_only_when_claims_supplied(self):
        a=self.space.readouts(self.space.encode(Q,['p1'],self.t))['N']
        self.assertIsNone(a['N']);self.assertIsNone(a['custom'])
        b=self.space.readouts(self.space.encode({'question':Q,'claims':['Augmentation reduces error.']},['p1'],self.t))['N']
        self.assertTrue(all(np.isfinite(b[k]) for k in ('Y','density','N','custom')))
        self.assertAlmostEqual(b['custom'],.75*b['Y']+.25*b['N'],places=6)

    def test_identity_and_signed_scope_are_symmetric_and_antisymmetric(self):
        a=self.space.encode(Q,[],self.t);b=self.space.encode(Q.replace('image classification','image classification under noise'),[],self.t)
        self.assertTrue(self.space.compare(a,a)['same_question'])
        ab=self.space.compare(a,b);ba=self.space.compare(b,a)
        self.assertAlmostEqual(ab['score'],ba['score']);self.assertAlmostEqual(ab['signed_scope'],-ba['signed_scope'])
        self.assertGreater(ab['signed_scope'],0)

    def test_temporal_update_preserves_old_snapshot_and_has_no_later_leakage(self):
        old=self.space.encode(Q,['p1'],self.t);serialized=old.to_dict()
        later=[{'paper_id':'exact','published':'2024-07-01','title':Q,'question':Q},
               {'paper_id':'too-late','published':'2030-01-01','title':Q}]
        future,new=self.space.update(old,later,'2025-01-01')
        self.assertEqual(old.to_dict(),serialized)
        self.assertEqual(new.previous_snapshot_id,old.snapshot_id)
        self.assertIn('exact',[p.paper.paper_id for p in new.literature])
        self.assertNotIn('too-late',[p.paper.paper_id for p in new.literature])
        self.assertLess(future.readouts(new)['N']['Y'],self.space.readouts(old)['N']['Y'])
        with self.assertRaises(LeakageError):self.space.update(old,[],'2023-01-01')
        with self.assertRaises(FrozenInstanceError):old.q='mutated'

    def test_late_arrival_not_backdated_and_versions_immutable(self):
        old=self.space.encode(Q,['p1'],self.t)
        future,_=self.space.update(old,[{'paper_id':'late','published':'2020-01-01','title':'Late discovery'}],'2025-01-01')
        self.assertNotIn('late',[p.paper_id for p in future.store.eligible(self.t)])
        with self.assertRaises(ValueError):self.space.update(old,[dict(fixture()[0],abstract='rewritten')],'2025-01-01')

    def test_diversity_uses_stored_shared_vectors_not_encoder(self):
        a=self.space.encode(Q,[],self.t);b=self.space.encode(OTHER,[],self.t)
        original=self.space.encoder.encode
        self.space.encoder.encode=lambda *a:(_ for _ in ()).throw(AssertionError('new embedding inside readout'))
        try:
            d=self.space.diversity([a,b]);self.assertEqual(d['n'],2);self.assertEqual(set(d['facet_dispersion']),{'purpose','mechanism','evaluation','domain'})
        finally:self.space.encoder.encode=original
        with self.assertRaises(ValueError):self.space.diversity([a,self.space.encode(Q,[],'2025-01-01')])

    def test_baseline_temporal_scope_and_published_abstract(self):
        phi=self.space.encode_paper('p2','2023-01-01',['p1']);b=self.space.readouts(phi)['baselines']
        self.assertFalse(b['B-Q']['available']);self.assertFalse(b['B-ABS']['available'])
        self.assertTrue(b['B-TF']['available']);self.assertEqual(b['B-TF']['training_ids'],['p1'])
        early=self.space.encode(Q,[],'2021-01-01');self.assertFalse(self.space.readouts(early)['baselines']['B-TF']['available'])
        with self.assertRaises(LeakageError):self.space.encode_paper('p2','2022-01-01')
        with self.assertRaises(MissingInputError):self.space.encode_paper('p3',self.t)
        with self.assertRaises(LeakageError):self.space.encode(Q,['p1'],'2022-01-01',source_kind='published',paper_id='p1')

    def test_snapshot_hash_and_future_reference_injection_rejected(self):
        phi=self.space.encode(Q,['p1'],self.t);r=phi.to_dict();r['q']='tampered'
        with self.assertRaises(ValueError):Phi.from_dict(r)
        r=phi.to_dict();r['inputs'][0]['paper']['published']='2028-01-01';r['inputs'][0]['paper']['available_at']='2028-01-01'
        r['inputs'][0]['paper']['answers']=[]
        r['snapshot_id']=fingerprint({k:v for k,v in r.items() if k!='snapshot_id'})
        with self.assertRaises(LeakageError):Phi.from_dict(r)

    def test_official_split_boundaries_and_no_test_training(self):
        cases={'2023-12-31':'train','2024-01-01':'validation','2024-12-31':'validation','2025-01-01':'gap','2025-06-30':'gap','2025-07-01':'test'}
        for when,expected in cases.items():self.assertEqual(split_for(when),expected)
        with self.assertRaises(LeakageError):validate_split([{'paper_id':'x','published':'2025-07-01'}],'train')
        with self.assertRaises(LeakageError):validate_split([{'paper_id':'x','published':'2023-01-01','available_at':'2024-01-01'}],'train')
        self.assertFalse(validate_split([{'paper_id':'x','published':'2025-07-01'}],'test')['heldout_evaluated'])

    def test_dated_same_topic_decoy_sampling(self):
        candidates=[{'question':OTHER,'topic':'images','posed_at':'2023-01-01'},
                    {'question':'Future?','topic':'images','posed_at':'2030-01-01'}]
        self.assertEqual(sample_same_topic_decoy(Q,'images',candidates,self.t)['question'],OTHER)
        with self.assertRaises(MissingInputError):sample_same_topic_decoy(Q,'other',candidates,self.t)

    def test_quality_fit_is_train_only_and_both_factors_are_unvalidated(self):
        records=[{'paper_id':'a','published':'2021-01-01','title':'a','abstract':'Earlier text','question':Q},
                 {'paper_id':'b','published':'2022-01-01','title':'b','abstract':'Later text','question':OTHER}]
        space=ResearchSpace(records);snapshots=[space.encode_paper(r['paper_id'],r['published'],[]) for r in records]
        labels=[{'peer_review':{'value':i+1,'observed_at':'2023-01-01'},'later_community_use':{'value':3-i,'observed_at':'2023-06-01'}} for i in range(2)]
        model=QualityModels.fit(records,snapshots,labels)
        p=model.predict(snapshots[0]);self.assertEqual(set(p),{'peer_review','later_community_use'})
        self.assertFalse(model.artifact['accuracy_established'])
        labels[0]['later_community_use']['observed_at']='2025-01-01'
        with self.assertRaises(LeakageError):QualityModels.fit(records,snapshots,labels)

    def test_json_embedding_cache_hash_model_and_missing_failures(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cache.json';row={'text':Q,'sha256':hashlib.sha256(Q.encode()).hexdigest(),'vector':[1.,0.,0.]}
            p.write_text(json.dumps({'model_id':'fixture','revision':'synthetic-v1','dimension':3,'records':[row]}))
            cache=CachedEncoder(p);self.assertEqual(cache.encode(Q),(1.,0.,0.))
            with self.assertRaises(MissingEmbeddingError):cache.encode('missing')
            row['sha256']='wrong';p.write_text(json.dumps({'model_id':'fixture','revision':'v1','dimension':3,'records':[row]}))
            with self.assertRaises(ValueError):CachedEncoder(p)

    def test_existing_cache_adapter_is_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'vectors.sqlite3';con=sqlite3.connect(p)
            con.execute('CREATE TABLE embeddings(model_id TEXT,text_hash TEXT,text_value TEXT,vector_json TEXT)')
            v=[1.]+[0.]*767
            con.execute('INSERT INTO embeddings VALUES(?,?,?,?)',('specter2_base+proximity-adapter+cls-v1',hashlib.sha256(Q.encode()).hexdigest(),Q,json.dumps(v)))
            con.commit();con.close();before=p.read_bytes()
            cache=CachedEncoder(p)
            self.assertEqual(len(cache.encode(Q)),768)
            with self.assertRaises(MissingEmbeddingError):cache.encode('missing')
            with self.assertRaises(sqlite3.OperationalError):cache.reader.connection.execute('DELETE FROM embeddings')
            cache.close();self.assertEqual(p.read_bytes(),before)

    def test_cli_smoke_synthetic_only(self):
        root=Path(__file__).resolve().parents[2]
        command=[sys.executable,'-B','-m','M','readouts','--papers','M/examples/papers.jsonl','--time',self.t,'--q',Q,'--inputs','p1']
        r=json.loads(subprocess.check_output(command,cwd=root))
        self.assertTrue(set('INGQDT')<=set(r));self.assertIsNone(r['Q']['factors']['peer_review']['prediction'])

    def test_missing_optional_abstract_baseline_does_not_abort_cached_phi(self):
        q='Can image models predict accurately?'
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'vectors.json';path.write_text(json.dumps({'model_id':'synthetic-fixture','revision':'v1','dimension':3,
                'records':[{'text':q,'sha256':hashlib.sha256(q.encode()).hexdigest(),'vector':[1.,0.,0.]}]}))
            encoder=CachedEncoder(path)
            space=ResearchSpace([{'paper_id':'f','published':'2023-01-01','abstract':'Not present in cache','question':q}],encoder)
            phi=space.encode_paper('f','2023-01-01',[]);r=space.readouts(phi)
            self.assertTrue(r['baselines']['B-Q']['available']);self.assertFalse(r['baselines']['B-ABS']['available'])
            self.assertIsNone(r['baselines']['B-ABS']['vector'])

    def test_conflicting_card_annotations_are_not_silently_merged_in_D(self):
        a=self.space.encode({'question':Q,'facets':{'domain':'images'}},[],self.t)
        b=self.space.encode({'question':Q,'facets':{'domain':'speech'}},[],self.t)
        with self.assertRaisesRegex(ValueError,'inconsistent'):self.space.diversity([a,b])

    def test_generated_question_cannot_hide_a_prior_paper_by_claiming_its_id(self):
        with self.assertRaises(ValueError):self.space.encode(Q,[],self.t,paper_id='p1')

    def test_snapshot_component_dimensions_are_validated(self):
        r=self.space.encode(Q,['p1'],self.t).to_dict();r['literature'][0]['text_vector']=(1.,)
        r['snapshot_id']=fingerprint({k:v for k,v in r.items() if k!='snapshot_id'})
        with self.assertRaisesRegex(ValueError,'component vector'):Phi.from_dict(r)
