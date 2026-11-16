import unittest
from E5.collect_openalex_known_groups import resolve_identifier,collect,S2_IDS
import hashlib,json,tempfile

class OpenAlexTests(unittest.TestCase):
 def test_exact_doi_resolution_and_mismatch_rejection(self):
  good={'id':'https://openalex.org/W1','doi':'https://doi.org/10.1/x','publication_date':'2020-01-01'}
  self.assertEqual(resolve_identifier({'kind':'doi','value':'10.1/x'},lambda u:good)[0]['id'],good['id'])
  with self.assertRaises(ValueError):resolve_identifier({'kind':'doi','value':'10.1/y'},lambda u:good)
 def test_requires_source_bound_identifiers_for_all_seeds(self):
  with self.assertRaises(ValueError):collect([], '/tmp/no-openalex-call',get=lambda u:self.fail('network must not run'))
 def test_user_attested_mapping_hash_is_not_external_evidence_hash(self):
  with tempfile.TemporaryDirectory() as d:
   seedmap=[]
   for i,sid in enumerate(S2_IDS):
    row={'semantic_scholar_id':sid,'kind':'arxiv','value':f'200{i}.00001','evidence_url':'https://www.semanticscholar.org/paper/'+sid,'evidence_kind':'user-attested page','mapping_verified_by_user':True}
    row['mapping_record_sha256']=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest();seedmap.append(row)
   def fake(url):
    if '/works/https' in url:
     import urllib.parse
     arxiv=urllib.parse.unquote(url).split('/abs/')[-1]
     return {'id':'https://openalex.org/W'+arxiv.replace('.',''),'ids':{},'locations':[{'landing_page_url':'https://arxiv.org/abs/'+arxiv}]}
    return {'results':[],'meta':{'next_cursor':None}}
   result=collect(seedmap,d,get=fake,sleep=lambda _:None)
   saved=json.loads((__import__('pathlib').Path(d)/'candidate_groups.json').read_text())
   self.assertEqual(len(saved['seed_resolution']),3)
   first=next(iter(saved['seed_resolution'].values()))
   self.assertTrue(first['mapping_record_sha256'])
   self.assertIsNone(first['external_source_evidence_sha256'])
   self.assertEqual(result['groups'],[])
