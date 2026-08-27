"""Curated FAQ endpoints: create / list / update / delete standard Q&A pairs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from apps.api.deps import ensure_services, require_internal
from ragkb.core.rag import strip_citation_markers

router = APIRouter(tags=["faqs"])


class FaqCreate(BaseModel):
    question: str
    answer: str
    category: str = ""


class FaqUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    category: str | None = None


@router.get("/faqs")
async def list_faqs(
    request: Request,
    category: str | None = None,
    user: dict = Depends(require_internal),
) -> dict:
    return {"faqs": request.app.state.faq_store.list(category)}


@router.post("/faqs")
async def create_faq(
    request: Request,
    body: FaqCreate,
    user: dict = Depends(require_internal),
) -> dict[str, object]:
    ensure_services(request.app)
    question_embedding = await request.app.state.embedding.embed_query(body.question)
    faq_id = request.app.state.faq_store.add(
        body.question,
        strip_citation_markers(body.answer),
        body.category,
        user["username"],
        question_embedding,
    )
    return {"status": "ok", "id": faq_id}


@router.patch("/faqs/{faq_id}")
async def update_faq(
    faq_id: int,
    request: Request,
    body: FaqUpdate,
    user: dict = Depends(require_internal),
) -> dict[str, str]:
    ensure_services(request.app)
    existing = request.app.state.faq_store.get(faq_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    question = body.question if body.question is not None else existing["question"]
    answer = strip_citation_markers(
        body.answer if body.answer is not None else existing["answer"]
    )
    category = body.category if body.category is not None else existing["category"]
    question_embedding = await request.app.state.embedding.embed_query(question)
    if not request.app.state.faq_store.update(
        faq_id, question, answer, category, question_embedding
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return {"status": "ok"}


@router.delete("/faqs/{faq_id}")
async def delete_faq(
    faq_id: int,
    request: Request,
    user: dict = Depends(require_internal),
) -> dict[str, str]:
    if not request.app.state.faq_store.delete(faq_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return {"status": "ok"}
