"""Application wiring: lazily build pipelines and resolve the current user."""

from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status

from ragkb.auth import decode_token
from ragkb.chunking.code_splitter import CodeSplitter
from ragkb.chunking.splitter import RecursiveCharacterSplitter
from ragkb.config import Settings
from ragkb.core.errors import ConfigurationError
from ragkb.core.ingestion import IngestionPipeline
from ragkb.core.rag import RAGPipeline
from ragkb.providers.registry import build_embedding, build_llm, build_vlm
from ragkb.retrieval.hybrid import HybridRetriever
from ragkb.retrieval.rerank import NoopReranker
from ragkb.retrieval.vector import VectorRetriever


def ensure_services(app: FastAPI) -> None:
    """Build pipelines on first use (so /health works without credentials)."""
    if hasattr(app.state, "rag_pipeline"):
        return
    settings: Settings = app.state.settings
    store = app.state.store
    embedding = build_embedding(settings)
    llm = build_llm(settings)
    try:
        vlm = build_vlm(settings)
    except ConfigurationError:
        vlm = None  # VLM is optional; schematics fall back to text extraction.
    if settings.retrieval_mode == "hybrid":
        retriever = HybridRetriever(
            embedding, store, settings.hybrid_candidate_k, settings.hybrid_rrf_k
        )
    else:
        retriever = VectorRetriever(embedding, store)
    reranker = NoopReranker()
    splitter = RecursiveCharacterSplitter(settings.chunk_size, settings.chunk_overlap)
    code_splitter = CodeSplitter()
    app.state.embedding = embedding
    app.state.llm = llm
    app.state.vlm = vlm
    app.state.retriever = retriever
    app.state.ingestion_pipeline = IngestionPipeline(
        embedding, store, splitter, code_splitter, vlm
    )
    app.state.rag_pipeline = RAGPipeline(
        embedding,
        store,
        llm,
        retriever,
        reranker,
        faq_store=app.state.faq_store,
        faq_threshold=settings.faq_score_threshold,
        faq_top_k=settings.faq_top_k,
    )


async def get_current_user(
    request: Request, authorization: str | None = Header(default=None)
) -> dict:
    """Resolve the authenticated user (role + ACL) from the bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(request.app.state.settings.jwt_secret, token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = request.app.state.user_store.get_user(payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_internal(user: dict = Depends(get_current_user)) -> dict:
    """Allow only admin/support (internal portal) roles."""
    if user["role"] not in ("admin", "support"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user
