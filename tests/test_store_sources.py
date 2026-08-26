"""Tests for source listing/deletion in the vector store."""

from __future__ import annotations

import asyncio

from ragkb.core.models import Chunk
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding


def test_list_and_delete_sources(tmp_path) -> None:
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    embedding = FakeEmbedding(dim=8)
    chunks = [
        Chunk(id="a", text="one", metadata={"source": "a.md"}),
        Chunk(id="b", text="two", metadata={"source": "b.md"}),
    ]
    embeddings = asyncio.run(embedding.embed_texts(["one", "two"]))
    store.add(chunks, embeddings)

    sources = store.list_sources()
    assert {item["source"] for item in sources} == {"a.md", "b.md"}

    assert store.delete_source("a.md") == 1
    assert store.count() == 1
    assert {item["source"] for item in store.list_sources()} == {"b.md"}


def test_delete_missing_source_returns_zero(tmp_path) -> None:
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    assert store.delete_source("nope.md") == 0
