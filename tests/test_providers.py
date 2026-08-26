"""Tests for provider factory functions and message types."""

from __future__ import annotations

import pytest

from ragkb.config import Settings
from ragkb.providers import build_embedding, build_llm
from ragkb.providers.base import Message
from ragkb.providers.embedding import OpenAICompatibleEmbedding
from ragkb.providers.llm import OpenAICompatibleLLM


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
