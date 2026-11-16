"""Targeted local Task 3 evidence recovery; no model fitting or test evaluation."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
import pyarrow.parquet as pq
from human_check import normalize,title_key,resolve,value
from cached_extensions import Cache,text


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--benchmark',type=Path,required=True)
    p.add_argument('--history',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent
    bench=[normalize(r) for r in pq.read_table(a.benchmark).to_pylist()]
    with (a.source/'data/human-only/pointwise.yaml').open() as f:source=yaml.safe_load(f)
    mapping=list(csv.DictReader((a.source/'data/openreview_forum_ids.csv').open()))
    notes=[{'id':r['forum_id'],'content':{'title':r['title']}} for r in mapping]
    nested=[normalize({'id':int(k),**r}) for k,r in source.items()]
    resolved=resolve(nested,notes)
    by_title={title_key(r['title']):r for r in bench}
    mismatches=[r['id'] for r in nested if title_key(r['title']) not in by_title or
                r['label']!=by_title[title_key(r['title'])]['label'] or r['idea']!=by_title[title_key(r['title'])]['idea']]
    test_ids={r['forum_id'] for r in bench};test_titles={title_key(r['title']) for r in bench}
    history_forums=set();overlap=[];date_stats={};potential_dates={}
    eligible=set()
    with (root/'analysis/historical_manifest.csv').open() as f:
        for r in csv.DictReader(f):eligible.add(r['forum_id'])
    for year in range(2022,2026):
        vals={k:[] for k in ('pdate','odate','cdate')}
        with (a.history/f'iclr_{year}'/'papers.jsonl').open() as f:
            for line in f:
                r=json.loads(line);history_forums.add(r['id'])
                if r['id'] in test_ids:potential_dates[r['id']]={k:r.get(k) for k in vals}
                if r['id'] in test_ids or title_key(value(r['content'].get('title',''))) in test_titles:overlap.append(r['id'])
                if r['id'] not in eligible:continue
                for k in vals:
                    if isinstance(r.get(k),(int,float)) and r[k]>0:vals[k].append(r[k])
        iso=lambda ms:datetime.fromtimestamp(ms/1000,timezone.utc).isoformat()
        date_stats[year]={k:{'count':len(v),'min':iso(min(v)) if v else None,'max':iso(max(v)) if v else None} for k,v in vals.items()}
    cache=Cache(root/'data/novelty_embeddings.sqlite3')
    exact_abstract_hits=[]
    try:
        for r in bench:
            try:cache.get(r['idea']);exact_abstract_hits.append(r['id'])
            except KeyError:pass
    finally:cache.close()
    search_roots=[root,root.parent/'E1',root.parent/'E4',a.source,a.history.parent]
    found=[]
    for folder in search_roots:
        for path in folder.rglob('*'):
            if not path.is_file():continue
            if path.suffix in ('.npz','.npy') or ('prediction' in path.name.casefold() and path.suffix in ('.json','.jsonl')):
                found.append(str(path))
    report={'benchmark_records':len(bench),'nested_yaml_records':len(nested),'nested_source_mismatches':mismatches,
        'nested_title_mappings_resolved':sum(bool(r['forum_id']) for r in resolved),
        'benchmark_forums_in_history':sorted(test_ids&history_forums),'exact_title_or_id_overlap':overlap,
        'test_dates_recovered_from_history':potential_dates,'dates_in_nested_source':sum(bool(r.get('published') or r.get('metadata',{}).get('published')) for r in source.values()),
        'historical_date_fields':date_stats,'history_years':[2022,2023,2024,2025],'test_cohort':2026,
        'chronological_separation':'venue-year separation confirmed; item-level test dates unavailable',
        'benchmark_exact_abstract_cache_hits':exact_abstract_hits,
        'baseline_cache_reuse':'existing novelty cache is normalized CLS; protocol baseline requires raw abstract-only CLS',
        'prediction_or_matrix_candidates':found,
        'exact_blockers':['No item-level benchmark posting dates in local sources',
        'No documented encoder training cutoff in the supplied E2 evidence',
        'No four-measure benchmark predictions, frozen per-item eligible reference pools, or test claims',
        'No complete provenance-verified raw abstract-only historical/test embedding matrices'],
        'exposure_limitation':'Prior test exposure remains disclosed; continuation protocol does not make the study blind',
        'human_check_executed':False}
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Recovered nested source:',len(nested),'mapped:',report['nested_title_mappings_resolved'],'dates:',len(potential_dates),'abstract cache hits:',len(exact_abstract_hits))

if __name__=='__main__':main()
