"""Retriever protocol."""

from __future__ import annotations

from typing import Protocol

from ragkb.core.models import SearchResult


class Retriever(Protocol):
    """Anything that can retrieve chunks for a query."""

    async def retrieve(self, query: str, k: int = 4) -> list[SearchResult]: ...
