"""Registered S1 paired statistics; prediction building never infers human labels."""
import numpy as np
from .evaluation import CONTROLS,DRAWS,bootstrap,validate,MARGIN


def paired_metrics(records,*,synthetic=False,draws=DRAWS):
    # No public real-execution bypass: future committed cohort-lock runner required.
    if not synthetic:raise ValueError('real S1 blocked until verified cohort/model lock is committed')
    validate('S1',records,synthetic=True)
    results={}
    for condition in CONTROLS:
        intervals=bootstrap('S1',records,condition,draws)
        accuracy={}
        for task in ('near_miss','minimal_paraphrase'):
            items=[r for r in records if r['task']==task]
            accuracy[task]={name:float(np.mean([r['predictions'][condition][key]==r['label'] for r in items])) for name,key in [('Phi','decision'),('B-Q','B-Q')]}
        results[condition]={'paired_improvement':intervals,'accuracy':accuracy}
    return {'status':'SYNTHETIC_ONLY','heldout_evaluated':False,'controls':results,
        'pass_criteria_met':all(v['ci95'][0]>MARGIN for v in results['original']['paired_improvement'].values())}
