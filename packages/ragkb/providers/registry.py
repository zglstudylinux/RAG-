"""Factory functions that build provider instances from Settings."""

from __future__ import annotations

from ragkb.config import Settings
from ragkb.core.errors import ConfigurationError
from ragkb.providers.base import EmbeddingProvider, LLMProvider
from ragkb.providers.embedding import OpenAICompatibleEmbedding
from ragkb.providers.fake import FakeEmbedding, FakeLLM, FakeVLM
from ragkb.providers.llm import OpenAICompatibleLLM
from ragkb.providers.local import LocalEmbedding
from ragkb.providers.vlm import OpenAICompatibleVLM, VLMProvider


def build_llm(settings: Settings) -> LLMProvider:
    """Build the configured LLM provider."""
    if settings.llm_provider == "openai-compatible":
        if not settings.llm_api_key:
            raise ConfigurationError("LLM API key is not configured (set RAGKB_LLM_API_KEY).")
        return OpenAICompatibleLLM(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )
    if settings.llm_provider == "fake":
        return FakeLLM()
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider!r}")


def build_embedding(settings: Settings) -> EmbeddingProvider:
    """Build the configured embedding provider."""
    if settings.embedding_provider == "openai-compatible":
        if not settings.embedding_api_key:
            raise ConfigurationError(
                "Embedding API key is not configured (set RAGKB_EMBEDDING_API_KEY)."
            )
        return OpenAICompatibleEmbedding(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
        )
    if settings.embedding_provider == "local":
        return LocalEmbedding(settings.embedding_model)
    if settings.embedding_provider == "fake":
        return FakeEmbedding()
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider!r}")


def build_vlm(settings: Settings) -> VLMProvider | None:
    """Build the configured VLM provider, or None when it is disabled."""
    if settings.vlm_provider in ("", "none"):
        return None
    if settings.vlm_provider == "fake":
        return FakeVLM()
    if settings.vlm_provider == "openai-compatible":
        if not settings.vlm_api_key:
            raise ConfigurationError("VLM API key is not configured (set RAGKB_VLM_API_KEY).")
        return OpenAICompatibleVLM(
            base_url=settings.vlm_base_url,
            api_key=settings.vlm_api_key,
            model=settings.vlm_model,
        )
    raise ValueError(f"Unsupported VLM provider: {settings.vlm_provider!r}")
