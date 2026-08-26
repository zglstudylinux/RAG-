"""Tests for the local sentence-transformers embedding provider."""

from __future__ import annotations

import asyncio

import numpy as np

from ragkb.config import Settings
from ragkb.providers.local import LocalEmbedding
from ragkb.providers.registry import build_embedding


class _StubEncoder:
    """Fake sentence-transformers model that returns deterministic vectors."""

    def __init__(self) -> None:
        self.calls = 0

    def encode(self, texts, *args, **kwargs):
        self.calls += 1
        return np.array([[float(len(text))] * 4 for text in texts], dtype=np.float32)


def test_local_embedding_wiring() -> None:
    encoder = _StubEncoder()
    provider = LocalEmbedding("stub", encoder=encoder)
    vectors = asyncio.run(provider.embed_texts(["ab", "abc", "abcd"]))
    assert vectors == [[2.0, 2.0, 2.0, 2.0], [3.0, 3.0, 3.0, 3.0], [4.0, 4.0, 4.0, 4.0]]
    assert encoder.calls == 1


def test_local_embedding_empty() -> None:
    provider = LocalEmbedding("stub", encoder=_StubEncoder())
    assert asyncio.run(provider.embed_texts([])) == []


def test_build_embedding_local() -> None:
    settings = Settings(embedding_provider="local", embedding_model="BAAI/bge-base-zh-v1.5")
    provider = build_embedding(settings)
    assert isinstance(provider, LocalEmbedding)
    assert provider.model == "BAAI/bge-base-zh-v1.5"
