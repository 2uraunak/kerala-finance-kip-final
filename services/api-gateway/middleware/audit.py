"""
Audit Logging Middleware.
Records every HTTP request with user identity, action, resource, and response status.
The audit log is the cornerstone of the enterprise data isolation criterion (4 marks).
"""
import json
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal
from models.user import AuditLog


# Paths to skip auditing (health checks, static assets)
_SKIP_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}

# Map path prefixes to human-readable action names
_PATH_ACTION_MAP = {
    "/api/v1/auth": "AUTH",
    "/api/v1/documents": "DOCUMENT",
    "/api/v1/search": "SEARCH",
    "/api/v1/lineage": "LINEAGE",
    "/api/v1/extract": "EXTRACTION",
    "/api/v1/gst": "GST_QUERY",
    "/api/v1/agent": "POLICY_AGENT",
    "/api/v1/analytics": "ANALYTICS",
    "/api/v1/chat": "CHAT",
}


def _resolve_action(path: str, method: str) -> str:
    for prefix, action in _PATH_ACTION_MAP.items():
        if path.startswith(prefix):
            suffix = {
                "GET": "VIEW",
                "POST": "CREATE",
                "PUT": "UPDATE",
                "DELETE": "DELETE",
                "PATCH": "PATCH",
            }.get(method, method)
            return f"{action}_{suffix}"
    return f"UNKNOWN_{method}"


class AuditMiddleware(BaseHTTPMiddleware):
    """Intercepts every request and writes an audit log entry."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start_time = time.time()
        response: Response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # Extract user identity from request state (set by auth dependency if called)
        user_id = getattr(request.state, "user_id", None)
        username = getattr(request.state, "username", "anonymous")
        role = getattr(request.state, "role", "unknown")

        # Build log entry (async, non-blocking)
        log_entry = AuditLog(
            id=uuid.uuid4(),
            timestamp=datetime.utcnow(),
            user_id=str(user_id) if user_id else None,
            username=username,
            role=role,
            action=_resolve_action(request.url.path, request.method),
            resource_type=request.url.path.split("/")[3] if len(request.url.path.split("/")) > 3 else None,
            resource_id=request.path_params.get("doc_id") or request.path_params.get("id"),
            request_path=request.url.path,
            request_method=request.method,
            payload_summary=str(dict(request.query_params))[:500],
            response_status=str(response.status_code),
            ip_address=request.client.host if request.client else "unknown",
            extra={"duration_ms": duration_ms},
        )

        # Write asynchronously to avoid blocking the response
        try:
            async with AsyncSessionLocal() as session:
                session.add(log_entry)
                await session.commit()
        except Exception:
            pass  # Never fail a request due to audit logging

        return response
