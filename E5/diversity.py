"""E5 diversity API. Default is an explicit CPU lexical/rule baseline.
A strict cache-only semantic backend supports real embeddings, a calibrated
same-question cross-encoder, facet answers and quality judgments. No inference.
"""
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[_k]='1'
import contextlib
import contextvars
import hashlib
import json
import math
import re
from pathlib import Path
import numpy as np

FACETS=('purpose','mechanism','evaluation','domain')
SAME=.65
DISTINCT=.35
GATES=('question_form','complete_facets','concrete_language')


def digest(text):return hashlib.sha256(text.encode()).hexdigest()

def hashed_vectors(texts,dimension=512):
    """Fixed nonnegative unigram/bigram hashing; no fitting on evaluation data."""
    result=np.zeros((len(texts),dimension),dtype=np.float64)
    for i,text in enumerate(texts):
        words=re.findall(r'[a-z0-9]+',text.casefold())
        tokens=words+[' '.join(words[j:j+2]) for j in range(len(words)-1)]
        for token in tokens:result[i,int(hashlib.blake2b(token.encode(),digest_size=8).hexdigest(),16)%dimension]+=1
        norm=np.linalg.norm(result[i])
        if norm:result[i]/=norm
    return result


# Controlled-language extractor. It is not presented as an LLM facet judge.
_PATTERNS=[
 r'For (?P<domain>.+?), does (?P<mechanism>.+?) help (?P<purpose>.+?), measured by (?P<evaluation>.+?)\?',
 r'In (?P<domain>.+?), can (?P<purpose>.+?) be achieved through (?P<mechanism>.+?), assessed using (?P<evaluation>.+?)\?',
 r'Using (?P<evaluation>.+?) as the criterion, does (?P<mechanism>.+?) help (?P<purpose>.+?) in (?P<domain>.+?)\?',
 r'When studying (?P<domain>.+?), what effect does (?P<mechanism>.+?) have on efforts to (?P<purpose>.+?), with (?P<evaluation>.+?) as the measure\?',
 r'Can (?P<mechanism>.+?) support attempts to (?P<purpose>.+?) for (?P<domain>.+?), if success is judged by (?P<evaluation>.+?)\?',
 r'Under an evaluation based on (?P<evaluation>.+?), how does (?P<mechanism>.+?) influence the aim to (?P<purpose>.+?) in (?P<domain>.+?)\?']


def extract_facets(text):
    for pattern in _PATTERNS:
        match=re.fullmatch(pattern,text.strip(),re.I)
        if match:return {k:match[k].casefold().strip() for k in FACETS}
    return {k:None for k in FACETS}


class LexicalBaseline:
    name='fixed_hash_lexical_and_controlled_regex_baseline'
    semantic_cross_encoder=False
    def embeddings(self,texts):return hashed_vectors(texts)
    def pair(self,a,b):
        v=hashed_vectors([a,b]);s=float(v[0]@v[1]);return s,s
    def facets(self,text):return extract_facets(text)
    def quality(self,text):
        words=re.findall(r'\w+',text)
        return {'question_form':text.strip().endswith('?') and 8<=len(words)<=100,
          'complete_facets':all(self.facets(text).values()),
          'concrete_language':not bool(re.search(r'\b(things|various|something|stuff|generally|unspecified)\b',text,re.I))}


class CachedSemanticBackend:
    """Exact text-bound artifacts only; a relevance model is not an identity judge.
    Cache schema: metadata, texts[sha]={text,embedding,facets,quality},
    pairs[sorted_sha_join]={forward,reverse}. Scores must be calibrated to [0,1].
    """
    def __init__(self,path):
        self.data=json.loads(Path(path).read_text());m=self.data['metadata']
        if m.get('kind')!='same_question_cross_encoder' or m.get('identity_calibration_verified') is not True or not m.get('calibration_source'):
            raise ValueError('validated same-question cross-encoder metadata required')
        for key in ('embedding_model','embedding_revision','cross_encoder_model','cross_encoder_revision','facet_extractor','quality_judge'):
            if not m.get(key):raise ValueError('missing semantic model provenance: '+key)
        self.name=m['cross_encoder_model'];self.semantic_cross_encoder=True
    def row(self,text):
        r=self.data['texts'].get(digest(text))
        if r is None:raise KeyError('missing exact semantic cache text: '+digest(text))
        if r['text']!=text:raise ValueError('semantic cache text/hash mismatch')
        return r
    def embeddings(self,texts):return np.asarray([self.row(t)['embedding'] for t in texts],dtype=float)
    def pair(self,a,b):
        self.row(a);self.row(b)
        if a==b:return 1.,1.
        key=':'.join(sorted([digest(a),digest(b)]));r=self.data['pairs'].get(key)
        if r is None:raise KeyError('missing bidirectional identity cache pair')
        x,y=float(r['forward']),float(r['reverse'])
        if not 0<=x<=1 or not 0<=y<=1:raise ValueError('identity scores not probabilities')
        return x,y
    def facets(self,text):
        r=self.row(text)['facets']
        if set(r)!=set(FACETS) or any(v is not None and (not isinstance(v,str) or not v.strip()) for v in r.values()):
            raise ValueError('invalid cached facet answers')
        return r
    def quality(self,text):
        r=self.row(text)['quality']
        if any(type(r.get(g)) is not bool for g in GATES):raise ValueError('explicit frozen quality gates required')
        return r


