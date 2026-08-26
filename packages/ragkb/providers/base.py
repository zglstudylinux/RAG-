"""Provider abstractions (LLM and embedding) that all backends implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass


@dataclass(slots=True)
class Message:
    """A single chat message."""

    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass(slots=True)
class ChatResult:
    """Result of a non-streaming LLM completion."""

    content: str
    raw: object | None = None


class LLMProvider(ABC):
    """Abstraction over chat-completion backends (OpenAI-compatible, etc.)."""

    @abstractmethod
    async def generate(self, messages: Sequence[Message], **kwargs: object) -> ChatResult:
        """Return a single completion for the given conversation."""

    @abstractmethod
    def stream(self, messages: Sequence[Message], **kwargs: object) -> AsyncIterator[str]:
        """Yield completion text chunks."""


class EmbeddingProvider(ABC):
    """Abstraction over text-embedding backends."""

    @abstractmethod
    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a batch of texts, preserving order."""

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query (default: reuse embed_texts)."""
        return (await self.embed_texts([text]))[0]
