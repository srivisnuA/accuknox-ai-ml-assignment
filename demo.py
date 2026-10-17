"""Run reproducible demonstrations; optionally include the live books service."""
import argparse
import json
from pathlib import Path
import threading

from werkzeug.serving import make_server
from books_api_sqlite import fetch_books, read_books, save_books
from csv_users_to_sqlite import import_users, list_users
from demo_api import app
from student_scores_api import create_chart, fetch_students


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/demo"))
    parser.add_argument("--live-books", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        students = fetch_students(f"http://127.0.0.1:{server.server_port}/students")
        average = create_chart(students, args.output / "student_scores.png")
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    db = args.output / "users.db"
    result = {
        "student_source": "Fictional local HTTP API",
        "student_count": len(students), "average_score": average,
        "csv_first_run": import_users(Path(__file__).parent / "data/users.csv", db),
        "csv_repeat_run": import_users(Path(__file__).parent / "data/users.csv", db),
        "users": list_users(db),
    }
    if args.live_books:
        books = fetch_books("python programming", limit=5)
        book_db = args.output / "books.db"
        save_books(book_db, books)
        save_books(book_db, books)
        result["books_source"] = "Live Open Library Search API"
        result["books"] = read_books(book_db, 5)
    output = json.dumps(result, indent=2)
    (args.output / "results.json").write_text(output, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
