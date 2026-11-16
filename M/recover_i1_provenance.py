"""Recover only fields explicitly present in existing E1 source records."""
import argparse,csv,hashlib,json
from pathlib import Path
from .training import rows

def recover(root='.',out='M/data/i1_provenance_v1'):
 root=Path(root);out=root/out if not Path(out).is_absolute() else Path(out);out.mkdir(parents=True,exist_ok=False)
 contrast=root/'E1/contrast.jsonl';meta=root/'E1/results_v2/source_metadata.csv';ledger=rows(root/'M/data/i1_evidence_v1/candidate_ledger.jsonl')
 originals={x['id']:x for x in rows(contrast)}
 with meta.open(newline='') as f: metadata={x['item_id']:x for x in csv.DictReader(f)}
 ch=hashlib.sha256(contrast.read_bytes()).hexdigest();mh=hashlib.sha256(meta.read_bytes()).hexdigest();outrows=[]
 for x in ledger:
  q=originals.get(x['candidate_id'],{});m=metadata.get(x['candidate_id'],{});pid=q.get('source_arxiv'); exact=bool(pid and pid==m.get('source_arxiv') and m.get('metadata_status')=='FOUND')
  outrows.append({'candidate_id':x['candidate_id'],'question_id':x['question_id'],'question_text':q.get('A'),'question_source':{'file':'E1/contrast.jsonl','line':x.get('contrast_line'),'sha256':ch,'identity_confidence':'high' if q else 'missing'},'source_paper':{'paper_id':pid if exact else None,'title':m.get('paper_title') if exact else None,'url':m.get('official_url') if exact else None,'published_at':m.get('first_posted_date') if exact else None,'available_at':m.get('last_updated_date') if exact else None,'evidence':{'file':'E1/results_v2/source_metadata.csv','sha256':mh,'status':m.get('metadata_status')},'confidence':'high_metadata_identity' if exact else 'unverified'},'question_created_at':None,'question_created_at_status':'MISSING_NO_CREATION_TIMESTAMP_IN_SOURCE','original_input_paper_ids':None,'input_ids_status':'MISSING_NOT_RECORDED; source paper association is not an input link','temporal_eligible':False,'missing':['question creation/availability date','original input paper IDs','input paper versions and availability dates']})
 report={'schema':'M-I1-provenance-v1','questions_examined':len(outrows),'verified_creation_dates':0,'verified_original_input_sets':0,'source_paper_identity_recovered':sum(bool(r['source_paper']['paper_id']) for r in outrows),'temporally_eligible_records':0,'heldout_evaluation_run':False,'remaining_blockers':['E1 contrast records identify an associated source paper, not disclosed original inputs.','No question creation or version availability timestamps are present.','Thus input-before-question temporal ordering cannot be verified.']}
 (out/'provenance_ledger.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in outrows));(out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',default='M/data/i1_provenance_v1');a=p.parse_args();print(json.dumps(recover(a.root,a.out),indent=2))
