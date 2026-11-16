"""Build provenance ledger for existing E1 I1 candidates; never infer eligibility."""
import argparse,csv,hashlib,json
from pathlib import Path
from .training import rows

def prepare(root='.',out='M/data/i1_evidence_v1'):
 root=Path(root);out=root/out if not Path(out).is_absolute() else Path(out);out.mkdir(parents=True,exist_ok=False)
 contrast=root/'E1/contrast.jsonl'; metadata=root/'E1/results_v2/source_metadata.csv'; audit=root/'E1/results_v2/source_alignment_audit.csv'
 cs=rows(contrast)
 with metadata.open(newline='') as mf, audit.open(newline='') as af:
  ms={x['item_id']:x for x in csv.DictReader(mf)}
  aus={x['item_id']:x for x in csv.DictReader(af)}
 ch=hashlib.sha256(contrast.read_bytes()).hexdigest(); mh=hashlib.sha256(metadata.read_bytes()).hexdigest()
 ledger=[];counts={'provenance_recovered':0,'independently_verified_labels':0,'eligible':0}
 for i,r in enumerate(cs,1):
  m=ms.get(r['id'],{});a=aus.get(r['id'],{}); blockers=[]
  identity=bool(m.get('source_arxiv')==r.get('source_arxiv') and m.get('official_url'))
  if identity:counts['provenance_recovered']+=1
  else:blockers.append('exact_source_paper_identity_or_url_missing')
  if not m.get('first_posted_date'):blockers.append('source_publication_date_missing')
  if a.get('abstract_review_status')!='VERIFIED':blockers.append('independent_source_alignment_annotation_missing')
  blockers += ['question_creation_or_version_availability_date_unverified','original_input_paper_ids_missing','shuffled_input_control_unavailable','independently_verified_same_topic_decoy_missing','frozen Q heads and normalization unavailable']
  ledger.append({'candidate_id':r['id'],'question_id':'E1:'+r['id']+':A','question_text':r['A'],'paraphrase_text':r['B_min'],'near_miss_text':r['C'],'source_paper_id':r.get('source_arxiv'),'source_metadata':m or None,'contrast_file_sha256':ch,'contrast_line':i,'metadata_file_sha256':mh,'alignment_status':a.get('abstract_review_status','MISSING'),'independent_human_verified':False,'controls':{'original':'MISSING','empty':'available only in later development workflow','shuffled':'MISSING','same_topic_decoy':'MISSING/UNVERIFIED'},'eligible':False,'blockers':blockers})
  counts['independently_verified_labels']+=int(a.get('abstract_review_status')=='VERIFIED')
 report={'schema':'M-I1-evidence-v1','candidates_examined':len(cs),'exact_source_identity_and_metadata_recovered':counts['provenance_recovered'],'independently_verified_labels':counts['independently_verified_labels'],'eligible_candidates':0,'heldout_evaluation_run':False,'blockers_summary':['E1 alignment audit is pending manual confirmation for candidates.','Question creation/availability dates and original input IDs are absent.','Required original, shuffled, and independently verified same-topic controls are incomplete.','Q readouts and frozen normalization are unavailable.']}
 (out/'candidate_ledger.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in ledger));(out/'eligibility_report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',default='M/data/i1_evidence_v1');a=p.parse_args();print(json.dumps(prepare(a.root,a.out),indent=2))
