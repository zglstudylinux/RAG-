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
    "如果资料中没有相关信息，请回答“资料中未找到相关内容”，不要编造。"
)

_CITATION_REF = re.compile(r"\[(\d+)\]")


class RAGPipeline:
    """Answers questions by retrieving chunks and generating a cited answer."""

    def __init__(
        self,
        embedding: EmbeddingProvider,
        store: VectorStore,
        llm: LLMProvider,
        retriever: Retriever | None = None,
        reranker: Reranker | None = None,
    ) -> None:
        self._retriever = retriever or VectorRetriever(embedding, store)
        self._reranker = reranker or NoopReranker()
        self._llm = llm

    async def answer(
        self,
        question: str,
        k: int = 4,
        scope: Scope | None = None,
        category: str | None = None,
    ) -> Answer:
        results = await self._retriever.retrieve(question, k=k, scope=scope, category=category)
        results = await self._reranker.rerank(question, results)
        if not results:
            return Answer(text="资料中未找到相关内容。", citations=[])
        context, citations = self._format_context(results)
        messages = [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=f"资料片段：\n\n{context}\n\n问题：{question}"),
        ]
        result = await self._llm.generate(messages)
        text, filtered = self._filter_citations(result.content, citations)
        return Answer(text=text, citations=filtered)

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
    def _format_context(results: list[SearchResult]) -> tuple[str, list[Citation]]:
        parts: list[str] = []
        citations: list[Citation] = []
        for index, result in enumerate(results, start=1):
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
