"""Bounded/resumable OpenAlex fallback; resolution requires exact DOI/arXiv evidence."""
import argparse,csv,hashlib,json,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
try:from .known_groups import build_groups
except ImportError:from known_groups import build_groups

S2_IDS=('659bf9ce7175e1ec266ff54359e2bd76e0b7ff31','b26f2037f769d5ffc5f7bdcec2de8da28ec14bee','ea8c46e193d5121e440daf96edfd15a47151c293')
BASE='https://api.openalex.org'
def get_json(url,opener=urllib.request.urlopen):
 try:
  with opener(url,timeout=20) as r:return json.loads(r.read())
 except urllib.error.HTTPError as e:raise RuntimeError(f'OpenAlex HTTP {e.code}: {e.read().decode("utf-8","replace")}') from None
def resolve_identifier(identifier,get=get_json):
 kind,value=identifier['kind'],identifier['value']
 if kind=='doi':url=BASE+'/works/'+urllib.parse.quote('https://doi.org/'+value,safe=':/')
 elif kind=='arxiv':url=BASE+'/works/'+urllib.parse.quote('https://arxiv.org/abs/'+value,safe=':/')
 else:raise ValueError('only DOI/arXiv identifiers can resolve seeds')
 work=get(url)
 if not str(work.get('id','')).startswith('https://openalex.org/W'):raise ValueError('OpenAlex work ID missing')
 if kind=='doi' and (work.get('doi') or '').lower()!='https://doi.org/'+value.lower():raise ValueError('resolved DOI mismatch')
 if kind=='arxiv' and value not in str(work.get('ids',{}).get('openalex','')) and not any(value in str(x) for x in work.get('locations',[])):raise ValueError('arXiv identity not verifiable in returned work')
 return work,url
def collect(seed_map,out,*,get=get_json,max_pages=2,per_page=100,sleep=time.sleep):
 seeds={r['semantic_scholar_id']:r for r in seed_map}
 if set(seeds)!=set(S2_IDS):raise ValueError('source-bound identifiers required for the three specified Semantic Scholar IDs')
 out=Path(out);out.mkdir(parents=True,exist_ok=True);raw=out/'raw_openalex.jsonl';state=out/'checkpoint.json';done=set(json.loads(state.read_text()).get('completed_s2_ids',[])) if state.exists() else set();resolved={}
 for sid in S2_IDS:
  row=seeds[sid]
  if not row.get('evidence_url') or row.get('mapping_verified_by_user') is not True or not row.get('mapping_record_sha256'):
   raise ValueError('source URL, explicit user verification, and mapping-record integrity hash required')
  work,url=resolve_identifier({'kind':row['kind'],'value':row['value']},get)
  resolved[sid]={'openalex_id':work['id'],'doi':work.get('doi'),'publication_date':work.get('publication_date'),'source_url':url,
                 'evidence_url':row['evidence_url'],'evidence_kind':row.get('evidence_kind'),
                 'mapping_record_sha256':row['mapping_record_sha256'],
                 'external_source_evidence_sha256':row.get('external_source_evidence_sha256')}
  if sid in done:continue
  cursor='*'
  for _ in range(max_pages):
   q=urllib.parse.urlencode({'filter':'cites:'+work['id'].rsplit('/',1)[-1],'select':'id,doi,publication_date,referenced_works','per-page':per_page,'cursor':cursor})
   req=BASE+'/works?'+q
   page=get(req)
   with raw.open('a') as f:f.write(json.dumps({'seed_s2_id':sid,'seed_openalex_id':work['id'],'request_url':req,'response':page},sort_keys=True)+'\n')
   cursor=page.get('meta',{}).get('next_cursor')
   if not cursor:break
   sleep(1)
  done.add(sid);state.write_text(json.dumps({'completed_s2_ids':sorted(done),'resolved_seeds':resolved},indent=2)+'\n')
 pages=[json.loads(x) for x in raw.read_text().splitlines() if x.strip()] if raw.exists() else []
 cited={sid:{} for sid in S2_IDS}
 for pg in pages:
  sid=pg['seed_s2_id'];seed_open=pg['seed_openalex_id']
  for w in pg['response'].get('results',[]):
   if seed_open in w.get('referenced_works',[]):cited[sid][w['id']]=w
 common=set.intersection(*(set(cited[s]) for s in S2_IDS)) if all(cited[s] for s in S2_IDS) else set()
 papers=[{'paperId':wid.rsplit('/',1)[-1],'publicationDate':next(cited[s][wid].get('publication_date') for s in S2_IDS),'source':'OpenAlex','source_url':wid,'references':[{'paperId':x.rsplit('/',1)[-1]} for x in next(cited[s][wid]['referenced_works'] for s in S2_IDS)]} for wid in sorted(common)]
 seed_open_ids=[x['openalex_id'].rsplit('/',1)[-1] for x in resolved.values()]
 result=build_groups(papers,seed_open_ids)
 bundle={'seed_resolution':resolved,'candidate_papers':papers,'groups':result['groups'],'excluded':result['excluded'],'raw_response_count':len(pages),'collection_complete':len(done)==3}
 (out/'candidate_groups.json').write_text(json.dumps(bundle,indent=2)+'\n');return bundle
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seed-map',required=True);p.add_argument('--out',required=True);p.add_argument('--max-pages',type=int,default=2);a=p.parse_args();print(json.dumps(collect(json.loads(Path(a.seed_map).read_text()),a.out,max_pages=a.max_pages),indent=2))
