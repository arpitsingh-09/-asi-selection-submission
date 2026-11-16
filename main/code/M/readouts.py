"""Six heads over one Phi snapshot; no retrieval, training or new embeddings."""
import ast
from functools import lru_cache
import hashlib
from pathlib import Path
import re
import numpy as np
from E5.diversity import diversity as e5_diversity,using_backend,mean_distance,pairwise_cosine
from E2.task3_novelty import novelty_scores
from .schema import norm,date
from .baselines import baselines


def cosine(a,b):
    a=np.asarray(a);b=np.asarray(b);den=np.linalg.norm(a)*np.linalg.norm(b)
    return float(np.clip(a@b/den,-1,1)) if den else 0.


def _specificity(q,facets):
    return sum(v is not None for _,v in facets)+len(re.findall(r'\b(only|without|within|under|exactly|at least|at most)\b',q,re.I))


def identity_scope(a,b):
    if a.space_id!=b.space_id or a.feature_schema!=b.feature_schema:raise ValueError('incompatible representations')
    similarity=cosine(a.question_vector,b.question_vector)
    difference=_specificity(b.q,b.facets)-_specificity(a.q,a.facets)
    signed=float(difference/(1+abs(difference)))
    return {'same_question':similarity>=.65,'score':similarity,
        'decision_status':'same_proxy' if similarity>=.65 else ('distinct_proxy' if similarity<=.35 else 'uncertain'),
        'signed_scope':signed,'scope_convention':'positive means first broader; negative first narrower',
        'scope_status':'constraint/facet-count proxy, not a validated semantic scope prediction',
        'shared_space_id':a.space_id}


@lru_cache(maxsize=1)
def _rnd():
    # Reuse E2's pure functions without importing torch/model initialization.
    path=Path(__file__).resolve().parents[1]/'E2/novelty.py';tree=ast.parse(path.read_text())
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('_cosine_distance_matrix','_rnd_score')]
    scope={'np':np,'RND_P':100,'RND_Q':50}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(path),'exec'),scope)
    return scope['_rnd_score']


def novelty(phi):
    q=np.asarray(phi.question_vector,dtype=np.float32);papers=phi.literature
    base={'reference_ids':[p.paper.paper_id for p in papers],'reference_scope':phi.reference_scope,
          'Y':None,'density':None,'N':None,'custom':None,'facets':{},
          'coordinate_questions':{'Y':'How distant is the nearest earlier paper text?',
            'density':'How sparse is the local earlier-paper neighborhood?',
            'N':'How much of the supplied atomic claim set lacks nearby earlier paper text?'},
          'status':'no eligible prior literature' if not papers else 'representation-based coordinates, not proven semantic novelty'}
    if not papers:return base
    r=np.asarray([p.text_vector for p in papers],dtype=np.float64)
    q64=np.asarray(q,dtype=np.float64)
    if r.ndim!=2 or q64.ndim!=1 or r.shape[1]!=q64.shape[0] or not np.isfinite(r).all() or not np.isfinite(q64).all():
        raise ValueError('invalid question/reference embedding inputs')
    # Avoid platform BLAS matmul status warnings on finite, unit-normalized
    # vectors. This computes the same per-reference cosine dot products in
    # float64 without dispatching to the problematic float32 GEMM path.
    dots=np.einsum('ij,j->i',r,q64,optimize=False)
    qnorm=np.linalg.norm(q64);rnorm=np.linalg.norm(r,axis=1)
    if qnorm<=0 or np.any(rnorm<=0):raise ValueError('zero novelty embedding')
    similarities=np.clip(dots/(rnorm*qnorm),-1.0,1.0)
    base['Y']=float(1.0-similarities.max())
    if len(r)>=2:base['density']=_rnd()(q,r)
    if phi.claim_vectors:
        c=np.asarray(phi.claim_vectors,dtype=np.float32)
        if len(r)>=2:
            scores=novelty_scores(q.reshape(1,-1),r,[c],block_size=16)
            base.update(Y=scores['Y'][0],density=scores['density'][0],N=scores['N'][0],custom=scores['yours'][0])
        else:
            base['N']=float(1-np.clip(c@r.T,-1,1).max(axis=1).mean())
            base['custom']=.75*base['Y']+.25*base['N']
    # Facet-to-facet only: absent paper-question facets never become a zero score.
    for f,v in phi.facet_vectors:
        candidates=[]
        for p in papers:
            other=dict(p.facets).get(f)
            if other:
                # These paper facet vectors are not stored in Phi; do not launch
                # an independent encoder or compare question facets to a whole text.
                candidates.append(p.paper.paper_id)
        base['facets'][f]={'score':None,'status':'unavailable: aligned reference facet vectors not yet stored',
                          'reference_questions_with_facet':candidates}
    return base


