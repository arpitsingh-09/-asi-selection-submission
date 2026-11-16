"""Offline importer for externally downloaded, exact OpenReview revision visibility evidence."""
import argparse,csv,hashlib,json
from pathlib import Path
from .training import rows

RELEASE={'conference':'ICLR 2023','released_at':'2022-11-05T01:00:00Z','source_url':'https://iclr.cc/Conferences/2023/Dates','scope':'conference-level review release only; not evidence for any exact review value/version'}
def import_evidence(root,api_jsonl,out):
 root=Path(root);out=Path(out);reviews=rows(root/'M/data/ingestion_v2/review_outcomes.jsonl');by={r['outcome_id']:r for r in reviews}; accepted=[];reasons={}
 for e in rows(api_jsonl):
  rid=e.get('note_id');r=by.get(rid);reason=None
  if not r:reason='unknown_note_id'
  elif e.get('paper_id')!=r.get('paper_id') or e.get('value')!=r.get('value'):reason='note_paper_or_value_mismatch'
  elif not all(e.get(k) for k in ('revision_id','revision_timestamp','public_at','visibility_evidence_url','visibility_evidence_sha256')):reason='missing_exact_revision_or_visibility_evidence'
  elif len(e['visibility_evidence_sha256'])!=64:reason='invalid_visibility_evidence_hash'
  if reason:reasons[reason]=reasons.get(reason,0)+1
  else:accepted.append({**e,'conference_release_evidence':RELEASE,'exact_revision_verified':True})
 out.mkdir(parents=True,exist_ok=False);(out/'verified_exact_revisions.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in accepted))
 report={'conference_release_evidence':RELEASE,'review_records_examined':len(reviews),'external_rows_examined':len(rows(api_jsonl)),'exact_review_versions_verified':len(accepted),'eligible_train_labels':0,'eligible_validation_labels':0,'exclusions':reasons,'blockers':['Conference release date does not prove the exact current local recommendation value matches the November 2022 published version.','Exact version evidence alone does not provide verified question-to-paper links in eligible train/validation manifests.','No later-community-use labels are supplied by this review evidence.']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--api-jsonl',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(import_evidence(a.root,a.api_jsonl,a.out),indent=2))
