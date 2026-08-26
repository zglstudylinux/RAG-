"""Markdown loader."""

from __future__ import annotations

from pathlib import Path

from ragkb.core.models import Document
from ragkb.loaders.base import Loader


class MarkdownLoader(Loader):
    """Loads a Markdown file as a single Document (chunking happens later)."""

    def load(self, path: Path) -> list[Document]:
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            return []
        return [
            Document(
                content=content,
                metadata={"source": str(path), "format": "markdown", "title": path.stem},
            )
        ]
