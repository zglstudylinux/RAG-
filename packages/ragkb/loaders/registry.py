"""Dispatch file loading by extension."""

from __future__ import annotations

from pathlib import Path

from ragkb.core.models import Document
from ragkb.loaders.base import Loader
from ragkb.loaders.docx import DOCXLoader
from ragkb.loaders.markdown import MarkdownLoader
from ragkb.loaders.pdf import PDFLoader

_LOADERS: dict[str, Loader] = {
    ".md": MarkdownLoader(),
    ".markdown": MarkdownLoader(),
    ".pdf": PDFLoader(),
    ".docx": DOCXLoader(),
}


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
        if file.is_file() and file.suffix.lower() in _LOADERS:
            documents.extend(load_document(file))
    return documents
