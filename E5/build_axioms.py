"""Deterministic controlled-language E5 development benchmark, not real papers."""
import hashlib
import json
import re
from pathlib import Path

DOMAINS=[
('medical image classification','assigning diagnostic labels to clinical pictures'),
('satellite image classification','labelling categories in orbital photographs'),
('speech transcription','converting spoken recordings into written words'),
('protein function prediction','inferring biological roles of proteins'),
('graph node classification','assigning categories to vertices of networks'),
('document classification','labelling written documents by category'),
('machine translation','converting text between natural languages'),
('time series forecasting','predicting future values of temporal sequences'),
('fraud detection','recognizing deceptive financial transactions'),
('robot navigation','guiding autonomous robots through environments'),
('object detection','locating and identifying objects in images'),
('sentiment classification','assigning emotional polarity to text'),
('anomaly detection','identifying unusual data instances'),
('recommendation systems','ranking items for individual users'),
('molecular property prediction','estimating characteristics of chemical compounds'),
('code completion','predicting subsequent source code'),
('speaker identification','recognizing who produced a speech recording'),
('traffic prediction','forecasting vehicle flow through road networks'),
('crop disease recognition','identifying illnesses in agricultural plants'),
('network intrusion detection','recognizing unauthorized activity in computer networks')]
MECHANISMS=[
('data augmentation','synthetic transformations of training examples'),
('model ensembling','aggregation of independently trained predictors'),
('knowledge distillation','teacher to student predictive transfer'),
('active learning','adaptive selection of examples to annotate'),
('contrastive learning','representation training using positive and negative pairs'),
('dropout regularization','random removal of activations during training'),
('transfer learning','reuse of representations learned on a different task'),
('curriculum learning','ordering training examples by difficulty'),
('parameter pruning','removal of low importance model weights'),
('adversarial training','learning from deliberately perturbed examples')]
TARGETS=[
('reduce predictive error','make fewer incorrect predictions','held-out error','the error rate on unseen labelled instances'),
('improve noise robustness','make predictions more resistant to corrupted inputs','accuracy under fixed corruption','correctness after a specified input perturbation'),
('improve probability calibration','align predicted confidence with actual correctness','expected calibration error','the discrepancy between confidence and empirical correctness'),
('reduce inference latency','produce predictions in less time','median prediction latency','the median time required for a prediction'),
('improve transfer generalization','perform better outside the training distribution','target-domain error','prediction mistakes on the shifted evaluation population'),
('reduce annotation cost','require fewer manually labelled examples','labels needed to reach target error','the annotation count needed for a specified error rate'),
('improve minority-group performance','increase correctness for underrepresented groups','worst-group accuracy','correctness in the least well served subgroup'),
('improve sample efficiency','learn useful predictions from fewer examples','learning curve area','the area under performance as training size changes'),
('reduce memory use','consume less storage during prediction','peak inference memory','the largest memory footprint while predicting'),
('accelerate convergence','reach a training target in fewer updates','steps to target loss','the optimization update count needed for a specified loss')]
FACETS=('purpose','mechanism','evaluation','domain')


def question(f,style=0):
    d,m,p,e=[f[k] for k in ('domain','mechanism','purpose','evaluation')]
    return [f'For {d}, does {m} help {p}, measured by {e}?',
      f'In {d}, can {p} be achieved through {m}, assessed using {e}?',
      f'Using {e} as the criterion, does {m} help {p} in {d}?',
      f'When studying {d}, what effect does {m} have on efforts to {p}, with {e} as the measure?',
      f'Can {m} support attempts to {p} for {d}, if success is judged by {e}?',
      f'Under an evaluation based on {e}, how does {m} influence the aim to {p} in {d}?'][style]


def build():
    rows=[]
    for di,domain in enumerate(DOMAINS):
        for ti,target in enumerate(TARGETS):
            i=di*10+ti
            facets=[{'domain':domain[0],'mechanism':MECHANISMS[(j+ti)%10][0],'purpose':target[0],'evaluation':target[2]} for j in range(5)]
            base=[question(f) for f in facets]
            syn={'domain':domain[1],'mechanism':MECHANISMS[ti%10][1],'purpose':target[1],'evaluation':target[3]}
            added=question(syn,1)
            edit=dict(facets[0]);changed=FACETS[i%4]
            edit[changed]={'purpose':TARGETS[(ti+1)%10][0],'mechanism':MECHANISMS[(ti+5)%10][0],
                           'evaluation':TARGETS[(ti+1)%10][2],'domain':DOMAINS[(di+1)%20][0]}[changed]
            vague=[
             'How might various approaches improve things in general?',
             'What unspecified methods could produce better results for diverse applications?',
             'Can something useful make systems more effective generally?',
             'Which broad techniques might help with various tasks?',
             'How can we improve stuff with new approaches?']
            matched=[]
            for q in base:
                count=len(re.findall(r'\w+',q))
                words=['Can','various','methods','improve','things','with','unspecified','changes']+['generally']*(count-8)
                matched.append(' '.join(words)+'?')
            decoy={'domain':'stellar spectral classification','mechanism':'model ensembling','purpose':'reduce predictive error','evaluation':'held-out error'}
            rows.append({'id':f'e5-{i:03d}','topic_family':f'domain-{di:02d}','topic':domain[0],
                'source':'procedurally constructed controlled-language development set; not human validated',
                'base':base,'paraphrase_added':base+[added],'facet_edit_added':base+[question(edit)],
                'clone':[base[0]]+[question(syn,j) for j in range(1,5)],'vague':vague,
                'vague_length_matched':matched,'decoy':base[:-1]+[question(decoy)],
                'paraphrase':added,'facet_edit':question(edit),'edited_facet':changed,
                'intended_facets':facets,'edit_intended_facets':edit,'paraphrase_intended_facets':facets[0],
                'semantic_annotation_status':'construction intent only; independent validation pending'})
    return rows


if __name__=='__main__':
    path=Path(__file__).resolve().parent/'data/axiom_sets_v1.jsonl'
    with path.open('x') as f:
        for r in build():f.write(json.dumps(r)+'\n')
    print('Constructed 200 five-question sets; no scores evaluated.')
