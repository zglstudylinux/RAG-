"""Tests for retrieval evaluation metrics."""

from __future__ import annotations

import asyncio

from ragkb.core.models import Chunk
from ragkb.eval.metrics import evaluate_retrieval
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding
from ragkb.retrieval.vector import VectorRetriever


def test_evaluate_retrieval(tmp_path) -> None:
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    embedding = FakeEmbedding(dim=32)
    chunks = [
        Chunk(id="1", text="GPIO pin configuration", metadata={"source": "gpio.md"}),
        Chunk(id="2", text="UART baud rate", metadata={"source": "uart.md"}),
    ]
    embeddings = asyncio.run(embedding.embed_texts([chunk.text for chunk in chunks]))
    store.add(chunks, embeddings)
    retriever = VectorRetriever(embedding, store)

    questions = [
        {"question": "GPIO pins", "relevant_sources": ["gpio.md"]},
        {"question": "UART baud", "relevant_sources": ["uart.md"]},
    ]
    metrics = asyncio.run(evaluate_retrieval(retriever, questions, k=2))
    assert metrics["num_questions"] == 2
    assert metrics["hit_at_k"] == 1.0
    assert metrics["mrr"] == 1.0
