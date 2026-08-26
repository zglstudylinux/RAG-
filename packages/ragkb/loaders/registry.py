"""Dispatch file loading by extension."""

from __future__ import annotations

from pathlib import Path

from ragkb.core.models import Document
from ragkb.loaders.base import Loader
from ragkb.loaders.code import CodeLoader
from ragkb.loaders.docx import DOCXLoader
from ragkb.loaders.markdown import MarkdownLoader
from ragkb.loaders.pdf import PDFLoader

CODE_SUFFIXES = frozenset(
    {
        ".c",
        ".h",
        ".cpp",
        ".cc",
        ".cxx",
        ".hpp",
        ".py",
        ".rs",
        ".go",
        ".js",
        ".ts",
        ".java",
        ".cs",
    }
)

_LOADERS: dict[str, Loader] = {
    ".md": MarkdownLoader(),
    ".markdown": MarkdownLoader(),
    ".pdf": PDFLoader(),
    ".docx": DOCXLoader(),
}
_LOADERS.update({suffix: CodeLoader() for suffix in CODE_SUFFIXES})


def is_supported(path: str | Path) -> bool:
    """Return True if the file extension has a registered loader."""
    return Path(path).suffix.lower() in _LOADERS


def load_document(path: str | Path) -> list[Document]:
    """Load a single file into Documents, dispatching on extension."""
    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(f"File not found: {file}")
    loader = _LOADERS.get(file.suffix.lower())
    if loader is None:
        raise ValueError(f"Unsupported file type: {file.suffix!r}")
    return loader.load(file)


def load_directory(path: str | Path) -> list[Document]:
    """Load all supported files under a directory (recursive)."""
    directory = Path(path)
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    documents: list[Document] = []
    for file in sorted(directory.rglob("*")):
        if file.is_file() and is_supported(file):
            documents.extend(load_document(file))
    return documents
