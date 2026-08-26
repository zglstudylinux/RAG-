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
