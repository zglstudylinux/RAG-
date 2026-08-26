"""Tests for the deterministic fake providers."""

from __future__ import annotations

import asyncio

from ragkb.providers.base import Message
from ragkb.providers.fake import FakeEmbedding, FakeLLM


def test_fake_embedding_is_deterministic() -> None:
    embedding = FakeEmbedding(dim=64)
    first = asyncio.run(embedding.embed_texts(["GPIO pin configuration"]))
    second = asyncio.run(embedding.embed_texts(["GPIO pin configuration"]))
    assert first == second


def test_fake_embedding_related_texts_are_closer() -> None:
    embedding = FakeEmbedding(dim=128)
    vectors = asyncio.run(
        embedding.embed_texts(
            ["GPIO pin configuration", "GPIO pins and clock", "recipe for cake"]
        )
    )

    def cosine(first: list[float], second: list[float]) -> float:
        return sum(x * y for x, y in zip(first, second))

    assert cosine(vectors[0], vectors[1]) > cosine(vectors[0], vectors[2])


def test_fake_llm_records_messages() -> None:
    llm = FakeLLM(answer="canned")
    result = asyncio.run(llm.generate([Message(role="system", content="sys")]))
    assert result.content == "canned"
    assert llm.last_messages[0].role == "system"
    assert llm.last_messages[0].content == "sys"
