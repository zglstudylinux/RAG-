"""Tests for the SQLite vector store."""

from __future__ import annotations

import asyncio

import pytest

from ragkb.core.models import Chunk
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding


def _embed(text: str) -> list[float]:
    return asyncio.run(FakeEmbedding(dim=64).embed_query(text))


def test_add_and_search_returns_nearest() -> None:
    store = SQLiteVectorStore(":memory:")
    chunks = [
        Chunk(id="a", text="GPIO pin configuration", metadata={"source": "a.md"}),
        Chunk(id="b", text="UART baud rate settings", metadata={"source": "b.md"}),
    ]
    store.add(chunks, [_embed(chunk.text) for chunk in chunks])
    assert store.count() == 2
    results = store.search(_embed("GPIO pin"), k=1)
    assert results[0].chunk.id == "a"


def test_search_empty_store_returns_nothing() -> None:
    store = SQLiteVectorStore(":memory:")
    assert store.search(_embed("anything"), k=4) == []


def test_add_mismatched_lengths_raises() -> None:
    store = SQLiteVectorStore(":memory:")
    with pytest.raises(ValueError, match="same length"):
        store.add([Chunk(id="a", text="x")], [])
