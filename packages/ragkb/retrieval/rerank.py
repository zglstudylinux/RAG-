"""Reranking abstraction (API rerankers plug in later; no-op is the default)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ragkb.core.models import SearchResult


class Reranker(ABC):
    """Reorders (and possibly re-scores) retrieval results for a query."""

    @abstractmethod
    async def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        """Return the re-ranked results."""


class NoopReranker(Reranker):
    """Identity reranker used when no rerank service is configured."""

    async def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        return results
