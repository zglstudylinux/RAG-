"""Tests for schematic detection and VLM-based loading."""

from __future__ import annotations

import asyncio

import pymupdf

from ragkb.core.ingestion import IngestionPipeline
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.loaders.schematic import SchematicLoader, is_schematic_pdf
from ragkb.providers.fake import FakeEmbedding, FakeVLM


def _make_pdf(path, text: str = "", pages: int = 1) -> None:
    pdf = pymupdf.open()
    for _ in range(pages):
        page = pdf.new_page()
        if text:
            page.insert_text((72, 72), text)
    pdf.save(str(path))
    pdf.close()


def test_detects_image_heavy_pdf(tmp_path) -> None:
    path = tmp_path / "schematic.pdf"
    _make_pdf(path, text="", pages=2)
    assert is_schematic_pdf(path)


def test_detects_text_pdf(tmp_path) -> None:
    path = tmp_path / "guide.pdf"
    _make_pdf(path, text="This is a normal text document with plenty of words. " * 20)
    assert not is_schematic_pdf(path)


def test_schematic_loader_uses_vlm(tmp_path) -> None:
    path = tmp_path / "schematic.pdf"
    _make_pdf(path, text="", pages=1)
    vlm = FakeVLM()
    docs = asyncio.run(SchematicLoader(vlm).load(path))
    assert len(docs) == 1
    assert "fake schematic description" in docs[0].content
    assert docs[0].metadata["kind"] == "schematic"
    assert docs[0].metadata["page"] == 1


def test_ingestion_routes_schematic_to_vlm(tmp_path) -> None:
    path = tmp_path / "schematic.pdf"
    _make_pdf(path, text="", pages=1)
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    pipeline = IngestionPipeline(FakeEmbedding(dim=16), store, vlm=FakeVLM())
    count = asyncio.run(pipeline.ingest_path(path))
    assert count >= 1