def groundedness(phi):
    similarities=[(cosine(phi.question_vector,p.text_vector),p) for p in phi.inputs]
    support=[{'paper_id':p.paper.paper_id,'relevance_proxy':s} for s,p in similarities if s>=.15]
    copied=[];answered=[]
    for _,p in similarities:
        if p.paper.question and norm(p.paper.question)==norm(phi.q):copied.append(p.paper.paper_id)
        for evidence in p.paper.answers:
            if evidence.verified and norm(evidence.question)==norm(phi.q) and date(evidence.available_at)<=date(phi.as_of):
                answered.append({'paper_id':p.paper.paper_id,'excerpt':evidence.excerpt,'source_field':evidence.field,
                                 'evidence_available_at':evidence.available_at})
    relevance=float(np.mean([max(0,s) for s,_ in similarities])) if similarities else None
    return {'score':relevance*(0. if copied or answered else 1.) if relevance is not None else None,
        'relevance_score':relevance,'score_definition':'noncopy/nonanswered relevance proxy; annotations are not inferred from cosine',
        'supporting_input_ids':[r['paper_id'] for r in support],'support':support,
        'copied_question_input_ids':copied,'copy_status':'exact question reuse; not a plagiarism inference' if copied else 'not established',
        'already_answered':True if answered else None,'answer_evidence':answered,
        'answer_status':'explicit source-bound verified annotation' if answered else 'unknown; similarity does not prove an answer',
        'input_mode':phi.input_mode,'scope':'relevance proxy is not entailment or scientific support certification'}


def quality(phi,models=None):
    factors={name:{'prediction':None,'status':'untrained; no predictive accuracy claimed'}
             for name in ('peer_review','later_community_use')}
    if models is not None:factors=models.predict(phi)
    return {'factors':factors,'structural_features':dict(phi.structural_quality),
            'status':'separate target factors; proxies are not substituted for outcomes'}


class _PhiBackend:
    name='M.shared-Phi readout (no independent E5 encoding)';semantic_cross_encoder=False
    def __init__(self,snapshots):
        self.snapshots={}
        for s in snapshots:
            if s.q in self.snapshots and (s.facets!=self.snapshots[s.q].facets or s.question_vector!=self.snapshots[s.q].question_vector):
                raise ValueError('same text has inconsistent facet/vector annotations')
            self.snapshots[s.q]=s
        self.vectors={}
        for s in snapshots:
            self.vectors[s.q]=s.question_vector
            for (f,text),(vf,v) in zip(s.facets,s.facet_vectors):
                if text:self.vectors[text]=v
    def embeddings(self,texts):return np.asarray([self.vectors[t] for t in texts])
    def pair(self,a,b):
        score=max(0,cosine(self.snapshots[a].question_vector,self.snapshots[b].question_vector))
        return score,score
    def facets(self,q):return dict(self.snapshots[q].facets)
    def quality(self,q):return dict(self.snapshots[q].structural_quality)


def diversity_readout(snapshots):
    if snapshots:
        if len({s.space_id for s in snapshots})!=1 or len({s.feature_schema for s in snapshots})!=1 or len({s.as_of for s in snapshots})!=1:
            raise ValueError('set diversity requires common representation and as-of date')
    with using_backend(_PhiBackend(snapshots)):
        r=e5_diversity([s.q for s in snapshots])
    r['shared_snapshot_ids']=[s.snapshot_id for s in snapshots]
    r['context_dispersion']=mean_distance(pairwise_cosine(np.asarray([s.vector for s in snapshots]))) if len(snapshots)>1 else 0.
    r['guarantees']='exact combinatorial count under proxy pair judgments; no claim of semantic anti-gaming guarantees'
    return r


def readouts(phi,models=None):
    nearest=None
    if phi.literature:
        p=max(phi.literature,key=lambda p:cosine(phi.question_vector,p.question_vector or p.text_vector))
        similarity=cosine(phi.question_vector,p.question_vector or p.text_vector)
        nearest={'paper_id':p.paper.paper_id,'same_question_proxy':similarity>=.65,'cosine':similarity,
                 'comparison_text_kind':'question' if p.question_vector else 'paper text surrogate'}
    return {'snapshot_id':phi.snapshot_id,'as_of':phi.as_of,'shared_space_id':phi.space_id,
      'I':{'question_signature':hashlib.sha256(norm(phi.q).encode()).hexdigest(),'closest_prior':nearest,
           'scope_interface':'ResearchSpace.compare(phi_a,phi_b); signed broader/narrower proxy'},
      'N':novelty(phi),'G':groundedness(phi),'Q':quality(phi,models),'D':diversity_readout([phi]),
      'T':{'as_of':phi.as_of,'previous_snapshot_id':phi.previous_snapshot_id or None,
           'eligible_reference_ids':[p.paper.paper_id for p in phi.literature],
           'future_information_exposed':False,
           'update_interface':'ResearchSpace.update(snapshot,later_literature,new_t)',
           'historical_snapshot_immutable':True},
      'baselines':baselines(phi),'warnings':list(phi.warnings)}
