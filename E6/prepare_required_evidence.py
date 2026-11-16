"""Build source-grounded evidence and genuine human decision forms, offline.

No extraction model outputs, human decisions or HDR scores are synthesized.
Literal source grouping is a proposal; it never becomes a feature denominator
or an automatic semantic-discovery judgment.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from evaluation import ARMS, TARGET_EXTRACTION_PROMPT
from researcher_approval import ROOT, digest, file_digest, safe_path
from literature_finalization import extraction_source, verify_seal
from prepare_literature_sample_proposal import verify_sample_proposal


def sha(text):return hashlib.sha256(text.encode()).hexdigest()

def save(path,value):
    with Path(path).open('x') as h:json.dump(value,h,indent=2,sort_keys=True,ensure_ascii=False)


def literal_rules(truth):
    rules=[]
    for i,text in enumerate(truth):
        match=re.search(r'^If the "([^"]+)" of the given tweet is "(.*?)", then (.*)$',text)
        if not match:raise ValueError('Unrecognized source rule; no heuristic semantic mapping allowed')
        rules.append({'ground_truth_index':i,'source_text':text,'source_text_sha256':sha(text),
            'predicate_field':match.group(1),'predicate_value':match.group(2),'relationship_quote':match.group(3),
            'predicate_value_span':[match.start(2),match.end(2)],
            'relationship_span':[match.start(3),match.end(3)]})
    return rules


def prepare(root,output):
    root=Path(root);output=Path(output)
    load=lambda p:json.loads(safe_path(root,p).read_text())
    config=load('E6/config.json');approval=load('E6/RESEARCHER_APPROVAL.json')
    selected=load(config['dataset']['literature_selected_manifest']);verify_seal(selected)
    candidate_path='E6/data/literature_citation_verified_manifest_v1.json'
    proposal_path='E6/data/literature_sample_proposal_v1.json'
    candidate=load(candidate_path);proposal=load(proposal_path)
    originals=verify_sample_proposal(candidate,proposal)
    if originals!=selected['input_sets']:raise ValueError('Selected source rows changed')
    decision=next(r for r in approval['decisions'] if r['id']==24)
    policy=decision['resolved_details']['review_policy'];checks=policy['check_fields']
    guide=safe_path(root,policy['guide_path'])
    if file_digest(guide)!=policy['guide_sha256']:raise ValueError('review guide changed')
    source_paths={config['dataset']['literature_selected_manifest'],candidate_path,proposal_path,
        'E6/config.json','E6/evaluation_config.json','E6/RESEARCHER_APPROVAL.json','E6/PREREG.md',
        policy['guide_path'],'prompts/e6/09_target_extraction.txt',config['dataset']['data_generation_proposal']}
    # Inventory and preserve every historical TRAIN JSON/JSONL, including 0007.
    for directory in sorted((root/'E6/runs').glob('priority10_train*')):
        source_paths.update(str(p.relative_to(root)) for p in directory.rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl'))
    packets=[];review_forms=[];adjudications=[]
    for row in originals:
        field,text=extraction_source(row)
        # These are source records, not invented fixed-model extraction results.
        packet={'input_set_id':row['input_set_id'],'title':row['target']['title'],
            'candidate_record_sha256':digest(row),'target_source_field':field,'target_source_text':text,
            'target_source_text_sha256':sha(text),'source_url':row['target'].get('paper_url'),
            'rendered_extraction_prompt':TARGET_EXTRACTION_PROMPT.read_text().replace('{{TARGET_PAPER_TEXT}}',text),
            'extraction_prompt_file_sha256':file_digest(TARGET_EXTRACTION_PROMPT),
            'source_record_complete':True,'fixed_model_extraction_record':None,
            'extraction_status':'missing_not_executed','source_component_annotations':{
                k:{'text':None,'source_quote':None,'character_span':None,'annotator':None} for k in ('problem','method','result')}}
        packets.append(packet)
        if row['input_set_id'] in selected['manual_review_input_set_ids']:
            base={'input_set_id':row['input_set_id'],'target_source_text_sha256':sha(text),
                'extraction_sha256':None,'review_guide_sha256':policy['guide_sha256'],
                'reviewer_id':None,'reviewed_at_utc':None,'manual_check_completed':False,
                **{k:None for k in checks},'reviewer_notes':None,'extraction_errors':None,'corrections':None,
                'status':'awaiting_actual_extraction_before_review'}
            review_forms.extend([dict(base,reviewer_slot=i+1) for i in range(policy['reviewer_count'])])
            adjudications.append({'input_set_id':row['input_set_id'],'status':'conditional_only_if_actual_reviewers_disagree',
                'adjudicator_id':None,'adjudicated_at_utc':None,'review_records_sha256':None,'rationale':None,**{k:None for k in checks}})
    # Source ground truth is evaluation reference material; never generation input.
    gt_relative='data/HypoBench-datasets/synthetic/election/level2/gt_hypotheses_level2.json'
    source_paths.add(gt_relative);truth=load(gt_relative);rules=literal_rules(truth)
    mapping={}
    for rule in rules:
        feature=rule['predicate_field']
        mapping.setdefault(feature,{'ground_truth_indices':[],'source_texts':[]})
        mapping[feature]['ground_truth_indices'].append(rule['ground_truth_index'])
        mapping[feature]['source_texts'].append(rule['source_text'])
    feature_proposal={'status':'literal_source_field_grouping_only_pending_domain_judgment',
        'ground_truth_source_sha256':file_digest(safe_path(root,gt_relative)),
        'reference_feature_ids':sorted(mapping),'feature_mapping':mapping,
        'feature_mapping_sha256':digest(mapping),'approved_HDR_denominator':False,
        'warning':'Field grouping is exact syntax, not an approved definition of discoverable features. Do not treat 14 rules as 14 independent features.'}
    hdr_forms=[];terminal=[];seen=set()
    for relative in sorted(source_paths):
        if not relative.endswith('_generation_envelope.json'):continue
        saved=load(relative)
        if saved.get('checkpoint_sha256')!=digest({k:v for k,v in saved.items() if k!='checkpoint_sha256'}):raise ValueError('checkpoint changed: '+relative)
        envelope=saved['envelope'];unit=envelope['paper_id']
        if unit in seen or ':TRAIN-SET:0007:' in unit:raise ValueError('duplicate checkpoint or unexpected resolved 0007')
        seen.add(unit)
        for arm in ARMS:
            entry=envelope['arms'][arm]
            if entry.get('execution_status')!='succeeded':
                terminal.append({'generation_input_set_id':unit,'arm':arm,'status':'terminal_generation_failure','checkpoint':relative,'missing_output':entry.get('missing_output')});continue
            hypotheses=[h['text'] for h in entry['output']['hypotheses']]
            if len(hypotheses)!=6:raise ValueError('successful cell lacks six hypotheses')
            hdr_forms.append({'generation_input_set_id':unit,'arm':arm,'hypotheses':hypotheses,
                'hypotheses_sha256':digest(hypotheses),'generation_checkpoint':relative,
                'generation_checkpoint_file_sha256':file_digest(safe_path(root,relative)),
                'reference_feature_proposal_sha256':digest(feature_proposal),
                'feature_mapping':None,'reference_feature_ids':None,'discovered_feature_ids':None,'relationship_scores':None,
                'provenance':{'ground_truth_source_sha256':file_digest(safe_path(root,gt_relative)),
                    'feature_mapping_sha256':None,'judge_provenance':None},
                'status':'awaiting_grounded_discovery_and_relationship_judgments',
                'judgment_evidence':None})
    train=load(config['dataset']['data_generation_proposal'])
    for row in train['input_sets']:
        if row['input_set_id'] not in seen:
            if ':TRAIN-SET:0007:' not in row['input_set_id']:raise ValueError('unexpected missing TRAIN checkpoint')
            terminal.extend({'generation_input_set_id':row['input_set_id'],'arm':arm,'status':'unresolved_0007_do_not_retry'} for arm in ARMS)
    if len(packets)!=100 or len(review_forms)!=40 or len(hdr_forms)!=125 or len(terminal)!=15:raise ValueError('frozen evidence inventory differs')
    before={p:file_digest(safe_path(root,p)) for p in sorted(source_paths)}
    output.mkdir(parents=True,exist_ok=False)
    artifacts={'literature_source_records.json':packets,'literature_review_forms.json':review_forms,
        'literature_adjudication_forms.json':adjudications,'ground_truth_rule_inventory.json':rules,
        'HDR_feature_mapping_proposal.json':feature_proposal,'HDR_judgment_forms.json':hdr_forms,
        'terminal_missing_cells.json':terminal,'hdr_inputs_actual.json':{}}
    for name,value in artifacts.items():save(output/name,value)
    # Reviewer packets contain complete exact evidence, not inferred summaries.
    md=['# Literature source review — 20 fixed cases','',
        'Two independent reviewers per case; third adjudicator only for disagreements. All seven checks are blank.',
        'Actual fixed-model extraction is missing. Do not sign reviews until it is attached and hash-bound.',
        'Problem/method/result annotations are also missing; the four-field extraction prompt does not supply them.','']
    for p in packets:
        if p['input_set_id'] not in selected['manual_review_input_set_ids']:continue
        md.extend(['## '+p['input_set_id']+' — '+p['title'],'',
            'Source SHA-256: `'+p['target_source_text_sha256']+'`','',p['target_source_text'],'',
            'Extraction: MISSING. Reviewer 1 / reviewer 2: pending.','',*['- '+k+': ______' for k in checks],'',
            'Source quotes/locations, errors, corrections, identity/date: ______',''])
    (output/'literature_review_sheet.md').write_text('\n'.join(md))
    md=['# HDR source-grounded judgment sheet','',
        'Confirm a defensible feature definition/mapping first; literal source grouping is a proposal.',
        'For each cell record discovered feature IDs and source-supported relationship correctness for exactly the matched features.',
        'Use actual judge identity, method, time and supporting quotations. Missing judgments must stay null, never empty/zero.','',
        '## Ground truth source rules','']
    md.extend(f"GT{r['ground_truth_index']+1}: {r['source_text']}\n" for r in rules)
    for form in hdr_forms:
        md.extend(['## '+form['generation_input_set_id']+' / '+form['arm'],'',
            *[f'H{i+1}: {t}\n' for i,t in enumerate(form['hypotheses'])],
            'Discovered feature IDs: ______; relationship scores and source rationale: ______',
            'Judge identity/method/date: ______',''])
    (output/'HDR_review_sheet.md').write_text('\n'.join(md))
    report={'schema_version':'e6-required-evidence-bundle-v1','status':'partial_evidence_human_decisions_pending',
        'literature_source_records_complete':100,'literature_fixed_model_extractions_complete':0,
        'literature_independent_reviews_complete':0,'literature_independent_review_forms':40,
        'HDR_inputs_complete':0,'HDR_inputs_required':125,'HDR_grounded_comparison_records':125,
        'terminal_missing_cells':15,'source_artifact_file_hashes':before,
        'implementation_sha256':file_digest(Path(__file__)),
        'artifact_file_hashes':{p.name:file_digest(p) for p in sorted(output.iterdir())},
        'model_calls':0,'scoring_ready':False,
        'blockers':['100 actual fixed-model literature extractions are absent; cannot synthesize under no-new-model-calls instruction.',
            'Decision 24 requires problem/method/result reviews, but frozen extraction output contains only question/hypothesis and explicitness fields; requires authorized compatible source-component evidence process before acceptance.',
            '40 genuine independent source reviews (20 cases, two reviewers), plus third-person adjudications only for disagreements.',
            'HDR reference-feature definition/mapping needs domain assessment; all 125 cells need real discovered-feature and relationship judgments.',
            'Evaluator semantic validation remains pending the separate independent pilot judgments.']}
    save(output/'bundle.json',report)
    if any(file_digest(safe_path(root,p))!=h for p,h in before.items()):raise ValueError('preserved artifact changed')
    return report


def validate_bundle(path,root=ROOT):
    path=Path(path);bundle=json.loads(path.read_text());root=Path(root)
    if bundle.get('schema_version')!='e6-required-evidence-bundle-v1':raise ValueError('unknown evidence bundle schema')
    for relative,expected in bundle['source_artifact_file_hashes'].items():
        if file_digest(safe_path(root,relative))!=expected:raise ValueError('evidence source changed: '+relative)
    for name,expected in bundle['artifact_file_hashes'].items():
        if Path(name).name!=name or file_digest(path.parent/name)!=expected:raise ValueError('evidence artifact changed: '+name)
    packets=json.loads((path.parent/'literature_source_records.json').read_text())
    selected=json.loads(safe_path(root,'E6/data/literature_selected_manifest_v1.json').read_text())
    if len(packets)!=len(selected['input_sets']):raise ValueError('literature evidence count mismatch')
    for packet,row in zip(packets,selected['input_sets']):
        field,text=extraction_source(row)
        if packet['input_set_id']!=row['input_set_id'] or packet['target_source_text']!=text or packet['target_source_text_sha256']!=sha(text) or packet['target_source_field']!=field or packet['candidate_record_sha256']!=digest(row):raise ValueError('literature evidence source mismatch')
    # Partial source evidence cannot authorize scoring. Completed inputs must pass
    # the existing source/review and bound_hdr_score validators separately.
    if bundle.get('scoring_ready') is not False:raise ValueError('source-only evidence cannot claim scoring authorization')
    return bundle


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args();r=prepare(ROOT,args.output_dir);validate_bundle(args.output_dir/'bundle.json')
    print(json.dumps({k:r[k] for k in ('literature_source_records_complete','literature_fixed_model_extractions_complete','HDR_inputs_complete','HDR_inputs_required','HDR_grounded_comparison_records','model_calls')},indent=2))

if __name__=='__main__':main()
