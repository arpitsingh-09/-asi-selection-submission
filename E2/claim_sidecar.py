"""Bounded Task 2 claim-vector preparation and strictly read-only overlay.

The CLI defaults to inventory only. No encoder is imported until future explicit
inference/resource authorization succeeds. The original cache is never writable.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import resource
import sys
import types
for _name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_name]='1'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',CUDA_VISIBLE_DEVICES='')
import numpy as np
from cached_extensions import Cache,MODEL
from abstract_embeddings import BASE_REV,ADAPTER_REV

DIM=768
SIDECAR='claim_vectors_v1.sqlite3'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def text_hash(s):return hashlib.sha256(s.encode()).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
def read_rows(path):
    with Path(path).open() as f:return [json.loads(s) for s in f if s.strip()]
def dump(path,obj):
    with Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')


def validate_requests(requests,claims,expected_count=93):
    """Check exact text and all paper/index uses; reject duplicate requests/uses."""
    if len(requests)!=expected_count:raise ValueError('exact request count required')
    byid={r['paper_id']:r for r in claims}
    if len(byid)!=len(claims):raise ValueError('duplicate claim-source paper')
    hashes=set();uses=set()
    for r in requests:
        s=r['text'];h=r['text_sha256']
        if not isinstance(s,str) or not s.strip() or s!=s.strip() or text_hash(s)!=h:
            raise ValueError('request text/hash mismatch')
        if h in hashes:raise ValueError('duplicate request hash')
        hashes.add(h)
        if r.get('model_id')!=MODEL:raise ValueError('request model mismatch')
        if not r.get('uses'):raise ValueError('request source uses missing')
        for u in r['uses']:
            pid=u['paper_id'];i=u['claim_index']
            if type(i) is not int or i<0 or pid not in byid or i>=len(byid[pid]['claims']):
                raise ValueError('request paper/index mismatch')
            if (pid,i) in uses:raise ValueError('duplicate source use')
            uses.add((pid,i))
            if byid[pid]['claims'][i]['claim'].strip()!=s:
                raise ValueError('request source text mismatch')
    return {r['text_sha256']:r for r in requests}


def prepare(plan_path,folder):
    """Freeze worker inputs/code separately; never alter the supplied plan."""
    plan_path=Path(plan_path).resolve();p=json.loads(plan_path.read_text())
    source={str(plan_path):sha(plan_path)}
    for name in ('requests','claim_source','fixed_condition_pools','parity_controls','model_inventory'):
        path=Path(p[name+'_path']).resolve();expected=p[name+'_sha256']
        if sha(path)!=expected:raise ValueError('source fingerprint mismatch: '+name)
        source[str(path)]=expected
    original=Path(p['existing_cache']).resolve()
    if sha(original)!=p['existing_cache_sha256']:raise ValueError('original cache fingerprint mismatch')
    source[str(original)]=p['existing_cache_sha256']
    requests=read_rows(p['requests_path']);claims=read_rows(p['claim_source_path'])
    validate_requests(requests,claims)
    uses=[u for r in requests for u in r['uses']]
    pools=read_rows(p['fixed_condition_pools_path'])
    if (len(pools)!=52 or len({r['paper_id'] for r in pools})!=52
        or {u['paper_id'] for u in uses}!={r['paper_id'] for r in pools}
        or p['unique_required_claim_texts']!=93):raise ValueError('fixed 52-paper request coverage')
    inv=json.loads(Path(p['model_inventory_path']).read_text())
    if p['base_revision']!=BASE_REV or inv['base_revision']!=BASE_REV or p['adapter_revision']!=ADAPTER_REV or inv['adapter_revision']!=ADAPTER_REV:
        raise ValueError('pinned model revision mismatch')
    if (p['representation']['model_id']!=MODEL or p['representation']['dimension']!=DIM
        or p['representation']['max_length']!=512 or p['representation']['dtype']!='float32'):
        raise ValueError('unexpected representation')
    controls=json.loads(Path(p['parity_controls_path']).read_text())
    if len(controls)!=3 or len({c['text_sha256'] for c in controls})!=3:
        raise ValueError('three parity controls required')
    cache=Cache(original)
    try:
        for c in controls:
            if text_hash(c['text'])!=c['text_sha256']:raise ValueError('parity text hash mismatch')
            v=cache.get(c['text'])
            if hashlib.sha256(v.astype('<f4').tobytes()).hexdigest()!=c['normalized_float32_vector_sha256']:
                raise ValueError('parity cached vector changed')
    finally:cache.close()
    root=Path(__file__).resolve().parent
    code=[Path(__file__).resolve(),root/'cached_extensions.py',root/'abstract_embeddings.py',root/'task3_execution.py',root/'novelty.py']
    manifest={'format':1,'plan_path':str(plan_path),'source_sha256':source,
        'code_sha256':{str(path):sha(path) for path in code},
        'model_key':text_hash(canonical({'base':BASE_REV,'adapter':ADAPTER_REV,
          'inventory_sha256':p['model_inventory_sha256'],'representation':p['representation']})),
        'request_count':93,'affected_focals':52,'sidecar_filename':SIDECAR,
        'parity_atol':1e-5,'parity_rtol':1e-4,'status':'prepared_no_inference_authorized'}
    folder=Path(folder).resolve()
    if folder/SIDECAR==original:raise ValueError('sidecar must differ from original cache')
    folder.mkdir(parents=True,exist_ok=False)
    dump(folder/'manifest.json',manifest)
    dump(folder/'authorization.template.json',{'manifest_sha256':sha(folder/'manifest.json'),
      'authorize_inference':False,'e6_inactive_verified':False,'resource_headroom_verified':False,
      'authorization_source':None,'calibration_review_path':None,'calibration_review_sha256':None})
    return status(folder)


def load(folder):
    folder=Path(folder).resolve();manifest_path=folder/'manifest.json'
    m=json.loads(manifest_path.read_text())
    if m['format']!=1 or m['request_count']!=93 or m['sidecar_filename']!=SIDECAR:
        raise ValueError('unsupported sidecar manifest')
    if m['parity_atol']!=1e-5 or m['parity_rtol']!=1e-4:raise ValueError('fixed parity tolerance changed')
    for path,h in {**m['source_sha256'],**m['code_sha256']}.items():
        if sha(path)!=h:raise ValueError('frozen sidecar binding changed: '+path)
    p=json.loads(Path(m['plan_path']).read_text())
    requests=read_rows(p['requests_path'])
    allowed=validate_requests(requests,read_rows(p['claim_source_path']))
    inv=json.loads(Path(p['model_inventory_path']).read_text())
    expected=text_hash(canonical({'base':BASE_REV,'adapter':ADAPTER_REV,
        'inventory_sha256':p['model_inventory_sha256'],'representation':p['representation']}))
    if m['model_key']!=expected or inv['base_revision']!=BASE_REV or inv['adapter_revision']!=ADAPTER_REV:
        raise ValueError('sidecar model identity mismatch')
    if (folder/SIDECAR).resolve()==Path(p['existing_cache']).resolve():raise ValueError('original cache is read only')
    return m,p,allowed


def binding(folder,m):
    return canonical({'format':1,'manifest_sha256':sha(Path(folder)/'manifest.json'),
                      'model_key':m['model_key'],'model_id':MODEL,'dimension':DIM,'dtype':'<f4','normalization':'unit_L2'})


def normalized(raw):
    v=np.asarray(raw,dtype=np.float32)
    if v.shape!=(DIM,) or not np.isfinite(v).all():raise ValueError('invalid raw vector')
    norm=float(np.linalg.norm(v))
    if not np.isfinite(norm) or norm<=0:raise ValueError('zero/nonfinite norm')
    v=np.asarray(v/norm,dtype='<f4')
    validate_vector(v)
    return v


def validate_vector(v):
    if v.shape!=(DIM,) or not np.isfinite(v).all() or not np.isclose(np.linalg.norm(v),1,atol=1e-4):
        raise ValueError('invalid normalized vector')


class Sidecar:
    """One versioned database, request-bound and checksummed; RO by default."""
    def __init__(self,path,expected_binding,allowed,model_key,write=False,parity=None):
        self.path=Path(path).resolve();self.allowed=allowed;self.model_key=model_key
        self.connection=None;self.write=write
        if not self.path.exists() and not write:return
        if write:
            self.connection=sqlite3.connect(self.path)
        else:self.connection=sqlite3.connect(self.path.as_uri()+'?mode=ro',uri=True)
        try:
            if write:
                with self.connection:
                    self.connection.execute('CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
                    self.connection.execute('CREATE TABLE IF NOT EXISTS vectors(text_hash TEXT PRIMARY KEY,text_value TEXT NOT NULL,model_key TEXT NOT NULL,checksum TEXT NOT NULL,vector BLOB NOT NULL)')
                    prior=self.connection.execute("SELECT value FROM metadata WHERE key='binding'").fetchone()
                    if prior is None:
                        if not parity or parity.get('passed') is not True:raise ValueError('parity certificate required')
                        self.connection.execute("INSERT INTO metadata VALUES('binding',?)",(expected_binding,))
                        self.connection.execute("INSERT INTO metadata VALUES('parity',?)",(canonical(parity),))
            meta=dict(self.connection.execute('SELECT key,value FROM metadata'))
            if meta.get('binding')!=expected_binding or json.loads(meta.get('parity','{}')).get('passed') is not True:
                raise ValueError('cache provenance/parity mismatch')
            # Validate the complete tiny sidecar immediately, even rows not requested.
            for h, in self.connection.execute('SELECT text_hash FROM vectors').fetchall():self.get_hash(h)
        except Exception:
            self.close();raise

    def get_hash(self,h):
        if self.connection is None:return None
        r=self.connection.execute('SELECT text_value,model_key,checksum,vector FROM vectors WHERE text_hash=?',(h,)).fetchone()
        if r is None:return None
        if h not in self.allowed or text_hash(r[0])!=h or r[0]!=self.allowed[h]['text'] or r[1]!=self.model_key:
            raise ValueError('sidecar request/model binding mismatch')
        blob=r[3]
        if len(blob)!=DIM*4 or hashlib.sha256(blob).hexdigest()!=r[2]:raise ValueError('sidecar checksum/size corruption')
        v=np.frombuffer(blob,dtype='<f4').copy();validate_vector(v)
        return v

    def put_batch(self,items):
        if not self.write or self.connection is None:raise ValueError('read-only sidecar')
        validated=[]
        for h,raw in items:
            if h not in self.allowed:raise ValueError('unrequested vector')
            v=np.asarray(raw,dtype='<f4');validate_vector(v)
            old=self.get_hash(h)
            if old is not None and not np.array_equal(old,v):raise ValueError('conflicting immutable vector')
            if old is None:
                blob=v.tobytes();validated.append((h,self.allowed[h]['text'],self.model_key,hashlib.sha256(blob).hexdigest(),blob))
        with self.connection:self.connection.executemany('INSERT INTO vectors VALUES(?,?,?,?,?)',validated)

    def close(self):
        if self.connection is not None:self.connection.close();self.connection=None


class Overlay:
    """Strict read-only original+sidecar lookup; never loads an encoder."""
    def __init__(self,folder):
        m,p,allowed=load(folder)
        self.original=Cache(Path(p['existing_cache']))
        try:self.sidecar=Sidecar(Path(folder)/SIDECAR,binding(folder,m),allowed,m['model_key'])
        except Exception:self.original.close();raise

    def get(self,text):
        try:original=self.original.get(text)
        except KeyError:original=None
        extra=self.sidecar.get_hash(text_hash(text))
        if extra is not None and text!=self.sidecar.allowed[text_hash(text)]['text']:
            raise ValueError('overlay exact-text binding mismatch')
        if original is not None:
            if extra is not None and not np.array_equal(original,extra):raise ValueError('overlay cache conflict')
            return original.copy()
        if extra is None:raise KeyError('missing vector; inference disabled: '+text_hash(text))
        return extra

    def encode(self,texts, batch_size=2):
        if not texts:return np.empty((0,DIM),dtype=np.float32)
        return np.stack([self.get(s) for s in texts]).astype(np.float32)

    def score(self,novelty_module,*args,**kwargs):
        """Execute novelty.score with a private RO encoder binding.
        No monkeypatch/module mutation, original-cache writes, or fallback inference.
        Pass the existing novelty module; it is never imported by this worker.
        """
        fn=novelty_module.score
        scope=dict(fn.__globals__);scope['_encode']=self.encode
        cached=types.FunctionType(fn.__code__,scope,fn.__name__,fn.__defaults__,fn.__closure__)
        cached.__kwdefaults__=fn.__kwdefaults__
        return cached(*args,**kwargs)

    def close(self):self.original.close();self.sidecar.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()


def status(folder):
    m,p,allowed=load(folder)
    c=Sidecar(Path(folder)/SIDECAR,binding(folder,m),allowed,m['model_key'])
    try:complete=sum(c.get_hash(h) is not None for h in allowed)
    finally:c.close()
    return {'required_vectors':93,'complete_vectors':complete,'missing_vectors':93-complete,
            'model_loaded':False,'new_vectors_generated':0,'inference_authorized':False}


def cpu_factory(inventory):
    # The shared loader lowers priority and verifies assets before torch/model import.
    from task3_execution import batched_cpu_encoder
    return batched_cpu_encoder({'model_inventory':inventory})


def authorize(folder,auth_path):
    if auth_path is None:raise ValueError('future explicit inference authorization required')
    a=json.loads(Path(auth_path).read_text())
    if a.get('manifest_sha256')!=sha(Path(folder)/'manifest.json'):raise ValueError('authorization fingerprint mismatch')
    for flag in ('authorize_inference','e6_inactive_verified','resource_headroom_verified'):
        if a.get(flag) is not True:raise ValueError('inference/resource/E6 authorization missing: '+flag)
    if not isinstance(a.get('authorization_source'),str) or not a['authorization_source'].strip():
        raise ValueError('authorization source required')
    return a


def encode(folder,auth_path=None,limit=0,batch_size=2,encoder_factory=cpu_factory):
    if type(limit) is not int or not 0<=limit<=93 or type(batch_size) is not int or not 1<=batch_size<=2:
        raise ValueError('limit 0-93 and batch size 1-2 required')
    if limit==0:return status(folder)
    m,p,allowed=load(folder);a=authorize(folder,auth_path)
    target=Path(folder)/SIDECAR
    c=Sidecar(target,binding(folder,m),allowed,m['model_key'])
    try:
        complete=sum(c.get_hash(h) is not None for h in allowed)
        missing=[r for h,r in allowed.items() if c.get_hash(h) is None][:limit]
    finally:c.close()
    if not missing:return status(folder) # Complete resume never loads a model.
    if complete+len(missing)>4:
        review=a.get('calibration_review_path')
        if not review or sha(review)!=a.get('calibration_review_sha256'):raise ValueError('calibration review required after four claims')
        r=json.loads(Path(review).read_text())
        if r.get('manifest_sha256')!=sha(Path(folder)/'manifest.json') or r.get('accepted') is not True or not r.get('review_source'):
            raise ValueError('calibration review is not accepted')
        report=r.get('calibration_report_path')
        if not report or sha(report)!=r.get('calibration_report_sha256'):
            raise ValueError('calibration report missing/changed')
        calibration=json.loads(Path(report).read_text())
        if (calibration.get('manifest_sha256')!=sha(Path(folder)/'manifest.json')
            or not 1<=calibration.get('new_vectors_generated',0)<=4
            or len(calibration.get('parity_controls',[]))!=3
            or not calibration.get('process_peak_rss_bytes')):
            raise ValueError('invalid calibration report')
    inv=json.loads(Path(p['model_inventory_path']).read_text())
    started=time.monotonic();encoder=encoder_factory(inv)
    controls=json.loads(Path(p['parity_controls_path']).read_text());parity=[]
    original=Cache(Path(p['existing_cache']))
    try:
        # Every model initialization must pass all three fixed parity controls.
        for c0 in controls:
            raw=np.asarray(encoder([c0['text']]),dtype=np.float32)
            if raw.shape!=(1,DIM):raise ValueError('parity encoder alignment')
            got=normalized(raw[0]);expected=original.get(c0['text'])
            if text_hash(c0['text'])!=c0['text_sha256'] or hashlib.sha256(expected.astype('<f4').tobytes()).hexdigest()!=c0['normalized_float32_vector_sha256']:
                raise ValueError('parity source mismatch')
            if not np.allclose(got,expected,atol=m['parity_atol'],rtol=m['parity_rtol']):raise ValueError('pinned encoder parity failed')
            parity.append({'text_sha256':c0['text_sha256'],'max_absolute_difference':float(np.abs(got-expected).max())})
    finally:original.close()
    cert={'passed':True,'controls':parity}
    c=Sidecar(target,binding(folder,m),allowed,m['model_key'],write=True,parity=cert)
    try:
        for start in range(0,len(missing),batch_size):
            batch=missing[start:start+batch_size]
            vectors=np.asarray(encoder([r['text'] for r in batch]),dtype=np.float32)
            if vectors.shape!=(len(batch),DIM):raise ValueError('encoder batch alignment')
            c.put_batch([(r['text_sha256'],normalized(v)) for r,v in zip(batch,vectors)])
    finally:c.close()
    result=status(folder)
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result.update(model_loaded=True,new_vectors_generated=len(missing),elapsed_seconds=time.monotonic()-started,
                  process_peak_rss_bytes=int(peak if sys.platform=='darwin' else peak*1024),
                  manifest_sha256=sha(Path(folder)/'manifest.json'),
                  inference_authorized=True,parity_controls=parity)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('prepare');a.add_argument('--plan',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a=s.add_parser('status');a.add_argument('--folder',type=Path,required=True)
    a=s.add_parser('encode');a.add_argument('--folder',type=Path,required=True);a.add_argument('--authorization',type=Path)
    a.add_argument('--limit',type=int,default=0);a.add_argument('--batch-size',type=int,default=2)
    a=p.parse_args()
    if a.command=='prepare':result=prepare(a.plan,a.output)
    elif a.command=='status':result=status(a.folder)
    else:result=encode(a.folder,a.authorization,a.limit,a.batch_size)
    print(json.dumps(result,indent=2))
