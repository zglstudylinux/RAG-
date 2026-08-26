"""Document management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from apps.api.deps import get_current_user

router = APIRouter(tags=["documents"])


@router.get("/documents")
async def list_documents(request: Request, user: dict = Depends(get_current_user)) -> dict:
    return {"documents": request.app.state.store.list_sources()}


@router.delete("/documents/{source}")
async def delete_document(
    source: str, request: Request, user: dict = Depends(get_current_user)
) -> dict:
    deleted = request.app.state.store.delete_source(source)
    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"deleted_chunks": deleted, "source": source}
