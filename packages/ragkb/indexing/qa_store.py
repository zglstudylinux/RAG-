"""Question & answer log with feedback, FAQ promotion, and similarity search."""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Sequence
from pathlib import Path

import numpy as np


class QAStore:
    """Persists user questions/answers plus feedback and FAQ flags."""

    def __init__(self, path: str = "data/ragkb.sqlite") -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS qa_log ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "question TEXT NOT NULL, answer TEXT NOT NULL, "
            "citations TEXT NOT NULL DEFAULT '[]', "
            "username TEXT NOT NULL DEFAULT '', "
            "customer TEXT NOT NULL DEFAULT '', model TEXT NOT NULL DEFAULT '', "
            "feedback INTEGER, is_faq INTEGER NOT NULL DEFAULT 0, "
            "question_embedding BLOB, "
            "created_at TEXT NOT NULL DEFAULT (datetime('now')))"
        )
        self._conn.commit()

    def record(
        self,
        question: str,
        answer: str,
        citations: list[dict],
        username: str,
        customer: str,
        model: str,
        question_embedding: Sequence[float],
    ) -> int:
        blob = np.asarray(question_embedding, dtype=np.float32).tobytes()
        with self._lock:
            cursor = self._conn.execute(
                "INSERT INTO qa_log "
                "(question, answer, citations, username, customer, model, question_embedding) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    question,
                    answer,
                    json.dumps(citations, ensure_ascii=False),
                    username,
                    customer,
                    model,
                    blob,
                ),
            )
            self._conn.commit()
            return int(cursor.lastrowid)

    def set_feedback(self, qa_id: int, feedback: int) -> None:
        with self._lock:
            self._conn.execute("UPDATE qa_log SET feedback = ? WHERE id = ?", (feedback, qa_id))
            self._conn.commit()

    def promote(self, qa_id: int) -> dict | None:
        """Mark a Q&A as FAQ and return its content plus a first-time flag."""
        with self._lock:
            row = self._conn.execute(
                "SELECT id, question, answer, customer, model, is_faq FROM qa_log WHERE id = ?",
                (qa_id,),
            ).fetchone()
            if row is None:
                return None
            newly_promoted = row[5] != 1
            self._conn.execute("UPDATE qa_log SET is_faq = 1 WHERE id = ?", (qa_id,))
            self._conn.commit()
        return {
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "customer": row[3],
            "model": row[4],
            "newly_promoted": newly_promoted,
        }

    def list_recent(self, limit: int = 20) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, question, answer, username, customer, model, feedback, is_faq, "
                "created_at FROM qa_log ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "username": row[3],
                "customer": row[4],
                "model": row[5],
                "feedback": row[6],
                "is_faq": row[7],
                "created_at": row[8],
            }
            for row in rows
        ]

    def find_similar(
        self, query_embedding: Sequence[float], k: int = 5, customer: str | None = None
    ) -> list[dict]:
        with self._lock:
            if customer:
                rows = self._conn.execute(
                    "SELECT id, question, question_embedding FROM qa_log "
                    "WHERE question_embedding IS NOT NULL AND customer = ?",
                    (customer,),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT id, question, question_embedding FROM qa_log "
                    "WHERE question_embedding IS NOT NULL"
                ).fetchall()
        if not rows:
            return []
        matrix = np.vstack([np.frombuffer(row[2], dtype=np.float32) for row in rows])
        query = np.asarray(query_embedding, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1)
        norms[norms == 0] = 1.0
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            scores = np.zeros(len(rows), dtype=np.float32)
        else:
            scores = (matrix @ query) / (norms * query_norm)
        top = np.argsort(-scores)[:k]
        return [
            {
                "id": rows[int(index)][0],
                "question": rows[int(index)][1],
                "score": float(scores[index]),
            }
            for index in top
        ]

    def close(self) -> None:
        with self._lock:
            self._conn.close()
