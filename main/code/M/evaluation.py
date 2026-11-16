"""Core battery over provenance-bound frozen predictions; real execution locked."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from .schema import date

TESTS=('I1','I3','S1','A1','H1','H3','O1','O2','T1')
CONTROLS=('original','empty','shuffled','decoy')
UNITS={'I1':'focal_question','I3':'paper_pair_component','S1':'focal_question','A1':'focal_paper','H1':'seed_battle_component','H3':'paper','O1':'topic','O2':'seed_component','T1':'paper'}
READOUTS=('I','N','G','Q_peer_review','Q_later_community_use','D','T')
SEED=20261113
DRAWS=2000
MARGIN=.02

class Blocked(ValueError):pass

def finite(x):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not np.isfinite(x):raise Blocked('missing/nonfinite numeric prediction or label')
    return float(x)

def rank(x):
    a=np.asarray(x);return np.array([1+np.sum(a<v)+(np.sum(a==v)-1)/2 for v in a])

def corr(x,y):
    a=rank(x);b=rank(y)
    if len(a)<3 or np.std(a)==0 or np.std(b)==0:raise Blocked('correlation needs >=3 nonconstant observations')
    return float(np.corrcoef(a,b)[0,1])

def concordance(pred,label):
    return .5 if pred==0 else float(np.sign(pred)==np.sign(label))

def metric(test,rs,control):
    p=[r['predictions'][control] for r in rs]
    avg=lambda x:float(np.mean(x))
    if test=='I1':return {k:avg([finite(v[k]['near_miss_drift'])-finite(v[k]['paraphrase_drift']) for v in p]) for k in READOUTS}
    if test=='I3':
        keys=sorted(p[0]['scores'])
        if not keys or not any(k.startswith('Q') for k in keys) or not any(k.startswith('N') for k in keys):raise Blocked('all claimed Q and N coordinates required')
        return {k:avg([concordance(finite(v['scores'][k]),finite(r['label']))-concordance(finite(v['B-LEN']),finite(r['label'])) for r,v in zip(rs,p)]) for k in keys}
    if test=='S1':
        return {task:avg([float(bool(v['decision'])==bool(r['label']))-float(bool(v['B-Q'])==bool(r['label'])) for r,v in zip(rs,p) if r['task']==task]) for task in ('near_miss','minimal_paraphrase') if any(r['task']==task for r in rs)}
    if test=='A1':
        # Supplied deltas are signed in the preregistered axiom direction.
        return {coordinate+':'+axiom:avg([float(finite(v['scores'][coordinate])>0) for r,v in zip(rs,p) if r['axiom']==axiom]) for coordinate in sorted(p[0]['scores']) for axiom in sorted({r['axiom'] for r in rs})}
    if test=='H1':
        raw=avg([concordance(finite(v['score_a'])-finite(v['score_b']),finite(r['label']))-concordance(finite(v['B-Q_a'])-finite(v['B-Q_b']),finite(r['label'])) for r,v in zip(rs,p)])
        # Endpoints retain system identity; demean each endpoint, not pair differences.
        means={}
        for key in ('score','B-Q'):
            for system in {r[s] for r in rs for s in ('system_a','system_b')}:
                values=[finite(v[key+'_'+s]) for r,v in zip(rs,p) for s in ('a','b') if r['system_'+s]==system]
                means[key,system]=avg(values)
        dem=avg([concordance((finite(v['score_a'])-means['score',r['system_a']])-(finite(v['score_b'])-means['score',r['system_b']]),finite(r['label']))-concordance((finite(v['B-Q_a'])-means['B-Q',r['system_a']])-(finite(v['B-Q_b'])-means['B-Q',r['system_b']]),finite(r['label'])) for r,v in zip(rs,p)])
        return {'raw_improvement':raw,'system_demeaned_improvement':dem}
    if test=='H3':
        y=[finite(r['label']) for r in rs];ceiling={finite(r['ceiling']) for r in rs}
        if len(ceiling)!=1 or not 0<next(iter(ceiling))<=1:raise Blocked('one independently estimated human ceiling required')
        q=corr([finite(v['score']) for v in p],y);b=corr([finite(v['B-Q']) for v in p],y)
        return {'spearman_improvement':q-b,'spearman':q,'share_of_ceiling':q/next(iter(ceiling))}
    if test in ('O1','O2'):
        baseline='B-Q' if test=='O1' else 'B-TF'
        factors=('peer_review','later_community_use') if test=='O1' else ('outcome',)
        return {f:avg([concordance(finite(v[f]),finite(r['labels'][f]))-concordance(finite(v[baseline][f]),finite(r['labels'][f])) for r,v in zip(rs,p)]) for f in factors}
    if test=='T1':return {k:avg([abs(finite(v[k]['Y'])-finite(v[k]['Y_minus_1'])) for v in p]) for k in READOUTS}
    raise ValueError('unknown test')


def bootstrap(test,rs,control,draws=DRAWS):
    """Paired cluster bootstrap: one draw for models, baselines, conditions."""
    ids=sorted({r['unit_id'] for r in rs});groups={k:[r for r in rs if r['unit_id']==k] for k in ids}
    estimate=metric(test,rs,control)
    if len(ids)<2:raise Blocked('at least two independent resampling units required')
    rng=np.random.default_rng(SEED);samples={k:[] for k in estimate};valid=0
    for _ in range(draws):
        sample=[r for i in rng.integers(0,len(ids),len(ids)) for r in groups[ids[i]]]
        try:v=metric(test,sample,control)
        except Blocked:continue
        if set(v)!=set(estimate) or any(not np.isfinite(x) for x in v.values()):continue
        valid+=1
        for k in samples:samples[k].append(v[k])
    if valid<.95*draws:raise Blocked('more than 5% undefined bootstrap replicates; insufficient data')
    return {k:{'estimate':v,'ci95':[float(x) for x in np.percentile(samples[k],[2.5,97.5])],
               'bootstrap_valid':valid,'bootstrap_requested':draws} for k,v in estimate.items()}


def validate(test,rs,synthetic=False):
    if not rs:raise Blocked('no annotated prediction records')
    seen=set();membership={}
    for r in rs:
        if r['record_id'] in seen:raise Blocked('duplicate evaluation record')
        seen.add(r['record_id'])
        if r.get('unit_kind')!=UNITS[test]:raise Blocked('wrong bootstrap unit kind')
        for qid in r.get('question_ids',[]):
            if qid in membership and membership[qid]!=r['unit_id']:raise Blocked('shared question split across resampling units')
            membership[qid]=r['unit_id']
        if not r.get('unit_id') or not r.get('question_ids'):raise Blocked('resampling unit and question IDs required')
        if synthetic and r.get('dataset_kind')!='synthetic':raise Blocked('synthetic command refuses real records')
        if date(r['posed_at'])<date('2025-07-01'):raise Blocked('not in heldout publication window')
        if date(r['available_at'])>date(r['posed_at']):raise Blocked('question version unavailable at posing time')
        for inp in r.get('input_versions',[]):
            if date(inp['published'])>=date(r['posed_at']) or date(inp['available_at'])>date(r['posed_at']):raise Blocked('future input leakage')
        if date(r['model_trained_until'])>=date('2024-01-01'):raise Blocked('model trained after 2023')
        if r['selected_on']!='2024-validation-only':raise Blocked('unfrozen model selection')
        if not r.get('provenance'):raise Blocked('source provenance missing')
        if set(r['predictions'])!=set(CONTROLS):raise Blocked('all four controls required')
        c=r['control_evidence']
        if not c['original_inputs'] or c['empty_inputs']!=[] or not c['shuffled_inputs'] or set(c['original_inputs'])==set(c['shuffled_inputs']) or not c['same_topic_verified'] or not c['topic_source']:raise Blocked('invalid or unverified controls')
        if test in ('I1','T1') and not r.get('normalization_provenance'):raise Blocked('frozen coordinate normalization required')
        if test in ('I3','H1') and (not r.get('length_matched') or abs(r['tokens_a']-r['tokens_b'])>max(1,.05*max(r['tokens_a'],r['tokens_b']))):raise Blocked('length matching exceeds 5% or one token')
        if test in ('S1','I3','H1','H3','O1','O2'):
            e=r.get('label_evidence',{})
            if not e.get('source') or not e.get('text') or hashlib.sha256(e['text'].encode()).hexdigest()!=e.get('sha256'):raise Blocked('genuine label evidence missing or corrupt')
            if date(e['observed_at'])<date(r['posed_at']):raise Blocked('label predates question')
        if test in ('I3','H1') and finite(r['label'])==0:raise Blocked('non-tied ranking label required')
        if test in ('O1','O2') and any(finite(v)==0 for v in r['labels'].values()):raise Blocked('non-tied outcomes required')
        if test=='S1':
            if type(r.get('label')) is not bool or any(type(r['predictions'][c].get(k)) is not bool for c in CONTROLS for k in ('decision','B-Q')):raise Blocked('identity labels and decisions must be genuine booleans')
        if test=='A1' and any(set(r['predictions'][c].get('scores',{}))!={'Y','density','N','custom'} for c in CONTROLS):raise Blocked('report all four novelty coordinates')
        if test=='H3' and not r.get('ceiling_evidence'):raise Blocked('independent ceiling evidence missing')
        if test=='O1' and not r.get('same_topic_verified'):raise Blocked('within-topic pairs required')
        if test=='O2':
            if len(set(r['seed_ids_a'])&set(r['seed_ids_b']))<3 or set(r['seed_ids_a'])!=set(r['seed_ids_b']):raise Blocked('same seed-input group required')
            if abs((date(r['paper_a_date'])-date(r['paper_b_date'])).days)>365:raise Blocked('same-input pair exceeds one year')
        if test=='T1' and (r['year_Y']!=2023 or r['model_Y_minus_1_until'][:4]!='2022'):raise Blocked('T1 requires frozen 2022 versus 2023 fits')
    if test=='S1' and {r['task'] for r in rs}!={'near_miss','minimal_paraphrase'}:raise Blocked('both identity subtasks required')
    if test in ('S1','A1'):
        field='task' if test=='S1' else 'axiom'
        required={'near_miss','minimal_paraphrase'} if test=='S1' else {'partial_coverage','concentration'}
        for unit in {r['unit_id'] for r in rs}:
            if not required<={r[field] for r in rs if r['unit_id']==unit}:raise Blocked('all paired edits/manipulations must remain within each focal unit')
    if test=='A1' and not {'partial_coverage','concentration'}<={r['axiom'] for r in rs}:raise Blocked('both primary E2 axioms required')


def evaluate(test,rs,*,synthetic=False,draws=DRAWS):
    base={'schema':'M-core-result-v1','test':test,'dataset_kind':'synthetic' if synthetic else 'real',
          'heldout_evaluated':False,'seed':SEED,'bootstrap_draws':draws,'margin':MARGIN}
    if not synthetic:return dict(base,status='BLOCKED',reason='Real execution disabled pending committed preregistration, eligible annotated cohort and explicit authorization.')
    try:
        validate(test,rs,synthetic=True)
        controls={c:bootstrap(test,rs,c,draws) for c in CONTROLS}
        primary=controls['original']
        if test=='T1':passed=all(v['ci95'][1]<=MARGIN for v in primary.values())
        elif test=='A1':passed=any(all(primary.get(k+':'+a,{}).get('ci95',[0])[0]>=.8 for a in ('partial_coverage','concentration')) for k in {x.split(':')[0] for x in primary})
        else:
            keys=([k for k in primary if k=='system_demeaned_improvement'] if test=='H1' else ['spearman_improvement'] if test=='H3' else list(primary))
            passed=all(primary[k]['ci95'][0]>MARGIN for k in keys)
        return dict(base,status='SYNTHETIC_ONLY',pass_criteria_met=passed,records=len(rs),resampling_units=len({r['unit_id'] for r in rs}),controls=controls)
    except (Blocked,KeyError,TypeError,ValueError) as e:return dict(base,status='BLOCKED',reason=str(e))


def main():
    p=argparse.ArgumentParser();p.add_argument('test',choices=TESTS);p.add_argument('--records');p.add_argument('--out',required=True);p.add_argument('--synthetic',action='store_true');a=p.parse_args()
    # Real mode deliberately does not even open a records file.
    rs=[json.loads(l) for l in Path(a.records).read_text().splitlines() if l.strip()] if a.synthetic and a.records else []
    result=evaluate(a.test,rs,synthetic=a.synthetic)
    with Path(a.out).open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps({'test':a.test,'status':result['status'],'output':a.out}))
if __name__=='__main__':main()
