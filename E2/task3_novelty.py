"""Bounded-memory Task 3 novelty formulas; no model imports or inference."""
import numpy as np


def unit_rows(x):
    x=np.asarray(x,dtype=np.float32)
    if x.ndim!=2 or not np.isfinite(x).all():raise ValueError('invalid embedding matrix')
    norms=np.linalg.norm(x,axis=1)
    if np.any(norms<=0):raise ValueError('zero embedding')
    return x/norms[:,None]


def novelty_scores(test,reference,claims,block_size=32,p=100,q=50):
    """Raw CLS matrices in; cosine-normalized copies, four fixed scores out.

    claims is a list of matrices, in test-paper order. Each reference density
    is calculated once on demand; each temporary distance block is B x n_ref.
    """
    if block_size<1:raise ValueError('positive density block size required')
    t=unit_rows(test);r=unit_rows(reference)
    if len(r)<2 or len(t)!=len(claims) or t.shape[1]!=r.shape[1]:raise ValueError('novelty alignment')
    p=min(max(1,p),len(r));q=min(max(1,q),len(r)-1)
    density={};rows=[]
    for idea,claim in zip(t,claims):
        c=unit_rows(claim)
        if not len(c) or c.shape[1]!=r.shape[1]:raise ValueError('missing/aligned claim embeddings required')
        distances=1-np.clip(np.einsum('ik,k->i',r,idea),-1,1)
        nearest=np.argsort(distances,kind='stable')[:p]
        query_density=float(np.mean(np.sort(distances)[:q]))
        missing=[int(i) for i in nearest if int(i) not in density]
        for start in range(0,len(missing),block_size):
            ids=missing[start:start+block_size]
            d=1-np.clip(np.einsum('ik,jk->ij',r[ids],r),-1,1)
            d[np.arange(len(ids)),ids]=np.inf
            nearest_d=np.partition(d,q-1,axis=1)[:,:q]
            # Sorting the selected values reproduces the existing mean order.
            means=np.sort(nearest_d,axis=1).mean(axis=1)
            density.update({i:float(v) for i,v in zip(ids,means)})
        y=float(np.min(distances))
        n=float(1-np.clip(np.einsum('ik,jk->ij',c,r),-1,1).max(axis=1).mean())
        rows.append({'Y':y,'N':n,'yours':.75*y+.25*n,
                     'density':float(100*np.mean([density[int(i)]<=query_density for i in nearest]))})
    return {k:[row[k] for row in rows] for k in ('Y','N','yours','density')}
