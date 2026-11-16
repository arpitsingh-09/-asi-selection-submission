"""Apply explicit Codex AI semantic review to recovered source candidates.
This records AI judgments, never human judgments or new claim text. No scoring.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

# Candidate indices refer to claim_recovery_v1/all_additional_candidates.
# Minimal additions: seek four claims without inflating counts via restatements.
PROMOTE={'2012.15515v1':[0],'2012.15525v3':[1],'2012.15793v1':[0],
 '2401.00907v1':[0],'2610.29216v1':[0],'2012.15245v1':[0],
 '2101.00973v1':[1],'2302.01921v1':[1],'2401.00237v1':[2],
 '2512.23953v2':[4],'2512.24947v1':[0],'2601.00905v1':[3],'2512.24564v1':[0]}
REASONS={
 '2012.15515v1':['Distinct sourced background assertion about NMT adoption.','Organizational statement about future discussion, not an additional scientific assertion.','Resource-summary organization, not an additional scientific assertion.'],
 '2012.15525v3':['Quantifies the original NAR improvement claim.','Distinct semi-NAR baseline comparison, beyond original NAR result.','Restates original BANG objective.','Compound and partly repeats existing performance claim.'],
 '2012.15793v1':['Distinct sourced background result on linearized graph transformers.','Restates original local-structure/invariance claim.'],
 '2112.11391v1':['Quoted study intention alone does not establish improvement; also overlaps originals.','Quantifies original WER-reduction result rather than a distinct claim.','Research motivation, not an additional result.','Restates separated-front-end comparison.'],
 '2112.13634v1':['Overlaps original survey scope.','Repeats original language coverage.','Survey organization rather than distinct scientific assertion.'],
 '2112.14330v1':['Restates original simple/interpretable/stable description.'],
 '2201.02735v1':['Vague efficiency statement without a distinct substantive result.','Overlaps original chatbot-understanding objective.'],
 '2312.17025v3':['Restates original learning-framework description.'],
 '2401.00907v1':['Distinct in-domain QA performance result, beyond feedback objective and data-fraction effect.'],
 '2412.20846v2':['Restates original high-probability answer observation.'],
 '2610.29216v1':['Distinct cross-rater disagreement observation; original learner accuracy is within-person.'],
 '2610.30132v1':['Restates original evidence expansion step.'],
 '2012.15245v1':['Distinct background claim about clinical boundary information; not a new claimed contribution.','Evidence truncates architecture name and does not fully support the architecture claim.','Compound restatement of original training setup and metrics.','Challenge/dataset context, not promoted as an extra paper contribution.'],
 '2101.00973v1':['Compound background statement; prefer more specific saved single-method claim.','Distinct description of prior differentiable-module substitution.','Restates original limitations addressed.'],
 '2302.00595v1':['Restates original survey scope and algorithm range.'],
 '2302.01921v1':['Overlaps original growing attention to transformers.','Distinct self-attention-only architecture property.','Background NLP success; target already met using the more direct architecture claim.'],
 '2401.00237v1':['Broad restatement of the proposed detection methodology.','Additional implementation detail; target met using distinct validation-design claim.','Distinct five-fold validation design.','Compound restatement with deployment implication.','Additional synthetic-data detail; target already met.'],
 '2412.20666v2':['Combines existing synthetic result with new comparison; not an atomic addition as saved.'],
 '2412.20872v2':['Restates original pseudo-label prior.','Restates original modality-adjustment mechanism.'],
 '2512.23953v2':['Restates original evaluation.','Restates original study scope and objectives.','Restates original semantic/temporal objectives.','Truncated evidence and restated study scope.','Distinct iterative word-perturbation mechanism.'],
 '2512.24947v1':['Distinct judge-driven caption-refinement mechanism.','Equivalent to chosen caption-refinement claim.'],
 '2601.00905v1':['Restates original recyclability prediction objective.','Repeats original contamination/damage scenarios.','Repeats original location-guideline scenario.','Distinct multi-material evaluation scenario.'],
 '2610.29176v1':['Overlaps original redundancy-reduction motivation.','Compound background limitations, not a distinct added result.'],
 '2512.24564v1':['Distinct invariant-morphology versus noncausal-artifact separation property.']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent
    source=root/'analysis/claim_recovery_v1/candidates.jsonl';selected=root/'data/claims_v8_selected.jsonl'
    raw={r['paper_id']:r for r in map(json.loads,(root/'data/raw_papers.jsonl').read_text().splitlines())}
    records=list(map(json.loads,source.read_text().splitlines()));original=list(map(json.loads,selected.read_text().splitlines()))
    updated=copy.deepcopy(original);byid={r['paper_id']:r for r in updated};reviews=[]
    for r in records:
        pid=r['paper_id'];all_c=r['all_additional_candidates']
        if all_c and len(REASONS[pid])!=len(all_c):raise ValueError('review/source index mismatch')
        choices=PROMOTE.get(pid,[])
        additions=[all_c[i] for i in choices]
        if len(r['original_claims'])+len(additions)>4:raise ValueError('excess additions')
        for i,c in enumerate(all_c):
            reviews.append({'paper_id':pid,'candidate_index':i,'claim':c['claim'],
                'decision':'promote_for_future_use' if i in choices else 'not_promoted',
                'reason':REASONS[pid][i],'reviewer':'Codex AI','human_review':False,
                'source':c['source'],'line':c['line']})
        if additions:
            target=byid[pid]
            target['claims']=target['claims']+[{'claim':c['claim'],'evidence':c['evidence']} for c in additions]
            target['claim_count']=len(target['claims'])
            old_audit={k:v for k,v in target.items() if k.startswith('audit_')}
            target['audit_exact_evidence']=sum(c['evidence'] in raw[pid]['abstract'] for c in target['claims'])
            target['audit_invalid_evidence']=len(target['claims'])-target['audit_exact_evidence']
            target['continuation_review']={'reviewer':'Codex AI','human_review':False,
                'source':str(source.relative_to(root)),'additions':additions,'original_audit':old_audit,
                'status':'AI_semantic_support_review_only_original_manual_review_requirements_unchanged'}
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/'review.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in reviews))
    (a.output/'claims_future.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in updated))
    summary={'reviewer':'Codex AI','human_review':False,'candidate_occurrences_reviewed':len(reviews),
        'promoted_claims':sum(len(v) for v in PROMOTE.values()),'papers_with_promoted_claims':len(PROMOTE),
        'short_sets_now_reaching_four':sum(len(byid[r['paper_id']]['claims'])>=4 for r in records),
        'short_sets_still_below_four':sum(len(byid[r['paper_id']]['claims'])<4 for r in records),
        'future_sets_with_4_to_10':sum(4<=len(r['claims'])<=10 for r in updated),
        'selected_source_sha256':hashlib.sha256(selected.read_bytes()).hexdigest(),
        'recovery_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'used_in_evaluation':False,'limitation':'Original and recovered claims are not independently human validated; background assertions are identified explicitly.'}
    (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

if __name__=='__main__':main()
