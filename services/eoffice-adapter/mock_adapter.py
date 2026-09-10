"""
e-Office Mock Adapter — simulates integration with the Government of Kerala's
e-Office document management and dispatch system.

This mock provides contract-faithful API boundaries, authentication simulation,
retry logic documentation, and realistic failure scenarios for the demo.

In production, this adapter would be replaced with the actual e-Office REST API
integration with OAuth 2.0 authentication.
"""
import os
import time
import random
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="KIP e-Office Mock Adapter",
    version="1.0.0",
    description=(
        "Mock adapter simulating the Government of Kerala e-Office API. "
        "Provides contract-faithful endpoints for document search, dispatch, "
        "and status tracking with authentication boundaries and failure simulation."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mock document registry (simulates e-Office document store) ──
MOCK_DOCUMENTS = [
    {
        "eoffice_id": "EOFF-2023-GO-045",
        "doc_number": "GO(Ms)No.45/2023/Fin",
        "title": "Dearness Allowance Revision — March 2023",
        "status": "SUPERSEDED",
        "department": "Finance Department",
        "filed_date": "2023-03-01",
        "file_number": "FIN-DA-2023-045",
    },
    {
        "eoffice_id": "EOFF-2023-GO-112",
        "doc_number": "GO(Ms)No.112/2023/Fin",
        "title": "Dearness Allowance Revision — September 2023 (AUTHORITATIVE)",
        "status": "ACTIVE",
        "department": "Finance Department",
        "filed_date": "2023-09-01",
        "file_number": "FIN-DA-2023-112",
    },
    {
        "eoffice_id": "EOFF-2022-GO-089",
        "doc_number": "GO(Ms)No.89/2022/Fin",
        "title": "Travelling Allowance Revision — 2022",
        "status": "ACTIVE",
        "department": "Finance Department",
        "filed_date": "2022-07-01",
        "file_number": "FIN-TA-2022-089",
    },
]

# Simulated dispatch queue
DISPATCH_QUEUE = {}


def _verify_auth(token: Optional[str]) -> dict:
    """
    Simulates OAuth 2.0 bearer token verification.
    In production: validates JWT against Government Identity Provider.
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized",
                "message": "Bearer token required. Obtain token from /auth/token endpoint.",
                "auth_endpoint": "https://eoffice.kerala.gov.in/auth/token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Simulate token expiry (demo: accept any non-empty token)
    if token.startswith("expired_"):
        raise HTTPException(
            status_code=401,
            detail={"error": "token_expired", "message": "Access token has expired. Please refresh."},
            headers={"WWW-Authenticate": "Bearer error=invalid_token"},
        )
    return {"user": "kip_service_account", "scopes": ["documents:read", "dispatch:write"]}


def _simulate_latency():
    """Simulates realistic network latency for a government API."""
    time.sleep(random.uniform(0.05, 0.15))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "eoffice-mock-adapter",
        "version": "1.0.0",
        "integration": "Government of Kerala e-Office System (Mock)",
        "auth_method": "OAuth 2.0 Bearer Token",
        "retry_policy": "Exponential backoff: 1s, 2s, 4s (max 3 retries)",
    }


@app.get("/eoffice/search", summary="Search e-Office document registry")
async def search_documents(
    query: str = Query(..., description="Search term for e-Office documents"),
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, SUPERSEDED, DRAFT"),
    department: Optional[str] = Query(None, description="Filter by department"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    Search the e-Office document registry.

    Authentication: Bearer token (OAuth 2.0)
    Rate limit: 100 requests/minute per service account
    Retry policy: Exponential backoff with max 3 retries
    """
    token = authorization.replace("Bearer ", "") if authorization else None
    _verify_auth(token)
    _simulate_latency()

    # Simulate occasional upstream failure (5% chance)
    if random.random() < 0.05:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "upstream_unavailable",
                "message": "e-Office upstream temporarily unavailable. Retry after 2 seconds.",
                "retry_after": 2,
                "retry_policy": "Exponential backoff recommended",
            },
            headers={"Retry-After": "2"},
        )

    results = []
    for doc in MOCK_DOCUMENTS:
        matches = query.lower() in doc["title"].lower() or query.lower() in doc["doc_number"].lower()
        status_ok = not status or doc["status"] == status.upper()
        dept_ok = not department or department.lower() in doc["department"].lower()
        if matches and status_ok and dept_ok:
            results.append({
                **doc,
                "kip_integration_note": (
                    "SUPERSEDED — KIP will flag this document and surface the active version."
                    if doc["status"] == "SUPERSEDED"
                    else "ACTIVE — Safe to reference in policy notes."
                ),
            })

    return {
        "query": query,
        "results": results,
        "total": len(results),
        "source": "e-Office Mock Registry",
        "timestamp": datetime.utcnow().isoformat(),
        "kip_lineage_check": "enabled",
    }


