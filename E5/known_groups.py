"""Known-group construction from externally supplied Semantic Scholar metadata.
No paper identities, dates, citations, real questions or generation are invented.
"""
import calendar
from datetime import date
from itertools import combinations
import hashlib
import json
from pathlib import Path


def twelve_months_after(d):
    return d.replace(year=d.year+1,day=min(d.day,calendar.monthrange(d.year+1,d.month)[1]))


def build_groups(papers,seed_ids):
    if len(seed_ids)<3 or len(set(seed_ids))!=len(seed_ids):raise ValueError('at least three unique declared seeds required')
    if len(seed_ids)>20:raise ValueError('bounded seed inventory: at most 20')
    byid={p['paperId']:p for p in papers}
    if len(byid)!=len(papers):raise ValueError('duplicate paper IDs')
    buckets={};excluded=[]
    for p in papers:
        if p['paperId'] in seed_ids:
            excluded.append({'paperId':p['paperId'],'reason':'seed_not_candidate'});continue
        if p.get('source')!='Semantic Scholar' or not p.get('source_url'):
            raise ValueError('Semantic Scholar source provenance required')
        try:d=date.fromisoformat(p['publicationDate'])
        except (ValueError,KeyError,TypeError):excluded.append({'paperId':p['paperId'],'reason':'missing_exact_publication_date'});continue
        refs={r['paperId'] for r in p.get('references',[]) if r.get('paperId')}
        shared=sorted(refs&set(seed_ids))
        for triple in combinations(shared,3):buckets.setdefault(triple,[]).append((d,p['paperId']))
    groups=[];seen=set()
    for seeds,members in sorted(buckets.items()):
        ordered=sorted(members)
        for i,(start,_) in enumerate(ordered):
            window=[(d,pid) for d,pid in ordered[i:] if d<=twelve_months_after(start)]
            if len(window)<5:continue
            chosen=tuple(pid for _,pid in window[:5]);key=(seeds,chosen)
            if key in seen:continue
            seen.add(key)
            groups.append({'id':hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16],
                'seed_ids':list(seeds),'paper_ids':list(chosen),'earliest_date':window[0][0].isoformat(),
                'latest_date':window[4][0].isoformat(),'citation_and_window_verified':True,
                'real_questions':None,'generated_questions':None,
                'status':'needs_source_bound_real_questions_and_five_generated_questions_from_same_seeds'})
    return {'groups':groups,'excluded':excluded}


def validate_pair(group):
    for key in ('real_questions','generated_questions'):
        if not isinstance(group.get(key),list) or len(group[key])!=5 or any(not isinstance(q,str) or not q.strip() for q in group[key]):
            raise ValueError('five genuine supplied '+key+' required')
    provenance=group.get('generator_provenance',{})
    sources=group.get('real_question_sources',[])
    if (len(sources)!=5 or {r.get('paperId') for r in sources}!=set(group['paper_ids'])
        or any(not r.get('source_url') or not r.get('evidence') for r in sources)
        or set(provenance.get('seed_ids',[]))!=set(group['seed_ids']) or not provenance.get('method')):
        raise ValueError('source-bound real questions and same-seed generator provenance required')
    if len(set(group['seed_ids']))<3 or len(set(group['paper_ids']))!=5:
        raise ValueError('group identities invalid')
    if group.get('citation_and_window_verified') is not True:raise ValueError('citation/window verification required')
    return group


def dependency_components(groups):
    """Bootstrap connected groups together when they share seeds or real papers."""
    parent=list(range(len(groups)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,g in enumerate(groups):
        for j in range(i):
            if set(g['seed_ids'])&set(groups[j]['seed_ids']) or set(g['paper_ids'])&set(groups[j]['paper_ids']):
                parent[find(i)]=find(j)
    return [find(i) for i in range(len(groups))]
