"""Build and validate a blank independent-review packet for the two I1 candidates.

Candidate contrasts in this packet are unreviewed text proposals, never labels.
The packet is not a frozen evaluation cohort and cannot authorize scoring.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


DECISIONS = ('YES', 'NO', 'UNCERTAIN')
REVIEW_FIELDS = (
    'reviewer_code', 'review_date_utc', 'question_input_relationship_valid',
    'paraphrase_equivalent', 'near_miss_distinct', 'same_topic_decoy_valid',
    'evidence_references_json', 'rationale',
)

LABEL_FIELDS = ('label_id', 'paper_id', 'factor', 'value', 'definition', 'observed_at',
                'source_url', 'source_revision_id', 'source_locator', 'source_quote',
                'public_at', 'public_date_basis', 'verification_status',
                'verifier_code', 'verified_at')


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def _iso_utc(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (AttributeError, ValueError):
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed)


def validate_packet(packet):
    if packet.get('schema') != 'M-I1-independent-review-packet-v1':
        raise ValueError('unsupported I1 review packet schema')
    candidates = packet.get('candidates')
    if not isinstance(candidates, list) or len(candidates) != 2:
        raise ValueError('the minimum I1 packet must contain two candidate questions')
    ids = set()
    for candidate in candidates:
        cid = candidate.get('candidate_id')
        if not cid or cid in ids:
            raise ValueError('missing or duplicate candidate ID')
        ids.add(cid)
        if not candidate.get('original_question') or not candidate.get('question_input_papers'):
            raise ValueError('original question and linked input papers are required')
        if not candidate.get('paraphrase', {}).get('text') or not candidate.get('near_miss', {}).get('text'):
            raise ValueError('unreviewed paraphrase and near-miss proposals are required')
        if candidate['paraphrase'].get('status') != 'UNREVIEWED_TEXT_PROPOSAL' or candidate['near_miss'].get('status') != 'UNREVIEWED_TEXT_PROPOSAL':
            raise ValueError('candidate contrasts must remain explicitly unreviewed')
        if not candidate.get('shuffled_control_papers') or not candidate.get('same_topic_decoy', {}).get('papers'):
            raise ValueError('shuffled controls and proposed decoy papers are required')
        for paper in candidate['question_input_papers'] + candidate['shuffled_control_papers'] + candidate['same_topic_decoy']['papers']:
            if not paper.get('paper_id') or not paper.get('url'):
                raise ValueError('each paper needs an exact source ID and URL')
    return True


def build_packet(root='.', out='M/data/i1_public_evidence_v1/i1_review_packet_v1'):
    root = Path(root).resolve()
    source_dir = root / 'M/data/i1_public_evidence_v1'
    evidence = json.loads((source_dir / 'manifest.json').read_text())
    if evidence.get('registered_test_target') != 'I1' or evidence.get('evaluation_executed') is not False:
        raise ValueError('source evidence manifest is not an unevaluated I1 manifest')
    candidate_path = source_dir / evidence['candidate_records_file']
    source_path = source_dir / evidence['public_source_checks']['sources_file']
    if _sha(candidate_path) != evidence['candidate_records_sha256']:
        raise ValueError('candidate evidence manifest hash mismatch')
    if _sha(source_path) != evidence['public_source_checks']['sources_sha256']:
        raise ValueError('verified source manifest hash mismatch')
    candidate_records = {x['candidate_id']: x for x in _read_jsonl(candidate_path)}
    generated_path = root / 'M/data/generated_questions_v1/generated_questions.jsonl'
    generated = {x['question_id']: x for x in _read_jsonl(generated_path)}
    verified_sources = {x['paper_id']: x for x in _read_jsonl(source_path)}
    decoy_path = root / 'M/data/generated_questions_v1/decoy_questions_v2.jsonl'
    decoy_records = {x['question_id']: x for x in _read_jsonl(decoy_path)}
    source_hash = evidence['frozen_input_hashes']['M/data/generated_questions_v1/generated_questions.jsonl']
    if _sha(generated_path) != source_hash:
        raise ValueError('generated-question source differs from evidence manifest')

    contrast_proposals = {
        'mgen-v1-01': {
            'paraphrase': 'In what ways do TiG-BEV and TiGDistill-BEV differ in how they address computer vision?',
            'near_miss': 'Which of TiG-BEV and TiGDistill-BEV achieves stronger 3D object-detection performance on nuScenes?',
        },
        'mgen-v1-02': {
            'paraphrase': 'In what ways do the two cited approaches differ in their computer-vision treatment of myocardial infarction?',
            'near_miss': 'Which method more accurately identifies myocardial infarction in delayed-enhancement cardiac MRI?',
        },
    }
    candidates = []
    for cid in evidence['cohort_selection']['candidate_ids']:
        candidate_record = candidate_records[cid]
        question = generated[cid]
        controls = question['controls']
        proposal = contrast_proposals[cid]
        def paper(pid):
            if pid not in verified_sources:
                raise ValueError('source ID absent from evidence manifest: ' + pid)
            row = verified_sources[pid]
            result = {k: row[k] for k in ('paper_id', 'title', 'published_at', 'version_updated_at', 'status')}
            result['url'] = row['primary_source_url']
            result['exact_source_id'] = row.get('versioned_arxiv_id', row['paper_id'])
            return result
        original_ids = candidate_record['question_input_links']['R_generator_inputs']
        shuffled_ids = candidate_record['question_input_links']['shuffled_input_ids']
        decoy = controls['same_topic_decoy']
        decoy_ids = decoy['source_ids']
        decoy_v2 = decoy_records.get(cid, {})
        candidates.append({
            'candidate_id': cid,
            'question_id': cid,
            'candidate_status': 'REJECTED_FOR_CURRENT_I1_EVALUATION_PENDING_REVIEW_AND_MODEL_EVIDENCE',
            'original_question': question['question'],
            'question_generated_at': question['generated_at'],
            'question_input_relationship': {
                'status': 'GENERATOR_INPUT_LINK_RECORDED_NOT_INDEPENDENTLY_VALIDATED',
                'input_papers': [paper(pid) for pid in original_ids],
            },
            'question_input_papers': [paper(pid) for pid in original_ids],
            'paraphrase': {'text': proposal['paraphrase'], 'status': 'UNREVIEWED_TEXT_PROPOSAL'},
            'near_miss': {'text': proposal['near_miss'], 'status': 'UNREVIEWED_TEXT_PROPOSAL'},
            'shuffled_control_papers': [paper(pid) for pid in shuffled_ids],
            'same_topic_decoy': {
                'question': decoy['question'],
                'status': 'CATEGORY_MATCH_ONLY_PENDING_INDEPENDENT_SEMANTIC_REVIEW',
                'papers': [paper(pid) for pid in decoy_ids],
                'additional_existing_proposal': decoy_v2.get('decoy'),
                'additional_existing_proposal_status': decoy_v2.get('status', 'NOT_AVAILABLE'),
            },
            'input_evidence_file': 'M/data/generated_questions_v1/generated_questions.jsonl',
            'input_evidence_sha256': source_hash,
            'human_judgments': None,
        })
    packet = {
        'schema': 'M-I1-independent-review-packet-v1',
        'purpose': 'independent source/question/contrast/control review only; not an evaluation cohort or result',
        'source_evidence_manifest': 'M/data/i1_public_evidence_v1/manifest.json',
        'source_evidence_manifest_sha256': _sha(source_dir / 'manifest.json'),
        'protocol': 'M/PREREG.md',
        'candidate_count': len(candidates),
        'reviewer_slots': 2,
        'reviewer_fields': list(REVIEW_FIELDS),
        'decision_values': list(DECISIONS),
        'review_instructions': [
            'Review independently; do not coordinate or copy another reviewer.',
            'The paraphrase and near-miss are unreviewed text proposals, not labels or claims.',
            'Cite exact source URLs and a locator plus supporting excerpt for each decision.',
            'Use UNCERTAIN when source evidence does not support a definite decision.',
            'A completed packet alone does not satisfy Q-head, normalization, cohort-lock, or evaluation authorization gates.',
        ],
        'candidates': candidates,
    }
    validate_packet(packet)
    out = Path(out)
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=False)
    packet_path = out / 'packet.json'
    with packet_path.open('x') as f:
        json.dump(packet, f, indent=2, ensure_ascii=False)
        f.write('\n')
    packet_hash = _sha(packet_path)
    fields = ('candidate_id', 'question_id', 'packet_sha256', 'reviewer_slot', *REVIEW_FIELDS)
    for slot in ('reviewer_1_template.csv', 'reviewer_2_template.csv'):
        with (out / slot).open('x', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for candidate in candidates:
                writer.writerow({'candidate_id': candidate['candidate_id'], 'question_id': candidate['question_id'],
                                 'packet_sha256': packet_hash,
                                 'reviewer_slot': '1' if slot.startswith('reviewer_1') else '2',
                                 **{name: '' for name in REVIEW_FIELDS}})
    with (out / 'dated_quality_labels_template.jsonl').open('x') as f:
        f.write(json.dumps({'schema': 'M-dated-quality-label-source-v1',
            'required_fields': list(LABEL_FIELDS),
            'instructions': 'One exact source-bound observation per row. Supply source URLs, stable revision, locator and quote; public_at must establish when this exact value became public. verifier fields must be completed by a human source checker. Do not infer dates or create labels from generated text.'}, ensure_ascii=False) + '\n')
    return out


def import_reviews(sheets, packet_path, out):
    packet = json.loads(Path(packet_path).read_text())
    validate_packet(packet)
    packet_hash = _sha(packet_path)
    candidates = {x['candidate_id']: x for x in packet['candidates']}
    if isinstance(sheets, (str, Path)):
        sheets = [sheets]
    rows = []
    for sheet in sheets:
        with Path(sheet).open(newline='') as f:
            rows.extend(csv.DictReader(f))
    grouped = {cid: [] for cid in candidates}
    for row in rows:
        cid = row.get('candidate_id', '')
        if cid not in candidates or row.get('question_id') != cid:
            raise ValueError('unknown candidate or question identity mismatch')
        if row.get('packet_sha256') != packet_hash:
            raise ValueError('review packet identity/hash mismatch')
        if row.get('reviewer_slot') not in ('1', '2'):
            raise ValueError('reviewer slot must be 1 or 2')
        grouped[cid].append(row)
    accepted = []
    for cid, reviews in grouped.items():
        if len(reviews) != 2 or {r['reviewer_slot'] for r in reviews} != {'1', '2'}:
            raise ValueError('exactly two independent reviewer slots required per candidate')
        if len({r.get('reviewer_code', '').strip() for r in reviews}) != 2 or not all(r.get('reviewer_code', '').strip() for r in reviews):
            raise ValueError('two distinct reviewer codes required per candidate')
        normalized = []
        for row in reviews:
            if not _iso_utc(row.get('review_date_utc', '')):
                raise ValueError('review date must be timezone-aware UTC ISO-8601')
            decisions = {field: row.get(field, '') for field in ('question_input_relationship_valid', 'paraphrase_equivalent', 'near_miss_distinct', 'same_topic_decoy_valid')}
            if any(value not in DECISIONS for value in decisions.values()):
                raise ValueError('all independent review decisions must be explicit')
            try:
                refs = json.loads(row.get('evidence_references_json', ''))
            except json.JSONDecodeError as exc:
                raise ValueError('evidence references must be a JSON list') from exc
            if not isinstance(refs, list) or not refs or any(not all(isinstance(ref.get(k), str) and ref[k].strip() for k in ('source_id', 'url', 'locator', 'quote')) for ref in refs if isinstance(ref, dict)) or any(not isinstance(ref, dict) for ref in refs):
                raise ValueError('each evidence reference needs source_id, url, locator, and quote')
            if not row.get('rationale', '').strip():
                raise ValueError('review rationale is required')
            normalized.append({'reviewer_code': row['reviewer_code'].strip(), 'review_date_utc': row['review_date_utc'],
                               'decisions': decisions, 'evidence_references': refs, 'rationale': row['rationale'].strip()})
        same = normalized[0]['decisions'] == normalized[1]['decisions']
        all_yes = all(value == 'YES' for value in normalized[0]['decisions'].values()) and same
        accepted.append({'candidate_id': cid, 'reviewers': normalized,
                         'review_status': 'AGREEMENT' if same else 'DISAGREEMENT_UNRESOLVED',
                         'review_gate_passed': all_yes,
                         'evaluation_eligible': False,
                         'remaining_gates': ['fitted Q heads and frozen normalization', 'new prospective cohort/model lock and authorization']})
    out = Path(out)
    with out.open('x') as f:
        for record in accepted:
            f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + '\n')
    return len(accepted)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    build = sub.add_parser('build')
    build.add_argument('--root', default='.')
    build.add_argument('--out', default='M/data/i1_public_evidence_v1/i1_review_packet_v1')
    imp = sub.add_parser('import-reviews')
    imp.add_argument('--sheet', required=True, action='append', help='supply both independently completed sheets')
    imp.add_argument('--packet', required=True)
    imp.add_argument('--out', required=True)
    args = parser.parse_args()
    result = build_packet(args.root, args.out) if args.command == 'build' else import_reviews(args.sheet, args.packet, args.out)
    print(result)


if __name__ == '__main__':
    main()
