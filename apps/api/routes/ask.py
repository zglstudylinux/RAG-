"""Question answering endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from apps.api.deps import ensure_services
from ragkb.core.rag import RAGPipeline


class AskRequest(BaseModel):
    question: str
    top_k: int = 4


router = APIRouter(tags=["ask"])


@router.post("/ask")
async def ask(request: Request, body: AskRequest) -> dict[str, object]:
    """Answer a question with citations from the knowledge base."""
    ensure_services(request.app)
    pipeline: RAGPipeline = request.app.state.rag_pipeline
    answer = await pipeline.answer(body.question, k=body.top_k)
    return {
        "answer": answer.text,
        "citations": [
            {"source": citation.source, "page": citation.page, "snippet": citation.snippet}
            for citation in answer.citations
        ],
    }
