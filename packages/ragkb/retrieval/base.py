"""Retriever protocol."""

from __future__ import annotations

from typing import Protocol

from ragkb.core.acl import Scope
from ragkb.core.models import SearchResult


class Retriever(Protocol):
    """Anything that can retrieve chunks for a query, optionally scoped."""

    async def retrieve(
        self,
        query: str,
        k: int = 4,
        scope: Scope | None = None,
        category: str | None = None,
    ) -> list[SearchResult]: ...
