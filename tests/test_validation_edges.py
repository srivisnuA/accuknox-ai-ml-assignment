"""Regression tests for malformed external data and CSV headers."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from assignment_1.question_01.books_api_sqlite import fetch_books
from assignment_1.question_02.student_scores_api import fetch_students
from assignment_1.question_03.csv_users_to_sqlite import import_users


class ValidationEdgeTests(unittest.TestCase):
    @patch("assignment_1.question_01.books_api_sqlite.requests.get")
    def test_book_fields_with_unexpected_types_are_sanitized(self, get):
        response = Mock()
        response.json.return_value = {"docs": [
            {"title": {"unexpected": "object"}, "author_name": ["X"]},
            {"title": "  Clean Title  ", "author_name": [" Alice ", None, 7],
             "first_publish_year": "not a year", "key": 123},
        ]}
        get.return_value = response
        records = fetch_books("books")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "Clean Title")
        self.assertEqual(records[0]["author"], "Alice")
        self.assertIsNone(records[0]["publication_year"])
        self.assertTrue(records[0]["book_key"].startswith("fallback:"))

    @patch("assignment_1.question_02.student_scores_api.requests.get")
    def test_boolean_student_score_is_rejected(self, get):
        response = Mock()
        response.json.return_value = {"students": [{"student": "A", "score": True}]}
        get.return_value = response
        with self.assertRaises(ValueError):
            fetch_students("http://example.test/students")

    def test_duplicate_case_insensitive_csv_headers_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.csv"
            path.write_text("name,NAME,email\nFirst,Second,a@example.com\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                import_users(path, Path(tmp) / "users.db")

    def test_empty_csv_header_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty-header.csv"
            path.write_text("name,,email\nA,unused,a@example.com\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "empty"):
                import_users(path, Path(tmp) / "users.db")


if __name__ == "__main__":
    unittest.main()
