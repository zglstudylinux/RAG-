"""Category storage: chip/project organization with an optional parent hierarchy."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path


class CategoryStore:
    """Persists categories (business domain -> category) and keeps chunk tags in sync.

    A category is a free-form name with an optional ``parent`` (another category name)
    used to build a two-level tree: the parent is the business domain (e.g. ``芯片SDK``,
    ``嵌入式-ESP32``) and the leaf is a chip model or a project (e.g. ``AB5766C``).
    """

    def __init__(self, path: str = "data/ragkb.sqlite") -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS categories ("
            "name TEXT PRIMARY KEY, "
            "parent TEXT, "
            "description TEXT NOT NULL DEFAULT '', "
            "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
        )
        self._conn.commit()

    def list(self) -> list[dict[str, str | None]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT name, parent, description FROM categories ORDER BY parent, name"
            ).fetchall()
        return [
            {"name": row[0], "parent": row[1], "description": row[2]} for row in rows
        ]

    def get(self, name: str) -> dict[str, str | None] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT name, parent, description FROM categories WHERE name = ?", (name,)
            ).fetchone()
        if row is None:
            return None
        return {"name": row[0], "parent": row[1], "description": row[2]}

    def create(self, name: str, parent: str | None = None, description: str = "") -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO categories (name, parent, description) VALUES (?, ?, ?)",
                (name, parent, description),
            )
            self._conn.commit()

    def rename(self, old_name: str, new_name: str) -> bool:
        """Rename a category, re-parenting children and re-tagging chunks atomically."""
        with self._lock:
            exists = self._conn.execute(
                "SELECT 1 FROM categories WHERE name = ?", (old_name,)
            ).fetchone()
            if not exists:
                return False
            self._conn.execute(
                "UPDATE categories SET name = ? WHERE name = ?", (new_name, old_name)
            )
            self._conn.execute(
                "UPDATE categories SET parent = ? WHERE parent = ?", (new_name, old_name)
            )
            self._conn.execute(
                "UPDATE chunks SET category = ? WHERE category = ?", (new_name, old_name)
            )
            self._conn.commit()
        return True

    def delete(self, name: str, cascade: bool = True) -> dict[str, object]:
        """Delete a category; by default also delete its chunks.

        With ``cascade=False`` the chunks are moved to the "uncategorized" bucket
        (empty string) instead. Children are re-parented to the top level.
        """
        with self._lock:
            exists = self._conn.execute(
                "SELECT 1 FROM categories WHERE name = ?", (name,)
            ).fetchone()
            if not exists:
                return {"deleted": False, "chunks": 0}
            chunk_count = self._conn.execute(
                "SELECT COUNT(*) FROM chunks WHERE category = ?", (name,)
            ).fetchone()[0]
            if cascade:
                self._conn.execute("DELETE FROM chunks WHERE category = ?", (name,))
            else:
                self._conn.execute(
                    "UPDATE chunks SET category = '' WHERE category = ?", (name,)
                )
            self._conn.execute(
                "UPDATE categories SET parent = NULL WHERE parent = ?", (name,)
            )
            self._conn.execute("DELETE FROM categories WHERE name = ?", (name,))
            self._conn.commit()
        return {"deleted": True, "chunks": chunk_count}

    def assign(self, source_contains: str, category: str) -> int:
        """Tag uncategorized chunks whose source path contains a substring.

        Used for one-time backfills (e.g. assign every existing 5766 chunk to AB5766C).
        Returns the number of chunks updated.
        """
        with self._lock:
            cursor = self._conn.execute(
                "UPDATE chunks SET category = ? WHERE category = '' AND source LIKE ?",
                (category, f"%{source_contains}%"),
            )
            self._conn.commit()
            return cursor.rowcount

    def close(self) -> None:
        with self._lock:
            self._conn.close()
