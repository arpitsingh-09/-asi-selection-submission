"""Bounded DOI verification against Semantic Scholar; OpenAlex is not evidence."""
import argparse
import json
import time
import urllib.parse
import urllib.error
import re
from pathlib import Path

try:
    from .collect_known_group_candidates import (PAPER_API, SemanticScholarHTTPError,
                                                  request_json)
    from .known_groups import build_groups
except ImportError:
    from collect_known_group_candidates import PAPER_API, SemanticScholarHTTPError, request_json
    from known_groups import build_groups

FIELDS = 'paperId,title,publicationDate,references.paperId'
IDENTITY_FIELDS = FIELDS + ',externalIds'


def acl_identifier(doi):
    match = re.fullmatch(r'10\.18653/v1/(.+)', doi, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _doi_url(doi):
    return PAPER_API.format('DOI:' + urllib.parse.quote(doi, safe='')) + '?' + urllib.parse.urlencode({'fields': IDENTITY_FIELDS})


def _acl_url(identifier):
    return PAPER_API.format('ACL:' + urllib.parse.quote(identifier, safe='')) + '?' + urllib.parse.urlencode({'fields': IDENTITY_FIELDS})


def _title_search_url(title):
    return 'https://api.semanticscholar.org/graph/v1/paper/search?' + urllib.parse.urlencode({
        'query': title, 'limit': 10, 'fields': IDENTITY_FIELDS})


def _normal_doi(value):
    return (value or '').strip().lower().removeprefix('https://doi.org/').removeprefix('http://doi.org/')


def identity_matches(response, doi, acl_id):
    ext = response.get('externalIds') or {}
    doi_match = _normal_doi(ext.get('DOI')) == _normal_doi(doi)
    acl_match = any(str(value).strip().lower() == acl_id.lower()
                    for key, value in ext.items() if key.upper() in ('ACL', 'ACLANTHOLOGY', 'ACL_ANTHOLOGY')) if acl_id else False
    return doi_match or acl_match


def _raw_append(path, record):
    with path.open('a') as f:
        f.write(json.dumps(record, sort_keys=True) + '\n')


def _attempt(fetch, url, raw_path, doi, method):
    try:
        response = fetch(url)
    except SemanticScholarHTTPError as exc:
        _raw_append(raw_path, {'doi': doi, 'method': method, 'request_url': url,
                               'response_status': exc.status, 'error_body': exc.body})
        return None, exc
    except urllib.error.URLError as exc:
        return None, exc
    _raw_append(raw_path, {'doi': doi, 'method': method, 'request_url': url,
                           'response_status': 200, 'response': response})
    return response, None


def _status(failure):
    return getattr(failure, 'status', None)


def _error_body(failure):
    return getattr(failure, 'body', str(getattr(failure, 'reason', failure)))


def _exact_title_response(response, title, doi, acl_id):
    exact = [r for r in response.get('data', []) if r.get('title') == title
             and r.get('paperId') and identity_matches(r, doi, acl_id)]
    unique = {r['paperId']: r for r in exact}
    return next(iter(unique.values())) if len(unique) == 1 else None


def _doi_key(candidate):
    doi = candidate.get('doi')
    if not isinstance(doi, str) or not doi.strip():
        raise ValueError('candidate DOI required for exact lookup')
    return doi.strip().lower().removeprefix('https://doi.org/').removeprefix('http://doi.org/')


def collect(candidates_path, out_dir, seed_ids, *, fetch=request_json, sleep=time.sleep,
            max_candidates=5, delay_seconds=1.0):
    if len(seed_ids) != 3 or len(set(seed_ids)) != 3:
        raise ValueError('exactly three unique verified Semantic Scholar seed IDs required')
    payload = json.loads(Path(candidates_path).read_text())
    candidates = payload.get('candidates')
    if not isinstance(candidates, list):
        raise ValueError('candidate export must contain candidates list')
    if not 1 <= max_candidates <= 10:
        raise ValueError('max_candidates must be 1..10')
    candidates = candidates[:max_candidates]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_path, checkpoint_path = out / 'raw_semantic_scholar.jsonl', out / 'checkpoint.json'
    state = json.loads(checkpoint_path.read_text()) if checkpoint_path.exists() else {
        'completed_dois': [], 'verified_records': {}, 'last_error': None}
    state.setdefault('attempt_errors', [])
    state.setdefault('doi_not_found', {})
    completed = set(state.get('completed_dois', []))
    verified_records = state.get('verified_records', {})
    error = None
    for candidate in candidates:
        doi = _doi_key(candidate)
        if doi in completed:
            continue
        acl_id = acl_identifier(doi)
        prior = state.get('last_error') or {}
        # The failed DOI lookup in a persisted checkpoint is already evidence;
        # continue at ACL fallback rather than repeating that request.
        prior_doi_404 = state['doi_not_found'].get(doi)
        if prior_doi_404 is None and prior.get('doi') == doi and prior.get('status') == 404:
            prior_doi_404 = prior.get('body', '')
            state['doi_not_found'][doi] = prior_doi_404
        reused_checkpoint_404 = prior_doi_404 is not None
        if prior_doi_404 is not None:
            response, failure = None, SemanticScholarHTTPError(404, prior_doi_404)
            checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
        else:
            response, failure = _attempt(fetch, _doi_url(doi), raw_path, doi, 'DOI')
            if _status(failure) == 404:
                state['doi_not_found'][doi] = _error_body(failure)
                state['last_error'] = {'doi': doi, 'status': 404, 'body': _error_body(failure), 'stage': 'DOI'}
                checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
        method = 'DOI'
        if failure and _status(failure) == 404:
            if not acl_id:
                error = {'doi': doi, 'status': 404, 'body': failure.body, 'stage': 'DOI'}
                state['last_error'] = error; state['attempt_errors'].append(error)
                checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
                continue
            if reused_checkpoint_404:
                prior_raw = [json.loads(line) for line in raw_path.read_text().splitlines() if line.strip()] if raw_path.exists() else []
                has_doi_404 = any(r.get('doi') == doi and r.get('method') == 'DOI' and r.get('response_status') == 404 for r in prior_raw)
                if not has_doi_404:
                    _raw_append(raw_path, {'doi': doi, 'method': 'DOI', 'request_url': _doi_url(doi),
                                           'response_status': 404, 'error_body': failure.body,
                                           'recovered_from_checkpoint': True})
            response, failure = _attempt(fetch, _acl_url(acl_id), raw_path, doi, 'ACL')
            method = 'ACL'
            if failure and _status(failure) == 404:
                # Only use a title explicitly tied to a source record. Current
                # OpenAlex export has no title, so this branch will normally stay closed.
                title = candidate.get('title')
                if title and candidate.get('title_source_url'):
                    response, failure = _attempt(fetch, _title_search_url(title), raw_path, doi, 'EXACT_TITLE')
                    method = 'EXACT_TITLE'
                    if response:
                        response = _exact_title_response(response, title, doi, acl_id)
            elif failure and _status(failure) == 429:
                error = {'doi': doi, 'status': 429, 'body': _error_body(failure), 'stage': method}
                state['last_error'] = error; state['attempt_errors'].append(error)
                checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
                break
            elif response and not identity_matches(response, doi, acl_id):
                title = candidate.get('title')
                if title and candidate.get('title_source_url'):
                    search, search_failure = _attempt(fetch, _title_search_url(title), raw_path, doi, 'EXACT_TITLE')
                    if search_failure and _status(search_failure) == 429:
                        error = {'doi': doi, 'status': 429, 'body': _error_body(search_failure), 'stage': 'EXACT_TITLE'}
                        state['last_error'] = error; state['attempt_errors'].append(error)
                        checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
                        break
                    response = _exact_title_response(search, title, doi, acl_id) if search else None
                    if response:
                        method = 'EXACT_TITLE'
        elif failure:
            status = _status(failure) if _status(failure) is not None else 'NETWORK_ERROR'
            body = _error_body(failure)
            error = {'doi': doi, 'status': status, 'body': body, 'stage': 'DOI'}
            state['last_error'] = error; state['attempt_errors'].append(error)
            checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
            break
        if response is None:
            status = _status(failure) if _status(failure) is not None else 'IDENTITY_NOT_VERIFIED'
            body = _error_body(failure) if failure else 'no unique response matched the source identity'
            error = {'doi': doi, 'status': status, 'body': body, 'stage': method}
            state['last_error'] = error; state['attempt_errors'].append(error)
            checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
            continue
        if not identity_matches(response, doi, acl_id):
            error = {'doi': doi, 'status': 'IDENTITY_MISMATCH', 'body': response.get('externalIds'), 'stage': method}
            state['last_error'] = error; state['attempt_errors'].append(error)
            checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
            continue
        paper_id = response.get('paperId')
        if not paper_id:
            error = {'doi': doi, 'status': 'INVALID_RESPONSE', 'body': 'missing paperId'}
            state['last_error'] = error
            checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
            break
        reference_ids = sorted({r.get('paperId') for r in response.get('references') or [] if r.get('paperId')})
        record = {
            'input_doi': doi, 'paperId': paper_id, 'title': response.get('title'),
            'publicationDate': response.get('publicationDate'),
            'externalIds': response.get('externalIds') or {},
            'references': [{'paperId': rid} for rid in reference_ids],
            'source': 'Semantic Scholar',
            'source_url': 'https://www.semanticscholar.org/paper/' + paper_id,
            'request_url': _acl_url(acl_id) if method == 'ACL' else _doi_url(doi),
            'lookup_method': method,
            'verified_seed_ids': sorted(set(reference_ids) & set(seed_ids)),
            'all_three_seed_citations_verified': set(seed_ids).issubset(reference_ids),
        }
        verified_records[doi] = record
        completed.add(doi)
        state.update({'completed_dois': sorted(completed), 'verified_records': verified_records, 'last_error': None})
        checkpoint_path.write_text(json.dumps(state, indent=2) + '\n')
        sleep(delay_seconds)
    records = list(verified_records.values())
    group_result = build_groups(records, seed_ids)
    result = {
        'source': 'Semantic Scholar Graph API DOI lookups',
        'requested_candidate_count': len(candidates),
        'lookup_verified_count': len(records),
        'all_three_citations_verified_count': sum(r['all_three_seed_citations_verified'] for r in records),
        'blocked_count': len(candidates) - len(records),
        'last_error': error or state.get('last_error'),
        'citation_window_candidate_groups': group_result['groups'],
        'protocol_eligible_groups': [],
        'protocol_group_status': 'BLOCKED_PENDING_SOURCE_BOUND_REAL_AND_GENERATED_QUESTIONS',
        'excluded': group_result['excluded'],
        'records': records,
    }
    (out / 'verification_report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--candidates', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--seed-ids', nargs=3, required=True)
    p.add_argument('--max-candidates', type=int, default=5)
    a = p.parse_args()
    result = collect(a.candidates, a.out, a.seed_ids, max_candidates=a.max_candidates)
    print(json.dumps({k: result[k] for k in ('lookup_verified_count', 'all_three_citations_verified_count', 'blocked_count', 'last_error', 'protocol_eligible_groups')}, indent=2))
