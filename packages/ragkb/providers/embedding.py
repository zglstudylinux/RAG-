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
        batch_size: int = 20,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self._model = model
        self._batch_size = max(1, batch_size)
        self._client = client or AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout)

    @property
    def model(self) -> str:
        return self._model

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        texts = list(texts)
        embeddings: list[list[float]] = []
        # Batch requests: some providers cap inputs per request (e.g. DashScope qwen3.7 = 20).
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            response = await self._client.embeddings.create(model=self._model, input=batch)
            data = sorted(response.data, key=lambda item: item.index)
            embeddings.extend(item.embedding for item in data)
        return embeddings
