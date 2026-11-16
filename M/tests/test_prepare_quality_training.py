import json,tempfile,unittest
from pathlib import Path
from M.prepare_quality_training import prepare

class TestPreparation(unittest.TestCase):
 def test_unverified_dates_excluded_and_gate_blocked(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'M/data/ingestion_v2').mkdir(parents=True);(root/'M/data/manifests_v1').mkdir(parents=True)
   row={'question_id':'q','paper_id':'p','published':'2023-01-01','available_at':'2023-01-01','split':'train'}
   for s in ('train','validation'):(root/f'M/data/manifests_v1/{s}.jsonl').write_text((json.dumps(row)+'\n') if s=='train' else '')
   review={'outcome_id':'o','paper_id':'p','factor':'peer_review','value':5,'definition':'d','observed_at':None,'usable_for_fitting':False,'value_evidence':{'binding':{'record_sha256':'a'*64}}}
   (root/'M/data/ingestion_v2/review_outcomes.jsonl').write_text(json.dumps(review)+'\n')
   result=prepare(root,'M/data/quality_training_v1')
   self.assertEqual(result['eligible_train'],0);self.assertEqual(result['eligible_validation'],0)
   self.assertEqual(result['training_status'],'BLOCKED_INELIGIBLE_LABELS')
   self.assertIn('missing_verified_review_observation_date',result['exclusions'])
