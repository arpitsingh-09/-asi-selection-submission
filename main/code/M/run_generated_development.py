"""Descriptive shared-space checks for generated questions; not an evaluation."""
import argparse,hashlib,json
from pathlib import Path
from .engine import ResearchSpace
from .store import PaperStore
from .readouts import diversity_readout

def read_jsonl(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(__file__).resolve().parents[1];out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
 cohort=read_jsonl(root/'M/data/generated_questions_v1/generated_questions.jsonl');decoys=read_jsonl(root/'M/data/generated_questions_v1/decoy_questions_v2.jsonl');decoy={x['row']:x for x in decoys}
 raw_path=root/'E2/data/raw_papers.jsonl';raw=read_jsonl(raw_path);byid={}
 for r in raw:
  old=byid.get(r['paper_id'])
  if old is not None:
   fields=('paper_id','published','updated','available_at','title','abstract','question','rq','answers','paper_url')
   if any(old.get(k)!=r.get(k) for k in fields):raise ValueError('conflicting source text/date for one paper ID')
   continue
  byid[r['paper_id']]=r
 store=PaperStore(byid.values());space=ResearchSpace(store,max_literature=128,retrieval_k=3)
 outputs=[];snapshots={c:[] for c in ('original','empty','shuffled')};failures=[]
 for i,r in enumerate(cohort,1):
  controls={'original':r['controls']['original_input_ids'],'empty':r['controls']['empty_input_ids'],'shuffled':r['controls']['shuffled_input_ids']}
  row={'row':i,'question_id':r['question_id'],'question':r['question'],'generated_at':r['generated_at'],'question_kind':'generated',
       'source_paper_ids':r['controls']['original_input_ids'],'source_record_sha256':r['provenance']['source_file_sha256'],
       'status':'DEVELOPMENT_ONLY_NOT_EVALUATION','controls':{}}
  for cond,ids in controls.items():
   if ids is None:failures.append({'row':i,'condition':cond,'reason':'input IDs unavailable'});continue
   try:
    phi=space.encode(r['question'],ids,r['generated_at'])
    result=space.readouts(phi);snapshots[cond].append(phi)
    row['controls'][cond]={'input_paper_ids':ids,'readouts':result,'readout_status':{
      'I':'available signature/nearest-prior proxy; no identity labels',
      'N':'available local earlier-text novelty proxy; no supplied claims means N/custom unavailable',
      'G':'available lexical relevance; answeredness remains unknown without verified answer annotations',
      'Q':'unavailable: no fitted genuine-label factors',
      'D':'available stored-vector singleton/facet proxy; no semantic validity claim',
      'T':'available as-of/provenance snapshot; no update forecasting test'}}
   except Exception as e:failures.append({'row':i,'condition':cond,'reason':type(e).__name__+': '+str(e)})
  # Scope/identity interface compares the same fixed question across these control snapshots.
  if len([c for c in ('original','empty','shuffled') if c in row['controls']])>1:
   pairs={}
   names=list(row['controls'])
   for j,left in enumerate(names):
    for right in names[j+1:]:
     pa=next(s for s in snapshots[left] if s.q==r['question']);pb=next(s for s in snapshots[right] if s.q==r['question'])
     pairs[left+'_vs_'+right]=space.compare(pa,pb)
   row['I_control_comparisons_same_question']=pairs
  outputs.append(row)
 diversity={c:diversity_readout(v) for c,v in snapshots.items() if v}
 result={'schema':'M-generated-development-check-v1','purpose':'readout smoke/descriptive inspection only','development_only':True,
  'heldout_evaluation':False,'n_questions':len(cohort),'readouts_attempted':['I','N','G','Q','D','T'],'per_question_controls':outputs,
  'set_diversity_by_control':diversity,'failures':failures,'source_manifest_sha256':sha(root/'M/data/generated_questions_v1/generated_questions.jsonl'),
  'decoy_questions_used':0,'reason_decoys_not_used':'same-topic status is pending human review; this check only reuses verified original/empty/shuffled inputs',
  'semantic_quality_validation':False,'bootstrap_ci':None,'pass_criteria_applied':False,'quality_label_status':'no genuine labels; both Q factors unavailable'}
 with (out/'results.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
 with (out/'summary.md').open('x') as f:
  f.write('# Generated-question development readouts\n\nThis is a development-only descriptive run. It is not a core test, has no pass criteria, no human labels, and no confidence intervals.\n\n')
  f.write(f"Questions: {len(cohort)}. Controls: original, empty and shuffled. Failures: {len(failures)}.\n\n")
  for c,v in diversity.items():f.write(f"- {c} set: mean pairwise cosine distance={v.get('mean_pairwise_cosine_distance')}; Vendi={v.get('vendi')}; class entropy={v.get('class_entropy')}.\n")
  f.write('\nQ is unavailable for every record because no quality heads are fitted from genuine labels. N claim-based coordinates are unavailable because generated cards supply no source-backed atomic claims.\n')
 print(json.dumps({'questions':len(cohort),'successful_snapshots':sum(len(v) for v in snapshots.values()),'failures':failures,'result':str(out/'results.json')}))
if __name__=='__main__':main()
