"""OpenAI-compatible embedding provider."""

from __future__ import annotations

from collections.abc import Sequence

from openai import AsyncOpenAI

from ragkb.providers.base import EmbeddingProvider


class OpenAICompatibleEmbedding(EmbeddingProvider):
    """Text embeddings against any OpenAI-compatible endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self._model = model
        self._client = client or AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout)

    @property
    def model(self) -> str:
        return self._model

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self._client.embeddings.create(model=self._model, input=list(texts))
        data = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in data]
