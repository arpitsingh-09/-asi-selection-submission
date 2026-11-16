"""Rebuild the Stage 5 results ledger from committed, existing M evidence."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent

def load(p):return json.loads((ROOT/p).read_text())
def main():
    ing=load('M/data/ingestion_v2/summary.json');s1=load('M/data/s1_review_v3/summary.json')
    q=load('M/results/quality_v2/validation_results.json');man=load('M/data/manifests_v2/manifest_report.json')
    statuses={t:load(f'M/data/ingestion_v2/{t}_status.json') for t in ('I1','I3','S1','A1','H1','H3','O1','O2','T1')}
    rows=[]
    for t,x in statuses.items():rows.append({'test':t,'status':'BLOCKED','eligible_records':0,'executed':False,'metrics':None,'ci95':None,'baseline_comparison':None,'blockers':x['missing_dependencies']})
    e1=ROOT/'E1/results_v2/source_alignment_audit.csv'
    with e1.open() as f:audit=list(csv.DictReader(f))
    vectors=json.loads((ROOT/'M/data/s1_review_v3/minilm_vectors.json').read_text())
    examples=[]
    with (ROOT/'E1/contrast.jsonl').open() as f:
        for line in f:
            r=json.loads(line)
            if r['id']=='h001':
                examples=[{'kind':'illustrative E1 pair; no human label','item_id':r['id'],'source_arxiv':r['source_arxiv'],
                    'candidate_A':r['A'],'candidate_B_min':r['B_min'],'candidate_C':r['C'],
                    'verified_status':'source_alignment_audit says PENDING_MANUAL_CONFIRMATION; excluded from all metrics'}];break
    desc={'s1_pairs_prepared':s1['pairs'],'s1_focal_questions':s1['focal_questions'],'s1_human_confirmed':s1['human_verified_pairs'],
        'e1_pending_manual_confirmation':sum(r['abstract_review_status']=='PENDING_MANUAL_CONFIRMATION' for r in audit),
        'cpu_semantic_vectors':len(vectors['records']),'vector_dimension':vectors['dimension'],'encoding_seconds':vectors['runtime']['elapsed_encoding_seconds'],
        'review_scores_recovered':ing['genuine_source_review_values'],'review_paper_identity_links':ing['paper_identity_links'],
        'review_public_observation_dates':ing['verified_public_observation_dates'],'question_linked_usable_labels':ing['usable_question_linked_labels'],
        'quality_models_fitted':sum(x['status']=='fitted' for x in q['heads'].values()),
        'train_records':man['counts']['train'],'validation_records':man['counts']['validation'],'heldout_candidates_manifest_only':man['counts']['test'],
        'heldout_evaluations':0,'examples':examples}
    result={'schema':'M-stage5-ledger-v1','evaluations_executed':0,'blocked_count':len(rows),'tests':rows,
        'descriptive_results':desc,'confidence_intervals':None,'interpretation':'Descriptive counts and encoder preparation only; no predictive or scientific validation.'}
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    md=['# Stage 5 results ledger','', 'No experimental evaluation was eligible or executed. Every numerical value below is an artifact count or offline preparation measurement, not a scientific performance result. No confidence intervals are available.','', '| Test | Status | Eligible | Metrics / CI | Exact blockers |','|---|---|---:|---|---|']
    for r in rows:md.append(f"| {r['test']} | BLOCKED | 0 | None | {'; '.join(r['blockers'])} |")
    md += ['', '## Reproducible descriptive results','',f"- S1: {s1['pairs']} source-bound pairs across {s1['focal_questions']} questions; {s1['human_verified_pairs']} human-confirmed.",f"- E1: {desc['e1_pending_manual_confirmation']} alignment labels remain pending manual confirmation.",f"- Review archive: {ing['genuine_source_review_values']} genuine recommendation values and {ing['paper_identity_links']} paper identity links recovered; zero public observation dates and zero usable question-linked labels.",f"- Cached MiniLM preparation: {len(vectors['records'])} CPU vectors, dimension {vectors['dimension']}; {vectors['runtime']['elapsed_encoding_seconds']:.3f}s encode loop. These were not used to score an evaluation.",f"- Quality training: 0 heads fit from {man['counts']['train']} train and {man['counts']['validation']} validation records; no genuine outcome labels.",f"- Heldout: {man['counts']['test']} metadata candidates only; zero eligible/evaluated.",'', '## Illustrative error-analysis example','',f"E1 item {examples[0]['item_id']} ({examples[0]['source_arxiv']}) pairs “{examples[0]['candidate_A']}” with minimal paraphrase “{examples[0]['candidate_B_min']}” and near-miss proposal “{examples[0]['candidate_C']}”. The source alignment audit marks this item pending manual confirmation. It illustrates the annotation question only; it is not a verified label, model error, or scored example.",'', '## Reproduction','', 'From repository root:','', '```sh','OPENBLAS_NUM_THREADS=1 .venv/bin/python -B M/results/stage5/build_report.py','.venv/bin/python -B -m unittest M.tests.test_space M.tests.test_training M.tests.test_evaluation M.tests.test_ingestion M.tests.test_s1_workflow -q','```','', 'The first command reads committed manifests/results and writes the deterministic ledger. The second runs the existing focused M tests; it does not run evaluations or model inference.','']
    (OUT/'RESULTS.md').write_text('\n'.join(md))
if __name__=='__main__':main()
