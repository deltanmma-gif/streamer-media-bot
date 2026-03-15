from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from .models import SourceItem

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    published_at TEXT NOT NULL,
    summary TEXT NOT NULL,
    fingerprint TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    collected_count INTEGER NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT ''
);
"""


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def insert_items(self, items: Iterable[SourceItem]) -> int:
        payload = [
            (
                item.source_id,
                item.source_name,
                item.category,
                item.title,
                item.url,
                item.published_at,
                item.summary,
                item.fingerprint,
            )
            for item in items
        ]
        if not payload:
            return 0
        with self.connect() as conn:
            cursor = conn.executemany(
                """
                INSERT OR IGNORE INTO items (
                    source_id, source_name, category, title, url,
                    published_at, summary, fingerprint
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
            return cursor.rowcount if cursor.rowcount != -1 else 0

    def create_run(self, note: str = "") -> int:
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO runs (started_at, note) VALUES (?, ?)",
                (datetime.now(timezone.utc).isoformat(), note),
            )
            return int(cur.lastrowid)

    def finish_run(self, run_id: int, collected_count: int) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE runs SET finished_at = ?, collected_count = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), collected_count, run_id),
            )

    def recent_items(self, days: int = 14, limit: int = 50) -> list[sqlite3.Row]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        with self.connect() as conn:
            cur = conn.execute(
                """
                SELECT * FROM items
                WHERE datetime(replace(substr(published_at, 1, 19), 'T', ' ')) >= datetime(?)
                ORDER BY published_at DESC
                LIMIT ?
                """,
                (cutoff.isoformat(), limit),
            )
            return cur.fetchall()

    def all_items(self, limit: int = 200) -> list[sqlite3.Row]:
        with self.connect() as conn:
            cur = conn.execute(
                "SELECT * FROM items ORDER BY published_at DESC LIMIT ?",
                (limit,),
            )
            return cur.fetchall()
