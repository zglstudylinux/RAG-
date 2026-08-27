"""Curated FAQ store: question -> standard answer, matched by embedding similarity."""

from __future__ import annotations

import sqlite3
import threading
from collections.abc import Sequence
from pathlib import Path

import numpy as np


class FaqStore:
    """Persists curated question/answer pairs and matches them by question similarity.

    Unlike the raw document chunks, FAQ entries are human-written standard answers.
    They are stored separately (own table, own embeddings) so retrieval can give them
    priority over raw docs when a question is a close match.
    """

    def __init__(self, path: str = "data/ragkb.sqlite") -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS faqs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "question TEXT NOT NULL, answer TEXT NOT NULL, "
            "category TEXT NOT NULL DEFAULT '', "
            "created_by TEXT NOT NULL DEFAULT '', "
            "created_at TEXT NOT NULL DEFAULT (datetime('now')), "
            "question_embedding BLOB NOT NULL)"
        )
        self._conn.commit()

    def add(
        self,
        question: str,
        answer: str,
        category: str,
        created_by: str,
        question_embedding: Sequence[float],
    ) -> int:
        blob = np.asarray(question_embedding, dtype=np.float32).tobytes()
        with self._lock:
            cursor = self._conn.execute(
                "INSERT INTO faqs (question, answer, category, created_by, question_embedding) "
                "VALUES (?, ?, ?, ?, ?)",
                (question, answer, category, created_by, blob),
            )
            self._conn.commit()
            return int(cursor.lastrowid)

    def update(
        self,
        faq_id: int,
        question: str,
        answer: str,
        category: str,
        question_embedding: Sequence[float],
    ) -> bool:
        blob = np.asarray(question_embedding, dtype=np.float32).tobytes()
        with self._lock:
            cursor = self._conn.execute(
                "UPDATE faqs SET question = ?, answer = ?, category = ?, question_embedding = ? "
                "WHERE id = ?",
                (question, answer, category, blob, faq_id),
            )
            self._conn.commit()
            return cursor.rowcount > 0

    def delete(self, faq_id: int) -> bool:
        with self._lock:
            cursor = self._conn.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
            self._conn.commit()
            return cursor.rowcount > 0

    def get(self, faq_id: int) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT id, question, answer, category, created_by, created_at "
                "FROM faqs WHERE id = ?",
                (faq_id,),
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def list(self, category: str | None = None) -> list[dict]:
        with self._lock:
            if category is not None:
                rows = self._conn.execute(
                    "SELECT id, question, answer, category, created_by, created_at "
                    "FROM faqs WHERE category = ? ORDER BY id DESC",
                    (category,),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT id, question, answer, category, created_by, created_at "
                    "FROM faqs ORDER BY id DESC"
                ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def search(
        self,
        query_embedding: Sequence[float],
        k: int = 3,
        category: str | None = None,
        min_score: float = 0.0,
    ) -> list[dict]:
        """Return the top-k FAQs whose question matches ``query_embedding``."""
        with self._lock:
            if category is not None:
                rows = self._conn.execute(
                    "SELECT id, question, answer, category, question_embedding "
                    "FROM faqs WHERE category = ?",
                    (category,),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT id, question, answer, category, question_embedding FROM faqs"
                ).fetchall()
        if not rows:
            return []
        matrix = np.vstack([np.frombuffer(row[4], dtype=np.float32) for row in rows])
        query = np.asarray(query_embedding, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1)
        norms[norms == 0] = 1.0
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            scores = np.zeros(len(rows), dtype=np.float32)
        else:
            scores = (matrix @ query) / (norms * query_norm)
        top_indices = np.argsort(-scores)[:k]
        results: list[dict] = []
        for index in top_indices:
            score = float(scores[index])
            if score < min_score:
                continue
            row = rows[int(index)]
            results.append(
                {
                    "id": row[0],
                    "question": row[1],
                    "answer": row[2],
                    "category": row[3],
                    "score": score,
                }
            )
        return results

    def count(self) -> int:
        with self._lock:
            return int(self._conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0])

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "category": row[3],
            "created_by": row[4],
            "created_at": row[5],
        }

    def close(self) -> None:
        with self._lock:
            self._conn.close()
