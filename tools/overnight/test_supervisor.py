import threading
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
import e6_supervisor as s


class SupervisorTests(unittest.TestCase):
    def test_completion_and_stop_release_execution_lock_and_caffeinate(self):
        for outcome in (None, s.GracefulStop()):
            with tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                (directory / 'execution.lock').touch()
                runner = Mock()
                runner.read.return_value = {'source': 'fixture', 'workers': 1,
                                            'unresolved_policy': 'retain-invalid'}
                runner.prepare.return_value = (1, 2, 3, 4)
                def execute(*args):
                    with (directory / 'execution.lock').open('r') as lock:
                        s.fcntl.flock(lock, s.fcntl.LOCK_EX | s.fcntl.LOCK_NB)
                        if outcome is not None:
                            raise outcome
                runner.execute.side_effect = execute
                awake = Mock()
                awake.poll.return_value = None
                with patch.dict(sys.modules, {'run_heldout_optimized': runner}), \
                     patch.object(s, 'STATE', directory), patch.object(s, 'OUTPUT', directory), \
                     patch.object(s, 'battery_percent', return_value=50), \
                     patch.object(s.subprocess, 'Popen', return_value=awake), \
                     patch.object(s.signal, 'signal'):
                    self.assertEqual(s.main(), 0)
                awake.terminate.assert_called_once()
                awake.wait.assert_called_once()
                status = s.json.loads((directory / 'status.json').read_text())
                self.assertTrue(status['execution_lock_released'])
                self.assertTrue(status['sleep_prevention_released'])

    def test_active_batch_returns_predictions_then_next_batch_stops(self):
        stop = threading.Event()
        def finish_batch(*args, **kwargs):
            stop.set()  # threshold reached during inference
            return ['completed prediction']
        predictor = Mock(predict_many=Mock(side_effect=finish_batch))
        wrapped = s.guarded_factory(lambda: predictor, stop)()
        self.assertEqual(wrapped.predict_many(['row']), ['completed prediction'])
        with self.assertRaises(s.GracefulStop):
            wrapped.predict_many(['next row'])
        self.assertEqual(predictor.predict_many.__name__, 'predict_many')

    def test_battery_threshold_and_sixty_second_interval(self):
        stop, done = threading.Event(), Mock()
        done.is_set.return_value = False
        done.wait.return_value = False
        with patch.object(s, 'battery_percent', side_effect=[21, 20]):
            s.monitor(stop, done)
        self.assertTrue(stop.is_set())
        done.wait.assert_called_once_with(60)

    def test_telemetry_failure_requests_safe_stop(self):
        stop, done = threading.Event(), threading.Event()
        with patch.object(s, 'battery_percent', side_effect=RuntimeError('missing')):
            s.monitor(stop, done)
        self.assertTrue(stop.is_set())

    def test_pmset_parsing_and_invalid_telemetry(self):
        for output, expected in [('InternalBattery-0 20%; discharging', 20),
                                 ('InternalBattery-0 100%; charged', 100)]:
            with patch.object(s.subprocess, 'run', return_value=Mock(stdout=output)):
                self.assertEqual(s.battery_percent(), expected)
        with patch.object(s.subprocess, 'run', return_value=Mock(stdout='No battery')):
            with self.assertRaises(RuntimeError):
                s.battery_percent()


if __name__ == '__main__':
    unittest.main()
