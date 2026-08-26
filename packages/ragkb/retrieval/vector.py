"""Vector-based retriever."""

from __future__ import annotations

from ragkb.core.acl import Scope
from ragkb.core.models import SearchResult
from ragkb.indexing.base import VectorStore
from ragkb.providers.base import EmbeddingProvider


class VectorRetriever:
    """Retrieves chunks by embedding similarity, optionally scoped by ACL."""

    def __init__(self, embedding: EmbeddingProvider, store: VectorStore) -> None:
        self._embedding = embedding
        self._store = store

    async def retrieve(
        self, query: str, k: int = 4, scope: Scope | None = None
    ) -> list[SearchResult]:
        if self._store.count() == 0:
            return []
        query_embedding = await self._embedding.embed_query(query)
        return self._store.search(query_embedding, k=k, scope=scope)
