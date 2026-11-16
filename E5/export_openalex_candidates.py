"""Offline export of date-bounded OpenAlex candidates for manual lookup.

This preserves OpenAlex identifiers and never represents Semantic Scholar
identity/provenance as verified. Saved API responses are the only input.
"""
import argparse
import csv
import json
from datetime import date
from pathlib import Path

try:
    from .collect_openalex_known_groups import S2_IDS
    from .known_groups import twelve_months_after
except ImportError:
    from collect_openalex_known_groups import S2_IDS
    from known_groups import twelve_months_after


def candidate_rows(raw_path):
    pages = [json.loads(line) for line in Path(raw_path).read_text().splitlines() if line.strip()]
    by_seed = {sid: {} for sid in S2_IDS}
    seed_ids = {}
    for page in pages:
        sid = page.get('seed_s2_id')
        if sid not in by_seed:
            raise ValueError('unexpected seed ID in saved OpenAlex response')
        seed_id = page.get('seed_openalex_id')
        if not seed_id:
            raise ValueError('missing OpenAlex seed ID')
        seed_ids[sid] = seed_id
        for paper in page.get('response', {}).get('results', []):
            if seed_id in paper.get('referenced_works', []):
                by_seed[sid][paper['id']] = paper
    if set(seed_ids) != set(S2_IDS):
        raise ValueError('saved responses must cover all three seeds')
    common = set.intersection(*(set(by_seed[sid]) for sid in S2_IDS))
    dated = []
    for pid in common:
        # Reconcile duplicate appearances across seed response pages.
        records = [by_seed[sid][pid] for sid in S2_IDS]
        canonical = records[0]
        if any(r.get('publication_date') != canonical.get('publication_date') for r in records):
            raise ValueError('conflicting publication dates for ' + pid)
        try:
            d = date.fromisoformat(canonical['publication_date'])
        except (KeyError, TypeError, ValueError):
            continue
        dated.append((d, pid, canonical))
    dated.sort(key=lambda x: (x[0], x[1]))
    window = None
    for i, (start, _, _) in enumerate(dated):
        group = [item for item in dated[i:] if item[0] <= twelve_months_after(start)]
        if len(group) >= 5:
            window = group
            break
    if window is None:
        return []
    seed_openalex_ids = sorted(set(seed_ids.values()))
    output = []
    for d, pid, paper in window:
        doi = paper.get('doi')
        output.append({
            'title': paper.get('title'),
            'title_status': 'AVAILABLE_IN_SAVED_RESPONSE' if paper.get('title') else 'NOT_INCLUDED_IN_SAVED_RESPONSE',
            'doi': doi,
            'arxiv_id': paper.get('arxiv_id'),
            'publication_date': d.isoformat(),
            'openalex_id': pid,
            'openalex_source_url': pid,
            'cited_seed_openalex_ids': seed_openalex_ids,
            'corresponding_seed_semantic_scholar_ids': list(S2_IDS),
            'semantic_scholar_lookup_url': 'https://www.semanticscholar.org/search?q=' + (doi or pid),
            'semantic_scholar_status': 'UNVERIFIED',
        })
    return output


def export(raw_path, out_dir):
    rows = candidate_rows(raw_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'candidates.json').write_text(json.dumps({
        'source': 'saved OpenAlex API responses; no network access',
        'protocol_eligibility': 'supplementary only; Semantic Scholar provenance remains required',
        'candidate_count': len(rows),
        'candidates': rows,
    }, indent=2) + '\n')
    if rows:
        with (out / 'candidates.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    print(f'Exported {len(export(args.raw, args.out))} supplementary candidates')
