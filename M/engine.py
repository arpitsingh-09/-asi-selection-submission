"""Build the single shared representation; all readouts consume this snapshot."""
import math
from dataclasses import replace
from pathlib import Path
import hashlib
import re
import numpy as np
from E5.diversity import extract_facets,FACETS
from .encoders import HashEncoder,MissingEmbeddingError
from .schema import Paper,EmbeddedPaper,Phi,date,iso,norm,fingerprint,LeakageError,MissingInputError
from .store import PaperStore


def _vector(v):return tuple(float(x) for x in v)


class ResearchSpace:
    def __init__(self,papers=None,encoder=None,max_literature=128,retrieval_k=3,quality_models=None):
        if type(max_literature) is not int or not 2<=max_literature<=256:raise ValueError('literature bound 2–256 required')
        if type(retrieval_k) is not int or not 0<=retrieval_k<=max_literature:raise ValueError('invalid retrieval size')
        self.store=papers if isinstance(papers,PaperStore) else PaperStore(papers or ())
        self.encoder=encoder or HashEncoder();self.max_literature=max_literature;self.retrieval_k=retrieval_k
        self.quality_models=quality_models
        root=Path(__file__).resolve().parents[1]
        self.feature_schema=fingerprint({'schema':'shared-phi-v1','space':self.encoder.space_id,
          'dimension':self.encoder.dimension,'flat_blocks':'q,mean_R,q-minus-R,four-facets,seven-scalars',
          'max_literature':max_literature,'retrieval_k':retrieval_k,
          'facet_code_sha256':hashlib.sha256((root/'E5/diversity.py').read_bytes()).hexdigest(),
          'novelty_code_sha256':hashlib.sha256((root/'E2/novelty.py').read_bytes()).hexdigest()})

    def encode(self,q,R=None,t=None,*,source_kind='generated',paper_id='',abstract=None,previous_snapshot_id=''):
        if source_kind not in ('generated','published'):raise ValueError('source kind must be generated or published')
        if source_kind=='generated' and paper_id:raise ValueError('paper_id is for published sources, not a way to exclude prior literature')
        card=q if isinstance(q,dict) else {'question':q}
        question=card.get('question',card.get('rq'))
        if not isinstance(question,str) or not question.strip():raise ValueError('research question required')
        question=question.strip();when=iso(t);source_abstract=''
        if source_kind=='published':
            if not paper_id:raise MissingInputError('published setting requires source paper ID')
            focal=self.store.get(paper_id)
            if date(focal.published)>date(when) or date(focal.available_at)>date(when):raise LeakageError('focal paper not yet available')
            source_abstract=focal.abstract
            if abstract is not None and abstract!=source_abstract:raise ValueError('abstract must match the version-bound source')
        elif abstract is not None:raise ValueError('B-ABS is for published papers only')
        qv=np.asarray(self.encoder.encode(question),dtype=np.float32)
        facets=extract_facets(question)
        if card.get('facets'):
            supplied=card['facets']
            if set(supplied)-set(FACETS):raise ValueError('unknown facet')
            for key,value in supplied.items():
                if value is not None and (not isinstance(value,str) or not value.strip()):raise ValueError('invalid supplied facet')
                facets[key]=value
        facet_vectors={f:_vector(self.encoder.encode(v)) if v else (0.,)*len(qv) for f,v in facets.items()}
        claim_texts=card.get('claims',[])
        if not isinstance(claim_texts,list) or any(not isinstance(c,str) or not c.strip() for c in claim_texts):raise ValueError('claims must be supplied text strings')
        if len({norm(c) for c in claim_texts})!=len(claim_texts):raise ValueError('duplicate claims')
        claim_texts=[c.strip() for c in claim_texts]
        input_papers=[];mode='provided'
        if R is not None:
            if not isinstance(R,(list,tuple)):raise ValueError('R must be paper identifiers/records or None')
            for r in R:
                if isinstance(r,str):p=self.store.get(r)
                else:p=Paper.from_dict(r.to_dict() if isinstance(r,Paper) else r)
                if p.paper_id==paper_id:raise LeakageError('focal paper cannot be its own input')
                if date(p.published)>=date(when) or date(p.available_at)>date(when):raise LeakageError('input publication/version is not strictly prior/available')
                if p.paper_id in self.store.papers and self.store.get(p.paper_id)!=p:raise ValueError('input version conflicts with metadata store')
                input_papers.append(p)
            if len({p.paper_id for p in input_papers})!=len(input_papers):raise ValueError('duplicate input IDs')
            mode='provided_empty' if not input_papers else 'provided'
        known={p.paper_id:p for p in self.store.eligible(when,exclude=paper_id)}
        known.update({p.paper_id:p for p in input_papers})
        ranked=[]
        for pid,p in sorted(known.items()):
            v=np.asarray(self.encoder.encode(p.text),dtype=np.float32)
            ranked.append((float(v@qv),pid,p,v))
        ranked.sort(key=lambda r:(-r[0],r[1]))
        if R is None:
            input_papers=[r[2] for r in ranked[:self.retrieval_k]]
            mode='retrieved_local_prior_cosine' if input_papers else 'retrieved_local_empty'
        input_papers=sorted(input_papers,key=lambda p:p.paper_id)
        lookup={r[1]:r[3] for r in ranked}
        def embedded(p):
            safe=replace(p,answers=tuple(a for a in p.answers if date(a.available_at)<=date(when)))
            return EmbeddedPaper(safe,_vector(lookup[p.paper_id]),
                _vector(self.encoder.encode(p.question)) if p.question else (),
                tuple(extract_facets(p.question).items()) if p.question else ())
        inputs=tuple(embedded(p) for p in input_papers)
        literature=tuple(embedded(r[2]) for r in ranked[:self.max_literature])
        context=np.mean([p.text_vector for p in inputs],axis=0) if inputs else np.zeros(len(qv))
        scores=[r[0] for r in ranked[:self.max_literature]]
        complete=sum(v is not None for v in facets.values())
        scalars=[math.log1p(len(re.findall(r'\w+',question))),math.log1p(len(inputs)),
                 float(qv@context),complete/4,math.log1p(len(literature)),max(scores) if scores else 0.,float(np.mean(scores)) if scores else 0.]
        vector=np.concatenate([qv,context,qv-context]+[np.asarray(facet_vectors[f]) for f in FACETS]+[scalars])
        quality=(('question_form',question.endswith('?') and 8<=len(question.split())<=100),
                 ('complete_facets',complete==4),('concrete_language',not bool(re.search(r'\b(things|various|something|stuff|generally|unspecified)\b',question,re.I))))
        # Even future IDs and future answer annotations are excluded from Phi.
        future=()
        # Baseline training vocabulary is limited by BOTH the question's as-of time
        # and the official training cutoff. Later snapshots cannot alter it in place.
        train_cut=min(date(when),date('2024-01-01'))
        training=tuple((p.paper_id,p.question or p.abstract or p.title) for p in self.store.eligible(train_cut.isoformat(),exclude=paper_id)
                       if date(p.available_at)<date('2024-01-01'))
        warnings=['Identity/scope/grounding are uncalibrated proxies; no predictive-accuracy claim.',
                  'Publication/availability are caller-supplied provenance; source version verification is not inferred.']
        if self.encoder.kind!='frozen_sentence_embedding':warnings.append('Lexical representation; official frozen-sentence B-Q/B-ABS are unavailable without a real cache.')
        if self.encoder.kind=='frozen_sentence_embedding':warnings.append('Cache presence does not establish encoder training cutoff; temporal model validation remains required.')
        if not claim_texts:warnings.append('No supplied atomic claims: N and custom coordinates unavailable.')
        if not inputs:warnings.append('No input evidence; groundedness and answeredness cannot be established.')
        abstract_vector=()
        if source_abstract:
            try:abstract_vector=_vector(self.encoder.encode(source_abstract))
            except MissingEmbeddingError:warnings.append('B-ABS unavailable: exact abstract embedding is not cached; no fallback inference.')
        snapshot=Phi('phi-v1','',previous_snapshot_id,question,when,source_kind,paper_id,source_abstract,
            abstract_vector,card.get('topic',''),
            self.encoder.space_id,self.encoder.kind,self.feature_schema,_vector(vector),_vector(qv),_vector(context),
            tuple(facets.items()),tuple(facet_vectors.items()),tuple(claim_texts),
            tuple(_vector(self.encoder.encode(c)) for c in claim_texts),inputs,literature,
            f'top-{self.max_literature} cosine-ranked eligible local papers; not a full-corpus novelty claim',
            mode,future,quality,training,tuple(warnings))
        values=snapshot.to_dict();values['snapshot_id']=fingerprint({k:v for k,v in values.items() if k!='snapshot_id'})
        return Phi.from_dict(values)

    def encode_paper(self,paper_id,t,R=None):
        p=self.store.get(paper_id)
        if not p.question:raise MissingInputError('paper needs an extracted question; title is not silently substituted')
        return self.encode(p.question,R,t,source_kind='published',paper_id=paper_id)

    def update(self,snapshot,later_literature,new_t):
        self._check(snapshot)
        if date(new_t)<=date(snapshot.as_of):raise LeakageError('update must move forward in time')
        store=self.store.updated(later_literature,arrival=new_t)
        future=ResearchSpace(store,self.encoder,self.max_literature,self.retrieval_k,self.quality_models)
        card={'question':snapshot.q,'facets':dict(snapshot.facets),'claims':list(snapshot.claims),'topic':snapshot.topic}
        updated=future.encode(card,[p.paper.paper_id if p.paper.paper_id in future.store.papers else p.paper for p in snapshot.inputs],new_t,source_kind=snapshot.source_kind,
                              paper_id=snapshot.source_paper_id,previous_snapshot_id=snapshot.snapshot_id)
        return future,updated

    def _check(self,snapshot):
        if snapshot.feature_schema!=self.feature_schema or snapshot.space_id!=self.encoder.space_id:raise ValueError('snapshot representation/backend mismatch')

    def readouts(self,snapshot):
        self._check(snapshot)
        from .readouts import readouts
        return readouts(snapshot,self.quality_models)

    def compare(self,a,b):
        self._check(a);self._check(b)
        from .readouts import identity_scope
        return identity_scope(a,b)

    def diversity(self,snapshots):
        for s in snapshots:self._check(s)
        from .readouts import diversity_readout
        return diversity_readout(snapshots)
