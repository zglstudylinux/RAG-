"""Factory functions that build provider instances from Settings."""

from __future__ import annotations

from ragkb.config import Settings
from ragkb.providers.base import EmbeddingProvider, LLMProvider
from ragkb.providers.embedding import OpenAICompatibleEmbedding
from ragkb.providers.llm import OpenAICompatibleLLM


def build_llm(settings: Settings) -> LLMProvider:
    """Build the configured LLM provider."""
    if settings.llm_provider == "openai-compatible":
        return OpenAICompatibleLLM(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider!r}")


def build_embedding(settings: Settings) -> EmbeddingProvider:
    """Build the configured embedding provider."""
    if settings.embedding_provider == "openai-compatible":
        return OpenAICompatibleEmbedding(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider!r}")
