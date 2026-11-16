import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from abstract_embeddings import prepare,encode_one,local_encoder

class AbstractPreparationTests(unittest.TestCase):
    def test_inventory_does_not_create_vectors(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'new';r=prepare([{'forum_id':'a','abstract':'only abstract'}],out,0)
            self.assertEqual(r['remaining'],1);self.assertFalse((out/'abstract_cls.sqlite3').exists())
    def test_raw_cls_resume_and_exact_text(self):
        calls=[]
        def encoder(s):calls.append(s);return np.full(768,2.)
        inputs=[{'forum_id':'a','abstract':'abstract one'},{'forum_id':'b','abstract':'abstract two'}]
        with tempfile.TemporaryDirectory() as tmp:
            r=prepare(inputs,Path(tmp),1,encoder);self.assertEqual(r['remaining'],1)
            r=prepare(inputs,Path(tmp),1,encoder);self.assertEqual(r['remaining'],0)
            r=prepare(inputs,Path(tmp),1,encoder);self.assertEqual(len(calls),2)
            self.assertEqual(calls,['abstract one','abstract two'])
        self.assertEqual(encode_one('a',encoder)[0],2.) # raw CLS, no normalization
    def test_invalid_encoder_rejected(self):
        for vector in [np.zeros(767),np.full(768,np.nan)]:
            with self.assertRaises(ValueError):encode_one('a',lambda _:vector)
    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):prepare([{'forum_id':'a'},{'forum_id':'a'}],Path(tmp),0)
    def test_priority_denial_precedes_model_loading(self):
        with patch('abstract_embeddings.os.nice',side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):local_encoder(Path('/not/a/model'))
