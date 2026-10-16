# AccuKnox AI/ML Assignment — Python + SQLite

**Author:** Srivisnu A

This repository contains three practical Python exercises demonstrating REST API retrieval, SQLite persistence, data visualization, and CSV import.

## Tasks

1. **Books API → SQLite** — `books_api_sqlite.py` fetches book search results from Open Library, stores the title/author/publication year in SQLite, and displays saved records.
2. **Student scores → average and bar chart** — `student_scores_api.py` retrieves scores from an HTTP endpoint, validates them, calculates the mean, saves a chart, and writes a JSON summary.
3. **CSV → SQLite** — `csv_users_to_sqlite.py` validates a CSV file and imports users, updating duplicate email addresses and reporting invalid rows.
4. **Local sample API** — `demo_api.py` serves fictional student scores so the chart example can run reproducibly without an external student-data service.
5. **Tests** — `tests/test_assignment.py` exercises API parsing (with mocked requests), database persistence, chart creation, and CSV duplicate handling.

## Assumptions

- Open Library Search API is used for books because it supplies title, author names, and first publication year.
- The assignment does not specify a student-score API, so `demo_api.py` provides a small local Flask API; the consumer accepts a configurable URL.
- Scores are percentages from 0 through 100. Invalid scores are rejected.
- SQLite is used for this local exercise. SQL values are parameterized, and unique keys prevent duplicate records.
- CSV columns are `name,email` (case-insensitive). Invalid rows are skipped with a message.

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run task 1 — Books API

Requires internet access.

```bash
python books_api_sqlite.py --query "python programming" --limit 10 --db books.db
```

The database is created automatically. Re-running updates existing book keys.

## Run task 2 — Student scores

Terminal 1:

```bash
python demo_api.py
```

Terminal 2:

```bash
python student_scores_api.py
```

Sample scores are 88, 76, 92, 81, and 69; the average is **81.20**. Outputs are written to `outputs/student_scores.png` and `outputs/student_scores_summary.json`.

To use a different API:

```bash
python student_scores_api.py --api-url http://localhost:8000/students
```

Expected JSON format is either `[{"student":"Asha","score":88}]` or `{"students":[{"student":"Asha","score":88}]}`.

## Run task 3 — CSV import

```bash
python csv_users_to_sqlite.py --csv data/users.csv --db users.db
```

The sample CSV includes an intentionally invalid email to demonstrate validation.

## Run tests

```bash
python -m unittest discover -s tests -v
```

The tests mock API requests, so they do not require internet access.

## Design choices

- HTTP calls use timeouts and raise errors for unsuccessful responses.
- Database writes use context managers and parameterized SQL.
- Unique identifiers and upserts make repeated runs safe against duplicate inserts.
- Matplotlib's non-interactive backend saves charts on headless machines.
- For production, consider structured logging, retry/backoff, schema migrations, pagination/rate-limit handling, and more comprehensive validation.

## Files

```text
.
├── books_api_sqlite.py
├── student_scores_api.py
├── csv_users_to_sqlite.py
├── demo_api.py
├── requirements.txt
├── data/users.csv
└── tests/test_assignment.py
```
