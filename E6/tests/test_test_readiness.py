"""No inference: integrity and seven-arm terminal checkpoint tests."""
import copy
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_readiness import checked_checkpoint
from evaluation import ARMS
from researcher_approval import digest

class ReadinessTests(unittest.TestCase):
    def saved(self):
        value={'context_sha256':'fixed','envelope':{'arms':{arm:{'execution_status':'failed'} for arm in ARMS}}}
        value['checkpoint_sha256']=digest(value)
        return value
    def test_partial_failure_retains_all_arms(self):
        saved=self.saved(); original=copy.deepcopy(saved)
        self.assertEqual(set(checked_checkpoint(saved,SimpleNamespace(context_sha256='fixed'))['arms']),set(ARMS))
        self.assertEqual(saved,original)
    def test_tampering_blocks(self):
        saved=self.saved();saved['envelope']['arms']['D']['execution_status']='succeeded'
        with self.assertRaisesRegex(ValueError,'checksum'): checked_checkpoint(saved,SimpleNamespace(context_sha256='fixed'))
    def test_other_context_blocks(self):
        with self.assertRaisesRegex(ValueError,'context'): checked_checkpoint(self.saved(),SimpleNamespace(context_sha256='other'))
    def test_missing_arm_blocks_even_with_valid_checksum(self):
        saved=self.saved();del saved['envelope']['arms']['D-empty'];del saved['checkpoint_sha256'];saved['checkpoint_sha256']=digest(saved)
        with self.assertRaisesRegex(ValueError,'seven arms'): checked_checkpoint(saved,SimpleNamespace(context_sha256='fixed'))

if __name__=='__main__':unittest.main()

class LauncherTests(unittest.TestCase):
    def test_blocked_readiness_never_constructs_or_executes_client(self):
        import tempfile
        from unittest.mock import patch
        import run_confirmatory_test as runner
        with tempfile.TemporaryDirectory() as tmp:
            hdr=Path(tmp)/'hdr.json';hdr.write_text('{}')
            output=Path(tmp)/'out'
            with patch.object(sys,'argv',['runner','--hdr-inputs',str(hdr),'--output-dir',str(output)]), patch.object(runner,'readiness',return_value={'status':'BLOCKED','mandatory_blockers':['fixture missing real review']}), patch.object(runner,'execute',side_effect=AssertionError('inference')):
                self.assertEqual(runner.main(),2)
                self.assertFalse(output.exists())

    def test_interrupted_call_never_reissued(self):
        import tempfile
        import run_confirmatory_test as runner
        class Client:
            def __init__(self):self.calls=0
            def _call(self,*args):self.calls+=1;raise RuntimeError('fixture transport failure')
        with tempfile.TemporaryDirectory() as tmp:
            client=Client();runner.journal(client,Path(tmp))
            with self.assertRaises(RuntimeError):client._call('s','p',{},32)
            replay=Client();runner.journal(replay,Path(tmp))
            with self.assertRaisesRegex(RuntimeError,'terminal'):replay._call('s','p',{},32)
            self.assertEqual(client.calls,1);self.assertEqual(replay.calls,0)
