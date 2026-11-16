import hashlib
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task3_eligibility import validate_review


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.b = [{'forum_id':'a','abstract':'original','published':'2025-10-08T00:00:00Z'}]
        self.r = [{'forum_id':'a','abstract_sha256':hashlib.sha256(b'original').hexdigest(),
                   'first_publication_verified':True,'source':'local primary evidence',
                   'first_public_date':'2025-02-01T00:00:00Z'}]
        self.bound = '2024-12-31T23:59:59.999999Z'

    def check_review(self):
        validate_review(self.r,self.b,self.bound,self.bound)

    def test_valid(self):
        self.check_review()

    def test_equal_cutoff(self):
        self.r[0]['first_public_date'] = self.bound
        with self.assertRaises(ValueError): self.check_review()

    def test_after_archive(self):
        self.r[0]['first_public_date'] = '2026-01-01T00:00:00Z'
        with self.assertRaises(ValueError): self.check_review()

    def test_text_binding(self):
        self.r[0]['abstract_sha256'] = 'edited'
        with self.assertRaises(ValueError): self.check_review()

    def test_truthy_is_not_verified(self):
        self.r[0]['first_publication_verified'] = 'false'
        with self.assertRaises(ValueError): self.check_review()

    def test_earlier_cutoff(self):
        with self.assertRaises(ValueError):
            validate_review(self.r,self.b,'2023-01-01T00:00:00Z',self.bound)

    def test_duplicate(self):
        self.r *= 2
        with self.assertRaises(ValueError): self.check_review()

    def test_naive(self):
        self.r[0]['first_public_date'] = '2025-02-01'
        with self.assertRaises(ValueError): self.check_review()

    def test_history_before_first_publication_not_just_archive(self):
        with self.assertRaisesRegex(ValueError, 'history must precede'):
            validate_review(self.r,self.b,self.bound,self.bound,
                            [{'published':'2025-03-01T00:00:00Z'}])
