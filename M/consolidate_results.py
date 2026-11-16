"""Deterministically consolidate registered status without promoting development outputs."""
import argparse,json
from pathlib import Path
TESTS=('I1','I3','S1','A1','H1','H3','O1','O2','T1')
def build(root='.'):
 root=Path(root);ledger=json.loads((root/'M/results/stage5/results.json').read_text()); by={x['test']:x for x in ledger.get('tests',[])}
 tests=[]
 for t in TESTS:
  receipt=root/f'M/data/ingestion_v2/{t}_status.json';d=json.loads(receipt.read_text()) if receipt.exists() else {}
  e=by.get(t,{})
  executed=bool(e.get('executed')) and e.get('status')=='COMPLETED'
  tests.append({'test':t,'registered_status':'COMPLETED' if executed else 'BLOCKED','eligible_records':e.get('eligible_records',d.get('eligible_records',0)),'executed':executed,'metrics':e.get('metrics') if executed else None,'ci95':e.get('ci95') if executed else None,'blockers':[] if executed else e.get('blockers',d.get('missing_dependencies',[]))})
 dev=[]
 for path in sorted((root/'M/results').glob('generated_development_*/results.json')):
  x=json.loads(path.read_text());dev.append({'path':str(path.relative_to(root)),'classification':'DEVELOPMENT_ONLY','registered_finding':False,'summary':x.get('summary'),'metrics':x.get('metrics')})
 return {'schema':'M-results-consolidation-v1','registered_evaluations':tests,'completed_registered_count':sum(x['executed'] for x in tests),'blocked_registered_count':sum(not x['executed'] for x in tests),'development_only':dev,'synthetic_tests_are_findings':False,'missing_evidence':['Eligible source-bound cohorts and controls for blocked tests','Genuine labels and/or verified human annotations required by each test']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--out',default='M/results/consolidated_v1/summary.json');a=p.parse_args();out=Path(a.root)/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(build(a.root),indent=2,sort_keys=True)+'\n');print(out)
if __name__=='__main__':main()
