"""Import users from CSV into SQLite, validating rows and upserting duplicate emails."""
from __future__ import annotations
import argparse
import csv
import re
import sqlite3
from pathlib import Path

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def initialize_database(db_path: str | Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

def import_users(csv_path: str | Path, db_path: str | Path) -> dict[str, int]:
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    initialize_database(db_path)
    inserted = updated = skipped = 0
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = {header.strip().lower() for header in (reader.fieldnames or [])}
        if not {"name", "email"}.issubset(headers):
            raise ValueError("CSV must contain 'name' and 'email' columns")
        # One transaction avoids opening a new SQLite connection for every CSV row.
        with sqlite3.connect(db_path) as conn:
            for row_number, raw_row in enumerate(reader, start=2):
                if None in raw_row or any(value is None for value in raw_row.values()):
                    skipped += 1
                    print(f"Skipping malformed CSV row {row_number}")
                    continue
                row = {key.strip().lower(): value.strip()
                       for key, value in raw_row.items()}
                name, email = row.get("name", ""), row.get("email", "")
                if not name or not EMAIL_RE.fullmatch(email):
                    skipped += 1
                    print(f"Skipping CSV row {row_number}: missing name or invalid email")
                    continue
                exists = conn.execute(
                    "SELECT 1 FROM users WHERE email = ? COLLATE NOCASE", (email,)
                ).fetchone()
                conn.execute("""
                    INSERT INTO users (name, email) VALUES (?, ?)
                    ON CONFLICT(email) DO UPDATE SET
                      name = excluded.name, imported_at = CURRENT_TIMESTAMP
                """, (name, email))
                if exists:
                    updated += 1
                else:
                    inserted += 1
    return {"inserted": inserted, "updated": updated, "skipped": skipped}

def list_users(db_path: str | Path) -> list[tuple]:
    initialize_database(db_path)
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT name, email FROM users ORDER BY name COLLATE NOCASE").fetchall()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="data/users.csv")
    parser.add_argument("--db", default="users.db")
    args = parser.parse_args()
    try:
        print("Import summary:", import_users(args.csv, args.db))
        print("\nUsers in database:")
        for name, email in list_users(args.db):
            print(f"- {name} <{email}>")
        return 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(f"Error: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
