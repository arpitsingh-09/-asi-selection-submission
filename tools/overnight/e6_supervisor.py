"""Mac overnight lifecycle wrapper; frozen E6 sources are only imported, never edited."""
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'E6/runs/heldout_accuracy_optimized_v1'
STATE = Path(__file__).resolve().parent


class GracefulStop(BaseException):
    pass


def log(message):
    print(message, flush=True)


def battery_percent():
    result = subprocess.run(['/usr/bin/pmset', '-g', 'batt'], check=True,
                            capture_output=True, text=True, timeout=15)
    values = re.findall(r'(\d+)%;', result.stdout)
    if not values or any(not 0 <= int(v) <= 100 for v in values):
        raise RuntimeError('Cannot read battery safely: ' + result.stdout)
    return min(map(int, values))


def monitor(stop, done):
    while not done.is_set():
        try:
            percent = battery_percent()
            log(f'Battery: {percent}%')
            if percent <= 20:
                log('Battery threshold reached; draining current batch before stopping.')
                stop.set()
                return
        except Exception as exc:
            log(f'Battery monitor unavailable; requesting safe stop: {exc}')
            stop.set()
            return
        if done.wait(60):
            return


def guarded_factory(factory, stop):
    def create(*args, **kwargs):
        predictor = factory(*args, **kwargs)
        original = predictor.predict_many

        def predict_many(*args, **kwargs):
            # The previous call has returned and its batch checkpoint was written.
            # Never raise after inference: allow its reply and checkpoint to persist.
            if stop.is_set():
                raise GracefulStop()
            return original(*args, **kwargs)

        predictor.predict_many = predict_many
        return predictor
    return create


def main():
    with (STATE / 'supervisor.lock').open('a') as own_lock:
        fcntl.flock(own_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stop, done = threading.Event(), threading.Event()
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, lambda *_: stop.set())
        # Refuse to start inference without functioning battery telemetry.
        initial = battery_percent()
        if initial <= 20:
            log(f'Battery {initial}%: TEST not started.')
            return 0
        sys.path.insert(0, str(ROOT / 'E6'))
        import run_heldout_optimized as runner
        binding = runner.read(OUTPUT / 'run_binding.json')
        # Check the existing execution lock before any runtime/model request.
        with (OUTPUT / 'execution.lock').open('r') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        awake = subprocess.Popen(['/usr/bin/caffeinate', '-i', '-w', str(os.getpid())])
        thread = threading.Thread(target=monitor, args=(stop, done), daemon=True)
        status, code = 'failed', 1
        try:
            if awake.poll() is not None:
                raise RuntimeError('caffeinate failed to start')
            thread.start()
            config, evaluation, context, plan = runner.prepare()
            if stop.is_set():
                raise GracefulStop()
            log(f'TEST starting/resuming; supervisor PID {os.getpid()}')
            (STATE / 'status.json').write_text(json.dumps({
                'status': 'running', 'pid': os.getpid(),
                'sleep_prevention_released': False}) + '\n')
            with patch.object(runner, 'make_hypobench_prediction_policy',
                              guarded_factory(runner.make_hypobench_prediction_policy, stop)):
                runner.execute(config, evaluation, context, plan, binding['source'], OUTPUT,
                               binding['workers'], binding['unresolved_policy'])
            status, code = 'completed', 0
        except GracefulStop:
            status, code = 'stopped_between_batches', 0
            log('TEST stopped after preserving the active batch.')
        except BaseException:
            traceback.print_exc()
        finally:
            done.set()
            if thread.ident is not None:
                thread.join()
            # execute() has unwound, joining batch workers and closing its lock.
            with (OUTPUT / 'execution.lock').open('r') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                log('TEST exited; execution lock verified released.')
            awake.terminate()
            awake.wait()
            (STATE / 'status.json').write_text(json.dumps({
                'status': status, 'pid': os.getpid(), 'sleep_prevention_released': True,
                'execution_lock_released': True}, indent=2) + '\n')
            log(f'Supervisor finished: {status}; sleep prevention released.')
        return code


if __name__ == '__main__':
    sys.exit(main())
