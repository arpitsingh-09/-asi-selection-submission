"""Offline temporal checks; no encoder imports or benchmark scoring."""
from datetime import datetime
import hashlib


def date(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timezone required')
    return dt


def validate_review(rows, benchmark, cutoff, release_bound, history=()):
    """Bind verified first-publication evidence to the frozen original text.

    A declared cutoff cannot precede the conservative pinned-weights bound.
    OpenReview dates alone do not establish first global publication.
    """
    byid = {r['forum_id']: r for r in benchmark}
    if len(byid) != len(benchmark) or len(rows) != len(byid) or {r['forum_id'] for r in rows} != set(byid):
        raise ValueError('eligibility review ID coverage')
    cutoff = date(cutoff)
    if cutoff < date(release_bound):
        raise ValueError('cutoff precedes pinned weights conservative bound')
    for row in rows:
        b = byid[row['forum_id']]
        expected = hashlib.sha256(b['abstract'].encode()).hexdigest()
        if row.get('abstract_sha256') != expected:
            raise ValueError('eligibility abstract binding mismatch')
        if row.get('first_publication_verified') is not True or not isinstance(row.get('source'), str) or not row['source'].strip():
            raise ValueError('first-publication eligibility not established')
        first = date(row['first_public_date'])
        if first <= cutoff or first > date(b['published']):
            raise ValueError('first-publication chronology inconsistent or not post-cutoff')
    earliest = min(date(row['first_public_date']) for row in rows)
    if any(date(row['published']) >= earliest for row in history):
        raise ValueError('history must precede every verified first publication')
