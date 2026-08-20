"""
Ingestion Service — FastAPI + Celery worker entry point.
Receives PDF uploads and triggers the async ingestion pipeline.
"""
import os
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from celery import Celery

app = FastAPI(title="KIP Ingestion Service", version="1.0.0")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("kip_ingest", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.task_routes = {"tasks.ingest_document.*": {"queue": "ingest"}}


@app.post("/ingest", summary="Submit document for async ingestion")
async def ingest_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    doc_number: str = Form(""),
    doc_type: str = Form("government_order"),
    department: str = Form("Finance Department, Kerala"),
    year: str = Form(""),
    issue_date: str = Form(""),
    is_restricted: str = Form("false"),
    supersedes_id: str = Form(""),
    tags: str = Form("[]"),
    uploaded_by: str = Form("system"),
):
    """
    Accepts a PDF, saves it temporarily, and dispatches a Celery task for:
    1. PDF type detection (scanned vs native)
    2. OCR (if scanned) or text extraction
    3. Semantic chunking
    4. Embedding generation
    5. ChromaDB indexing
    6. PostgreSQL metadata write
    """
    file_bytes = await file.read()
    tmp_path = f"/tmp/{uuid.uuid4()}.pdf"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    task = celery_app.send_task(
        "tasks.ingest_document.run_ingestion",
        kwargs={
            "tmp_path": tmp_path,
            "filename": file.filename,
            "title": title,
            "doc_number": doc_number,
            "doc_type": doc_type,
            "department": department,
            "year": int(year) if year.isdigit() else None,
            "issue_date": issue_date or None,
            "is_restricted": is_restricted.lower() == "true",
            "supersedes_id": supersedes_id or None,
            "tags": tags,
            "uploaded_by": uploaded_by,
        },
    )
    return {
        "message": "Document queued for ingestion",
        "task_id": task.id,
        "filename": file.filename,
        "status": "queued",
    }


@app.get("/task/{task_id}", summary="Check ingestion task status")
async def task_status(task_id: str):
    """Poll for ingestion pipeline completion status."""
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ingestion"}
