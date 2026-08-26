"""Tests for the category store (chip/project organization)."""

from __future__ import annotations

import asyncio
import sqlite3

from ragkb.core.models import Chunk
from ragkb.indexing.category_store import CategoryStore
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding


def _seed_chunks(path: str, categories: list[str]) -> None:
    store = SQLiteVectorStore(path)
    embedding = FakeEmbedding(dim=8)
    chunks = [
        Chunk(id=str(i), text=f"text {i}", metadata={"source": f"s{i}.md", "category": cat})
        for i, cat in enumerate(categories)
    ]
    embeddings = asyncio.run(embedding.embed_texts([chunk.text for chunk in chunks]))
    store.add(chunks, embeddings)
    store.close()


def _sources(path: str, category: str | None = None) -> list[dict]:
    store = SQLiteVectorStore(path)
    try:
        return store.list_sources(category=category)
    finally:
        store.close()


def _count(path: str) -> int:
    store = SQLiteVectorStore(path)
    try:
        return store.count()
    finally:
        store.close()


def test_create_list_rename_delete(tmp_path) -> None:
    path = str(tmp_path / "store.sqlite")
    _seed_chunks(path, ["AB5766C", "AB5766C", "BT897X"])
    store = CategoryStore(path)
    try:
        store.create("芯片SDK", description="芯片 SDK 业务域")
        store.create("AB5766C", parent="芯片SDK")
        store.create("BT897X", parent="芯片SDK")

        assert {c["name"] for c in store.list()} == {"芯片SDK", "AB5766C", "BT897X"}
        assert store.get("AB5766C")["parent"] == "芯片SDK"

        # rename re-tags chunks and re-parents children
        assert store.rename("BT897X", "BT895X")
        assert store.get("BT895X")["parent"] == "芯片SDK"
        assert _sources(path, "BT895X")[0]["category"] == "BT895X"

        # cascade delete removes the category's chunks
        result = store.delete("AB5766C", cascade=True)
        assert result["deleted"] is True
        assert result["chunks"] == 2
        assert _count(path) == 1  # only the BT895X chunk remains

        # non-cascade delete moves chunks to "uncategorized"
        result = store.delete("BT895X", cascade=False)
        assert result["chunks"] == 1
        assert _count(path) == 1
        assert _sources(path)[0]["category"] == ""
    finally:
        store.close()


def test_delete_missing_category(tmp_path) -> None:
    store = CategoryStore(str(tmp_path / "store.sqlite"))
    try:
        assert store.delete("nope") == {"deleted": False, "chunks": 0}
        assert store.rename("nope", "other") is False
    finally:
        store.close()


def test_assign_backfills_uncategorized_chunks(tmp_path) -> None:
    path = str(tmp_path / "store.sqlite")
    _seed_chunks(path, ["", "AB5766C"])
    store = CategoryStore(path)
    try:
        updated = store.assign("s0", "BT897X")
        # only the chunk whose source "s0.md" contains "s0" and is uncategorized moves
        assert updated == 1
        assert _sources(path, "BT897X")[0]["source"] == "s0.md"
        # already-tagged chunks are left alone
        assert _sources(path, "AB5766C")[0]["source"] == "s1.md"
    finally:
        store.close()


def test_category_column_migration(tmp_path) -> None:
    """An existing store without the category column gains it on open."""
    path = str(tmp_path / "old.sqlite")
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE chunks ("
        "id TEXT PRIMARY KEY, source TEXT NOT NULL, text TEXT NOT NULL, "
        "metadata TEXT NOT NULL, embedding BLOB NOT NULL, "
        "customer TEXT NOT NULL DEFAULT '', model TEXT NOT NULL DEFAULT '')"
    )
    conn.commit()
    conn.close()

    store = SQLiteVectorStore(path)
    try:
        columns = {row[1] for row in store._conn.execute("PRAGMA table_info(chunks)").fetchall()}
        assert "category" in columns
    finally:
        store.close()
