# Verification record

Executed on 18 October 2026 with CPython 3.10 on Windows.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` | 21 tests passed |
| `python demo.py --live-books` | Live Open Library retrieval + real local HTTP student API + SQLite imports succeeded |
| Student mean | 81.20 from five fictional records |
| Fresh CSV import | 4 inserts, 0 updates, 1 skipped |
| Repeat CSV import | 0 inserts, 4 updates, 1 skipped |
| Chart inspection | Labels, mean line and axes readable |

Regression coverage includes timeouts/HTTP failures/invalid JSON, wrong payload shapes,
boolean/non-finite scores, missing student names, duplicate/empty CSV headers, BOMs,
case-insensitive email updates, SQL failures rolling back earlier batch writes, and
chart cleanup when saving fails. One test invokes the actual student CLI in a subprocess
against a real local HTTP server. Unit tests do not require internet access.

`docs/demo-results.json` records the executed demo, not a fixed Open Library fixture.
Book search results can change. CI also checks Python 3.10, 3.11 and 3.12; consult the
PR checks for remote results rather than inferring them from the local run.

References: [Open Library Search API](https://openlibrary.org/dev/docs/api/search),
[SQLite connection context managers](https://docs.python.org/3/library/sqlite3.html#how-to-use-the-connection-context-manager).
