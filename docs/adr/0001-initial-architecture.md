# 1. Initial Architecture and Technology Stack

Date: 2024-04-12

## Status
Accepted

## Context
We need to build a scalable, AI-powered knowledge management and policy research assistant for the Kerala Finance Department (KIP). The system needs to ingest complex PDF documents, perform OCR, chunk text, generate embeddings, and serve these through specialized agent services (GST, Policy).

## Decision
We have decided on the following technology stack and microservices architecture:

1. **Frontend**: React + Vite + TailwindCSS. State management via Zustand.
2. **API Gateway**: FastAPI for routing, auth, and rate limiting.
3. **Core Services**:
   - `ingestion-service`: Celery/Redis workers for document processing.
   - `search-service`: Hybrid search (Vector + BM25).
   - `extraction-service`: LLM-based clause/figure extraction.
   - `lineage-service`: Document versioning and supersession tracking.
   - `analytics-service`: Usage metrics.
4. **Agent Services**: LangChain-powered FastAPI services for specific domains.
   - `gst-agent-service`
   - `policy-agent-service`
5. **Infrastructure**: Docker Compose for local development. Postgres for relational data. MinIO for object storage (S3 compatible). Ollama for local LLM inference to ensure data privacy.

## Consequences
- **Positive**: High modularity, separation of concerns, ability to scale individual components (e.g., ingestion workers), privacy maintained via local LLMs.
- **Negative**: Increased operational complexity, higher memory footprint for running local models.
