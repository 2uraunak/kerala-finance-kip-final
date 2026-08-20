"""
Kerala Finance Knowledge Intelligence Platform
API Gateway — Main Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware.audit import AuditMiddleware
from middleware.rate_limiter import RateLimiterMiddleware
from routers import documents, search, lineage, extract, gst, agent, analytics, chat, auth
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Kerala Finance KIP — API Gateway",
    description=(
        "Enterprise Knowledge Intelligence Platform for the Finance Department, "
        "Government of Kerala. Provides document ingestion, search, lineage tracking, "
        "clause extraction, GST assistance, and agentic policy-note drafting."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Custom Middleware ────────────────────────────────────────────────────────
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimiterMiddleware, max_requests=200, window_seconds=60)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(auth.router,       prefix="/api/v1/auth",       tags=["Authentication"])
app.include_router(documents.router,  prefix="/api/v1/documents",  tags=["Documents"])
app.include_router(search.router,     prefix="/api/v1/search",     tags=["Search"])
app.include_router(lineage.router,    prefix="/api/v1/lineage",    tags=["Lineage & Versioning"])
app.include_router(extract.router,    prefix="/api/v1/extract",    tags=["Clause & Figure Extraction"])
app.include_router(gst.router,        prefix="/api/v1/gst",        tags=["GST Policy Assistant"])
app.include_router(agent.router,      prefix="/api/v1/agent",      tags=["Policy Note Agent"])
app.include_router(analytics.router,  prefix="/api/v1/analytics",  tags=["Analytics"])
app.include_router(chat.router,       prefix="/api/v1/chat",       tags=["Conversational Chat"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Kerala Finance KIP — API Gateway",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
