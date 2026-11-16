import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from run_baseline import JsonExport


class ExportTests(unittest.TestCase):
    def test_numpy_scalars_round_trip_without_changing_values(self):
        data={'passed':np.bool_(True),'count':np.int64(3),'score':np.float64(.125)}
        self.assertEqual(json.loads(JsonExport.dumps(data,allow_nan=False)),{'passed':True,'count':3,'score':.125})

    def test_nonfinite_and_unknown_types_fail(self):
        with self.assertRaises(ValueError):JsonExport.dumps({'bad':float('nan')},allow_nan=False)
        with self.assertRaises(TypeError):JsonExport.dumps({'bad':object()},allow_nan=False)
