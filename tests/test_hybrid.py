"""Tests for hybrid BM25+vector retrieval."""

from __future__ import annotations

import asyncio

from ragkb.core.models import Chunk
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding
from ragkb.retrieval.hybrid import HybridRetriever


def _populate(store: SQLiteVectorStore) -> FakeEmbedding:
    embedding = FakeEmbedding(dim=32)
    chunks = [
        Chunk(id="1", text="GPIO 引脚初始化配置方法", metadata={"source": "gpio.md"}),
        Chunk(id="2", text="UART 波特率设置说明", metadata={"source": "uart.md"}),
        Chunk(id="3", text="I2C 总线读写流程", metadata={"source": "i2c.md"}),
    ]
    embeddings = asyncio.run(embedding.embed_texts([chunk.text for chunk in chunks]))
    store.add(chunks, embeddings)
    return embedding


def test_hybrid_retrieves_results(tmp_path) -> None:
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    embedding = _populate(store)
    retriever = HybridRetriever(embedding, store)
    results = asyncio.run(retriever.retrieve("GPIO 引脚", k=2))
    assert results
    assert len(results) <= 2


def test_hybrid_rebuilds_after_ingest(tmp_path) -> None:
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    embedding = _populate(store)
    retriever = HybridRetriever(embedding, store)
    asyncio.run(retriever.retrieve("GPIO", k=2))

    chunk = Chunk(id="4", text="ADC 采样", metadata={"source": "adc.md"})
    store.add([chunk], asyncio.run(embedding.embed_texts(["ADC 采样"])))

    results = asyncio.run(retriever.retrieve("ADC", k=1))
    assert results
    assert results[0].chunk.id == "4"
