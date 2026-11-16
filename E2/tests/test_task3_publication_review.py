import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from task3_publication_review import digest, identity, resolve, public_date
from task3_eligibility import validate_review


class PublicationReviewTests(unittest.TestCase):
    def setUp(self):
        self.b = {'forum_id':'test','title':'Exact Paper','abstract':'Original abstract.',
                  'abstract_sha256':digest('Original abstract.'),'published':'2025-10-08T00:00:00Z'}
        self.o = {'forum_id':'test','title':'Exact Paper','abstract':'Original abstract.',
                  'abstract_sha256':self.b['abstract_sha256'],'public_date':self.b['published'],
                  'source':'local archive','kind':'openreview'}
        self.bound = '2024-12-31T23:59:59.999999Z'

    def review(self, observations=None):
        return resolve(self.b, [self.o] if observations is None else observations, self.bound)

    def test_release_is_not_global_first_publication(self):
        r=self.review()
        self.assertEqual(r['earliest_verified_observed_release'],self.b['published'])
        self.assertIsNone(r['first_public_date'])
        self.assertFalse(r['first_publication_verified'])
        self.assertEqual(r['publication_history_status'],'unresolved_publication_history')

    def test_review_cannot_pass_evaluation_gate(self):
        with self.assertRaises(ValueError):
            validate_review([self.review()],[self.b],self.bound,self.bound)

    def test_earlier_exact_preprint(self):
        preprint=dict(self.o,forum_id=None,kind='arxiv',public_date='2024-01-01T00:00:00Z')
        r=self.review([self.o,preprint])
        self.assertTrue(r['earlier_preprint_detected'])
        self.assertEqual(r['eligibility_relative_to_conservative_bound'],'fails_post_bound_requirement')
        self.assertFalse(r['first_publication_verified'])

    def test_title_only_match_never_verifies_identity(self):
        candidate=dict(self.o,forum_id='other',abstract='Different text',public_date='2023-01-01T00:00:00Z')
        r=self.review([self.o,candidate])
        self.assertFalse(r['earlier_public_release_detected'])
        self.assertEqual(len(r['manual_identity_candidates']),1)
        self.assertEqual(r['earliest_verified_observed_release'],self.b['published'])

    def test_whitespace_normalized_identity(self):
        o=dict(self.o,forum_id='different',abstract='Original\nabstract.')
        self.assertIsNotNone(identity(self.b,o))

    def test_abstract_only_does_not_resolve_different_title(self):
        self.assertIsNone(identity(self.b,dict(self.o,forum_id='different',title='Another paper')))

    def test_same_forum_must_match_hash(self):
        self.assertIsNone(identity(self.b,dict(self.o,abstract_sha256='edited')))

    def test_no_creation_or_modification_date_substitution(self):
        self.assertIsNone(public_date({'cdate':1000,'mdate':2000,'odate':True}))

    def test_earliest_public_field(self):
        self.assertEqual(public_date({'odate':2000,'pdate':1000})[0],'pdate')

    def test_no_naive_release_dates(self):
        with self.assertRaises(ValueError):self.review([dict(self.o,public_date='2025-01-01')])

    def test_earlier_openreview_is_not_preprint(self):
        r=self.review([self.o,dict(self.o,forum_id='old',public_date='2024-01-01T00:00:00Z')])
        self.assertTrue(r['earlier_public_release_detected'])
        self.assertFalse(r['earlier_preprint_detected'])

    def test_inputs_immutable(self):
        b,o=copy.deepcopy(self.b),copy.deepcopy(self.o)
        self.review()
        self.assertEqual(self.b,b);self.assertEqual(self.o,o)
