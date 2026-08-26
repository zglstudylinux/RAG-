"""PDF loader (text extraction; OCR comes in a later milestone)."""

from __future__ import annotations

from pathlib import Path

import pymupdf

from ragkb.core.models import Document
from ragkb.loaders.base import Loader


class PDFLoader(Loader):
    """Extracts one Document per text-bearing page, tagging the page number."""

    def load(self, path: Path) -> list[Document]:
        documents: list[Document] = []
        with pymupdf.open(str(path)) as pdf:
            for page_index in range(pdf.page_count):
                text = pdf[page_index].get_text().strip()
                if not text:
                    continue  # image-only page: skipped for now (OCR in later milestone)
                documents.append(
                    Document(
                        content=text,
                        metadata={
                            "source": str(path),
                            "format": "pdf",
                            "title": path.stem,
                            "page": page_index + 1,  # 1-based page number
                        },
                    )
                )
        return documents
