"""Source-bound HDR compilation and objective identity evidence, with no inference.

Unmatched text is unknown, never evidence of non-discovery or a zero score.
The frozen 14-rule recovery prompt is not an HDR evaluator policy.
"""
import argparse
import fcntl
import json
import math
import os
import re
from pathlib import Path
from types import SimpleNamespace
from researcher_approval import ROOT, digest, file_digest, safe_path
from inductive_execution import bound_hdr_score

FORMS='E6/data/required_evidence_v1/HDR_judgment_forms.json'
TERMINAL='E6/data/required_evidence_v1/terminal_missing_cells.json'
TRUTH='data/HypoBench-datasets/synthetic/election/level2/gt_hypotheses_level2.json'


def save(path,value):
    with Path(path).open('x') as handle:
        json.dump(value,handle,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)
        handle.flush();os.fsync(handle.fileno())


def checked_forms(root=ROOT):
    root=Path(root)
    forms=json.loads((root/FORMS).read_text());terminal=json.loads((root/TERMINAL).read_text())
    identities=set();checkpoints={}
    for form in forms:
        unit,arm=form['generation_input_set_id'],form['arm']
        if ':TRAIN-SET:' not in unit or ':TRAIN-SET:0007:' in unit or (unit,arm) in identities:
            raise ValueError('foreign, unresolved or duplicate scoring cell')
        identities.add((unit,arm));relative=form['generation_checkpoint']
        if relative not in checkpoints:
            path=safe_path(root,relative)
            if file_digest(path)!=form['generation_checkpoint_file_sha256']:raise ValueError('TRAIN checkpoint file changed')
            saved=json.loads(path.read_text())
            if saved.get('checkpoint_sha256')!=digest({k:v for k,v in saved.items() if k!='checkpoint_sha256'}):raise ValueError('TRAIN checkpoint checksum mismatch')
            checkpoints[relative]=saved['envelope']
        envelope=checkpoints[relative]
        if envelope['paper_id']!=unit or envelope['execution_mode']!='final':raise ValueError('TRAIN source identity mismatch')
        entry=envelope['arms'][arm]
        if entry.get('execution_status')!='succeeded':raise ValueError('failed generation cannot receive HDR')
        hypotheses=[h['text'] for h in entry['output']['hypotheses']]
        if hypotheses!=form['hypotheses'] or digest(hypotheses)!=form['hypotheses_sha256']:raise ValueError('hypothesis evidence changed')
    if len(forms)!=125 or len(terminal)!=15:raise ValueError('fixed TRAIN cell inventory changed')
    if any((r['generation_input_set_id'],r['arm']) in identities for r in terminal):raise ValueError('missing cells overlap scored cells')
    return forms,terminal


def exact_rule_matches(hypotheses,truth):
    """Only literal equality proves a full-rule match; no negative inferences."""
    return [{'hypothesis_index':i,'ground_truth_index':j,'source_text_sha256':digest(source),
             'method':'literal_full_rule_equality','relationship_correctness':1.0}
            for i,text in enumerate(hypotheses) for j,source in enumerate(truth) if text==source]


def validate_mapping(mapping,truth,truth_sha):
    if not isinstance(mapping,dict) or mapping.get('approved_HDR_denominator') is not True:
        raise ValueError('actual justified reference-feature definition required; pending grouping proposal cannot define HDR denominator')
    refs=mapping.get('reference_feature_ids');features=mapping.get('feature_mapping')
    if not isinstance(refs,list) or not refs or len(set(refs))!=len(refs) or not isinstance(features,dict) or set(features)!=set(refs):
        raise ValueError('complete unique reference-feature mapping required')
    if mapping.get('ground_truth_source_sha256')!=truth_sha or mapping.get('feature_mapping_sha256')!=digest(features):
        raise ValueError('reference-feature mapping hash/source mismatch')
    provenance=mapping.get('definition_provenance')
    if not isinstance(provenance,dict) or not all(isinstance(provenance.get(k),str) and provenance[k].strip() for k in ('author_id','defined_at_utc','source_supported_justification')):
        raise ValueError('actual feature-definition provenance required')
    from researcher_approval import valid_utc
    if not valid_utc(provenance['defined_at_utc']):raise ValueError('feature-definition UTC time invalid')
    for feature in features.values():
        indices=feature.get('ground_truth_indices')
        if not isinstance(indices,list) or not indices or any(type(i) is not int or not 0<=i<len(truth) for i in indices):raise ValueError('feature lacks source-rule mapping')
        if feature.get('source_texts')!=[truth[i] for i in indices]:raise ValueError('feature source quotations differ from ground truth')
    return True


