"""
Lineage & Versioning router — track document supersession chains.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from database import get_db
from models.document import Document, DocumentStatus
from models.user import User
from middleware.auth import require_any_role, require_analyst_or_admin

router = APIRouter()
LINEAGE_SERVICE_URL = os.getenv("LINEAGE_SERVICE_URL", "http://lineage-service:8003")


@router.get("/{doc_id}", summary="Get full lineage chain for a document")
async def get_lineage(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_role),
):
    """
    Returns the complete version lineage for a document:
    - Original order
    - All versions (amendments, modifications)
    - Current active/superseded/draft status
    - Which order superseded it (if superseded)
    - Which orders it supersedes
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{LINEAGE_SERVICE_URL}/lineage/{doc_id}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Document not found")
    return resp.json()


@router.post("/{doc_id}/supersede", summary="Mark a document as superseded (Admin/Analyst only)")
async def supersede_document(
    doc_id: str,
    superseded_by_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Mark document `doc_id` as superseded by `superseded_by_id`."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{LINEAGE_SERVICE_URL}/supersede",
            json={"doc_id": doc_id, "superseded_by_id": superseded_by_id, "updated_by": current_user.username},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=resp.text)
    return resp.json()


@router.get("/active/{doc_number}", summary="Get the current active version of a document by number")
async def get_active_version(
    doc_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_role),
):
    """
    Given a GO number (e.g. 'GO_Ms_45'), returns the currently active version.
    Critical for preventing use of superseded orders in file processing.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{LINEAGE_SERVICE_URL}/active/{doc_number}")
    return resp.json()
