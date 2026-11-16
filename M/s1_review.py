"""Blind independent S1 review packets and source-bound human consensus import."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
from datetime import datetime,timezone
from .evidence import iter_bound,assertion,verify_assertion
from .schema import date

SEED=20261113

def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def write(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False)
def jsonl(path,items):
    with Path(path).open('x') as f:
        for r in items:f.write(json.dumps(r,sort_keys=True)+'\n')
def rows(path):
    with Path(path).open() as f:return [json.loads(l) for l in f if l.strip()]


def prepare(root,out):
    root=Path(root).resolve();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    metadata_path=root/'E1/results_v2/source_metadata.csv'
    with metadata_path.open() as f:metadata={r['item_id']:r for r in csv.DictReader(f)}
    metadata_sha=hashlib.sha256(metadata_path.read_bytes()).hexdigest();manifest=[];packet=[]
    for r,b in iter_bound(root/'E1/contrast.jsonl'):
        m=metadata.get(r['id'],{});source_id=r['source_arxiv']
        identifier_match=source_id==m.get('source_arxiv') and m.get('metadata_status')=='FOUND'
        for variant,task in [('B_min','minimal_paraphrase'),('C','near_miss')]:
            content={'anchor':r['A'],'candidate':r[variant]};fingerprint=sha(json.dumps(content,sort_keys=True));pid=sha(r['id']+':'+variant+':'+fingerprint)[:24]
            item={'pair_id':pid,'item_id':r['id'],'task':task,'pair_sha256':fingerprint,**content,
                'source_author':r.get('author'),'source_evidence':{k:assertion(b,[field],r[field]) for k,field in [('anchor','A'),('candidate',variant),('source_id','source_arxiv')]},
                'source_paper_id':source_id,'source_identifier_link_verified':identifier_match,
                'paper_first_posted':m.get('first_posted_date') if identifier_match else None,
                'paper_version_available_at':m.get('last_updated_date') if identifier_match else None,
                'paper_metadata_provenance':{'path':str(metadata_path),'sha256':metadata_sha,'key':r['id'],'official_url':m.get('official_url')},
                'question_publication_date':None,'question_available_at':None,
                'original_input_ids':None,'source_paper_is_original_input':'UNVERIFIED; identifier association is not semantic source alignment',
                'prior_review_status':'UNVERIFIED; original dataset labels are proposals, not human confirmation',
                'annotation_status':'PENDING_INDEPENDENT_HUMAN_REVIEW','eligible':False}
            context={'paper_id':source_id,'url':m.get('official_url'),'title':m.get('paper_title'),'abstract':m.get('abstract'),
                'paper_first_posted':m.get('first_posted_date'),'warning':'Paper dates are not authored-question creation dates'}
            item['source_context_sha256']=sha(json.dumps(context,sort_keys=True))
            manifest.append(item)
            packet.append({'pair_id':pid,'pair_sha256':fingerprint,**content,'source_context':{'paper_id':source_id,'url':m.get('official_url'),'title':m.get('paper_title'),'abstract':m.get('abstract'),
                'paper_first_posted':m.get('first_posted_date'),'warning':'Paper dates are not authored-question creation dates'},
                'reviewer_id':None,'reviewer_kind':None,
                'independent_of_author':None,'same_question':None,'source_alignment_verified':None,
                'rationale':None,'reviewed_at':None})
    manifest.sort(key=lambda r:r['pair_id']);random.Random(SEED).shuffle(packet)
    jsonl(out/'annotation_manifest.jsonl',manifest);jsonl(out/'blind_review_template.jsonl',packet)
    texts=sorted({r[k] for r in manifest for k in ('anchor','candidate')})
    write(out/'embedding_requests.json',{'purpose':'B-Q preparation only; not evaluation','texts':texts,'count':len(texts)})
    result={'pairs':len(manifest),'focal_questions':len({r['item_id'] for r in manifest}),
        'identifier_links':sum(r['source_identifier_link_verified'] for r in manifest),
        'paper_dates_recovered':sum(r['paper_first_posted'] is not None for r in manifest),
        'verified_question_dates':0,'verified_original_inputs':0,'human_verified_pairs':0,'eligible_pairs':0}
    write(out/'summary.json',result);return result


def import_reviews(manifest_path,review_paths,out):
    manifest=rows(manifest_path);by_id={r['pair_id']:r for r in manifest};votes={k:[] for k in by_id};rejected=[]
    for path in review_paths:
        for r,b in iter_bound(path):
            try:
                item=by_id[r['pair_id']]
                if sha(json.dumps(r.get('source_context'),sort_keys=True))!=item['source_context_sha256']:raise ValueError('review source context changed')
                for k in ('pair_sha256','anchor','candidate'):
                    if r.get(k)!=item[k]:raise ValueError('review text/hash mismatch')
                if r.get('reviewer_kind')!='human' or r.get('independent_of_author') is not True:raise ValueError('independent human attestation required')
                reviewer=r.get('reviewer_id')
                if not isinstance(reviewer,str) or not reviewer.strip() or reviewer.strip().casefold() in {str(item.get('source_author','')).casefold(),'codex','ai','assistant'}:raise ValueError('independent reviewer identity required')
                if type(r.get('same_question')) is not bool or type(r.get('source_alignment_verified')) is not bool:raise ValueError('explicit reviewed relation and alignment required')
                if not isinstance(r.get('rationale'),str) or not r['rationale'].strip():raise ValueError('rationale required')
                date(r['reviewed_at'])
                if date(r['reviewed_at'])>datetime.now(timezone.utc):raise ValueError('future review timestamp')
                if any(v['reviewer_id']==reviewer.strip() for v in votes[r['pair_id']]):raise ValueError('duplicate reviewer; repeated votes do not create independence')
                votes[r['pair_id']].append({'reviewer_id':reviewer.strip(),'label':r['same_question'],'alignment':r['source_alignment_verified'],
                    'evidence':{k:assertion(b,[k],r[k]) for k in ('reviewer_id','reviewer_kind','independent_of_author','same_question','source_alignment_verified','rationale','reviewed_at')}})
            except (KeyError,ValueError,TypeError) as e:rejected.append({'pair_id':r.get('pair_id'),'reason':str(e)})
    imported=[]
    for item in manifest:
        v=votes[item['pair_id']];agreement=len(v)>=2 and len({r['label'] for r in v})==1 and all(r['alignment'] for r in v)
        status='HUMAN_CONSENSUS' if agreement else 'DISAGREEMENT_OR_ALIGNMENT_REJECTED' if len(v)>=2 else 'PENDING_SECOND_HUMAN' if v else 'PENDING_HUMAN'
        for proof in item['source_evidence'].values():verify_assertion(proof)
        imported.append(dict(item,annotation_status=status,human_label=v[0]['label'] if agreement else None,
            human_votes=v,eligible=False,eligibility_blockers=['Question availability/creation date unverified','Original/shuffled input links and independent same-topic decoy missing','Frozen semantic model training cutoff missing']))
    out=Path(out);out.mkdir(parents=True,exist_ok=False);jsonl(out/'reviewed_manifest.jsonl',imported)
    summary={'human_verified_pairs':sum(r['annotation_status']=='HUMAN_CONSENSUS' for r in imported),'eligible_pairs':0,
        'rejected_reviews':rejected,'real_evaluation_executed':False,'status':'BLOCKED'}
    write(out/'summary.json',summary);return summary


def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('prepare');a.add_argument('--root',default='.');a.add_argument('--out',required=True)
    a=s.add_parser('import');a.add_argument('--manifest',required=True);a.add_argument('--reviews',nargs='+',required=True);a.add_argument('--out',required=True)
    a=p.parse_args();print(json.dumps(prepare(a.root,a.out) if a.command=='prepare' else import_reviews(a.manifest,a.reviews,a.out),indent=2))
if __name__=='__main__':main()
