"""Resumable abstract-only preparation with pinned local models; no evaluation.

Default inventory only. Positive --max-new encodes that many HISTORICAL records
on CPU, one thread, with lowered process priority and no model downloads.
Each raw CLS vector is stored separately from the original novelty cache.
Test embedding preparation is deliberately not exposed until dates are verified.
"""
import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path
import numpy as np
from human_check import historical

BASE_REV='3447645e1def9117997203454fa4495937bfbd83'
ADAPTER_REV='2081559630a80fc5851d8f798a05ba81e9468089'
PROVENANCE={'encoder':'allenai/specter2_base','encoder_revision':BASE_REV,
 'adapter':'allenai/specter2','adapter_revision':ADAPTER_REV,'input':'abstract_only',
 'pooling':'CLS','max_length':512,'frozen':True,'normalization':'none','device':'cpu'}

def input_digest(text):return hashlib.sha256(text.encode()).hexdigest()

def encode_one(text,encoder):
    """Reject nonfinite/wrong-shape data; raw CLS vectors are not normalized."""
    result=np.asarray(encoder(text),dtype=np.float32)
    if result.shape!=(768,) or not np.isfinite(result).all():raise ValueError('invalid abstract embedding')
    return result

def local_encoder(hub):
    # Refuse to load weights if low-priority CPU execution cannot be established.
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',
                      OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    os.nice(15)
    import torch
    from transformers import AutoTokenizer
    from adapters import AutoAdapterModel
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    base=hub/'models--allenai--specter2_base'/'snapshots'/BASE_REV
    adapter=hub/'models--allenai--specter2'/'snapshots'/ADAPTER_REV
    if not (base/'pytorch_model.bin').exists() or not (adapter/'pytorch_adapter.bin').exists():
        raise FileNotFoundError('pinned local model assets missing')
    tokenizer=AutoTokenizer.from_pretrained(str(base),local_files_only=True)
    model=AutoAdapterModel.from_pretrained(str(base),local_files_only=True).to('cpu')
    model.load_adapter(str(adapter),load_as='proximity',set_active=True)
    model.set_active_adapters('proximity');model.eval()
    def encode(s):
        inputs=tokenizer(s,truncation=True,padding=True,max_length=512,return_tensors='pt')
        with torch.inference_mode():return model(**inputs).last_hidden_state[0,0,:].float().cpu().numpy()
    return encode

def prepare(records,output,max_new,encoder=None):
    if max_new<0:raise ValueError('negative preparation limit')
    if len({r['forum_id'] for r in records})!=len(records):raise ValueError('duplicate embedding ID')
    output.mkdir(parents=True,exist_ok=True)
    cache_path=output/'abstract_cls.sqlite3';existing={};connection=None
    provenance_json=json.dumps(PROVENANCE,sort_keys=True)
    if cache_path.exists():
        connection=sqlite3.connect(cache_path.resolve().as_uri()+'?mode=ro',uri=True)
        existing=dict(connection.execute('SELECT forum_id,text_hash FROM vectors WHERE provenance=?',(provenance_json,)))
        connection.close();connection=None
    missing=[r for r in records if existing.get(r['forum_id'])!=input_digest(r['abstract'])]
    if max_new:
        if encoder is None:raise ValueError('encoder required for positive preparation limit')
        connection=sqlite3.connect(cache_path)
        try:
            connection.execute('CREATE TABLE IF NOT EXISTS vectors(forum_id TEXT PRIMARY KEY,text_hash TEXT NOT NULL, provenance TEXT NOT NULL,vector BLOB NOT NULL)')
            for r in missing[:max_new]:
                vector=encode_one(r['abstract'],encoder)
                connection.execute('INSERT OR REPLACE INTO vectors VALUES(?,?,?,?)',
                    (r['forum_id'],input_digest(r['abstract']),provenance_json,vector.astype('<f4').tobytes()))
                connection.commit();existing[r['forum_id']]=input_digest(r['abstract'])
        finally:connection.close()
    status={'provenance':PROVENANCE,'historical_inputs':len(records),'complete_vectors':sum(existing.get(r['forum_id'])==input_digest(r['abstract']) for r in records),
            'remaining':sum(existing.get(r['forum_id'])!=input_digest(r['abstract']) for r in records),
            'test_vectors':0,'partial_preparation_only':True}
    (output/'status.json').write_text(json.dumps(status,indent=2)+'\n')
    return status

def main():
    p=argparse.ArgumentParser();p.add_argument('--history',type=Path,required=True)
    p.add_argument('--benchmark',type=Path,required=True,help='cached parquet for exclusion only; labels never enter embeddings')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-new',type=int,default=0)
    p.add_argument('--hub',type=Path,default=Path.home()/'.cache/huggingface/hub');a=p.parse_args()
    import pyarrow.parquet as pq
    from human_check import normalize
    benchmark=[normalize(r) for r in pq.read_table(a.benchmark).to_pylist()]
    records,_=historical(a.history,benchmark)
    records.sort(key=lambda r:(r['year'],r['forum_id']))
    try:
        encoder=local_encoder(a.hub) if a.max_new>0 else None
    except (PermissionError,FileNotFoundError) as error:
        status=prepare(records,a.output,0)
        status['requested_new']=a.max_new
        status['preparation_blocker']=type(error).__name__+': '+str(error)
        status['preparation_stage']='lower_CPU_priority_before_model_load' if isinstance(error,PermissionError) else 'local_model_asset_preflight'
        status['model_inference_started']=False
        (a.output/'status.json').write_text(json.dumps(status,indent=2)+'\n')
        print(status)
        return
    print(prepare(records,a.output,a.max_new,encoder))

if __name__=='__main__':main()
