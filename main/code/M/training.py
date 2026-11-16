"""Provenance-bound, bounded CPU training. Never encodes or scores heldout rows."""
import argparse
import hashlib
import json
import re
import platform
from pathlib import Path
import numpy as np
from .schema import date, fingerprint, LeakageError
from .temporal import split_for
from .quality import QualityModels, FACTORS
from .engine import ResearchSpace
from .store import PaperStore


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rows(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,indent=2,allow_nan=False)


def validate_record(r):
    for k in ('question_id','paper_id','question','source_dataset','provenance'):
        if not r.get(k):raise ValueError('missing '+k)
    if not isinstance(r['input_paper_ids'],list):raise ValueError('input IDs must be explicit list')
    if len(set(r['input_paper_ids']))!=len(r['input_paper_ids']):raise ValueError('duplicate inputs')
    p=date(r['published']);a=date(r['available_at'])
    if a<p:raise LeakageError('version predates publication')
    split=split_for(p)
    end={'train':'2024-01-01','validation':'2025-01-01'}.get(split)
    if end and a>=date(end):raise LeakageError('version unavailable in partition')
    if r.get('split',split)!=split:raise LeakageError('incorrect partition')
    for name,label in r.get('labels',{}).items():
        if name not in FACTORS:raise ValueError('unknown target')
        if label is None:continue
        if not label.get('source') or not label.get('definition') or not re.fullmatch(r'[0-9a-f]{64}',label.get('evidence_sha256','')):raise ValueError('label provenance required')
        if not isinstance(label.get('evidence_text'),str) or hashlib.sha256(label['evidence_text'].encode()).hexdigest()!=label['evidence_sha256']:raise ValueError('label evidence hash mismatch')
        if not isinstance(label.get('value'),(int,float)) or isinstance(label['value'],bool) or not np.isfinite(label['value']):raise ValueError('numeric observed label required')
        when=date(label['observed_at'])
        if when<p:raise LeakageError('outcome before publication')
        if end and when>=date(end):raise LeakageError('label observed after partition')
    return split


