"""Synthetic evidence in temporary directories only; no model calls."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import ExitStack
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
import literature_review_documents as reviews
import error_analysis_memo as memo
from ingest_independent_review import ingest
from literature_source_components import component_form
from literature_finalization import extraction_source
from researcher_approval import digest
import test_literature_finalization as review_fixtures
from test_researcher_approval import resign
from evaluation import ARMS,evaluate_literature_seven_arm_outputs


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))

class ReviewBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        review_fixtures.LiteratureFinalizationTests.setUpClass();cls.base=review_fixtures.LiteratureFinalizationTests()
    def fixture(self,root):
        approval=self.base.approval(root)
        decision=approval['decisions'][23]
        decision['resolved_details']['review_policy'].update(check_fields=list(reviews.CHECKS),require_error_and_correction_records=True)
        resign(decision)
        rows=self.base.reviews(approval);selected=set(self.base.worklist['selected_input_set_ids'])
        sidecars=[]
        for row in self.base.extracted:
            if row['input_set_id'] not in selected:continue
            sidecar=component_form(row);_,text=extraction_source(row);quote=text[:12]
            for entry in sidecar['components'].values():
                entry.update(text=quote,source_quote=quote,character_span=[0,len(quote)],annotator_id='fixture-annotator',annotated_at_utc='2020-01-01T00:00:00Z')
            sidecars.append(sidecar)
        by_id={r['input_set_id']:r for r in sidecars}
        originals=[]
        for index,row in enumerate(rows):
            row.update(reviewer_slot=index%2+1,packet_sha256='fixture-packet',
                source_component_sidecar_sha256=digest(by_id[row['input_set_id']]),
                extraction_errors=[],corrections=[],reviewer_notes='Synthetic source review only.',
                check_evidence={key:{'rationale':'Synthetic fixture.','source_quote_or_location':'abstract, initial span'} for key in reviews.CHECKS},
                **{key:True for key in reviews.CHECKS})
            originals.append(copy.deepcopy(row))
        source=root/'source';source.mkdir()
        paths={}
        for key,value in [('candidate',self.base.candidate),('proposal',self.base.proposal),('extraction_manifest',self.base.manifest),('worklist',self.base.worklist)]:
            paths[key]=key+'.json';write(root/paths[key],value)
        write(root/'E6/RESEARCHER_APPROVAL.json',approval)
        write(source/'evidence_bundle.json',{'review_bundle_paths':paths})
        write(source/'independent_review_forms.json',originals)
        for unit in selected:write(source/'packets'/(unit+'.json'),{'source_component_sidecar':by_id[unit]})
        write(root/'components.json',sidecars)
        return source,rows
    def sheets(self,root,rows):
        paths=[]
        for slot in (1,2):
            path=root/f'reviewer{slot}.md'
            path.write_text('\n\n'.join('```review-response\n'+json.dumps(r)+'\n```' for r in rows if r['reviewer_slot']==slot))
            paths.append(path)
        return paths
    def test_completed_forms_validate_and_export_to_existing_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,rows=self.fixture(root);sheets=self.sheets(root,rows)
            with patch.object(reviews,'ROOT',root),patch.object(reviews,'verify_bundle'):
                report=reviews.ingest(source,*sheets,components=root/'components.json')
                self.assertTrue(report['annotations_usable']);self.assertEqual(report['human_reviews_completed'],40)
                paths=reviews.export_validated(report,source,root/'export',None,root/'components.json')
                from literature_finalization import validate_review_bundle
                bundle={k:json.loads((root/p).read_text()) for k,p in paths.items()}
                self.assertTrue(validate_review_bundle(**bundle,approval=json.loads((root/'E6/RESEARCHER_APPROVAL.json').read_text()),root=root)['annotations_usable'])
    def test_missing_adjudication_and_matching_negatives_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,rows=self.fixture(root);rows[0][reviews.CHECKS[0]]=False
            with patch.object(reviews,'ROOT',root),patch.object(reviews,'verify_bundle'):
                report=reviews.ingest(source,*self.sheets(root,rows),components=root/'components.json')
                self.assertFalse(report['annotations_usable']);self.assertEqual(len(report['adjudication_required']),1)
                pair=rows[:2]
                final={'input_set_id':pair[0]['input_set_id'],'adjudicator_id':'fixture-third',
                    'adjudicated_at_utc':'2020-01-01T00:00:00Z','rationale':'Synthetic adjudication fixture only.',
                    'review_records_sha256':digest(sorted(pair,key=lambda r:r['reviewer_id'])),**{key:True for key in reviews.CHECKS}}
                write(root/'adjudications.json',[final])
                accepted=reviews.ingest(source,*self.sheets(root,rows),components=root/'components.json',adjudications=root/'adjudications.json')
                self.assertTrue(accepted['annotations_usable'])
                rows[1][reviews.CHECKS[0]]=False
                rejected=reviews.ingest(source,*self.sheets(root,rows),components=root/'components.json')
                self.assertFalse(rejected['annotations_usable'])
                with self.assertRaisesRegex(ValueError,'scoring blocked'):
                    reviews.export_validated(rejected,source,root/'blocked',None,root/'components.json')
                self.assertFalse((root/'blocked').exists())

class AnalysisBridgeTests(unittest.TestCase):
    def test_native_literature_outputs_feed_input_set_statistics(self):
        outputs={arm:{'execution_status':'succeeded','output':{'hypotheses':[{'text':'Fixture hypothesis','question_text':'Fixture question?'}]}} for arm in ARMS}
        outputs['HQ']={'execution_status':'failed'}
        bundle=evaluate_literature_seven_arm_outputs('fixture-paper',outputs,{'research_question':'Fixture question?','main_hypothesis':'Fixture hypothesis'},
            similarity_evaluator=lambda a,b:4,same_question_evaluator=lambda a,b:True,
            similarity_policy_id='fixture-only',same_question_policy_id='fixture-only',reference_provenance={})
        native=memo.reconstruction_metrics(bundle,'fixture-paper','D')
        self.assertEqual(native['main_hypothesis_best_similarity'],4)
        self.assertIsNone(memo.reconstruction_metrics(bundle,'fixture-paper','HQ')['main_hypothesis_best_similarity'])
        sources=[{'input_set_id':'fixture-paper','records':[{'input_set_id':'fixture-paper','stage':'verified_input_set_scalar','evaluation_input':{'field':'main_hypothesis_best_similarity'},'provenance':{'arm':arm},'status':'succeeded' if arm!='HQ' else 'blocked','parsed_output':{'value':4 if arm!='HQ' else None}} for arm in ARMS]}]
        config=json.loads((memo.ROOT/'E6/config.json').read_text());evaluation=json.loads((memo.ROOT/'E6/evaluation_config.json').read_text());evaluation['paired_bootstrap']['replicates']=5
        result=memo.summarize_metric(sources,'literature','main_hypothesis_best_similarity',config,evaluation)
        self.assertEqual(result['arm_estimates']['D']['point_estimate'],4)
        self.assertIsNone(result['arm_estimates']['HQ']['point_estimate'])
    def test_compiled_hdr_payloads_are_bound_and_recomputed(self):
        from test_hdr_pipeline import HDRPipelineTests
        import hdr_pipeline
        form,mapping,payload,truth,sha=HDRPipelineTests().fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write(root/hdr_pipeline.TRUTH,truth)
            payload['provenance']['ground_truth_source_sha256']=memo.file_digest(root/hdr_pipeline.TRUTH)
            with patch.object(hdr_pipeline,'load_compilation',return_value={form['generation_input_set_id']:{form['arm']:payload}}),patch.object(hdr_pipeline,'checked_forms',return_value=([form],[])):
                values=memo.compiled_hdr_metrics('fixture',root)
            self.assertEqual(values[form['generation_input_set_id'],form['arm']],.25)
            with patch.object(hdr_pipeline,'load_compilation',return_value={}),patch.object(hdr_pipeline,'checked_forms',return_value=([form],[])):
                self.assertEqual(memo.compiled_hdr_metrics('fixture',root),{})
    def test_human_diversity_null_is_completed_abstention_not_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);predictions=[];cases=[];sheet=[]
            for i in range(10):
                cid=f'diversity-{i+1:02d}';predictions.append({'case_id':cid,'section':'diversity','expected':None,'prediction':False})
                cases.append({'case_id':cid,'a':'Fixture A','b':'Fixture B'})
                sheet.append(f'## {cid}\n\nA: Fixture A\nB: Fixture B\nIndependent label: null  Reviewer/date: fixture-human / 2020-01-01\nRationale: Fixture insufficient source evidence.\n')
            write(root/'predictions.json',predictions);write(root/'human_review.json',cases);(root/'sheet.md').write_text('\n'.join(sheet))
            report=ingest(root/'sheet.md',root/'predictions.json')
            self.assertEqual(report['human_labels_verified'],10)
            self.assertEqual(report['sections']['diversity']['agreement_count'],0)
            self.assertEqual(report['validations_genuinely_completed'],0)
            self.assertTrue(all(r['label'] is None and r['verified_fields_complete'] for r in report['records']))

if __name__=='__main__':unittest.main()
