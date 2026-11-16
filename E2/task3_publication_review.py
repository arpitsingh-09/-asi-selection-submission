"""Conservative local publication-history review. No network, models or scoring.

An observed release proves availability by a date, never absence of earlier work.
Title-only matches and cited arXiv links are manual leads, not paper identities.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from datetime import datetime, timezone


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def title_key(s):
    return re.sub(r'[^\w]', '', unicodedata.normalize('NFKC', s).casefold())


def abstract_key(s):
    return ' '.join(unicodedata.normalize('NFKC', s).split())


def value(x):
    return x.get('value', '') if isinstance(x, dict) else x


def timestamp(s):
    dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timezone required')
    return dt


def public_date(note):
    vals = [(k, v) for k in ('odate', 'pdate')
            if type(v := note.get(k)) in (int, float) and v > 0]
    if not vals:
        return None
    k, ms = min(vals, key=lambda x:x[1])
    return k, datetime.fromtimestamp(ms/1000, timezone.utc).isoformat()


def identity(benchmark, record):
    if record.get('forum_id') == benchmark['forum_id']:
        # A forum joins the paper, but text still must bind to the recovered source.
        if (record.get('abstract_sha256') == benchmark['abstract_sha256']
                and digest(record['abstract']) == benchmark['abstract_sha256']):
            return 'forum_and_original_abstract_hash'
        return None
    if (record['title'].strip() and record['abstract'].strip()
            and title_key(record['title']) == title_key(benchmark['title'])
            and abstract_key(record['abstract']) == abstract_key(benchmark['abstract'])):
        return 'normalized_title_and_exact_whitespace_normalized_abstract'
    return None


def resolve(benchmark, observations, cutoff):
    verified, candidates = [], []
    for obs in observations:
        method = identity(benchmark, obs)
        e = dict(obs, identity_method=method)
        if method and obs.get('public_date'):
            timestamp(obs['public_date'])
            verified.append(e)
        else:
            candidates.append(e)
    verified.sort(key=lambda x:timestamp(x['public_date']))
    earliest = verified[0] if verified else None
    earlier = [o for o in verified if timestamp(o['public_date']) < timestamp(benchmark['published'])]
    preprints = [o for o in earlier if o['kind'] == 'arxiv']
    before_bound = [o for o in verified if timestamp(o['public_date']) <= timestamp(cutoff)]
    return {
        'forum_id':benchmark['forum_id'], 'title':benchmark['title'],
        'abstract_sha256':benchmark['abstract_sha256'],
        'archived_openreview_public_date':benchmark['published'],
        'earliest_verified_observed_release':earliest['public_date'] if earliest else None,
        'earliest_verified_observed_source':earliest['source'] if earliest else None,
        # Never turn a finite cache search into proof of first global publication.
        'first_public_date':None, 'first_publication_verified':False, 'source':None,
        'publication_history_status':'earlier_preprint_detected' if preprints else 'unresolved_publication_history',
        'earlier_public_release_detected':bool(earlier),
        'earlier_preprint_detected':bool(preprints),
        'eligibility_relative_to_conservative_bound':
            'fails_post_bound_requirement' if before_bound else 'unresolved_earlier_history_not_excluded',
        'exact_training_cutoff_eligibility':'unresolved_exact_cutoff_unknown',
        'verified_release_observations':verified, 'manual_identity_candidates':candidates,
        'archived_text_at_first_release_verified':False,
        'manual_action':'Verify first global publication/preprint history and exact paper/version identity; retain original abstract hash.',
    }


def run(root, history, upstream, output):
    root = Path(root).resolve()
    paths = {
        'benchmark':root/'analysis/recovered_inputs_v1/benchmark_inputs.jsonl',
        'pending':root/'analysis/task3_first_publication_review_pending_v1.json',
        'recovered_archive':root/'analysis/openreview_archive_v1/benchmark_records.jsonl',
        'model_inventory':root/'analysis/task3_execution_v1/model_inventory.json',
        'arxiv_cache':root/'data/raw_papers.jsonl',
        'upstream_labels':Path(upstream)/'data/human-only/pointwise.yaml',
    }
    fingerprints = {}
    def lines(path):
        # Hash exact bytes while reading each bounded local metadata source once.
        h = hashlib.sha256(); count = 0
        with Path(path).open('rb') as f:
            for number, raw in enumerate(f, 1):
                h.update(raw)
                if raw.strip():
                    count += 1
                    yield number, json.loads(raw)
        fingerprints[str(path)] = {'sha256':h.hexdigest(), 'records':count}
    bench = [r for _, r in lines(paths['benchmark'])]
    if len(bench) != 299 or len({r['forum_id'] for r in bench}) != 299:
        raise ValueError('expected 299 unique benchmark forums')
    for b in bench:
        if digest(b['abstract']) != b['abstract_sha256']:
            raise ValueError('benchmark abstract hash mismatch')
        timestamp(b['published'])
    frozen_summary_path = root/'analysis/recovered_inputs_v1/summary.json'
    frozen_bytes = frozen_summary_path.read_bytes()
    frozen_summary = json.loads(frozen_bytes)
    if fingerprints[str(paths['benchmark'])]['sha256'] != frozen_summary['benchmark_inputs_sha256']:
        raise ValueError('frozen benchmark fingerprint changed')
    fingerprints[str(frozen_summary_path)] = {'sha256':hashlib.sha256(frozen_bytes).hexdigest()}
    pending_bytes = paths['pending'].read_bytes()
    pending = json.loads(pending_bytes)['records']
    fingerprints[str(paths['pending'])] = {'sha256':hashlib.sha256(pending_bytes).hexdigest()}
    if len(pending) != len(bench) or {r['forum_id']:r['abstract_sha256'] for r in pending} != {r['forum_id']:r['abstract_sha256'] for r in bench}:
        raise ValueError('pending review coverage/binding mismatch')
    bytitle = {}
    for b in bench:bytitle.setdefault(title_key(b['title']), []).append(b)
    byid = {b['forum_id']:b for b in bench}; observations = {pid:[] for pid in byid}
    for number, r in lines(paths['recovered_archive']):
        b = byid[r['forum_id']]
        t = public_date(r['openreview_dates'])
        if not t or timestamp(t[1]) != timestamp(b['published']) or r['abstract'] != b['abstract']:
            raise ValueError('recovered source binding/date mismatch')
        observations[b['forum_id']].append({
            'kind':'openreview', 'forum_id':r['forum_id'], 'title':r['title'],
            'abstract':r['abstract'], 'abstract_sha256':digest(r['abstract']),
            'public_date':t[1], 'date_field':t[0],
            'source':str(paths['recovered_archive']), 'source_line':number,
            'url':'https://openreview.net/forum?id='+r['forum_id'],
        })
    if any(len(v)!=1 for v in observations.values()):raise ValueError('archive coverage mismatch')
    source_paths = [paths['arxiv_cache']] + [Path(history)/f'iclr_{y}/papers.jsonl' for y in range(2022,2026)]
    for path in source_paths:
        arxiv = path == paths['arxiv_cache']
        for number, r in lines(path):
            c = r if arxiv else r['content']
            title, abstract = value(c.get('title','')), value(c.get('abstract',''))
            matches = bytitle.get(title_key(title), [])
            if not matches:continue
            t = ('published',r.get('published')) if arxiv else public_date(r)
            pid = r['paper_id'] if arxiv else r['id']
            for b in matches:
                observations[b['forum_id']].append({
                    'kind':'arxiv' if arxiv else 'openreview',
                    'forum_id':None if arxiv else pid, 'paper_id':pid,
                    'title':title, 'abstract':abstract, 'abstract_sha256':digest(abstract),
                    'public_date':t[1] if t else None, 'date_field':t[0] if t else None,
                    'source':str(path), 'source_line':number,
                    'url':('https://arxiv.org/abs/' if arxiv else 'https://openreview.net/forum?id=')+pid,
                    'authors':value(c.get('authors',[])),
                    'identity_caveat':'Title match only unless original text also matches; earlier version may differ.',
                })
    # Reviewer references are leads only; a cited paper is not necessarily this paper.
    import yaml
    raw = paths['upstream_labels'].read_bytes()
    fingerprints[str(paths['upstream_labels'])] = {'sha256':hashlib.sha256(raw).hexdigest()}
    labels = yaml.safe_load(raw)
    leads = {}
    for b in bench:
        row = labels.get(str(b['id']), labels.get(b['id']))
        if row is None or title_key(row['metadata']['title']) != title_key(b['title']):
            raise ValueError('upstream label identity mismatch')
        def strings(obj):
            if isinstance(obj, str):yield obj
            elif isinstance(obj, dict):
                for v in obj.values():yield from strings(v)
            elif isinstance(obj, list):
                for v in obj:yield from strings(v)
        urls = sorted({u for text in strings(row) for u in re.findall(r'https?://[^\s<>\]\"\)]+', text)})
        leads[b['forum_id']] = [{'url':u,'identity_verified':False,
            'source':str(paths['upstream_labels']), 'source_key':str(b['id']),
            'caveat':'May describe cited/related work; not self-preprint evidence.'} for u in urls]
    inv_bytes = paths['model_inventory'].read_bytes()
    fingerprints[str(paths['model_inventory'])] = {'sha256':hashlib.sha256(inv_bytes).hexdigest()}
    evidence = json.loads(inv_bytes)['release_evidence']
    cutoff = evidence['conservative_weights_existence_bound']
    rows = [resolve(b, observations[b['forum_id']], cutoff) for b in bench]
    for r in rows:r['unverified_url_leads'] = leads[r['forum_id']]
    counts = {
        'papers':len(rows),
        'automatically_verified_observed_release':sum(bool(r['verified_release_observations']) for r in rows),
        'automatically_verified_first_global_release':0,
        'earlier_preprint_detected':sum(r['earlier_preprint_detected'] for r in rows),
        'earlier_public_release_detected':sum(r['earlier_public_release_detected'] for r in rows),
        'manual_identity_candidate_papers':sum(bool(r['manual_identity_candidates']) for r in rows),
        'manual_identity_candidate_records':sum(len(r['manual_identity_candidates']) for r in rows),
        'papers_requiring_manual_verification':sum(not r['first_publication_verified'] for r in rows),
        'eligibility_relative_to_bound':dict(Counter(r['eligibility_relative_to_conservative_bound'] for r in rows)),
    }
    fingerprints[str(Path(__file__).resolve())] = {'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    report = {'format':1, 'status':'local_review_not_evaluation_authorization',
        'summary':counts, 'model_evidence':evidence, 'source_fingerprints':fingerprints,
        'limitations':[
            'No evidence of absence of earlier preprints; first global publication remains unverified.',
            'Recovered archive omits benchmark authors and external-link fields; raw 489 MiB bzip2 archive was not decompressed under lightweight-only restrictions.',
            'Historical metadata and arXiv cache are finite and incomplete; title variants may be missed.',
            'No date is inferred from an arXiv identifier, venue year, creation time or modified time.',
            'Original archived abstract availability at first release remains unverified.',
        ], 'records':rows}
    output = Path(output); output.mkdir(parents=True,exist_ok=False)
    (output/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    with (output/'review.csv').open('w') as f:
        fields = ['forum_id','title','abstract_sha256','earliest_verified_observed_release',
                  'first_publication_verified','publication_history_status','earlier_preprint_detected',
                  'eligibility_relative_to_conservative_bound']
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    candidate_rows = []
    for r in rows:
        for c in r['manual_identity_candidates']:
            candidate_rows.append({'benchmark_forum_id':r['forum_id'], 'title':r['title'],
                'candidate_paper_id':c['paper_id'], 'candidate_public_date':c['public_date'],
                'before_model_bound':bool(c['public_date'] and timestamp(c['public_date']) <= timestamp(cutoff)),
                'identity_verified':False, 'source':c['source'], 'source_line':c['source_line']})
    with (output/'identity_candidates.csv').open('w') as f:
        fields = ['benchmark_forum_id','title','candidate_paper_id','candidate_public_date',
                  'before_model_bound','identity_verified','source','source_line']
        w = csv.DictWriter(f,fields);w.writeheader();w.writerows(candidate_rows)
    table = '\n'.join(f"| {r['forum_id']} | {r['title']} | {len(r['manual_identity_candidates'])} |" for r in rows if r['manual_identity_candidates'])
    (output/'REPORT.md').write_text(
        '# Local first-publication review\n\n' +
        '\n'.join(f'- {k}: {v}' for k,v in counts.items()) +
        '\n\nAll 299 observed OpenReview release dates are verified locally; none proves first global publication. '
        'No earlier preprint was confirmed in these finite local sources. The exact model cutoff remains unknown; '
        'all post-cutoff eligibility decisions remain unresolved.\n\n'
        '| Forum | Title requiring identity review | Older records |\n|---|---|---|\n'+table+
        '\n\nNext: verify these three older-title identity candidates first, then obtain authoritative '
        'first-version/preprint histories and exact identity evidence for all 299 papers. '
        'All four candidate release dates precede the conservative model bound; if identity is confirmed, '
        'the three affected papers cannot satisfy the declared post-bound criterion. '
        'Do not promote cited links or absent cache hits to publication-history verification.\n')
    print(json.dumps(counts,indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--history',type=Path,default=Path.home()/'Downloads/iclr_task3_baseline/data')
    p.add_argument('--upstream',type=Path,default=Path.home()/'Downloads/novelty-eval-main')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.root,a.history,a.upstream,a.output)
