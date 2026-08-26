"""Core data models shared across ingestion and retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Document:
    """A parsed document (or a page of one) ready for chunking."""

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Chunk:
    """A chunk of text stored in the vector store."""

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SearchResult:
    """A chunk retrieved from the vector store."""

    chunk: Chunk
    score: float


@dataclass(slots=True)
class Citation:
    """A source citation attached to an answer."""

    source: str
    page: int | None
    snippet: str


@dataclass(slots=True)
class Answer:
    """An answer returned by the RAG pipeline."""

    text: str
    citations: list[Citation] = field(default_factory=list)
