"""Preregistered bounded CPU baseline evaluation; no learned model inference."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import numpy as np
from diversity import diversity,LexicalBaseline,using_backend,FACETS
from known_groups import validate_pair,dependency_components

ROOT=Path(__file__).resolve().parent
MEASURES=('mean_pairwise_cosine_distance','vendi','distinct_question_count','class_entropy','quality_diversity_count')+tuple('facet_'+f for f in FACETS)
TOL=1e-8
SEED=20261113


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rows(path):return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]
def metrics(r):
    return {**{m:r[m] for m in MEASURES[:5]},**{'facet_'+f:r['facet_dispersion'][f] for f in FACETS}}


def pass_rule(axiom,m,base,new):
    if new is None or not np.isfinite(new):return False
    if axiom=='paraphrase':return abs(new-base)<=TOL
    if axiom=='facet_edit':
        return abs(new-base-1)<=TOL if m in ('distinct_question_count','quality_diversity_count') else new>base+TOL
    if axiom=='clone':
        if m in ('distinct_question_count','quality_diversity_count','vendi'):return new<=2+TOL
        if m=='class_entropy':return new<=np.log(2)+TOL
        return new<=base+TOL
    if axiom in ('vague','vague_length_matched'):return new<base-TOL
    raise ValueError('unknown axiom')


def bootstrap_cluster(values,clusters,replicates=10000):
    """Resample topic/dependency clusters, keeping all linked sets paired."""
    groups={}
    for v,c in zip(values,clusters):groups.setdefault(c,[]).append(float(v))
    if len(groups)<2:return None
    arrays=list(groups.values());sums=np.array([sum(a) for a in arrays]);sizes=np.array([len(a) for a in arrays])
    rng=np.random.default_rng(SEED);estimates=[]
    for start in range(0,replicates,250):
        ix=rng.integers(0,len(arrays),(min(250,replicates-start),len(arrays)))
        estimates.extend(sums[ix].sum(1)/sizes[ix].sum(1))
    return np.percentile(estimates,[2.5,97.5]).tolist()


def commit_gate(manifest):
    for rel,h in manifest['committed_sha256'].items():
        data=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT.parent)
        if hashlib.sha256(data).hexdigest()!=h or sha(ROOT.parent/rel)!=h:raise ValueError('preregistration/code/data not committed unchanged')
    protocol=subprocess.check_output(['git','show','HEAD:E5/PREREG.md'],cwd=ROOT.parent)
    if hashlib.sha256(protocol).hexdigest()!=sha(ROOT/'PREREG.md'):raise ValueError('protocol changed')
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip()


def evaluate(output,manifest_path=ROOT/'manifest_v1.json'):
    manifest=json.loads(Path(manifest_path).read_text());commit=commit_gate(manifest)
    # The manifest itself must also be committed before actual evaluations.
    data=subprocess.check_output(['git','show','HEAD:E5/manifest_v1.json'],cwd=ROOT.parent)
    if hashlib.sha256(data).hexdigest()!=sha(manifest_path):raise ValueError('uncommitted manifest')
    output=Path(output)
    if output.exists():raise FileExistsError('never overwrite a previous run')
    sets=rows(ROOT/'data/axiom_sets_v1.jsonl')
    if len(sets)!=200 or len({r['id'] for r in sets})!=200:raise ValueError('exact frozen 200 required')
    backend=LexicalBaseline();results=[];facet_rows=[];control_rows=[]
    with using_backend(backend):
        for row in sets:
            if len(row['base'])!=5:raise ValueError('five base questions required')
            scored={name:diversity(row[name]) for name in ('base','paraphrase_added','facet_edit_added','clone','vague','vague_length_matched','decoy')}
            values={name:metrics(v) for name,v in scored.items()};base=values['base']
            passes={}
            for axiom,condition in [('paraphrase','paraphrase_added'),('facet_edit','facet_edit_added'),('clone','clone'),('vague','vague'),('vague_length_matched','vague_length_matched')]:
                passes[axiom]={m:pass_rule(axiom,m,base[m],values[condition][m]) for m in MEASURES}
            anchor=backend.facets(row['base'][0]);para=backend.facets(row['paraphrase']);edit=backend.facets(row['facet_edit'])
            para_stable={f:anchor[f] is not None and para[f] is not None and anchor[f]==para[f] for f in FACETS}
            edited_moves={f:anchor[f] is not None and edit[f] is not None and anchor[f]!=edit[f] for f in FACETS}
            facet_rows.append({'id':row['id'],'topic_family':row['topic_family'],'intended_edit':row['edited_facet'],
                'paraphrase_stable':para_stable,'edit_moves':edited_moves,
                'edit_locality_pass':edited_moves[row['edited_facet']] and all(not edited_moves[f] for f in FACETS if f!=row['edited_facet'])})
            shuffled=metrics(diversity(list(reversed(row['base']))));empty=metrics(diversity([]))
            control_rows.append({'id':row['id'],'topic_family':row['topic_family'],
                'question_order_invariant':all(abs(shuffled[m]-base[m])<=TOL for m in MEASURES),
                'empty_question_set':empty,'decoy_minus_base':{m:values['decoy'][m]-base[m] for m in MEASURES}})
            length_ratio=len(re.findall(r'\w+',row['paraphrase']))/len(re.findall(r'\w+',row['base'][0]))
            overlap=len(set(row['base'][0].lower().split())&set(row['paraphrase'].lower().split()))/len(set(row['base'][0].lower().split()))
            results.append({'id':row['id'],'topic_family':row['topic_family'],'metrics':values,'passes':passes,
                'paraphrase_length_ratio':length_ratio,'paraphrase_source_unique_word_retention':overlap})
    clusters=[r['topic_family'] for r in results];rates=[]
    for axiom in ('paraphrase','facet_edit','clone','vague','vague_length_matched'):
        for m in MEASURES:
            v=[r['passes'][axiom][m] for r in results]
            rates.append({'axiom':axiom,'measure':m,'passes':sum(v),'valid':len(v),'rate':float(np.mean(v)),
                          'ci95':bootstrap_cluster(v,clusters)})
    stability=[]
    for f in FACETS:
        v=[r['paraphrase_stable'][f] for r in facet_rows]
        stability.append({'facet':f,'stable':sum(v),'valid':len(v),'rate':float(np.mean(v)),'ci95':bootstrap_cluster(v,clusters)})
    edit_by_facet=[]
    for f in FACETS:
        selected=[r for r in facet_rows if r['intended_edit']==f]
        v=[r['edit_moves'][f] and all(not r['edit_moves'][other] for other in FACETS if other!=f) for r in selected]
        edit_by_facet.append({'facet':f,'local_moves':sum(v),'valid':len(v),'rate':float(np.mean(v)),
            'ci95':bootstrap_cluster(v,[r['topic_family'] for r in selected])})
    local=[r['edit_locality_pass'] for r in facet_rows]
    order=[r['question_order_invariant'] for r in control_rows]
    summary={'status':'controlled_development_baseline_not_semantic_model_validation',
      'preregistration_commit':commit,'backend':backend.name,'semantic_cross_encoder':False,'sets':200,'topic_clusters':len(set(clusters)),
      'scored_set_conditions':1400,'primary_axioms':['paraphrase','facet_edit','clone','vague'],
      'rates':rates,'facet_paraphrase_stability':stability,'edit_by_intended_facet':edit_by_facet,
      'facet_edit_locality':{'passes':sum(local),'valid':200,'rate':float(np.mean(local)),'ci95':bootstrap_cluster(local,clusters)},
      'question_order_control':{'passes':sum(order),'valid':200,'rate':float(np.mean(order)),'ci95':bootstrap_cluster(order,clusters)},
      'paraphrase_length_matched_count':sum(.9<=r['paraphrase_length_ratio']<=1.1 for r in results),
      'paraphrases_with_less_than_75_percent_source_word_retention':sum(r['paraphrase_source_unique_word_retention']<.75 for r in results),
      'bootstrap':{'draws':10000,'seed':SEED,'unit':'domain/topic family; all ten related sets retained together'},
      'known_groups_evaluated':0,'new_model_inference':False,
      'limitations':['Procedural template labels encode design intent, not independent human semantic validation.',
       'Hash embeddings and regex facets are explicit baselines, not a same-question cross-encoder or GENIE reproduction.',
       'Quality gates operationalize question form, complete facets and concrete language, not scientific soundness.',
       'Raw distance/facet axioms use response surrogates where distinct-question units do not apply.',
       'Class entropy weights multiplicity; adding a true paraphrase can change it even with perfect classes.',
       'Missing facet answers fail the associated axiom; they are never silently imputed.',
       'Question-order/empty-question controls do not replace empty/shuffled seed and decoy controls for known groups.',
       'No heldout evaluation or real/generated separation claim. Real citation groups and semantic-model experiments remain required.']}
    for path,h in manifest['committed_sha256'].items():
        if sha(ROOT.parent/path)!=h:raise ValueError('frozen source changed during run')
    output.mkdir(parents=True,exist_ok=False)
    for name,obj in [('results.jsonl',results),('facet_reliability.jsonl',facet_rows),('controls.jsonl',control_rows)]:
        with (output/name).open('x') as f:
            for r in obj:f.write(json.dumps(r,allow_nan=False)+'\n')
    with (output/'summary.json').open('x') as f:json.dump(summary,f,indent=2,allow_nan=False);f.write('\n')
    return summary


def compare_known_groups(groups,backend):
    """Executable paired comparison once real, provenance-complete groups exist."""
    for g in groups:validate_pair(g)
    if not groups:raise ValueError('no real citation groups supplied')
    components=dependency_components(groups);differences=[]
    with using_backend(backend):
        for g in groups:
            real=metrics(diversity(g['real_questions']));generated=metrics(diversity(g['generated_questions']))
            differences.append({'id':g['id'],'difference_generated_minus_real':{m:generated[m]-real[m] if generated[m] is not None and real[m] is not None else None for m in MEASURES}})
    stats=[]
    for m in MEASURES:
        valid=[(r['difference_generated_minus_real'][m],c) for r,c in zip(differences,components) if r['difference_generated_minus_real'][m] is not None]
        if valid:
            values,clusters=zip(*valid)
            stats.append({'measure':m,'mean_generated_minus_real':float(np.mean(values)),
                         'ci95':bootstrap_cluster(values,clusters),'groups':len(valid),'dependency_components':len(set(clusters))})
    return {'differences':differences,'summary':stats,'interpretation':'association only; source, author, date, length and selection confounds remain'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=evaluate(a.output)
    print(json.dumps({'sets':result['sets'],'backend':result['backend'],'facet_edit_locality':result['facet_edit_locality']}))
