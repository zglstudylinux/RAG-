"""API integration tests for category management."""

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


def test_category_crud(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)

    assert client.post("/categories", json={"name": "芯片SDK"}, headers=headers).status_code == 200
    assert (
        client.post(
            "/categories", json={"name": "AB5766C", "parent": "芯片SDK"}, headers=headers
        ).status_code
        == 200
    )
    # duplicate name -> 409
    assert client.post("/categories", json={"name": "AB5766C"}, headers=headers).status_code == 409

    names = {c["name"] for c in client.get("/categories", headers=headers).json()["categories"]}
    assert {"芯片SDK", "AB5766C"} <= names

    assert (
        client.patch(
            "/categories/AB5766C", json={"new_name": "AB5766D"}, headers=headers
        ).status_code
        == 200
    )
    names = {c["name"] for c in client.get("/categories", headers=headers).json()["categories"]}
    assert "AB5766D" in names and "AB5766C" not in names

    assert client.delete("/categories/AB5766D", headers=headers).status_code == 200
    names = {c["name"] for c in client.get("/categories", headers=headers).json()["categories"]}
    assert "AB5766D" not in names


def test_ingest_with_category_and_filter(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)
    content = "# GPIO\n\nGPIO pins are used for input and output.\n".encode("utf-8")

    response = client.post(
        "/ingest",
        files={"file": ("guide.md", content, "text/markdown")},
        data={"category": "AB5766C"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["category"] == "AB5766C"

    documents = client.get("/documents", headers=headers).json()["documents"]
    assert documents[0]["category"] == "AB5766C"

    filtered = client.get(
        "/documents", params={"category": "AB5766C"}, headers=headers
    ).json()["documents"]
    assert len(filtered) == 1
    assert client.get("/documents", params={"category": "OTHER"}, headers=headers).json()[
        "documents"
    ] == []


def test_categories_require_auth(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)
    assert client.get("/categories").status_code == 401


def test_full_category_lifecycle(monkeypatch, tmp_path) -> None:
    """Create -> ingest -> ask (category-filtered) -> cascade delete, end to end."""
    client = _client(monkeypatch, tmp_path)
    headers = _login(client)

    client.post("/categories", json={"name": "A"}, headers=headers)
    client.post("/categories", json={"name": "B"}, headers=headers)
    client.post(
        "/ingest",
        files={"file": ("a.md", "# GPIO\n\nGPIO pins are used.\n".encode(), "text/markdown")},
        data={"category": "A"},
        headers=headers,
    )
    client.post(
        "/ingest",
        files={"file": ("b.md", "# UART\n\nUART baud rate is 115200.\n".encode(), "text/markdown")},
        data={"category": "B"},
        headers=headers,
    )

    response = client.post(
        "/ask", json={"question": "GPIO", "category": "A"}, headers=headers
    )
    assert response.status_code == 200
    citations = response.json()["citations"]
    assert citations
    assert all("a.md" in citation["source"] for citation in citations)

    response = client.delete("/categories/A", headers=headers)
    assert response.status_code == 200
    sources = [d["source"] for d in client.get("/documents", headers=headers).json()["documents"]]
    assert "a.md" not in sources
    assert "b.md" in sources
