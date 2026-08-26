"""Tests for the SQLite user store."""

from __future__ import annotations

from ragkb.indexing.user_store import UserStore


def test_default_user_created_once(tmp_path) -> None:
    store = UserStore(str(tmp_path / "users.sqlite"))
    store.ensure_default_user("admin", "admin123")
    store.ensure_default_user("admin", "admin123")
    assert store.authenticate("admin", "admin123") is not None
    assert store.authenticate("admin", "wrong") is None
    store.close()


def test_create_user_with_role(tmp_path) -> None:
    store = UserStore(str(tmp_path / "users.sqlite"))
    store.create_user("bob", "pw", role="support")
    user = store.authenticate("bob", "pw")
    assert user is not None
    assert user["role"] == "support"
    store.close()
