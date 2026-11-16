"""Bounded local outcome recovery and separate core eligibility cohorts.
Produces source-bound observations, never synthetic labels or evaluation claims.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import re
from pathlib import Path
from .evidence import iter_bound,assertion,read_bound,verify_assertion
from .evaluation import TESTS
from .schema import date
from .import_dated_quality_labels import verify_dated_outcome

REASONS={
'I1':['No verified original input links, shuffled/independently verified decoy controls.','No fitted Q heads or frozen normalization for every readout.'],
'I3':['No length-matched dated Q/N preference labels linked to M questions.','Q heads unavailable.'],
'S1':['E1 source-alignment/second-reader annotations are unverified.','Question creation dates and original input/control links unavailable.','No verified cache model training cutoff.'],
'A1':['Existing E2 results are previously evaluated development evidence, not prospective M tests.','No new heldout partial-coverage/concentration cohort with original inputs and four controls.'],
'H1':['No local source-bound expert battles linked to seed IDs and generating systems with dated labels.','Q heads unavailable.'],
'H3':['No post-July-2025 original question/version and review-observation-date linkage.','Q heads, semantic B-Q and independently estimated human ceiling unavailable.'],
'O1':['No dated peer-review AND community-use outcomes linked to postcutoff question versions within topic.','Both Q heads unavailable.'],
'O2':['No verified identical >=3-seed citation groups, within-year dates and dated outcome linkage.','Q outcome prediction unavailable.'],
'T1':['No separately trained and prospectively frozen 2022 and 2023 head artifacts.','No complete-head normalized predictions and original input controls.']}

def utc_ms(x):
    if not isinstance(x,(int,float)) or isinstance(x,bool) or x<=0:return None
    return datetime.fromtimestamp(x/1000,timezone.utc).isoformat()

def unwrap(v):return v.get('value') if isinstance(v,dict) else v

def recover_review(r,binding):
    if r.get('_kind')!='Official_Review':return None
    content=r.get('content',{});key=next((k for k in ('rating','recommendation') if k in content),None)
    if key is None:return None
    raw=unwrap(content[key]);m=re.match(r'^\s*([0-9]+(?:\.[0-9]+)?)(?:\s*:|\s*$)',str(raw))
    if not m:return None
    identity=r.get('forum')
    if not identity or identity!=r.get('_paper_forum',identity):raise ValueError('review/forum identity mismatch')
    value=float(m.group(1));path=['content',key]+(['value'] if isinstance(content[key],dict) else [])
    # tmdate is version metadata, never substituted for public observation.
    latest=max([x for x in (r.get('tmdate'),r.get('mdate'),r.get('tcdate'),r.get('cdate')) if isinstance(x,(int,float)) and not isinstance(x,bool)],default=0)
    opened=utc_ms(r.get('odate'));version=utc_ms(latest)
    # Even odates earlier than the current version do not prove this value existed then.
    observed=opened if opened and version and date(opened)>=date(version) else None
    return {'outcome_id':r['id'],'paper_id':identity,'factor':'peer_review',
        'value':value,'definition':f'ICLR {r.get("_year")} {key} raw numeric scale; do not pool across rubrics',
        'observed_at':observed,'observed_at_status':'public release of current version' if observed else 'unknown_public_availability_of_current_value',
        'record_version_timestamp':version,'record_opened_timestamp':opened,
        'public_readers_now':r.get('readers',[]),'observation_is_publication_date':False,
        'value_evidence':assertion(binding,path,raw),'identity_evidence':assertion(binding,['forum'],identity),
        'usable_for_fitting':False,'missing_dependencies':['Original question/version identity and paper date linkage','Public availability of this exact review version' ] if observed is None else ['Original question/version identity and paper date linkage']}


def verify_outcome(o):
    if o.get('source_type')=='M_DATED_QUALITY_LABEL':
        return verify_dated_outcome(o)
    verify_assertion(o['value_evidence']);verify_assertion(o['identity_evidence'])
    r=read_bound(o['value_evidence']['binding']);expected=recover_review(r,o['value_evidence']['binding'])
    if expected is None or any(o.get(k)!=expected.get(k) for k in ('outcome_id','paper_id','factor','value','definition','observed_at','record_version_timestamp','usable_for_fitting')):raise ValueError('derived outcome disagrees with source evidence')
    return True


def prepare(root,out,review_limit=1000):
    root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    if not 1<=review_limit<=1000:raise ValueError('bounded review limit 1–1000 required')
    recovered=[];sources=[]
    # Fixed bounded prefixes are recovery/development material, never confirmatory cohorts.
    for year in (2023,2024):
        p=Path.home()/f'Downloads/iclr_task3_baseline/data/iclr_{year}/reviews.jsonl'
        if not p.exists():continue
        scanned=0;count=0
        for r,b in iter_bound(p,review_limit):
            scanned+=1;o=recover_review(r,b)
            if o is not None:o['source_year']=year
            if o is not None:recovered.append(o);count+=1
        sources.append({'path':str(p),'records_scanned':scanned,'outcomes_recovered':count,'scan_rule':'first fixed 1000 records maximum; no outcome-based selection'})
    paper_links=[]
    for year in (2023,2024):
        targets={o['paper_id'] for o in recovered if o['source_year']==year}
        path=Path.home()/f'Downloads/iclr_task3_baseline/data/iclr_{year}/papers.jsonl'
        for paper,b in iter_bound(path):
            if paper.get('forum',paper.get('id')) not in targets:continue
            content=paper.get('content',{});abstract=unwrap(content.get('abstract',''));title=unwrap(content.get('title',''))
            paper_links.append({'paper_id':paper.get('forum',paper.get('id')),'source_year':year,
                'identity_evidence':assertion(b,['id'],paper['id']),
                'paper_record_binding':b,'title':title,
                'verbatim_question_candidates':[m.group().strip() for m in re.finditer(r'[^.!?\n]*\?',abstract) if len(m.group().split())>=5],
                'question_intent_human_verified':False,'original_input_ids':None,
                'paper_public_open_timestamp':utc_ms(paper.get('odate')),
                'paper_version_timestamp':utc_ms(paper.get('tmdate')),
                'status':'IDENTITY_LINK_ONLY_NOT_ELIGIBLE'})
    write(out/'review_paper_links.json',paper_links)
    with (out/'review_outcomes.jsonl').open('x') as f:
        for o in recovered:f.write(json.dumps(o)+'\n')
    # Explicitly recover aggregate benchmarks but keep missing observation dates visible.
    benchmark=[]
    for r,b in iter_bound(root/'E2/analysis/openreview_archive_v1/benchmark_records.jsonl'):
        if r.get('rating') is not None:
            benchmark.append({'paper_id':r['forum_id'],'value':r['rating'],'observed_at':None,'status':'undated_aggregate_not_individual_review',
                 'evidence':assertion(b,['rating'],r['rating']),'usable':False})
    write(out/'benchmark_aggregates.json',benchmark)
    # Input review statuses are existing declarations, never upgraded by AI.
    import csv
    alignment=list(csv.DictReader((root/'E1/results_v2/source_alignment_audit.csv').open()))
    counts={}
    for r in alignment:counts[r['abstract_review_status']]=counts.get(r['abstract_review_status'],0)+1
    controls={'E1_alignment_status_counts':counts,'E1_source_file_sha256':hashlib.sha256((root/'E1/results_v2/source_alignment_audit.csv').read_bytes()).hexdigest()}
    summary={'schema':'M-ingestion-v1','review_sources':sources,'genuine_source_review_values':len(recovered),
        'verified_public_observation_dates':sum(o['observed_at'] is not None for o in recovered),
        'paper_identity_links':len(paper_links),'linked_papers_with_verbatim_question_candidates':sum(bool(p['verbatim_question_candidates']) for p in paper_links),
        'usable_question_linked_labels':0,'undated_benchmark_aggregates':len(benchmark),'annotation_status':controls,
        'real_evaluations':0,'cohorts':{}}
    for test in TESTS:
        (out/(test+'_eligible.jsonl')).touch(exist_ok=False)
        receipt={'schema':'M-core-readiness-v2','test':test,'status':'BLOCKED','eligible_records':0,
            'heldout_evaluated':False,'metrics':None,'ci95':None,'baseline_comparisons':None,'missing_dependencies':REASONS[test]}
        write(out/(test+'_status.json'),receipt);summary['cohorts'][test]=receipt
    write(out/'summary.json',summary);return summary

def write(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',required=True);a=p.parse_args()
    r=prepare(a.root,a.out);print(json.dumps({k:v for k,v in r.items() if k not in ('cohorts','annotation_status')},indent=2))
