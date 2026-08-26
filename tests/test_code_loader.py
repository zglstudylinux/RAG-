"""Tests for the source-code loader and registry dispatch."""

from __future__ import annotations

from ragkb.loaders.code import CodeLoader
from ragkb.loaders.registry import is_supported, load_document


def test_loads_python_file(tmp_path) -> None:
    path = tmp_path / "gpio.py"
    path.write_text("def init():\n    pass\n", encoding="utf-8")
    docs = CodeLoader().load(path)
    assert len(docs) == 1
    assert docs[0].metadata["kind"] == "code"
    assert docs[0].metadata["language"] == "python"
    assert "def init" in docs[0].content


def test_registry_dispatches_code(tmp_path) -> None:
    path = tmp_path / "main.c"
    path.write_text("int main(void) { return 0; }\n", encoding="utf-8")
    assert is_supported(path)
    docs = load_document(path)
    assert docs[0].metadata["kind"] == "code"
    assert docs[0].metadata["language"] == "c"