def build(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    groups={s:[] for s in ('train','validation','test','gap')};rejected=[]
    paths=[root/'E2/data/raw_papers.jsonl']
    # Exact source passages only: never turn titles or edited abstracts into questions.
    for path in paths:
        sha=digest(path)
        for line,r in enumerate(rows(path),1):
            abstract=r.get('abstract','');matches=list(re.finditer(r'[^.!?\n]*\?',abstract))
            if not matches:continue
            for n,m in enumerate(matches):
                q=m.group().strip()
                if len(q.split())<5:continue
                rec={'question_id':str(r['paper_id'])+':abstract-question:'+str(n),'paper_id':r['paper_id'],
                    'question':q,'input_paper_ids':[], 'inputs_status':'unavailable_not_inferred',
                    'published':r.get('published'),'available_at':r.get('updated'),
                    'title':r.get('title',''),'abstract':abstract,
                    'source_dataset':str(path.relative_to(root)),
                    'provenance':{'file_sha256':sha,'line':line,'question_span':[m.start(),m.end()],
                        'question_method':'verbatim interrogative passage; not independently validated focal intent',
                        'text_sha256':hashlib.sha256(abstract.encode()).hexdigest(),
                        'date_source':'arXiv API published and updated fields; version availability, not first-global-release proof'},
                    'labels':{f:None for f in FACTORS},'missing_label_status':{f:'no dated outcome evidence' for f in FACTORS}}
                try:
                    split=validate_record(rec);rec['split']=split;groups[split].append(rec)
                except (ValueError,KeyError,TypeError) as e:rejected.append({'question_id':rec['question_id'],'reason':str(e)})
    # E1's questions are authored contrasts, not proven available at paper publication:
    # preserve metadata-only heldout candidates with explicit unresolved eligibility.
    import csv
    meta={r['item_id']:r for r in csv.DictReader((root/'E1/results_v2/source_metadata.csv').open())}
    source=root/'E1/contrast.jsonl';sha=digest(source)
    for line,r in enumerate(rows(source),1):
        m=meta.get(r['id'],{})
        rec={'question_id':'E1:'+r['id']+':A','paper_id':r['source_arxiv'],'question':r['A'],
             'input_paper_ids':[],'inputs_status':'unavailable_not_inferred','published':m.get('first_posted_date'),
             'available_at':m.get('last_updated_date'),'source_dataset':'E1/contrast.jsonl',
             'provenance':{'file_sha256':sha,'line':line,'metadata_file_sha256':digest(root/'E1/results_v2/source_metadata.csv'),
                'question_availability':'unknown; author-created contrast, not original paper quotation'},
             'labels':{f:None for f in FACTORS},'missing_label_status':{f:'no dated outcome evidence' for f in FACTORS},
             'evaluation_eligible':False,'eligibility_blocker':'question creation date and input references unavailable'}
        try:
            split=validate_record(rec)
            if split!='test':raise ValueError('E1 candidates accepted for heldout manifest only')
            rec['split']=split;groups[split].append(rec)
        except (ValueError,KeyError,TypeError) as e:rejected.append({'question_id':rec['question_id'],'reason':str(e)})
    deduplicated=0
    for split,items in groups.items():
        unique={}
        for r in items:
            key=r['question_id']
            if key in unique:
                before={k:v for k,v in unique[key].items() if k!='provenance'}
                after={k:v for k,v in r.items() if k!='provenance'}
                if before!=after:raise ValueError('conflicting duplicate question '+key)
                unique[key]['provenance'].setdefault('duplicate_source_lines',[]).append(r['provenance']['line'])
                deduplicated+=1
            else:unique[key]=r
        groups[split]=list(unique.values())
    for split,items in groups.items():
        with (out/(split+'.jsonl')).open('x') as f:
            for r in items:f.write(json.dumps(r,allow_nan=False)+'\n')
    report={'exact_duplicate_rows_removed':deduplicated,'counts':{s:len(v) for s,v in groups.items()},'genuine_labels':{s:{k:sum(r['labels'].get(k) is not None for r in v) for k in FACTORS} for s,v in groups.items()},
        'rejected':rejected,'heldout_evaluated':False,'limitations':['Verbatim question passages need focal-intent review.','Input references absent; explicit empty-input condition only.','E1 heldout candidates are not evaluation eligible.','No quality labels imputed from text, scores or venue years.']}
    write(out/'manifest_report.json',report);return report


def run(train_path,validation_path,out,alphas=(.1,1.,10.),max_records=128):
    train=rows(train_path);val=rows(validation_path)
    for group,split in ((train,'train'),(val,'validation')):
        if len({r['question_id'] for r in group})!=len(group):raise ValueError('duplicate question IDs')
        for r in group:
            if validate_record(r)!=split:raise LeakageError('wrong training/selection partition')
    if {r['paper_id'] for r in train}&{r['paper_id'] for r in val}:raise LeakageError('paper overlaps train/validation')
    if not alphas or any(not np.isfinite(a) or a<=0 for a in alphas):raise ValueError('positive alpha grid required')
    if not 2<=max_records<=256:raise ValueError('bounded record cap required')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    # Data-dependent fits only use explicit labels. No hidden test file is opened.
    result={'heldout_evaluated':False,'train_records':len(train),'validation_records':len(val),'heads':{},
        'train_sha256':digest(train_path),'validation_sha256':digest(validation_path),'alpha_grid':list(alphas),
        'selection_metric':'2024 validation mean squared error','encoder':'fixed lexical hashing; unvalidated semantic quality',
        'input_condition':'explicit supplied IDs; no inferred citation edges','max_records_per_split':max_records,
        'normalization':'feature mean and standard deviation fit on TRAIN only',
        'runtime':{'python':platform.python_version(),'numpy':np.__version__},
        'fit_method':'closed-form ridge; validation MSE selects alpha; ties choose smaller alpha'}
    validation_predictions=[]
    for factor in FACTORS:
        tr=[r for r in train if r.get('labels',{}).get(factor) is not None and date(r['available_at'])==date(r['published'])]
        va=[r for r in val if r.get('labels',{}).get(factor) is not None and date(r['available_at'])==date(r['published'])]
        tr=sorted(tr,key=lambda r:r['question_id'])[:max_records];va=sorted(va,key=lambda r:r['question_id'])[:max_records]
        if len(tr)<2 or not va:
            result['heads'][factor]={'status':'unavailable','train_labels_at_publication':len(tr),'validation_labels_at_publication':len(va),'reason':'need >=2 dated training labels and >=1 dated validation label on publication-time text'};continue
        # Context metadata must be supplied explicitly; unresolved nonempty R fails.
        papers={r['paper_id']:{'paper_id':r['paper_id'],'published':r['published'],'available_at':r['available_at'],'question':r['question'],'abstract':r.get('abstract',''),'title':r.get('title','')} for r in train+val}
        space=ResearchSpace(PaperStore(papers.values()))
        def encode(rs):return [space.encode(r['question'],r['input_paper_ids'],r['published'],source_kind='published',paper_id=r['paper_id']) for r in rs]
        ts=encode(tr);vs=encode(va);x=np.asarray([s.vector for s in ts]);v=np.asarray([s.vector for s in vs]);y=np.array([r['labels'][factor]['value'] for r in tr]);truth=np.array([r['labels'][factor]['value'] for r in va])
        mean=x.mean(0);scale=x.std(0);scale[scale<1e-8]=1;z=(x-mean)/scale;vz=(v-mean)/scale;intercept=float(y.mean());scores=[];models={}
        for alpha in sorted(set(alphas)):
            coef=np.einsum('ij,i->j',z,np.linalg.solve(np.einsum('ik,jk->ij',z,z)+alpha*np.eye(len(z)),y-intercept))
            pred=np.einsum('ij,j->i',vz,coef)+intercept;mse=float(np.mean((pred-truth)**2));scores.append({'alpha':alpha,'mse':mse});models[alpha]=coef
        best=min(scores,key=lambda s:(s['mse'],s['alpha']));a=best['alpha']
        artifact={'factors':list(FACTORS),'space_id':ts[0].space_id,'feature_schema':ts[0].feature_schema,'feature_dimension':x.shape[1],
            'mean':mean.tolist(),'scale':scale.tolist(),'heads':{f:None for f in FACTORS},'trained_until':max(date(r['labels'][factor]['observed_at']) for r in tr).isoformat(),
            'alpha':a,'training_snapshot_ids':[s.snapshot_id for s in ts],'training_data_fingerprint':fingerprint(tr),'accuracy_established':False,
            'target_definitions':sorted({r['labels'][factor]['definition'] for r in tr})}
        if len(artifact['target_definitions'])!=1 or {r['labels'][factor]['definition'] for r in va}!=set(artifact['target_definitions']):raise ValueError('incompatible label target definitions')
        artifact['heads'][factor]={'coefficients':models[a].tolist(),'intercept':intercept}
        model_path=out/(factor+'.json')
        QualityModels(artifact).save(model_path)
        prediction_values=np.einsum('ij,j->i',vz,models[a])+intercept
        for record,prediction in zip(va,prediction_values):
            label=record['labels'][factor]
            validation_predictions.append({
                'factor':factor,'question_id':record['question_id'],'paper_id':record['paper_id'],
                'prediction':float(prediction),'observed_value':float(label['value']),
                'observed_at':label['observed_at'],'label_source':label['source'],
                'label_evidence_sha256':label['evidence_sha256'],
            })
        result['heads'][factor]={'status':'fitted','selected_alpha':a,'validation_mse':best['mse'],'candidates':scores,
            'training_ids':[r['question_id'] for r in tr],'validation_ids':[r['question_id'] for r in va],
            'model_sha256':digest(model_path)}
    if validation_predictions:
        prediction_path=out/'validation_predictions.jsonl'
        with prediction_path.open('x') as f:
            for prediction in validation_predictions:f.write(json.dumps(prediction,sort_keys=True,allow_nan=False)+'\n')
        result['validation_predictions_sha256']=digest(prediction_path)
    write(out/'validation_results.json',result);return result


def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    b=s.add_parser('build');b.add_argument('--root',default='.');b.add_argument('--out',required=True)
    f=s.add_parser('fit');f.add_argument('--train',required=True);f.add_argument('--validation',required=True);f.add_argument('--out',required=True)
    a=p.parse_args();print(json.dumps(build(a.root,a.out) if a.command=='build' else run(a.train,a.validation,a.out),indent=2))
if __name__=='__main__':main()
