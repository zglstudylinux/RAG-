"""Source-code loader (many languages; chunked by CodeSplitter later)."""

from __future__ import annotations

from pathlib import Path

from ragkb.core.models import Document
from ragkb.loaders.base import Loader

_LANGUAGE_BY_SUFFIX = {
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".py": "python",
    ".rs": "rust",
    ".go": "go",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cs": "csharp",
}


class CodeLoader(Loader):
    """Loads a source file as a single Document tagged with its language."""

    def load(self, path: Path) -> list[Document]:
        text = path.read_text(encoding="utf-8", errors="replace")
        language = _LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "text")
        return [
            Document(
                content=text,
                metadata={
                    "source": str(path),
                    "title": path.stem,
                    "kind": "code",
                    "language": language,
                },
            )
        ]
