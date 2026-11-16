"""Prepare source-verified dated question/control records; never evaluates them."""
import argparse,csv,hashlib,json,re
from pathlib import Path
from .schema import date
from .training import validate_record

def read_jsonl(p):
 with Path(p).open() as f:return [json.loads(x) for x in f if x.strip()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
 raw_path=root/'E2/data/raw_papers.jsonl';raw=read_jsonl(raw_path);byid={r['paper_id']:r for r in raw};sourcehash=sha(raw_path)
 splits={s:read_jsonl(root/f'M/data/manifests_v2/{s}.jsonl') for s in ('train','validation','test')}
 known={r['paper_id'] for s in ('train','validation','test') for r in splits[s] if r.get('source_dataset')=='E2/data/raw_papers.jsonl'}
 files={};counts={};all_rows=[]
 for split in ('train','validation','test'):
  candidates=[];rejected=[]
  for old in splits[split]:
   if old.get('source_dataset')!='E2/data/raw_papers.jsonl':continue
   paper=byid.get(old['paper_id'])
   if not paper:rejected.append({'question_id':old['question_id'],'reason':'source paper absent'});continue
   row=dict(old);row['provenance']={**old['provenance'],'paper_record_sha256':hashlib.sha256(json.dumps(paper,sort_keys=True).encode()).hexdigest(),'paper_record_id':paper['paper_id'],'paper_record_source_url':paper['paper_url'],'manifest_source_sha256':sha(root/f'M/data/manifests_v2/{split}.jsonl')}
   row['topics']=paper.get('categories',[]);row['input_paper_ids']=[];row['original_inputs_status']='MISSING_SOURCE_REFERENCE_LINKS';row['eligible_for_evaluation']=False
   # Empty is a valid explicit control. Other controls remain proposals unless source R exists.
   row['controls']={'empty':{'input_paper_ids':[],'status':'prepared'},'shuffled':{'input_paper_ids':None,'status':'blocked_no_original_input_ids'},'same_topic_decoy':None}
   try:validate_record(row)
   except (ValueError,KeyError,TypeError) as e:rejected.append({'question_id':row['question_id'],'reason':str(e)});continue
   peers=[]
   for other in raw:
    if other['paper_id']==paper['paper_id'] or not set(other.get('categories',[]))&set(row['topics']):continue
    try:
     if date(other['published'])>=date(row['published']) or date(other['updated'])>date(row['published']):continue
     matches=[m.group().strip() for m in re.finditer(r'[^.!?\n]*\?',other.get('abstract','')) if len(m.group().split())>=5]
     if matches:peers.append((other,matches[0]))
    except (ValueError,TypeError,KeyError):continue
   if peers:
    decoy,text=sorted(peers,key=lambda x:x[0]['paper_id'])[0]
    row['controls']['same_topic_decoy']={'question':text,'paper_id':decoy['paper_id'],'published':decoy['published'],'available_at':decoy['updated'],'source_url':decoy['paper_url'],'source_record_sha256':hashlib.sha256(json.dumps(decoy,sort_keys=True).encode()).hexdigest(),'topic_overlap':sorted(set(row['topics'])&set(decoy.get('categories',[]))),'status':'dated_category_match_proposal_not_human_topic_verified'}
   else:row['controls']['same_topic_decoy']={'status':'blocked_no_dated_question_candidate'}
   row['labels']={'peer_review':None,'later_community_use':None};row['missing_label_status']={'peer_review':'no linked dated outcome','later_community_use':'no linked dated outcome'}
   candidates.append(row)
  with (out/f'{split}.jsonl').open('x') as f:
   for r in candidates:f.write(json.dumps(r,sort_keys=True)+'\n')
  files[split]=sha(out/f'{split}.jsonl');counts[split]={'source_date_valid_records':len(candidates),'evaluation_eligible':0,'empty_controls':sum(x['controls']['empty']['status']=='prepared' for x in candidates),'shuffled_ready':sum(x['controls']['shuffled']['status']=='prepared' for x in candidates),'dated_decoy_proposals':sum(bool(x['controls']['same_topic_decoy'] and x['controls']['same_topic_decoy'].get('question')) for x in candidates),'rejected':rejected}
  all_rows+=candidates
 receipt={'schema':'M-local-data-preparation-v1','evaluations_run':0,'source_sha256':sourcehash,'source_record_count':len(raw),'manifests':{s:sha(root/f'M/data/manifests_v2/{s}.jsonl') for s in splits},'output_sha256':files,'counts':counts,'heldout_fresh_eligible':0,'genuine_dated_quality_labels':{'peer_review':0,'later_community_use':0},'blockers':['E2 source records are existing development pool; heldout reuse is prohibited.','Original input-paper references are absent from local raw-paper records.','Shuffled controls require known original inputs.','Topic-category decoys are proposals and lack human same-topic verification.','No dated quality labels link to these question identities.','No heldout record may be frozen without fresh independent provenance.'],'heldout_candidates_considered':len([x for x in splits['test'] if x.get('source_dataset')=='E2/data/raw_papers.jsonl']),'test_records_frozen':0}
 with (out/'readiness.json').open('x') as f:json.dump(receipt,f,indent=2)
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
