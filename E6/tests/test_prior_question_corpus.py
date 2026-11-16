"""Synthetic source fixtures only; no network, models or experimental questions."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prior_question_corpus import (PROMPT, ROOT, paper_from_web_snapshot, build_corpus,
    validate_corpus, retrieve_candidates, make_temporal_matcher, predates, precise_date)
from researcher_approval import digest
from evaluation import evaluate_already_asked_rate


class PriorQuestionCorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        prompt = self.root / PROMPT.relative_to(ROOT)
        prompt.parent.mkdir(parents=True); prompt.write_bytes(PROMPT.read_bytes())

    def paper(self, paper_id='2001.00001', abstract='What causes the fixture outcome?', revised=False):
        version = 2 if revised else 1
        source = self.root / (paper_id + '.txt')
        source.write_text(f'[{paper_id}] Fixture paper (https://arxiv.org/abs/{paper_id})\n'
            f'L0: # Title:Fixture research\nL1: > Abstract:{abstract}\nL2: Subjects: fixture\n'
            f'L3: (or arXiv:{paper_id}v{version})\nL4: [v1] Wed, 1 Jan 2020 12:00:00 UTC\n'
            + ('L5: [v2] Mon, 1 Jan 2024 12:00:00 UTC\n' if revised else ''))
        return paper_from_web_snapshot(source,source_url=f'https://arxiv.org/abs/{paper_id}',
            retrieved_at_utc='2026-11-12T00:00:00Z',root=self.root)

    def test_deterministic_deduplication_and_all_source_fields(self):
        p = self.paper(); q = self.paper('2001.00002')
        a = build_corpus([p,q,p],root=self.root)
        self.assertEqual(a,build_corpus([q,p,p],root=self.root))
        self.assertEqual(a['statistics']['papers_retrieved'],3)
        self.assertEqual(a['statistics']['papers_accepted'],2)
        self.assertEqual(a['statistics']['papers_rejected'],1)
        self.assertEqual(a['question_count'],1)
        self.assertEqual(len(a['questions'][0]['source_records']),2)
        for key in ('paper_id','title','submission_date','source_url','abstract','retrieved_at_utc','provenance','validation_status'):
            self.assertIn(key,p)
        validate_corpus(a,root=self.root)

    def test_version_date_temporal_leakage_and_strict_boundary(self):
        c = build_corpus([self.paper(revised=True)],root=self.root)
        for cutoff in ('2021-01-01','2024-01-01T12:00:00Z'):
            self.assertEqual(retrieve_candidates(c,'fixture',evaluation_cutoff=cutoff,candidate_limit=3,root=self.root)['returned_count'],0)
        self.assertEqual(retrieve_candidates(c,'fixture',evaluation_cutoff='2024-01-02',candidate_limit=3,root=self.root)['returned_count'],1)
        self.assertFalse(predates('2024-01-01','2024-01-01T20:00:00Z'))
        self.assertTrue(predates('2024-01-01','2024-01-02'))

    def test_missing_and_uncertain_dates_rejected(self):
        for value in (None,'2024','2024-01','2024-01-01T00:00:00'):
            with self.assertRaises(ValueError): precise_date(value)
            p = self.paper(); p['effective_date'] = value
            c = build_corpus([p],root=self.root)
            self.assertEqual(c['statistics']['papers_rejected'],1)
            self.assertEqual(c['question_count'],0)

    def test_extraction_failure_never_rewrites_an_objective(self):
        c = build_corpus([self.paper(abstract='We study the fixture outcome and report an effect.')],root=self.root)
        self.assertEqual(c['question_count'],0)
        self.assertEqual(c['statistics']['extraction_failures'],1)
        self.assertEqual(c['sources'][0]['extraction']['questions'],[])

    def test_provenance_and_source_tampering_detected_even_after_rehash(self):
        c = build_corpus([self.paper()],root=self.root)
        c['questions'][0]['source_records'][0]['effective_date']='2010-01-01'
        c['manifest_sha256']=digest({k:v for k,v in c.items() if k!='manifest_sha256'})
        with self.assertRaises(ValueError):validate_corpus(c,root=self.root)
        c = build_corpus([self.paper()],root=self.root)
        (self.root/'2001.00001.txt').write_text('tampered')
        with self.assertRaises(ValueError):validate_corpus(c,root=self.root)

    def test_empty_or_temporally_ineligible_corpus_is_unavailable(self):
        c=build_corpus([],root=self.root); calls=[]
        matcher=make_temporal_matcher(c,evaluation_cutoff='2024-01-01',candidate_limit=10,
            identity_evaluator=lambda *args:calls.append(args) or False,identity_policy_id='fixture',root=self.root)
        with self.assertRaises(ValueError):matcher('Fixture?',[])
        self.assertEqual(calls,[])
        result=evaluate_already_asked_rate('fixture',[{'question_id':'q1','question':'Fixture?'}],[],matcher,
            denominator_policy_id='fixture',provenance={})
        self.assertEqual(result['status'],'blocked');self.assertIsNone(result['parsed_output'])

    def test_similarity_is_retrieval_only_boolean_identity_is_configurable(self):
        c=build_corpus([self.paper()],root=self.root); questions=[q['question'] for q in c['questions']];calls=[]
        matcher=make_temporal_matcher(c,evaluation_cutoff='2024-01-01',candidate_limit=2,
            identity_evaluator=lambda *args:calls.append(args) or False,identity_policy_id='fixture',root=self.root)
        self.assertFalse(matcher(questions[0],questions)) # Exact words still do not bypass judge.
        self.assertEqual(len(calls),1)
        self.assertEqual(matcher.attempts[0]['candidates'][0]['lexical_jaccard'],1)
        with self.assertRaises(ValueError):matcher('Fixture?', ['changed corpus'])
        invalid=make_temporal_matcher(c,evaluation_cutoff='2024-01-01',candidate_limit=2,
            identity_evaluator=lambda *args:.99,identity_policy_id='fixture',root=self.root)
        with self.assertRaises(ValueError):invalid('Fixture?',questions)

    def test_configured_already_asked_interface_enforces_cutoff_and_reuses_temporal_matcher(self):
        from unittest.mock import patch
        from configured_evaluators import ConfiguredEvaluators
        from researcher_approval import file_digest
        corpus=build_corpus([self.paper()],root=self.root)
        path=self.root/'corpus.json';path.write_text(json.dumps(corpus))
        calls=[]
        matcher=make_temporal_matcher(corpus,evaluation_cutoff='2024-01-01',candidate_limit=2,
            identity_evaluator=lambda *args:calls.append(args) or False,identity_policy_id='fixture-binary',root=self.root)
        identity={k:v for k,v in matcher.policy_identity.items() if k!='evaluation_cutoff'}
        evaluation={'already_asked':{'reference_question_corpus':{'path':'corpus.json','file_sha256':file_digest(path)},
            'semantic_matcher':identity, 'evaluation_cutoffs_by_input_set':{'fixture-input':'2024-01-01'},
            'denominator_and_missing_reference_policy':'fixture-complete'}}
        connected=ConfiguredEvaluators({},evaluation,{},object(),root=self.root)
        # Gate behavior is separately tested against the real closed configuration.
        # Only offline policy wiring is exercised in this synthetic fixture.
        with patch.object(connected,'_require_execution'):
            with self.assertRaises(ValueError):
                connected.score_already_asked('fixture-input',[],matcher,evaluation_cutoff='2025-01-01')
            self.assertEqual(calls,[])
            result=connected.score_already_asked('fixture-input',[{'question_id':'fixture-q','question':'What causes a fixture outcome?'}],
                matcher,evaluation_cutoff='2024-01-01')
        self.assertEqual(result['parsed_output']['rate'],0)
        self.assertEqual(result['parsed_output']['denominator'],1)
        self.assertEqual(len(result['candidate_retrieval_and_judgments']),1)
        self.assertEqual(len(calls),1)

    def test_published_corpus_replays_from_real_source_snapshots(self):
        corpus=json.loads((ROOT/'E6/data/prior_question_corpus_v3.json').read_text())
        validate_corpus(corpus)
        self.assertEqual(corpus['statistics']['papers_retrieved'],9)
        self.assertEqual(corpus['question_count'],6)
        self.assertEqual(corpus['status'],'provisional_pending_decision20_approval')
