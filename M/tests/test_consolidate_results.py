import json,tempfile,unittest
from pathlib import Path
from M.consolidate_results import build
class TestConsolidate(unittest.TestCase):
 def test_synthetic_or_development_never_completed(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'M/results/stage5').mkdir(parents=True);(r/'M/data/ingestion_v2').mkdir(parents=True)
   tests=[{'test':t,'status':'SYNTHETIC_ONLY','executed':True,'metrics':{'fake':1}} for t in ('I1','I3','S1','A1','H1','H3','O1','O2','T1')]
   (r/'M/results/stage5/results.json').write_text(json.dumps({'tests':tests}))
   for x in tests:(r/f"M/data/ingestion_v2/{x['test']}_status.json").write_text('{"status":"BLOCKED","eligible_records":0}')
   z=build(r);self.assertEqual(z['completed_registered_count'],0);self.assertEqual(z['blocked_registered_count'],9)
