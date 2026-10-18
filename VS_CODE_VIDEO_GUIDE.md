# Run and explain the assignment in VS Code

This guide is for the code in the `quality-hardening-2026-10` branch of the [AccuKnox assignment repository](https://github.com/srivisnuA/accuknox-ai-ml-assignment/tree/quality-hardening-2026-10). Download [that branch as a ZIP](https://github.com/srivisnuA/accuknox-ai-ml-assignment/archive/refs/heads/quality-hardening-2026-10.zip), extract it, then use **File → Open Folder** in VS Code to open the extracted `accuknox-ai-ml-assignment-quality-hardening-2026-10` folder. The terminal must be at the folder containing `requirements.txt`, `demo.py`, and `assignment_1`.

These are AI-assisted study and demonstration materials. Review the code, test each command, and describe your own contribution accurately in the recording.

## One-time VS Code setup (Windows)

Open **Terminal → New Terminal** in VS Code. Check `python --version`; use Python 3.10 or newer. If `python` opens the Microsoft Store or is not found, try `py -3.10 --version` and use `py -3.10` in the first command below. Create an environment and install the three project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

In VS Code, use **Ctrl+Shift+P → Python: Select Interpreter** and select `.venv\Scripts\python.exe` in this folder. The commands below name that interpreter explicitly, so they also work before interpreter selection. If VS Code initially opens a different directory, run `cd` to the extracted repository root first. Do not open just an individual question folder as the workspace: the `python -m ...` commands rely on the repository root.

## Part A, Question 1 — Books API and SQLite

Open `assignment_1/question_01/books_api_sqlite.py`. In the VS Code terminal, run:

```powershell
.\.venv\Scripts\python.exe -m assignment_1.question_01.books_api_sqlite --query "python programming" --limit 5 --db books.db
```

This question needs internet access. The terminal prints books **read back from SQLite**. Open Library's live results can change. The generated database is `books.db` at the repository root.

**Say:** “The script requests books from Open Library, checks the response, and keeps the title, author, and publication year. SQLite stores them under a book key. `ON CONFLICT` updates a matching book when I run it again, so the same key does not create a duplicate. Missing titles are skipped, and SQL parameters keep data separate from the query.” Point at `fetch_books`, `save_books`, and `read_books`, then run it. The fallback key is based on metadata, so changing metadata can change that key.

## Part A, Question 2 — Student API, mean, and chart

Open `assignment_1/question_02/demo_api.py` and `student_scores_api.py`. Use **Terminal → New Terminal** twice. In terminal 1, start the local sample API and leave it running:

```powershell
.\.venv\Scripts\python.exe -m assignment_1.question_02.demo_api
```

In terminal 2, from the same repository root, run:

```powershell
.\.venv\Scripts\python.exe -m assignment_1.question_02.student_scores_api
```

The output should report **5 students** and an **81.20** average. Click `outputs/student_scores.png` in VS Code to show the chart. The JSON data comes from `http://127.0.0.1:8000/students`; you can open that URL in a browser. Stop the API with **Ctrl+C** in terminal 1 when finished.

**Say:** “No student API was specified, so this local Flask service supplies fictional sample data over HTTP. The client validates that scores are finite numbers between 0 and 100, calculates the mean, and draws one bar per student with a line for the mean. It also saves a JSON summary.” Point at `fetch_students`, `validate_students`, and `create_chart`. If the client reports “connection refused,” start terminal 1 first.

## Part A, Question 3 — CSV to SQLite

Open `assignment_1/question_03/data/users.csv`, then `csv_users_to_sqlite.py`. Run:

```powershell
.\.venv\Scripts\python.exe -m assignment_1.question_03.csv_users_to_sqlite --db users.db
```

Run the **same command a second time**. With a fresh `users.db`, the first run inserts four valid rows and skips one invalid row; the second run updates those four and skips the same invalid row. If you already ran the command, the first visible run may show updates because the database persists. For a fresh recording, use a new name such as `video_users.db` in both commands.

**Say:** “`DictReader` reads named CSV columns. The program checks the required headers and each name and email, skips bad rows, and writes valid users in one transaction. Email has a case-insensitive unique constraint. Repeating the import updates those users rather than making duplicates. A parsing or database failure rolls back the batch.” Point at `import_users` and the `ON CONFLICT(email)` SQL. The email rule checks format; it does not verify mailbox ownership.

## Part A, Questions 4 and 5 — FaceFare code walkthrough

The submitted answers link to the [FaceFare repository](https://github.com/srivisnuA/FaceFare/tree/f649acac36682042c6ec657a5d3e89cc768b4077). **You do not need to install or run FaceFare for this video.** Open the excerpts already in this ZIP: `assignment_1/question_04/code_excerpt.txt` and `assignment_1/question_05/code_excerpt.sql`. The excerpts are portions of the full code, not standalone scripts.

For Question 4, the relevant full source is [`database/models.py`, `change_balance`](https://github.com/srivisnuA/FaceFare/blob/f649acac36682042c6ec657a5d3e89cc768b4077/database/models.py). Show the excerpt and explain:

> “This function adjusts a passenger wallet. It validates the input, converts money to integer cents, and starts a SQLite write transaction. An `operation_id` prevents a retry from charging twice. It checks for insufficient funds, then updates the balance and inserts a ledger entry in the same transaction. If the transaction fails, both changes roll back.”

For Question 5, open the SQL excerpt and the full [`database/db.py`](https://github.com/srivisnuA/FaceFare/blob/f649acac36682042c6ec657a5d3e89cc768b4077/database/db.py). Explain:

> “The `passengers` table keeps the current balance; `wallet_transactions` stores each change in integer cents. The foreign key links the ledger to a passenger, `CHECK` constraints reject negative recorded balances and unsupported transaction kinds, and a unique `operation_id` supports retry protection. The index helps load a passenger’s transactions in order.”

The schema currently cascades passenger deletion to their transactions; in a production payment system, audit retention would need separate review. Avoid claiming this snippet runs a face recognition model.

## Optional ChestXpert snippet explanation

ChestXpert is a separate project, not an extra numbered question in this assignment. If you want to mention another project briefly, open its [dataset split validation code](https://github.com/srivisnuA/ChestXpert-Explainable-Chest-X-Ray-AI/blob/ff14a4ecf749a1c024b91a40a9be912511cc3d60/app/preprocessing/splits.py) in your browser. A useful section is:

```python
if train_names & test_names:
    raise ValueError("Training/test image overlap detected")
# The same function also checks patient IDs across train, validation and test.
```

**Say:** “The split checker rejects duplicate image IDs and overlapping train/test images. If patient IDs are present, it also rejects a patient appearing in more than one split. This matters because otherwise the model could be evaluated on images from a patient it saw during training, making the result look better than it is. The file validates provided split lists; it does not create the medical dataset or prove clinical performance.”

If you would rather discuss explainability, the [Grad-CAM class](https://github.com/srivisnuA/ChestXpert-Explainable-Chest-X-Ray-AI/blob/ff14a4ecf749a1c024b91a40a9be912511cc3d60/app/explainability/gradcam.py) captures a convolutional layer’s activations and gradients, weights the activation maps, upsamples and normalizes the heatmap. Describe it as a model visualization, not a medical explanation or diagnosis.

## Part B — speak from the response document

No code needs to run for Part B. Show the Word response and summarize each table in your own words: **Q1:** B, “can code under supervision,” in the four requested areas; **Q2:** authenticated input, permission-checked retrieval, LLM response with sources, and evaluation; **Q3:** embeddings and why PostgreSQL with pgvector is a candidate for an existing PostgreSQL help desk. These are proposed designs, not deployed features.

## Recording order and quick checks

Show the repository root in VS Code, then Q1 run, Q2 two-terminal run and chart, Q3 twice, FaceFare Q4/Q5 excerpts, optional ChestXpert snippet, and Part B tables. Use the output you actually see rather than memorizing live API rows. The short `README.md` and each question’s `answer.txt` remain useful prompts during practice.

If a module cannot import, confirm VS Code opened the repository root and that `.venv` was created there. If Q2 fails to connect, start the sample API in the other terminal. If port 8000 is busy, stop a previous copy of the sample API. The ZIP does not include trained medical model weights or private FaceFare data; neither is needed for this walkthrough.
