"""Local metadata only. No implicit network retrieval, model call or mutation."""
import json
from pathlib import Path
from types import MappingProxyType
from .schema import Paper,date,MissingInputError,LeakageError


class PaperStore:
    def __init__(self,records=()):
        papers={}
        for r in records:
            p=Paper.from_dict(r.to_dict() if isinstance(r,Paper) else r)
            if p.paper_id in papers and papers[p.paper_id]!=p:raise ValueError('conflicting paper/version ID')
            papers[p.paper_id]=p
        self.papers=MappingProxyType(papers)

    @classmethod
    def load(cls,path):
        path=Path(path)
        if path.suffix=='.jsonl':records=[json.loads(s) for s in path.read_text().splitlines() if s.strip()]
        else:
            obj=json.loads(path.read_text());records=obj['papers'] if isinstance(obj,dict) else obj
        return cls(records)

    def get(self,pid):
        if pid not in self.papers:raise MissingInputError('unknown paper: '+pid)
        return self.papers[pid]

    def eligible(self,t,exclude=''):
        when=date(t)
        return [p for _,p in sorted(self.papers.items()) if p.paper_id!=exclude and date(p.published)<when and date(p.available_at)<=when]

    def updated(self,records,arrival):
        new=list(self.papers.values())
        for r in records:
            p=Paper.from_dict(r.to_dict() if isinstance(r,Paper) else r,arrival=arrival)
            if p.paper_id in self.papers:
                if self.papers[p.paper_id]!=p:raise ValueError('updates must use a new version ID; historical paper is immutable')
            else:new.append(p)
        return PaperStore(new)
