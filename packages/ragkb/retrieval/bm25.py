"""Okapi BM25 lexical retrieval with Chinese/English tokenization."""

from __future__ import annotations

import math
import re
from collections import defaultdict

_TOKEN_CHARS = re.compile(r"[\w\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words (jieba for Chinese, word-level for ASCII)."""
    import jieba  # lazy: the slow dictionary build happens on first cut, not on import

    tokens: list[str] = []
    for token in jieba.cut(text):
        token = token.strip().lower()
        if token and _TOKEN_CHARS.search(token):
            tokens.append(token)
    return tokens


class BM25:
    """In-memory Okapi BM25 index over tokenized documents."""

    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._n = len(corpus)
        self._doc_len = [len(doc) for doc in corpus]
        self._avgdl = sum(self._doc_len) / self._n if self._n else 0.0
        self._freqs: list[dict[str, int]] = []
        self._df: dict[str, int] = defaultdict(int)
        self._idf: dict[str, float] = {}
        self._build(corpus)

    def _build(self, corpus: list[list[str]]) -> None:
        for doc in corpus:
            freqs: dict[str, int] = defaultdict(int)
            for token in doc:
                freqs[token] += 1
            self._freqs.append(freqs)
            for token in freqs:
                self._df[token] += 1
        for token, df in self._df.items():
            self._idf[token] = math.log((self._n - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query_tokens: list[str], top_k: int = 10) -> list[tuple[int, float]]:
        """Return the top-k ``(document_index, score)`` tuples."""
        if self._n == 0 or not query_tokens:
            return []
        scores: list[tuple[int, float]] = []
        for index in range(self._n):
            length = self._doc_len[index] or 1
            freqs = self._freqs[index]
            score = 0.0
            for token in query_tokens:
                tf = freqs.get(token)
                if tf:
                    idf = self._idf.get(token, 0.0)
                    denominator = tf + self._k1 * (
                        1 - self._b + self._b * length / self._avgdl
                    )
                    score += idf * tf * (self._k1 + 1) / denominator
            scores.append((index, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]
