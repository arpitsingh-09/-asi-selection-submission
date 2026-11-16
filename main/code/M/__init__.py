"""First working shared research-question space; no inference or evaluation on import."""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
from .schema import Phi,Paper,LeakageError,MissingInputError
from .store import PaperStore
from .encoders import HashEncoder,CachedEncoder,MissingEmbeddingError
from .engine import ResearchSpace
from .quality import QualityModels
from .temporal import split_for,validate_split
from .controls import controls,sample_same_topic_decoy


def encode(q,R,t,*,papers=(),encoder=None,**kwargs):
    return ResearchSpace(papers,encoder).encode(q,R,t,**kwargs)


__all__=['Phi','Paper','PaperStore','ResearchSpace','HashEncoder','CachedEncoder','QualityModels',
         'LeakageError','MissingInputError','MissingEmbeddingError','encode','controls',
         'sample_same_topic_decoy','split_for','validate_split']
