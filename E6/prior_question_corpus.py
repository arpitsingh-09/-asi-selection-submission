"""Source-bound, temporal prior-question corpus; no model inference.

Reuses E6 source adapters, canonical IDs, hashing and exclusive output writes.
ArXiv API transport is optional; saved arXiv web-tool snapshots are also accepted.
Only verbatim abstract questions qualify; implicit objectives are never invented.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import json
from pathlib import Path
import re

from citation_sources import ArxivApiAdapter, JsonFileCache
from prepare_dataset import canonicalize_arxiv_id
from researcher_approval import ROOT, digest, file_digest, safe_path
from prepare_already_asked_corpus import write_exclusive

PROMPT = ROOT / 'prompts/e6/17_prior_question_verbatim.txt'
SCHEMA = 'e6-temporal-prior-question-corpus-v1'
QUESTION = re.compile(r'(?<!\S)(?:What|Why|When|Where|Which|Who|How|Can|Could|Should|Would|Will|Do|Does|Did|Is|Are|Was|Were|Has|Have|To what extent)\b[^.!?]*\?', re.I)


def precise_date(value):
    """Exact day or timezone-aware timestamp; never infer missing month/day/zone."""
    if not isinstance(value, str): raise ValueError('missing source/cutoff date')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return datetime.strptime(value, '%Y-%m-%d').replace(tzinfo=timezone.utc), 'day'
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
        raise ValueError('uncertain or timezone-free date')
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc), 'instant'


def predates(source_date, cutoff):
    source, precision = precise_date(source_date)
    limit, _ = precise_date(cutoff)
    # A day-only date denotes an interval: exclude the whole uncertain boundary day.
    return source + timedelta(days=1) <= limit if precision == 'day' else source < limit


def paper_from_web_snapshot(path, *, source_url, retrieved_at_utc, root=ROOT):
    """Parse observed arXiv page text, retaining immutable web-tool evidence."""
    path = Path(path)
    raw = path.read_text()
    lines = [re.sub(r'^L\d+: ?', '', x) for x in raw.splitlines() if re.match(r'^L\d+:', x)]
    text = '\n'.join(lines)
    title = re.search(r'^# Title:(.+)$', text, re.M)
    abstract = re.search(r'> Abstract:(.*?)(?=\n(?:Comments:|Subjects:|Cite as:|##))', text, re.S)
    history = []
    for version, date in re.findall(r'\[v(\d+)\].*?((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} UTC)', text):
        history.append((int(version), parsedate_to_datetime(date).astimezone(timezone.utc).isoformat()))
    if not title or not abstract or not history: raise ValueError('source lacks title/abstract/exact version history')
    match = re.fullmatch(r'https://arxiv\.org/abs/([^/?#]+)', source_url)
    if not match: raise ValueError('expected canonical arXiv source URL')
    paper_id = canonicalize_arxiv_id(match[1])
    if f'[{paper_id}]' not in raw.splitlines()[0]: raise ValueError('source identifier mismatch')
    current = re.search(r'or .*?arXiv:' + re.escape(paper_id) + r'v(\d+)', text)
    if not current: raise ValueError('observed abstract version is uncertain')
    version = int(current[1])
    dates = dict(history)
    if version not in dates or 1 not in dates: raise ValueError('exact source version date missing')
    precise_date(retrieved_at_utc)
    relative = str(path.resolve().relative_to(Path(root).resolve()))
    return dict(paper_id='arxiv:' + paper_id, versioned_id=paper_id + 'v' + str(version),
        title=title[1].strip(), submission_date=dates[1], effective_date=dates[version],
        source_url=source_url, version_url='https://arxiv.org/abs/' + paper_id + 'v' + str(version),
        abstract=abstract[1].strip(), retrieved_at_utc=retrieved_at_utc,
        provenance=dict(retrieval_method='web_tool_source_snapshot', source_path=relative,
                        source_file_sha256=file_digest(path)), validation_status='source_snapshot_verified')


def paper_from_api(response, *, root=ROOT):
    """Normalize existing ArxivApiAdapter output, preserving its raw Atom body."""
    import xml.etree.ElementTree as ET
    body = response['raw_body']
    nodes = ET.fromstring(body).findall('{http://www.w3.org/2005/Atom}entry')
    canonical = response['canonical_arxiv_id']
    nodes = [n for n in nodes if canonicalize_arxiv_id(n.findtext('{http://www.w3.org/2005/Atom}id', '').rsplit('/', 1)[-1]) == canonical]
    if len(nodes) != 1: raise ValueError('arXiv response is not an exact unique source')
    node = nodes[0]
    def field(name): return node.findtext('{http://www.w3.org/2005/Atom}' + name, '').strip()
    published, updated = field('published'), field('updated')
    precise_date(published); precise_date(updated)
    versioned = field('id').rsplit('/', 1)[-1]
    if not re.search(r'v\d+$', versioned): raise ValueError('arXiv abstract version is missing')
    return dict(paper_id='arxiv:' + canonical, versioned_id=versioned, title=field('title'),
        submission_date=published, effective_date=updated, source_url='https://arxiv.org/abs/' + canonical,
        version_url='https://arxiv.org/abs/' + versioned, abstract=field('summary'),
        retrieved_at_utc=response['retrieved_at_utc'],
        provenance=dict(retrieval_method='arxiv_api', raw_body=body, raw_body_sha256=digest(body),
                        request_url=response['request_url']), validation_status='source_atom_verified')


def verify_paper(paper, *, root=ROOT):
    for field in ('paper_id','versioned_id','title','abstract','source_url','retrieved_at_utc'):
        if not isinstance(paper.get(field), str) or not paper[field].strip(): raise ValueError('missing paper ' + field)
    precise_date(paper['submission_date']); precise_date(paper['effective_date']); precise_date(paper['retrieved_at_utc'])
    submitted, _ = precise_date(paper['submission_date']); effective, _ = precise_date(paper['effective_date'])
    if effective < submitted: raise ValueError('version date precedes submission')
    retrieved, _ = precise_date(paper['retrieved_at_utc'])
    if effective > retrieved: raise ValueError('source version postdates retrieval')
    prov = paper['provenance']
    if prov['retrieval_method'] == 'web_tool_source_snapshot':
        path = safe_path(root, prov['source_path'])
        if file_digest(path) != prov['source_file_sha256']: raise ValueError('source snapshot hash mismatch')
        expected = paper_from_web_snapshot(path, source_url=paper['source_url'],
                    retrieved_at_utc=paper['retrieved_at_utc'], root=root)
    elif prov['retrieval_method'] == 'arxiv_api':
        if digest(prov['raw_body']) != prov['raw_body_sha256']: raise ValueError('raw Atom hash mismatch')
        expected = paper_from_api(dict(raw_body=prov['raw_body'], canonical_arxiv_id=paper['paper_id'].removeprefix('arxiv:'),
            retrieved_at_utc=paper['retrieved_at_utc'], request_url=prov['request_url']))
    else: raise ValueError('unverified retrieval method')
    if expected != paper: raise ValueError('paper metadata differs from original source evidence')


def extract_questions(paper):
    text = paper['abstract']
    rendered = PROMPT.read_text().replace('{{SOURCE_ABSTRACT}}', text)
    matches = [dict(question=m[0], start=m.start(), end=m.end()) for m in QUESTION.finditer(text)
               if m.start() == 0 or text[:m.start()].rstrip().endswith(('.', '!', '?', ':', '\n'))]
    return dict(method='verbatim_interrogative_v1_no_model', prompt_version='e6-prior-question-verbatim-v1',
                prompt_path=str(PROMPT.relative_to(ROOT)), prompt_file_sha256=file_digest(PROMPT),
                rendered_input_sha256=digest(rendered), questions=matches,
                status='extracted' if matches else 'no_explicit_question_in_abstract')


def build_corpus(papers, *, root=ROOT, retrieval_failures=()):
    """Deterministic deduplication; rejected sources and extraction failures retained."""
    def order_key(p):
        try: date = precise_date(p.get('effective_date'))[0].isoformat()
        except ValueError: date = '9999-invalid-date'
        return p.get('paper_id',''), date, digest(p)
    ordered = sorted(list(papers), key=order_key)
    accepted, rejected, sources, seen, grouped = [], [], [], set(), {}
    for paper in ordered:
        try:
            verify_paper(paper, root=root)
            if paper['paper_id'] in seen: raise ValueError('duplicate_paper; earliest observed version retained')
            seen.add(paper['paper_id'])
            extraction = extract_questions(paper)
            source = dict(paper=paper, extraction=extraction, source_record_sha256=digest(paper))
            sources.append(source)
            if not extraction['questions']: raise ValueError('no_explicit_question_in_abstract')
            accepted.append(paper['paper_id'])
            for question in extraction['questions']:
                # Group only text-equivalent questions; retain all source spans.
                key = ' '.join(question['question'].split()).casefold()
                provenance = dict(source_record_sha256=digest(paper), paper_id=paper['paper_id'],
                                  effective_date=paper['effective_date'], source_question=question)
                grouped.setdefault(key, []).append(provenance)
        except (ValueError, KeyError, OSError, TypeError) as exc:
            rejected.append(dict(paper_id=paper.get('paper_id'), record_sha256=digest(paper), reason=str(exc)))
    questions = []
    for key in sorted(grouped):
        links = sorted(grouped[key], key=lambda r: (r['paper_id'], r['source_question']['start']))
        value = dict(question=links[0]['source_question']['question'], source_records=links,
                     validation_status='verbatim_source_verified; semantic_review_not_performed')
        questions.append(dict(value, question_id='pq-' + digest(value)[:24]))
    dates = sorted(p['paper']['effective_date'] for p in sources if p['paper']['paper_id'] in accepted)
    value = dict(schema_version=SCHEMA, status='provisional_pending_decision20_approval',
        corpus_frozen=True, independently_sourced=True, approval_required=True,
        input_records=ordered, sources=sources, questions=questions, question_count=len(questions),
        pipeline_file_sha256=file_digest(Path(__file__)),
        statistics=dict(papers_retrieved=len(ordered), papers_accepted=len(accepted), papers_rejected=len(rejected),
                        unique_papers=len(seen), extraction_failures=sum(r['reason']=='no_explicit_question_in_abstract' for r in rejected),
                        date_coverage=[dates[0],dates[-1]] if dates else []),
        rejections=rejected, retrieval_failures=list(retrieval_failures),
        limitations=['small convenience/source-discovery sample; not representative',
                    'abstract-only explicit verbatim questions; implicit objectives excluded',
                    'latest observed version date governs temporal eligibility, not original submission',
                    'lexical candidate retrieval may miss paraphrases; identity always needs semantic judgment',
                    'source grounding is mechanical, not independent human semantic validation',
                    'rhetorical or underspecified explicit questions require semantic review before use'],
        extraction_prompt=dict(path=str(PROMPT.relative_to(ROOT)), file_sha256=file_digest(PROMPT)))
    return dict(value, manifest_sha256=digest(value))


def validate_corpus(corpus, *, root=ROOT):
    if corpus.get('schema_version') != SCHEMA or corpus.get('manifest_sha256') != digest({k:v for k,v in corpus.items() if k!='manifest_sha256'}):
        raise ValueError('corpus schema/content hash mismatch')
    if file_digest(safe_path(root, corpus['extraction_prompt']['path'])) != corpus['extraction_prompt']['file_sha256']:
        raise ValueError('extraction prompt hash mismatch')
    lookup = {}
    for source in corpus['sources']:
        paper = source['paper']; verify_paper(paper, root=root)
        if source['source_record_sha256'] != digest(paper) or source['extraction'] != extract_questions(paper):
            raise ValueError('source/extraction provenance mismatch')
        lookup[digest(paper)] = source
    for question in corpus['questions']:
        if not question['source_records']: raise ValueError('question lacks source links')
        for link in question['source_records']:
            source = lookup[link['source_record_sha256']]; paper=source['paper']; span=link['source_question']
            if (span not in source['extraction']['questions'] or paper['abstract'][span['start']:span['end']] != span['question']
                    or link['paper_id'] != paper['paper_id'] or link['effective_date'] != paper['effective_date']
                    or ' '.join(span['question'].split()).casefold() != ' '.join(question['question'].split()).casefold()):
                raise ValueError('question or temporal provenance mismatch')
    if corpus['question_count'] != len(corpus['questions']): raise ValueError('question count mismatch')
    if corpus != build_corpus(corpus['input_records'], root=root, retrieval_failures=corpus['retrieval_failures']):
        raise ValueError('corpus ordering, deduplication, counts or provenance differs from deterministic replay')


def retrieve_candidates(corpus, question, *, evaluation_cutoff, candidate_limit, root=ROOT):
    validate_corpus(corpus, root=root)
    precise_date(evaluation_cutoff)
    if type(candidate_limit) is not int or candidate_limit < 1: raise ValueError('explicit positive candidate limit required')
    if not isinstance(question, str) or not question.strip(): raise ValueError('nonempty question required')
    query = set(re.findall(r'\w+', question.casefold()))
    candidates=[]
    for row in corpus['questions']:
        eligible=[s for s in row['source_records'] if predates(s['effective_date'], evaluation_cutoff)]
        if not eligible: continue
        words=set(re.findall(r'\w+',row['question'].casefold()))
        score=len(query & words)/len(query | words) if query | words else 0
        candidates.append(dict(row, source_records=eligible, lexical_jaccard=score))
    candidates.sort(key=lambda r:(-r['lexical_jaccard'],r['question_id']))
    return dict(candidates=candidates[:candidate_limit], eligible_question_count=len(candidates),
                returned_count=min(candidate_limit,len(candidates)), evaluation_cutoff=evaluation_cutoff,
                ranking='token-set Jaccard descending, stable question_id tie-break; not identity',
                candidate_limit=candidate_limit)


def make_temporal_matcher(corpus, *, evaluation_cutoff, candidate_limit, identity_evaluator,
                          identity_policy_id, root=ROOT):
    validate_corpus(corpus, root=root); precise_date(evaluation_cutoff)
    if type(candidate_limit) is not int or candidate_limit < 1: raise ValueError('explicit positive candidate limit required')
    if not callable(identity_evaluator) or not isinstance(identity_policy_id, str) or not identity_policy_id.strip(): raise ValueError('explicit semantic identity evaluator/policy required')
    attempts=[]
    def match(question, reference_questions):
        if list(reference_questions) != [r['question'] for r in corpus['questions']]: raise ValueError('reference corpus differs from bound corpus')
        retrieved=retrieve_candidates(corpus, question, evaluation_cutoff=evaluation_cutoff,candidate_limit=candidate_limit,root=root)
        audit=dict(retrieved, judgments=[]);attempts.append(audit)
        if not retrieved['candidates']: raise ValueError('no eligible historical corpus; unavailable, not a zero rate')
        decisions=[]
        for candidate in retrieved['candidates']:
            try:
                verdict=identity_evaluator(question,candidate['question'])
                if type(verdict) is not bool: raise ValueError('semantic identity must be Boolean; no similarity threshold substitution')
            except Exception as exc:
                audit['error'] = str(exc)
                raise
            audit['judgments'].append(dict(question_id=candidate['question_id'],same_question=verdict))
            decisions.append(verdict)
        return any(decisions)
    match.policy_identity=dict(policy_id='e6-temporal-prior-question-matcher-v1', corpus_sha256=corpus['manifest_sha256'],
        evaluation_cutoff=evaluation_cutoff,candidate_limit=candidate_limit,identity_policy_id=identity_policy_id,
        retrieval='lexical_jaccard_stable_id; identity requires explicit semantic decision')
    match.attempts=attempts
    return match


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,help='saved source index with exact retrieval URLs/timestamps')
    parser.add_argument('--arxiv-id',action='append',default=[])
    parser.add_argument('--cache-dir',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv); papers=[]; failures=[]
    if args.sources:
        index=json.loads(args.sources.read_text())
        failures.extend(index.get('retrieval_failures',[]))
        for source in index['sources']:
            try:
                papers.append(paper_from_web_snapshot(safe_path(ROOT,source['path']),source_url=source['source_url'],retrieved_at_utc=source['retrieved_at_utc']))
            except (ValueError, OSError, KeyError) as exc:
                papers.append(dict(paper_id=source.get('source_url','unknown'), normalization_error=str(exc), source_index_record=source))
    if args.arxiv_id:
        adapter=ArxivApiAdapter(cache=JsonFileCache(args.cache_dir) if args.cache_dir else None,max_attempts=1,timeout_seconds=15)
        for paper_id in sorted(set(args.arxiv_id)):
            try: papers.append(paper_from_api(adapter.get_paper(paper_id)))
            except Exception as exc: failures.append(dict(paper_id=paper_id,error=str(exc)))
    corpus=build_corpus(papers,retrieval_failures=failures);validate_corpus(corpus)
    write_exclusive(args.output,corpus)
    print(json.dumps(dict(output=str(args.output),**corpus['statistics'],question_count=corpus['question_count'],manifest_sha256=corpus['manifest_sha256'])))
    return 0 if corpus['question_count'] else 2


if __name__=='__main__': raise SystemExit(main())
