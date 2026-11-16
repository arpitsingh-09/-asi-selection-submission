import copy
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime,timezone
from M.s1_review import prepare,import_reviews,rows,jsonl
from M.s1_encoder import validate_requests
from M.s1_metrics import paired_metrics
from M.tests.test_evaluation import fixtures

class S1WorkflowTests(unittest.TestCase):
    def setup_packet(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);p=Path(tmp.name)
        prepare(Path(__file__).resolve().parents[2],p/'packet')
        return p,rows(p/'packet/blind_review_template.jsonl')

    def reviews(self,packet,reviewer,label=True):
        rs=copy.deepcopy(packet)
        for r in rs:r.update(reviewer_id=reviewer,reviewer_kind='human',independent_of_author=True,
            same_question=label,source_alignment_verified=True,rationale='Synthetic workflow test only, not an actual annotation.',reviewed_at='2025-01-01T00:00:00Z')
        return rs

    def test_packet_blind_pending_and_dates_not_imputed(self):
        p,packet=self.setup_packet();manifest=rows(p/'packet/annotation_manifest.jsonl')
        self.assertEqual(len(packet),122)
        self.assertTrue(all(r['same_question'] is None and 'task' not in r and 'source_author' not in r for r in packet))
        self.assertTrue(all(r['question_publication_date'] is None and r['original_input_ids'] is None and not r['eligible'] for r in manifest))

    def test_templates_cannot_create_human_confirmation(self):
        p,packet=self.setup_packet();jsonl(p/'empty.jsonl',packet)
        s=import_reviews(p/'packet/annotation_manifest.jsonl',[p/'empty.jsonl'],p/'import')
        self.assertEqual(s['human_verified_pairs'],0);self.assertEqual(s['eligible_pairs'],0)

    def test_two_human_attestations_consensus_still_ineligible(self):
        p,packet=self.setup_packet()
        # Synthetic fixtures test attestations; they are never saved in real outputs.
        for name in ('reader1','reader2'):jsonl(p/(name+'.jsonl'),self.reviews(packet,name))
        s=import_reviews(p/'packet/annotation_manifest.jsonl',[p/'reader1.jsonl',p/'reader2.jsonl'],p/'import')
        self.assertEqual(s['human_verified_pairs'],122);self.assertEqual(s['eligible_pairs'],0)

    def test_disagreement_duplicate_and_ai_rejected(self):
        for mode in ('disagree','duplicate','AI'):
            p,packet=self.setup_packet();a=self.reviews(packet,'reader1');b=self.reviews(packet,'reader2',mode!='disagree')
            if mode=='duplicate':b=self.reviews(packet,'reader1')
            if mode=='AI':
                for r in b:r['reviewer_kind']='AI'
            jsonl(p/'a',a);jsonl(p/'b',b)
            s=import_reviews(p/'packet/annotation_manifest.jsonl',[p/'a',p/'b'],p/'out')
            self.assertEqual(s['human_verified_pairs'],0)

    def test_changed_pair_or_context_rejected(self):
        p,packet=self.setup_packet();review=self.reviews(packet,'reader1');review[0]['anchor']='changed';review[1]['source_context']['abstract']='changed'
        jsonl(p/'a',review);s=import_reviews(p/'packet/annotation_manifest.jsonl',[p/'a'],p/'out')
        self.assertGreaterEqual(len(s['rejected_reviews']),2)

    def test_encoder_request_bounds(self):
        self.assertEqual(validate_requests({'texts':['a'],'count':1}),['a'])
        for x in ({'texts':['a','a'],'count':2},{'texts':['a'],'count':2},{'texts':['a']*257,'count':257}):
            with self.assertRaises(ValueError):validate_requests(x)

    def test_bq_paired_statistics_synthetic_only(self):
        r=paired_metrics(fixtures('S1'),synthetic=True,draws=30)
        self.assertEqual(r['controls']['original']['accuracy']['near_miss'],{'Phi':1.,'B-Q':0.})
        with self.assertRaises(ValueError):paired_metrics(fixtures('S1'))

    def test_generated_sidecar_exact_requests_and_integrity(self):
        from M.encoders import CachedEncoder
        import hashlib
        import numpy as np
        root=Path(__file__).resolve().parents[1]/'data/s1_review_v3'
        cache=root/'minilm_vectors.json'
        if not cache.exists():self.skipTest('bounded encoder preparation has not run')
        obj=json.loads(cache.read_text());requests=json.loads((root/'embedding_requests.json').read_text())
        self.assertEqual(obj['request_file_sha256'],hashlib.sha256((root/'embedding_requests.json').read_bytes()).hexdigest())
        self.assertEqual(obj['revision'],'1110a243fdf4706b3f48f1d95db1a4f5529b4d41')
        self.assertEqual(len(obj['records']),183);self.assertFalse(obj['training_cutoff_verified'])
        encoder=CachedEncoder(cache)
        try:
            for text in requests['texts']:
                v=encoder.encode(text);self.assertEqual(len(v),384);self.assertTrue(np.isfinite(v).all());self.assertAlmostEqual(float(np.linalg.norm(v)),1.,places=5)
        finally:encoder.close()
