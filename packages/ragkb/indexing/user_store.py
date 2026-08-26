"""User storage: roles plus customer/model scope (ACL)."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from ragkb.auth import hash_password, verify_password


class UserStore:
    """Persists users with a role and optional customer/model ACL."""

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
            "customers TEXT NOT NULL DEFAULT '[]', "
            "models TEXT NOT NULL DEFAULT '[]', "
            "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
        )
        self._migrate()
        self._conn.commit()

    def _migrate(self) -> None:
        columns = {row[1] for row in self._conn.execute("PRAGMA table_info(users)").fetchall()}
        for column in ("customers", "models"):
            if column not in columns:
                self._conn.execute(
                    f"ALTER TABLE users ADD COLUMN {column} TEXT NOT NULL DEFAULT '[]'"
                )

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
        """Return the user record when credentials are valid, else None."""
        with self._lock:
            row = self._conn.execute(
                "SELECT username, password_hash, role, customers, models "
                "FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None or not verify_password(password, row[1]):
            return None
        return self._record(row[0], row[2], row[3], row[4])

    def get_user(self, username: str) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT username, role, customers, models FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None:
            return None
        return self._record(row[0], row[1], row[2], row[3])

    def create_user(
        self,
        username: str,
        password: str,
        role: str = "admin",
        customers: list[str] | None = None,
        models: list[str] | None = None,
    ) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO users (username, password_hash, role, customers, models) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    username,
                    hash_password(password),
                    role,
                    json.dumps(customers or [], ensure_ascii=False),
                    json.dumps(models or [], ensure_ascii=False),
                ),
            )
            self._conn.commit()

    def list_users(self) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT username, role, customers, models FROM users ORDER BY username"
            ).fetchall()
        return [self._record(row[0], row[1], row[2], row[3]) for row in rows]

    @staticmethod
    def _record(username: str, role: str, customers: str, models: str) -> dict:
        return {
            "username": username,
            "role": role,
            "customers": json.loads(customers or "[]"),
            "models": json.loads(models or "[]"),
        }

    def close(self) -> None:
        with self._lock:
            self._conn.close()
