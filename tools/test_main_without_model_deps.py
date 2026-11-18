"""Run Main Problem unit tests when inference dependencies are not installed.

This adds import-only sentinels for missing torch/transformers/adapters modules.
Any attempted model loading raises immediately. It validates software logic and
input adapters only; it does not validate embeddings, model inference, scoring,
or any experiment.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest
import os

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


def _unavailable(name: str):
    class MissingInferenceDependency:
        def __init__(self, *args, **kwargs):
            raise RuntimeError(f"{name} is unavailable; inference is disabled in this runner")
    return MissingInferenceDependency


if importlib.util.find_spec("torch") is None:
    sys.modules["torch"] = types.ModuleType("torch")

if importlib.util.find_spec("transformers") is None:
    module = types.ModuleType("transformers")
    module.AutoTokenizer = _unavailable("transformers")
    sys.modules["transformers"] = module

if importlib.util.find_spec("adapters") is None:
    module = types.ModuleType("adapters")
    module.AutoAdapterModel = _unavailable("adapters")
    sys.modules["adapters"] = module

suite = unittest.defaultTestLoader.discover(str(ROOT / "M" / "tests"), pattern="test_*.py")
result = unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
