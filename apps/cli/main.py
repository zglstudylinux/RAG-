"""Command-line interface: ingest, ask, evaluate, back up, list, and delete."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ragkb.indexing.sqlite_store import SQLiteVectorStore


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

    backup = subparsers.add_parser("backup", help="Back up the SQLite store file")
    backup.add_argument("dest", help="destination file or directory")

    subparsers.add_parser("list", help="List ingested sources and their chunk counts")

    delete = subparsers.add_parser("delete", help="Delete an ingested source from the store")
    delete.add_argument(
        "source",
        help="exact source path, or a substring that uniquely matches one source",
    )

    args = parser.parse_args(argv)
    return asyncio.run(_run(args))


async def _run(args: argparse.Namespace) -> int:
    # Imported lazily so `--help` stays fast and does not load numpy/pymupdf/jieba.
    from ragkb.config import get_settings

    settings = get_settings()

    if args.command == "backup":
        from ragkb.core.backup import backup_store

        target = backup_store(settings.store_path, args.dest)
        print(f"Backed up {settings.store_path} -> {target}")
        return 0

    if args.command in ("list", "delete"):
        from ragkb.indexing.sqlite_store import SQLiteVectorStore

        store = SQLiteVectorStore(settings.store_path)
        try:
            if args.command == "list":
                sources = store.list_sources()
                if not sources:
                    print("(store is empty)")
                for item in sources:
                    tags = [t for t in (item["customer"], item["model"]) if t]
                    suffix = f"  [{', '.join(tags)}]" if tags else ""
                    print(f"{item['chunks']:>5} | {item['source']}{suffix}")
                return 0

            target = _resolve_source(store, args.source)
            if target is None:
                return 1
            deleted = store.delete_source(target)
            print(f"Deleted {deleted} chunks: {target}")
            return 0
        finally:
            store.close()

    import json
    from pathlib import Path

    from ragkb.core.factory import build_services
    from ragkb.eval.metrics import evaluate_retrieval

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


def _resolve_source(store: SQLiteVectorStore, needle: str) -> str | None:
    """Resolve a user-supplied source string to an exact stored source path.

    Accepts an exact path, or a substring that uniquely matches one source
    (case-insensitive). Prints guidance and returns None when it cannot resolve.
    """
    sources = [item["source"] for item in store.list_sources()]
    if needle in sources:
        return needle
    matches = [s for s in sources if needle.lower() in s.lower()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        print(f"No source matched: {needle}", file=sys.stderr)
    else:
        print(
            f"Ambiguous: {len(matches)} sources match {needle!r}; be more specific:",
            file=sys.stderr,
        )
        for source in matches:
            print(f"  - {source}", file=sys.stderr)
    return None


if __name__ == "__main__":
    sys.exit(main())
