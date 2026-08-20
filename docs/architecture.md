# System Architecture

The Knowledge Intelligence Platform uses a scalable, event-driven microservices architecture to ensure high cohesion, low coupling, and enterprise-grade security.

## Core Components

1. **Frontend (React / Vite)**
   - Provides an accessible, responsive UI for officers.
   - Communicates exclusively via REST API.

2. **API Gateway (FastAPI)**
   - Single entry point for all client requests.
   - Handles JWT authentication and Role-Based Access Control (RBAC).
   - Routes requests to appropriate internal microservices.

3. **Search Service (FastAPI)**
   - Manages semantic (vector) and keyword queries.
   - Interfaces directly with ChromaDB for vector retrieval.
   - Implements Reciprocal Rank Fusion (RRF) for high accuracy.

4. **Ingestion Service (FastAPI + Celery)**
   - Listens to upload queues.
   - Runs Tesseract OCR on scanned PDFs.
   - Chunks text based on semantic boundaries (e.g., clauses).
   - Generates embeddings using `sentence-transformers/all-MiniLM-L6-v2`.

5. **GST Policy Agent (FastAPI)**
   - Agentic workflow designed to answer complex tax and compliance questions.
   - Queries the local LLM using LangChain.

6. **Storage Layer**
   - **PostgreSQL:** Stores document metadata, lineage (superseded links), user accounts, and audit logs.
   - **ChromaDB:** Stores vector embeddings of document chunks.
   - **Redis:** Acts as a message broker for Celery queues.

## Trust Boundaries
- **No external data leaks:** All embeddings and LLM generations happen entirely on the local network. 
- **Isolated Databases:** Only the internal microservices can communicate with Postgres and ChromaDB; they are not exposed to the public internet.
