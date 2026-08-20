"""
Analytics Service — usage metrics, query logs, document coverage.
"""
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="KIP Analytics Service", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kip:kip_secret@postgres:5432/kipdb").replace(
    "postgresql+asyncpg://", "postgresql://"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


@app.get("/summary")
async def summary(days: int = 30):
    """Platform usage summary."""
    since = datetime.utcnow() - timedelta(days=days)
    with SessionLocal() as session:
        total_docs = session.execute(text("SELECT COUNT(*) FROM documents")).scalar()
        total_queries = session.execute(
            text("SELECT COUNT(*) FROM audit_logs WHERE action LIKE 'SEARCH%' AND timestamp > :since"),
            {"since": since}
        ).scalar()
        active_users = session.execute(
            text("SELECT COUNT(DISTINCT username) FROM audit_logs WHERE timestamp > :since"),
            {"since": since}
        ).scalar()
        scanned_docs = session.execute(
            text("SELECT COUNT(*) FROM documents WHERE is_scanned = true")
        ).scalar()
        active_docs = session.execute(
            text("SELECT COUNT(*) FROM documents WHERE status = 'active'")
        ).scalar()
        superseded_docs = session.execute(
            text("SELECT COUNT(*) FROM documents WHERE status = 'superseded'")
        ).scalar()

    return {
        "period_days": days,
        "total_documents": total_docs,
        "active_documents": active_docs,
        "superseded_documents": superseded_docs,
        "scanned_documents": scanned_docs,
        "total_search_queries": total_queries,
        "active_users": active_users,
        "generated_at": datetime.utcnow().isoformat(),
    }


@app.get("/top-queries")
async def top_queries(days: int = 7, limit: int = 10):
    """Most frequent search queries."""
    since = datetime.utcnow() - timedelta(days=days)
    with SessionLocal() as session:
        rows = session.execute(text("""
            SELECT payload_summary, COUNT(*) as freq
            FROM audit_logs
            WHERE action='SEARCH_VIEW' AND timestamp > :since
            GROUP BY payload_summary
            ORDER BY freq DESC
            LIMIT :limit
        """), {"since": since, "limit": limit}).fetchall()
    return {
        "period_days": days,
        "top_queries": [{"query": r.payload_summary, "count": r.freq} for r in rows]
    }


@app.get("/document-coverage")
async def document_coverage():
    """Document indexing and type coverage."""
    with SessionLocal() as session:
        by_type = session.execute(text("""
            SELECT doc_type, COUNT(*) as count FROM documents GROUP BY doc_type
        """)).fetchall()
        indexed = session.execute(
            text("SELECT COUNT(*) FROM documents WHERE is_indexed = true")
        ).scalar()
        total = session.execute(text("SELECT COUNT(*) FROM documents")).scalar()

    return {
        "total_documents": total,
        "indexed_documents": indexed,
        "coverage_percentage": round((indexed / total * 100) if total > 0 else 0, 1),
        "by_type": [{"doc_type": r.doc_type, "count": r.count} for r in by_type],
    }


@app.get("/search-latency")
async def search_latency(days: int = 7):
    """Search latency statistics."""
    since = datetime.utcnow() - timedelta(days=days)
    with SessionLocal() as session:
        rows = session.execute(text("""
            SELECT extra->>'duration_ms' as duration_ms
            FROM audit_logs
            WHERE action='SEARCH_VIEW' AND timestamp > :since
            AND extra->>'duration_ms' IS NOT NULL
        """), {"since": since}).fetchall()

    latencies = [int(r.duration_ms) for r in rows if r.duration_ms]
    if not latencies:
        return {"message": "No search latency data available", "period_days": days}

    latencies.sort()
    n = len(latencies)
    return {
        "period_days": days,
        "sample_count": n,
        "p50_ms": latencies[n // 2],
        "p90_ms": latencies[int(n * 0.9)],
        "p99_ms": latencies[int(n * 0.99)] if n > 100 else latencies[-1],
        "avg_ms": round(sum(latencies) / n, 1),
        "min_ms": latencies[0],
        "max_ms": latencies[-1],
    }


@app.get("/audit-log")
async def audit_log(skip: int = 0, limit: int = 50, username: str = None, action: str = None):
    """View audit log entries."""
    with SessionLocal() as session:
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = {}
        if username:
            query += " AND username = :username"
            params["username"] = username
        if action:
            query += " AND action = :action"
            params["action"] = action
        query += " ORDER BY timestamp DESC LIMIT :limit OFFSET :skip"
        params.update({"limit": limit, "skip": skip})

        rows = session.execute(text(query), params).fetchall()
        total = session.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [dict(r._mapping) for r in rows],
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "analytics"}
