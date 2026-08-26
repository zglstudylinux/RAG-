"""Question answering endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from apps.api.deps import ensure_services, get_current_user
from ragkb.core.acl import build_scope
from ragkb.core.rag import RAGPipeline


class AskRequest(BaseModel):
    question: str
    top_k: int = 4
    category: str | None = None


router = APIRouter(tags=["ask"])


@router.post("/ask")
async def ask(
    request: Request,
    body: AskRequest,
    user: dict = Depends(get_current_user),
) -> dict[str, object]:
    """Answer a question with citations, restricted to the user's ACL scope."""
    ensure_services(request.app)
    pipeline: RAGPipeline = request.app.state.rag_pipeline
    scope = build_scope(user["role"], user["customers"], user["models"])
    answer = await pipeline.answer(
        body.question, k=body.top_k, scope=scope, category=body.category
    )
    citations = [
        {"source": citation.source, "page": citation.page, "snippet": citation.snippet}
        for citation in answer.citations
    ]

    # Log the Q&A for feedback / FAQ curation / similar-question lookup.
    question_embedding = await request.app.state.embedding.embed_query(body.question)
    customer = user["customers"][0] if user["role"] == "customer" and user["customers"] else ""
    model = user["models"][0] if user["role"] == "customer" and user["models"] else ""
    request.app.state.qa_store.record(
        body.question, answer.text, citations, user["username"], customer, model,
        question_embedding,
    )

    return {"answer": answer.text, "citations": citations}
