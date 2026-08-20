"""
Analytics router — usage metrics, top queries, document coverage.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
import httpx

from models.user import User
from middleware.auth import require_analyst_or_admin

router = APIRouter()
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8007")


@router.get("/summary", summary="Platform usage summary")
async def analytics_summary(
    days: int = Query(30, description="Look-back window in days"),
    current_user: User = Depends(require_analyst_or_admin),
):
    """Returns platform-wide usage summary: total queries, documents, top queries, active users."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/summary", params={"days": days})
    return resp.json()


@router.get("/top-queries", summary="Most frequent search queries")
async def top_queries(
    days: int = 7,
    limit: int = 10,
    current_user: User = Depends(require_analyst_or_admin),
):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/top-queries", params={"days": days, "limit": limit})
    return resp.json()


@router.get("/document-coverage", summary="Document indexing coverage by type")
async def document_coverage(
    current_user: User = Depends(require_analyst_or_admin),
):
    """Returns breakdown of documents by type, OCR vs native, indexed vs pending."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/document-coverage")
    return resp.json()


@router.get("/search-latency", summary="Search latency histogram")
async def search_latency(
    days: int = 7,
    current_user: User = Depends(require_analyst_or_admin),
):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/search-latency", params={"days": days})
    return resp.json()


@router.get("/audit-log", summary="View audit log (Admin only)")
async def view_audit_log(
    skip: int = 0,
    limit: int = 50,
    username: Optional[str] = None,
    action: Optional[str] = None,
    current_user: User = Depends(require_analyst_or_admin),
):
    """View the system audit trail. Admins see all, Analysts see their own."""
    params: dict = {"skip": skip, "limit": limit}
    if current_user.role != "admin":
        params["username"] = current_user.username  # Restrict to own logs
    elif username:
        params["username"] = username
    if action:
        params["action"] = action

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{ANALYTICS_SERVICE_URL}/audit-log", params=params)
    return resp.json()
