"""Freeze recovered original abstracts, dates and strictly prior reference IDs.
Prepares inputs only. Does not score, embed, fit models, or compute AUROC.
"""
import csv,hashlib,json
from pathlib import Path
from human_check import value
from recover_openreview_archive import public_time
from cached_extensions import Cache,text


def digest(s):return hashlib.sha256(s.encode()).hexdigest()

def prior_references(records,cutoff):
    return [r for r in records if r.get('public_date') and r['public_date']<cutoff]

def main():
    root=Path(__file__).resolve().parent;out=root/'analysis/recovered_inputs_v1';out.mkdir(exist_ok=False)
    test=list(map(json.loads,(root/'analysis/openreview_archive_v1/benchmark_records.jsonl').read_text().splitlines()))
    if len(test)!=299 or any(not r['title_exact_normalized_match'] or not r['abstract'] or not r['first_available_public_date'] for r in test):
        raise ValueError('incomplete/unmatched test records')
    earliest=min(r['first_available_public_date']['iso'] for r in test)
    test_ids={r['forum_id'] for r in test};eligible={}
    with (root/'analysis/historical_manifest.csv').open() as f:
        for r in csv.DictReader(f):eligible[r['forum_id']]=r
    refs=[];missing=[]
    history=Path.home()/'Downloads/iclr_task3_baseline/data'
    for year in range(2022,2026):
        source=history/f'iclr_{year}'/'papers.jsonl'
        with source.open() as f:
            for line,s in enumerate(f,1):
                r=json.loads(s)
                if r['id'] not in eligible:continue
                if r['id'] in test_ids:raise ValueError('test leakage')
                date=public_time(r);abstract=value(r['content'].get('abstract',''))
                if not date or not abstract:missing.append(r['id']);continue
                refs.append({'forum_id':r['id'],'year':year,'public_date':date['iso'],'date_field':date['field'],
                    'abstract_sha256':digest(abstract),'source':str(source),'source_line':line})
    references=prior_references(refs,earliest)
    if len({r['forum_id'] for r in references})!=len(references):raise ValueError('duplicate reference IDs')
    fields=['forum_id','year','public_date','date_field','abstract_sha256','source','source_line']
    with (out/'reference_manifest.csv').open('w') as f:
        w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(references)
    # Original source abstract is distinct from edited benchmark idea; never substitute silently.
    import pyarrow.parquet as pq
    p=next((Path.home()/'.cache/huggingface/hub/datasets--allenai--novelty-judge-bench/snapshots').rglob('human-only_pointwise.parquet'))
    bench={r['id']:r for r in pq.read_table(p).to_pylist()}
    inputs=[]
    for r in test:
        b=bench[r['benchmark_id']]
        inputs.append({'id':r['benchmark_id'],'forum_id':r['forum_id'],'title':r['title'],
            'label':b['label'],'rating':b['rating'],'contribution':b['contribution'],
            'idea':b['idea'],'abstract':r['abstract'],'published':r['first_available_public_date']['iso'],
            'abstract_sha256':digest(r['abstract']),'idea_sha256':digest(b['idea']),
            'abstract_source':'original_archived_OpenReview_note','idea_source':'R2_model_edited_abstract',
            'reference_pool':'reference_manifest.csv'})
    (out/'benchmark_inputs.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in inputs))
    # Check only previously unscored modified texts; no numerical evaluation occurs here.
    cache=Cache(root/'data/novelty_embeddings.sqlite3');missing_texts=set();plans=0;complete=0
    try:
        for r in map(json.loads,(root/'analysis/cached_extensions_v1/nearest_planting_plan.jsonl').read_text().splitlines()):
            plans+=1;all_present=True
            for paper in r['synthetic_papers']:
                s=text(paper)
                try:cache.get(s)
                except KeyError:missing_texts.add(digest(s));all_present=False
            complete+=int(all_present)
    finally:cache.close()
    summary={'test_dates_recovered':len(test),'original_test_abstracts_recovered':len(inputs),
        'benchmark_labels_available':len(inputs),'historical_quality_training_papers':len(eligible),
        'references_with_abstract_and_public_date':len(refs),'references_before_every_test_public_date':len(references),
        'references_missing_date_or_abstract':missing,'references_not_before_earliest_test':len(refs)-len(references),
        'earliest_test_public_date':earliest,'latest_reference_public_date':max(r['public_date'] for r in references),
        'original_vs_edited_abstract_exact_agreement':sum(r['abstract']==r['idea'] for r in inputs),
        'nearest_plans_checked':plans,'nearest_plans_with_all_modified_embeddings':complete,
        'missing_unique_nearest_modified_embeddings':len(missing_texts),
        'reference_manifest_sha256':hashlib.sha256((out/'reference_manifest.csv').read_bytes()).hexdigest(),
        'benchmark_inputs_sha256':hashlib.sha256((out/'benchmark_inputs.jsonl').read_bytes()).hexdigest(),
        'evaluation_executed':False,
        'remaining_blockers':['Documented encoder cutoff or defensible release-bound evidence for the pinned weights',
        'Raw abstract-only historical/test embeddings are unavailable; new inference is prohibited',
        'Benchmark claim sets and four novelty prediction vectors are unavailable'],
        'protocol_note':'Input preparation only. Original abstracts differ from edited R2 ideas; representation choice must be frozen before evaluation. Prior label exposure remains disclosed.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

if __name__=='__main__':main()