_BACKEND=contextvars.ContextVar('e5_backend',default=None)
@contextlib.contextmanager
def using_backend(backend):
    token=_BACKEND.set(backend)
    try:yield
    finally:_BACKEND.reset(token)


def pairwise_cosine(v):
    v=np.asarray(v,dtype=float)
    if v.ndim!=2 or not np.isfinite(v).all():raise ValueError('invalid embeddings')
    norms=np.linalg.norm(v,axis=1)
    if np.any(norms<=0):raise ValueError('zero embedding')
    v=v/norms[:,None];return np.clip(v@v.T,-1,1)

def mean_distance(kernel):
    n=len(kernel)
    return float(np.mean(1-kernel[np.triu_indices(n,1)])) if n>1 else 0.

def vendi(kernel):
    n=len(kernel)
    if not n:return 0.
    if not np.allclose(kernel,kernel.T,atol=1e-10) or not np.allclose(np.diag(kernel),1):raise ValueError('invalid Vendi kernel')
    eigen=np.linalg.eigvalsh(kernel/n)
    if eigen.min() < -1e-8:raise ValueError('Vendi kernel not positive semidefinite')
    eigen=np.maximum(eigen,0);eigen/=eigen.sum();p=eigen[eigen>0]
    return float(np.exp(-np.sum(p*np.log(p))))


def clique_partition(same):
    """Exact minimum clique partition; no unsafe connected-component chaining.
    Small E5 sets only. Stable lexical input order makes ties reproducible.
    """
    n=len(same);best=[tuple([i]) for i in range(n)]
    def search(i,groups):
        nonlocal best
        if i==n:
            if len(groups)<len(best):best=[tuple(g) for g in groups]
            return
        if len(groups)>=len(best):return
        for group in groups:
            if all(same[i,j] for j in group):
                group.append(i);search(i+1,groups);group.pop()
        groups.append([i]);search(i+1,groups);groups.pop()
    search(0,[])
    return best


def maximum_distinct_subset(distinct,eligible):
    """Exact maximum clique in confident-distinct graph after quality gates."""
    eligible=list(eligible);best=[]
    def search(chosen,candidates):
        nonlocal best
        if len(chosen)+len(candidates)<=len(best):return
        if not candidates:
            if len(chosen)>len(best):best=list(chosen)
            return
        while candidates:
            if len(chosen)+len(candidates)<=len(best):return
            i=candidates.pop(0)
            next_candidates=[j for j in candidates if distinct[i,j]]
            if not next_candidates:
                if len(chosen)+1>len(best):best=chosen+[i]
            else:search(chosen+[i],next_candidates)
    search([],eligible)
    return best


def diversity(rqs: list[str], facets: bool = True) -> dict:
    if not isinstance(rqs,list) or any(not isinstance(q,str) or not q.strip() for q in rqs):raise ValueError('nonempty question strings required')
    if len(rqs)>12:raise ValueError('exact E5 subset solver bounded to 12 questions')
    backend=_BACKEND.get() or LexicalBaseline()
    # Order-invariant representative choice, retain multiplicities for class entropy.
    texts=sorted(q.strip() for q in rqs);n=len(texts)
    kernel=pairwise_cosine(backend.embeddings(texts)) if n else np.empty((0,0))
    same=np.eye(n,dtype=bool);different=np.zeros((n,n),dtype=bool);uncertain=0
    for i in range(n):
        for j in range(i+1,n):
            forward,reverse=backend.pair(texts[i],texts[j])
            same[i,j]=same[j,i]=min(forward,reverse)>=SAME
            different[i,j]=different[j,i]=max(forward,reverse)<=DISTINCT
            if not same[i,j] and not different[i,j]:uncertain+=1
    classes=clique_partition(same)
    counts=np.asarray([len(c) for c in classes],dtype=float)
    entropy=float(-np.sum(counts/n*np.log(counts/n))) if n else 0.
    violations=sum(same[i,j] and same[j,k] and not same[i,k] for i in range(n) for j in range(n) for k in range(i+1,n) if j not in (i,k))
    answers=[backend.facets(q) for q in texts]
    quality=[backend.quality(q) for q in texts]
    eligible=[i for i,g in enumerate(quality) if all(g.get(k) is True for k in GATES)]
    selected=maximum_distinct_subset(different,eligible)
    result={'n':n,'backend':backend.name,'semantic_cross_encoder':backend.semantic_cross_encoder,
      'mean_pairwise_cosine_distance':mean_distance(kernel),'vendi':vendi(kernel),
      'distinct_question_count':len(classes),'class_entropy':entropy,
      'class_sizes':[len(c) for c in classes],'equivalence_status':'consistent' if not violations else 'nontransitive_pair_judgments_clique_partition_approximation',
      'nontransitive_chains':int(violations),'uncertain_pairs':uncertain,
      'quality_diversity_count':len(selected),'quality_passing_questions':len(eligible),
      'quality_gates':list(GATES),'quality_scope':'operational clarity/specificity; not scientific soundness certification'}
    if facets:
        result['facet_answers']=answers;result['facet_dispersion']={};result['facet_missing']={}
        for f in FACETS:
            values=[a[f] for a in answers if a[f] is not None]
            result['facet_missing'][f]=n-len(values)
            result['facet_dispersion'][f]=mean_distance(pairwise_cosine(backend.embeddings(values))) if len(values)>=2 else (0. if values else None)
    return result
