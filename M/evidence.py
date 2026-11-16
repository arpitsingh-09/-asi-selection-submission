"""Exact-byte, field-bound local evidence. Dates are never inferred from years."""
import hashlib
import json
from pathlib import Path

MAX_RECORD=1024*1024

def sha(data):return hashlib.sha256(data).hexdigest()

def iter_bound(path,limit=None):
    path=Path(path).resolve()
    with path.open('rb') as f:
        line=0
        while limit is None or line<limit:
            offset=f.tell();raw=f.readline(MAX_RECORD+1)
            if not raw:break
            if len(raw)>MAX_RECORD:raise ValueError('evidence record exceeds bounded reader')
            line+=1
            if not raw.strip():continue
            yield json.loads(raw),{'path':str(path),'offset':offset,'length':len(raw),'line':line,'record_sha256':sha(raw)}

def read_bound(binding):
    n=binding['length']
    if type(n) is not int or not 0<n<=MAX_RECORD or binding['offset']<0:raise ValueError('invalid evidence slice')
    with Path(binding['path']).open('rb') as f:f.seek(binding['offset']);raw=f.read(n)
    if sha(raw)!=binding['record_sha256']:raise ValueError('source evidence changed')
    return json.loads(raw)

def field(obj,path):
    for key in path:obj=obj[key]
    return obj

def assertion(binding,path,value):
    source=read_bound(binding)
    if field(source,path)!=value:raise ValueError('asserted field does not match exact source')
    return {'binding':binding,'field_path':path,'value':value}

def verify_assertion(a):
    assertion(a['binding'],a['field_path'],a['value']);return True
