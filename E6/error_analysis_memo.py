"""Offline 20-set error review packets, frozen summaries and one-page draft memo.

Reads only completed TRAIN generation by default. Literature arm/evaluation
artifacts must be supplied explicitly; running extraction is never scanned.
"""
import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import sys
from pathlib import Path
from evaluation import ARMS
from researcher_approval import ROOT, digest, file_digest, safe_path, valid_utc
from statistical_analysis import analyze_configured_evaluations, write_analysis_exclusive

ISSUES=('generation_schema_failure','unsupported_evidence','redundancy','question_hypothesis_mismatch','target_mismatch')
COMMON=('generated_tokens','already_asked_rate','diversity','type_constructive','type_analytic','type_other','type_ambiguous')
METRICS={'data':('heldout_accuracy','HDR','planted_recovery')+COMMON,
         'literature':('main_hypothesis_best_similarity','research_question_best_similarity','same_question_fraction')+COMMON}


def save(path,value):
    with Path(path).open('x') as h:json.dump(value,h,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)


def frozen_sample(config,cohorts):
    plan=config['evaluation_human_review']['pre_outcome_error_review_plan']
    if plan['case_count']!=20 or plan['cases_per_testbed']!=10 or plan['reviewer_count']!=1:
        raise ValueError('unsupported frozen error review plan')
    selected={bed:sorted(ids,key=lambda unit:(hashlib.sha256(f'E6-ERROR-REVIEW-v1|2026|{bed}|{unit}'.encode()).hexdigest(),unit))[:10]
              for bed,ids in cohorts.items()}
    if selected['data']+selected['literature']!=config['evaluation_human_review']['human_review_sample']:
        raise ValueError('frozen error review sample differs from deterministic selection')
    return selected


def verify_runtime(config):
    expected=config['statistical_analysis']['analysis_runtime_observation']
    actual={'python_version':platform.python_version(),'executable_sha256':file_digest(Path(sys.executable)),
        'standard_library_sha256':{name:file_digest(Path(module.__file__)) for name,module in (('random',random),('statistics',statistics))}}
    if any(actual[key]!=expected[key] for key in actual):raise ValueError('runtime/dependency hashes differ from frozen analysis settings')
    return actual


def generation(saved,unit):
    if saved.get('checkpoint_sha256')!=digest({k:v for k,v in saved.items() if k!='checkpoint_sha256'}):raise ValueError('generation checkpoint hash mismatch')
    envelope=saved['envelope']
    if envelope.get('paper_id')!=unit or envelope.get('execution_mode')!='final' or envelope.get('protocol_validation_errors') or set(envelope.get('arms',{}))!=set(ARMS):raise ValueError('foreign, blocked or incomplete generation envelope')
    return envelope


def scalar(record,path):
    if not isinstance(record,dict) or record.get('status') not in ('succeeded','evaluated','scored'):return None
    current=record
    for key in path:
        if isinstance(current,dict) and current.get('status') not in (None,'succeeded','evaluated','scored'):return None
        if not isinstance(current,dict) or key not in current:return None
        current=current[key]
    return current if type(current) in (int,float) and math.isfinite(current) else None


def secondary_metrics(record,entry,unit):
    values={}
    for key,name,path in (('diversity','diversity',['parsed_output','aggregate']),
                           ('already_asked','already_asked_rate',['parsed_output','rate']),
                           ('planted_recovery','planted_recovery',['parsed_output','recovery_recall'])):
        sub=record.get(key,{})
        if sub and sub.get('input_set_id')!=unit:raise ValueError('secondary metric belongs to another unit')
        values[name]=scalar(sub,path)
    questions={h['question_text'] for h in entry.get('output',{}).get('hypotheses',[]) if h.get('question_text')}
    classifications=record.get('question_types',[])
    if questions:
        by_question={}
        for r in classifications:
            if r.get('input_set_id')!=unit:raise ValueError('classification belongs to another unit')
            question=r.get('evaluation_input',{}).get('question')
            if question in by_question:raise ValueError('duplicate question classification')
            by_question[question]=r
        if set(by_question)==questions and all(r.get('status')=='succeeded' and r.get('parsed_output',{}).get('type') in ('constructive','analytic','other','ambiguous') for r in by_question.values()):
            for category in ('constructive','analytic','other','ambiguous'):
                values['type_'+category]=sum(r['parsed_output']['type']==category for r in by_question.values())/len(questions)
    return values


