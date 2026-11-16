"""Required baselines with explicit availability and immutable training scope."""
from collections import Counter
import math
import re
import numpy as np


def tfidf(question,training):
    if not training:return {'available':False,'reason':'no as-of-available training documents through 2023'}
    tokens=lambda s:re.findall(r'[a-z0-9]+',s.casefold())
    documents=[tokens(text) for _,text in training]
    df=Counter(t for doc in documents for t in set(doc));vocabulary=sorted(df)
    counts=Counter(tokens(question));n=len(documents)
    vector=np.array([counts[t]*(1+math.log((1+n)/(1+df[t]))) for t in vocabulary],dtype=float)
    length=np.linalg.norm(vector)
    if length:vector/=length
    return {'available':True,'vector':vector.tolist(),'vocabulary':vocabulary,
            'training_ids':[pid for pid,_ in training],'training_scope':'available before as-of AND publication before 2024; frozen per snapshot',
            'out_of_vocabulary_query':not bool(length)}


def baselines(phi):
    frozen=phi.encoder_kind=='frozen_sentence_embedding'
    bq={'available':frozen,'space_id':phi.space_id,'vector':list(phi.question_vector) if frozen else None,
        'reason':None if frozen else 'question vector is a lexical proxy, not the required frozen sentence model'}
    babs={'available':frozen and phi.source_kind=='published' and bool(phi.source_abstract_vector),
          'vector':list(phi.source_abstract_vector) if frozen and phi.source_kind=='published' and phi.source_abstract_vector else None,
          'space_id':phi.space_id,'reason':'published setting only; requires exact cached abstract embedding'}
    return {'B-Q':bq,'B-ABS':babs,'B-TF':tfidf(phi.q,phi.tfidf_training_documents),
            'B-LEN':{'available':True,'tokens':len(re.findall(r'\w+',phi.q)),'characters':len(phi.q)},
            'B-JUDGE':{'available':False,'reason':'optional judge not invoked'}}
