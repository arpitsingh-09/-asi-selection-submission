import csv,tempfile,unittest
from pathlib import Path
from M.i1_contrast_review import validate, FIELDS, DECOY_EVIDENCE

class TestI1DecoyVerification(unittest.TestCase):
 def _sheet(self,d,row):
  p=Path(d)/'review.csv'; fields=['question_id','decoy_status',*FIELDS,*DECOY_EVIDENCE]
  with p.open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(row)
  return p
 def _base(self):
  r={k:'value' for k in FIELDS};r.update(question_id='q1',decoy_status='VERIFIED',decoy_same_topic='YES',paraphrase_preserves_question='YES',near_miss_changes_question='YES')
  r.update({k:'source-backed evidence' for k in DECOY_EVIDENCE});return r
 def test_accepts_explicit_traceable_human_verification(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(validate(self._sheet(d,self._base()),['q1']),1)
 def test_rejects_blank_missing_or_unsupported_evidence(self):
  for key,value in [('decoy_evidence_source',''),('decoy_evidence_locator',''),('decoy_evidence_quote',''),('decoy_status','MAYBE'),('decoy_same_topic','')]:
   with self.subTest(key=key), tempfile.TemporaryDirectory() as d:
    row=self._base();row[key]=value
    with self.assertRaises(ValueError):validate(self._sheet(d,row),['q1'])
 def test_rejects_yes_without_verified_status(self):
  with tempfile.TemporaryDirectory() as d:
   row=self._base();row['decoy_status']='UNVERIFIED'
   with self.assertRaises(ValueError):validate(self._sheet(d,row),['q1'])
