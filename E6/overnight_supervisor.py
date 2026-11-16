"""macOS E6 supervisor. Events live outside experiment outputs.

Existing uninstrumented TEST: SIGINT is the safe fallback at low battery; the
in-flight attempt may be interrupted and must never be retried. New launches
install a cooperative request-boundary stop without changing frozen files.
"""
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'E6/runs/heldout_accuracy_v1'
OUTPUT = ROOT / 'E6/runs/heldout_accuracy_optimized_v1'
STATE = ROOT / 'E6/supervision'
COMMAND = ['python3', 'E6/run_heldout_optimized.py', '--source', str(SOURCE),
           '--output-dir', str(OUTPUT), '--workers', '1',
           '--unresolved-policy', 'retain-invalid', '--execute']


def battery():
    raw = subprocess.check_output(['/usr/bin/pmset', '-g', 'batt'], text=True, timeout=10)
    match = re.search(r'(\d+)%;\s*([^;\n]+)', raw)
    if not match:
        raise RuntimeError('Cannot determine battery state')
    return {'percent': int(match[1]), 'status': match[2].strip(),
            'ac_power': "'AC Power'" in raw}


def holders(path):
    result = subprocess.run(['/usr/sbin/lsof', '-n', '-Fpc', str(path)],
                            text=True, capture_output=True, timeout=15)
    if result.returncode not in (0, 1) or result.stderr.strip():
        raise RuntimeError('Cannot identify execution lock owner: ' + result.stderr)
    return {int(line[1:]) for line in result.stdout.splitlines() if line.startswith('p')}


def locked(path):
    with path.open('r') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        return False


def owner():
    path = OUTPUT / 'execution.lock'
    if not locked(path):
        return None
    pids = holders(path)
    if len(pids) != 1:
        raise RuntimeError('Ambiguous execution lock ownership')
    return pids.pop()


