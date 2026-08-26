"""Tests for the CLI list/delete commands."""

from __future__ import annotations

import asyncio

from apps.cli import main as cli
from ragkb.config import Settings
from ragkb.core.models import Chunk
from ragkb.indexing.sqlite_store import SQLiteVectorStore
from ragkb.providers.fake import FakeEmbedding


def _seed(tmp_path) -> str:
    path = str(tmp_path / "store.sqlite")
    store = SQLiteVectorStore(path)
    embedding = FakeEmbedding(dim=8)
    chunks = [
        Chunk(id="a", text="one", metadata={"source": "a.md"}),
        Chunk(id="b", text="two", metadata={"source": "b.md"}),
    ]
    embeddings = asyncio.run(embedding.embed_texts(["one", "two"]))
    store.add(chunks, embeddings)
    store.close()
    return path


def _patch(monkeypatch, path: str) -> None:
    monkeypatch.setattr(
        "ragkb.config.get_settings",
        lambda: Settings(_env_file=None, store_path=path),
    )


def test_cli_list(tmp_path, monkeypatch, capsys) -> None:
    _patch(monkeypatch, _seed(tmp_path))
    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "a.md" in out
    assert "b.md" in out


def test_cli_delete_exact(tmp_path, monkeypatch, capsys) -> None:
    _patch(monkeypatch, _seed(tmp_path))
    assert cli.main(["delete", "a.md"]) == 0
    assert "Deleted 1 chunks" in capsys.readouterr().out
    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "a.md" not in out
    assert "b.md" in out


def test_cli_delete_substring(tmp_path, monkeypatch, capsys) -> None:
    _patch(monkeypatch, _seed(tmp_path))
    assert cli.main(["delete", "b"]) == 0  # "b" uniquely matches b.md
    assert "Deleted 1 chunks: b.md" in capsys.readouterr().out


def test_cli_delete_missing(tmp_path, monkeypatch, capsys) -> None:
    _patch(monkeypatch, _seed(tmp_path))
    assert cli.main(["delete", "does-not-exist"]) == 1
    assert "No source matched" in capsys.readouterr().err
