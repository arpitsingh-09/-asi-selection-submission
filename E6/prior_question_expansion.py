"""Systematic expansion and source review of the E6 prior-question corpus.

Preserves the original extractor/prompt and archived corpora. No inference.
Reviews are assistant source comparisons, never represented as human reviews.
"""
import copy
import json
from pathlib import Path
import re

from prior_question_corpus import (ROOT, QUESTION, build_corpus, validate_corpus,
    paper_from_web_snapshot, predates, precise_date)
from researcher_approval import digest, file_digest, safe_path
from prepare_dataset import canonicalize_arxiv_id

SCHEMA = 'e6-reviewed-temporal-prior-question-corpus-v1'
CANDIDATE_LIMIT = 20


def source_frame(manifest, *, manifest_file_sha256):
    refs = {}
    for target in manifest['input_sets']:
        for row in target['references']:
            paper_id = row.get('paper_id','')
            if not re.fullmatch(r'\d{4}\.\d{4,5}(?:v\d+)?',paper_id): continue
            paper_id=canonicalize_arxiv_id(paper_id)
            ref=refs.setdefault(paper_id,dict(paper_id=paper_id,target_ids=set(),abstract_versions={}))
            ref['target_ids'].add(target['input_set_id'])
            abstract=row.get('abstract','')
            matches=[m[0] for m in QUESTION.finditer(abstract)
                if m.start()==0 or abstract[:m.start()].rstrip().endswith(('.', '!', '?', ':', '\n'))]
            ref['abstract_versions'][digest(abstract)]=matches
    rows=[]
    for pid,ref in sorted(refs.items()):
        rows.append(dict(paper_id=pid,target_ids=sorted(ref['target_ids']),
            cached_abstract_versions=[dict(sha256=k,screen_matches=v) for k,v in sorted(ref['abstract_versions'].items())]))
    candidates=[r['paper_id'] for r in rows if any(v['screen_matches'] for v in r['cached_abstract_versions'])]
    value=dict(schema_version='e6-systematic-prior-question-frame-v1',
        frozen_literature_manifest_file_sha256=manifest_file_sha256,frame=rows,
        candidate_ids=candidates,target_count=len(manifest['input_sets']),frame_paper_count=len(rows),
        rule='all unique arXiv references; fixed extractor screens every cached abstract version; retrieve every positive ID in ascending canonical order; no outcome-dependent selection')
    return dict(value,manifest_sha256=digest(value))


def review_key(question):
    return question['question_id']


def validate_reviews(base, reviews):
    by_id={r['question_id']:r for r in reviews}
    if len(by_id)!=len(reviews) or set(by_id)!={q['question_id'] for q in base['questions']}:
        raise ValueError('source review must cover every extracted question exactly once')
    sources={s['source_record_sha256']:s['paper'] for s in base['sources']}
    for question in base['questions']:
        review=by_id[question['question_id']]
        if (type(review.get('accepted')) is not bool or not review.get('reason')
                or review.get('review_method')!='assistant_source_comparison_not_human_review'
                or review.get('question_sha256')!=digest(question['question'])):
            raise ValueError('incomplete or misbound source review')
        evidence=review.get('source_evidence')
        if not isinstance(evidence,list) or not evidence: raise ValueError('source evidence is required')
        for item in evidence:
            source=sources.get(item.get('source_record_sha256'))
            if (not source or not isinstance(item.get('quote'),str) or not item['quote']
                    or item['quote'] not in source['abstract']):
                raise ValueError('review quote is not grounded in the original abstract')
        linked={s['source_record_sha256'] for s in question['source_records']}
        if not {e['source_record_sha256'] for e in evidence} <= linked:
            raise ValueError('review is linked to a different paper')
    return by_id


def build_reviewed_corpus(base, frame, reviews, selected_manifest, *, root=ROOT):
    validate_corpus(base,root=root)
    expected=source_frame(selected_manifest,manifest_file_sha256=frame['frozen_literature_manifest_file_sha256'])
    if expected!=frame: raise ValueError('source frame does not match frozen references')
    if {p['paper_id'].removeprefix('arxiv:') for p in base['input_records']} != set(frame['candidate_ids']):
        raise ValueError('retrieved records must cover exactly the systematic candidate frame')
    by_id=validate_reviews(base,reviews)
    accepted=[copy.deepcopy(q) for q in base['questions'] if by_id[q['question_id']]['accepted']]
    for q in accepted:
        q['validation_status']='verbatim_source_and_assistant_context_review_passed; not independent human validation'
        q['source_review_sha256']=digest(by_id[q['question_id']])
    cutoffs={}
    for target in selected_manifest['input_sets']:
        date=target['target'].get('published')
        precise_date(date) # No guessed target cutoff; missing/uncertain dates fail closed.
        native=target['target'].get('source_record',{}).get('published')
        if native!=date: raise ValueError('target cutoff differs from frozen native publication date')
        cutoffs[target['input_set_id']]=date
    eligibility={key:sum(any(predates(s['effective_date'],cutoff) for s in q['source_records'])
                        for q in accepted) for key,cutoff in sorted(cutoffs.items())}
    papers={s['paper_id'] for q in accepted for s in q['source_records']}
    value=dict(schema_version=SCHEMA,status='pending_final_decision20_researcher_approval',
        corpus_frozen=True,independently_sourced=True,approval_required=True,
        source_corpus=base,source_frame=frame,source_reviews=sorted(reviews,key=lambda r:r['question_id']),
        questions=accepted,question_count=len(accepted),candidate_limit=CANDIDATE_LIMIT,
        evaluation_cutoffs_by_input_set=dict(sorted(cutoffs.items())),
        statistics=dict(frame_papers=frame['frame_paper_count'],screen_positive_papers=len(frame['candidate_ids']),
            retrieved_papers=base['statistics']['papers_retrieved'],valid_question_papers=len(papers),
            extracted_questions=base['question_count'],accepted_questions=len(accepted),
            rejected_ambiguous_questions=base['question_count']-len(accepted),
            extraction_failures=base['statistics']['extraction_failures'],
            temporal_eligible_counts=eligibility,targets_with_eligible_questions=sum(n>0 for n in eligibility.values())),
        coverage=dict(domain='reference neighborhood of frozen 100-paper literature testbed',
            systematic=True,full_scientific_literature_coverage=False,
            date_coverage=base['statistics']['date_coverage']),
        limitations=['arXiv-only references; excludes non-arXiv and papers without explicit abstract questions',
            'cached abstracts screen discovery; independently retrieved versions can differ',
            'conservative source review rejects underspecified or rhetorical questions rather than rewriting them',
            'assistant contextual review is not independent human validation or semantic matcher validation',
            'lexical top-20 retrieval may miss paraphrases; Boolean semantic identity is always required',
            'source version date must predate each target publication cutoff; no date inferred for data-testbed questions'],
        expansion_pipeline_sha256=file_digest(Path(__file__)))
    return dict(value,manifest_sha256=digest(value))


