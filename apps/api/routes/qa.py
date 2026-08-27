"""Question & answer logging, feedback, and FAQ promotion endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from apps.api.deps import ensure_services, get_current_user, require_internal

router = APIRouter(tags=["qa"])


class FeedbackRequest(BaseModel):
    feedback: int  # 1 = helpful, 0 = not helpful


@router.get("/qa/recent")
async def recent(
    request: Request, limit: int = 20, user: dict = Depends(require_internal)
) -> dict:
    return {"qa": request.app.state.qa_store.list_recent(limit)}


@router.post("/qa/{qa_id}/feedback")
async def feedback(
    qa_id: int,
    request: Request,
    body: FeedbackRequest,
    user: dict = Depends(get_current_user),
) -> dict[str, str]:
    if body.feedback not in (0, 1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="feedback must be 0 or 1"
        )
    request.app.state.qa_store.set_feedback(qa_id, body.feedback)
    return {"status": "ok"}


@router.post("/qa/{qa_id}/promote")
async def promote(
    qa_id: int, request: Request, user: dict = Depends(require_internal)
) -> dict[str, object]:
    """Mark a Q&A as FAQ and add it to the curated FAQ store (idempotent)."""
    ensure_services(request.app)
    record = request.app.state.qa_store.promote(qa_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QA not found")
    if record["newly_promoted"]:
        question_embedding = await request.app.state.embedding.embed_query(record["question"])
        request.app.state.faq_store.add(
            record["question"], record["answer"], "", user["username"], question_embedding
        )
    return {"status": "ok", "qa_id": qa_id}


@router.get("/qa/similar")
async def similar(
    request: Request,
    question: str,
    k: int = 5,
    user: dict = Depends(get_current_user),
) -> dict:
    """Find past questions similar to the given one (scoped to the customer)."""
    ensure_services(request.app)
    query_embedding = await request.app.state.embedding.embed_query(question)
    customer = user["customers"][0] if user["role"] == "customer" and user["customers"] else None
    results = request.app.state.qa_store.find_similar(query_embedding, k=k, customer=customer)
    return {"similar": results}
