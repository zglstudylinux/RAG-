"""End-to-end RAG pipeline tests (offline)."""

from __future__ import annotations

import asyncio

from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.core.ingestion import IngestionPipeline
from ragkb.core.rag import RAGPipeline, strip_citation_markers
from ragkb.indexing.faq_store import FaqStore
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding, FakeLLM


def _build(tmp_path) -> tuple[RAGPipeline, FakeLLM, SQLiteVectorStore]:
    guide = tmp_path / "guide.md"
    guide.write_text(
        "# GPIO\n\nGPIO pins are used for input and output.\n\n"
        "# UART\n\nUART baud rate is 115200.\n",
        encoding="utf-8",
    )
    store = SQLiteVectorStore(":memory:")
    embedding = FakeEmbedding(dim=128)
    ingestion = IngestionPipeline(
        embedding=embedding,
        store=store,
        splitter=RecursiveCharacterSplitter(chunk_size=50, chunk_overlap=0),
    )
    asyncio.run(ingestion.ingest_path(guide))
    llm = FakeLLM()
    return RAGPipeline(embedding=embedding, store=store, llm=llm), llm, store


def test_answer_returns_top_citation_from_matching_doc(tmp_path) -> None:
    rag, _, _ = _build(tmp_path)
    answer = asyncio.run(rag.answer("How to configure GPIO pins?"))
    assert answer.text == "This is a fake answer."
    assert answer.citations
    assert "GPIO" in answer.citations[0].snippet


def test_answer_empty_store_returns_not_found() -> None:
    store = SQLiteVectorStore(":memory:")
    rag = RAGPipeline(embedding=FakeEmbedding(), store=store, llm=FakeLLM())
    answer = asyncio.run(rag.answer("anything"))
    assert answer.text == "资料中未找到相关内容。"
    assert answer.citations == []


def test_llm_received_context(tmp_path) -> None:
    rag, llm, _ = _build(tmp_path)
    asyncio.run(rag.answer("GPIO pins"))
    user_message = llm.last_messages[-1].content
    assert "GPIO" in user_message
    assert "来源:" in user_message


def test_answer_filters_unreferenced_citations(tmp_path) -> None:
    rag, llm, _ = _build(tmp_path)
    llm._answer = "GPIO pins are for input and output [1]."
    answer = asyncio.run(rag.answer("How to configure GPIO pins?"))
    assert answer.text == "GPIO pins are for input and output [1]."
    assert len(answer.citations) == 1
    assert "GPIO" in answer.citations[0].snippet


def test_answer_renumbers_citations_consistently(tmp_path) -> None:
    rag, llm, _ = _build(tmp_path)
    llm._answer = "UART baud rate is 115200 [2]."
    answer = asyncio.run(rag.answer("GPIO pins"))
    # [2] is the only used citation; it is renumbered to [1] in both text and list
    assert answer.text == "UART baud rate is 115200 [1]."
    assert len(answer.citations) == 1
    assert "UART" in answer.citations[0].snippet


def test_answer_no_markers_keeps_all_citations(tmp_path) -> None:
    rag, llm, _ = _build(tmp_path)
    llm._answer = "This is a fake answer."  # no [n] markers
    answer = asyncio.run(rag.answer("How to configure GPIO pins?"))
    assert answer.citations  # fallback keeps all retrieved candidates


def test_strip_citation_markers() -> None:
    assert strip_citation_markers("abc[1]def") == "abcdef"
    assert strip_citation_markers("a [1][2] b") == "a  b"
    assert strip_citation_markers("no markers") == "no markers"


def test_faq_answer_markers_stripped_in_context(tmp_path) -> None:
    store = SQLiteVectorStore(":memory:")
    embedding = FakeEmbedding(dim=64)
    faq_store = FaqStore(str(tmp_path / "faq.sqlite"))
    faq_store.add("GPIO", "GPIO answer [1].", "", "admin",
                  asyncio.run(embedding.embed_query("GPIO")))
    llm = FakeLLM()
    rag = RAGPipeline(
        embedding=embedding,
        store=store,
        llm=llm,
        faq_store=faq_store,
        faq_threshold=0.5,
        faq_top_k=1,
    )
    asyncio.run(rag.answer("GPIO"))
    context = llm.last_messages[-1].content
    assert "答：GPIO answer ." in context
    assert "GPIO answer [1]" not in context
