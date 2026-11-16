"""Offline sample freezing and real-record validation; model replies are test fixtures."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_prepare_literature_sample_proposal import candidate_manifest
from test_researcher_approval import approved_record, resign
from prepare_literature_sample_proposal import build_literature_sample_proposal, extract_proposed_literature_sample
from researcher_approval import digest, file_digest
from literature_finalization import (
    build_freeze_plan, build_frozen_literature_manifest, prepare_extraction_review,
    validate_extracted_candidates, validate_review_bundle, CHECK_FIELDS, SOURCE_CONTENT_CHECK_FIELDS, freeze_approved_selection,
)

MODEL = {'model': 'offline-fixture-only'}


class LiteratureFinalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = candidate_manifest()
        cls.proposal = build_literature_sample_proposal(cls.candidate, sample_size=100, seed=2026)
        raw = json.dumps({'research_question': 'Fixture question?', 'main_hypothesis': 'Fixture hypothesis.',
                          'research_question_explicit': True, 'main_hypothesis_explicit': True})
        cls.extracted = extract_proposed_literature_sample(
            cls.candidate, cls.proposal, lambda stage, prompt: raw, model_configuration=MODEL)
        cls.manifest, cls.worklist = prepare_extraction_review(
            cls.candidate, cls.proposal, cls.extracted, model_configuration=MODEL)

    def approval(self, root):
        record = approved_record(root)
        guide = Path(root) / 'guide.md'
        guide.write_text('offline guide fixture')
        record['decisions'][4]['resolved_details']['sample_proposal_sha256'] = self.proposal['proposal_sha256']
        row = record['decisions'][23]
        row['resolved_details'] = {
            'extraction_model_configuration': MODEL,
            'review_policy': {'reviewer_count': 2, 'guide_path': 'guide.md',
                              'guide_sha256': file_digest(guide),
                              'disagreement_policy': 'independent_adjudicator'}}
        resign(record['decisions'][4]); resign(row)
        return record

    def reviews(self, approval):
        guide_hash = approval['decisions'][23]['resolved_details']['review_policy']['guide_sha256']
        return [dict(input_set_id=case['input_set_id'], reviewer_id=reviewer,
                     reviewed_at_utc='2026-01-01T00:00:00Z', manual_check_completed=True,
                     extraction_sha256=digest(case['target_extraction']),
                     target_source_text_sha256=case['target_source_text_sha256'],
                     review_guide_sha256=guide_hash, **{key: True for key in CHECK_FIELDS})
                for case in self.worklist['reviews'] for reviewer in ('fixture-a', 'fixture-b')]

    def validate(self, approval, records, root, adjudications=None, **overrides):
        args = dict(candidate=self.candidate, proposal=self.proposal,
                    extraction_manifest=self.manifest, worklist=self.worklist,
                    records=records, adjudications=adjudications or [], approval=approval, root=root)
        args.update(overrides)
        return validate_review_bundle(**args)

    def test_explicit_freeze_operation_requires_approval_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'selected.json'
            record = self.approval(directory)
            plan = build_freeze_plan(self.candidate, self.proposal)
            pending = copy.deepcopy(record)
            pending['decisions'][4]['status'] = 'pending_researcher_approval'
            with self.assertRaises(ValueError):
                freeze_approved_selection(self.candidate, self.proposal, plan, pending, path, root=directory)
            self.assertFalse(path.exists())
            before = copy.deepcopy(record)
            selected = freeze_approved_selection(self.candidate, self.proposal, plan, record, path, root=directory)
            self.assertEqual(json.loads(path.read_text()), selected)
            self.assertEqual(record, before)
            self.assertFalse(selected['target_annotations_validated'])
            with self.assertRaises(FileExistsError):
                freeze_approved_selection(self.candidate, self.proposal, plan, record, path, root=directory)

    def test_problem_method_result_review_requires_actual_records_and_records_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            approval = self.approval(directory)
            row = approval['decisions'][23]
            row['resolved_details']['review_policy'].update(
                check_fields=list(CHECK_FIELDS + SOURCE_CONTENT_CHECK_FIELDS),
                require_error_and_correction_records=True)
            resign(row)
            records = self.reviews(approval)
            with self.assertRaisesRegex(ValueError, 'incomplete human review'):
                self.validate(approval, records, directory)
            for record in records:
                record.update({key: True for key in SOURCE_CONTENT_CHECK_FIELDS})
            with self.assertRaisesRegex(ValueError, 'errors, corrections and source notes'):
                self.validate(approval, records, directory)
            for record in records:
                record.update(extraction_errors=[], corrections=[], reviewer_notes='offline source fixture')
            self.assertTrue(self.validate(approval, records, directory)['annotations_usable'])
            records[0]['method_extraction_accurate'] = False
            with self.assertRaisesRegex(ValueError, 'independent source-bound adjudication'):
                self.validate(approval, records, directory)
            records[1]['method_extraction_accurate'] = False
            records[0]['extraction_errors'] = ['fixture method omitted']
            self.assertFalse(self.validate(approval, records, directory)['annotations_usable'])

    def test_real_selected_manifest_is_source_frozen_without_completed_reviews(self):
        import hashlib
        from researcher_approval import ROOT
        from literature_finalization import verify_seal
        selected_path = ROOT / 'E6/data/literature_selected_manifest_v1.json'
        selected = json.loads(selected_path.read_text())
        verify_seal(selected)
        self.assertEqual(len(selected['input_sets']), 100)
        self.assertEqual(len(set(selected['selected_input_set_ids'])), 100)
        self.assertEqual(len(selected['manual_review_input_set_ids']), 20)
        self.assertFalse(selected['target_annotations_validated'])
        for paper in selected['input_sets']:
            self.assertGreaterEqual(sum(isinstance(ref.get('abstract'), str) and bool(ref['abstract'].strip())
                                        for ref in paper['references']), 10)
        approval = json.loads((ROOT / 'E6/RESEARCHER_APPROVAL.json').read_text())
        snapshot = json.loads((ROOT / 'E6/data/literature_selection_approval_v1.json').read_text())
        self.assertEqual(selected['approval_record_sha256'], digest(snapshot))
        frozen = approval['frozen_artifacts']['literature_selected_manifest']
        self.assertEqual(hashlib.sha256(selected_path.read_bytes()).hexdigest(), frozen['file_sha256'])
        self.assertEqual(frozen['reviews_completed'], 0)

    def test_freeze_plan_is_deterministic_and_does_not_freeze(self):
        first = build_freeze_plan(self.candidate, self.proposal)
        self.assertEqual(first, build_freeze_plan(self.candidate, self.proposal))
        self.assertFalse(first['sample_frozen'])
        self.assertEqual(len(first['extraction_jobs']), 100)
        self.assertEqual(len(first['proposed_manual_review_input_set_ids']), 20)

    def test_freeze_requires_explicit_hash_bound_sample_approval(self):
        with tempfile.TemporaryDirectory() as root:
            approval = self.approval(root)
            plan = build_freeze_plan(self.candidate, self.proposal)
            frozen = build_frozen_literature_manifest(self.candidate, self.proposal, plan, approval, root=root)
            self.assertTrue(frozen['input_sets_frozen'])
            self.assertFalse(frozen['target_annotations_validated'])
            approval['decisions'][4]['status'] = 'pending_researcher_approval'
            with self.assertRaisesRegex(ValueError, 'explicit researcher approval'):
                build_frozen_literature_manifest(self.candidate, self.proposal, plan, approval, root=root)

    def test_changed_plan_is_rejected_even_if_rehashed(self):
        with tempfile.TemporaryDirectory() as root:
            plan = build_freeze_plan(self.candidate, self.proposal)
            plan['proposed_manual_review_input_set_ids'].reverse()
            plan['manifest_sha256'] = digest({k: v for k, v in plan.items() if k != 'manifest_sha256'})
            with self.assertRaisesRegex(ValueError, 'freeze plan differs'):
                build_frozen_literature_manifest(self.candidate, self.proposal, plan, self.approval(root), root=root)

    def test_changed_sources_duplicate_ids_and_raw_output_are_rejected(self):
        for change in ('source', 'duplicate', 'raw', 'prompt', 'model'):
            extracted = copy.deepcopy(self.extracted)
            row = extracted[0]
            if change == 'source': row['target']['abstract'] = 'altered'
            if change == 'duplicate': extracted[1] = extracted[0]
            if change == 'raw': row['target_extraction']['raw_output'] = '{}'
            if change == 'prompt': row['target_extraction']['evaluation_input']['rendered_prompt'] = 'altered'
            if change == 'model': row['target_extraction']['provenance']['model_configuration'] = {'model': 'other'}
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_extracted_candidates(self.candidate, self.proposal, extracted, MODEL)

    def test_twenty_cases_with_two_source_bound_reviews_pass(self):
        with tempfile.TemporaryDirectory() as root:
            approval = self.approval(root)
            result = self.validate(approval, self.reviews(approval), root)
            self.assertEqual(result['completed_unique_cases'], 20)
            self.assertTrue(result['annotations_usable'])

    def test_missing_duplicate_foreign_or_stale_reviews_block(self):
        with tempfile.TemporaryDirectory() as root:
            approval = self.approval(root)
            for change in ('missing', 'duplicate', 'foreign', 'hash', 'boolean', 'time'):
                reviews = self.reviews(approval)
                if change == 'missing': reviews.pop()
                if change == 'duplicate': reviews[1]['reviewer_id'] = reviews[0]['reviewer_id']
                if change == 'foreign': reviews[0]['input_set_id'] = 'foreign'
                if change == 'hash': reviews[0]['extraction_sha256'] = '0' * 64
                if change == 'boolean': reviews[0][CHECK_FIELDS[0]] = 1
                if change == 'time': reviews[0]['reviewed_at_utc'] = 'no time'
                with self.subTest(change=change), self.assertRaises(ValueError):
                    self.validate(approval, reviews, root)

    def test_disagreement_requires_independent_bound_adjudication(self):
        with tempfile.TemporaryDirectory() as root:
            approval = self.approval(root)
            reviews = self.reviews(approval)
            reviews[0][CHECK_FIELDS[0]] = False
            with self.assertRaisesRegex(ValueError, 'adjudication'):
                self.validate(approval, reviews, root)
            adjudication = dict(input_set_id=reviews[0]['input_set_id'], adjudicator_id='fixture-c',
                                adjudicated_at_utc='2026-01-01T00:00:00Z', rationale='fixture rationale',
                                review_records_sha256=digest(sorted(reviews[:2], key=lambda r: r['reviewer_id'])),
                                **{key: True for key in CHECK_FIELDS})
            self.assertTrue(self.validate(approval, reviews, root, [adjudication])['annotations_usable'])
            adjudication['adjudicator_id'] = reviews[0]['reviewer_id']
            with self.assertRaises(ValueError):
                self.validate(approval, reviews, root, [adjudication])

    def test_matching_negative_checks_complete_review_but_block_acceptance(self):
        with tempfile.TemporaryDirectory() as root:
            approval = self.approval(root)
            reviews = self.reviews(approval)
            reviews[0][CHECK_FIELDS[0]] = reviews[1][CHECK_FIELDS[0]] = False
            result = self.validate(approval, reviews, root)
            self.assertEqual(result['completed_unique_cases'], 20)
            self.assertFalse(result['annotations_usable'])

    def test_rehashed_worklist_source_change_rejected_by_bundle(self):
        with tempfile.TemporaryDirectory() as root:
            approval = self.approval(root)
            worklist = copy.deepcopy(self.worklist)
            worklist['reviews'][0]['target_source_text'] = 'altered'
            worklist['worklist_sha256'] = digest({k: v for k, v in worklist.items() if k != 'worklist_sha256'})
            with self.assertRaisesRegex(ValueError, 'worklist differs'):
                self.validate(approval, self.reviews(approval), root, worklist=worklist)