def event(kind, **values):
    with (STATE / 'events.jsonl').open('a') as handle:
        handle.write(json.dumps({'time': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                                 'supervisor_pid': os.getpid(), 'event': kind, **values}) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def fully_complete():
    """Accept completion only when the marker and durable summary agree."""
    marker_path = OUTPUT / 'launch_completed.json'
    summary_path = OUTPUT / 'heldout_phase_summary.json'
    try:
        marker = json.loads(marker_path.read_text())
        summary = json.loads(summary_path.read_text())
    except (OSError, ValueError, TypeError):
        return False
    if (marker.get('phase') != 'heldout_accuracy'
            or marker.get('status') != 'phase_completed'
            or marker.get('full_evaluation_complete') is not True
            or summary.get('evaluation_phase') != 'heldout_accuracy'
            or summary.get('full_evaluation_complete') is not True):
        return False
    sets = summary.get('generation_sets')
    if not isinstance(sets, list):
        return False
    cells = set()
    for item in sets:
        if not isinstance(item, dict) or not isinstance(item.get('generation_input_set_id'), str):
            return False
        arms = item.get('evaluated_arms')
        if not isinstance(arms, list) or not all(isinstance(arm, str) for arm in arms):
            return False
        for arm in arms:
            cell = (item['generation_input_set_id'], arm)
            if cell in cells:
                return False
            cells.add(cell)
    # E6's frozen heldout plan contains 125 evaluable arm cells.
    return len(cells) == 125


def preflight(*, attaching=False):
    from run_heldout_optimized import prepare, check_run_binding
    from test_readiness import readiness
    from run_literature_extraction import verify_live_identity
    report = readiness(phase='heldout_accuracy')
    if report['status'] != 'READY':
        raise RuntimeError(str(report['mandatory_blockers']))
    config, _, _, plan = prepare()
    check_run_binding(OUTPUT / 'run_binding.json', {'plan': plan, 'source': str(SOURCE),
                      'workers': 1, 'unresolved_policy': 'retain-invalid'})
    try:
        live = verify_live_identity(config)
    except RuntimeError as exc:
        # A sandbox-denied identity read must never permit new inference startup.
        # Attaching only adds battery protection to an already running TEST.
        if not attaching or 'Operation not permitted' not in str(exc):
            raise
        event('live_identity_unavailable_attach_only', error=str(exc))
        live = None
    prior = json.loads((SOURCE / 'actual_runtime_identity.json').read_text())
    for section, key in [('version', 'version'), ('tag', 'digest'), ('tokenizer', 'metadata_sha256')]:
        if live is not None and live[section][key] != prior[section][key]:
            raise RuntimeError('Source live identity mismatch')
    state = battery()
    if state['percent'] <= 20:
        raise RuntimeError('Battery must be above 20%')
    event('preflight_pass', battery=state, gates=report['gates'], live_identity=live)


class GracefulStop(BaseException):
    pass


def worker():
    # Keep the existing command/parser and all hashed experiment files intact.
    import run_heldout_optimized as runner
    stopping = []
    signal.signal(signal.SIGINT, lambda *_: stopping.append(True))
    original = runner.ExactRequestCache.__call__

    def guarded(self, *args, **kwargs):
        if stopping:
            raise GracefulStop()
        return original(self, *args, **kwargs)

    runner.ExactRequestCache.__call__ = guarded
    sys.argv = COMMAND[1:]
    try:
        runner.main()
    except GracefulStop:
        event('cooperative_stop_checkpoints_preserved')


def supervise():
    STATE.mkdir(exist_ok=True)
    with (STATE / 'supervisor.lock').open('a') as guard:
        fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        pid = owner()
        if pid is not None:
            # Permission probe only; signal 0 never changes TEST state.
            # Refuse an overnight safety claim if low-battery SIGINT is denied.
            os.kill(pid, 0)
        preflight(attaching=pid is not None)
        if pid != owner():
            raise RuntimeError('Execution owner changed during preflight; rerun required')
        child = None
        cooperative = False
        if pid is None:
            # Existing execution locks remain the final authority over launch races.
            if locked(SOURCE / 'execution.lock'):
                raise RuntimeError('Source TEST still running')
            if fully_complete():
                event('already_complete')
                return
            log = (STATE / ('test-%s.log' % time.time_ns())).open('x')
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker'],
                                     cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                     start_new_session=True)
            log.close()
            pid = child.pid
            cooperative = True
            event('launched', test_pid=pid, command=COMMAND)
            for _ in range(120):
                if child.poll() is not None:
                    raise RuntimeError('TEST exited during startup')
                actual = owner()
                if actual == pid:
                    break
                if actual is not None:
                    raise RuntimeError('Another TEST won the execution lock')
                time.sleep(1)
            else:
                raise RuntimeError('TEST did not acquire execution lock')
        else:
            event('attached', test_pid=pid, cooperative=False,
                  stop_policy='SIGINT; in-flight attempt may be interrupted; never retried')
        # -i prevents idle system sleep on battery too; -w ties assertion to TEST.
        awake = subprocess.Popen(['/usr/bin/caffeinate', '-i', '-w', str(pid)],
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
        event('active', test_pid=pid, caffeinate_pid=awake.pid, cooperative=cooperative)
        stop = False

        def request_stop(reason):
            nonlocal stop
            if not stop and owner() == pid:
                event('stop_requested', reason=reason, test_pid=pid, cooperative=cooperative)
                os.kill(pid, signal.SIGINT)
                stop = True

        signal.signal(signal.SIGTERM, lambda *_: request_stop('supervisor_sigterm'))
        signal.signal(signal.SIGINT, lambda *_: request_stop('supervisor_sigint'))
        try:
            next_check = 0
            while owner() == pid:
                if awake.poll() is not None:
                    request_stop('sleep_prevention_lost')
                if time.monotonic() >= next_check:
                    try:
                        state = battery()
                        event('battery', test_pid=pid, **state)
                        if state['percent'] <= 20:
                            request_stop('battery_at_or_below_20')
                    except Exception as exc:
                        event('battery_error', error=str(exc))
                        request_stop('battery_unreadable')
                    next_check = time.monotonic() + 60
                time.sleep(1)
            if child:
                child.wait()
            event('test_exited', test_pid=pid, stop_requested=stop,
                  natural_completion=fully_complete())
        finally:
            awake.terminate()
            awake.wait()
            event('sleep_prevention_released', test_pid=pid)


if __name__ == '__main__':
    if sys.argv[1:] == ['--worker']:
        worker()
    else:
        try:
            supervise()
        except BaseException as exc:
            if STATE.exists():
                event('supervisor_error', error=repr(exc))
            raise
