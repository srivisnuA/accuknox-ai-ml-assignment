# AccuKnox AI/ML Assignment

**Repository owner:** Srivisnu A

Each question has its own numbered folder and individual `answer.txt`. Practical code and sample inputs are stored with their question. Shared dependencies, tests, and verification records remain at repository level.

These materials include AI-assisted work. The provided problem statement prohibits copying and ChatGPT use; these files must not be represented as independently authored work.

## Problem Statement 1 / Assignment 1

| Question | Topic | Answer | Implementation or excerpt |
|---|---|---|---|
| 1 | API data retrieval and SQLite storage | [answer.txt](assignment_1/question_01/answer.txt) | [books_api_sqlite.py](assignment_1/question_01/books_api_sqlite.py) |
| 2 | Student scores, average, and bar chart | [answer.txt](assignment_1/question_02/answer.txt) | [student_scores_api.py](assignment_1/question_02/student_scores_api.py), [sample API](assignment_1/question_02/demo_api.py), [chart](assignment_1/question_02/student_scores.png) |
| 3 | CSV import to SQLite | [answer.txt](assignment_1/question_03/answer.txt) | [csv_users_to_sqlite.py](assignment_1/question_03/csv_users_to_sqlite.py), [sample CSV](assignment_1/question_03/data/users.csv) |
| 4 | Complex Python code | [answer.txt](assignment_1/question_04/answer.txt) | [FaceFare function excerpt](assignment_1/question_04/code_excerpt.txt) |
| 5 | Complex database code | [answer.txt](assignment_1/question_05/answer.txt) | [FaceFare schema excerpt](assignment_1/question_05/code_excerpt.sql) |

## Assignment 2

| Question | Topic | Answer |
|---|---|---|
| 1 | LLM, Deep Learning, AI, and ML self-rating | [answer.txt](assignment_2/question_01/answer.txt) |
| 2 | High-level LLM chatbot architecture | [answer.txt](assignment_2/question_02/answer.txt) |
| 3 | Vector databases and a hypothetical database choice | [answer.txt](assignment_2/question_03/answer.txt) |

The selected self-rating is **B — can code under supervision** for all four areas. Each theory response is in its own text file.

## Setup

Use Python 3.10 or newer. Run commands from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run Assignment 1

Question 1 — requires internet access:

```bash
python -m assignment_1.question_01.books_api_sqlite --query "python programming" --limit 10 --db books.db
```

Question 2 — start the sample API in one terminal:

```bash
python -m assignment_1.question_02.demo_api
```

Then run the consumer in a second terminal:

```bash
python -m assignment_1.question_02.student_scores_api
```

The five sample scores average **81.20**. The chart and JSON summary are written to `outputs/`. To use another service, pass `--api-url http://localhost:8000/students`. Expected JSON is a list of `{"student":"Asha","score":88}` records, optionally wrapped in a `students` property.

Question 3 — the default sample CSV is resolved relative to its script:

```bash
python -m assignment_1.question_03.csv_users_to_sqlite --db users.db
```

Use `--csv path/to/users.csv` for another input. Questions 4 and 5 contain source links and excerpts for inspection; the excerpts depend on the full FaceFare project.

## Assumptions and behavior

- Open Library supplies book search data because the question specifies no API. Missing authors become `Unknown`; invalid years become SQL NULL; records without a usable title are skipped.
- Book keys prevent duplicate imports. If a key is missing, a title/author/year hash supplies a fallback; changed metadata may produce a different fallback key.
- The student API uses fictional data because no endpoint is provided. Scores must be finite numbers between 0 and 100. Empty datasets and invalid records are rejected.
- CSV columns must include `name,email` (case-insensitive). UTF-8 BOMs and extra named columns are supported. Invalid rows are skipped; duplicate emails update existing users.
- Duplicate/blank CSV headers are errors. Malformed quoting aborts and rolls back the import. Database writes use parameterized SQL, transactions, and explicit connection closing.

## Demonstration and verification

```bash
python demo.py
python demo.py --live-books
python -m unittest discover -s tests -v
```

The demo starts and stops its own local HTTP API, calculates the mean and chart, and imports the CSV twice. Results go to `outputs/demo/`; use `--output` with a fresh directory to reproduce first-import counts. `--live-books` also exercises Open Library.

See [verification records](docs/VERIFICATION.md) and [recorded demo results](docs/demo-results.json). Tests cover malformed API responses, rollback behavior, repeated imports, validation failures, and a real local HTTP CLI run.
