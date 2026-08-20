"""
Documents router — upload, list, retrieve, delete.
"""
import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import httpx

from database import get_db
from models.document import Document, DocumentType, DocumentStatus
from models.user import User
from middleware.auth import require_any_role, require_analyst_or_admin, require_admin

router = APIRouter()

INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://ingestion-service:8001")
MINIO_URL = os.getenv("MINIO_URL", "minio:9000")


@router.post("/upload", summary="Upload a new document for ingestion")
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    title: str = Form(...),
    doc_number: str = Form(None),
    doc_type: DocumentType = Form(DocumentType.GOVERNMENT_ORDER),
    department: str = Form("Finance Department, Kerala"),
    year: int = Form(None),
    issue_date: str = Form(None),
    is_restricted: bool = Form(False),
    supersedes_id: str = Form(None),
    tags: str = Form("[]"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Upload a PDF document (scanned or native). Triggers async OCR → chunking → embedding pipeline.
    Only Admin can upload restricted documents.
    """
    # Restriction check
    if is_restricted and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload restricted documents")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    file_bytes = await file.read()

    # Forward to ingestion service
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{INGESTION_SERVICE_URL}/ingest",
            files={"file": (file.filename, file_bytes, "application/pdf")},
            data={
                "title": title,
                "doc_number": doc_number or "",
                "doc_type": doc_type.value,
                "department": department,
                "year": str(year) if year else "",
                "issue_date": issue_date or "",
                "is_restricted": str(is_restricted).lower(),
                "supersedes_id": supersedes_id or "",
                "tags": tags,
                "uploaded_by": current_user.username,
            },
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Ingestion service error: {resp.text}")

    return resp.json()


@router.get("/", summary="List all documents")
async def list_documents(
    doc_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    year: Optional[int] = None,
    is_restricted: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_role),
):
    """List documents with optional filters. Viewers and non-admins cannot see restricted documents."""
    query = select(Document)

    # Non-admins cannot see restricted documents
    if current_user.role != "admin":
        query = query.where(Document.is_restricted == False)  # noqa: E712
    elif is_restricted is not None:
        query = query.where(Document.is_restricted == is_restricted)

    if doc_type:
        query = query.where(Document.doc_type == doc_type)
    if status:
        query = query.where(Document.status == status)
    if year:
        query = query.where(Document.year == year)
    if search:
        query = query.where(Document.title.ilike(f"%{search}%"))

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset(skip).limit(limit).order_by(Document.created_at.desc())
    result = await db.execute(query)
    docs = result.scalars().all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "documents": [d.to_dict() for d in docs],
    }


@router.get("/{doc_id}", summary="Get document details")
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_role),
):
    """Get full metadata for a single document."""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.is_restricted and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: restricted document")
    return doc.to_dict()


@router.delete("/{doc_id}", summary="Delete a document (Admin only)")
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Hard-delete a document. Admin only."""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()
    return {"message": f"Document {doc_id} deleted successfully"}
