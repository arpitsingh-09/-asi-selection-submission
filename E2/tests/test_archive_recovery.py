import hashlib
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from recover_openreview_archive import public_time,join_records
from freeze_recovered_inputs import prior_references

class ArchiveRecoveryTests(unittest.TestCase):
    def test_no_creation_date_substitution(self):
        self.assertIsNone(public_time({'cdate':1,'tmdate':2}))
    def test_public_and_publication_fields_retained(self):
        r=public_time({'odate':2000,'pdate':3000,'cdate':1})
        self.assertEqual(r['field'],'odate');self.assertEqual(r['milliseconds'],2000)
        self.assertEqual(public_time({'pdate':1000})['field'],'pdate')
    def test_match_by_forum_and_preserve_original_abstract(self):
        b=[{'id':1,'forum_id':'forum','title':'A TITLE','idea':'edited','label':'POSITIVE','rating':6,'contribution':3}]
        notes=[{'id':'other','content':{}},{'id':'forum','content':{'title':{'value':'A title'},'abstract':{'value':'original'}},'odate':2000}]
        r=join_records(b,notes)['forum']
        self.assertEqual(r['abstract'],'original');self.assertFalse(r['abstract_exact_match'])
        self.assertTrue(r['title_exact_normalized_match'])
    def test_duplicate_archive_matches_rejected(self):
        b=[{'id':1,'forum_id':'f','title':'T','idea':'A','label':'NEGATIVE','rating':2,'contribution':1}]
        n={'id':'f','content':{'title':'T','abstract':'A'}}
        with self.assertRaises(ValueError):join_records(b,[n,n])
    def test_reference_date_strictness(self):
        records=[{'public_date':'2024-01-01T00:00:00+00:00'},
                 {'public_date':'2025-01-01T00:00:00+00:00'}, {'public_date':None}]
        self.assertEqual(prior_references(records,'2025-01-01T00:00:00+00:00'),records[:1])
    def test_recovered_inputs_have_bound_original_abstracts(self):
        p=Path(__file__).resolve().parents[1]/'analysis/recovered_inputs_v1/benchmark_inputs.jsonl'
        if not p.exists():self.skipTest('archive input artifact absent')
        records=list(map(json.loads,p.read_text().splitlines()))
        self.assertEqual(len(records),299)
        for r in records:
            self.assertEqual(hashlib.sha256(r['abstract'].encode()).hexdigest(),r['abstract_sha256'])
            self.assertEqual(hashlib.sha256(r['idea'].encode()).hexdigest(),r['idea_sha256'])
            self.assertNotEqual(r['abstract_source'],r['idea_source'])

class RecoveredBaselineBindingTests(unittest.TestCase):
    def test_edited_idea_cannot_stand_in_for_original_abstract(self):
        from evaluate_human_check import validate_abstract_binding
        r=[{'idea':'edited','abstract':'original'}]
        with self.assertRaises(ValueError):validate_abstract_binding(r,[hashlib.sha256(b'edited').hexdigest()])
        validate_abstract_binding(r,[hashlib.sha256(b'original').hexdigest()])
        with self.assertRaises(ValueError):validate_abstract_binding([{'idea':'edited'}],[])
    def test_shared_excerpt_recovery_uses_saved_claims(self):
        root=Path(__file__).resolve().parents[1]
        folder=root/'analysis/shared_excerpt_recovery_v1'
        if not folder.exists():self.skipTest('artifact absent')
        from recover_claims import candidates
        for r in map(json.loads,(folder/'candidate_review.jsonl').read_text().splitlines()):
            if not r['promote']:continue
            note=json.loads((root/r['source']).read_text().splitlines()[r['line']-1])
            self.assertTrue(any(isinstance(c,dict) and c.get('claim')==r['claim'] and c.get('evidence')==r['evidence'] for c,_ in candidates(note)))
            self.assertFalse(r['human_review'])
