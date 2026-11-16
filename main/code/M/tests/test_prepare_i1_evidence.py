import json,tempfile,unittest,csv
from pathlib import Path
from M.prepare_i1_evidence import prepare

class TestI1Evidence(unittest.TestCase):
 def test_missing_independent_evidence_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'E1/results_v2').mkdir(parents=True)
   (r/'E1/contrast.jsonl').write_text(json.dumps({'id':'h1','source_arxiv':'x','A':'q','B_min':'p','C':'n'})+'\n')
   (r/'E1/results_v2/source_metadata.csv').write_text('item_id,source_arxiv,official_url,first_posted_date\nh1,x,u,2025-07-01\n')
   (r/'E1/results_v2/source_alignment_audit.csv').write_text('item_id,abstract_review_status\nh1,PENDING_MANUAL_CONFIRMATION\n')
   o=prepare(r,'M/out');self.assertEqual(o['eligible_candidates'],0);self.assertEqual(o['candidates_examined'],1)
