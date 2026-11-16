"""Two independent ridge factors; fitting is optional and train-only.
No accuracy claim, heldout evaluation, or implicit outcome acquisition.
"""
import json
from pathlib import Path
import numpy as np
from .schema import date,fingerprint,LeakageError
from .temporal import validate_split

FACTORS=('peer_review','later_community_use')


class QualityModels:
    def __init__(self,artifact):
        if artifact.get('factors')!=list(FACTORS) or date(artifact['trained_until'])>=date('2024-01-01'):
            raise LeakageError('quality factors must be trained through 2023 only')
        dim=artifact['feature_dimension']
        if len(artifact['mean'])!=dim or len(artifact['scale'])!=dim or not np.isfinite(artifact['mean']).all() or not np.isfinite(artifact['scale']).all() or np.any(np.asarray(artifact['scale'])<=0):raise ValueError('invalid quality feature normalization')
        for name in FACTORS:
            h=artifact['heads'][name]
            if h is None:continue
            if len(h['coefficients'])!=dim:raise ValueError('quality coefficient dimension mismatch')
            if not np.isfinite(h['intercept']) or not np.isfinite(h['coefficients']).all():raise ValueError('invalid quality head')
        self.artifact=artifact

    @classmethod
    def fit(cls,records,snapshots,labels,alpha=1.):
        if not 0<alpha or not np.isfinite(alpha):raise ValueError('positive fixed ridge alpha required')
        validate_split(records,'train')
        if not 2<=len(records)<=256 or len(snapshots)!=len(records) or len(labels)!=len(records):raise ValueError('bounded aligned train records/snapshots/labels required')
        if len({s.feature_schema for s in snapshots})!=1 or len({s.space_id for s in snapshots})!=1:raise ValueError('one feature space required')
        observed=[];targets={f:[] for f in FACTORS}
        for r,s,y in zip(records,snapshots,labels):
            if s.source_paper_id!=r['paper_id'] or date(s.as_of)!=date(r['published']):
                raise LeakageError('quality training features must be at the source publication time')
            for f in FACTORS:
                entry=y[f];when=date(entry['observed_at']);value=entry['value']
                if when>=date('2024-01-01') or when<date(s.as_of):raise LeakageError('outcome observation outside permitted training window')
                if not isinstance(value,(int,float)) or not np.isfinite(value):raise ValueError('finite numeric factor labels required')
                observed.append(when);targets[f].append(value)
        x=np.asarray([s.vector for s in snapshots]);mean=x.mean(0);scale=x.std(0);scale[scale<1e-8]=1
        z=(x-mean)/scale;gram=np.einsum('ik,jk->ij',z,z)+alpha*np.eye(len(z));heads={}
        for f in FACTORS:
            target=np.asarray(targets[f]);intercept=float(target.mean())
            coefficients=np.einsum('ij,i->j',z,np.linalg.solve(gram,target-intercept))
            heads[f]={'coefficients':coefficients.tolist(),'intercept':intercept}
        return cls({'factors':list(FACTORS),'space_id':snapshots[0].space_id,'feature_schema':snapshots[0].feature_schema,
            'feature_dimension':x.shape[1],'mean':mean.tolist(),'scale':scale.tolist(),'heads':heads,
            'trained_until':max(observed).isoformat(),'alpha':alpha,
            'training_snapshot_ids':[s.snapshot_id for s in snapshots],
            'training_data_fingerprint':fingerprint({'records':records,'labels':labels}),
            'accuracy_established':False,'target_definitions':'Supplied peer-review and later-community-use labels; no outcome validity inferred.'})

    def predict(self,phi):
        a=self.artifact
        if phi.space_id!=a['space_id'] or phi.feature_schema!=a['feature_schema'] or len(phi.vector)!=a['feature_dimension']:
            raise ValueError('quality feature representation mismatch')
        z=(np.asarray(phi.vector)-np.asarray(a['mean']))/np.asarray(a['scale'])
        return {f:({'prediction':None,'status':'unavailable; no fitted genuine-label head'} if a['heads'][f] is None else {'prediction':float(np.einsum('i,i->',z,np.asarray(a['heads'][f]['coefficients']))+a['heads'][f]['intercept']),
            'status':'fitted numeric factor score; predictive accuracy unvalidated','trained_until':a['trained_until']}) for f in FACTORS}

    def save(self,path):
        with Path(path).open('x') as f:json.dump(self.artifact,f,allow_nan=False)

    @classmethod
    def load(cls,path):return cls(json.loads(Path(path).read_text()))
