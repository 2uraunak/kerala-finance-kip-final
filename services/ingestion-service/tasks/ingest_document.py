"""
Celery Task — Full ingestion pipeline for a single document.
Orchestrates: detect → OCR/extract → chunk → embed → index → metadata write.
"""
import os
import uuid
import json
import asyncio
from datetime import datetime
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kip:kip_secret@postgres:5432/kipdb").replace(
    "postgresql+asyncpg://", "postgresql://"
)

celery_app = Celery("kip_ingest", broker=REDIS_URL, backend=REDIS_URL)

# Sync SQLAlchemy engine for Celery tasks
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


@celery_app.task(name="tasks.ingest_document.run_ingestion", bind=True, max_retries=3)
def run_ingestion(self, tmp_path: str, filename: str, title: str, doc_number: str,
                  doc_type: str, department: str, year: int | None, issue_date: str | None,
                  is_restricted: bool, supersedes_id: str | None, tags: str, uploaded_by: str):
    """
    Full ingestion pipeline Celery task.
    Steps:
        1. Detect scanned vs native PDF
        2. Extract text (OCR or native)
        3. Chunk text semantically
        4. Generate embeddings (local)
        5. Index into ChromaDB
        6. Write metadata to PostgreSQL
        7. Clean up temp file
    """
    from pipeline.detector import is_scanned_pdf
    from pipeline.ocr import ocr_pdf
    from pipeline.extractor import extract_native_pdf
    from pipeline.chunker import chunk_pages
    from pipeline.embedder import embed_texts
    from pipeline.indexer import index_chunks

    doc_id = str(uuid.uuid4())

    try:
        # Step 1: Detect
        self.update_state(state="PROGRESS", meta={"step": "detecting", "doc_id": doc_id})
        scanned = is_scanned_pdf(tmp_path)

        # Step 2: Extract
        self.update_state(state="PROGRESS", meta={"step": "extracting", "scanned": scanned})
        if scanned:
            pages, ocr_confidence = ocr_pdf(tmp_path)
            tables = []
        else:
            pages, tables = extract_native_pdf(tmp_path)
            ocr_confidence = None

        # Step 3: Chunk
        self.update_state(state="PROGRESS", meta={"step": "chunking"})
        chunks = chunk_pages(pages, doc_id=doc_id, doc_title=title)

        # Step 4: Embed
        self.update_state(state="PROGRESS", meta={"step": "embedding", "chunks": len(chunks)})
        if chunks:
            texts = [c["text"] for c in chunks]
            embeddings = embed_texts(texts)

            # Step 5: Index
            self.update_state(state="PROGRESS", meta={"step": "indexing"})
            indexed = index_chunks(chunks, embeddings, is_restricted=is_restricted)
        else:
            indexed = 0

        # Step 6: Write metadata to PostgreSQL
        self.update_state(state="PROGRESS", meta={"step": "writing_metadata"})
        full_text = "\n\n".join(p.get("text", "") for p in pages)

        with SessionLocal() as session:
            from sqlalchemy import text
            session.execute(text("""
                INSERT INTO documents (
                    id, title, doc_number, doc_type, status, department, year,
                    issue_date, is_scanned, ocr_confidence, is_restricted, is_indexed,
                    tags, raw_text, created_at, updated_at, created_by, supersedes_id
                ) VALUES (
                    :id, :title, :doc_number, :doc_type, 'active', :department, :year,
                    :issue_date, :is_scanned, :ocr_confidence, :is_restricted, true,
                    :tags, :raw_text, now(), now(), :created_by, :supersedes_id
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": doc_id, "title": title, "doc_number": doc_number or None,
                "doc_type": doc_type, "department": department, "year": year,
                "issue_date": issue_date, "is_scanned": scanned,
                "ocr_confidence": ocr_confidence, "is_restricted": is_restricted,
                "tags": json.dumps(json.loads(tags) if tags else []),
                "raw_text": full_text[:50000],  # Cap at 50KB
                "created_by": uploaded_by, "supersedes_id": supersedes_id,
            })

            # Update lineage if this supersedes another doc
            if supersedes_id:
                session.execute(text("""
                    UPDATE documents SET status='superseded', superseded_by_id=:new_id
                    WHERE id=:old_id
                """), {"new_id": doc_id, "old_id": supersedes_id})

            session.commit()

        # Step 7: Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        return {
            "doc_id": doc_id,
            "title": title,
            "chunks_indexed": indexed,
            "pages": len(pages),
            "tables": len(tables),
            "is_scanned": scanned,
            "ocr_confidence": ocr_confidence,
            "status": "completed",
        }

    except Exception as exc:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise self.retry(exc=exc, countdown=30)
