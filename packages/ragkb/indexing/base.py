"""Vector store abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ragkb.core.models import Chunk, SearchResult


class VectorStore(ABC):
    """Interface for storing chunks and searching by embedding similarity."""

    @abstractmethod
    def add(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        """Add chunks with their embeddings."""

    @abstractmethod
    def search(self, query_embedding: Sequence[float], k: int = 4) -> list[SearchResult]:
        """Return the k most similar chunks."""

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored chunks."""

    @abstractmethod
    def all_chunks(self) -> list[Chunk]:
        """Return every stored chunk (for building lexical indexes)."""
