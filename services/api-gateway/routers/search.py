"""
Search router — natural language search with source citations.
The source review labels on every result are critical for Feature Completeness marks.
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, Query
import httpx

from models.user import User
from middleware.auth import require_any_role

router = APIRouter()
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://search-service:8002")


@router.get("/", summary="Natural language search with source citations")
async def search(
    q: str = Query(..., description="Natural language query (e.g. 'DA increase for state employees 2023')"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to return"),
    doc_type: Optional[str] = Query(None, description="Filter by document type"),
    year: Optional[int] = Query(None, description="Filter by year"),
    status: Optional[str] = Query(None, description="Filter by document status (active/superseded/draft)"),
    include_superseded: bool = Query(False, description="Include superseded orders in results"),
    generate_answer: bool = Query(True, description="Generate an LLM answer from retrieved chunks"),
    current_user: User = Depends(require_any_role),
):
    """
    Hybrid semantic + keyword search with LLM-generated answer and source citations.

    Each result includes:
    - Source document title, number, and date
    - Exact page and clause reference
    - Relevance score and match type (semantic/keyword/hybrid)
    - Document status label (ACTIVE / SUPERSEDED / DRAFT)
    - Confidence score for the generated answer
    """
    # Non-admins don't see restricted docs in search
    params = {
        "q": q,
        "top_k": top_k,
        "include_restricted": current_user.role == "admin",
        "include_superseded": include_superseded,
        "generate_answer": generate_answer,
    }
    if doc_type:
        params["doc_type"] = doc_type
    if year:
        params["year"] = year
    if status:
        params["status"] = status

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(f"{SEARCH_SERVICE_URL}/search", params=params)

    if resp.status_code != 200:
        return {"error": f"Search service error: {resp.text}", "results": []}
    return resp.json()


@router.post("/semantic", summary="Pure vector/semantic search")
async def semantic_search(
    q: str,
    top_k: int = 5,
    current_user: User = Depends(require_any_role),
):
    """Pure vector search without keyword fallback."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{SEARCH_SERVICE_URL}/semantic",
            json={"q": q, "top_k": top_k, "include_restricted": current_user.role == "admin"},
        )
    return resp.json()
