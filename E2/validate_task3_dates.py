"""Recheck frozen local date/text evidence without inference or evaluation."""
import argparse
import csv
import json
from pathlib import Path
from recover_openreview_archive import public_time
from task3_eligibility import date
from task3_plan import jsonl, sha_file, sha_text


def audit(output):
    root = Path(__file__).resolve().parent
    recovered = root/'analysis/recovered_inputs_v1'
    summary = json.loads((recovered/'summary.json').read_text())
    bench_path = recovered/'benchmark_inputs.jsonl'
    ref_path = recovered/'reference_manifest.csv'
    assert sha_file(bench_path) == summary['benchmark_inputs_sha256']
    assert sha_file(ref_path) == summary['reference_manifest_sha256']
    bench = list(jsonl(bench_path))
    with ref_path.open() as f:
        refs = list(csv.DictReader(f))
    archive = {r['forum_id']: r for r in jsonl(root/'analysis/openreview_archive_v1/benchmark_records.jsonl')}
    earliest = min(date(b['published']) for b in bench)
    for b in bench:
        a = archive[b['forum_id']]
        t = public_time(a['openreview_dates'])
        assert t and date(t['iso']) == date(b['published'])
        assert a['abstract'] == b['abstract'] and sha_text(b['abstract']) == b['abstract_sha256']
    groups = {}
    for r in refs:
        groups.setdefault(r['source'], {})[r['forum_id']] = r
    checked = 0
    for source, wanted in groups.items():
        seen = set()
        for note in jsonl(source):
            if note['id'] not in wanted:
                continue
            r = wanted[note['id']]
            assert note['id'] not in seen
            seen.add(note['id'])
            t = public_time(note)
            assert t and t['field'] == r['date_field'] and date(t['iso']) == date(r['public_date'])
            abstract = note['content']['abstract']
            if isinstance(abstract, dict): abstract = abstract['value']
            assert sha_text(abstract) == r['abstract_sha256']
            assert date(r['public_date']) < earliest
            checked += 1
        assert seen == set(wanted)
    assert len(bench) == len(archive) == 299 and checked == len(refs) == 25186
    assert not {b['forum_id'] for b in bench} & {r['forum_id'] for r in refs}
    inventory = root/'analysis/task3_execution_v1/model_inventory.json'
    evidence = json.loads(inventory.read_text())['release_evidence']
    report = {
        'benchmark_records_verified':len(bench), 'historical_records_verified':checked,
        'benchmark_sha256':sha_file(bench_path), 'reference_sha256':sha_file(ref_path),
        'model_inventory_sha256':sha_file(inventory),
        'earliest_test_openreview_date':earliest.isoformat(),
        'latest_history_openreview_date':max(date(r['public_date']) for r in refs).isoformat(),
        'date_rule':'Earliest positive odate/pdate; never creation/modification timestamps or venue-year dates. History strictly before earliest benchmark OpenReview date.',
        'source_date_and_abstract_bindings_verified':True,
        'local_model_evidence':evidence,
        'exact_training_cutoff_established':False,
        'first_global_publication_verified':False,
        'version_caveat':'Archived abstracts are hash-bound, but availability of that exact text at first publication is unverified.',
        'next_step':'Collect item-level first global publication/preprint evidence for all 299 papers, bound to original abstract hashes; do not infer it from October 2025 OpenReview dates.',
        'inference_executed':False, 'evaluation_executed':False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as f: json.dump(report,f,indent=2); f.write('\n')
    print({'benchmark_verified':len(bench),'history_verified':checked,'cutoff_established':False})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    audit(parser.parse_args().output)
