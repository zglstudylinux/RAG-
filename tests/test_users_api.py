"""API integration tests for user management and scoped access."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("RAGKB_LLM_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_EMBEDDING_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_RETRIEVAL_MODE", "vector")
    monkeypatch.setenv("RAGKB_STORE_PATH", str(tmp_path / "store.sqlite"))
    monkeypatch.setenv("RAGKB_JWT_SECRET", "test-secret-key-for-ragkb-0123456789")
    return TestClient(create_app())


def _login(
    client: TestClient, username: str = "admin", password: str = "admin123"
) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_admin_can_manage_users(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)
    response = client.post(
        "/users",
        json={"username": "acme", "password": "pw", "role": "customer",
              "customers": ["acme"], "models": ["x1"]},
        headers=headers,
    )
    assert response.status_code == 200
    response = client.get("/users", headers=headers)
    assert response.status_code == 200
    usernames = [user["username"] for user in response.json()["users"]]
    assert "acme" in usernames


def test_customer_cannot_manage_users(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    admin = _login(client)
    client.post(
        "/users",
        json={"username": "acme", "password": "pw", "role": "customer", "customers": ["acme"]},
        headers=admin,
    )
    customer = _login(client, "acme", "pw")
    assert client.get("/users", headers=customer).status_code == 403


def test_customer_ask_is_scoped(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    admin = _login(client)
    client.post(
        "/ingest",
        files={"file": ("a.md", "# secret A\nacme info\n".encode("utf-8"), "text/markdown")},
        data={"customer": "acme"},
        headers=admin,
    )
    client.post(
        "/ingest",
        files={"file": ("b.md", "# secret B\nglobex info\n".encode("utf-8"), "text/markdown")},
        data={"customer": "globex"},
        headers=admin,
    )
    client.post(
        "/users",
        json={"username": "acme", "password": "pw", "role": "customer", "customers": ["acme"]},
        headers=admin,
    )
    acme = _login(client, "acme", "pw")

    response = client.post("/ask", json={"question": "info"}, headers=acme)
    assert response.status_code == 200
    citations = response.json()["citations"]
    assert citations
    assert all(citation["source"] == "a.md" for citation in citations)
