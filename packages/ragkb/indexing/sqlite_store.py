"""SQLite-backed vector store with brute-force cosine similarity (numpy)."""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Sequence
from pathlib import Path

import numpy as np

from ragkb.core.models import Chunk, SearchResult
from ragkb.indexing.base import VectorStore


class SQLiteVectorStore(VectorStore):
    """Stores chunks and float32 embeddings in a single SQLite file.

    The connection is created with ``check_same_thread=False`` and guarded by a lock so it
    can be shared across the worker threads an async web framework uses.
    """

    def __init__(self, path: str = "data/ragkb.sqlite") -> None:
        self._path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS chunks ("
            "id TEXT PRIMARY KEY, source TEXT NOT NULL, text TEXT NOT NULL, "
            "metadata TEXT NOT NULL, embedding BLOB NOT NULL)"
        )
        self._migrate()
        self._conn.commit()

    def _migrate(self) -> None:
        columns = {row[1] for row in self._conn.execute("PRAGMA table_info(chunks)").fetchall()}
        if "source" not in columns:
            self._conn.execute(
                "ALTER TABLE chunks ADD COLUMN source TEXT NOT NULL DEFAULT ''"
            )
            try:
                self._conn.execute(
                    "UPDATE chunks SET source = COALESCE(json_extract(metadata, '$.source'), '')"
                )
            except sqlite3.OperationalError:
                pass  # json_extract unavailable; leave existing rows empty.

    def add(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            blob = np.asarray(embedding, dtype=np.float32).tobytes()
            rows.append(
                (
                    chunk.id,
                    str(chunk.metadata.get("source", "")),
                    chunk.text,
                    json.dumps(chunk.metadata, ensure_ascii=False),
                    blob,
                )
            )
        with self._lock:
            self._conn.executemany(
                "INSERT OR REPLACE INTO chunks (id, source, text, metadata, embedding) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            self._conn.commit()

    def search(self, query_embedding: Sequence[float], k: int = 4) -> list[SearchResult]:
        if k <= 0:
            return []
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, text, metadata, embedding FROM chunks"
            ).fetchall()
        if not rows:
            return []
        matrix = np.vstack([np.frombuffer(row[3], dtype=np.float32) for row in rows])
        query = np.asarray(query_embedding, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1)
        norms[norms == 0] = 1.0
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            scores = np.zeros(len(rows), dtype=np.float32)
        else:
            scores = (matrix @ query) / (norms * query_norm)
        top_indices = np.argsort(-scores)[:k]
        results: list[SearchResult] = []
        for index in top_indices:
            row = rows[int(index)]
            chunk = Chunk(id=row[0], text=row[1], metadata=json.loads(row[2]))
            results.append(SearchResult(chunk=chunk, score=float(scores[index])))
        return results

    def list_sources(self) -> list[dict[str, object]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT source, COUNT(*) FROM chunks GROUP BY source ORDER BY source"
            ).fetchall()
        return [{"source": row[0], "chunks": row[1]} for row in rows]

    def delete_source(self, source: str) -> int:
        with self._lock:
            cursor = self._conn.execute("DELETE FROM chunks WHERE source = ?", (source,))
            self._conn.commit()
            return cursor.rowcount

    def count(self) -> int:
        with self._lock:
            return int(self._conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])

    def close(self) -> None:
        with self._lock:
            self._conn.close()
