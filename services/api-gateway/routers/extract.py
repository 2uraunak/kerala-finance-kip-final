"""
Clause & Figure Extraction router.
Extracts structured clauses, financial figures, tables, and key dates from documents.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
import httpx

from models.user import User
from middleware.auth import require_analyst_or_admin

router = APIRouter()
EXTRACTION_SERVICE_URL = os.getenv("EXTRACTION_SERVICE_URL", "http://extraction-service:8004")


@router.post("/clauses/{doc_id}", summary="Extract clauses from a document")
async def extract_clauses(
    doc_id: str,
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Uses LLM to extract structured clauses from a document.
    Returns JSON with clause number, text, type (operative/recital/definition), and page reference.
    Includes source review label: document title, GO number, page, confidence score.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{EXTRACTION_SERVICE_URL}/extract/clauses/{doc_id}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Document not found")
    return resp.json()


@router.post("/figures/{doc_id}", summary="Extract financial figures and tables from a document")
async def extract_figures(
    doc_id: str,
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Extracts monetary amounts, percentages, budget allocations, GST rates, and dates.
    Returns structured JSON with source page reference and confidence score.
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{EXTRACTION_SERVICE_URL}/extract/figures/{doc_id}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Document not found")
    return resp.json()


@router.post("/full/{doc_id}", summary="Full extraction: clauses + figures + dates + entities")
async def full_extraction(
    doc_id: str,
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Complete structured extraction: clauses, financial figures, key dates,
    named entities (officers, positions), and referenced GO numbers.
    """
    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(f"{EXTRACTION_SERVICE_URL}/extract/full/{doc_id}")
    return resp.json()


@router.get("/tables/{doc_id}", summary="Extract all tables from a document")
async def extract_tables(
    doc_id: str,
    current_user: User = Depends(require_analyst_or_admin),
):
    """Returns all tables detected in the document as structured JSON arrays."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(f"{EXTRACTION_SERVICE_URL}/extract/tables/{doc_id}")
    return resp.json()
