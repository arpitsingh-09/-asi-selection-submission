import unittest,tempfile,json,csv
from pathlib import Path
from M.i1_human_review import import_reviews

class TestReviewImport(unittest.TestCase):
 def test_rejects_blank_and_accepts_explicit_review(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);base={'candidate_id':'h1','question_id':'E1:h1:A','source_paper_id':'arXiv:1','alignment_status':'PENDING'}
   (p/'ledger').write_text(json.dumps(base)+'\n');fields=['candidate_id','question_id','source_paper_id','reviewer_id','question_matches_source','paraphrase_same_question','near_miss_distinct_question','evidence_note','reviewed_at']
   row=dict(zip(fields,['h1','E1:h1:A','arXiv:1','human-1','YES','YES','YES','checked source','2026-11-13']))
   with (p/'sheet').open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(row)
   self.assertEqual(import_reviews(p/'sheet',p/'ledger',p/'out'),1)
   row['candidate_id']='bad'
   with (p/'sheet').open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(row)
   with self.assertRaises(ValueError):import_reviews(p/'sheet',p/'ledger',p/'out2')
