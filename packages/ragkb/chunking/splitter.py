"""Text splitting into overlapping chunks."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

from ragkb.core.models import Chunk, Document


class RecursiveCharacterSplitter:
    """Splits documents into overlapping chunks on paragraph/newline boundaries."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents: Sequence[Document]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for document in documents:
            source = str(document.metadata.get("source", ""))
            page = document.metadata.get("page", "")
            for index, text in enumerate(self._split_text(document.content)):
                metadata = dict(document.metadata)
                metadata["chunk_index"] = index
                chunks.append(
                    Chunk(
                        id=self._make_id(source, page, index),
                        text=text,
                        metadata=metadata,
                    )
                )
        return chunks

    @staticmethod
    def _make_id(source: str, page: object, index: int) -> str:
        # Include the page number so multi-page documents (each page a Document with the
        # same source) do not collide on chunk_index.
        digest = hashlib.sha1(f"{source}::page{page}::{index}".encode("utf-8")).hexdigest()
        return digest[:16]

    def _split_text(self, text: str) -> list[str]:
        return self._merge(self._paragraphs(text))

    @staticmethod
    def _paragraphs(text: str) -> list[str]:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        blocks: list[str] = []
        for block in normalized.split("\n\n"):
            blocks.extend(block.split("\n"))
        return [block.strip() for block in blocks if block.strip()]

    def _merge(self, paragraphs: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if not current:
                current = paragraph
            elif len(current) + 1 + len(paragraph) <= self.chunk_size:
                current = f"{current}\n{paragraph}"
            else:
                chunks.append(current)
                tail = current[-self.chunk_overlap :] if self.chunk_overlap else ""
                current = f"{tail}\n{paragraph}".strip() if tail else paragraph
        if current:
            chunks.append(current)
        return self._hard_split(chunks)

    def _hard_split(self, chunks: list[str]) -> list[str]:
        result: list[str] = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                result.append(chunk)
                continue
            start = 0
            step = self.chunk_size - self.chunk_overlap or 1
            while start < len(chunk):
                result.append(chunk[start : start + self.chunk_size])
                start += step
        return result
