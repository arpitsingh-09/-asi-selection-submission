import json,tempfile,unittest
from pathlib import Path
from M.import_review_visibility_evidence import import_evidence
class TestVisibilityImport(unittest.TestCase):
 def test_mismatched_or_missing_version_never_verified(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'M/data/ingestion_v2').mkdir(parents=True)
   review={'outcome_id':'n1','paper_id':'forum1','value':5}
   (p/'M/data/ingestion_v2/review_outcomes.jsonl').write_text(json.dumps(review)+'\n')
   api=p/'api.jsonl';api.write_text(json.dumps({'note_id':'n1','paper_id':'forum1','value':5})+'\n')
   result=import_evidence(p,api,p/'out');self.assertEqual(result['exact_review_versions_verified'],0)
   self.assertIn('missing_exact_revision_or_visibility_evidence',result['exclusions'])
