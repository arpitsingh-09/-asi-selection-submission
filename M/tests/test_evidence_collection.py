import unittest
from M.prepare_evidence_collection import validate_review_row,validate_human_row

class TestEvidenceCollection(unittest.TestCase):
 def test_review_date_requires_archived_exact_version(self):
  r=dict(outcome_id='o',paper_id='p',factor='peer_review',version_id='v',public_at='2024-01-01T12:00:00Z',archived_evidence_url='https://example.org/archive',evidence_quote='score: 5',verifier_id='v1',verified_at='2026-11-13')
  self.assertTrue(validate_review_row(r));r['archived_evidence_url']=''
  with self.assertRaises(ValueError):validate_review_row(r)
 def test_human_review_requires_independence_and_evidence(self):
  keys=('candidate_id','question_id','source_paper_id','question_identity_yes_no','paraphrase_same_question_yes_no','near_miss_distinct_yes_no','decoy_same_topic_yes_no','reviewer_id','independent_of_author','evidence_source','evidence_locator','rationale','reviewed_at')
  r={k:'x' for k in keys};r.update(independent_of_author='YES',question_identity_yes_no='YES',paraphrase_same_question_yes_no='YES',near_miss_distinct_yes_no='NO',decoy_same_topic_yes_no='YES')
  self.assertTrue(validate_human_row(r));r['independent_of_author']='NO'
  with self.assertRaises(ValueError):validate_human_row(r)
