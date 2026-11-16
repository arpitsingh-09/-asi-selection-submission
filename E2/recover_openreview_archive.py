"""Recover benchmark records directly from a local tar archive, without extraction.
Never runs upstream fetch scripts (which can invoke proprietary models).
"""
import argparse
import hashlib
import json
import tarfile
from datetime import datetime,timezone
from pathlib import Path
from human_check import value,title_key


def public_time(note):
    """OpenReview odate records public release; pdate is a separate publication field.
    Never substitute creation/modification timestamps for either public date.
    """
    vals=[(k,note.get(k)) for k in ('odate','pdate') if isinstance(note.get(k),(int,float)) and note[k]>0]
    if not vals:return None
    field,ms=min(vals,key=lambda item:item[1])
    return {'field':field,'milliseconds':ms,'iso':datetime.fromtimestamp(ms/1000,timezone.utc).isoformat()}


def join_records(benchmark,notes):
    byid={r['forum_id']:r for r in benchmark};matches={}
    for note in notes:
        if note.get('id') not in byid:continue
        pid=note['id'];b=byid[pid];c=note['content']
        if pid in matches:raise ValueError('duplicate matched forum')
        title=value(c.get('title',''));abstract=value(c.get('abstract',''))
        matches[pid]={'benchmark_id':b['id'],'forum_id':pid,'title':title,'abstract':abstract,
            'title_exact_normalized_match':title_key(title)==title_key(b['title']),
            'abstract_exact_match':abstract==b['idea'],
            'label':b['label'],'rating':b['rating'],'contribution':b['contribution'],
            'openreview_dates':{k:note.get(k) for k in ('cdate','pdate','odate','mdate','tcdate','tmdate')},
            'first_available_public_date':public_time(note)}
    return matches


def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--benchmark',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    import pyarrow.parquet as pq
    from human_check import normalize
    benchmark=[normalize(r) for r in pq.read_table(a.benchmark).to_pylist()]
    member='data/iclr_2026/papers.jsonl';found={}
    # Stream only as far as the needed member; never extract paths or scan reviews.
    with tarfile.open(a.archive,'r|bz2') as archive:
        for item in archive:
            if item.name!=member:continue
            with archive.extractfile(item) as handle:
                found=join_records(benchmark,(json.loads(line) for line in handle))
            break
        else:raise FileNotFoundError(member)
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'benchmark_records.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in sorted(found.values(),key=lambda r:r['benchmark_id'])))
    dated=[r for r in found.values() if r['first_available_public_date']]
    fingerprint=hashlib.sha256()
    with a.archive.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):fingerprint.update(chunk)
    summary={'archive':str(a.archive),'archive_sha256':fingerprint.hexdigest(),'archive_size_bytes':a.archive.stat().st_size,'member':member,
        'benchmark_sha256':hashlib.sha256(a.benchmark.read_bytes()).hexdigest(),
        'benchmark_records':len(benchmark),'matched_forums':len(found),'missing_forums':sorted({r['forum_id'] for r in benchmark}-set(found)),
        'titles_agree':sum(r['title_exact_normalized_match'] for r in found.values()),
        'abstracts_agree_exactly':sum(r['abstract_exact_match'] for r in found.values()),
        'with_public_date':len(dated),
        'earliest_public_date':min((r['first_available_public_date']['iso'] for r in dated),default=None),
        'latest_public_date':max((r['first_available_public_date']['iso'] for r in dated),default=None),
        'date_semantics':'Earliest available positive OpenReview odate (public release) or pdate (publication), never cdate/tmdate; raw fields retained.',
        'model_cutoff_verified':False,'human_check_executed':False}
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary,flush=True)

if __name__=='__main__':main()
