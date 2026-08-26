"""Tests for scoped (ACL-filtered) retrieval."""

from __future__ import annotations

import asyncio

from ragkb.core.acl import Scope
from ragkb.core.models import Chunk
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding
from ragkb.retrieval.vector import VectorRetriever


def test_scope_filters_vector_results(tmp_path) -> None:
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    embedding = FakeEmbedding(dim=32)
    chunks = [
        Chunk(
            id="a", text="acme confidential data",
            metadata={"source": "a.md", "customer": "acme"},
        ),
        Chunk(
            id="b", text="globex confidential data",
            metadata={"source": "b.md", "customer": "globex"},
        ),
    ]
    embeddings = asyncio.run(embedding.embed_texts([chunk.text for chunk in chunks]))
    store.add(chunks, embeddings)
    retriever = VectorRetriever(embedding, store)

    restricted = asyncio.run(
        retriever.retrieve("confidential data", k=4, scope=Scope(customers=frozenset(["acme"])))
    )
    assert restricted
    assert all(result.chunk.metadata.get("customer") == "acme" for result in restricted)

    unrestricted = asyncio.run(retriever.retrieve("confidential data", k=4))
    assert len(unrestricted) == 2
