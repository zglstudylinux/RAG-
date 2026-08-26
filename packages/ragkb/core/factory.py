"""Build wired-up services from settings."""

from __future__ import annotations

from dataclasses import dataclass

from ragkb.chunking.code_splitter import CodeSplitter
from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.config import Settings
from ragkb.core.ingestion import IngestionPipeline
from ragkb.core.rag import RAGPipeline
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.base import EmbeddingProvider
from ragkb.providers.registry import build_embedding, build_llm, build_vlm
from ragkb.retrieval.base import Retriever
from ragkb.retrieval.hybrid import HybridRetriever
from ragkb.retrieval.rerank import NoopReranker, Reranker
from ragkb.retrieval.vector import VectorRetriever


def build_store(settings: Settings) -> SQLiteVectorStore:
    """Build the vector store (no credentials required)."""
    return SQLiteVectorStore(settings.store_path)


def build_retriever(
    settings: Settings, embedding: EmbeddingProvider, store: SQLiteVectorStore
) -> Retriever:
    """Build the configured retriever (hybrid BM25+vector by default)."""
    if settings.retrieval_mode == "hybrid":
        return HybridRetriever(
            embedding,
            store,
            candidate_k=settings.hybrid_candidate_k,
            rrf_k=settings.hybrid_rrf_k,
        )
    return VectorRetriever(embedding, store)


def build_reranker(settings: Settings) -> Reranker:
    """Build the configured reranker (no-op until an API reranker is added)."""
    if settings.rerank_provider == "none":
        return NoopReranker()
    raise ValueError(f"Unsupported rerank provider: {settings.rerank_provider!r}")


@dataclass
class Services:
    """Wired-up ingestion + retrieval + RAG services sharing one store."""

    ingestion: IngestionPipeline
    rag: RAGPipeline
    store: SQLiteVectorStore
    retriever: Retriever
    embedding: EmbeddingProvider


def build_services(settings: Settings) -> Services:
    """Build a shared store plus ingestion and RAG pipelines."""
    store = build_store(settings)
    embedding = build_embedding(settings)
    llm = build_llm(settings)
    vlm = build_vlm(settings)
    retriever = build_retriever(settings, embedding, store)
    reranker = build_reranker(settings)
    splitter = RecursiveCharacterSplitter(settings.chunk_size, settings.chunk_overlap)
    code_splitter = CodeSplitter()
    ingestion = IngestionPipeline(embedding, store, splitter, code_splitter, vlm)
    rag = RAGPipeline(embedding, store, llm, retriever, reranker)
    return Services(
        ingestion=ingestion, rag=rag, store=store, retriever=retriever, embedding=embedding
    )