def reconstruction_metrics(bundle,unit,arm):
    values={}
    for record in bundle.get('records',[]):
        if record.get('input_set_id')!=unit:raise ValueError('reconstruction source identity mismatch')
        if record.get('provenance',{}).get('arm')!=arm:continue
        field=record.get('evaluation_input',{}).get('field');stage=record.get('stage')
        name=('main_hypothesis_best_similarity' if field=='main_hypothesis' else 'research_question_best_similarity') if stage=='literature_reconstruction_similarity' else 'same_question_fraction' if stage=='same_question_judgment' else None
        if name:
            if name in values:raise ValueError('duplicate reconstruction metric')
            values[name]=scalar(record,['analysis_summary','same_question_fraction'] if name=='same_question_fraction' else ['parsed_output','best_similarity'])
    return values


def summarize_metric(sources,bed,metric,config,evaluation):
    if bed=='data':
        return analyze_configured_evaluations(sources,config=config,evaluation_config=evaluation,
            testbed=bed,metric=metric,value_path=['metrics',metric])
    return analyze_configured_evaluations(sources,config=config,evaluation_config=evaluation,testbed=bed,metric=metric,
        stage='verified_input_set_scalar',field=metric,value_path=['parsed_output','value'])


def review_status(packets,reviews):
    expected={(p['testbed'],p['input_set_id']):p for p in packets};seen=set();verified=[]
    for row in reviews:
        key=(row.get('testbed'),row.get('input_set_id'))
        if key not in expected or key in seen:raise ValueError('foreign or duplicate human error review')
        seen.add(key);packet=expected[key]
        if row.get('packet_sha256')!=packet['packet_sha256'] or not row.get('reviewer_id') or not valid_utc(row.get('reviewed_at_utc')):
            raise ValueError('error review must bind packet and actual reviewer/time')
        if row.get('end_to_end_review_completed') is not True or not row.get('notes'):raise ValueError('incomplete end-to-end error review')
        if set(row.get('arms',{}))!=set(ARMS):raise ValueError('error review requires all seven arms')
        for arm,judgment in row['arms'].items():
            available=packet['arms'][arm]['generation_status']=='succeeded'
            if not judgment.get('notes'):raise ValueError('actual seven-arm review notes required')
            if available:
                if judgment.get('status')!='reviewed' or any(type(judgment.get(issue)) is not bool for issue in ISSUES):
                    raise ValueError('actual seven-arm error coding required')
            elif judgment.get('status')!='missing_not_evaluable' or any(judgment.get(issue) is not None for issue in ISSUES):
                raise ValueError('missing/failed generation must remain not evaluable, not negative error judgments')
            examples=judgment.get('examples')
            if not isinstance(examples,list) or (any(judgment[i] for i in ISSUES) and not examples):raise ValueError('coded errors require real examples')
            haystack=json.dumps({'source_evidence':packet['source_evidence'],'cell':packet['arms'][arm]},ensure_ascii=False)
            for example in examples:
                if not example.get('quote') or example['quote'] not in haystack or not example.get('explanation'):raise ValueError('error example not grounded in saved packet')
        verified.append(row)
    return {'reviewed_input_sets':len(verified),'required_input_sets':20,'human_error_analysis_complete':len(verified)==20,
        'issue_cell_counts':{issue:sum(r['arms'][a][issue] is True for r in verified for a in ARMS) for issue in ISSUES} if verified else None,
        'coded_arm_cells':sum(r['arms'][a].get('status')=='reviewed' for r in verified for a in ARMS),
        'reviewed_arm_cells':len(verified)*7,'identity_authentication':'attributed fields only; software cannot authenticate independence',
        'reviews':verified}


