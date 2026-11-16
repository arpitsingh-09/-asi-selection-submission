"""Unscored manipulation constructors using supplied, frozen cosine similarities.

No model inference, score evaluation, artifact replacement, or human approval.
Callers must freeze ranking provenance and review paraphrases before evaluation.
Synthetic publication dates are explicit experimental interventions, not real dates.
"""
import hashlib
import math
from datetime import datetime
import numpy as np

def parse(s):
    d=datetime.fromisoformat(s.replace('Z','+00:00'))
    if d.tzinfo is None:raise ValueError('timezone required')
    return d

def select_pools(papers, focal_id, cutoff, similarity, size):
    """Equal-sized near/far and old/new pools, all strictly prior and nonfocal."""
    eligible=[p for p in papers if p['paper_id']!=focal_id and parse(p['published'])<parse(cutoff)]
    if size<2 or len(eligible)<2*size:raise ValueError('insufficient disjoint prior papers')
    if any(p['paper_id'] not in similarity or not math.isfinite(similarity[p['paper_id']]) for p in eligible):
        raise ValueError('missing frozen similarity')
    near=sorted(eligible,key=lambda p:(-similarity[p['paper_id']],p['paper_id']))
    age=sorted(eligible,key=lambda p:(parse(p['published']),p['paper_id']))
    ids=lambda ps:[p['paper_id'] for p in ps]
    return {'near':ids(near[:size]),'far':ids(near[-size:]),'older':ids(age[:size]),'newer':ids(age[-size:])}

def plant_nearest(papers, claims, similarities, percent, focal_id, cutoff):
    """Clone nearest existing papers and append selected claims to those clones.

    similarities shape is (number of claims, number of candidate papers).
    Return replacements and mapping; the caller replaces originals in pool_ids.
    Original source records remain unchanged. Claim selection retains source order.
    """
    if not 4<=len(claims)<=10 or percent not in (25,50,75,100):raise ValueError('claim count/coverage')
    sim=np.asarray(similarities,float)
    if sim.shape!=(len(claims),len(papers)) or not np.isfinite(sim).all():raise ValueError('similarity alignment')
    if len({p['paper_id'] for p in papers})!=len(papers):raise ValueError('duplicate paper')
    eligible=[i for i,p in enumerate(papers) if p['paper_id']!=focal_id and parse(p['published'])<parse(cutoff)]
    if not eligible:raise ValueError('no eligible papers')
    groups={}
    for j in range(math.ceil(len(claims)*percent/100)):
        i=min(eligible,key=lambda i:(-sim[j,i],papers[i]['paper_id']))
        groups.setdefault(i,[]).append(claims[j])
    replacements=[]; mapping={}
    for i,planted in groups.items():
        p=dict(papers[i]);source=p['paper_id']
        digest=hashlib.sha256((source+'|'+str(percent)+'|'+ '\n'.join(planted)).encode()).hexdigest()[:24]
        p.update(paper_id='e2nearest:'+digest,abstract=p['abstract']+'\n\n'+'\n'.join(planted),
                 synthetic_manipulation=True,source_paper_id=source,synthetic_condition=f'nearest_coverage_{percent}')
        replacements.append(p);mapping[source]=p['paper_id']
    return replacements,mapping

def paraphrased_copy(paper, paraphrase, provenance):
    if not paraphrase.strip() or paraphrase.strip()==paper['abstract'].strip():raise ValueError('nontrivial paraphrase required')
    if not provenance.get('source') or not provenance.get('meaning_preservation_review'):
        raise ValueError('paraphrase provenance and actual review record required')
    p=dict(paper);p.update(abstract=paraphrase,synthetic_manipulation=True,
        paper_id='e2paraphrase:'+hashlib.sha256(paraphrase.encode()).hexdigest()[:24],
        synthetic_condition='paraphrased_copy',paraphrase_provenance=provenance)
    return p
