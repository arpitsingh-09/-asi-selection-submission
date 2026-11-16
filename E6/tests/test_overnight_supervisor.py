"""Offline supervisor safety checks; no inference or signals to live TEST."""
import fcntl
import json
from pathlib import Path
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import overnight_supervisor as s
import run_heldout_optimized as r


class SupervisorTests(unittest.TestCase):
    def test_incomplete_completion_marker_does_not_block_resume(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s, 'OUTPUT', Path(tmp)):
            output = Path(tmp)
            (output / 'launch_completed.json').write_text(json.dumps({
                'phase': 'heldout_accuracy', 'status': 'phase_completed',
                'full_evaluation_complete': False}))
            (output / 'heldout_phase_summary.json').write_text(json.dumps({
                'evaluation_phase': 'heldout_accuracy', 'full_evaluation_complete': False,
                'generation_sets': []}))
            self.assertFalse(s.fully_complete())

    def test_consistent_full_completion_marker_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s, 'OUTPUT', Path(tmp)):
            output = Path(tmp)
            (output / 'launch_completed.json').write_text(json.dumps({
                'phase': 'heldout_accuracy', 'status': 'phase_completed',
                'full_evaluation_complete': True}))
            cells = [{'generation_input_set_id': f'set-{i // 7}',
                      'evaluated_arms': [f'arm-{i}']} for i in range(125)]
            (output / 'heldout_phase_summary.json').write_text(json.dumps({
                'evaluation_phase': 'heldout_accuracy', 'full_evaluation_complete': True,
                'generation_sets': cells}))
            self.assertTrue(s.fully_complete())

    def test_missing_or_malformed_completion_evidence_fails_open_to_resume(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s, 'OUTPUT', Path(tmp)):
            output = Path(tmp)
            self.assertFalse(s.fully_complete())
            (output / 'launch_completed.json').write_text('{malformed')
            self.assertFalse(s.fully_complete())

    def test_battery_states_and_unknown_fail_closed(self):
        for raw, percent, status in [("Now drawing from 'AC Power'\n -InternalBattery-0 43%; charging;",43,'charging'),
                                     ("Now drawing from 'Battery Power'\n 20%; discharging;",20,'discharging')]:
            with patch.object(s.subprocess,'check_output',return_value=raw):
                self.assertEqual(s.battery()['percent'],percent)
                self.assertEqual(s.battery()['status'],status)
        with patch.object(s.subprocess,'check_output',return_value='unknown'):
            with self.assertRaises(RuntimeError):s.battery()

    def test_execution_lock_detection_preserves_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'execution.lock';path.write_text('preserve')
            with path.open() as guard:
                fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
                self.assertTrue(s.locked(path))
            self.assertFalse(s.locked(path));self.assertEqual(path.read_text(),'preserve')

    def test_worker_finishes_current_and_never_starts_next(self):
        handlers={};calls=[]
        class Cache:
            def __call__(self,*args,**kwargs):
                calls.append('current')
                handlers[signal.SIGINT]()
                calls.append('completed_checkpoint')
        def main():
            cache=r.ExactRequestCache()
            cache('first')
            cache('forbidden next')
        original=r.ExactRequestCache
        with patch.object(r,'ExactRequestCache',Cache), patch.object(r,'main',side_effect=main), \
             patch.object(s.signal,'signal',side_effect=lambda sig,fn:handlers.update({sig:fn})), \
             patch.object(s,'event') as events, patch.object(sys,'argv',[]):
            s.worker()
            self.assertEqual(calls,['current','completed_checkpoint'])
            events.assert_called_with('cooperative_stop_checkpoints_preserved')
        self.assertIs(r.ExactRequestCache,original)

    def test_attach_never_launches_test_and_releases_awake(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(s,'STATE',Path(tmp)), patch.object(s,'preflight'), \
             patch.object(s,'owner',side_effect=[123,123,123,123,None]), \
             patch.object(s,'battery',return_value={'percent':20,'status':'discharging'}), \
             patch.object(s,'event') as events, patch.object(s.os,'kill') as kill, \
             patch.object(s.subprocess,'Popen') as popen, patch.object(s.time,'sleep'), \
             patch.object(s.signal,'signal'):
            popen.return_value.poll.return_value=None
            s.supervise()
            self.assertEqual(popen.call_count,1)
            self.assertEqual(popen.call_args.args[0],['/usr/bin/caffeinate','-i','-w','123'])
            self.assertEqual(kill.call_args_list[-1].args,(123,signal.SIGINT))
            self.assertEqual(kill.call_count,2)
            popen.return_value.terminate.assert_called_once()
            self.assertTrue(any(c.args[0]=='sleep_prevention_released' for c in events.call_args_list))

    def test_signal_permission_denied_refuses_supervision(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s,'STATE',Path(tmp)), \
             patch.object(s,'owner',return_value=123), patch.object(s,'preflight') as preflight, \
             patch.object(s.os,'kill',side_effect=PermissionError('denied')), \
             patch.object(s.subprocess,'Popen') as popen:
            with self.assertRaises(PermissionError):s.supervise()
            preflight.assert_not_called();popen.assert_not_called()

    def test_natural_exit_releases_awake_without_signal(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s,'STATE',Path(tmp)), \
             patch.object(s,'preflight'), patch.object(s,'owner',side_effect=[123,123,None]), \
             patch.object(s,'event'), patch.object(s.os,'kill') as kill, \
             patch.object(s.subprocess,'Popen') as popen, patch.object(s.signal,'signal'):
            s.supervise();kill.assert_called_once_with(123,0);popen.return_value.terminate.assert_called_once()

if __name__=='__main__':unittest.main()
