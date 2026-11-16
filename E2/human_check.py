"""Offline Task 3 analysis. Never imports novelty models or calls a service.

Frozen embeddings must be abstract-only SPECTER2 proximity CLS (512 tokens),
with IDs aligned explicitly. Callers must verify provenance before evaluation.
"""
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np

MEASURES = ('Y', 'N', 'yours', 'density')  # all higher = more novel
ALPHAS = (0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000)
SEED = 20261113

def title_key(s):
    return ''.join(c for c in unicodedata.normalize('NFKC', s).casefold() if c.isalnum())

def value(v):
    return v.get('value') if isinstance(v, dict) else v

def normalize(row):
    out = dict(row)
    meta = row.get('metadata') or {}
    if isinstance(meta, str): meta = json.loads(meta)
    for k in ('title', 'forum_id', 'rating', 'contribution'):
        if k in meta and k in row and meta[k] != row[k]:
            raise ValueError('conflicting nested metadata: ' + k)
        out[k] = meta.get(k, row.get(k))
    if out.get('label') not in ('POSITIVE', 'NEGATIVE'):
        raise ValueError('invalid label')
    if not out.get('title') or not out.get('idea'):
        raise ValueError('missing title or abstract/idea')
    for k in ('rating', 'contribution'):
        if not np.isfinite(float(out[k])): raise ValueError('invalid ' + k)
    return out

def resolve(rows, papers):
    """Only unique exact normalized titles; ambiguous titles remain unresolved."""
    index = defaultdict(set)
    for p in papers:
        index[title_key(value(p['content']['title']))].add(p['id'])
    result = []
    for r in rows:
        ids = index.get(title_key(r['title']), set())
        result.append({'id': r['id'], 'title': r['title'],
                       'forum_id': r.get('forum_id') or (next(iter(ids)) if len(ids)==1 else None),
                       'mapping_source': 'benchmark' if r.get('forum_id') else 'unique_exact_title' if len(ids)==1 else 'unresolved'})
    return result

def jsonl(path):
    with Path(path).open() as handle:
        for line in handle:
            if line.strip(): yield json.loads(line)

def historical(root, benchmark):
    test_ids = {r['forum_id'] for r in benchmark if r.get('forum_id')}
    test_titles = {title_key(r['title']) for r in benchmark}
    conservative = ('hotpate', 'conjuringsemanticsimilarity', 'counterfactualtechniquesforenhancingcustomerretention')
    eligible, excluded = [], []
    for year in range(2022, 2026):
        folder = Path(root)/f'iclr_{year}'
        ratings = defaultdict(dict)
        for r in jsonl(folder/'reviews.jsonl'):
            invitations = (r.get('invitations') or []) + [r.get('invitation') or '']
            if not any('Official_Review' in s for s in invitations): continue
            v = value(r['content'].get('rating', r['content'].get('recommendation')))
            m = re.match(r'^\s*(\d+(?:\.\d+)?)\s*(?::|$)', str(v))
            if m and float(m[1]) in (1,3,5,6,8,10):
                ratings[r['forum']][r['id']] = float(m[1])
        seen = set()
        for p in jsonl(folder/'papers.jsonl'):
            pid = p['id']; c = p['content']
            if pid in seen: raise ValueError('duplicate historical forum')
            seen.add(pid)
            title = value(c.get('title', '')); abstract = value(c.get('abstract', ''))
            k = title_key(title)
            if pid in test_ids or k in test_titles or any(s in k for s in conservative):
                excluded.append({'forum_id':pid,'year':year,'title':title}); continue
            rs = list(ratings[pid].values())
            if abstract and len(rs)>=2:
                eligible.append({'forum_id':pid,'year':year,'title':title,'abstract':abstract,
                                 'mean_rating':float(np.mean(rs)), 'review_count':len(rs)})
    return eligible, excluded

def auc(labels, scores):
    y = np.asarray(labels); s = np.asarray(scores, float)
    if y.ndim!=1 or s.shape!=y.shape or not np.isfinite(s).all() or set(y)!={0,1}:
        raise ValueError('finite aligned scores and both binary classes required')
    order=np.argsort(s, kind='stable'); ranks=np.empty(len(s),float)
    i=0
    while i<len(s):
        j=i+1
        while j<len(s) and s[order[j]]==s[order[i]]: j+=1
        ranks[order[i:j]]=(i+1+j)/2; i=j
    n=y.sum(); return float((ranks[y==1].sum()-n*(n+1)/2)/(n*(len(y)-n)))

