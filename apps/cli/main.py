"""Command-line interface: ingest documents and ask questions."""

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

    args = parser.parse_args(argv)
    return asyncio.run(_run(args))


async def _run(args: argparse.Namespace) -> int:
    # Imported lazily so `--help` stays fast and does not load numpy/pymupdf.
    from ragkb.config import get_settings
    from ragkb.core.factory import build_services

    settings = get_settings()
    ingestion, rag, store = build_services(settings)
    try:
        if args.command == "ingest":
            count = await ingestion.ingest_path(args.path)
            print(f"Ingested {count} chunks.")
        else:
            top_k = args.top_k or settings.retrieval_top_k
            answer = await rag.answer(args.question, k=top_k)
            print(answer.text)
            for index, citation in enumerate(answer.citations, start=1):
                page = f" p.{citation.page}" if citation.page else ""
                print(f"[{index}] {citation.source}{page}")
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
