"""Tests for provider factory functions and message types."""

from __future__ import annotations

import asyncio

import pytest

from ragkb.config import Settings
from ragkb.core.errors import ConfigurationError
from ragkb.providers import build_embedding, build_llm
from ragkb.providers.base import Message
from ragkb.providers.embedding import OpenAICompatibleEmbedding
from ragkb.providers.llm import OpenAICompatibleLLM


class _FakeItem:
    def __init__(self, index: int, embedding: list[float]) -> None:
        self.index = index
        self.embedding = embedding


class _FakeResp:
    def __init__(self, inputs: list[str]) -> None:
        self.data = [
            _FakeItem(i, [float(text[1:])] * 3) for i, text in enumerate(inputs)
        ]


class _FakeEmbeddings:
    def __init__(self, calls: list[list[str]]) -> None:
        self._calls = calls

    async def create(self, model: str, input: list[str]) -> _FakeResp:
        self._calls.append(list(input))
        return _FakeResp(input)


class _FakeClient:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.embeddings = _FakeEmbeddings(self.calls)


def test_build_llm_returns_openai_compatible() -> None:
    settings = Settings(
        _env_file=None,
        llm_provider="openai-compatible",
        llm_api_key="test-key",
    )
    provider = build_llm(settings)
    assert isinstance(provider, OpenAICompatibleLLM)
    assert provider.model == settings.llm_model


def test_build_llm_unknown_provider_raises() -> None:
    settings = Settings(_env_file=None, llm_provider="unknown-provider")
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        build_llm(settings)


def test_build_embedding_returns_openai_compatible() -> None:
    settings = Settings(
        _env_file=None,
        embedding_provider="openai-compatible",
        embedding_api_key="test-key",
    )
    provider = build_embedding(settings)
    assert isinstance(provider, OpenAICompatibleEmbedding)
    assert provider.model == settings.embedding_model


def test_build_embedding_unknown_provider_raises() -> None:
    settings = Settings(_env_file=None, embedding_provider="unknown-provider")
    with pytest.raises(ValueError, match="Unsupported embedding provider"):
        build_embedding(settings)


def test_message_dataclass() -> None:
    message = Message(role="user", content="hello")
    assert message.role == "user"
    assert message.content == "hello"


def test_build_llm_missing_key_raises() -> None:
    settings = Settings(_env_file=None, llm_provider="openai-compatible", llm_api_key="")
    with pytest.raises(ConfigurationError):
        build_llm(settings)


def test_build_embedding_missing_key_raises() -> None:
    settings = Settings(
        _env_file=None, embedding_provider="openai-compatible", embedding_api_key=""
    )
    with pytest.raises(ConfigurationError):
        build_embedding(settings)


def test_embedding_batches_requests() -> None:
    client = _FakeClient()
    provider = OpenAICompatibleEmbedding(
        base_url="x", api_key="k", model="m", batch_size=20, client=client
    )
    texts = [f"t{i}" for i in range(45)]
    embeddings = asyncio.run(provider.embed_texts(texts))
    assert len(embeddings) == 45
    assert [len(c) for c in client.calls] == [20, 20, 5]
    # order preserved across batches
    assert embeddings[0] == [0.0, 0.0, 0.0]
    assert embeddings[44] == [44.0, 44.0, 44.0]
