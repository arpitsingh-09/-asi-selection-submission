"""Synthetic review/retrieval fixtures and read-only validation of real sources."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import test_prior_question_corpus as fixtures
from prior_question_corpus import ROOT,build_corpus
from prior_question_expansion import (source_frame,build_reviewed_corpus,validate_reviewed_corpus,
                                     retrieve_candidates,make_temporal_matcher)
from researcher_approval import digest,file_digest


class PriorQuestionExpansionTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.PriorQuestionCorpusTests();self.helper.setUp();self.addCleanup(self.helper.doCleanups)
        self.root=self.helper.root

    def corpus(self,*,abstract='What causes the fixture outcome?',accepted=True,revised=False):
        paper=self.helper.paper(abstract=abstract,revised=revised)
        m={'input_sets':[{'input_set_id':'fixture-target','target':{'published':'2021-01-01T00:00:00Z',
            'source_record':{'published':'2021-01-01T00:00:00Z'}},'references':[
            {'paper_id':'2001.00001','abstract':abstract},
            {'paper_id':'2001.00002','abstract':'A fixture paper without an explicit question.'}]}]}
        path=self.root/'E6/data/literature_selected_manifest_v1.json';path.parent.mkdir(parents=True);path.write_text(json.dumps(m))
        frame=source_frame(m,manifest_file_sha256=file_digest(path))
        base=build_corpus([paper],root=self.root)
        reviews=[{'question_id':q['question_id'],'question_sha256':digest(q['question']),
                  'accepted':accepted,'reason':'synthetic source context review',
                  'review_method':'assistant_source_comparison_not_human_review',
                  'source_evidence':[{'source_record_sha256':q['source_records'][0]['source_record_sha256'],
                                     'quote':abstract}]} for q in base['questions']]
        return build_reviewed_corpus(base,frame,reviews,m,root=self.root)

    def test_systematic_frame_includes_screen_negatives_and_replays(self):
        c=self.corpus();self.assertEqual(c['statistics']['frame_papers'],2)
        self.assertEqual(c['statistics']['screen_positive_papers'],1)
        self.assertEqual(c['statistics']['accepted_questions'],1)
        validate_reviewed_corpus(c,root=self.root)
        c['statistics']['accepted_questions']=2;c['manifest_sha256']=digest({k:v for k,v in c.items() if k!='manifest_sha256'})
        with self.assertRaises(ValueError):validate_reviewed_corpus(c,root=self.root)

    def test_rejected_questions_never_reach_candidate_retrieval(self):
        c=self.corpus(accepted=False)
        r=retrieve_candidates(c,'Fixture?',evaluation_cutoff='2022-01-01',root=self.root)
        self.assertEqual(r['eligible_question_count'],0)
        self.assertEqual(r['candidate_limit'],20)

    def test_unfounded_review_evidence_and_missing_reviews_rejected(self):
        c=self.corpus();path=self.root/'E6/data/literature_selected_manifest_v1.json';m=json.loads(path.read_text())
        reviews=copy.deepcopy(c['source_reviews']);reviews[0]['source_evidence'][0]['quote']='unsupported invented evidence'
        with self.assertRaises(ValueError):build_reviewed_corpus(c['source_corpus'],c['source_frame'],reviews,m,root=self.root)
        with self.assertRaises(ValueError):build_reviewed_corpus(c['source_corpus'],c['source_frame'],[],m,root=self.root)

    def test_version_date_excludes_later_revision_despite_older_first_submission(self):
        c=self.corpus(revised=True)
        self.assertEqual(c['statistics']['temporal_eligible_counts']['fixture-target'],0)
        r=retrieve_candidates(c,'Fixture?',evaluation_cutoff='2024-01-01T12:00:00Z',root=self.root)
        self.assertEqual(r['returned_count'],0)

    def test_exact_top20_and_semantic_identity_not_similarity(self):
        c=self.corpus(abstract=' '.join(f'What causes fixture outcome number {i}?' for i in range(25)))
        ranked=retrieve_candidates(c,'What causes fixture outcome?',evaluation_cutoff='2022-01-01',root=self.root)
        self.assertEqual(ranked['returned_count'],20);self.assertEqual(ranked['eligible_question_count'],25)
        self.assertEqual(ranked,retrieve_candidates(c,'What causes fixture outcome?',evaluation_cutoff='2022-01-01',root=self.root))
        with self.assertRaises(ValueError):retrieve_candidates(c,'Fixture?',evaluation_cutoff='2022-01-01',candidate_limit=21,root=self.root)
        calls=[]
        matcher=make_temporal_matcher(c,evaluation_cutoff='2022-01-01',identity_evaluator=lambda *a:calls.append(a) or False,identity_policy_id='fixture',root=self.root)
        self.assertFalse(matcher('What causes fixture outcome?',[r['question'] for r in c['questions']]))
        self.assertEqual(len(calls),20)

    def test_configured_reviewed_corpus_uses_bound_target_cutoff_and_boolean_matcher(self):
        from unittest.mock import patch
        from configured_evaluators import ConfiguredEvaluators
        c=self.corpus();path=self.root/'reviewed.json';path.write_text(json.dumps(c))
        calls=[]
        matcher=make_temporal_matcher(c,evaluation_cutoff='2021-01-01T00:00:00Z',
            identity_evaluator=lambda *a:calls.append(a) or False,identity_policy_id='fixture',root=self.root)
        identity={k:v for k,v in matcher.policy_identity.items() if k!='evaluation_cutoff'}
        evaluation={'already_asked':{'reference_question_corpus':{'path':'reviewed.json','file_sha256':file_digest(path)},
            'semantic_matcher':identity,'evaluation_cutoffs_by_input_set':c['evaluation_cutoffs_by_input_set'],
            'denominator_and_missing_reference_policy':'fixture'}}
        connected=ConfiguredEvaluators({},evaluation,{},object(),root=self.root)
        with patch.object(connected,'_require_execution'):
            result=connected.score_already_asked('fixture-target',[{'question_id':'fixture','question':'What causes the fixture outcome?'}],matcher)
            self.assertEqual(result['provenance']['evaluation_cutoff'],'2021-01-01T00:00:00Z')
            self.assertEqual(result['parsed_output']['rate'],0)
            with self.assertRaises(ValueError):
                connected.score_already_asked('fixture-target',[],matcher,evaluation_cutoff='2025-01-01')
        self.assertEqual(len(calls),1)
        invalid=make_temporal_matcher(c,evaluation_cutoff='2022-01-01',identity_evaluator=lambda *a:.99,
            identity_policy_id='fixture',root=self.root)
        with self.assertRaises(ValueError):invalid('Fixture?', [r['question'] for r in c['questions']])

    def test_real_reviewed_corpus_source_and_temporal_coverage(self):
        c=json.loads((ROOT/'E6/data/prior_question_corpus_v4.json').read_text())
        validate_reviewed_corpus(c)
        self.assertEqual(c['statistics']['frame_papers'],1659)
        self.assertEqual(c['statistics']['retrieved_papers'],29)
        self.assertEqual(c['statistics']['accepted_questions'],13)
        self.assertEqual(c['statistics']['rejected_ambiguous_questions'],15)
        self.assertEqual(c['statistics']['targets_with_eligible_questions'],100)
        self.assertEqual(c['candidate_limit'],20)