def validate_reviewed_corpus(corpus, *, root=ROOT):
    if corpus.get('schema_version')!=SCHEMA or corpus.get('manifest_sha256')!=digest({k:v for k,v in corpus.items() if k!='manifest_sha256'}):
        raise ValueError('reviewed corpus schema/hash mismatch')
    path=safe_path(root,'E6/data/literature_selected_manifest_v1.json')
    if file_digest(path)!=corpus['source_frame']['frozen_literature_manifest_file_sha256']:
        raise ValueError('frozen literature selection changed')
    expected=build_reviewed_corpus(corpus['source_corpus'],corpus['source_frame'],corpus['source_reviews'],
                                   json.loads(path.read_text()),root=root)
    if expected!=corpus: raise ValueError('review, coverage, ordering or temporal cutoff replay mismatch')


def retrieve_candidates(corpus, question, *, evaluation_cutoff, candidate_limit=CANDIDATE_LIMIT, root=ROOT):
    """Apply temporal and source-review filters before deterministic top-20 truncation."""
    from prior_question_corpus import retrieve_candidates as original_retrieval
    validate_reviewed_corpus(corpus,root=root)
    if candidate_limit != CANDIDATE_LIMIT or type(candidate_limit) is not int:
        raise ValueError('approved deterministic candidate limit must be 20')
    base=corpus['source_corpus']
    ranked=original_retrieval(base,question,evaluation_cutoff=evaluation_cutoff,
                              candidate_limit=max(1,base['question_count']),root=root)
    accepted={q['question_id']:q for q in corpus['questions']}
    rows=[dict(accepted[r['question_id']],source_records=r['source_records'],lexical_jaccard=r['lexical_jaccard'])
          for r in ranked['candidates'] if r['question_id'] in accepted]
    return dict(candidates=rows[:CANDIDATE_LIMIT],eligible_question_count=len(rows),
        returned_count=min(CANDIDATE_LIMIT,len(rows)),evaluation_cutoff=evaluation_cutoff,
        ranking=ranked['ranking'],candidate_limit=CANDIDATE_LIMIT)


def make_temporal_matcher(corpus, *, evaluation_cutoff, candidate_limit=CANDIDATE_LIMIT,
                          identity_evaluator, identity_policy_id, root=ROOT):
    validate_reviewed_corpus(corpus,root=root);precise_date(evaluation_cutoff)
    if type(candidate_limit) is not int or candidate_limit!=CANDIDATE_LIMIT:
        raise ValueError('approved deterministic candidate limit must be 20')
    if not callable(identity_evaluator) or not isinstance(identity_policy_id,str) or not identity_policy_id.strip():
        raise ValueError('explicit semantic identity judgment is required')
    attempts=[]
    def match(question,reference_questions):
        if list(reference_questions)!=[r['question'] for r in corpus['questions']]:
            raise ValueError('reference questions differ from approved reviewed corpus')
        ranked=retrieve_candidates(corpus,question,evaluation_cutoff=evaluation_cutoff,root=root)
        audit=dict(ranked,judgments=[]);attempts.append(audit)
        if not ranked['candidates']:raise ValueError('no eligible historical corpus; rate unavailable')
        verdicts=[]
        for candidate in ranked['candidates']:
            try:
                verdict=identity_evaluator(question,candidate['question'])
                if type(verdict) is not bool:raise ValueError('semantic identity must be Boolean; similarity is not identity')
            except Exception as exc:
                audit['error']=str(exc);raise
            audit['judgments'].append(dict(question_id=candidate['question_id'],same_question=verdict))
            verdicts.append(verdict)
        return any(verdicts)
    match.policy_identity=dict(policy_id='e6-reviewed-temporal-prior-question-matcher-v1',
        corpus_sha256=corpus['manifest_sha256'],evaluation_cutoff=evaluation_cutoff,
        candidate_limit=CANDIDATE_LIMIT,identity_policy_id=identity_policy_id,
        retrieval='lexical_jaccard_stable_id; identity requires explicit semantic decision')
    match.attempts=attempts
    return match
