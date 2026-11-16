"""Export-only recovery wrapper; preserves the preregistered numerical engine."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import types
import numpy as np
import evaluate as original

ROOT=Path(__file__).resolve().parent


def numpy_scalar(value):
    if isinstance(value,np.generic):return value.item()
    raise TypeError('unsupported export type: '+type(value).__name__)


class JsonExport:
    @staticmethod
    def dumps(value,**kwargs):return json.dumps(value,default=numpy_scalar,**kwargs)
    @staticmethod
    def dump(value,file,**kwargs):return json.dump(value,file,default=numpy_scalar,**kwargs)
    loads=staticmethod(json.loads)


def run(output):
    m=json.loads((ROOT/'manifest_export_v2.json').read_text())
    for rel,h in m['committed_sha256'].items():
        data=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT.parent)
        if hashlib.sha256(data).hexdigest()!=h or original.sha(ROOT.parent/rel)!=h:
            raise ValueError('export fix not committed unchanged')
    data=subprocess.check_output(['git','show','HEAD:E5/manifest_export_v2.json'],cwd=ROOT.parent)
    if hashlib.sha256(data).hexdigest()!=original.sha(ROOT/'manifest_export_v2.json'):raise ValueError('export manifest changed')
    # Private exporter binding; original module/functions and all numeric work unchanged.
    scope=dict(original.evaluate.__globals__);scope['json']=JsonExport
    fn=types.FunctionType(original.evaluate.__code__,scope,original.evaluate.__name__,original.evaluate.__defaults__)
    return fn(output)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=run(a.output)
    print(JsonExport.dumps({'sets':r['sets'],'backend':r['backend'],'facet_edit_locality':r['facet_edit_locality']}))
