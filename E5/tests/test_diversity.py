import copy
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from diversity import (diversity,vendi,clique_partition,maximum_distinct_subset,
 CachedSemanticBackend,using_backend,digest,extract_facets)
from build_axioms import build,question
from known_groups import build_groups,twelve_months_after,validate_pair,dependency_components
from evaluate import bootstrap_cluster,pass_rule,compare_known_groups
from datetime import date


class DiversityTests(unittest.TestCase):
    def test_vendi_extremes_and_invalid_kernel(self):
        self.assertAlmostEqual(vendi(np.eye(5)),5)
        self.assertAlmostEqual(vendi(np.ones((5,5))),1)
        with self.assertRaises(ValueError):vendi(np.array([[1,2],[2,1.]]))

    def test_empty_and_singleton_schema(self):
        a=diversity([]);self.assertEqual(a['vendi'],0);self.assertEqual(a['quality_diversity_count'],0)
        b=diversity(['How can various things improve generally?'])
        self.assertEqual(b['vendi'],1);self.assertEqual(b['distinct_question_count'],1)
        self.assertFalse(b['semantic_cross_encoder'])

    def test_duplicate_invariance_of_distinct_count_not_frequency_entropy(self):
        a=diversity(['How can trees grow?','What makes stars collapse?'])
        b=diversity(['How can trees grow?','What makes stars collapse?','How can trees grow?'])
        self.assertEqual(a['distinct_question_count'],b['distinct_question_count'])
        self.assertNotEqual(a['class_entropy'],b['class_entropy'])

    def test_nontransitive_chain_not_one_equivalence_class(self):
        same=np.array([[1,1,0],[1,1,1],[0,1,1]],dtype=bool)
        classes=clique_partition(same);self.assertEqual(len(classes),2)
        self.assertTrue(all(same[i,j] for c in classes for i in c for j in c))

    def test_exact_joint_count_against_bruteforce_all_four_node_graphs(self):
        edges=list(itertools.combinations(range(4),2))
        for bits in range(2**len(edges)):
            graph=np.zeros((4,4),dtype=bool)
            for k,(i,j) in enumerate(edges):graph[i,j]=graph[j,i]=bool(bits&(1<<k))
            expected=max(len(s) for n in range(5) for s in itertools.combinations(range(4),n)
                         if all(graph[i,j] for i,j in itertools.combinations(s,2)))
            self.assertEqual(len(maximum_distinct_subset(graph,range(4))),expected)

    def test_order_invariance(self):
        q=['For graph classification, does ensembling help reduce error, measured by held-out error?',
           'For graph classification, does distillation help reduce error, measured by held-out error?']
        self.assertEqual(diversity(q),diversity(list(reversed(q))))

    def test_facets_false_has_no_dispersion(self):
        self.assertNotIn('facet_dispersion',diversity(['How can things work?'],facets=False))

    def test_invalid_requests_fail(self):
        for q in ([None],[''],['q']*13,'not a list'):
            with self.assertRaises(ValueError):diversity(q)

    def test_all_controlled_forms_parse(self):
        f={'domain':'images','mechanism':'augmentation','purpose':'reduce error','evaluation':'test error'}
        for i in range(6):self.assertEqual(extract_facets(question(f,i)),f)

    def test_dataset_counts_intended_single_edits_and_length_control(self):
        import re
        data=build();self.assertEqual(len(data),200)
        self.assertEqual(len({r['id'] for r in data}),200)
        for r in data:
            self.assertEqual(len(r['base']),5);self.assertEqual(len(r['clone']),5)
            old=r['intended_facets'][0];new=r['edit_intended_facets']
            self.assertEqual([f for f in old if old[f]!=new[f]],[r['edited_facet']])
            self.assertEqual([len(re.findall(r'\w+',q)) for q in r['base']],
                             [len(re.findall(r'\w+',q)) for q in r['vague_length_matched']])

    def test_semantic_cache_rejects_relevance_model_and_missing_data(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'cache.json';path.write_text(json.dumps({'metadata':{'kind':'passage_relevance'}}))
            with self.assertRaises(ValueError):CachedSemanticBackend(path)
            metadata={'kind':'same_question_cross_encoder','identity_calibration_verified':True,'calibration_source':'synthetic fixture',
                      **{k:'fixture' for k in ('embedding_model','embedding_revision','cross_encoder_model','cross_encoder_revision','facet_extractor','quality_judge')}}
            path.write_text(json.dumps({'metadata':metadata,'texts':{},'pairs':{}}))
            backend=CachedSemanticBackend(path)
            with using_backend(backend):
                with self.assertRaises(KeyError):diversity(['A real question?'])

    def test_semantic_backend_executes_from_exact_synthetic_cache(self):
        q='For images, does augmentation help reduce error, measured by test error?'
        f=extract_facets(q);texts={}
        for t in [q]+list(f.values()):
            texts[digest(t)]={'text':t,'embedding':[1.,0.], 'facets':f,
                'quality':{'question_form':True,'complete_facets':True,'concrete_language':True}}
        metadata={'kind':'same_question_cross_encoder','identity_calibration_verified':True,'calibration_source':'synthetic only',
                  **{k:'fixture' for k in ('embedding_model','embedding_revision','cross_encoder_model','cross_encoder_revision','facet_extractor','quality_judge')}}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cache.json';p.write_text(json.dumps({'metadata':metadata,'texts':texts,'pairs':{}}))
            with using_backend(CachedSemanticBackend(p)):r=diversity([q,q])
            self.assertEqual(r['distinct_question_count'],1);self.assertEqual(r['quality_diversity_count'],1)
            self.assertTrue(r['semantic_cross_encoder'])

    def test_bootstrap_clusters_and_repeatability(self):
        values=[0,0,1,1];clusters=['a','a','b','b']
        self.assertEqual(bootstrap_cluster(values,clusters,100),[0.,1.])
        self.assertEqual(bootstrap_cluster(values,clusters,100),bootstrap_cluster(values,clusters,100))
        self.assertIsNone(bootstrap_cluster([1,1],['a','a'],100))

    def test_metric_specific_pass_criteria(self):
        self.assertTrue(pass_rule('facet_edit','distinct_question_count',5,6))
        self.assertFalse(pass_rule('paraphrase','vendi',4,4.01))
        self.assertFalse(pass_rule('vague','facet_domain',1,None))


class KnownGroupTests(unittest.TestCase):
    def fixture(self):
        return [{'paperId':str(i),'title':'Synthetic metadata fixture','publicationDate':f'2024-0{i+1}-01',
                 'references':[{'paperId':s} for s in ('s1','s2','s3')],
                 'source':'Semantic Scholar','source_url':'https://example.invalid/fixture'} for i in range(5)]

    def test_three_common_seeds_and_twelve_months(self):
        r=build_groups(self.fixture(),['s1','s2','s3'])
        self.assertEqual(len(r['groups']),1);self.assertEqual(len(r['groups'][0]['paper_ids']),5)
        self.assertIsNone(r['groups'][0]['real_questions'])

    def test_no_fabrication_when_date_or_reference_missing(self):
        records=self.fixture();records[0]['publicationDate']=None
        self.assertEqual(len(build_groups(records,['s1','s2','s3'])['groups']),0)
        records=self.fixture();records[0]['references'].pop()
        self.assertEqual(len(build_groups(records,['s1','s2','s3'])['groups']),0)

    def test_exact_calendar_window_not_venue_year(self):
        self.assertEqual(twelve_months_after(date(2024,2,29)),date(2025,2,28))
        records=self.fixture();records[-1]['publicationDate']='2025-02-01'
        self.assertEqual(len(build_groups(records,['s1','s2','s3'])['groups']),0)

    def test_missing_real_questions_do_not_become_results(self):
        g=build_groups(self.fixture(),['s1','s2','s3'])['groups'][0]
        with self.assertRaises(ValueError):validate_pair(g)
        with self.assertRaises(ValueError):compare_known_groups([],None)

    def test_shared_seed_groups_are_not_independent_pairs(self):
        groups=[{'seed_ids':['a','b','c'],'paper_ids':['p1']},
                {'seed_ids':['c','d','e'],'paper_ids':['p2']},
                {'seed_ids':['f','g','h'],'paper_ids':['p3']}]
        ids=dependency_components(groups);self.assertEqual(ids[0],ids[1]);self.assertNotEqual(ids[1],ids[2])
