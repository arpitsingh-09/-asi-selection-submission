import hashlib
import copy
import json
from pathlib import Path
import tempfile
import unittest
from M.training import run,validate_record,rows
from M.schema import LeakageError
from M.quality import QualityModels


def record(i,year,value=None):
    t=f'{year}-02-01'
    return {'question_id':str(i),'paper_id':str(i),'question':f'Does mechanism {i} improve image classification accuracy?',
        'input_paper_ids':[],'published':t,'available_at':t,'source_dataset':'synthetic-test',
        'provenance':{'fixture':True},'labels':{'peer_review':None if value is None else
            {'value':value,'observed_at':f'{year}-06-01','source':'fixture-only','definition':'test-rating','evidence_text':'synthetic test outcome','evidence_sha256':hashlib.sha256(b'synthetic test outcome').hexdigest()},'later_community_use':None}}

class TrainingTests(unittest.TestCase):
    def test_temporal_and_labels(self):
        r=record(1,2023,2)
        self.assertEqual(validate_record(r),'train')
        for change in ({'available_at':'2024-01-01'},{'published':'unknown'}):
            x=copy.deepcopy(r);x.update(change)
            with self.assertRaises(ValueError):validate_record(x)
        for change in ({'observed_at':'2024-01-01'},{'source':''},{'evidence_sha256':''},{'value':float('nan')},{'evidence_text':'tampered'}):
            x=copy.deepcopy(r);x['labels']['peer_review'].update(change)
            with self.assertRaises(ValueError):validate_record(x)

    def execute(self,train,val):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);p=Path(tmp.name)
        for name,data in [('train',train),('validation',val)]:
            (p/name).write_text(''.join(json.dumps(r)+'\n' for r in data))
        return p,run(p/'train',p/'validation',p/'output')

    def test_missing_labels_unavailable(self):
        p,r=self.execute([record(1,2023)],[record(2,2024)])
        self.assertTrue(all(h['status']=='unavailable' for h in r['heads'].values()))
        self.assertFalse(list((p/'output').glob('peer_review.json')))

    def test_deterministic_train_and_validation(self):
        tr=[record(1,2022,1),record(2,2023,3),record(3,2023,4)];va=[record(4,2024,2)]
        a,x=self.execute(tr,va);b,y=self.execute(tr,va)
        self.assertEqual(x,y)
        model=QualityModels.load(a/'output/peer_review.json')
        self.assertIsNone(model.artifact['heads']['later_community_use'])
        self.assertEqual((a/'output/peer_review.json').read_bytes(),(b/'output/peer_review.json').read_bytes())
        self.assertEqual(x['heads']['peer_review']['validation_ids'],['4'])
        self.assertEqual(set(x['heads']['peer_review']['training_ids']),{'1','2','3'})

    def test_wrong_split_rejected(self):
        with self.assertRaises(LeakageError):self.execute([record(1,2025,2)],[record(2,2024,3)])

    def test_overlap_rejected(self):
        with self.assertRaises(LeakageError):self.execute([record(1,2023,2)],[record(1,2024,3)])

    def test_target_definition_mismatch(self):
        r=record(3,2024,2);r['labels']['peer_review']['definition']='different'
        with self.assertRaises(ValueError):self.execute([record(1,2022,1),record(2,2023,3)],[r])

    def test_real_manifests_unique_and_time_bound(self):
        root=Path(__file__).resolve().parents[1]/'data/manifests_v2'
        for split in ('train','validation','test'):
            rs=rows(root/(split+'.jsonl'))
            self.assertEqual(len(rs),len({r['question_id'] for r in rs}))
            for r in rs:self.assertEqual(validate_record(r),split)
