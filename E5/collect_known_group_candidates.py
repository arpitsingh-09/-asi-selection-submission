"""Resumable Semantic Scholar citation collector; never derives identity from titles."""
import argparse,json,os,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
try:from .known_groups import build_groups
except ImportError:from known_groups import build_groups

API='https://api.semanticscholar.org/graph/v1/paper/{}/citations'
PAPER_API='https://api.semanticscholar.org/graph/v1/paper/{}'
def collect(seed_ids,out,*,transport=None,sleep=time.sleep,limit=100,max_pages=1):
 if len(seed_ids)<3 or len(seed_ids)>20 or len(set(seed_ids))!=len(seed_ids):raise ValueError('provide 3–20 unique verified seed IDs')
 out=Path(out);out.mkdir(parents=True,exist_ok=True);raw=out/'raw_pages.jsonl';state=out/'checkpoint.json'
 done=set(json.loads(state.read_text()).get('completed_seed_ids',[])) if state.exists() else set()
 fetch=transport or _fetch; pages=[]
 for sid in seed_ids:
  if sid in done:continue
  offset=0;seedpages=[]
  for _page in range(max_pages):
   obj=fetch(sid,offset,limit)
   with raw.open('a') as f:f.write(json.dumps({'seed_id':sid,'offset':offset,'response':obj},sort_keys=True)+'\n')
   seedpages.append(obj);data=obj.get('data',[])
   if len(data)<limit or offset+len(data)>=obj.get('total',0):break
   offset+=len(data);sleep(1.0)
  pages.extend(seedpages);done.add(sid);state.write_text(json.dumps({'completed_seed_ids':sorted(done)},indent=2)+'\n')
 # Rehydrate previously saved responses as well, so resume yields identical output.
 allpages=[json.loads(x) for x in raw.read_text().splitlines() if x.strip()]
 papers={}
 for page in allpages:
  for item in page['response'].get('data',[]):
   p=item.get('citingPaper') or {};pid=p.get('paperId')
   if not pid:continue
   rec={'paperId':pid,'publicationDate':p.get('publicationDate'),'source':'Semantic Scholar','source_url':p.get('url'),'references':p.get('references') or []}
   if pid in papers and papers[pid]!=rec:raise ValueError('conflicting API records for exact paper ID '+pid)
   papers[pid]=rec
 result=build_groups(list(papers.values()),seed_ids)
 truncated=any(len(x['response'].get('data',[]))==limit and x['response'].get('total',0)>x['offset']+len(x['response'].get('data',[])) for x in allpages)
 (out/'candidate_groups.json').write_text(json.dumps({'seed_ids':seed_ids,'candidate_papers':list(papers.values()),'collection_truncated':truncated,**result},indent=2)+'\n')
 return result
def _fetch(seed,offset,limit):
 # Citations endpoint returns citingPaper.paperId/title by default; nested
 # citingPaper.* selectors are not valid citation fields and trigger HTTP 400.
 url=API.format(urllib.parse.quote(seed,safe=''))+'?'+urllib.parse.urlencode({'limit':limit,'offset':offset})
 return request_json(url)

class SemanticScholarHTTPError(RuntimeError):
 def __init__(self,status,body):
  self.status=status;self.body=body
  super().__init__(f'Semantic Scholar HTTP {status}: {body}')

def request_json(url):
 """Shared read-only Graph API transport, including bounded error detail."""
 headers={'User-Agent':'ASI-Lab-E5/1.0'}
 key=os.environ.get('SEMANTIC_SCHOLAR_API_KEY')
 if key:headers['x-api-key']=key
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=20) as r:return json.loads(r.read())
 except urllib.error.HTTPError as e:
  body=e.read().decode('utf-8','replace');key=os.environ.get('SEMANTIC_SCHOLAR_API_KEY')
  if key:body=body.replace(key,'[REDACTED]')
  raise SemanticScholarHTTPError(e.code,body) from None
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seed-ids',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--limit',type=int,default=100);p.add_argument('--max-pages-per-seed',type=int,default=1);a=p.parse_args();print(json.dumps(collect(a.seed_ids,a.out,limit=a.limit,max_pages=a.max_pages_per_seed),indent=2))
