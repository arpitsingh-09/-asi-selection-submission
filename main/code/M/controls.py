"""Input controls from the same encoder, time, and shared representation."""
import random
from .schema import norm,date,MissingInputError


def controls(space,q,R,t,*,shuffled_R,decoy_q,topic=None):
    original=space.encode(q,R,t)
    empty=space.encode(q,[],t)
    shuffled=space.encode(q,shuffled_R,t)
    if not shuffled.inputs or {p.paper.paper_id for p in shuffled.inputs}=={p.paper.paper_id for p in original.inputs}:
        raise ValueError('shuffled control must use another instance inputs, not a permutation')
    decoy_text=decoy_q.get('question',decoy_q.get('rq','')) if isinstance(decoy_q,dict) else decoy_q
    if norm(decoy_text)==norm(original.q):raise ValueError('decoy must differ from original question')
    declared_topic=topic or original.topic
    if isinstance(decoy_q,dict) and declared_topic and decoy_q.get('topic')!=declared_topic:
        raise ValueError('decoy must have the same declared topic')
    decoy=space.encode(decoy_q,[p.paper for p in original.inputs],t)
    snapshots={'original':original,'empty':empty,'shuffled':shuffled,'decoy':decoy}
    return {'controls':{k:space.readouts(v) for k,v in snapshots.items()},
            'snapshot_ids':{k:v.snapshot_id for k,v in snapshots.items()},
            'same_topic_status':'caller-declared topic, not independent semantic validation' if declared_topic else 'unverified; caller must validate same-topic decoy'}


def sample_same_topic_decoy(question,topic,candidates,t,seed=20261113):
    pool=[r for r in candidates if r.get('topic')==topic and norm(r['question'])!=norm(question)
          and r.get('posed_at') and date(r['posed_at'])<=date(t)]
    if not pool:raise MissingInputError('no dated same-topic decoy candidate')
    return random.Random(seed).choice(sorted(pool,key=lambda r:r['question']))
