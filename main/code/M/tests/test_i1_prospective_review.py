import csv,json,tempfile,unittest
from pathlib import Path
from M.i1_prospective_review import import_reviews

class TestProspectiveReviewImporter(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
  self.q={'question_id':'q1','question':'Does method X help?','R':[{'paper_id':'p1','version':'v1'}]}
  self.src=self.d/'src.jsonl';self.src.write_text(json.dumps(self.q)+'\n')
  self.sheet=self.d/'review.csv';self.out=self.d/'out.jsonl'
  self.row={'question_id':'q1','question':self.q['question'],'original_inputs_json':json.dumps(self.q['R']),'question_same_as_intended':'YES','paraphrase_preserves_identity':'YES','near_miss_changes_identity':'YES','decoy_same_topic':'NO','reviewer_id':'reviewer-1','independent_of_author':'YES','evidence_source':'https://example.org/source','evidence_locator':'section 2, paragraph 1','rationale':'Compared the question and cited source details.','reviewed_at':'2026-11-13T00:00:00Z'}
 def tearDown(self):self.tmp.cleanup()
 def write(self,rows):
  with self.sheet.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(self.row));w.writeheader();w.writerows(rows)
 def test_valid_independent_review_imports_without_approving_decoy(self):
  self.write([self.row]);self.assertEqual(import_reviews(self.sheet,self.src,self.out),1)
  x=json.loads(self.out.read_text());self.assertEqual(x['decoy_human_status'],'REJECTED')
 def test_missing_judgment_rejected(self):
  r=dict(self.row,paraphrase_preserves_identity='');self.write([r])
  with self.assertRaises(ValueError):import_reviews(self.sheet,self.src,self.out)
 def test_unsupported_evidence_rejected(self):
  r=dict(self.row,evidence_source='trust me');self.write([r])
  with self.assertRaises(ValueError):import_reviews(self.sheet,self.src,self.out)
 def test_incorrect_question_or_inputs_rejected(self):
  r=dict(self.row,question='different question');self.write([r])
  with self.assertRaises(ValueError):import_reviews(self.sheet,self.src,self.out)
 def test_yes_decoy_is_explicit_human_decision_only(self):
  r=dict(self.row,decoy_same_topic='YES');self.write([r]);import_reviews(self.sheet,self.src,self.out)
  self.assertEqual(json.loads(self.out.read_text())['decoy_human_status'],'VERIFIED')
 def test_duplicate_conflicting_reviews_rejected(self):
  self.write([self.row,dict(self.row,decoy_same_topic='YES')])
  with self.assertRaises(ValueError):import_reviews(self.sheet,self.src,self.out)
 def test_missing_candidate_review_rejected(self):
  self.write([])
  with self.assertRaises(ValueError):import_reviews(self.sheet,self.src,self.out)
