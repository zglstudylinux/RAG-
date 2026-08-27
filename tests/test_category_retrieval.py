"""Tests for category-filtered retrieval (vector and hybrid)."""

from __future__ import annotations

import asyncio

from ragkb.core.models import Chunk
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding
from ragkb.retrieval.hybrid import HybridRetriever
from ragkb.retrieval.vector import VectorRetriever


def _store(tmp_path) -> tuple[SQLiteVectorStore, FakeEmbedding]:
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    embedding = FakeEmbedding(dim=32)
    chunks = [
        Chunk(
            id="a", text="GPIO pins control output",
            metadata={"source": "a.md", "category": "AB5766C"},
        ),
        Chunk(
            id="b", text="GPIO pins control output",
            metadata={"source": "b.md", "category": "BT897X"},
        ),
    ]
    embeddings = asyncio.run(embedding.embed_texts([chunk.text for chunk in chunks]))
    store.add(chunks, embeddings)
    return store, embedding


def test_vector_retrieval_filters_by_category(tmp_path) -> None:
    store, embedding = _store(tmp_path)
    results = asyncio.run(
        VectorRetriever(embedding, store).retrieve("GPIO", k=4, category="AB5766C")
    )
    assert results
    assert all(result.chunk.metadata["category"] == "AB5766C" for result in results)


def test_hybrid_retrieval_filters_by_category(tmp_path) -> None:
    store, embedding = _store(tmp_path)
    retriever = HybridRetriever(embedding, store, candidate_k=10)
    restricted = asyncio.run(retriever.retrieve("GPIO", k=4, category="BT897X"))
    assert restricted
    assert all(result.chunk.metadata["category"] == "BT897X" for result in restricted)

    unrestricted = asyncio.run(retriever.retrieve("GPIO", k=4))
    assert len(unrestricted) == 2


def test_category_filter_uses_column_not_metadata(tmp_path) -> None:
    """Backfilled chunks (category column set, metadata JSON lacks the key) still match."""
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    embedding = FakeEmbedding(dim=32)
    chunk = Chunk(id="a", text="GPIO pins control output", metadata={"source": "a.md"})
    embeddings = asyncio.run(embedding.embed_texts([chunk.text]))
    store.add([chunk], embeddings)
    # simulate the one-time backfill: set the category column only
    store._conn.execute("UPDATE chunks SET category = 'AB5766C' WHERE id = 'a'")
    store._conn.commit()

    query = asyncio.run(embedding.embed_query("GPIO"))
    assert len(store.search(query, k=4, category="AB5766C")) == 1
    assert store.search(query, k=4, category="OTHER") == []
    assert store.all_chunks()[0].metadata["category"] == "AB5766C"