def memo_text(summary,analyses):
    def estimate(bed,metric,arm):
        r=analyses[bed,metric]['arm_estimates'][arm]
        if r['point_estimate'] is None:return 'pending'
        lo,hi=r['interval'];return f"{r['point_estimate']:.3g} [{lo:.3g}, {hi:.3g}] (n={r['included_count']})"
    def contrast(bed,metric,left,right):
        comparisons=analyses[bed,metric]['comparisons'];key=left+'-minus-'+right
        reverse=key not in comparisons
        r=comparisons.get(key,comparisons.get(right+'-minus-'+left))
        if r is None or r['point_estimate'] is None:return 'pending'
        point=r['point_estimate'];lo,hi=r['interval']
        if reverse:point,lo,hi=-point,-hi,-lo
        return f"{point:.3g} [{lo:.3g}, {hi:.3g}] (n={r['included_count']})"
    lines=['# E6 research-agent memo — provisional one-page draft','',
        '**Decision: pending verified outcome evaluation.** Whether questions-first decomposition helps, selection beats random choice, or controls degrade cannot be concluded from generation alone.','',
        '| Arm | Data accuracy | Literature hypothesis similarity | Data generated-token cost |',
        '|---|---|---|---|']
    for arm in ARMS:lines.append('| '+arm+' | '+estimate('data','heldout_accuracy',arm)+' | '+estimate('literature','main_hypothesis_best_similarity',arm)+' | '+estimate('data','generated_tokens',arm)+' |')
    lines.extend(['',
        'Entries are arithmetic means with descriptive 95% bootstrap intervals and available input-set counts; unavailable outcomes are pending. Costs include charged failed-arm work and shared preparation under the frozen per-arm accounting; do not sum shared costs across arms.',
        '', '**Conditions and controls.** Paired differences (left minus right):', '',
        '| Contrast | Data accuracy | Literature hypothesis similarity |',
        '|---|---|---|'])
    for left,right in (('QH','D'),('QH-sel','QH-rand'),('QH','D-shuffled'),('D','D-empty')):
        lines.append('| '+left+' − '+right+' | '+contrast('data','heldout_accuracy',left,right)+' | '+contrast('literature','main_hypothesis_best_similarity',left,right)+' |')
    lines.extend(['',
        '**Error analysis.** '+str(summary['human_review']['reviewed_input_sets'])+'/20 fixed cases have attributed end-to-end reviews. Saved examples and failure records are provided for all seven arms; semantic error judgments remain pending. No most-common failure is claimed without completed coding.','',
        '**Scope and limits.** Testbeds remain separate. Failed generation and unresolved TRAIN set 0007 are missing, not zero. Literature reference extraction is not seven-arm experimental output. HDR, historical-question rates, diversity and question types remain pending where genuine scoring is unavailable.','',
        '**Method and cost.** One frozen model/decoding configuration, 8192 generated-token cap per set/arm, six hypotheses. Bootstrap: 10,000 input-set resamples, seed 2026, SHA256-seeded MT19937 streams, linear-percentile intervals; complete pairs for contrasts. Intervals are unadjusted and descriptive. See analysis.json and error review packets for provenance and denominators.'])
    return '\n'.join(lines)+'\n'


