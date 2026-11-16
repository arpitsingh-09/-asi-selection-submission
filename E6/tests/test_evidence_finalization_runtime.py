import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from researcher_approval import ROOT,digest
from ingest_independent_review import ingest
from run_literature_extraction import run_one
from literature_source_components import component_form,validate_components,validate_component_reviews

SAVED=ROOT/'E6/data/evaluator_validation_train_v2_finalized'
MODEL={'model':'fixture-only','max_output_tokens':2048}
RAW=json.dumps({'research_question':'Fixture question?','main_hypothesis':'Fixture hypothesis.',
                'research_question_explicit':True,'main_hypothesis_explicit':True})

class Client:
    model_configuration={'model':'fixture-only'}
    def __init__(self,fail=False):self.calls=0;self.fail=fail
    def call_with_token_limit(self,stage,prompt,*,max_output_tokens):
        self.calls+=1
        if self.fail:raise RuntimeError('fixture backend failure')
        return {'raw_response':RAW,'output_tokens':9}

class EvidenceRuntimeTests(unittest.TestCase):
    def row(self):return {'input_set_id':'fixture-target','target':{'abstract':'Problem. Method. Result.'}}
    def test_actual_review_sheet_is_blank(self):
        r=ingest(SAVED/'human_review_blind.md',SAVED/'verified_responses.json')
        self.assertEqual(r['human_labels_verified'],0)
        self.assertTrue(all(s['agreement_rate'] is None for s in r['sections'].values()))
    def test_genuine_field_format_metrics_fixture_not_validation_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp);sheet=(SAVED/'human_review_blind.md').read_text()
            predictions=json.loads((SAVED/'verified_responses.json').read_text())
            # Clearly labeled offline test references, never written to real evidence.
            import re
            blocks=re.split(r'(^## [a-z_]+-\d+\s*$)',sheet,flags=re.M)
            refs={r['case_id']:r for r in predictions}
            for i in range(1,len(blocks),2):
                cid=blocks[i].strip()[3:];value=refs[cid]['prediction']
                blocks[i+1]=blocks[i+1].replace('Independent label: ______  Reviewer/date: ______',f'Independent label: {str(value).lower()}  Reviewer/date: fixture-human / 2020-01-01').replace('Rationale: ______','Rationale: Offline test fixture only.')
            (dest/'sheet.md').write_text(''.join(blocks));(dest/'human_review.json').write_bytes((SAVED/'human_review.json').read_bytes())
            r=ingest(dest/'sheet.md',SAVED/'verified_responses.json')
            self.assertEqual(r['human_labels_verified'],10)
            self.assertTrue(all(s['agreement_rate']==1 for s in r['sections'].values()))
            self.assertEqual(r['validations_genuinely_completed'],0)
    def test_completed_extraction_replayed_without_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client();r=run_one(self.row(),MODEL,client,Path(tmp),'fixture-plan')
            self.assertEqual(client.calls,1)
            self.assertEqual(run_one(self.row(),MODEL,Client(True),Path(tmp),'fixture-plan'),r)
    def test_failed_call_is_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=Client(True);r=run_one(self.row(),MODEL,client,Path(tmp),'fixture-plan')
            self.assertEqual(r['target_extraction']['status'],'failed')
            second=Client();self.assertEqual(run_one(self.row(),MODEL,second,Path(tmp),'fixture-plan'),r)
            self.assertEqual(second.calls,0)
    def test_interrupted_request_blocks_reissue(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);client=Client();run_one(self.row(),MODEL,client,d,'fixture-plan')
            (d/'extraction_checkpoint.json').unlink();(d/'response.json').unlink()
            second=Client()
            with self.assertRaisesRegex(ValueError,'interrupted'):run_one(self.row(),MODEL,second,d,'fixture-plan')
            self.assertEqual(second.calls,0)
    def test_durable_response_recovers_without_new_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);r=run_one(self.row(),MODEL,Client(),d,'fixture-plan');(d/'extraction_checkpoint.json').unlink()
            second=Client();self.assertEqual(run_one(self.row(),MODEL,second,d,'fixture-plan'),r)
            self.assertEqual(second.calls,0)
    def test_sidecar_keeps_four_field_output_and_checks_exact_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            row=run_one(self.row(),MODEL,Client(),Path(tmp),'fixture-plan');before=copy.deepcopy(row)
            sidecar=component_form(row)
            with self.assertRaises(ValueError):validate_components(row,sidecar)
            text=row['target']['abstract']
            for component,quote in [('problem','Problem.'),('method','Method.'),('result','Result.')]:
                pos=text.index(quote);sidecar['components'][component]={'text':quote,'source_quote':quote,'character_span':[pos,pos+len(quote)],'annotator_id':'fixture-annotator','annotated_at_utc':'2020-01-01T00:00:00Z'}
            self.assertTrue(validate_components(row,sidecar));self.assertEqual(row,before)
            reviews=[{'input_set_id':row['input_set_id'],'source_component_sidecar_sha256':digest(sidecar),**{k+'_extraction_accurate':True for k in ('problem','method','result')}} for _ in range(2)]
            self.assertTrue(validate_component_reviews([row],[sidecar],reviews,[row['input_set_id']]))
            sidecar['components']['method']['source_quote']='fabrication'
            with self.assertRaisesRegex(ValueError,'quotation'):validate_components(row,sidecar)

if __name__=='__main__':unittest.main()
