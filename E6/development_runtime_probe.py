"""Minimal, resumable DEVELOPMENT-only 32768-context / 2048-output probe.

No TRAIN/TEST/EVALUATION inputs accepted, no seven-arm experiment run, no
configuration or approval mutation. Each completed step is written exclusively.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from ollama_adapter import OllamaModelClient
from profile_development_token_budget import load_development_manifest
from development_profile_runner import _load_verified_source_rows
from question_pipeline import _read_prompt, _render
from researcher_approval import digest, file_digest
from token_budget import PerArmTokenBudget, TokenBudgetError
from verify_gemma3_local import _request_json, tokenizer_metadata_summary

ROOT = Path(__file__).resolve().parent
SETTINGS = {'model': 'gemma3:12b', 'temperature': 0.0, 'top_p': 1.0,
            'seed': 2026, 'num_ctx': 32768, 'num_predict': 2048}


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        handle.write('\n')


def measured_context_guard(preflight):
    """Negative software test using real measured tokens; no extra model call."""
    class MustNotRun:
        generation_options = {'num_ctx': preflight['input_tokens'] + 2047, 'num_predict': 2048}
        def call_with_token_limit(self, *args, **kwargs):
            raise AssertionError('overflow generation must never run')
    ledger = PerArmTokenBudget('development-runtime-guard', 8192, None,
        model_prompt_counter=lambda stage, prompt: preflight, budget_unit='generated_tokens')
    try:
        ledger.invoke(MustNotRun(), 'D_generation', 'same measured probe prompt')
    except TokenBudgetError:
        return {'passed': bool(ledger.blocked_calls) and ledger.blocked_calls[-1]['status'] == 'context_overflow',
                'test_kind': 'software_negative_test_using_measured_prompt_count',
                'configured_negative_context': MustNotRun.generation_options['num_ctx'],
                'generated_cap_unchanged': ledger.cap,
                'blocked_calls': ledger.blocked_calls}
    return {'passed': False}


def run_probe(output_dir, *, request=_request_json, client_factory=OllamaModelClient):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest, manifest_sha = load_development_manifest()
    _load_verified_source_rows(manifest['inputs'])
    record = max(manifest['inputs'], key=lambda r: (len(r['abstract']), r['paper_id']))
    verification = json.loads((ROOT / 'data/gemma3_local_verification_v1.json').read_text())
    identity = digest({'settings': SETTINGS, 'manifest_sha256': manifest_sha,
                       'verification_sha256': file_digest(ROOT / 'data/gemma3_local_verification_v1.json'),
                       'probe_implementation_sha256': file_digest(Path(__file__)),
                       'development_prompt_template_sha256': file_digest(ROOT.parent / 'prompts/e6/01_generator_D.txt'),
                       'development_profile_config_sha256': file_digest(ROOT / 'development_profile_config.json')})
    report = {'schema_version': 'e6-development-runtime-probe-v1',
              'scope': 'DEVELOPMENT_only_runtime_verification', 'confirmatory_experiment': False,
              'approval_mutation': False, 'settings': SETTINGS, 'run_identity': identity,
              'development_manifest_sha256': manifest_sha, 'development_input_id': record['paper_id'],
              'started_at_utc': datetime.now(timezone.utc).isoformat(), 'steps': {}}

    def step(name, action):
        path = output_dir / (name + '.json')
        if path.exists():
            stored = json.loads(path.read_text())
            unsigned = {k: v for k, v in stored.items() if k != 'checkpoint_sha256'}
            if stored.get('run_identity') != identity or stored.get('checkpoint_sha256') != digest(unsigned):
                raise ValueError('checkpoint source/settings/hash changed: ' + name)
            result = stored['result']
        else:
            result = action()
            stored = {'run_identity': identity, 'step': name, 'result': result}
            stored['checkpoint_sha256'] = digest(stored)
            write_new(path, stored)
        report['steps'][name] = result
        return result

    try:
        def runtime_identity():
            version = request('/api/version')
            tags = request('/api/tags')
            model = next((r for r in tags.get('models', []) if r.get('name') == SETTINGS['model'] or r.get('model') == SETTINGS['model']), None)
            if not model:
                raise ValueError('verified Gemma tag unavailable')
            expected_digest = verification['digest_verification']['api_tags_digest_raw']
            if model.get('digest', '').removeprefix('sha256:') != expected_digest.removeprefix('sha256:'):
                raise ValueError('Gemma tag digest changed since saved verification')
            show = request('/api/show', {'model': SETTINGS['model'], 'verbose': True})
            fingerprint = tokenizer_metadata_summary(show)['metadata_sha256']
            if fingerprint != verification['tokenizer']['metadata_sha256']:
                raise ValueError('runtime tokenizer fingerprint changed')
            return {'ollama_version': version.get('version'), 'tag_digest': model['digest'],
                    'tokenizer_metadata_sha256': fingerprint}
        live_identity = runtime_identity()
        recorded_identity = step('01_identity', lambda: live_identity)
        if recorded_identity != live_identity:
            raise ValueError('live runtime identity changed since checkpoint; use a new probe directory')
        client = client_factory(model=SETTINGS['model'], timeout_seconds=600,
            generation_options={k: v for k, v in SETTINGS.items() if k != 'model'})
        task = json.loads((ROOT / 'development_profile_config.json').read_text())['generic_task_text']
        actual_prompt = _render(_read_prompt('prompts/e6/01_generator_D.txt'),
                                DOMAIN_AND_TASK=task, EVIDENCE=record['abstract'])

        def count(prompt):
            # Dedicated DEVELOPMENT count at the tested context. Unlike the
            # production conservative-byte admission path, this controlled probe
            # checks the measured token headroom explicitly and performs no arm generation.
            result = client._call('DEVELOPMENT_runtime_token_count', prompt,
                                  {**client.generation_options, 'num_predict': 1}, 1)
            inp, out = result.get('input_tokens'), result.get('output_tokens')
            if type(inp) is not int or type(out) is not int or out not in (0, 1) or result.get('total_tokens') != inp + out or result.get('adapter_metadata', {}).get('done') is not True:
                raise ValueError('runtime returned inconsistent prompt/output token counts')
            result['token_count_preflight'] = {'method': 'ollama_prompt_eval_count_with_num_predict_one',
                'requested_num_predict': 1, 'bounded_probe_confirmed': True}
            return result
        normal = step('02_development_prompt_count', lambda: count(actual_prompt))
        if normal['input_tokens'] + 2048 > 32768:
            raise ValueError('actual DEVELOPMENT prompt does not fit proposed context/output')
        # Long controlled padding tests actual context use; the sole source
        # evidence remains the bound DEVELOPMENT abstract, never held-out data.
        pressure_prompt = ('DEVELOPMENT runtime capacity test. Return JSON with key items containing '
            'the consecutive integers 1 through 50000. Do not stop until all are present. '
            'The following is diagnostic context, not an experimental task.\n'
            + record['abstract'] + '\nPadding:' + ' x' * 28500
            + '\nNow emit the entire requested integer array as JSON.')
        long_count = step('03_long_context_count', lambda: count(pressure_prompt))
        if not 24576 <= long_count['input_tokens'] <= 30720:
            raise ValueError('controlled padding did not establish 24576–30720 actual prompt tokens; no automatic extra inference')
        pressure = step('04_output_pressure', lambda: client.call_with_token_limit(
            'DEVELOPMENT_runtime_output_pressure', pressure_prompt, max_output_tokens=2048))
        ps = step('05_runtime_allocation', lambda: request('/api/ps'))
        models = [r for r in ps.get('models', []) if r.get('name') == SETTINGS['model'] or r.get('model') == SETTINGS['model']]
        allocated = max((r.get('context_length', 0) for r in models if type(r.get('context_length')) is int), default=0)
        output_honored = pressure.get('output_tokens') == 2048 and pressure.get('adapter_metadata', {}).get('done_reason') in ('length', 'max_tokens', 'token_limit')
        parity = pressure.get('input_tokens') == long_count['input_tokens']
        guard = step('06_context_guard', lambda: measured_context_guard(long_count))
        report.update(status='passed' if allocated >= 32768 and output_honored and parity and guard['passed'] else 'inconclusive',
            actual_development_prompt_tokens=normal['input_tokens'], actual_long_prompt_tokens=long_count['input_tokens'],
            actual_output_tokens=pressure.get('output_tokens'), context_allocation=allocated,
            output_limit_verified=output_honored, prompt_accounting_parity=parity, context_guard_verified=guard['passed'],
            limit='Verifies this DEVELOPMENT probe only, not all workflow completions or evaluation prompt distributions.')
    except Exception as exc:
        report.update(status='blocked_or_failed', error_type=type(exc).__name__, error=str(exc),
                      actual_development_prompt_tokens=None if '02_development_prompt_count' not in report['steps'] else report['steps']['02_development_prompt_count']['input_tokens'])
    report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    report['report_sha256'] = digest(report)
    # Preserve each attempt's report; successful checkpoints can be reused.
    index = 1
    while (output_dir / f'report_{index:02d}.json').exists(): index += 1
    write_new(output_dir / f'report_{index:02d}.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    report = run_probe(args.output_dir)
    summary = {k: report[k] for k in ('status', 'actual_development_prompt_tokens', 'actual_long_prompt_tokens',
               'actual_output_tokens', 'context_allocation', 'output_limit_verified', 'prompt_accounting_parity',
               'context_guard_verified', 'error') if k in report}
    summary['report_file'] = str(max(args.output_dir.glob('report_*.json'), key=lambda p: int(p.stem.split('_')[-1])).resolve())
    print(json.dumps(summary, indent=2))
    return 0 if report['status'] == 'passed' else 2


def validate_runtime_evidence(config, *, root):
    """Final execution requires real, source-bound evidence for its exact limits."""
    if not isinstance(config, dict) or not isinstance(config.get('generation'), dict):
        return ['runtime verification: invalid generation configuration']
    gen = config.get('generation', {})
    relative = gen.get('development_runtime_probe_report')
    expected_sha = gen.get('development_runtime_probe_report_sha256')
    if not relative or not expected_sha:
        return ['runtime verification: DEVELOPMENT context/output report not registered']
    from researcher_approval import safe_path
    try:
        path = safe_path(root, relative)
        report = json.loads(path.read_text())
        if file_digest(path) != expected_sha or report.get('report_sha256') != digest({k: v for k, v in report.items() if k != 'report_sha256'}):
            return ['runtime verification: report file/content hash mismatch']
        if (report.get('status') != 'passed' or report.get('scope') != 'DEVELOPMENT_only_runtime_verification'
                or report.get('confirmatory_experiment') is not False
                or report.get('settings', {}).get('model') != gen.get('model')
                or report.get('settings', {}).get('num_ctx') != gen.get('context_limit')
                or report.get('settings', {}).get('num_predict') != gen.get('max_output_tokens')
                or report.get('development_manifest_sha256') != file_digest(Path(root) / 'E6/data/development_manifest_v2.json')
                or not all(report.get(key) is True for key in ('output_limit_verified', 'prompt_accounting_parity', 'context_guard_verified'))):
            return ['runtime verification: report does not establish frozen Gemma settings on DEVELOPMENT data']
        manifest = json.loads((Path(root) / 'E6/data/development_manifest_v2.json').read_text())
        if report.get('development_input_id') not in {row['paper_id'] for row in manifest['inputs']}:
            return ['runtime verification: probe source is not DEVELOPMENT']
        original = json.loads((Path(root) / 'E6/data/gemma3_local_verification_v1.json').read_text())
        steps = report.get('steps', {})
        runtime = steps.get('01_identity', {})
        if (runtime.get('tag_digest', '').removeprefix('sha256:') != original['digest_verification']['api_tags_digest_raw'].removeprefix('sha256:')
                or runtime.get('tokenizer_metadata_sha256') != original['tokenizer']['metadata_sha256']
                or runtime.get('ollama_version') != gen.get('backend_version')):
            return ['runtime verification: model/tokenizer/backend identity differs from frozen evidence']
        if (steps.get('02_development_prompt_count', {}).get('input_tokens') != report.get('actual_development_prompt_tokens')
                or steps.get('03_long_context_count', {}).get('input_tokens') != report.get('actual_long_prompt_tokens')
                or steps.get('04_output_pressure', {}).get('input_tokens') != report.get('actual_long_prompt_tokens')
                or steps.get('04_output_pressure', {}).get('output_tokens') != report.get('actual_output_tokens')
                or steps.get('04_output_pressure', {}).get('adapter_metadata', {}).get('done_reason') not in ('length', 'max_tokens', 'token_limit')):
            return ['runtime verification: summary differs from actual recorded probe counts']
        normal = report.get('actual_development_prompt_tokens')
        long_count = report.get('actual_long_prompt_tokens')
        if (type(normal) is not int or type(long_count) is not int or long_count < 24576
                or long_count + gen['max_output_tokens'] > gen['context_limit']
                or report.get('actual_output_tokens') != gen['max_output_tokens']
                or report.get('context_allocation', 0) < gen['context_limit']):
            return ['runtime verification: actual prompt/output/context counts do not fit required limits']
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return ['runtime verification: invalid or missing DEVELOPMENT evidence']
    return []


if __name__ == '__main__':
    raise SystemExit(main())
