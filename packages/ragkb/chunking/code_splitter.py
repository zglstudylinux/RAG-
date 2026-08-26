"""Structure-aware chunking for source code (best-effort, regex-based)."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence

from ragkb.core.models import Chunk, Document

_ANCHOR = re.compile(
    r"^(?:\s*(?:"
    r"(?:async\s+)?def\s|class\s"  # Python
    r"|struct\s|enum\s|union\s|typedef\s|namespace\s"  # C/C++
    r"|#\s*(?:define|include|ifdef|ifndef|if|elif|else|endif|pragma)"
    r"|(?:static|inline|extern|const|volatile)\s+"
    r")|[A-Za-z_][\w\s*]*[\w*]+\s*\([^;]*$)"
)


class CodeSplitter:
    """Splits source code into chunks that keep top-level constructs together."""

    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 100) -> None:
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
                metadata["kind"] = "code"
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
        digest = hashlib.sha1(f"{source}::code::page{page}::{index}".encode("utf-8")).hexdigest()
        return digest[:16]

    def _split_text(self, text: str) -> list[str]:
        return self._merge(self._blocks(text))

    @staticmethod
    def _blocks(text: str) -> list[str]:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")
        blocks: list[str] = []
        current: list[str] = []
        for line in lines:
            if current and _ANCHOR.match(line):
                blocks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current and any(line.strip() for line in current):
            blocks.append("\n".join(current).strip())
        return [block for block in blocks if block.strip()]

    def _merge(self, blocks: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""
        for block in blocks:
            if not current:
                current = block
            elif len(current) + 1 + len(block) <= self.chunk_size:
                current = f"{current}\n{block}"
            else:
                chunks.append(current)
                tail = current[-self.chunk_overlap :] if self.chunk_overlap else ""
                current = f"{tail}\n{block}".strip() if tail else block
        if current:
            chunks.append(current)
        return self._hard_split(chunks)

    def _hard_split(self, chunks: list[str]) -> list[str]:
        result: list[str] = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                result.append(chunk)
                continue
            current = ""
            for line in chunk.split("\n"):
                if current and len(current) + 1 + len(line) > self.chunk_size:
                    result.append(current)
                    current = line
                else:
                    current = f"{current}\n{line}" if current else line
            if current:
                result.append(current)
        return result