class DispatchRequest(BaseModel):
    document_id: str
    recipient_department: str
    subject: str
    priority: str = "NORMAL"  # NORMAL | URGENT | IMMEDIATE
    drafted_by: str
    policy_note_reference: Optional[str] = None


@app.post("/eoffice/dispatch", summary="Dispatch document/policy note via e-Office")
async def dispatch_document(
    req: DispatchRequest,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    Dispatch a document or policy note to another department via e-Office.

    Authentication: Bearer token with dispatch:write scope
    Idempotency: Provide a unique policy_note_reference to prevent duplicate dispatch
    """
    token = authorization.replace("Bearer ", "") if authorization else None
    _verify_auth(token)
    _simulate_latency()

    dispatch_id = str(uuid.uuid4())[:8].upper()
    DISPATCH_QUEUE[dispatch_id] = {
        "dispatch_id": dispatch_id,
        "document_id": req.document_id,
        "recipient": req.recipient_department,
        "subject": req.subject,
        "priority": req.priority,
        "drafted_by": req.drafted_by,
        "status": "QUEUED",
        "created_at": datetime.utcnow().isoformat(),
        "estimated_delivery": "2-4 hours (NORMAL priority)",
    }

    return {
        "success": True,
        "dispatch_id": dispatch_id,
        "status": "QUEUED",
        "message": f"Document queued for dispatch to {req.recipient_department}",
        "tracking_url": f"/eoffice/status/{dispatch_id}",
        "audit_reference": f"KIP-DISPATCH-{dispatch_id}",
        "kip_note": "This dispatch is logged in the KIP audit trail for compliance.",
    }


@app.get("/eoffice/status/{dispatch_id}", summary="Track dispatch status")
async def get_dispatch_status(
    dispatch_id: str,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """Track the delivery status of a dispatched document."""
    token = authorization.replace("Bearer ", "") if authorization else None
    _verify_auth(token)

    if dispatch_id not in DISPATCH_QUEUE:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": f"Dispatch ID {dispatch_id} not found"},
        )

    item = DISPATCH_QUEUE[dispatch_id]
    # Simulate status progression based on time
    elapsed = (datetime.utcnow() - datetime.fromisoformat(item["created_at"])).seconds
    if elapsed > 30:
        item["status"] = "DELIVERED"
    elif elapsed > 10:
        item["status"] = "IN_TRANSIT"

    return item


@app.get("/eoffice/auth-info", summary="Authentication boundary documentation")
async def auth_info():
    """Returns the authentication contract for this adapter."""
    return {
        "adapter": "KIP e-Office Mock Adapter",
        "auth_method": "OAuth 2.0 Bearer Token",
        "token_endpoint": "https://eoffice.kerala.gov.in/auth/token (production)",
        "scopes": {
            "documents:read": "Search and retrieve e-Office documents",
            "dispatch:write": "Dispatch documents and policy notes",
        },
        "retry_policy": {
            "strategy": "Exponential backoff",
            "delays_seconds": [1, 2, 4],
            "max_retries": 3,
            "on_status_codes": [429, 503, 504],
        },
        "rate_limits": {
            "requests_per_minute": 100,
            "burst_limit": 150,
        },
        "failure_handling": {
            "503": "Service unavailable — retry with backoff",
            "401": "Token expired — refresh token and retry",
            "403": "Insufficient scope — check service account permissions",
            "429": "Rate limited — wait for Retry-After header duration",
        },
        "isolation": "All KIP ↔ e-Office communication stays within the government intranet. No data leaves the local environment.",
    }
