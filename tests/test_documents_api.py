"""API integration tests for document management and auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("RAGKB_LLM_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_EMBEDDING_PROVIDER", "fake")
    monkeypatch.setenv("RAGKB_STORE_PATH", str(tmp_path / "store.sqlite"))
    monkeypatch.setenv("RAGKB_JWT_SECRET", "test-secret-key-for-ragkb-0123456789")
    return TestClient(create_app())


def _login(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_ingest_list_delete_flow(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)
    content = "# GPIO\n\nGPIO pins are used for input and output.\n".encode("utf-8")

    response = client.post(
        "/ingest", files={"file": ("guide.md", content, "text/markdown")}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["chunks"] > 0

    response = client.get("/documents", headers=headers)
    assert response.status_code == 200
    sources = [item["source"] for item in response.json()["documents"]]
    assert "guide.md" in sources

    response = client.delete("/documents/guide.md", headers=headers)
    assert response.status_code == 200

    response = client.get("/documents", headers=headers)
    assert response.json()["documents"] == []


def test_login_with_wrong_password(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    response = client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_documents_require_auth(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    assert client.get("/documents").status_code == 401
