"""
Lineage Service — document versioning, supersession chains, active version resolver.
"""
import os
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kip:kip_secret@postgres:5432/kipdb").replace(
    "postgresql+asyncpg://", "postgresql://"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="KIP Lineage Service", version="1.0.0")


@app.get("/lineage/{doc_id}")
async def get_lineage(doc_id: str):
    """Return the full lineage chain for a document."""
    with SessionLocal() as session:
        # Walk the supersession chain upward (older to newer)
        doc = session.execute(text("SELECT * FROM documents WHERE id=:id"), {"id": doc_id}).fetchone()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        chain = _build_chain(session, doc_id)
        versions = session.execute(
            text("SELECT * FROM document_versions WHERE document_id=:id ORDER BY version_number"),
            {"id": doc_id}
        ).fetchall()

    return {
        "doc_id": doc_id,
        "lineage_chain": chain,
        "versions": [dict(v._mapping) for v in versions],
        "current_status": dict(doc._mapping).get("status", "active"),
        "is_superseded": dict(doc._mapping).get("status") == "superseded",
        "superseded_by_id": str(dict(doc._mapping).get("superseded_by_id", "") or ""),
    }


def _build_chain(session, doc_id: str, visited: set = None, depth: int = 0) -> list:
    """Recursively build the supersession chain."""
    if visited is None:
        visited = set()
    if doc_id in visited or depth > 20:
        return []
    visited.add(doc_id)

    row = session.execute(text("SELECT * FROM documents WHERE id=:id"), {"id": doc_id}).fetchone()
    if not row:
        return []

    data = dict(row._mapping)
    node = {
        "id": str(data.get("id", "")),
        "title": data.get("title", ""),
        "doc_number": data.get("doc_number", ""),
        "status": data.get("status", "active"),
        "issue_date": str(data.get("issue_date", "")) if data.get("issue_date") else None,
        "depth": depth,
        "superseded_by": [],
    }

    superseded_by_id = data.get("superseded_by_id")
    if superseded_by_id:
        node["superseded_by"] = _build_chain(session, str(superseded_by_id), visited, depth + 1)

    return [node]


class SupersedeRequest(BaseModel):
    doc_id: str
    superseded_by_id: str
    updated_by: str = "system"


@app.post("/supersede")
async def supersede(req: SupersedeRequest):
    """Mark a document as superseded."""
    with SessionLocal() as session:
        # Verify both documents exist
        old = session.execute(text("SELECT id FROM documents WHERE id=:id"), {"id": req.doc_id}).fetchone()
        new = session.execute(text("SELECT id FROM documents WHERE id=:id"), {"id": req.superseded_by_id}).fetchone()
        if not old or not new:
            raise HTTPException(status_code=404, detail="One or both documents not found")

        session.execute(text("""
            UPDATE documents SET status='superseded', superseded_by_id=:new_id, updated_at=now()
            WHERE id=:old_id
        """), {"new_id": req.superseded_by_id, "old_id": req.doc_id})
        session.execute(text("""
            UPDATE documents SET supersedes_id=:old_id, updated_at=now()
            WHERE id=:new_id
        """), {"old_id": req.doc_id, "new_id": req.superseded_by_id})
        session.commit()

    return {"message": f"Document {req.doc_id} marked as superseded by {req.superseded_by_id}"}


@app.get("/active/{doc_number}")
async def get_active_version(doc_number: str):
    """Find the currently active version of a document by its GO number."""
    with SessionLocal() as session:
        rows = session.execute(text("""
            SELECT * FROM documents
            WHERE doc_number ILIKE :num
            ORDER BY issue_date DESC NULLS LAST, created_at DESC
        """), {"num": f"%{doc_number}%"}).fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail=f"No documents found matching '{doc_number}'")

        # Find the active one
        active = next((r for r in rows if dict(r._mapping)["status"] == "active"), None)
        latest = dict(rows[0]._mapping) if rows else None

    return {
        "doc_number": doc_number,
        "active_version": dict(active._mapping) if active else None,
        "latest_version": latest,
        "total_versions": len(rows),
        "warning": "No active version found — all versions are superseded or archived" if not active else None,
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "lineage"}
