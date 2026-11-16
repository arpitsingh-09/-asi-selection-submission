import unittest,tempfile,json,csv
from pathlib import Path
from M.recover_i1_provenance import recover
class TestRecover(unittest.TestCase):
 def test_no_creation_or_inputs_inferred(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'E1/results_v2').mkdir(parents=True);(r/'M/data/i1_evidence_v1').mkdir(parents=True)
   (r/'E1/contrast.jsonl').write_text(json.dumps({'id':'h1','source_arxiv':'1234.1','A':'Question?'})+'\n')
   (r/'E1/results_v2/source_metadata.csv').write_text('item_id,source_arxiv,paper_title,official_url,first_posted_date,last_updated_date,metadata_status\nh1,1234.1,T,url,2025-01-01,2025-01-02,FOUND\n')
   (r/'M/data/i1_evidence_v1/candidate_ledger.jsonl').write_text(json.dumps({'candidate_id':'h1','question_id':'E1:h1:A','contrast_line':1})+'\n')
   x=recover(r,'M/out');self.assertEqual(x['verified_creation_dates'],0);self.assertEqual(x['temporally_eligible_records'],0)
