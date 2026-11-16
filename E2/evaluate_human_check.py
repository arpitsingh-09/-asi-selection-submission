"""Offline evaluator for future frozen inputs. No inference or model downloads.

Input bundle JSON: benchmark (normalized records with published timestamps),
history (historical() output), history_ids, test_ids, embedding_provenance,
novelty_scores {Y,N,yours,density}, test_abstract_sha256 (original abstracts), and authorization {protocol_sha256,
prospective_preregistration_verified, post_cutoff_verified, encoder_cutoff}.
NPZ: history_embeddings, test_embeddings. Matrices must follow supplied IDs.
A signed-off prospective protocol must exist before producing held-out scores.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from human_check import normalize, historical, quality_scores, comparison, eligibility, MEASURES


def validate_abstract_binding(benchmark, declared_hashes):
    """R2 ideas are edited abstracts; bind baseline inputs to recovered originals."""
    if any(not isinstance(r.get('abstract'),str) or not r['abstract'].strip() for r in benchmark):
        raise ValueError('original source abstracts required for quality baseline')
    expected=[hashlib.sha256(r['abstract'].encode()).hexdigest() for r in benchmark]
    if declared_hashes!=expected:
        raise ValueError('test original-abstract embedding hash alignment')

def evaluate(bundle, arrays, protocol):
    auth=bundle['authorization']
    if not auth.get('prospective_preregistration_verified') or not auth.get('post_cutoff_verified'):
        raise ValueError('held-out evaluation requires verified preregistration and cutoff evidence')
    if auth['protocol_sha256']!=hashlib.sha256(protocol.read_bytes()).hexdigest():
        raise ValueError('protocol hash mismatch')
    provenance=bundle['embedding_provenance']
    required={'encoder':'allenai/specter2_base','adapter':'allenai/specter2',
              'input':'abstract_only','pooling':'CLS','max_length':512,'frozen':True,'normalization':'none'}
    if any(provenance.get(k)!=v for k,v in required.items()):raise ValueError('embedding provenance mismatch')
    bench=[normalize(r) for r in bundle['benchmark']]
    validate_abstract_binding(bench,bundle.get('test_abstract_sha256'))
    if len({r['id'] for r in bench})!=len(bench):raise ValueError('duplicate benchmark id')
    ids=[r['forum_id'] for r in bench]
    if None in ids or len(set(ids))!=len(ids) or ids!=bundle['test_ids']:raise ValueError('test ID alignment')
    if any(eligibility(r,auth['encoder_cutoff'])!='eligible' for r in bench):
        raise ValueError('test item is not verified post-cutoff')
    history=bundle['history']
    if [r['forum_id'] for r in history]!=bundle['history_ids']:raise ValueError('history ID alignment')
    if bundle.get('history_abstract_sha256')!=[r.get('abstract_sha256') for r in history]:
        raise ValueError('history abstract embedding hash alignment')
    from datetime import datetime
    def parse_date(s):
        date=datetime.fromisoformat(s.replace('Z','+00:00'))
        if date.tzinfo is None:raise ValueError('timezone required')
        return date
    earliest_test=min(parse_date(r['published']) for r in bench)
    if any(r.get('venue')!='ICLR' or not r.get('published') or parse_date(r['published'])>=earliest_test for r in history):
        raise ValueError('history must be earlier same-venue reviews')
    # Recheck title overlap and conservative exclusions even for caller-provided history.
    from human_check import title_key
    titles={title_key(r['title']) for r in bench}
    for r in history:
        k=title_key(r['title'])
        if r['year'] not in (2022,2023,2024,2025) or r['review_count']<2 or k in titles or any(
            s in k for s in ('hotpate','conjuringsemanticsimilarity','counterfactualtechniquesforenhancingcustomerretention')):
            raise ValueError('ineligible historical record')
    pred,selection=quality_scores(history,arrays['history_embeddings'],ids,arrays['test_embeddings'])
    scores={m:bundle['novelty_scores'][m] for m in MEASURES}
    scores['quality']=pred
    report=comparison([int(r['label']=='POSITIVE') for r in bench],scores)
    report['ridge_selection']=selection
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--embeddings',type=Path,required=True);p.add_argument('--protocol',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('refusing to overwrite results')
    result=evaluate(json.loads(a.bundle.read_text()),np.load(a.embeddings,allow_pickle=False),a.protocol)
    with a.output.open('x') as f:json.dump(result,f,indent=2,allow_nan=False)

if __name__=='__main__':main()
