import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from finalize_short_claim_review import revise


class ShortSetRevisionTests(unittest.TestCase):
    def setUp(self):
        self.prior=[{'paper_id':'a','pool':'p','claims':[{'claim':'Old','evidence':'Old'}]},
                    {'paper_id':'untouched','pool':'p','claims':[{'claim':str(i),'evidence':str(i)} for i in range(4)]}]
        self.raw=[{'paper_id':'a','pool':'p','title':'Paper','published':'2024-01-01',
                   'abstract':'Alpha. Beta. Gamma. Delta.'}]
        self.decisions=[{'paper_id':'a','status':'supported_count_complete','semantic_review':'Four distinct assertions',
                         'human_review':False,'claims':[{'claim':s,'evidence':s+'.','kind':'result'} for s in ('Alpha','Beta','Gamma','Delta')]}]

    def call(self):
        return revise(self.prior,self.decisions,self.raw,{'a'},Path('source.jsonl'),'sha')

    def test_source_binding_offsets_and_preservation(self):
        original=copy.deepcopy(self.prior)
        updated,reviews=self.call()
        self.assertEqual(self.prior,original)
        self.assertEqual(updated[1],original[1])
        self.assertEqual(updated[0]['prior_claims_before_short_set_review'],original[0]['claims'])
        self.assertEqual(len(updated[0]['claims']),4)
        for c in reviews[0]['claims']:
            self.assertEqual(self.raw[0]['abstract'][c['evidence_start']:c['evidence_end']],c['evidence'])
            self.assertEqual(c['source_sha256'],'sha')

    def test_evidence_limited_never_promoted(self):
        self.decisions[0].update(status='evidence_limited',claims=None,limitation='Missing full text')
        updated,_=self.call()
        self.assertEqual(updated[0]['claims'],self.prior[0]['claims'])

    def test_exact_pending_coverage(self):
        self.decisions=[]
        with self.assertRaisesRegex(ValueError,'exactly'):self.call()

    def test_count_not_padded(self):
        self.decisions[0]['claims'].pop()
        with self.assertRaisesRegex(ValueError,'4-10'):self.call()

    def test_nonexact_evidence_rejected(self):
        self.decisions[0]['claims'][0]['evidence']='Invented'
        with self.assertRaisesRegex(ValueError,'unsupported'):self.call()

    def test_duplicate_assertions_rejected(self):
        self.decisions[0]['claims'][1]['claim']=' alpha '
        with self.assertRaisesRegex(ValueError,'duplicate claim'):self.call()

    def test_no_changes_to_already_complete_focals(self):
        self.prior[0]['claims']*=4
        with self.assertRaisesRegex(ValueError,'completed focal'):self.call()
