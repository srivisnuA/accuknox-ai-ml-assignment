import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from assignment_1.question_01.books_api_sqlite import fetch_books, read_books, save_books
from assignment_1.question_02.student_scores_api import create_chart, fetch_students
from assignment_1.question_03.csv_users_to_sqlite import import_users, list_users



class AssignmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    @patch("assignment_1.question_01.books_api_sqlite.requests.get")
    def test_book_api_and_sqlite(self, mock_get):
        response = Mock()
        response.json.return_value = {"docs": [{"key": "/works/OL1W", "title": "Example Book",
          "author_name": ["A. Author"], "first_publish_year": 2020}]}
        response.raise_for_status = Mock()
        mock_get.return_value = response
        books = fetch_books("example", 1)
        self.assertEqual(books[0]["author"], "A. Author")
        db = self.root / "books.db"
        self.assertEqual(save_books(db, books), 1)
        self.assertEqual(read_books(db)[0][0], "Example Book")

    @patch("assignment_1.question_02.student_scores_api.requests.get")
    def test_student_average_and_chart(self, mock_get):
        response = Mock()
        response.raise_for_status = Mock()
        response.json.return_value = {"students": [{"student": "Asha", "score": 80},
                                                    {"student": "Bala", "score": 100}]}
        mock_get.return_value = response
        students = fetch_students("http://example.test/students")
        chart = self.root / "scores.png"
        self.assertEqual(create_chart(students, chart), 90)
        self.assertTrue(chart.exists())
    @patch("assignment_1.question_02.student_scores_api.requests.get")
    def test_invalid_student_scores(self, mock_get):
        response = Mock()
        response.json.return_value = {"students": [{"student": "A", "score": "nan"}]}
        mock_get.return_value = response
        with self.assertRaises(ValueError):
            fetch_students("http://example.test/students")

    @patch("assignment_1.question_01.books_api_sqlite.requests.get")
    def test_invalid_books_payload(self, mock_get):
        response = Mock()
        response.json.return_value = {"docs": "not-a-list"}
        mock_get.return_value = response
        with self.assertRaises(ValueError):
            fetch_books("example")


    def test_csv_malformed_rows(self):
        path = self.root / "malformed.csv"
        path.write_text("name,email\nAsha,asha@example.com,extra\nBala\n", encoding="utf-8")
        db = self.root / "malformed.db"
        self.assertEqual(import_users(path, db), {"inserted": 0, "updated": 0, "skipped": 2})


    def test_csv_import_and_duplicate_update(self):
        path = self.root / "users.csv"
        path.write_text("name,email\nAsha,asha@example.com\nBad,not-an-email\n", encoding="utf-8")
        db = self.root / "users.db"
        self.assertEqual(import_users(path, db), {"inserted": 1, "updated": 0, "skipped": 1})
        path.write_text("name,email\nAsha Updated,asha@example.com\n", encoding="utf-8")
        self.assertEqual(import_users(path, db)["updated"], 1)
        self.assertEqual(list_users(db)[0][0], "Asha Updated")

if __name__ == "__main__":
    unittest.main()
