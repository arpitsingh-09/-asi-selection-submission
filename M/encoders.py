"""Explicit lightweight or cached embedding backends; never infer/download."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import numpy as np
from E5.diversity import hashed_vectors


class MissingEmbeddingError(KeyError):pass


def valid(vector,dimension):
    v=np.asarray(vector,dtype=np.float32)
    if v.shape!=(dimension,) or not np.isfinite(v).all():raise ValueError('invalid cached embedding')
    length=float(np.linalg.norm(v.astype(np.float64)))
    if not np.isfinite(length) or length<=0:raise ValueError('invalid cached embedding norm')
    return (v.astype(np.float64)/length).astype(np.float32)


class HashEncoder:
    kind='lexical_proxy_not_sentence_model'
    dimension=512
    space_id='e5-fixed-nonnegative-word-bigram-hash-512-v1'
    @lru_cache(maxsize=4096)
    def encode(self,text):
        v=hashed_vectors([text],self.dimension)[0]
        return tuple(float(x) for x in valid(v,self.dimension))


class CachedEncoder:
    """Exact JSON vectors or the existing E2 SQLite reader, strictly read-only."""
    kind='frozen_sentence_embedding'
    def __init__(self,path):
        self.path=Path(path);self.reader=None
        if self.path.suffix in ('.sqlite3','.sqlite','.db'):
            # Reuse the existing reader without importing its evaluator/model code.
            module_path=Path(__file__).resolve().parents[1]/'E2/cached_extensions.py'
            # Its lightweight helper imports need E2 on sys.path. Use the package
            # reader through a small isolated source extraction instead of executing
            # the top-level evaluator and its unrelated absolute imports.
            import ast,sqlite3
            tree=ast.parse(module_path.read_text())
            cache_class=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Cache')
            scope={'sqlite3':sqlite3,'hashlib':hashlib,'json':json,'np':np,'MODEL':'specter2_base+proximity-adapter+cls-v1'}
            exec(compile(ast.Module(body=[cache_class],type_ignores=[]),str(module_path),'exec'),scope)
            self.reader=scope['Cache'](self.path)
            self.dimension=768;self.space_id='specter2_base+proximity-adapter+cls-v1:cache-only'
            self.records=None
        else:
            obj=json.loads(self.path.read_text())
            if not obj.get('model_id') or not obj.get('revision') or type(obj.get('dimension')) is not int:raise ValueError('cache model/revision/dimension required')
            self.dimension=obj['dimension'];self.space_id=obj['model_id']+'@'+obj['revision']
            self.records={}
            for r in obj['records']:
                h=hashlib.sha256(r['text'].encode()).hexdigest()
                if r.get('sha256')!=h or h in self.records:raise ValueError('cache hash/duplicate mismatch')
                self.records[h]=(r['text'],valid(r['vector'],self.dimension))

    def encode(self,text):
        if self.reader is not None:
            try:v=self.reader.get(text)
            except KeyError as e:raise MissingEmbeddingError('no exact cached text; inference disabled') from e
        else:
            r=self.records.get(hashlib.sha256(text.encode()).hexdigest())
            if r is None:raise MissingEmbeddingError('no exact cached text; inference disabled')
            if r[0]!=text:raise ValueError('cache text binding mismatch')
            v=r[1]
        return tuple(float(x) for x in valid(v,self.dimension))

    def close(self):
        if self.reader is not None:self.reader.close()
