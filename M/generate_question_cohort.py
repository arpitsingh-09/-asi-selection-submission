"""Deterministic local-only generated question cohort preparation; never scores."""
import argparse,csv,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path

LIMIT=6
TEMPLATE='m_generated_question_v1'
TOPICS={'cs.CV':'computer vision'}
def norm(s):return re.findall(r'[a-z0-9]+',s.casefold())
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 with Path(p).open() as f:return [json.loads(l) for l in f if l.strip()]
def focal_ids(root):
 out=set()
 for p in [root/'E2/data/focal_papers.csv',root/'E2/data/raw_papers.jsonl']:
  if p.suffix=='.csv' and p.exists():
   with p.open() as f:out|={r.get('paper_id') or r.get('arxiv_id') for r in csv.DictReader(f)}
 return out-{'',None}
def question_strings(root):
 q=set()
 for p in [root/'E2/data/raw_papers.jsonl',root/'E1/contrast.jsonl']:
  if p.exists():
   for r in load(p):q|={str(v).strip().casefold() for v in r.values() if isinstance(v,str) and '?' in v}
 for p in (root/'M/data/manifests_v2').glob('*.jsonl'):
  for r in load(p):
   if r.get('question'):q.add(r['question'].strip().casefold())
 return q
def jaccard(a,b):
 x=set(norm(a));y=set(norm(b));return len(x&y)/len(x|y) if x|y else 0.
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(__file__).resolve().parents[1];out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
 raw_path=root/'E2/data/raw_papers.jsonl';raw=load(raw_path);linehash={};
 with raw_path.open('rb') as f:
  for i,line in enumerate(f,1):
   try:r=json.loads(line);linehash[r['paper_id']]={'line':i,'line_sha256':sha(line)}
   except Exception:continue
 # Preserve exact byte offsets in a bounded second pass.
 with raw_path.open('rb') as f:
  offset=0
  for i,line in enumerate(f,1):
   try:r=json.loads(line);linehash[r['paper_id']].update(line=i,offset=offset,line_sha256=sha(line))
   except Exception:pass
   offset+=len(line)
 stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z');focals=focal_ids(root);known=question_strings(root);raw_sha=sha(raw_path.read_bytes())
 papers=[r for r in raw if r.get('primary_pool_category')=='cs.CV']
 papers=[r for r in papers if r.get('paper_id') not in focals and r.get('paper_url','').startswith('https://arxiv.org/abs/') and re.search(r'v[1-9][0-9]*$',r['paper_id'])]
 eligible=[]
 for p in papers:
  try:
   from datetime import datetime as dt
   pub=dt.fromisoformat(p['published'].replace('Z','+00:00'));upd=dt.fromisoformat(p['updated'].replace('Z','+00:00'));now=dt.fromisoformat(stamp.replace('Z','+00:00'))
   if pub<now and upd<now:eligible.append(p)
  except Exception:continue
 eligible.sort(key=lambda p:p['paper_id']);pairs=[];used=set()
 candidates=[]
 for i,p in enumerate(eligible):
  for q in eligible[i+1:]:
   if p['paper_id']==q['paper_id'] or p.get('primary_pool_category')!=q.get('primary_pool_category'):continue
   ov=jaccard(p['title'],q['title'])
   if ov>=.10:candidates.append((-ov,p['paper_id'],q['paper_id'],p,q))
 for _,_,_,p,q in sorted(candidates) :
  if p['paper_id'] in used or q['paper_id'] in used:continue
  pairs.append((p,q));used|={p['paper_id'],q['paper_id']}
  if len(pairs)>=LIMIT:break
 def cat(p):return linehash[p['paper_id']]
 rows=[]
 for n,(p,q) in enumerate(pairs):
  topic=TOPICS.get(p.get('primary_pool_category'),p.get('primary_pool_category'))
  text=f"How do the approaches in {p['title']} and {q['title']} differ in their treatment of {topic}?"
  overlap=text.casefold() in known
  if overlap:continue
  inputs=[p['paper_id'],q['paper_id']]
  other_pair=pairs[(n+1)%len(pairs)] if len(pairs)>1 else None
  shuffled=list(other_pair) if other_pair and set(x['paper_id'] for x in other_pair).isdisjoint(inputs) else []
  decoy_pair=next((pair for j,pair in enumerate(pairs) if j not in (n,(n+1)%len(pairs)) and set(x['paper_id'] for x in pair).isdisjoint(inputs)),None)
  def bind(r):return {'paper_id':r['paper_id'],'title':r['title'],'url':r['paper_url'],'published':r['published'],'updated':r['updated'],'source':r['source'],'source_record':cat(r)}
  rows.append({'question_id':f'mgen-v1-{n+1:02d}','question':text,'question_kind':'generated','generated_at':stamp,'template':TEMPLATE,'topic':topic,'primary_category':p.get('primary_pool_category'),
      'R':[bind(p),bind(q)],'controls':{'original_input_ids':inputs,'empty_input_ids':[],
      'shuffled_input_ids':[r['paper_id'] for r in shuffled], 'shuffled_sources':[bind(r) for r in shuffled],
      'same_topic_decoy':None if decoy_pair is None else {'question':f"How do the approaches in {decoy_pair[0]['title']} and {decoy_pair[1]['title']} differ in their treatment of {topic}?",'source_ids':[decoy_pair[0]['paper_id'],decoy_pair[1]['paper_id']],'sources':[bind(x) for x in decoy_pair],'status':'same arXiv primary category; human semantic confirmation absent'}},
      'provenance':{'source_file':str(raw_path),'source_file_sha256':raw_sha,'template':'fixed in committed generator code','generator_code_sha256':sha(Path(__file__).read_bytes()),'generation_not_published':True},
      'overlaps_existing_question':overlap,'source_paper_ids_overlap_development_pool':True,'labels':{'peer_review':None,'later_community_use':None},'evaluation_eligible':False,'eligibility_status':'CANDIDATE_ONLY',
      'blockers':['Questions are newly generated, not human validated.','Shared category decoy lacks independent semantic verification.','No original input source was disclosed by a question author; R is explicitly the generation input set, not inferred author provenance.']})
 with (out/'generated_questions.jsonl').open('x') as f:
  for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
 sha_out=sha((out/'generated_questions.jsonl').read_bytes())
 manifest={'generated_at':stamp,'records':len(rows),'eligible_records':0,'data_sha256':sha_out,'evaluation_run':False,'cohort_lock_commit':None,'temporal_basis':'actual generation timestamp; source published and updated timestamps precede it','question_overlap_count':sum(r['overlaps_existing_question'] for r in rows),'sources':sorted({x['paper_id'] for r in rows for x in r['R']}),'controls':{'original':len(rows),'empty':len(rows),'shuffled_ready':sum(bool(r['controls']['shuffled_input_ids']) for r in rows),'same_category_decoy_proposals':sum(bool(r['controls']['same_topic_decoy']) for r in rows),'independently_verified_same_topic':0},'blockers':sorted({b for r in rows for b in r['blockers']})}
 with (out/'manifest.json').open('x') as f:json.dump(manifest,f,indent=2)
 print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
