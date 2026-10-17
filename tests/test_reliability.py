"""Failure-path, transaction and real HTTP integration coverage."""
import csv
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

import matplotlib.pyplot as plt
import requests
from werkzeug.serving import make_server

from books_api_sqlite import fetch_books, read_books, save_books
from csv_users_to_sqlite import import_users, list_users
from demo_api import app
from student_scores_api import create_chart, fetch_students, validate_students


class ReliabilityTests(unittest.TestCase):
    def test_bad_book_arguments_never_make_network_requests(self):
        with patch("books_api_sqlite.requests.get") as get:
            for query, limit in [(None, 1), (" ", 1), ("q", True), ("q", 1.5), ("q", 101)]:
                with self.subTest(query=query, limit=limit), self.assertRaises(ValueError):
                    fetch_books(query, limit)
            get.assert_not_called()

    def test_api_errors_propagate_without_accepting_partial_data(self):
        for fetch, argument in [(fetch_books, "query"), (fetch_students, "https://example.test")]:
            for error in [requests.Timeout("timeout"), requests.HTTPError("503")]:
                with self.subTest(fetch=fetch.__name__, error=type(error).__name__):
                    with patch("requests.get", side_effect=error), self.assertRaises(type(error)):
                        fetch(argument)
            response = Mock()
            response.json.side_effect = ValueError("invalid JSON")
            with patch("requests.get", return_value=response), self.assertRaises(ValueError):
                fetch(argument)

    def test_book_payload_contract(self):
        for payload in [None, [], {}, {"docs": None}, {"docs": {}}]:
            response = Mock()
            response.json.return_value = payload
            with self.subTest(payload=payload), patch("requests.get", return_value=response):
                with self.assertRaises(ValueError):
                    fetch_books("q")
        response = Mock()
        response.json.return_value = {"docs": [None, {}, {"title": ""}]}
        with patch("requests.get", return_value=response):
            self.assertEqual(fetch_books("q"), [])

    def test_same_title_distinct_authors_have_stable_distinct_keys(self):
        response = Mock()
        response.json.return_value = {"docs": [
            {"title": "Same", "author_name": ["Alice"]},
            {"title": "Same", "author_name": ["Bob"]},
        ]}
        with patch("requests.get", return_value=response):
            first = fetch_books("q")
            self.assertEqual(first, fetch_books("q"))
            self.assertNotEqual(first[0]["book_key"], first[1]["book_key"])

    def test_book_batch_rolls_back_and_repeated_save_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "books.db"
            record = dict(book_key="one", title="Original", author="A", publication_year=2000)
            save_books(db, [record])
            changed = dict(record, title="Changed")
            with self.assertRaises(sqlite3.IntegrityError):
                save_books(db, [changed, dict(record, book_key="bad", title=None)])
            self.assertEqual(read_books(db), [("Original", "A", 2000)])
            save_books(db, [changed, changed])
            self.assertEqual(read_books(db), [("Changed", "A", 2000)])

    def test_student_payload_contract(self):
        for payload in [None, {}, [], [None], [{}], [{"score": True}], [{"score": 101}],
                        [{"score": -1}], [{"score": "NaN"}], [{"score": "inf"}],
                        [{"score": 10, "student": None}], [{"score": 10, "student": " "}]]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_students(payload)
        self.assertEqual(validate_students([{"score": "0"}, {"score": 100}])[0],
                         {"student": "Student 1", "score": 0.0})

    def test_chart_direct_input_and_save_failure_close_figures(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                create_chart([], Path(tmp) / "empty.png")
            before = plt.get_fignums()
            with patch("matplotlib.figure.Figure.savefig", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    create_chart([{"student": "A", "score": 50}], Path(tmp) / "bad.png")
            self.assertEqual(plt.get_fignums(), before)

    def test_csv_bom_case_and_repeated_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, db = Path(tmp) / "users.csv", Path(tmp) / "users.db"
            source.write_text("\ufeff NAME , Email \nAlice,a@example.com\nUpdated,A@EXAMPLE.COM\n", encoding="utf-8")
            self.assertEqual(import_users(source, db), {"inserted": 1, "updated": 1, "skipped": 0})
            self.assertEqual(import_users(source, db), {"inserted": 0, "updated": 2, "skipped": 0})
            self.assertEqual(list_users(db), [("Updated", "a@example.com")])

    def test_bad_csv_quoting_rolls_back_earlier_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, db = Path(tmp) / "users.csv", Path(tmp) / "users.db"
            source.write_text('name,email\nValid,valid@example.com\n"unterminated', encoding="utf-8")
            with self.assertRaises(csv.Error):
                import_users(source, db)
            self.assertEqual(list_users(db), [])

    def test_csv_database_failure_rolls_back_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, db = Path(tmp) / "users.csv", Path(tmp) / "users.db"
            list_users(db)
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.execute("CREATE TRIGGER fail_insert BEFORE INSERT ON users WHEN NEW.name = 'Fail' BEGIN SELECT RAISE(ABORT, 'injected'); END")
            source.write_text("name,email\nValid,a@example.com\nFail,b@example.com\n", encoding="utf-8")
            with self.assertRaises(sqlite3.IntegrityError):
                import_users(source, db)
            self.assertEqual(list_users(db), [])

    def test_real_http_student_cli(self):
        server = make_server("127.0.0.1", 0, app)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                chart, summary = Path(tmp) / "chart.png", Path(tmp) / "summary.json"
                result = subprocess.run([
                    sys.executable, str(Path(__file__).resolve().parents[1] / "student_scores_api.py"),
                    "--api-url", f"http://127.0.0.1:{server.server_port}/students",
                    "--chart", str(chart), "--json-output", str(summary),
                ], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(json.loads(summary.read_text())["average_score"], 81.2)
                self.assertEqual(chart.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
