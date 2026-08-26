"""Retrieval evaluation metrics (Hit@k and MRR)."""

from __future__ import annotations

from typing import Any

from ragkb.retrieval.base import Retriever


async def evaluate_retrieval(
    retriever: Retriever,
    questions: list[dict[str, Any]],
    k: int = 4,
) -> dict[str, float | int]:
    """Evaluate a retriever against ``{question, relevant_sources}`` items.

    A hit is scored when any retrieved chunk's source contains one of the
    ``relevant_sources`` substrings.
    """
    if not questions:
        return {"hit_at_k": 0.0, "mrr": 0.0, "num_questions": 0}
    hits = 0
    reciprocal_ranks: list[float] = []
    for item in questions:
        relevant = [str(value) for value in item.get("relevant_sources", [])]
        results = await retriever.retrieve(str(item["question"]), k=k)
        rank: int | None = None
        for position, result in enumerate(results, start=1):
            source = str(result.chunk.metadata.get("source", ""))
            if any(substring in source for substring in relevant):
                rank = position
                break
        if rank is not None:
            hits += 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)
    return {
        "hit_at_k": hits / len(questions),
        "mrr": sum(reciprocal_ranks) / len(questions),
        "num_questions": len(questions),
    }
