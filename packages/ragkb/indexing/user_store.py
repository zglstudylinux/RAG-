"""User storage (roles and ACL become richer in M5)."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from ragkb.auth import hash_password, verify_password


class UserStore:
    """Persists users (username / password hash / role) in SQLite."""

    def __init__(self, path: str = "data/ragkb.sqlite") -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT NOT NULL UNIQUE, "
            "password_hash TEXT NOT NULL, "
            "role TEXT NOT NULL DEFAULT 'admin', "
            "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
        )
        self._conn.commit()

    def ensure_default_user(self, username: str, password: str) -> None:
        """Create the default admin user if no users exist yet."""
        with self._lock:
            exists = self._conn.execute(
                "SELECT COUNT(*) FROM users WHERE username = ?", (username,)
            ).fetchone()[0]
            if not exists:
                self._conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                    (username, hash_password(password)),
                )
                self._conn.commit()

    def authenticate(self, username: str, password: str) -> dict | None:
        """Return {username, role} when credentials are valid, else None."""
        with self._lock:
            row = self._conn.execute(
                "SELECT username, password_hash, role FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None or not verify_password(password, row[1]):
            return None
        return {"username": row[0], "role": row[2]}

    def create_user(self, username: str, password: str, role: str = "admin") -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hash_password(password), role),
            )
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()
