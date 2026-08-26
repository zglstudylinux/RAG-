"""Application wiring: lazily build pipelines once per app instance."""

from __future__ import annotations

from fastapi import FastAPI

from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.config import Settings
from ragkb.core.ingestion import IngestionPipeline
from ragkb.core.rag import RAGPipeline
from ragkb.providers.registry import build_embedding, build_llm


def ensure_services(app: FastAPI) -> None:
    """Build pipelines on first use (so /health works without credentials)."""
    if hasattr(app.state, "rag_pipeline"):
        return
    settings: Settings = app.state.settings
    store = app.state.store
    embedding = build_embedding(settings)
    llm = build_llm(settings)
    splitter = RecursiveCharacterSplitter(settings.chunk_size, settings.chunk_overlap)
    app.state.embedding = embedding
    app.state.llm = llm
    app.state.ingestion_pipeline = IngestionPipeline(embedding, store, splitter)
    app.state.rag_pipeline = RAGPipeline(embedding, store, llm)
