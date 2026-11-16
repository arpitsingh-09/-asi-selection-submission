"""Offline submission export from verified, completed TRAIN sources only."""
import argparse
import json
from pathlib import Path
from execution_preparation import export_generation_records, write_jsonl_exclusive
from hdr_pipeline import checked_forms
from researcher_approval import ROOT, file_digest


def package(output):
    output=Path(output)
    forms,terminal=checked_forms(ROOT)
    paths=sorted({r['generation_checkpoint'] for r in forms})
    sources={};rows=[];failures=[]
    for relative in paths:
        path=ROOT/relative;saved=json.loads(path.read_text());envelope=saved['envelope']
        seed=envelope['model_configuration']['generation_options']['seed']
        exported,failed=export_generation_records(envelope,testbed='data',seed=seed)
        rows.extend(exported);failures.extend(failed);sources[relative]=file_digest(path)
    if len(rows)!=750 or len(failures)!=8 or len(terminal)!=15:
        raise ValueError('completed TRAIN inventory differs from prepared evidence')
    identities={(r['input_set_id'],r['arm'],r['hypothesis_id']) for r in rows}
    if len(identities)!=750:raise ValueError('duplicate generation records')
    # Only explicit stable result directories; never enumerate held-out run files.
    for directory in ('E6/data/evaluator_validation_train_v2','E6/data/evaluator_validation_train_v2_finalized',
                      'E6/data/literature_evidence_finalized_v1','E6/data/error_analysis_memo_v2',
                      'E6/data/hdr_scoring_v3'):
        for path in sorted((ROOT/directory).rglob('*')):
            if path.is_file():sources[str(path.relative_to(ROOT))]=file_digest(path)
    for pattern in ('*.py','*.json','*.md','*.txt'):
        for path in sorted((ROOT/'E6').glob(pattern)):
            sources[str(path.relative_to(ROOT))]=file_digest(path)
    for path in sorted((ROOT/'E6/tests').glob('test_*.py')):
        sources[str(path.relative_to(ROOT))]=file_digest(path)
    output.mkdir(parents=True,exist_ok=False)
    prompt_dir=output/'prompts';prompt_dir.mkdir()
    for path in sorted((ROOT/'prompts/e6').rglob('*')):
        if not path.is_file():continue
        target=prompt_dir/path.relative_to(ROOT/'prompts/e6');target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(path.read_bytes());sources[str(path.relative_to(ROOT))]=file_digest(path)
    write_jsonl_exclusive(output/'generations.jsonl',rows)
    write_jsonl_exclusive(output/'failed_generation_cells.jsonl',failures)
    write_jsonl_exclusive(output/'terminal_missing_cells.jsonl',terminal)
    memo=(ROOT/'E6/data/error_analysis_memo_v2/memo_one_page.md').read_text()
    memo=memo.replace('provisional one-page draft','provisional submission snapshot')
    memo+='\n**Submission status.** Literature extraction: 100/100 verified, with 40 independent source reviews still pending. Evaluator pilot: 16/16 responses verified, 0/10 independent judgments. HDR: 0/125 scored. Held-out accuracy is running separately; its partial outputs are excluded. Literature seven-arm experiments and 20-case end-to-end human coding are incomplete. These gaps prevent a defensible benefit or deployment recommendation.\n'
    (output/'memo_one_page.md').write_text(memo)
    manifest={'status':'incomplete_submission_snapshot','generation_records':len(rows),'successful_arm_cells':125,
        'failed_arm_cells':len(failures),'unresolved_set_0007_arm_cells':7,'literature_arm_generations_included':0,
        'existing_artifact_sha256':sources,'model_calls':0,'running_TEST_accessed':False,
        'scope':'Use with the repository root, including prompts/e6 and data source dependencies. Stable originals remain in place; this is an indexed submission, not a standalone execution archive.',
        'exclusions':['Active E6/runs/heldout_accuracy_v1 is deliberately not read, hashed, copied or packaged. Include only after completion and reconciliation.'],
        'packaged_file_sha256':{str(p.relative_to(output)):file_digest(p) for p in sorted(output.rglob('*')) if p.is_file()}}
    with (output/'manifest.json').open('x') as handle:json.dump(manifest,handle,indent=2,sort_keys=True)
    return {k:manifest[k] for k in ('status','generation_records','successful_arm_cells','failed_arm_cells','unresolved_set_0007_arm_cells','model_calls','running_TEST_accessed')}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    print(json.dumps(package(parser.parse_args().output_dir),indent=2))
