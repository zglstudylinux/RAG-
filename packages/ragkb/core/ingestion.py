"""Ingestion pipeline: load -> chunk -> embed -> store."""

from __future__ import annotations

from pathlib import Path

from ragkb.chunking.code_splitter import CodeSplitter
from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.core.models import Chunk, Document
from ragkb.indexing.base import VectorStore
from ragkb.loaders.registry import is_supported, load_document
from ragkb.loaders.schematic import SchematicLoader, is_schematic_pdf
from ragkb.providers.base import EmbeddingProvider
from ragkb.providers.vlm import VLMProvider


class IngestionPipeline:
    """Turns files into stored, embedded chunks."""

    def __init__(
        self,
        embedding: EmbeddingProvider,
        store: VectorStore,
        splitter: RecursiveCharacterSplitter | None = None,
        code_splitter: CodeSplitter | None = None,
        vlm: VLMProvider | None = None,
    ) -> None:
        self._embedding = embedding
        self._store = store
        self._splitter = splitter or RecursiveCharacterSplitter()
        self._code_splitter = code_splitter or CodeSplitter()
        self._vlm = vlm

    async def ingest_path(self, path: str | Path, *, source: str | None = None) -> int:
        """Ingest a file or directory and return the number of chunks stored.

        Image-heavy PDFs (schematics) are routed through the VLM when one is configured;
        source files use a structure-aware code splitter.
        """
        target = Path(path)
        files = self._collect_files(target)
        single_file = target.is_file()
        documents: list[Document] = []
        for file_path in files:
            if (
                self._vlm is not None
                and file_path.suffix.lower() == ".pdf"
                and is_schematic_pdf(file_path)
            ):
                docs = await SchematicLoader(self._vlm).load(file_path)
            else:
                docs = load_document(file_path)
            if single_file and source is not None:
                for document in docs:
                    document.metadata["source"] = source
                    document.metadata["title"] = Path(source).stem
            documents.extend(docs)
        if not documents:
            return 0

        chunks: list[Chunk] = []
        for document in documents:
            if document.metadata.get("kind") == "code":
                chunks.extend(self._code_splitter.split_documents([document]))
            else:
                chunks.extend(self._splitter.split_documents([document]))
        if not chunks:
            return 0
        embeddings = await self._embedding.embed_texts([chunk.text for chunk in chunks])
        self._store.add(chunks, embeddings)
        return len(chunks)

    @staticmethod
    def _collect_files(target: Path) -> list[Path]:
        if target.is_file():
            return [target]
        if not target.is_dir():
            raise FileNotFoundError(f"Path not found: {target}")
        return sorted(p for p in target.rglob("*") if p.is_file() and is_supported(p))
