"""Deduplication utilities backed by SQLite."""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from .models import Publication

DATA_DIR = Path.home() / ".publication_scout"
DB_PATH = DATA_DIR / "seen.sqlite"


SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doi TEXT,
    title TEXT NOT NULL,
    year TEXT,
    url_hash TEXT,
    UNIQUE(doi),
    UNIQUE(title, year),
    UNIQUE(url_hash)
);
"""


class Deduplicator:
    """Deduplicate publications using DOI, (title, year) and URL hash."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(SCHEMA)
            conn.commit()

    def _hash_url(self, url: str | None) -> Optional[str]:
        if not url:
            return None
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def is_seen(self, publication: Publication) -> bool:
        url_hash = self._hash_url(publication.url)
        query = """
        SELECT 1 FROM seen
        WHERE (doi IS NOT NULL AND doi = ?)
           OR (title = ? AND year IS ?)
           OR (url_hash IS NOT NULL AND url_hash = ?)
        LIMIT 1;
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                query,
                (
                    publication.doi,
                    publication.title,
                    publication.year,
                    url_hash,
                ),
            )
            return cursor.fetchone() is not None

    def mark_seen(self, publications: Iterable[Publication]) -> None:
        insert = """
        INSERT OR IGNORE INTO seen (doi, title, year, url_hash)
        VALUES (?, ?, ?, ?);
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                insert,
                [
                    (
                        publication.doi,
                        publication.title,
                        publication.year,
                        self._hash_url(publication.url),
                    )
                    for publication in publications
                ],
            )
            conn.commit()
