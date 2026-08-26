"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from apps.api.deps import get_current_user
from ragkb.auth import create_token


class LoginRequest(BaseModel):
    username: str
    password: str


router = APIRouter(tags=["auth"])


@router.post("/auth/login")
async def login(request: Request, body: LoginRequest) -> dict[str, str]:
    user = request.app.state.user_store.authenticate(body.username, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    settings = request.app.state.settings
    token = create_token(
        settings.jwt_secret, user["username"], user["role"], settings.jwt_expires_minutes
    )
    return {"token": token, "username": user["username"], "role": user["role"]}


@router.get("/auth/me")
async def me(user: dict = Depends(get_current_user)) -> dict:
    return user
