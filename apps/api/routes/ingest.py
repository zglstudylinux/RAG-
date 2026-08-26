"""Document ingestion endpoint."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile

from apps.api.deps import ensure_services
from ragkb.core.ingestion import IngestionPipeline

router = APIRouter(tags=["ingest"])


@router.post("/ingest")
async def ingest(request: Request, file: UploadFile = File(...)) -> dict[str, object]:
    """Upload a document and index its chunks."""
    ensure_services(request.app)
    pipeline: IngestionPipeline = request.app.state.ingestion_pipeline
    filename = file.filename or "upload.txt"
    suffix = Path(filename).suffix or ".txt"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        count = await pipeline.ingest_path(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    return {"status": "ok", "filename": filename, "chunks": count}
