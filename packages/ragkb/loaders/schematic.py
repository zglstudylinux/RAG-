"""Schematic (image-heavy PDF) loading via a vision-language model."""

from __future__ import annotations

from pathlib import Path

import pymupdf

from ragkb.core.models import Document
from ragkb.providers.vlm import VLMProvider

SCHEMATIC_PROMPT = (
    "You are an electronics schematic reader. Describe this schematic page in Chinese: "
    "list the main components (part designators such as R1/C1/U1), key net labels, power "
    "rails, interfaces/connectors, and any visible notes. Output a concise structured "
    "summary that can be searched later. Do not invent details that are not visible."
)


class SchematicLoader:
    """Renders each page to an image and asks a VLM to describe it."""

    def __init__(self, vlm: VLMProvider, dpi: int = 120) -> None:
        self._vlm = vlm
        self._dpi = dpi

    async def load(self, path: Path) -> list[Document]:
        documents: list[Document] = []
        with pymupdf.open(str(path)) as pdf:
            for index, page in enumerate(pdf):
                embedded = (page.get_text() or "").strip()
                description = ""
                try:
                    pix = page.get_pixmap(dpi=self._dpi)
                    description = await self._vlm.describe_image(
                        pix.tobytes("png"), "image/png", SCHEMATIC_PROMPT
                    )
                except Exception:
                    description = ""
                text = "\n\n".join(part for part in (description.strip(), embedded) if part)
                if not text:
                    text = "(schematic page with no extractable text)"
                documents.append(
                    Document(
                        content=text,
                        metadata={
                            "source": str(path),
                            "title": Path(path).stem,
                            "kind": "schematic",
                            "page": index + 1,
                        },
                    )
                )
        return documents


def is_schematic_pdf(path: str | Path, min_chars_per_page: int = 80) -> bool:
    """Heuristic: a PDF whose average extracted text per page is tiny is image-heavy."""
    try:
        with pymupdf.open(str(path)) as pdf:
            page_count = len(pdf)
            if page_count == 0:
                return False
            total = sum(len(page.get_text() or "") for page in pdf)
    except Exception:
        return False
    return (total / page_count) < min_chars_per_page
