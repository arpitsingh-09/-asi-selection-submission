"""Local metadata/cache CLI; commands produce features/readouts, not test accuracy."""
import argparse
import json
from pathlib import Path
from . import ResearchSpace,PaperStore,CachedEncoder,Phi,QualityModels,validate_split,controls


def records(path):
    p=Path(path)
    if p.suffix=='.jsonl':return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
    r=json.loads(p.read_text());return r['papers'] if isinstance(r,dict) and 'papers' in r else r


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('encode','readouts','compare','set','controls','update'):
        a=sub.add_parser(name);a.add_argument('--papers',type=Path)
        a.add_argument('--embeddings-cache',type=Path);a.add_argument('--quality-model',type=Path)
        a.add_argument('--time',required=True);a.add_argument('--inputs',nargs='*',default=None)
        if name not in ('set','update'):a.add_argument('--q',required=True)
        if name in ('encode','readouts'):a.add_argument('--kind',choices=('generated','published'),default='generated');a.add_argument('--paper-id',default='')
        if name=='compare':a.add_argument('--other',required=True)
        if name=='set':a.add_argument('--questions',type=Path,required=True)
        if name=='controls':a.add_argument('--shuffled-inputs',nargs='+',required=True);a.add_argument('--decoy',required=True)
        if name=='update':a.add_argument('--snapshot',type=Path,required=True);a.add_argument('--new-papers',type=Path,required=True)
    a=sub.add_parser('validate-splits');a.add_argument('--records',type=Path,required=True);a.add_argument('--split',choices=('train','validation','test'),required=True)
    a=p.parse_args()
    if a.command=='validate-splits':result=validate_split(records(a.records),a.split)
    else:
        encoder=CachedEncoder(a.embeddings_cache) if a.embeddings_cache else None
        space=ResearchSpace(PaperStore.load(a.papers) if a.papers else (),encoder,
                            quality_models=QualityModels.load(a.quality_model) if a.quality_model else None)
        try:
            if a.command in ('encode','readouts'):
                s=space.encode(a.q,a.inputs,a.time,source_kind=a.kind,paper_id=a.paper_id)
                result=s.to_dict() if a.command=='encode' else space.readouts(s)
            elif a.command=='compare':result=space.compare(space.encode(a.q,a.inputs,a.time),space.encode(a.other,a.inputs,a.time))
            elif a.command=='set':result=space.diversity([space.encode(q,a.inputs,a.time) for q in records(a.questions)])
            elif a.command=='controls':result=controls(space,a.q,a.inputs,a.time,shuffled_R=a.shuffled_inputs,decoy_q=a.decoy)
            else:
                old=Phi.from_dict(json.loads(a.snapshot.read_text()))
                future,s=space.update(old,records(a.new_papers),a.time)
                result={'snapshot':s.to_dict(),'readouts':future.readouts(s)}
        finally:
            if encoder is not None:encoder.close()
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
