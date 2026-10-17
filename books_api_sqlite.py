"""Fetch books from Open Library, persist them to SQLite, and display saved rows."""
from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
from typing import Any
import requests

OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

def fetch_books(query: str, limit: int = 10, timeout: int = 15) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("query must not be empty")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    response = requests.get(OPEN_LIBRARY_URL, params={
        "q": query, "limit": limit,
        "fields": "key,title,author_name,first_publish_year"
    }, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("docs"), list):
        raise ValueError("Unexpected books API response format")
    books = []
    for doc in payload["docs"]:
        if not isinstance(doc, dict):
            continue
        raw_title = doc.get("title")
        title = raw_title.strip() if isinstance(raw_title, str) else ""
        if not title:
            continue
        authors = doc.get("author_name") or []
        if not isinstance(authors, list):
            authors = []
        authors = [author.strip() for author in authors if isinstance(author, str) and author.strip()]
        year = doc.get("first_publish_year")
        if isinstance(year, bool) or not isinstance(year, int) or not 0 < year <= 9999:
            year = None
        raw_key = doc.get("key")
        book_key = raw_key.strip() if isinstance(raw_key, str) and raw_key.strip() else f"title:{title.casefold()}"
        books.append({
            "book_key": book_key,
            "title": title,
            "author": ", ".join(authors) if authors else "Unknown",
            "publication_year": year,
        })
    return books

def initialize_database(db_path: str | Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                book_key TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publication_year INTEGER,
                retrieved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_books(db_path: str | Path, books: list[dict[str, Any]]) -> int:
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.executemany("""
            INSERT INTO books (book_key, title, author, publication_year)
            VALUES (:book_key, :title, :author, :publication_year)
            ON CONFLICT(book_key) DO UPDATE SET
                title = excluded.title, author = excluded.author,
                publication_year = excluded.publication_year,
                retrieved_at = CURRENT_TIMESTAMP
        """, books)
    return len(books)

def read_books(db_path: str | Path, limit: int = 20) -> list[tuple]:
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        return conn.execute("""
            SELECT title, author, publication_year FROM books
            ORDER BY title COLLATE NOCASE LIMIT ?
        """, (limit,)).fetchall()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="python programming")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--db", default="books.db")
    args = parser.parse_args()
    try:
        books = fetch_books(args.query, args.limit)
        count = save_books(args.db, books)
        print(f"Retrieved and stored {count} book record(s) in {args.db}\n")
        rows = read_books(args.db, args.limit)
        print(f"{'TITLE':55} | {'AUTHOR':30} | YEAR")
        print("-" * 100)
        for title, author, year in rows:
            print(f"{title[:55]:55} | {author[:30]:30} | {year or 'Unknown'}")
        return 0
    except (requests.RequestException, ValueError, sqlite3.Error) as exc:
        print(f"Error: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
