"""Local, offline embedding via sentence-transformers (CPU)."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from ragkb.core.errors import ConfigurationError
from ragkb.providers.base import EmbeddingProvider


class LocalEmbedding(EmbeddingProvider):
    """Embed texts with a local sentence-transformers model (e.g. ``BAAI/bge-base-zh-v1.5``).

    The heavy ``sentence_transformers`` import is deferred until first use so the rest of the
    package stays importable without the optional ``[local]`` extra installed. Encoding runs
    in a worker thread so the async event loop is never blocked by the CPU-bound model.
    """

    def __init__(self, model: str, *, encoder: object | None = None) -> None:
        self._model_name = model
        self._encoder = encoder  # injectable for tests; lazily loaded otherwise

    @property
    def model(self) -> str:
        return self._model_name

    def _load(self) -> object:
        if self._encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise ConfigurationError(
                    "sentence-transformers is not installed; run: pip install -e '.[local]'"
                ) from exc
            self._encoder = SentenceTransformer(self._model_name)
        return self._encoder

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        encoder = self._load()
        matrix = await asyncio.to_thread(encoder.encode, list(texts))
        return [vector.astype("float32").tolist() for vector in matrix]
