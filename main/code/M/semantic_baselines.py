"""Frozen question/abstract vectors only; no inference or score-to-vector conversion."""
import hashlib
from pathlib import Path
import numpy as np
from .evidence import verify_assertion
from .schema import date
from .encoders import CachedEncoder,MissingEmbeddingError

class SemanticBaselines:
    def __init__(self,path,*,model_evidence=None):
        self.encoder=CachedEncoder(path);self.path=str(Path(path).resolve());self.model_evidence=model_evidence
        if model_evidence is not None:
            for key in ('training_through','model_id'):verify_assertion(model_evidence[key])
            if date(model_evidence['training_through']['value'])>=date('2024-01-01'):raise ValueError('semantic model trained after 2023')
            if not self.encoder.space_id.startswith(model_evidence['model_id']['value']):raise ValueError('cutoff evidence belongs to another model')
    def vector(self,text,kind='B-Q'):
        if kind not in ('B-Q','B-ABS'):raise ValueError('semantic vector baseline required')
        v=self.encoder.encode(text)
        return {'baseline':kind,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'space_id':self.encoder.space_id,'cache_path':self.path,'vector':list(v),
            'vector_sha256':hashlib.sha256(np.asarray(v,dtype='<f4').tobytes()).hexdigest(),
            'training_cutoff_verified':bool(self.model_evidence),
            'training_cutoff_evidence':self.model_evidence}
    def similarity(self,a,b):
        x=self.vector(a);y=self.vector(b)
        return {'cosine':float(np.clip(np.dot(x['vector'],y['vector']),-1,1)),
            'space_id':x['space_id'],'text_hashes':[x['text_sha256'],y['text_sha256']]}
    def close(self):self.encoder.close()


def readiness(manifest,cache):
    import json
    reader=SemanticBaselines(cache);counts={'records':0,'exact_B_Q_vectors':0,'exact_B_ABS_vectors':0,'model_cutoff_verified':False,'inference_calls':0};missing=[]
    try:
        with Path(manifest).open() as f:
            for line in f:
                r=json.loads(line);counts['records']+=1
                for kind,key,count in [('B-Q','question','exact_B_Q_vectors'),('B-ABS','abstract','exact_B_ABS_vectors')]:
                    if not r.get(key):continue
                    try:reader.vector(r[key],kind);counts[count]+=1
                    except MissingEmbeddingError:missing.append({'question_id':r['question_id'],'baseline':kind,'text_sha256':hashlib.sha256(r[key].encode()).hexdigest()})
    finally:reader.close()
    return dict(counts,missing=missing)
