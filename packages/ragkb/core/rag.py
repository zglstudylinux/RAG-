"""RAG query pipeline: retrieve -> rerank -> prompt -> generate, with citations."""

from __future__ import annotations

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

    async def answer(self, question: str, k: int = 4) -> Answer:
        results = await self._retriever.retrieve(question, k=k)
        results = await self._reranker.rerank(question, results)
        if not results:
            return Answer(text="资料中未找到相关内容。", citations=[])
        context, citations = self._format_context(results)
        messages = [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=f"资料片段：\n\n{context}\n\n问题：{question}"),
        ]
        result = await self._llm.generate(messages)
        return Answer(text=result.content, citations=citations)

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
