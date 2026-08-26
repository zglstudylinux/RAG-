"""Document ingestion endpoint (internal portal only)."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from apps.api.deps import ensure_services, require_internal
from ragkb.core.ingestion import IngestionPipeline
from ragkb.loaders.registry import is_supported

router = APIRouter(tags=["ingest"])


@router.post("/ingest")
async def ingest(
    request: Request,
    file: UploadFile = File(...),
    customer: str | None = Form(default=None),
    model: str | None = Form(default=None),
    category: str | None = Form(default=None),
    user: dict = Depends(require_internal),
) -> dict[str, object]:
    """Upload a document, tag it with customer/model/category, and index its chunks.

    A ``.zip`` archive is extracted and every supported file inside is indexed, tagged
    with the same customer/model/category and sourced as ``archive/relative/path``.
    """
    ensure_services(request.app)
    pipeline: IngestionPipeline = request.app.state.ingestion_pipeline
    filename = file.filename or "upload.txt"
    suffix = Path(filename).suffix or ".txt"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        if suffix.lower() == ".zip":
            count, files = await _ingest_archive(
                pipeline, tmp_path, filename, customer, model, category
            )
            return {
                "status": "ok",
                "filename": filename,
                "customer": customer,
                "model": model,
                "category": category,
                "chunks": count,
                "files": files,
            }
        count = await pipeline.ingest_path(
            tmp_path,
            source=filename,
            customer=customer,
            model=model,
            category=category,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    return {
        "status": "ok",
        "filename": filename,
        "customer": customer,
        "model": model,
        "category": category,
        "chunks": count,
    }


async def _ingest_archive(
    pipeline: IngestionPipeline,
    archive_path: str,
    filename: str,
    customer: str | None,
    model: str | None,
    category: str | None,
) -> tuple[int, int]:
    """Extract a zip and ingest every supported file inside it."""
    with tempfile.TemporaryDirectory() as extract_dir:
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)
        files = [
            p
            for p in sorted(Path(extract_dir).rglob("*"))
            if p.is_file() and is_supported(p)
        ]
        count = 0
        for extracted in files:
            relative = extracted.relative_to(extract_dir).as_posix()
            count += await pipeline.ingest_path(
                extracted,
                source=f"{filename}/{relative}",
                customer=customer,
                model=model,
                category=category,
            )
    return count, len(files)
