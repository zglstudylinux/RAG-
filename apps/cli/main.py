"""Command-line interface: ingest documents, ask questions, and evaluate retrieval."""

from __future__ import annotations

import argparse
import asyncio
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ragkb", description="ragkb command line")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Ingest a file or directory")
    ingest.add_argument("path", help="file or directory to ingest")

    ask = subparsers.add_parser("ask", help="Ask a question against the knowledge base")
    ask.add_argument("question", help="the question to ask")
    ask.add_argument("-k", "--top-k", type=int, default=None, help="chunks to retrieve")

    evaluate = subparsers.add_parser("eval", help="Evaluate retrieval against a JSON eval set")
    evaluate.add_argument(
        "eval_file",
        help='JSON file: {"questions": [{"question": str, "relevant_sources": [str]}]}',
    )
    evaluate.add_argument("-k", "--top-k", type=int, default=None, help="chunks to retrieve")

    args = parser.parse_args(argv)
    return asyncio.run(_run(args))


async def _run(args: argparse.Namespace) -> int:
    # Imported lazily so `--help` stays fast and does not load numpy/pymupdf/jieba.
    import json
    from pathlib import Path

    from ragkb.config import get_settings
    from ragkb.core.factory import build_services
    from ragkb.eval.metrics import evaluate_retrieval

    settings = get_settings()
    services = build_services(settings)
    try:
        if args.command == "ingest":
            count = await services.ingestion.ingest_path(args.path)
            print(f"Ingested {count} chunks.")
        elif args.command == "ask":
            top_k = args.top_k or settings.retrieval_top_k
            answer = await services.rag.answer(args.question, k=top_k)
            print(answer.text)
            for index, citation in enumerate(answer.citations, start=1):
                page = f" p.{citation.page}" if citation.page else ""
                print(f"[{index}] {citation.source}{page}")
        else:  # eval
            data = json.loads(Path(args.eval_file).read_text(encoding="utf-8"))
            questions = data.get("questions", [])
            top_k = args.top_k or settings.retrieval_top_k
            metrics = await evaluate_retrieval(services.retriever, questions, k=top_k)
            print(f"num_questions: {metrics['num_questions']}")
            print(f"hit@{top_k}: {metrics['hit_at_k']:.3f}")
            print(f"mrr: {metrics['mrr']:.3f}")
    finally:
        services.store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
