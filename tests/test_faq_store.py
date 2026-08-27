"""Tests for the curated FAQ store."""

from __future__ import annotations

from ragkb.indexing.faq_store import FaqStore


def _vec(vals) -> list[float]:
    return [float(v) for v in vals]


def test_faq_crud_and_search(tmp_path) -> None:
    store = FaqStore(str(tmp_path / "faq.sqlite"))
    first = store.add(
        "如何配置一个新的串口",
        "1. 使能 UART1\n2. 配置 IO 复用",
        "AB5766C",
        "admin",
        _vec([1.0, 0.0, 0.0]),
    )
    store.add("如何配置 GPIO", "配置为输出", "AB5766C", "admin", _vec([0.0, 1.0, 0.0]))

    assert store.count() == 2
    assert len(store.list()) == 2
    assert len(store.list(category="AB5766C")) == 2
    assert store.list(category="NOPE") == []

    hits = store.search(_vec([1.0, 0.1, 0.0]), k=1)
    assert hits and hits[0]["id"] == first
    assert store.search(_vec([1.0, 0.1, 0.0]), k=5, min_score=1.01) == []

    assert store.update(first, "新问题", "新答案", "", _vec([0.0, 0.0, 1.0]))
    assert store.get(first)["question"] == "新问题"
    assert store.delete(first) is True
    assert store.count() == 1
    assert store.delete(first) is False
