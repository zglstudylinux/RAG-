"""End-to-end ingestion tests (offline, using the fake embedding provider)."""

from __future__ import annotations

import asyncio

from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.core.ingestion import IngestionPipeline
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding


def test_ingest_markdown_into_store(tmp_path) -> None:
    path = tmp_path / "guide.md"
    path.write_text(
        "# GPIO\n\nGPIO pins are used for input and output.\n\n"
        "# UART\n\nUART baud rate is 115200.\n",
        encoding="utf-8",
    )

    store = SQLiteVectorStore(":memory:")
    pipeline = IngestionPipeline(
        embedding=FakeEmbedding(dim=64),
        store=store,
        splitter=RecursiveCharacterSplitter(chunk_size=200, chunk_overlap=0),
    )
    count = asyncio.run(pipeline.ingest_path(path))
    assert count == store.count()
    assert count > 0


def test_ingest_tags_category(tmp_path) -> None:
    path = tmp_path / "guide.md"
    path.write_text(
        "# GPIO\n\nGPIO pins are used for input and output.\n", encoding="utf-8"
    )

    store = SQLiteVectorStore(":memory:")
    pipeline = IngestionPipeline(
        embedding=FakeEmbedding(dim=64),
        store=store,
        splitter=RecursiveCharacterSplitter(chunk_size=200, chunk_overlap=0),
    )
    count = asyncio.run(pipeline.ingest_path(path, category="AB5766C"))
    assert count > 0
    assert all(chunk.metadata.get("category") == "AB5766C" for chunk in store.all_chunks())


def test_ingest_derives_folder_from_directory(tmp_path) -> None:
    root = tmp_path / "chip"
    (root / "sdk").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)
    (root / "sdk" / "bsp.md").write_text("# BSP\n\nUART baud config.\n", encoding="utf-8")
    (root / "docs" / "gpio.md").write_text("# GPIO\n\nGPIO pins for IO.\n", encoding="utf-8")

    store = SQLiteVectorStore(":memory:")
    pipeline = IngestionPipeline(
        embedding=FakeEmbedding(dim=64),
        store=store,
        splitter=RecursiveCharacterSplitter(chunk_size=200, chunk_overlap=0),
    )
    count = asyncio.run(pipeline.ingest_path(root))
    assert count > 0
    folders = {
        chunk.metadata["source"]: chunk.metadata.get("folder") for chunk in store.all_chunks()
    }
    assert set(folders.values()) == {"sdk", "docs"}
