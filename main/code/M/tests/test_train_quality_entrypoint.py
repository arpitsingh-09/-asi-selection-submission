import json
import tempfile
import unittest
from pathlib import Path
from M.train_quality_entrypoint import train_if_eligible

class TestQualityGate(unittest.TestCase):
 def test_zero_labels_blocks_without_fitting(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   for n in ('train','val'):(p/n).write_text('')
   (p/'elig.json').write_text(json.dumps({'eligible_train':0,'eligible_validation':0}))
   x=train_if_eligible(p/'train',p/'val',p/'elig.json',p/'out')
   self.assertEqual(x['status'],'BLOCKED_INELIGIBLE_LABELS');self.assertTrue((p/'out/training_status.json').exists())
   self.assertEqual(x['verified_publication_time_labels'],{'train':{'peer_review':0,'later_community_use':0},'validation':{'peer_review':0,'later_community_use':0}})

 def test_stale_report_cannot_authorize_empty_manifests(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   for n in ('train','val'):(p/n).write_text('')
   (p/'elig.json').write_text(json.dumps({'eligible_train':2,'eligible_validation':1,'eligible_by_factor_split':{'train':{'peer_review':2,'later_community_use':2},'validation':{'peer_review':1,'later_community_use':1}}}))
   x=train_if_eligible(p/'train',p/'val',p/'elig.json',p/'out')
   self.assertEqual(x['status'],'BLOCKED_INELIGIBLE_LABELS')
   self.assertIn('eligibility report does not match',x['reason'])
   self.assertFalse((p/'out/validation_results.json').exists())

 def test_current_frozen_train_and_validation_have_no_eligible_labels(self):
  root=Path(__file__).resolve().parents[2]
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'quality-fit'
   result=train_if_eligible(root/'M/data/manifests_v2/train.jsonl',root/'M/data/manifests_v2/validation.jsonl',root/'M/data/quality_training_v1/eligibility_report.json',out)
   self.assertEqual(result['status'],'BLOCKED_INELIGIBLE_LABELS')
   self.assertEqual(result['verified_publication_time_labels']['train'],{'peer_review':0,'later_community_use':0})
   self.assertEqual(result['verified_publication_time_labels']['validation'],{'peer_review':0,'later_community_use':0})
   self.assertFalse((out/'peer_review.json').exists())
