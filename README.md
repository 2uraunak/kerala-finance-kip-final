# 🏛️ Kerala Finance KIP — Knowledge Intelligence Platform

> **Finance Department, Government of Kerala**  
> Enterprise document intelligence platform for Government Orders, Circulars, GST Policy, and Budget documents.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![LLM](https://img.shields.io/badge/LLM-Ollama%20Local-orange.svg)](https://ollama.ai)

---

## 📋 Overview

The Kerala Finance KIP is a **fully local, enterprise-grade** knowledge intelligence platform that:

- 🔍 **Hybrid Search** — Semantic (ChromaDB) + Keyword (BM25) + RRF reranking
- 🤖 **AI Q&A** — Local LLM (Ollama/llama3.2) with source citations
- 🔗 **Document Lineage** — Tracks Government Order supersession chains
- ⚗️ **Clause Extraction** — Structured clause and financial figure extraction
- 💹 **GST Assistant** — GST policy research with rate lookup
- ✍️ **Policy Note Agent** — Multi-step agentic policy-note drafting
- 📊 **Analytics** — Usage metrics and tamper-evident audit trail
- 🔒 **100% Local** — No data leaves the server

---

## ⚡ Quick Start (One Command)

### Prerequisites

| Requirement | Version | Notes |
|------------|---------|-------|
| Docker Desktop | 24+ | Enable Docker Compose v2 |
| RAM | ≥ 8 GB | 16 GB recommended with LLM |
| Disk Space | ≥ 20 GB | For model weights + documents |

### 1. Clone and Configure

```bash
git clone <repo-url>
cd kerala-finance-kip
cp .env.example .env
```

### 2. Start All Services

```bash
docker-compose up -d --build
# OR
make up
```

This starts: PostgreSQL, Redis, MinIO, ChromaDB, Ollama, API Gateway (8000), all microservices, and React frontend (3000).

### 3. Pull the LLM Model (Required)

```bash
make pull-model
# This runs: docker exec kip-ollama ollama pull llama3.2
# Wait ~5 min for first download (3.8 GB)
```

### 4. Seed Sample Documents & Users

```bash
make seed
```

This creates:
- 🔴 Admin: `admin_kerala` / `Admin@123`
- 🟡 Analyst: `analyst_finance` / `Analyst@123`
- ⚪ Viewer: `viewer_gst` / `Viewer@123`
- 6 sample Kerala Finance documents (GOs, Budget, GST, OM)

### 5. Access the Platform

| Service | URL |
|---------|-----|
| 🌐 **Web UI** | http://localhost:3000 |
| 📖 **API Docs** | http://localhost:8000/docs |
| 🗄️ **MinIO Console** | http://localhost:9001 (minioadmin/minioadmin123) |
| 🔗 **ChromaDB** | http://localhost:8100 |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     React Frontend (Port 3000)                      │
│   Dashboard │ Search │ Documents │ Lineage │ GST │ Agent │ Analytics│
└──────────────────────────┬──────────────────────────────────────────┘
                           │ REST / WebSocket
┌──────────────────────────▼──────────────────────────────────────────┐
│           FastAPI API Gateway (Port 8000) — /docs (OpenAPI)         │
│         JWT Auth │ RBAC │ Audit Middleware │ Rate Limiter            │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────────┬───┘
   ▼          ▼          ▼          ▼          ▼                 ▼
Ingest     Search    Lineage   Extract    GST Agent         Analytics
(8001)     (8002)    (8003)    (8004)     (8005/8006)       (8007)
   │          │                              │
   ▼          ▼                              ▼
ChromaDB  BM25+RRF                       Ollama (local LLM)
MinIO     Ollama                         LangChain Agent
Celery    sentence-transformers
   │
   ▼
PostgreSQL (metadata + audit log)
Redis (cache + task queue)
```

### Trust Boundaries

| Component | Isolation |
|-----------|-----------|
| Restricted documents | Separate ChromaDB collection (`kip_documents_restricted`) |
| LLM inference | 100% local Ollama — no external API calls |
| Embeddings | Local sentence-transformers — no external API calls |
| Audit log | Append-only PostgreSQL + SQLite — tamper-evident |
| Role enforcement | RBAC at API Gateway — Viewer/Analyst/Admin |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **API Framework** | FastAPI 0.111 (Python 3.11) |
| **LLM (Local)** | Ollama + llama3.2:3b |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Vector DB** | ChromaDB |
| **Keyword Search** | rank_bm25 |
| **Fusion** | Reciprocal Rank Fusion (RRF) |
| **OCR** | Tesseract 5 + PyMuPDF + pdfplumber |
| **Document Parsing** | Unstructured.io (open-source) |
| **Metadata DB** | PostgreSQL 16 |
| **Document Store** | MinIO (local S3) |
| **Task Queue** | Celery + Redis |
| **Agent Framework** | LangChain |
| **Frontend** | React 18 + Vite + Vanilla CSS |
| **Charts** | Chart.js + react-chartjs-2 |
| **Containers** | Docker Compose |

---

## 📁 Repository Structure

```
kerala-finance-kip/
├── docker-compose.yml          # One-command full stack
├── Makefile                    # make up / make seed / make test
├── .env.example                # Environment template
├── services/
│   ├── api-gateway/            # FastAPI gateway — auth, RBAC, routing
│   ├── ingestion-service/      # OCR pipeline + Celery workers
│   ├── search-service/         # Hybrid search + LLM answer generation
│   ├── lineage-service/        # Document versioning & supersession
│   ├── extraction-service/     # Clause & figure extraction
│   ├── gst-agent-service/      # GST policy research agent
│   ├── policy-agent-service/   # Policy note drafter agent
│   └── analytics-service/      # Usage metrics & audit log
├── frontend/                   # React + Vite UI
├── data/sample_documents/      # Mock Kerala Finance GOs (PDFs)
├── scripts/                    # Seed scripts
├── tests/                      # Automated test suite
├── nginx/                      # Reverse proxy
└── docs/                       # Architecture diagrams
```

---

## 🧪 Running Tests

```bash
make test
# OR
docker exec kip-api-gateway python -m pytest tests/ -v --tb=short
```

Test coverage:
- ✅ Authentication (login, invalid credentials)
- ✅ Access control (RBAC — viewer vs admin vs analyst)
- ✅ Search quality (citations present, answers generated)
- ✅ Document lineage (superseded status correctly set)
- ✅ Analytics (coverage metrics available)

---

## 🎯 Key Features Demonstrated

### 1. Document Ingestion & OCR
- Automatic scanned vs. native PDF detection
- Tesseract OCR with image preprocessing (grayscale, contrast, sharpen)
- Semantic chunking with page-level provenance
- Async pipeline via Celery task queue

### 2. Hybrid Search with Source Citations
Every search result includes a **Source Review Label**:
```json
{
  "source_label": "📄 GO(Ms)No.112/2023/Fin | Page 3",
  "status_label": "ACTIVE",
  "confidence": "HIGH",
  "match_type": "hybrid",
  "lineage_warning": false
}
```

### 3. Document Lineage & Version Tracking
```
GO(Ms)No.45/2023/Fin [SUPERSEDED]
         ↓ superseded by
GO(Ms)No.112/2023/Fin [ACTIVE]
```

### 4. Agentic Policy Note Drafting
3-step agent workflow:
1. **Retrieve** — Search for relevant GOs on the subject
2. **Verify** — Check lineage; reject superseded citations
3. **Draft** — Generate policy note in official Kerala format

### 5. Enterprise Data Isolation
- Restricted documents in separate ChromaDB collection
- RBAC enforced at gateway level
- Audit log captures every action (user, timestamp, IP, action, status)
- Zero external API calls — fully air-gappable

---

## 🔐 User Roles

| Role | Documents | Search | Extract | Agent | Admin |
|------|-----------|--------|---------|-------|-------|
| **Admin** | All (incl. restricted) | ✅ | ✅ | ✅ | ✅ |
| **Analyst** | Non-restricted | ✅ | ✅ | ✅ | ❌ |
| **Viewer** | Non-restricted | ✅ | ❌ | ❌ | ❌ |

---

## 📦 Deliverables

- [x] ✅ Working POC (ingestion, OCR, indexing, search, GST assistant)
- [x] ✅ Clean repository with service boundaries
- [x] ✅ OpenAPI specification at http://localhost:8000/docs
- [x] ✅ Docker Compose containerized deployment
- [x] ✅ Measured search/retrieval evaluation (`make test`)
- [x] ✅ Architecture & data-flow diagrams (see `docs/`)

---

## 📧 Contact

TCS AI Club Hackathon — ai.club@tcs.com
