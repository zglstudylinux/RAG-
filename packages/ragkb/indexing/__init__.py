"""Vector store adapters and metadata repositories."""

from ragkb.indexing.base import VectorStore
from ragkb.indexing.sqlite_store import SQLiteVectorStore

__all__ = ["SQLiteVectorStore", "VectorStore"]
