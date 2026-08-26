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

    async def ingest_path(self, path: str | Path, *, source: str | None = None) -> int:
        """Ingest a file or directory and return the number of chunks stored.

        When ``source`` is given it overrides the ``source`` metadata (useful when
        ingesting uploaded files whose temporary path is not meaningful).
        """
        target = Path(path)
        if target.is_dir():
            documents = load_directory(target)
        else:
            documents = load_document(target)
        if source is not None:
            for document in documents:
                document.metadata["source"] = source
                document.metadata["title"] = Path(source).stem
        if not documents:
            return 0
        chunks = self._splitter.split_documents(documents)
        if not chunks:
            return 0
        embeddings = await self._embedding.embed_texts([chunk.text for chunk in chunks])
        self._store.add(chunks, embeddings)
        return len(chunks)