def compiled_hdr_metrics(directory,root=ROOT):
    """Recompute existing bound HDR payloads; never infer missing judgments."""
    from types import SimpleNamespace
    from hdr_pipeline import load_compilation, checked_forms, TRUTH
    from inductive_execution import bound_hdr_score
    inputs=load_compilation(directory)
    forms,_=checked_forms(root)
    expected={(r['generation_input_set_id'],r['arm']):r for r in forms}
    context=SimpleNamespace(test_manifest={'dataset_ground_truth':{
        'source_file_sha256':file_digest(Path(root)/TRUTH),
        'hypotheses':json.loads((Path(root)/TRUTH).read_text())}})
    values={}
    for unit,arms in inputs.items():
        for arm,payload in arms.items():
            if (unit,arm) not in expected:raise ValueError('foreign or failed HDR compilation cell')
            form=expected[unit,arm]
            score=bound_hdr_score(context,unit,arm,form['hypotheses'],payload)
            if score.get('status')!='scored':raise ValueError('HDR compilation cell is not scored')
            values[unit,arm]=score['hypothesis_discovery_rate']
    return values


def build(output,*,artifact_index=None,reviews=None,hdr_compilation=None,root=ROOT):
    root=Path(root);output=Path(output)
    read=lambda relative:json.loads(safe_path(root,relative).read_text())
    config=read('E6/config.json');evaluation=read('E6/evaluation_config.json');runtime=verify_runtime(config)
    train=read(config['dataset']['data_generation_proposal']);literature=read(config['dataset']['literature_selected_manifest'])
    cohorts={'data':[r['input_set_id'] for r in train['input_sets']],'literature':literature['selected_input_set_ids']}
    chosen=frozen_sample(config,cohorts)
    source_rows={'data':{r['input_set_id']:r for r in train['input_sets']},'literature':{r['input_set_id']:r for r in literature['input_sets']}}
    envelopes={};provenance={};evaluations={};histories={}
    for folder in sorted((root/'E6/runs').glob('priority10_train*')):
        for path in folder.rglob('*_generation_envelope.json'):
            saved=json.loads(path.read_text());unit=saved['envelope']['paper_id'];key=('data',unit)
            if unit not in cohorts['data'] or key in envelopes:raise ValueError('duplicate or foreign TRAIN checkpoint')
            envelopes[key]=generation(saved,unit);provenance[str(path.relative_to(root))]=file_digest(path)
        for path in folder.rglob('model_calls.jsonl'):
            histories[str(path.relative_to(root))]=file_digest(path)
    # Explicit completed-artifact index avoids reading the concurrent extraction tree.
    for item in (artifact_index or {}).get('artifacts',[]):
        bed,unit=item['testbed'],item['input_set_id'];key=(bed,unit)
        if bed not in cohorts or unit not in cohorts[bed]:raise ValueError('foreign evaluation unit')
        path=safe_path(root,item['path'])
        if 'literature_extraction' in str(path):raise ValueError('reference extraction is not experimental arm output')
        if file_digest(path)!=item['file_sha256']:raise ValueError('completed evaluation artifact hash mismatch')
        value=json.loads(path.read_text());provenance[item['path']]=item['file_sha256']
        kind=item['kind']
        if kind=='generation_checkpoint':
            if key in envelopes:raise ValueError('duplicate generation source')
            envelopes[key]=generation(value,unit)
        else:
            if kind not in ('train_evaluation','literature_reconstruction','secondary'):raise ValueError('unsupported experimental artifact kind')
            ekey=(bed,unit,kind,item.get('arm'))
            if ekey in evaluations:raise ValueError('duplicate evaluation artifact')
            for hash_key in ('result_sha256','bundle_sha256'):
                if hash_key in value and value[hash_key]!=digest({k:v for k,v in value.items() if k!=hash_key}):raise ValueError('evaluation content checksum mismatch')
            evaluations[ekey]=value
    hdr_values=compiled_hdr_metrics(hdr_compilation,root) if hdr_compilation is not None else {}
    values={};packets=[];normalized={bed:{m:[] for m in METRICS[bed]} for bed in cohorts}
    for bed,ids in cohorts.items():
        for unit in ids:
            env=envelopes.get((bed,unit));cells={};unit_values={}
            for arm in ARMS:
                entry=env['arms'][arm] if env else None
                status=entry.get('execution_status') if entry else 'missing'
                cell={'generation_status':status,'missing_reason':'unresolved_0007' if ':TRAIN-SET:0007:' in unit else 'generation_not_available' if entry is None else None,
                    'generation_entry':entry,'semantic_error_codes':{k:None for k in ISSUES}}
                cells[arm]=cell;v={m:None for m in METRICS[bed]}
                if env:
                    accounting=env.get('token_budget_accounting',{}).get(arm,{})
                    if accounting.get('budget_unit')=='generated_tokens' and type(accounting.get('tokens_used')) is int:
                        v['generated_tokens']=accounting['tokens_used']
                if entry and status=='succeeded':
                    native=evaluations.get((bed,unit,'train_evaluation',None),{})
                    if native:
                        if native.get('generation_input_set_id')!=unit:raise ValueError('TRAIN metric source identity mismatch')
                        metric=native.get('evaluations',{}).get(arm,{})
                        v['heldout_accuracy']=scalar(metric,['heldout','heldout_accuracy','parsed_output','accuracy'])
                        v['HDR']=scalar(metric,['hdr','hypothesis_discovery_rate'])
                    if (unit,arm) in hdr_values:
                        if v['HDR'] is not None and v['HDR']!=hdr_values[unit,arm]:raise ValueError('conflicting completed HDR scores')
                        v['HDR']=hdr_values[unit,arm]
                    reconstruction=evaluations.get((bed,unit,'literature_reconstruction',None),{})
                    v.update(reconstruction_metrics(reconstruction,unit,arm))
                    v.update(secondary_metrics(evaluations.get((bed,unit,'secondary',arm),{}),entry,unit))
                unit_values[arm]=v
            def metric_status(arm,metric):
                if unit_values[arm].get(metric) is not None:return 'succeeded' if bed=='literature' else 'evaluated'
                if cells[arm]['generation_status']!='succeeded' and metric!='generated_tokens':return 'generation_missing_or_failed'
                if arm in ('D','D-empty','D-shuffled') and (metric.startswith('type_') or metric in ('already_asked_rate','research_question_best_similarity','same_question_fraction')):
                    return 'not_applicable_questionless_arm'
                return 'pending_metric'
            for metric in METRICS[bed]:
                if bed=='data':
                    normalized[bed][metric].append({'generation_input_set_id':unit,'evaluations':{arm:{'status':metric_status(arm,metric),'metrics':{metric:unit_values[arm].get(metric)}} for arm in ARMS}})
                else:
                    normalized[bed][metric].append({'input_set_id':unit,'records':[{'input_set_id':unit,'stage':'verified_input_set_scalar','evaluation_input':{'field':metric},'provenance':{'arm':arm},'status':metric_status(arm,metric),'parsed_output':{'value':unit_values[arm].get(metric)}} for arm in ARMS]})
            if unit in chosen[bed]:
                packet={'testbed':bed,'input_set_id':unit,'source_evidence':source_rows[bed][unit],
                    'arms':cells,'evaluation_metrics':unit_values,'call_history_file_hashes':histories if bed=='data' else {},
                    'human_review_completed':False}
                packet['packet_sha256']=digest(packet);packets.append(packet)
    review=review_status(packets,reviews or [])
    output.mkdir(parents=True,exist_ok=False);(output/'packets').mkdir();(output/'statistics').mkdir()
    analyses={};stats_index={}
    for bed in cohorts:
        for metric in METRICS[bed]:
            result=summarize_metric(normalized[bed][metric],bed,metric,config,evaluation)
            analyses[bed,metric]=result;filename=f'{bed}_{metric}.json'
            write_analysis_exclusive(output/'statistics'/filename,result)
            stats_index[bed+':'+metric]={'path':'statistics/'+filename,'file_sha256':file_digest(output/'statistics'/filename)}
    forms=[];md=['# Fixed 20-set end-to-end error review','',
        'One actual reviewer per set. Read original evidence, all seven arm outputs, intermediate artifacts/call histories and available evaluation results. Blank semantic codes are pending, never negative judgments.','']
    for packet in packets:
        bed,unit=packet['testbed'],packet['input_set_id'];name=bed+'_'+digest(unit)[:16]+'.json';save(output/'packets'/name,packet)
        forms.append({'testbed':bed,'input_set_id':unit,'packet_sha256':packet['packet_sha256'],'reviewer_id':None,'reviewed_at_utc':None,
            'end_to_end_review_completed':False,'notes':None,'arms':{arm:{'status':'pending_review',**{k:None for k in ISSUES},'notes':None,'examples':[]} for arm in ARMS}})
        md.extend(['## '+bed+' / '+unit,'','Packet: `packets/'+name+'`',''])
        for arm,cell in packet['arms'].items():
            md.extend(['### '+arm+' — '+str(cell['generation_status']),''])
            entry=cell['generation_entry'] or {}
            hypotheses=(entry.get('output') or {}).get('hypotheses',[])
            if not hypotheses:md.extend(['No successful six-hypothesis output: '+str(cell['missing_reason'] or entry.get('missing_output') or cell['generation_status']),''])
            for hypothesis in hypotheses:md.append('- '+hypothesis['text'])
            md.extend(['','Error codes, actual quote/explanation, reviewer notes: PENDING',''])
    save(output/'human_error_review_pending.json',forms);save(output/'human_error_review_status.json',review)
    (output/'error_review_sheet.md').write_text('\n'.join(md))
    summary={'schema_version':'e6-error-analysis-and-memo-v1','sample':chosen,'sample_size':20,'human_review':review,
        'planned_units':{b:len(ids) for b,ids in cohorts.items()},'statistics':stats_index,'runtime':runtime,
        'generation_checkpoints_found':len(envelopes),'explicit_evaluation_artifacts_found':len(evaluations),
        'source_artifact_hashes':provenance,'TRAIN_call_history_hashes':histories,
        'frozen_file_hashes':{p:file_digest(root/p) for p in ('E6/config.json','E6/evaluation_config.json','E6/PREREG.md')},
        'HDR_compilation':str(hdr_compilation) if hdr_compilation is not None else None,
        'HDR_cells_supplied':len(hdr_values),'implementation_sha256':file_digest(Path(__file__)),'model_calls':0,'TEST_evaluation':False,
        'report_status':'provisional_pending_outcomes_and_human_reviews'}
    save(output/'analysis.json',summary);(output/'memo_one_page.md').write_text(memo_text(summary,analyses))
    save(output/'completed_artifact_index_template.json',{'artifacts':[],
        'accepted_kinds':['generation_checkpoint','train_evaluation','literature_reconstruction','secondary'],
        'required_fields':['testbed','input_set_id','kind','path','file_sha256'],'secondary_additional_field':'arm',
        'instruction':'Index completed stable artifacts only. Do not index reference extraction or an actively written run.'})
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--hdr-compilation',type=Path);p.add_argument('--artifact-index',type=Path);p.add_argument('--reviews',type=Path);args=p.parse_args()
    r=build(args.output_dir,artifact_index=json.loads(args.artifact_index.read_text()) if args.artifact_index else None,
        reviews=json.loads(args.reviews.read_text()) if args.reviews else None,hdr_compilation=args.hdr_compilation)
    print(json.dumps({'selected_error_review_sets':r['sample_size'],'reviews_completed':r['human_review']['reviewed_input_sets'],
        'testbeds':r['planned_units'],'saved_generation_checkpoints':r['generation_checkpoints_found'],
        'saved_evaluation_artifacts':r['explicit_evaluation_artifacts_found'],'model_calls':0},indent=2))

if __name__=='__main__':main()
