"""Immutable, JSON-serializable data contracts for the shared research space."""
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import hashlib
import json
import math


class LeakageError(ValueError):pass
class MissingInputError(ValueError):pass


def date(value):
    if isinstance(value,datetime):d=value
    elif isinstance(value,str):
        d=datetime.fromisoformat(value.replace('Z','+00:00'))
        if len(value)==10:d=d.replace(tzinfo=timezone.utc)
    else:raise ValueError('date must be ISO text or datetime')
    if d.tzinfo is None:raise ValueError('timezone required for timestamps')
    return d.astimezone(timezone.utc)


def iso(value):return date(value).isoformat()
def norm(value):return ' '.join(value.casefold().split())
def fingerprint(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class AnswerEvidence:
    question:str
    excerpt:str
    field:str
    available_at:str
    verified:bool


@dataclass(frozen=True)
class Paper:
    paper_id:str
    published:str
    title:str=''
    abstract:str=''
    question:str=''
    available_at:str=''
    topic:str=''
    answers:tuple=()

    @classmethod
    def from_dict(cls,r,arrival=None):
        pid=r.get('paper_id',r.get('id'))
        if not isinstance(pid,str) or not pid.strip():raise ValueError('paper ID required')
        pub=iso(r['published'])
        default_available=max(date(arrival),date(pub)).isoformat() if arrival else pub
        available=iso(r.get('available_at') or default_available)
        if date(available)<date(pub):raise LeakageError('paper available before publication')
        title=r.get('title','');abstract=r.get('abstract','');q=r.get('question',r.get('rq',''))
        if any(not isinstance(s,str) for s in (title,abstract,q)):raise ValueError('paper texts must be strings')
        answers=[]
        for a in r.get('answers',[]):
            field=a.get('field','abstract');body={'title':title,'abstract':abstract,'question':q}.get(field)
            if not isinstance(a.get('question'),str) or not a['question'].strip() or not isinstance(a.get('excerpt'),str) or not a['excerpt'].strip() or body is None or a['excerpt'] not in body:
                raise ValueError('answer evidence must quote an actual source field')
            when=iso(a.get('available_at',available))
            if date(when)<date(pub):raise LeakageError('answer evidence before source publication')
            answers.append(AnswerEvidence(a['question'],a['excerpt'],field,when,a.get('verified') is True))
        return cls(pid,pub,title,abstract,q,available,r.get('topic',''),tuple(answers))

    @property
    def text(self):return (self.title.strip()+'\n\n'+self.abstract.strip()).strip() or self.question.strip()
    def to_dict(self):return asdict(self)


@dataclass(frozen=True)
class EmbeddedPaper:
    paper:Paper
    text_vector:tuple
    question_vector:tuple=()
    facets:tuple=()


@dataclass(frozen=True)
class Phi:
    """One structured representation: shared vectors, relations and as-of memory.
    Readouts do not retrieve, re-encode, or launch independent model prompts.
    """
    schema_version:str
    snapshot_id:str
    previous_snapshot_id:str
    q:str
    as_of:str
    source_kind:str
    source_paper_id:str
    source_abstract:str
    source_abstract_vector:tuple
    topic:str
    space_id:str
    encoder_kind:str
    feature_schema:str
    vector:tuple
    question_vector:tuple
    context_vector:tuple
    facets:tuple
    facet_vectors:tuple
    claims:tuple
    claim_vectors:tuple
    inputs:tuple
    literature:tuple
    reference_scope:str
    input_mode:str
    excluded_future_ids:tuple
    structural_quality:tuple
    tfidf_training_documents:tuple
    warnings:tuple

    def to_dict(self):return asdict(self)

    @classmethod
    def from_dict(cls,r):
        data=dict(r)
        for field in ('source_abstract_vector','vector','question_vector','context_vector','claims','excluded_future_ids','warnings'):
            data[field]=tuple(data[field])
        for field in ('facets','facet_vectors','claim_vectors','structural_quality','tfidf_training_documents'):
            data[field]=tuple((k,tuple(v) if field=='facet_vectors' else v) for k,v in data[field]) if field in ('facets','facet_vectors','structural_quality','tfidf_training_documents') else tuple(tuple(v) for v in data[field])
        for field in ('inputs','literature'):
            values=[]
            for row in data[field]:
                p=dict(row['paper']);p['answers']=[dict(a) for a in p.get('answers',[])]
                values.append(EmbeddedPaper(Paper.from_dict(p),tuple(row['text_vector']),tuple(row.get('question_vector',())),tuple(tuple(x) for x in row.get('facets',()))))
            data[field]=tuple(values)
        obj=cls(**data)
        if obj.schema_version!='phi-v1' or not obj.q.strip() or not obj.space_id:raise ValueError('invalid Phi schema')
        dim=len(obj.question_vector)
        if dim==0 or len(obj.vector)!=7*dim+7 or len(obj.context_vector)!=dim:raise ValueError('Phi feature dimension mismatch')
        names={'purpose','mechanism','evaluation','domain'}
        if len(obj.facets)!=4 or set(dict(obj.facets))!=names or len(obj.facet_vectors)!=4 or set(dict(obj.facet_vectors))!=names:
            raise ValueError('four aligned facets required')
        if len(obj.claims)!=len(obj.claim_vectors):raise ValueError('claim vector alignment mismatch')
        vectors=[v for _,v in obj.facet_vectors]+list(obj.claim_vectors)
        if obj.source_abstract_vector:vectors.append(obj.source_abstract_vector)
        for p in obj.inputs+obj.literature:
            vectors.append(p.text_vector)
            if p.question_vector:vectors.append(p.question_vector)
        if any(len(v)!=dim or not all(math.isfinite(x) for x in v) for v in vectors):raise ValueError('invalid Phi component vector')
        if any(not math.isfinite(v) for v in obj.vector+obj.question_vector+obj.context_vector):raise ValueError('nonfinite Phi feature')
        for paper in obj.inputs+obj.literature:
            if date(paper.paper.published)>=date(obj.as_of) or date(paper.paper.available_at)>date(obj.as_of):
                raise LeakageError('snapshot contains future reference/input')
            if paper.paper.paper_id==obj.source_paper_id:raise LeakageError('snapshot contains its focal paper')
            if any(date(a.available_at)>date(obj.as_of) for a in paper.paper.answers):raise LeakageError('snapshot contains future answer annotation')
        if obj.excluded_future_ids:raise LeakageError('future identifiers must not enter Phi')
        if fingerprint({k:v for k,v in obj.to_dict().items() if k!='snapshot_id'})!=obj.snapshot_id:raise ValueError('snapshot fingerprint mismatch')
        return obj
