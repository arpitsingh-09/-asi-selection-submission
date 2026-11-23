#!/usr/bin/env python3
"""Offline structural/provenance checks for the original S1 evidence inventories."""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, re, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
Q=HERE/'E1_QUESTION_HISTORY.csv'; P=HERE/'E1_PAPER_INPUTS.csv'; C=HERE/'E1_S1_CONTROLS.csv'
V=HERE/'E1_FIRST_COMMITTED_QUESTION_VERSIONS.csv'; SRC=HERE/'E1_contrast.jsonl'
HEX=re.compile(r'^[0-9a-fA-F]{64}$')
IDS={f'h{i:03d}' for i in range(1,63)}-{'h028'}
CONDS={'original','empty','cross_instance_shuffled','same_topic_unsupported_decoy'}
QCOL={'question_id','exact_question_text','question_version','creation_timestamp','sharing_timestamp','timestamp_timezone','original_source_path','source_sha256','timestamp_evidence_path','evidence_reference','creation_timestamp_status','sharing_timestamp_status','verification_status'}
PCOL={'question_id','paper_id','paper_version','paper_sha256','paper_availability_date','original_input_manifest_path','availability_evidence_path','evidence_status'}
CCOL={'question_id','condition','source_question_id','source_paper_ids','source_paper_versions','source_record_path','source_sha256','independent_decoy_verification_path','evidence_status'}
STAT={'VERIFIED','PARTIAL','MISSING','UNVERIFIED'}
def load(p):
 with p.open(newline='',encoding='utf-8') as f:
  r=csv.DictReader(f); return set(r.fieldnames or []),list(r)
def exists_ref(s):
 s=(s or '').strip()
 if not s:return False
 # Drop CSV evidence-reference fragments such as #question_id=h001.
 path=s.split('#',1)[0]
 p=Path(path)
 return (p if p.is_absolute() else HERE/p).is_file()
def parse_time(s):
 try:return dt.datetime.fromisoformat(s.replace('Z','+00:00'))
 except Exception:return None
