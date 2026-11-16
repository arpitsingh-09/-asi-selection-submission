"""Provenance-checked links; separate per-test eligibility without common-cohort forcing."""
from .evidence import verify_assertion
from .schema import date
from .evaluation import TESTS,CONTROLS


def verified_value(a):
    verify_assertion(a);return a['value']


def link_question_outcome(question,outcome):
    """Fail closed. Exact text, paper identity, dates and references need source proofs."""
    from .ingestion import verify_outcome
    verify_outcome(outcome)
    fields={k:verified_value(question[k+'_evidence']) for k in
            ('paper_id','question','published','available_at','input_paper_ids')}
    if fields['paper_id']!=outcome['paper_id']:raise ValueError('outcome belongs to another paper')
    if not isinstance(fields['question'],str) or not fields['question'].strip():raise ValueError('empty question')
    if not isinstance(fields['input_paper_ids'],list):raise ValueError('source references must be explicit')
    if date(fields['available_at'])<date(fields['published']):raise ValueError('invalid paper/version dates')
    when=outcome['observed_at']
    if when is None:raise ValueError('exact outcome version has no verified public observation date')
    if date(when)<date(fields['published']):raise ValueError('outcome predates paper')
    return dict(fields,outcome=outcome,question_id=question['question_id'])


def separate_cohorts(candidates):
    """Each annotated candidate independently declares its test; no all-test intersection.
    Evidence is verified BEFORE it can enter a prospective cohort lock. This is
    necessary but not sufficient: prediction generation, locks and review still gate execution.
    """
    cohorts={t:[] for t in TESTS};excluded={t:[] for t in TESTS}
    for c in candidates:
        test=c['test']
        if test not in TESTS:raise ValueError('unknown core test')
        try:
            d={k:verified_value(v) for k,v in c['assertions'].items()}
            for k in ('question_id','question','paper_id','posed_at','available_at','original_inputs','shuffled_inputs','decoy_question','topic_verified','human_verified'):
                if k not in d:raise ValueError('missing verified '+k)
            if d['human_verified'] is not True or d['topic_verified'] is not True:raise ValueError('human/topic verification absent')
            if date(d['posed_at'])<date('2025-07-01') or date(d['available_at'])>date(d['posed_at']):raise ValueError('question outside temporal eligibility')
            if not d['original_inputs'] or not d['shuffled_inputs'] or set(d['original_inputs'])==set(d['shuffled_inputs']):raise ValueError('original/shuffled reference links absent')
            dependencies={'I1':('complete_normalization','all_heads_available','paired_edit_annotations'),
                'I3':('length_matched_labels','quality_heads_available'),
                'S1':('minimal_paraphrase_label','near_miss_label','semantic_model_cutoff_verified'),
                'A1':('partial_coverage_annotations','concentration_annotations','fresh_prospective_cohort'),
                'H1':('expert_battle_labels','system_ids','length_matching','quality_heads_available'),
                'H3':('dated_review_labels','human_ceiling','quality_heads_available'),
                'O1':('dated_both_factor_labels','within_topic_pairs','quality_heads_available'),
                'O2':('same_seed_groups','within_year_pairs','dated_outcomes','quality_heads_available'),
                'T1':('model_2022_lock','model_2023_lock','all_heads_available','complete_normalization')}
            for k in dependencies[test]:
                if k=='near_miss_label':
                    if d.get(k) is not False:raise ValueError('near-miss label must explicitly be false')
                elif not d.get(k):raise ValueError('missing verified dependency '+k)
            cohorts[test].append({'source_candidate_id':c['candidate_id'],'verified_fields':d,'assertions':c['assertions'],
                                  'status':'ANNOTATED_CANDIDATE_NOT_EXECUTION_AUTHORIZATION'})
        except (ValueError,KeyError,TypeError) as e:excluded[test].append({'candidate_id':c['candidate_id'],'reason':str(e)})
    return {'cohorts':cohorts,'excluded':excluded}
