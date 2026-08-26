"""Hybrid retrieval: BM25 + vector, fused with Reciprocal Rank Fusion."""

from __future__ import annotations

from ragkb.core.acl import Scope
from ragkb.core.models import Chunk, SearchResult
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.base import EmbeddingProvider
from ragkb.retrieval.bm25 import BM25, tokenize


class HybridRetriever:
    """Fuses lexical (BM25) and semantic (vector) retrieval with RRF."""

    def __init__(
        self,
        embedding: EmbeddingProvider,
        store: SQLiteVectorStore,
        candidate_k: int = 10,
        rrf_k: int = 60,
    ) -> None:
        self._embedding = embedding
        self._store = store
        self._candidate_k = candidate_k
        self._rrf_k = rrf_k
        self._bm25: BM25 | None = None
        self._chunks: list[Chunk] = []
        self._fingerprint = -1

    def _ensure_index(self) -> None:
        """(Re)build the BM25 index when the store's chunk count has changed."""
        count = self._store.count()
        if self._bm25 is None or count != self._fingerprint:
            self._chunks = self._store.all_chunks()
            self._bm25 = BM25([tokenize(chunk.text) for chunk in self._chunks])
            self._fingerprint = count

    async def retrieve(
        self, query: str, k: int = 4, scope: Scope | None = None
    ) -> list[SearchResult]:
        if self._store.count() == 0:
            return []
        self._ensure_index()
        query_embedding = await self._embedding.embed_query(query)
        vector_results = self._store.search(query_embedding, k=self._candidate_k, scope=scope)

        bm25_top = self._candidate_k if scope is None else len(self._chunks)
        bm25_results = self._bm25.search(tokenize(query), top_k=bm25_top)
        if scope is not None:
            bm25_results = [
                item for item in bm25_results if scope.allows(self._chunks[item[0]].metadata)
            ]
        bm25_results = bm25_results[: self._candidate_k]

        vector_rank = {result.chunk.id: rank for rank, result in enumerate(vector_results)}
        bm25_rank = {
            self._chunks[index].id: rank for rank, (index, _score) in enumerate(bm25_results)
        }
        chunks_by_id = {result.chunk.id: result.chunk for result in vector_results}
        for index, _score in bm25_results:
            chunks_by_id.setdefault(self._chunks[index].id, self._chunks[index])

        fused: dict[str, float] = {}
        for chunk_id in set(vector_rank) | set(bm25_rank):
            score = 0.0
            if chunk_id in vector_rank:
                score += 1.0 / (self._rrf_k + vector_rank[chunk_id] + 1)
            if chunk_id in bm25_rank:
                score += 1.0 / (self._rrf_k + bm25_rank[chunk_id] + 1)
            fused[chunk_id] = score
        ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:k]
        return [
            SearchResult(chunk=chunks_by_id[chunk_id], score=score)
            for chunk_id, score in ranked
        ]
