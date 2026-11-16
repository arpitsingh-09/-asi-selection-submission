"""Targeted tests for the new source-bound claim merge only."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from complete_claim_additions import merge


class ClaimAdditionTests(unittest.TestCase):
    def setUp(self):
        self.prior=[{'paper_id':'a','pool':'vision','claims':[{'claim':'Old','evidence':'Old'}]}]
        self.raw=[{'paper_id':'a','pool':'vision','title':'Title','abstract':'Old. New result.', 'published':'2024-01-01'}]
        self.add=[{'paper_id':'a','claim':'New result','evidence':'New result.',
                   'distinctness_review':'Different result','human_review':False}]

    def call(self):
        return merge(self.prior,self.add,self.raw,Path('source.jsonl'),'source-sha')

    def test_addition_binds_to_source_without_mutation(self):
        old=copy.deepcopy(self.prior)
        result,review=self.call()
        self.assertEqual(self.prior,old)
        self.assertEqual(len(result[0]['claims']),2)
        self.assertEqual(review[0]['source_line'],1)
        self.assertEqual(review[0]['source_sha256'],'source-sha')
        self.assertFalse(review[0]['human_review'])

    def test_nonexact_evidence_rejected(self):
        self.add[0]['evidence']='Invented'
        with self.assertRaisesRegex(ValueError,'nonexact'):self.call()

    def test_restatement_with_same_text_rejected(self):
        self.add[0]['claim']='  OLD '
        with self.assertRaisesRegex(ValueError,'duplicate claim'):self.call()

    def test_conflicting_source_duplicate_rejected(self):
        self.raw.append(dict(self.raw[0],abstract='Conflicting abstract'))
        with self.assertRaisesRegex(ValueError,'conflicting source'):self.call()

    def test_consistent_cross_pool_duplicate_retains_correct_source_line(self):
        self.raw.insert(0,dict(self.raw[0],pool='language'))
        _,review=self.call()
        self.assertEqual(review[0]['source_line'],2)

    def test_does_not_pad_already_complete_sets(self):
        self.prior[0]['claims']*=4
        with self.assertRaisesRegex(ValueError,'minimal additions'):self.call()
