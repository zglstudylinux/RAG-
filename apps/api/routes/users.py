"""User management endpoints (admin portal)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from apps.api.deps import require_internal


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "customer"
    customers: list[str] = []
    models: list[str] = []


router = APIRouter(tags=["users"])


@router.get("/users")
async def list_users(request: Request, user: dict = Depends(require_internal)) -> dict:
    return {"users": request.app.state.user_store.list_users()}


@router.post("/users")
async def create_user(
    request: Request,
    body: CreateUserRequest,
    user: dict = Depends(require_internal),
) -> dict[str, str]:
    request.app.state.user_store.create_user(
        body.username, body.password, body.role, body.customers, body.models
    )
    return {"status": "ok", "username": body.username}
