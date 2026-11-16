"""Bounded single-thread CPU encoding from an existing local MiniLM snapshot only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import subprocess

MODEL='sentence-transformers/all-MiniLM-L6-v2'
REVISION='1110a243fdf4706b3f48f1d95db1a4f5529b4d41'
MAX_TEXTS=256


def validate_requests(obj):
    texts=obj['texts']
    if not isinstance(texts,list) or not 1<=len(texts)<=MAX_TEXTS or len(set(texts))!=len(texts):raise ValueError('1–256 unique text requests required')
    if any(not isinstance(s,str) or not s.strip() or len(s)>3000 for s in texts):raise ValueError('bounded nonempty text required')
    if obj.get('count')!=len(texts):raise ValueError('request count mismatch')
    return texts


def encode(requests,out,snapshot=None):
    requests=Path(requests);out=Path(out)
    if out.exists():raise FileExistsError('sidecar cannot overwrite existing data')
    texts=validate_requests(json.loads(requests.read_text()))
    root=Path(__file__).resolve().parents[1]
    lock_path=root/'M/amendments/S1_encoder_preparation_lock.json'
    lock=json.loads(lock_path.read_text())
    for name in lock['committed_files']:
        path=root/name
        committed=subprocess.check_output(['git','show','HEAD:'+name],cwd=root)
        if committed!=path.read_bytes() or hashlib.sha256(committed).hexdigest()!=lock['committed_files'][name]:raise ValueError('preparation code/protocol/requests must be committed unchanged')
    lock_committed=subprocess.check_output(['git','show','HEAD:M/amendments/S1_encoder_preparation_lock.json'],cwd=root)
    if lock_committed!=lock_path.read_bytes():raise ValueError('encoder lock is not committed unchanged')
    if hashlib.sha256(requests.read_bytes()).hexdigest()!=lock['request_sha256']:raise ValueError('requests differ from committed preparation lock')
    snapshot=Path(snapshot) if snapshot else Path.home()/f'.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/{REVISION}'
    if snapshot.name!=REVISION:raise ValueError('exact preregistered snapshot required')
    names=('config.json','modules.json','model.safetensors','tokenizer.json','tokenizer_config.json','1_Pooling/config.json','sentence_bert_config.json')
    if any(not (snapshot/n).is_file() for n in names):raise FileNotFoundError('incomplete local-only snapshot; downloads forbidden')
    for name,h in lock['model_files'].items():
        if hashlib.sha256((snapshot/name).read_bytes()).hexdigest()!=h:raise ValueError('local model bytes differ from prospective lock')
    config=json.loads((snapshot/'config.json').read_text())
    if config.get('num_hidden_layers')!=6 or config.get('hidden_size')!=384:raise ValueError('bounded MiniLM architecture required')
    if (snapshot/'model.safetensors').stat().st_size>100_000_000:raise ValueError('model exceeds lightweight bound')
    modules=json.loads((snapshot/'modules.json').read_text())
    if any(m['type'] not in ('sentence_transformers.models.Transformer','sentence_transformers.models.Pooling','sentence_transformers.models.Normalize') for m in modules):raise ValueError('unapproved local model module')
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
    import torch
    from sentence_transformers import SentenceTransformer
    import numpy as np
    torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(20261113)
    model=SentenceTransformer(str(snapshot),device='cpu',local_files_only=True,trust_remote_code=False)
    model.max_seq_length=128;model.eval()
    lengths=[len(model.tokenizer(s,truncation=False)['input_ids']) for s in texts]
    if max(lengths)>128:raise ValueError('question exceeds token cap; do not silently truncate')
    start=time.monotonic();vectors=[]
    with torch.inference_mode():
        for i in range(0,len(texts),4):
            if time.monotonic()-start>30:raise RuntimeError('CPU budget exceeded; no cache saved')
            vectors.extend(model.encode(texts[i:i+4],batch_size=4,normalize_embeddings=True,show_progress_bar=False,convert_to_numpy=True))
    v=np.asarray(vectors,dtype=np.float32)
    if v.shape!=(len(texts),384) or not np.isfinite(v).all() or not np.allclose(np.linalg.norm(v,axis=1),1,atol=1e-4):raise ValueError('invalid encoder vectors')
    artifact={'model_id':MODEL,'revision':REVISION,'dimension':384,'training_cutoff_verified':False,
        'purpose':'Frozen B-Q vector preparation; no label or metric evaluation',
        'request_file_sha256':hashlib.sha256(requests.read_bytes()).hexdigest(),
        'model_file_hashes':{n:hashlib.sha256((snapshot/n).read_bytes()).hexdigest() for n in names},
        'runtime':{'device':'cpu','threads':1,'batch_size':4,'max_seq_length':128,'max_input_tokens':max(lengths),
                   'torch':torch.__version__,'elapsed_encoding_seconds':time.monotonic()-start},
        'records':[{'text':s,'sha256':hashlib.sha256(s.encode()).hexdigest(),'vector':[float(x) for x in a]} for s,a in zip(texts,v)]}
    with out.open('x') as f:json.dump(artifact,f,allow_nan=False)
    return {'vectors':len(texts),'dimension':384,'device':'cpu','training_cutoff_verified':False,'evaluations':0}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--requests',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(encode(a.requests,a.out)))
