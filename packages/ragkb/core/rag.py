"""RAG query pipeline: retrieve -> rerank -> prompt -> generate, with citations."""

from __future__ import annotations

import re

from ragkb.core.acl import Scope
from ragkb.core.models import Answer, Citation, SearchResult
from ragkb.indexing.base import VectorStore
from ragkb.providers.base import EmbeddingProvider, LLMProvider, Message
from ragkb.retrieval.base import Retriever
from ragkb.retrieval.rerank import NoopReranker, Reranker
from ragkb.retrieval.vector import VectorRetriever

SYSTEM_PROMPT = (
    "你是芯片原厂技术资料助手。请只依据提供的资料片段回答问题，"
    "并在回答中用 [1]、[2] 等编号标注引用来源。"
    "如果资料中包含“FAQ 标准答案”，请优先直接采用该标准答案。"
    "如果资料中没有相关信息，请回答“资料中未找到相关内容”，不要编造。"
)

_CITATION_REF = re.compile(r"\[(\d+)\]")


def strip_citation_markers(text: str) -> str:
    """Remove ``[n]`` citation markers from an answer.

    FAQ answers are stored verbatim from a prior LLM generation, which included
    ``[n]`` markers referring to that generation's chunk order. When the FAQ is later
    prepended to a fresh context with a different order, those stale markers corrupt
    the citations, so they are stripped before storing/serving the FAQ.
    """
    return _CITATION_REF.sub("", text)


class RAGPipeline:
    """Answers questions by retrieving chunks and generating a cited answer."""

    def __init__(
        self,
        embedding: EmbeddingProvider,
        store: VectorStore,
        llm: LLMProvider,
        retriever: Retriever | None = None,
        reranker: Reranker | None = None,
        *,
        faq_store: object | None = None,
        faq_threshold: float = 0.70,
        faq_top_k: int = 2,
    ) -> None:
        self._retriever = retriever or VectorRetriever(embedding, store)
        self._reranker = reranker or NoopReranker()
        self._llm = llm
        self._embedding = embedding
        self._faq_store = faq_store
        self._faq_threshold = faq_threshold
        self._faq_top_k = faq_top_k

    async def answer(
        self,
        question: str,
        k: int = 4,
        scope: Scope | None = None,
        category: str | None = None,
    ) -> Answer:
        results = await self._retriever.retrieve(question, k=k, scope=scope, category=category)
        results = await self._reranker.rerank(question, results)
        faqs = await self._search_faqs(question, category)
        if not results and not faqs:
            return Answer(text="资料中未找到相关内容。", citations=[])
        context, citations = self._format_context(results, faqs)
        messages = [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=f"资料片段：\n\n{context}\n\n问题：{question}"),
        ]
        result = await self._llm.generate(messages)
        text, filtered = self._filter_citations(result.content, citations)
        faq_hits = [{"id": faq["id"], "question": faq["question"]} for faq in faqs]
        return Answer(text=text, citations=filtered, faq_hits=faq_hits)

    async def _search_faqs(self, question: str, category: str | None) -> list[dict]:
        """Find curated FAQ entries whose question closely matches ``question``."""
        if self._faq_store is None:
            return []
        query_embedding = await self._embedding.embed_query(question)
        return self._faq_store.search(  # type: ignore[attr-defined]
            query_embedding,
            k=self._faq_top_k,
            category=category,
            min_score=self._faq_threshold,
        )

    @staticmethod
    def _filter_citations(
        text: str | None, citations: list[Citation]
    ) -> tuple[str | None, list[Citation]]:
        """Keep only the citations the answer referenced via [n], renumbering both.

        The LLM is asked to cite sources with [1], [2], ...; retrieved-but-unused
        candidates are dropped so the "引用来源" list matches what the answer relies
        on. The [n] markers in the text are rewritten to stay consistent with the
        filtered list. If the LLM cited nothing, everything is returned unchanged.
        """
        if not citations:
            return text, citations
        used: set[int] = set()
        for match in _CITATION_REF.finditer(text or ""):
            index = int(match.group(1))
            if 1 <= index <= len(citations):
                used.add(index)
        if not used:
            return text, citations
        used_sorted = sorted(used)
        remap = {old: new for new, old in enumerate(used_sorted, start=1)}

        def _rewrite(match: re.Match[str]) -> str:
            index = int(match.group(1))
            return f"[{remap[index]}]" if index in remap else match.group(0)

        new_text = _CITATION_REF.sub(_rewrite, text or "")
        new_citations = [citations[index - 1] for index in used_sorted]
        return new_text, new_citations

    @staticmethod
    def _format_context(
        results: list[SearchResult], faqs: list[dict]
    ) -> tuple[str, list[Citation]]:
        parts: list[str] = []
        citations: list[Citation] = []
        for index, faq in enumerate(faqs, start=1):
            answer = strip_citation_markers(str(faq["answer"]))
            parts.append(f"[{index}] FAQ 标准答案\n问：{faq['question']}\n答：{answer}")
            citations.append(Citation(source="FAQ 沉淀", page=None, snippet=answer[:200]))
        for index, result in enumerate(results, start=len(faqs) + 1):
            metadata = result.chunk.metadata
            source = str(metadata.get("source", "unknown"))
            page = metadata.get("page")
            page_number = int(page) if page is not None else None
            header = f"[{index}] 来源: {source}"
            if page_number is not None:
                header += f" 页码: {page_number}"
            parts.append(f"{header}\n{result.chunk.text}")
            citations.append(
                Citation(source=source, page=page_number, snippet=result.chunk.text[:200])
            )
        return "\n\n".join(parts), citations
