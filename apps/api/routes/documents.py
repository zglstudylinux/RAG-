"""Document management endpoints (internal portal only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from apps.api.deps import require_internal

router = APIRouter(tags=["documents"])


@router.get("/documents")
async def list_documents(request: Request, user: dict = Depends(require_internal)) -> dict:
    return {"documents": request.app.state.store.list_sources()}


@router.delete("/documents/{source}")
async def delete_document(
    source: str, request: Request, user: dict = Depends(require_internal)
) -> dict:
    deleted = request.app.state.store.delete_source(source)
    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"deleted_chunks": deleted, "source": source}