def score_cell(form,mapping,payload,truth,truth_sha):
    matches=exact_rule_matches(form['hypotheses'],truth)
    evidence={'exact_full_rule_matches':matches,'nonmatch_interpretation':'unknown, not zero or NO_MATCH'}
    if mapping is None:return None,None,dict(evidence,status='blocked_reference_feature_definition_missing')
    validate_mapping(mapping,truth,truth_sha)
    if payload is None:
        # An exact identity establishes both discovery and relationship only when
        # every mapped source rule for every reference feature is present. No
        # choice of aggregation over partially matched rules is introduced.
        matched_indices={r['ground_truth_index'] for r in matches}
        covered={f for f,entry in mapping['feature_mapping'].items() if set(entry['ground_truth_indices'])<=matched_indices}
        if covered!=set(mapping['reference_feature_ids']):
            return None,None,dict(evidence,status='blocked_semantic_discovery_or_relationship_judgments_missing',
                objective_fully_supported_features=sorted(covered))
        payload={'generation_input_set_id':form['generation_input_set_id'],'arm':form['arm'],
            'hypotheses_sha256':form['hypotheses_sha256'],'feature_mapping':mapping['feature_mapping'],
            'reference_feature_ids':mapping['reference_feature_ids'],'discovered_feature_ids':mapping['reference_feature_ids'],
            'relationship_scores':{f:1.0 for f in mapping['reference_feature_ids']},
            'provenance':{'ground_truth_source_sha256':truth_sha,'feature_mapping_sha256':mapping['feature_mapping_sha256'],
                'judge_provenance':{'method':'all_mapped_full_source_rules_literal_equality','mapping_definition_provenance':mapping['definition_provenance'],
                    'exact_matches':matches}}}
    if payload.get('feature_mapping')!=mapping['feature_mapping'] or payload.get('reference_feature_ids')!=mapping['reference_feature_ids']:
        raise ValueError('cell mapping differs from source-defined denominator')
    # Supplied semantic judgments require actual attributable evidence; an empty
    # discovery list is valid only as an explicit recorded judgment, not a default.
    judge=payload.get('provenance',{}).get('judge_provenance')
    if not isinstance(judge,dict) or not judge.get('method'):raise ValueError('attributable HDR judgment method required')
    if judge['method']=='all_mapped_full_source_rules_literal_equality':
        matched_indices={r['ground_truth_index'] for r in matches}
        if (any(not set(entry['ground_truth_indices'])<=matched_indices for entry in mapping['feature_mapping'].values())
                or set(payload.get('discovered_feature_ids',[]))!=set(mapping['reference_feature_ids'])
                or payload.get('relationship_scores')!={f:1.0 for f in mapping['reference_feature_ids']}):
            raise ValueError('claimed objective identity judgments lack full exact source support')
    else:
        from researcher_approval import valid_utc
        if not judge.get('judge_id') or not valid_utc(judge.get('judged_at_utc')) or not judge.get('evidence'):
            raise ValueError('actual judge identity/time/supporting evidence required')
    context=SimpleNamespace(test_manifest={'dataset_ground_truth':{'source_file_sha256':truth_sha,'hypotheses':truth}})
    result=bound_hdr_score(context,form['generation_input_set_id'],form['arm'],form['hypotheses'],payload)
    return payload,result,dict(evidence,status='scored')


def frozen_hdr_policy_errors(config,evaluation):
    """Do not invent a semantic policy or repurpose the recovery evaluator."""
    hdr=evaluation['hypobench']['paper_hdr']
    if not hdr.get('discovery_judgment_policy') or not hdr.get('relationship_judgment_policy'):
        return ['Frozen evaluation_config.json contains no HDR discovery/relationship judgment policy or prompt. Recovery prompt 14 measures a separate outcome; no HDR model calls are authorized by this runner.']
    return ['Unrecognized HDR policy: no implemented frozen source-bound semantic interface.']


