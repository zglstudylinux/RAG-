"""Ingestion pipeline: load -> chunk -> embed -> store."""

from __future__ import annotations

from pathlib import Path

from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.indexing.base import VectorStore
from ragkb.loaders import load_directory, load_document
from ragkb.providers.base import EmbeddingProvider


class IngestionPipeline:
    """Turns files into stored, embedded chunks."""

    def __init__(
        self,
        embedding: EmbeddingProvider,
        store: VectorStore,
        splitter: RecursiveCharacterSplitter | None = None,
    ) -> None:
        self._embedding = embedding
        self._store = store
        self._splitter = splitter or RecursiveCharacterSplitter()

    async def ingest_path(self, path: str | Path) -> int:
        """Ingest a file or directory and return the number of chunks stored."""
        target = Path(path)
        if target.is_dir():
            documents = load_directory(target)
        else:
            documents = load_document(target)
        if not documents:
            return 0
        chunks = self._splitter.split_documents(documents)
        if not chunks:
            return 0
        embeddings = await self._embedding.embed_texts([chunk.text for chunk in chunks])
        self._store.add(chunks, embeddings)
        return len(chunks)