def comparison(labels, scores, replicates=10000, seed=SEED):
    """Paired class-stratified percentile intervals, with fixed score orientation."""
    y=np.asarray(labels); scores={k:np.asarray(v,float) for k,v in scores.items()}
    if 'quality' not in scores: raise ValueError('quality baseline missing')
    point={k:auc(y,v) for k,v in scores.items()}
    rng=np.random.default_rng(seed); pos=np.flatnonzero(y==1); neg=np.flatnonzero(y==0)
    boot={k:[] for k in scores}
    for _ in range(replicates):
        ix=np.r_[rng.choice(pos,len(pos)),rng.choice(neg,len(neg))]
        for k,v in scores.items(): boot[k].append(auc(y[ix],v[ix]))
    interval=lambda v: np.percentile(v,[2.5,97.5]).tolist()
    return {'seed':seed,'replicates':replicates,'n':len(y),'measures':{
        k:{'auroc':point[k],'ci95':interval(boot[k]),
           **({'minus_quality':point[k]-point['quality'],
               'difference_ci95':interval(np.asarray(boot[k])-boot['quality'])} if k!='quality' else {})}
        for k in scores}}

def ridge_predict(train_x, target, test_x, alpha):
    """Training-only standardization and intercept; no benchmark target input."""
    x=np.asarray(train_x,float); t=np.asarray(test_x,float); y=np.asarray(target,float)
    if x.ndim!=2 or t.ndim!=2 or x.shape[1]!=t.shape[1] or len(y)!=len(x) or alpha<=0:
        raise ValueError('invalid ridge inputs')
    if not all(np.isfinite(a).all() for a in (x,t,y)): raise ValueError('nonfinite ridge input')
    mean=x.mean(0); sd=x.std(0); sd[sd==0]=1
    z=(x-mean)/sd; yt=y-y.mean()
    # einsum avoids the documented local large-matmul runtime warning.
    gram=np.einsum('ni,nj->ij',z,z); gram.flat[::len(gram)+1]+=alpha
    coef=np.linalg.solve(gram,np.einsum('ni,n->i',z,yt))
    return np.einsum('ni,i->n',(t-mean)/sd,coef)+y.mean()

def ridge_path(train_x,target,valid_x,alphas=ALPHAS):
    """One train-fold scaling/Gram eigendecomposition for the full alpha path."""
    x=np.asarray(train_x,float);v=np.asarray(valid_x,float);y=np.asarray(target,float)
    if x.ndim!=2 or v.ndim!=2 or x.shape[1]!=v.shape[1] or y.shape!=(len(x),) or not len(x):
        raise ValueError('invalid chronological ridge inputs')
    if not all(np.isfinite(a).all() for a in (x,v,y)) or any(a<=0 for a in alphas):
        raise ValueError('invalid chronological ridge values')
    mean=x.mean(0);sd=x.std(0);sd[sd==0]=1;z=(x-mean)/sd
    gram=np.einsum('ni,nj->ij',z,z);rhs=np.einsum('ni,n->i',z,y-y.mean())
    eigenvalues,eigenvectors=np.linalg.eigh(gram)
    eigenvalues=np.maximum(eigenvalues,0.)
    rotated_rhs=np.einsum('ij,i->j',eigenvectors,rhs)
    projection=np.einsum('ni,ij->nj',(v-mean)/sd,eigenvectors)
    return {a:np.einsum('ni,i->n',projection,rotated_rhs/(eigenvalues+a))+y.mean() for a in alphas}


def quality_scores(records, embeddings, test_ids, test_embeddings):
    ids=[r['forum_id'] for r in records]
    if len(set(ids))!=len(ids) or set(ids)&set(test_ids): raise ValueError('duplicate or test leakage')
    if embeddings.shape[0]!=len(records) or test_embeddings.shape[0]!=len(test_ids):
        raise ValueError('embedding alignment error')
    years=np.array([r['year'] for r in records]);targets=np.array([r['mean_rating'] for r in records])
    if not set(years)<={2022,2023,2024,2025}:raise ValueError('foreign historical cohort')
    sums={a:0. for a in ALPHAS};n=0
    for year in (2023,2024,2025):
        train=years<year;valid=years==year
        if not train.any() or not valid.any():raise ValueError('missing chronological fold')
        predictions=ridge_path(embeddings[train],targets[train],embeddings[valid])
        for a,pred in predictions.items():sums[a]+=float(((pred-targets[valid])**2).sum())
        n+=int(valid.sum())
    losses={a:sums[a]/n for a in ALPHAS};alpha=min(ALPHAS,key=lambda a:losses[a])
    final=ridge_path(embeddings,targets,test_embeddings,(alpha,))[alpha]
    return final,{'alpha':alpha,'validation_mse':losses,'selection':'pooled out-of-time MSE; train-fold preprocessing only'}

def eligibility(row, cutoff):
    """No cohort-derived dates; compare only verified item-level publication times."""
    s=row.get('published')
    if not s: return 'unknown_missing_publication_date'
    parse=lambda x:datetime.fromisoformat(x.replace('Z','+00:00'))
    a,b=parse(s),parse(cutoff)
    if a.tzinfo is None or b.tzinfo is None: raise ValueError('timezone required')
    return 'eligible' if a>b else 'ineligible'
