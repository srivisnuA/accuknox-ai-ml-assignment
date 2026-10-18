-- AI-assisted excerpt copied from FaceFare/database/db.py.
-- Source, branch quality-hardening-2026-10:
-- https://github.com/srivisnuA/FaceFare/blob/f649acac36682042c6ec657a5d3e89cc768b4077/database/db.py
-- The passengers table must exist first; see the full source for initialization and migration logic.

CREATE TABLE IF NOT EXISTS wallet_transactions (
    id INTEGER PRIMARY KEY,
    pid TEXT NOT NULL REFERENCES passengers(pid)
        ON UPDATE CASCADE ON DELETE CASCADE,
    delta_cents INTEGER NOT NULL,
    balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0),
    kind TEXT NOT NULL CHECK (kind IN ('opening', 'adjustment', 'set')),
    operation_id TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS wallet_transactions_pid
    ON wallet_transactions(pid, id);
