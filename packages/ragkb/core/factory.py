"""Build wired-up services from settings."""

from __future__ import annotations

from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.config import Settings
from ragkb.core.ingestion import IngestionPipeline
from ragkb.core.rag import RAGPipeline
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.registry import build_embedding, build_llm


def build_store(settings: Settings) -> SQLiteVectorStore:
    """Build the vector store (no credentials required)."""
    return SQLiteVectorStore(settings.store_path)


def build_services(
    settings: Settings,
) -> tuple[IngestionPipeline, RAGPipeline, SQLiteVectorStore]:
    """Build a shared store plus ingestion and RAG pipelines."""
    store = build_store(settings)
    embedding = build_embedding(settings)
    llm = build_llm(settings)
    splitter = RecursiveCharacterSplitter(settings.chunk_size, settings.chunk_overlap)
    ingestion = IngestionPipeline(embedding=embedding, store=store, splitter=splitter)
    rag = RAGPipeline(embedding=embedding, store=store, llm=llm)
    return ingestion, rag, store
