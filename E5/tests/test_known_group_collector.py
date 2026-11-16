import tempfile,unittest,json
from pathlib import Path
from E5.collect_known_group_candidates import collect,_fetch
import urllib.error,urllib.request,io

class CollectorTests(unittest.TestCase):
 def test_collects_exact_ids_dates_refs_and_resume(self):
  with tempfile.TemporaryDirectory() as d:
   calls=[]
   def fake(seed,offset,limit):
    calls.append(seed);return {'total':1,'data':[{'citingPaper':{'paperId':'p'+seed,'publicationDate':'2024-01-01','url':'https://semanticscholar.org/p'+seed,'references':[{'paperId':seed} for _ in range(3)]}}]}
   collect(['s1','s2','s3'],Path(d),transport=fake,sleep=lambda _:None,limit=10)
   saved=json.loads((Path(d)/'candidate_groups.json').read_text())
   self.assertEqual(len(saved['candidate_papers']),3);self.assertEqual(len(calls),3)
   collect(['s1','s2','s3'],Path(d),transport=lambda *a: self.fail('must resume'),sleep=lambda _:None)
 def test_rejects_insufficient_seed_inventory(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):collect(['s1','s2'],d,transport=lambda *a:{})
 def test_citations_url_omits_invalid_nested_paper_fields(self):
  seen=[]
  class Response:
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def read(self):return b'{"data":[]}'
  old=urllib.request.urlopen
  try:
   urllib.request.urlopen=lambda req,timeout: (seen.append(req.full_url) or Response())
   _fetch('seed',0,10)
  finally:urllib.request.urlopen=old
  self.assertNotIn('fields=',seen[0]);self.assertIn('limit=10',seen[0])
 def test_http_error_includes_status_and_body(self):
  e=urllib.error.HTTPError('https://api.semanticscholar.org/x',400,'bad',{},io.BytesIO(b'{"error":"invalid fields"}'))
  old=urllib.request.urlopen
  try:
   urllib.request.urlopen=lambda *a,**k: (_ for _ in ()).throw(e)
   with self.assertRaisesRegex(RuntimeError,'HTTP 400.*invalid fields'):_fetch('seed',0,10)
  finally:urllib.request.urlopen=old
