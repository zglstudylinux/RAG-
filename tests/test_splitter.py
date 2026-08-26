"""Tests for the recursive character splitter."""

from __future__ import annotations

import pytest

from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.core.models import Document


def test_split_respects_chunk_size() -> None:
    splitter = RecursiveCharacterSplitter(chunk_size=50, chunk_overlap=0)
    document = Document(content="word " * 100, metadata={"source": "a.md"})
    chunks = splitter.split_documents([document])
    assert len(chunks) > 1
    assert all(len(chunk.text) <= 50 for chunk in chunks)


def test_chunk_metadata_includes_index_and_page() -> None:
    splitter = RecursiveCharacterSplitter(chunk_size=50, chunk_overlap=0)
    document = Document(content="word " * 100, metadata={"source": "a.md", "page": 3})
    chunks = splitter.split_documents([document])
    assert chunks[0].metadata["page"] == 3
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].metadata["chunk_index"] == 1


def test_chunk_ids_are_deterministic() -> None:
    splitter = RecursiveCharacterSplitter(chunk_size=50, chunk_overlap=0)
    document = Document(content="word " * 100, metadata={"source": "a.md"})
    first = splitter.split_documents([document])
    second = splitter.split_documents([document])
    assert [chunk.id for chunk in first] == [chunk.id for chunk in second]


def test_overlap_must_be_smaller_than_size() -> None:
    with pytest.raises(ValueError):
        RecursiveCharacterSplitter(chunk_size=10, chunk_overlap=10)
