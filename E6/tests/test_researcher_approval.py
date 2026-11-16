"""Offline approval-record and prospective artifact sign-off checks."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from researcher_approval import (
    SCHEMA, DETAILS, CONFIGURATION_PATHS, ROOT, digest, file_digest,
    decision_payload, validate_approval_record, RESEARCHER_DECISION_IDS, configuration_artifact_hashes,
)


def approved_record(root):
    evidence = Path(root) / 'evidence.txt'
    evidence.write_text('offline fixture, no actual researcher approval')
    rows = []
    for number in range(1, 27):
        row = {'id': number, 'title': f'Fixture decision {number}',
               'proposed_value': {'fixture': number}, 'choice': 'accept_proposal',
               'approved_value': {'fixture': number}, 'status': 'approved',
               'resolved_details': {key: 'fixture explicit detail' for key in DETAILS[number]},
               'evidence': [{'path': 'evidence.txt', 'file_sha256': file_digest(evidence)}],
               'approved_by': 'offline test fixture', 'approved_at_utc': '2026-01-01T00:00:00Z'}
        row['approved_payload_sha256'] = digest(decision_payload(row))
        rows.append(row)
    return {'schema_version': SCHEMA, 'decisions': rows, 'configuration_signoff': None}


def resign(row):
    row['approved_payload_sha256'] = digest(decision_payload(row))


class ResearcherApprovalTests(unittest.TestCase):
    def test_signoff_hash_preparation_requires_all_artifacts_and_never_approves(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                configuration_artifact_hashes(root=directory)
            for relative in CONFIGURATION_PATHS:
                path = Path(directory) / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('offline source fixture')
            values = configuration_artifact_hashes(root=directory)
            self.assertEqual(set(values), set(CONFIGURATION_PATHS))
            self.assertTrue(all(len(value) == 64 for value in values.values()))
            with self.assertRaises(ValueError):
                configuration_artifact_hashes(root=directory, extra_paths=['../outside'])

    def test_real_record_approves_only_explicit_researcher_scope(self):
        record = json.loads((ROOT / 'E6/RESEARCHER_APPROVAL.json').read_text())
        self.assertEqual([r['id'] for r in record['decisions']], list(range(1, 27)))
        approved = {1,2,3,4,5,8,9,10,11,12,13,14,15,16,18,19,20,21,22,23,24,25,26}
        self.assertEqual({r['id'] for r in record['decisions'] if r['status'] == 'approved'}, approved)
        self.assertEqual(validate_approval_record(record, required_ids=approved), [])
        errors = validate_approval_record(record)
        self.assertEqual(errors, [])
        self.assertFalse(any('decision 24:' in error for error in errors))
        self.assertIsNotNone(record['configuration_signoff'])
        self.assertEqual(validate_approval_record(record, finalization=True), [])

    def test_explicit_null_missing_score_policy_is_complete_but_not_other_null_details(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            row = record['decisions'][11]
            row['resolved_details']['failed_cell_metric_values_by_outcome'] = {
                'missing_score': None, 'imputation': 'none', 'denominator': 'complete input-set pairs'}
            resign(row)
            self.assertEqual(validate_approval_record(record, root=directory, required_ids={12}), [])
            row['resolved_details']['failed_cell_metric_values_by_outcome']['denominator'] = None
            resign(row)
            self.assertTrue(validate_approval_record(record, root=directory, required_ids={12}))

    def test_explicit_complete_approvals_pass_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            before = copy.deepcopy(record)
            self.assertEqual(validate_approval_record(record, root=directory), [])
            self.assertEqual(record, before)

    def test_administrative_items_need_no_new_scientific_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            for number in (6, 7, 17):
                record['decisions'][number - 1]['status'] = 'pending_researcher_approval'
            self.assertEqual(validate_approval_record(record, root=directory), [])
            # An edited classification flag cannot exempt a scientific choice.
            record['decisions'][0]['status'] = 'pending_researcher_approval'
            record['decisions'][0]['separate_scientific_approval_required'] = False
            self.assertTrue(validate_approval_record(record, root=directory))

    def test_one_missing_or_duplicate_decision_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            for mutation in ('missing', 'duplicate', 'pending'):
                record = approved_record(directory)
                if mutation == 'missing':
                    record['decisions'].pop()
                elif mutation == 'duplicate':
                    record['decisions'][-1]['id'] = 1
                else:
                    record['decisions'][8]['status'] = 'pending_researcher_approval'
                self.assertTrue(validate_approval_record(record, root=directory))

    def test_changed_value_or_evidence_invalidates_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            record['decisions'][0]['approved_value'] = 'changed'
            errors = validate_approval_record(record, root=directory)
            self.assertTrue(any('payload' in e for e in errors))
            record = approved_record(directory)
            (Path(directory) / 'evidence.txt').write_text('changed source')
            self.assertTrue(any('evidence changed' in e for e in validate_approval_record(record, root=directory)))

    def test_blank_identity_future_timestamp_and_unresolved_details_block(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            row = record['decisions'][3]
            row['approved_by'] = ''
            row['approved_at_utc'] = '2999-01-01T00:00:00Z'
            row['resolved_details']['task_text_by_testbed'] = None
            resign(row)
            errors = validate_approval_record(record, root=directory)
            self.assertTrue(any('identity' in e for e in errors))
            self.assertTrue(any('unresolved detail' in e for e in errors))

    def test_replacement_requires_explicit_signed_value(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            row = record['decisions'][0]
            row['choice'] = 'replacement'
            row['approved_value'] = {'study_status': 'exploratory'}
            resign(row)
            self.assertEqual(validate_approval_record(record, root=directory), [])

    def test_finalization_requires_artifact_signoff_and_detects_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            self.assertTrue(validate_approval_record(record, root=directory, finalization=True))
            artifacts = {}
            for relative in CONFIGURATION_PATHS:
                path = Path(directory) / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fixture config')
                artifacts[relative] = file_digest(path)
            record['configuration_signoff'] = {
                'artifacts': artifacts, 'approved_by': 'test reviewer',
                'approved_at_utc': '2026-01-01T00:00:00Z',
                'approved_decisions_sha256': digest(record['decisions'])}
            self.assertEqual(validate_approval_record(record, root=directory, finalization=True), [])
            (Path(directory) / CONFIGURATION_PATHS[0]).write_text('changed')
            self.assertTrue(any('signed artifact changed' in e for e in
                                validate_approval_record(record, root=directory, finalization=True)))

    def test_evidence_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            record = approved_record(directory)
            record['decisions'][0]['evidence'][0]['path'] = '../outside'
            resign(record['decisions'][0])
            self.assertTrue(validate_approval_record(record, root=directory))
