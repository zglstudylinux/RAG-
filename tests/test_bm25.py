"""Tests for BM25 tokenization and ranking."""

from __future__ import annotations

from ragkb.retrieval.bm25 import BM25, tokenize


def test_tokenize_chinese_and_english() -> None:
    tokens = tokenize("GPIO 引脚初始化")
    assert tokens
    assert "gpio" in tokens


def test_bm25_ranks_matching_doc_first() -> None:
    corpus = [tokenize("GPIO 引脚初始化函数"), tokenize("UART 波特率配置")]
    bm25 = BM25(corpus)
    results = bm25.search(tokenize("GPIO 引脚"), top_k=2)
    assert results
    assert results[0][0] == 0
