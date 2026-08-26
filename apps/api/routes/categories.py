"""Category management endpoints (internal portal only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from apps.api.deps import require_internal

router = APIRouter(tags=["categories"])


class CreateCategoryRequest(BaseModel):
    name: str
    parent: str | None = None
    description: str = ""


class RenameCategoryRequest(BaseModel):
    new_name: str


@router.get("/categories")
async def list_categories(request: Request, user: dict = Depends(require_internal)) -> dict:
    categories = request.app.state.category_store.list()
    counts: dict[str, int] = {}
    for item in request.app.state.store.list_sources():
        name = str(item.get("category") or "")
        counts[name] = counts.get(name, 0) + int(item["chunks"])
    for entry in categories:
        entry["chunks"] = counts.get(entry["name"], 0)
    return {"categories": categories}


@router.post("/categories")
async def create_category(
    body: CreateCategoryRequest,
    request: Request,
    user: dict = Depends(require_internal),
) -> dict[str, str]:
    store = request.app.state.category_store
    if store.get(body.name) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Category already exists"
        )
    store.create(body.name, body.parent, body.description)
    return {"status": "ok", "name": body.name}


@router.patch("/categories/{name}")
async def rename_category(
    name: str,
    body: RenameCategoryRequest,
    request: Request,
    user: dict = Depends(require_internal),
) -> dict[str, str]:
    if not request.app.state.category_store.rename(name, body.new_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"status": "ok", "name": body.new_name}


@router.delete("/categories/{name}")
async def delete_category(
    name: str,
    request: Request,
    user: dict = Depends(require_internal),
    cascade: bool = True,
) -> dict[str, object]:
    result = request.app.state.category_store.delete(name, cascade=cascade)
    if not result["deleted"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"status": "ok", "name": name, "deleted_chunks": result["chunks"]}