def compile_hdr(output, *, mapping=None, judgments=None, root=ROOT):
    root=Path(root);output=Path(output)
    config=json.loads((root/'E6/config.json').read_text());evaluation=json.loads((root/'E6/evaluation_config.json').read_text())
    forms,terminal=checked_forms(root)
    truth=json.loads((root/TRUTH).read_text());truth_sha=file_digest(root/TRUTH)
    required_sha=config['dataset']['external_source_repository']['file_hashes'][TRUTH]
    if truth_sha!=required_sha:raise ValueError('frozen source ground truth changed')
    if mapping is not None:validate_mapping(mapping,truth,truth_sha)
    judgments=judgments or {}
    allowed={(r['generation_input_set_id'],r['arm']) for r in forms}
    supplied={(unit,arm) for unit,arms in judgments.items() for arm in arms}
    if not supplied<=allowed:raise ValueError('judgments contain failed, foreign or unresolved generation cells')
    output.mkdir(parents=True,exist_ok=True)
    with (output/'compile.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Inputs and implementation bind a fresh immutable compilation; no calls
        # occur, so reruns can replay checkpoints but cannot change judgments.
        files=(FORMS,TERMINAL,TRUTH,'E6/config.json','E6/evaluation_config.json','E6/PREREG.md')
        identity=digest({'files':{p:file_digest(root/p) for p in files},'mapping':mapping,'judgments':judgments,
            'implementation_sha256':file_digest(Path(__file__))})
        binding=output/'compilation_identity.json'
        if binding.exists():
            if json.loads(binding.read_text())!={'identity':identity}:raise ValueError('new source/mapping/judgments require a new output directory')
        else:save(binding,{'identity':identity})
        hdr_inputs={};scores=[];pending=[];exact_total=0
        for form in forms:
            unit,arm=form['generation_input_set_id'],form['arm']
            checkpoint=output/(digest([unit,arm])[:20]+'.json')
            if checkpoint.exists():
                saved=json.loads(checkpoint.read_text())
                if saved.get('identity')!=identity or saved.get('checkpoint_sha256')!=digest({k:v for k,v in saved.items() if k!='checkpoint_sha256'}):raise ValueError('HDR checkpoint changed')
            else:
                payload,score,evidence=score_cell(form,mapping,judgments.get(unit,{}).get(arm),truth,truth_sha)
                saved={'identity':identity,'generation_input_set_id':unit,'arm':arm,'payload':payload,'score':score,'evidence':evidence}
                saved['checkpoint_sha256']=digest(saved);save(checkpoint,saved)
            exact_total+=len(saved['evidence']['exact_full_rule_matches'])
            if saved['score'] is not None:
                hdr_inputs.setdefault(unit,{})[arm]=saved['payload'];scores.append({'generation_input_set_id':unit,'arm':arm,**saved['score']})
            else:pending.append(saved)
        report={'schema_version':'e6-hdr-compilation-v1','HDR_cells_scored':len(scores),'HDR_cells_required':len(forms),
            'objective_full_rule_matches':exact_total,'terminal_missing_cells':terminal,'scores':scores,
            'pending_cells':[{'generation_input_set_id':r['generation_input_set_id'],'arm':r['arm'],'reason':r['evidence']['status']} for r in pending],
            'semantic_runner_blockers':frozen_hdr_policy_errors(config,evaluation),
            'mapping_present':mapping is not None,'identity':identity,'model_calls':0,'TEST_evaluation':False,
            'readiness_inputs_file':'hdr_inputs_actual.json','note':'Failed generation cells excluded from scoring, never replaced; no imputation. Exact full-rule matches do not define the feature denominator.'}
        for name,value in (('hdr_inputs_actual.json',hdr_inputs),('report.json',report)):
            path=output/name
            if path.exists():
                if json.loads(path.read_text())!=value:raise ValueError('HDR result differs from immutable compilation')
            else:save(path,value)
        return report


def load_compilation(path):
    """Read scoring inputs produced by this compiler; pending cells stay absent."""
    path=Path(path)
    report=json.loads((path/'report.json').read_text())
    identity=json.loads((path/'compilation_identity.json').read_text())['identity']
    if report.get('schema_version')!='e6-hdr-compilation-v1' or report.get('identity')!=identity:
        raise ValueError('HDR report identity mismatch')
    inputs=json.loads((path/'hdr_inputs_actual.json').read_text())
    expected={}
    for checkpoint in path.glob('*.json'):
        if checkpoint.name in ('report.json','compilation_identity.json','hdr_inputs_actual.json'):continue
        row=json.loads(checkpoint.read_text())
        if row.get('identity')!=identity or row.get('checkpoint_sha256')!=digest({k:v for k,v in row.items() if k!='checkpoint_sha256'}):
            raise ValueError('HDR compilation checkpoint integrity mismatch')
        if row.get('score') is not None:
            expected.setdefault(row['generation_input_set_id'],{})[row['arm']]=row['payload']
    if inputs!=expected or sum(len(arms) for arms in inputs.values())!=report['HDR_cells_scored']:
        raise ValueError('HDR completed-input inventory mismatch')
    return inputs


def prepare_independent_review(output, root=ROOT):
    """Collapse literal duplicate sets only; never infer semantic equivalence."""
    root=Path(root);output=Path(output)
    forms,terminal=checked_forms(root)
    truth=json.loads((root/TRUTH).read_text())
    config=json.loads((root/'E6/config.json').read_text())
    if file_digest(root/TRUTH)!=config['dataset']['external_source_repository']['file_hashes'][TRUTH]:
        raise ValueError('frozen ground truth changed')
    metadata_path=root/'data/HypoBench-datasets/synthetic/election/level2/metadata.json'
    metadata=json.loads(metadata_path.read_text())
    if metadata['ground_truth_hypotheses']!=truth:raise ValueError('metadata and frozen rule list differ')
    groups={}
    for form in forms:
        key=digest(form['hypotheses'])
        group=groups.setdefault(key,{'review_case_id':'HDR-'+key[:16],
            'hypotheses':form['hypotheses'],'hypotheses_sha256':key,'records':[]})
        if group['hypotheses']!=form['hypotheses']:raise ValueError('hypothesis digest collision')
        group['records'].append({'generation_input_set_id':form['generation_input_set_id'],'arm':form['arm']})
    fields=sorted({re.match(r'^If the "([^"]+)"',t).group(1) for t in truth})
    report={'HDR_records_scored':0,'HDR_records_required':len(forms),'unique_review_sets':len(groups),
        'exact_duplicate_reviews_avoided':len(forms)-len(groups),'denominator':None,
        'literal_rule_field_groups':fields,'metadata_feature_categories':list(metadata['features']),
        'ground_truth_rules':len(truth),'model_calls':0,
        'blocker':'Source evidence does not uniquely choose reference-feature granularity or how several value-specific rules determine one feature relationship score. Actual grounded mapping and attributable discovery/relationship judgments are absent.',
        'readiness_inputs':'E6/data/hdr_scoring_v3/hdr_inputs_actual.json',
        'scoring_ready':False,'human_judgments_created':0,
        'source_hashes':{p:file_digest(root/p) for p in (TRUTH,str(metadata_path.relative_to(root)),FORMS,
            'E6/assignment_e6_excerpt_v1.txt','E6/PREREG.md','E6/evaluation_config.json')},
        'paper_source':'https://arxiv.org/html/2504.11524v1#S3',
        'interpretation':'The paper defines HDR over true features and separately rates relationship correctness. Its Appendix A matches input variables independently of outcomes. It does not settle this local grouping and aggregation choice.',
        'next_action':'Independent domain reviewer defines source-grounded feature IDs, rule mapping and relationship aggregation consistent with frozen requirements, with identity, UTC time and justification; then judges each distinct set. If this requires a new method rather than documenting an existing one, researcher resolution is necessary before scoring.'}
    output.mkdir(parents=True,exist_ok=False)
    save(output/'review_inventory.json',report)
    save(output/'coordinator_case_mapping.json',list(groups.values()))
    md=['# HDR independent source review','',
        'No model judgments or human answers are prefilled. Review independently; coordinator mapping contains arm identities and should be withheld until completion.',
        str(len(forms))+' records reduce to '+str(len(groups))+' literally identical-set groups. Reuse only exact full ordered-set identity; no paraphrase equivalence is inferred.','',
        '## First resolve the reference-feature definition','',
        'HDR = (discovered true features / all true features) × mean relationship correctness over discovered features. See [frozen source paper, section 3 and Appendix A](https://arxiv.org/html/2504.11524v1#S3). Fourteen-reference recovery recall is a separate outcome.',
        'The source has 14 rules over three predicate fields; metadata lists four feature categories and four templates. Those counts describe different objects. No count is silently selected as the denominator. Template placeholders alone do not prove an independent outcome relationship for every placeholder.','',
        'Required one-time decision: define the true feature unit, reference_feature_ids and feature_mapping (exact rule indices and source_texts), justify omissions/overlaps, and explain how multiple rules and multiple generated claims determine a feature relationship score. Do not invent a new frozen method. If source evidence is insufficient, record unresolved and stop scoring.','',
        'Definition author / UTC time: ______',
        'Source-supported definition and mapping: ______',
        'Multiple-rule / multiple-claim relationship interpretation: ______',
        'Rationale and source locations: ______','',
        'Literal rule predicate fields: '+', '.join(fields),
        'Metadata feature category keys: '+', '.join(metadata['features']),
        'Metadata num_templates: '+str(metadata['num_templates']),
        'Metadata num_impactful_feature: '+str(metadata['num_impactful_feature'])+' (not assumed to be the HDR denominator).','',
        '## Exact ground-truth evidence (zero-based rule indices)','']
    for i,text in enumerate(truth):md += [f'{i}: '+text,'']
    md += ['## Per-case instructions','',
        'After the denominator is resolved, for each reference feature record discovery true/false, supporting generated hypothesis index and ground-truth rule index, brief rationale, and relationship correctness in [0,1] if discovered. Explicit negative judgments require evidence; unmatched literal text is unknown, not false. Do not fill relationship scores for undiscovered features. No pairwise 6×14 judgment matrix is required by this handoff; review the full six-hypothesis set once.',
        'Use the existing payload schema documented in E6/HDR_SCORING.md. Coordinator expands exact duplicate groups to their original records, preserving each record arm/input ID and hypotheses hash. Judge identity, UTC time and evidence must accompany every actual judgment. No automatic approval follows from completing a form.','']
    for group in groups.values():
        md += ['## '+group['review_case_id'],'']
        for i,text in enumerate(group['hypotheses']):md += [f'H{i}: '+text,'']
        md += ['Reviewer / UTC time: ______',
            'Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______',
            'Unresolved interpretation / source limitation: ______','']
    (output/'independent_review.md').write_text('\n'.join(md))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--prepare-review',action='store_true',help='prepare deduplicated blind source-review worklist without assigning judgments')
    parser.add_argument('--mapping',type=Path);parser.add_argument('--judgments',type=Path)
    parser.add_argument('--execute-judgments',action='store_true',help='fail closed unless a frozen HDR semantic policy exists; never uses recovery as HDR')
    args=parser.parse_args()
    if args.prepare_review:
        if args.mapping or args.judgments or args.execute_judgments:parser.error('review preparation does not consume judgments')
        print(json.dumps(prepare_independent_review(args.output_dir),indent=2));return 0
    if args.execute_judgments:
        evaluation=json.loads((ROOT/'E6/evaluation_config.json').read_text());config=json.loads((ROOT/'E6/config.json').read_text())
        errors=frozen_hdr_policy_errors(config,evaluation)
        print(json.dumps({'status':'blocked_before_client_construction','model_calls':0,'blockers':errors},indent=2));return 2
    report=compile_hdr(args.output_dir,mapping=json.loads(args.mapping.read_text()) if args.mapping else None,
                       judgments=json.loads(args.judgments.read_text()) if args.judgments else None)
    print(json.dumps({k:report[k] for k in ('HDR_cells_scored','HDR_cells_required','objective_full_rule_matches','mapping_present','model_calls','semantic_runner_blockers')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
