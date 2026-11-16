"""Source-component sidecars for Decision 24; frozen model output stays intact.

The combined review packet is the original four-field model extraction plus
separate attributed problem/method/result annotations. No component is supplied
automatically and absent components cannot pass their corresponding checks.
"""
from researcher_approval import digest, valid_utc
from literature_finalization import extraction_source

COMPONENTS=('problem','method','result')


def component_form(row):
    field,text=extraction_source(row)
    import hashlib
    return {'input_set_id':row['input_set_id'],'target_source_field':field,
        'target_source_text_sha256':hashlib.sha256(text.encode()).hexdigest(),
        'fixed_extraction_sha256':digest(row['target_extraction']),
        'components':{k:{'text':None,'source_quote':None,'character_span':None,
            'annotator_id':None,'annotated_at_utc':None} for k in COMPONENTS},
        'status':'pending_actual_source_annotations'}


def validate_components(row,sidecar):
    base=component_form(row)
    for key in ('input_set_id','target_source_field','target_source_text_sha256','fixed_extraction_sha256'):
        if sidecar.get(key)!=base[key]:raise ValueError('component source/extraction binding mismatch: '+key)
    field,text=extraction_source(row)
    if set(sidecar.get('components',{}))!=set(COMPONENTS):raise ValueError('all three source components required')
    for name,entry in sidecar['components'].items():
        for key in ('text','source_quote','annotator_id'):
            if not isinstance(entry.get(key),str) or not entry[key].strip() or set(entry[key].strip())=={'_'}:
                raise ValueError(name+': missing actual annotation '+key)
        if not valid_utc(entry.get('annotated_at_utc')):raise ValueError(name+': actual annotation UTC time required')
        span=entry.get('character_span')
        if (not isinstance(span,list) or len(span)!=2 or any(type(x) is not int for x in span)
                or not 0<=span[0]<span[1]<=len(text) or text[span[0]:span[1]]!=entry['source_quote']):
            raise ValueError(name+': quotation/span not supported by original source')
    return True


def validate_component_reviews(extracted,sidecars,records,review_ids):
    """Validate supplement attribution and join genuine checks to exact annotations.

    Existing validate_review_bundle must also pass: it enforces the two reviewer
    and independent adjudication rules and all seven actual Boolean decisions.
    """
    by_id={r['input_set_id']:r for r in sidecars}
    if len(by_id)!=len(sidecars):raise ValueError('duplicate component sidecars')
    originals={r['input_set_id']:r for r in extracted}
    for unit in review_ids:
        if unit not in by_id:raise ValueError('missing source-component sidecar: '+unit)
        validate_components(originals[unit],by_id[unit])
        reviews=[r for r in records if r['input_set_id']==unit]
        if len(reviews)!=2:raise ValueError('two component reviewers required')
        for review in reviews:
            if review.get('source_component_sidecar_sha256')!=digest(by_id[unit]):
                raise ValueError('review must bind exact source-component sidecar')
            if any(type(review.get(k+'_extraction_accurate')) is not bool for k in COMPONENTS):
                raise ValueError('actual three source-component checks required')
    return True
