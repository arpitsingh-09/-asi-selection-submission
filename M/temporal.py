"""Official M temporal splits; metadata validation only, no heldout scoring."""
from .schema import date,LeakageError


def split_for(value):
    t=date(value)
    if t<date('2024-01-01'):return 'train'
    if t<date('2025-01-01'):return 'validation'
    if t<date('2025-07-01'):return 'gap'
    return 'test'


def validate_split(records,split):
    if split not in ('train','validation','test'):raise ValueError('unsupported split')
    ids=set()
    for r in records:
        pid=r.get('paper_id',r.get('id'))
        if not pid or pid in ids:raise ValueError('unique record IDs required')
        ids.add(pid)
        if split_for(r['published'])!=split:raise LeakageError('record outside declared '+split)
        if date(r.get('available_at',r['published']))<date(r['published']):raise LeakageError('availability precedes publication')
        if split=='train' and date(r.get('available_at',r['published']))>=date('2024-01-01'):
            raise LeakageError('post-2023 training text/version')
    return {'split':split,'records':len(records),'metadata_valid':True,'heldout_evaluated':False}
