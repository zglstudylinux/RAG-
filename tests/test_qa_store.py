"""Tests for the Q&A log store."""

from __future__ import annotations

from ragkb.indexing.qa_store import QAStore


def test_record_and_list(tmp_path) -> None:
    store = QAStore(str(tmp_path / "qa.sqlite"))
    qa_id = store.record("how to gpio", "answer", [], "alice", "acme", "", [1.0, 0.0])
    assert qa_id == 1
    rows = store.list_recent()
    assert len(rows) == 1
    assert rows[0]["question"] == "how to gpio"
    store.close()


def test_feedback(tmp_path) -> None:
    store = QAStore(str(tmp_path / "qa.sqlite"))
    qa_id = store.record("q", "a", [], "alice", "", "", [1.0])
    store.set_feedback(qa_id, 1)
    assert store.list_recent()[0]["feedback"] == 1
    store.close()


def test_promote(tmp_path) -> None:
    store = QAStore(str(tmp_path / "qa.sqlite"))
    qa_id = store.record("q", "a", [], "alice", "acme", "x1", [1.0])
    record = store.promote(qa_id)
    assert record["question"] == "q"
    assert record["customer"] == "acme"
    assert store.list_recent()[0]["is_faq"] == 1
    store.close()


def test_find_similar(tmp_path) -> None:
    store = QAStore(str(tmp_path / "qa.sqlite"))
    store.record("gpio init", "a", [], "alice", "acme", "", [1.0, 0.0, 0.0])
    store.record("uart baud", "a", [], "alice", "globex", "", [0.0, 1.0, 0.0])

    results = store.find_similar([1.0, 0.0, 0.0], k=2)
    assert results[0]["id"] == 1

    scoped = store.find_similar([1.0, 0.0, 0.0], k=2, customer="acme")
    assert [item["id"] for item in scoped] == [1]
    store.close()
