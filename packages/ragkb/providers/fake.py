"""Deterministic in-process providers for tests and offline development."""

from __future__ import annotations

import hashlib
import math
from collections.abc import AsyncIterator, Sequence

from ragkb.providers.base import ChatResult, EmbeddingProvider, LLMProvider, Message
from ragkb.providers.vlm import VLMProvider


class FakeEmbedding(EmbeddingProvider):
    """Deterministic hashing vectorizer (character bigrams).

    Language-agnostic and offline: texts sharing character bigrams get higher cosine
    similarity, which is enough to exercise the ingestion/retrieval pipeline in tests.
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for token in self._tokens(text):
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            vector[int(digest, 16) % self.dim] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm > 0:
            vector = [value / norm for value in vector]
        return vector

    @staticmethod
    def _tokens(text: str) -> list[str]:
        cleaned = "".join(char.lower() for char in text if not char.isspace())
        bigrams = [cleaned[i : i + 2] for i in range(len(cleaned) - 1)]
        return bigrams or [cleaned]


class FakeLLM(LLMProvider):
    """Returns a canned answer and records the messages it was asked with."""

    def __init__(self, answer: str = "This is a fake answer.") -> None:
        self._answer = answer
        self.last_messages: list[Message] = []

    async def generate(self, messages: Sequence[Message], **kwargs: object) -> ChatResult:
        self.last_messages = list(messages)
        return ChatResult(content=self._answer)

    async def stream(self, messages: Sequence[Message], **kwargs: object) -> AsyncIterator[str]:
        self.last_messages = list(messages)
        yield self._answer


class FakeVLM(VLMProvider):
    """Returns a deterministic description and records its calls."""

    def __init__(self, description: str = "fake schematic description") -> None:
        self._description = description
        self.calls: list[tuple[str, str]] = []

    async def describe_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        self.calls.append((mime_type, prompt))
        return self._description
