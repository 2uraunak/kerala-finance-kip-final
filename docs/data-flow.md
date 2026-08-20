# Document Data Flow & RAG Pipeline

This document explains the step-by-step flow of a government order from upload to AI retrieval.

## 1. Document Ingestion Phase
1. **Upload:** User uploads a PDF (e.g., `GO_45_2023.pdf`) via the UI.
2. **Gateway:** The API Gateway validates the file type, checks RBAC, and stores metadata in PostgreSQL.
3. **Queueing:** A Celery task is dispatched to Redis.
4. **Extraction & OCR:** The Ingestion Service picks up the task. It uses `pdfplumber` to extract native text. If it detects a scanned document, it routes the pages through `Tesseract OCR`.
5. **Chunking:** The text is semantically chunked into meaningful paragraphs/clauses (approx 500-1000 tokens each).
6. **Embedding:** `sentence-transformers` generates vector embeddings for every chunk.
7. **Indexing:** Vectors and metadata (status, doc_type) are stored in ChromaDB.

## 2. Search & Retrieval Phase
1. **Query:** User searches for "dearness allowance revision 2023".
2. **Hybrid Search:** The Search Service executes two parallel searches:
   - **Semantic Search:** Finds chunks in ChromaDB with similar vector meanings.
   - **Keyword Search:** Uses BM25 algorithm to find exact terminology matches.
3. **RRF (Reciprocal Rank Fusion):** The results are merged. If a document ranks highly in both keyword and semantic searches, it is pushed to the top.
4. **Lineage Check:** The system checks PostgreSQL. If the top result is marked as `SUPERSEDED`, a prominent warning flag and a link to the active document are attached.

## 3. GST Agent (RAG) Phase
1. **Chat:** User asks "What is the GST rate for works contract?"
2. **Retrieval:** The GST agent internally queries the Search Service for highly relevant GST policies.
3. **Prompt Assembly:** The retrieved circular text is injected into a strict prompt template instructing the LLM to only use the provided context.
4. **Generation:** The local LLM generates a response citing the exact source documents.
