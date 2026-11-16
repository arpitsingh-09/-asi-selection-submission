import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import prepare_required_evidence as p
from inductive_execution import bound_hdr_score
from test_readiness import required_evidence_gates
from researcher_approval import file_digest

PACK=p.ROOT/'E6/data/required_evidence_v1'

def load(name):return json.loads((PACK/name).read_text())

class RequiredEvidenceTests(unittest.TestCase):
    def test_all_source_packets_verify_without_network(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('network prohibited')):
            report=p.validate_bundle(PACK/'bundle.json')
        self.assertEqual(report['literature_source_records_complete'],100)
        self.assertEqual(report['literature_fixed_model_extractions_complete'],0)
        self.assertEqual(report['HDR_inputs_complete'],0)
    def test_no_fabricated_reviews_or_scores(self):
        reviews=load('literature_review_forms.json');forms=load('HDR_judgment_forms.json')
        self.assertEqual(len(reviews),40);self.assertEqual(len(forms),125)
        for r in reviews:
            self.assertIsNone(r['reviewer_id']);self.assertFalse(r['manual_check_completed'])
            self.assertIsNone(r['extraction_errors'])
        for form in forms:
            self.assertIsNone(form['discovered_feature_ids']);self.assertIsNone(form['relationship_scores'])
            self.assertIsNone(form['provenance']['judge_provenance'])
        self.assertEqual(load('hdr_inputs_actual.json'),{})
    def test_exact_ground_truth_quotations_and_grouping(self):
        rules=load('ground_truth_rule_inventory.json');proposal=load('HDR_feature_mapping_proposal.json')
        self.assertEqual(len(rules),14);self.assertFalse(proposal['approved_HDR_denominator'])
        self.assertEqual(len(proposal['reference_feature_ids']),3)
        for r in rules:
            a,b=r['predicate_value_span'];self.assertEqual(r['source_text'][a:b],r['predicate_value'])
            a,b=r['relationship_span'];self.assertEqual(r['source_text'][a:b],r['relationship_quote'])
    def test_pending_HDR_form_cannot_score_as_zero(self):
        form=load('HDR_judgment_forms.json')[0]
        truth=json.loads((p.ROOT/'data/HypoBench-datasets/synthetic/election/level2/gt_hypotheses_level2.json').read_text())
        context=SimpleNamespace(test_manifest={'dataset_ground_truth':{'source_file_sha256':form['provenance']['ground_truth_source_sha256'],'hypotheses':truth}})
        with self.assertRaises(ValueError):bound_hdr_score(context,form['generation_input_set_id'],form['arm'],form['hypotheses'],form)
    def test_terminal_missing_cells_include_all_0007_arms(self):
        missing=load('terminal_missing_cells.json')
        self.assertEqual(len(missing),15)
        self.assertEqual(len([r for r in missing if r['status']=='unresolved_0007_do_not_retry']),7)
    def test_readiness_integration_retains_blockers(self):
        result=required_evidence_gates(PACK/'bundle.json')
        self.assertFalse(result['scoring_ready']);self.assertTrue(result['blockers'])
        self.assertEqual(result['HDR_inputs_complete'],0)
    def test_changed_source_text_rejected_even_with_updated_file_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'evidence';shutil.copytree(PACK,dest)
            rows=json.loads((dest/'literature_source_records.json').read_text());rows[0]['target_source_text']='fabricated'
            (dest/'literature_source_records.json').write_text(json.dumps(rows))
            bundle=json.loads((dest/'bundle.json').read_text())
            bundle['artifact_file_hashes']['literature_source_records.json']=file_digest(dest/'literature_source_records.json')
            (dest/'bundle.json').write_text(json.dumps(bundle))
            with self.assertRaisesRegex(ValueError,'source mismatch'):p.validate_bundle(dest/'bundle.json')

if __name__=='__main__':unittest.main()