def main():
 err=[]; result={}
 for p in [Q,P,C,V,SRC]:
  if not p.is_file():err.append(f'missing required evidence input: {p.name}')
 qcols,qr=load(Q); pcols,pr=load(P); ccols,cr=load(C); _,vr=load(V)
 for name,actual,required in [('question',qcols,QCOL),('paper-input',pcols,PCOL),('control',ccols,CCOL)]:
  missing=sorted(required-actual)
  if missing:err.append(f'{name}: missing columns {missing}')
 qids=[r.get('question_id','') for r in qr]
 if len(qr)!=61:err.append(f'question-history rows={len(qr)}; expected 61')
 if len(set(qids))!=len(qids):err.append('duplicate question-history IDs')
 if set(qids)!=IDS:err.append(f'question-history ID mismatch missing={sorted(IDS-set(qids))} extra={sorted(set(qids)-IDS)}')
 source={}
 with SRC.open(encoding='utf-8') as f:
  for line in f:
   if line.strip():
    x=json.loads(line);source[x['id']]=x
 versions={x.get('question_id'):x for x in vr}
 ts_verified=0
 for r in qr:
  qid=r.get('question_id','')
  if not HEX.fullmatch(r.get('source_sha256','')):err.append(f'{qid}: source_sha256 malformed')
  if r.get('verification_status') not in STAT:err.append(f'{qid}: invalid verification_status')
  for field in ('creation_timestamp_status','sharing_timestamp_status'):
   if r.get(field) not in STAT:err.append(f'{qid}: invalid {field}')
  for val,status_field,label in [(r.get('creation_timestamp',''), 'creation_timestamp_status','creation'),(r.get('sharing_timestamp',''),'sharing_timestamp_status','sharing')]:
   if r.get(status_field)=='VERIFIED':
    ts_verified+=1
    parsed=parse_time(val)
    if not parsed or parsed.tzinfo is None or parsed.utcoffset() is None:err.append(f'{qid}: {label} timestamp VERIFIED but timestamp is missing or lacks timezone')
    if not r.get('timestamp_timezone','').strip():err.append(f'{qid}: {label} timestamp VERIFIED but timezone field blank')
    ev=r.get('timestamp_evidence_path','').strip()
    if not exists_ref(ev):err.append(f'{qid}: {label} timestamp VERIFIED without existing evidence file')
    elif '.git' in ev.lower() or 'git' in ev.lower():err.append(f'{qid}: Git metadata cannot verify {label} timestamp')
  if r.get('verification_status')=='VERIFIED' and (r.get('creation_timestamp_status')!='VERIFIED' or r.get('sharing_timestamp_status')!='VERIFIED'):
   err.append(f'{qid}: whole question history VERIFIED without both timestamp checks VERIFIED')
  v=versions.get(qid)
  if not v:err.append(f'{qid}: missing first-observed Git version reference')
  else:
   if v.get('record_sha256')!=r.get('source_sha256'):err.append(f'{qid}: source hash differs from preserved Git-record hash')
   if v.get('first_observed_commit_sha','') not in r.get('question_version',''):err.append(f'{qid}: Git version reference mismatch')
  try:text=json.loads(r.get('exact_question_text',''))
  except Exception:err.append(f'{qid}: exact_question_text invalid JSON');text={}
  expected={k:source.get(qid,{}).get(k,'') for k in ('A','B','B_min','C','C_tilde','narrower','broader')}
  if text!=expected:err.append(f'{qid}: question text differs from preserved E1 snapshot')
 result['question_history']={'rows':len(qr),'questions_with_local_git_versions':sum(bool(r.get('question_version')) for r in qr),'verified_creation_timestamps':sum(r.get('creation_timestamp_status')=='VERIFIED' for r in qr),'verified_sharing_timestamps':sum(r.get('sharing_timestamp_status')=='VERIFIED' for r in qr)}
 # A paper may have multiple rows per question; require full question coverage, not uniqueness.
 pids=[r.get('question_id','') for r in pr]
 if not IDS.issubset(set(pids)):err.append(f'paper-input inventory lacks question rows for {sorted(IDS-set(pids))}')
 verified_papers=0
 for i,r in enumerate(pr,1):
  if r.get('evidence_status') not in STAT:err.append(f'paper row {i}: invalid evidence_status')
  if r.get('evidence_status')=='VERIFIED':
   verified_papers+=1
   if not all(r.get(k,'').strip() for k in ('paper_id','paper_version','paper_sha256','paper_availability_date','original_input_manifest_path','availability_evidence_path')):err.append(f'paper row {i}: VERIFIED but required input fields missing')
   if not HEX.fullmatch(r.get('paper_sha256','')):err.append(f'paper row {i}: malformed paper_sha256')
   for k in ('original_input_manifest_path','availability_evidence_path'):
    if not exists_ref(r.get(k,'')):err.append(f'paper row {i}: VERIFIED evidence path missing: {k}')
 result['paper_inputs']={'rows':len(pr),'questions_covered':len(set(pids)&IDS),'verified_input_records':verified_papers}
 combos=[(r.get('question_id',''),r.get('condition','')) for r in cr]
 if len(cr)!=244:err.append(f'control rows={len(cr)}; expected 244')
 if len(set(combos))!=len(combos):err.append('duplicate question-condition control row')
 expected={(qid,c) for qid in IDS for c in CONDS}
 if set(combos)!=expected:err.append(f'control coverage mismatch missing={len(expected-set(combos))} extra={len(set(combos)-expected)}')
 verified_controls=0
 for i,r in enumerate(cr,1):
  if r.get('evidence_status') not in STAT:err.append(f'control row {i}: invalid evidence_status')
  if r.get('evidence_status')!='VERIFIED':continue
  verified_controls+=1; cond=r.get('condition')
  if not r.get('source_record_path','').strip() or not exists_ref(r.get('source_record_path','')):err.append(f'control row {i}: VERIFIED source record missing')
  if not HEX.fullmatch(r.get('source_sha256','')):err.append(f'control row {i}: VERIFIED source hash malformed')
  if cond in {'original','same_topic_unsupported_decoy','cross_instance_shuffled'} and (not r.get('source_paper_ids','').strip() or not r.get('source_paper_versions','').strip()):err.append(f'control row {i}: VERIFIED {cond} lacks paper IDs/versions')
  if cond=='cross_instance_shuffled' and not r.get('source_question_id','').strip():err.append(f'control row {i}: VERIFIED shuffle lacks source question ID')
  if cond=='same_topic_unsupported_decoy' and not exists_ref(r.get('independent_decoy_verification_path','')):err.append(f'control row {i}: VERIFIED decoy lacks independent verification file')
 result['controls']={'rows':len(cr),'question_condition_pairs':len(set(combos)),'verified_condition_records':verified_controls}
 result['validation_errors']=err
 print(json.dumps(result,indent=2))
 if err:return 1
 print('PASS: all three inventories are structurally valid; every VERIFIED claim has required source support.')
 return 0
if __name__=='__main__':raise SystemExit(main())
