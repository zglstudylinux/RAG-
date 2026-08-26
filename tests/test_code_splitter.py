"""Tests for the structure-aware code splitter."""

from __future__ import annotations

import asyncio

from ragkb.chunking.code_splitter import CodeSplitter
from ragkb.core.ingestion import IngestionPipeline
from ragkb.core.models import Document
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding


def test_splits_python_functions() -> None:
    doc = Document(
        content="import os\n\n\ndef foo():\n    return 1\n\n\ndef bar():\n    return 2\n",
        metadata={"source": "a.py", "language": "python", "kind": "code"},
    )
    chunks = CodeSplitter().split_documents([doc])
    assert chunks
    assert all(chunk.metadata["kind"] == "code" for chunk in chunks)
    joined = "\n".join(chunk.text for chunk in chunks)
    assert "def foo" in joined
    assert "def bar" in joined


def test_splits_c_functions() -> None:
    doc = Document(
        content=(
            "#include <stdio.h>\n\n"
            "static void helper(void) {\n    a = 1;\n}\n\n"
            "void init_gpio(void) {\n    gpio = 1;\n}\n\n"
            "int main(void) {\n    init_gpio();\n    return 0;\n}\n"
        ),
        metadata={"source": "a.c", "language": "c", "kind": "code"},
    )
    chunks = CodeSplitter().split_documents([doc])
    assert chunks
    joined = "\n".join(chunk.text for chunk in chunks)
    assert "init_gpio" in joined
    assert "main" in joined


def test_code_ingestion_uses_code_splitter(tmp_path) -> None:
    path = tmp_path / "main.c"
    path.write_text("int main(void) {\n    return 0;\n}\n", encoding="utf-8")
    store = SQLiteVectorStore(str(tmp_path / "store.sqlite"))
    pipeline = IngestionPipeline(FakeEmbedding(dim=16), store)
    count = asyncio.run(pipeline.ingest_path(path))
    assert count >= 1
    assert store.list_sources()[0]["source"] == str(path)
