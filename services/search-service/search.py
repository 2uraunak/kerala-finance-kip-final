"""
Search Service — Main FastAPI application.
Hybrid search: vector + BM25 + RRF reranking + LLM answer generation.
"""
import os
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

from hybrid.vector_search import vector_search
from hybrid.bm25_search import bm25_search, build_bm25_index
from hybrid.reranker import reciprocal_rank_fusion
from cite import build_citations

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build BM25 index at startup."""
    try:
        build_bm25_index()
    except Exception as e:
        print(f"Warning: BM25 index build failed at startup: {e}")
    yield


app = FastAPI(title="KIP Search Service", version="1.0.0", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    doc_ids: List[str] = []
    user_role: str = "viewer"
    include_restricted: bool = False


def _generate_answer(query: str, chunks: List[dict]) -> tuple[str, float]:
    """
    Use Ollama to generate a grounded answer from retrieved chunks.
    Returns (answer_text, confidence_score).
    """
    import httpx
    if not chunks:
        return "No relevant documents found for this query.", 0.0

    context_parts = []
    for i, chunk in enumerate(chunks[:5]):
        meta = chunk.get("metadata", {})
        context_parts.append(
            f"[Source {i+1}: {meta.get('doc_title', 'Unknown')} | Page {meta.get('page', '?')}]\n"
            f"{chunk.get('chunk_text', '')}"
        )
    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are an expert assistant for the Finance Department, Government of Kerala.
Answer the following question based ONLY on the provided source documents.
Always cite your sources using [Source N] notation.
If the answer is not in the documents, say so clearly.

QUESTION: {query}

SOURCE DOCUMENTS:
{context}

ANSWER (with source citations):"""

    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        answer = llm.invoke(prompt)
        # Estimate confidence based on top chunk score
        top_score = chunks[0].get("rrf_score", chunks[0].get("score", 0.5))
        confidence = min(round(float(top_score) * 1.5, 2), 1.0)
        return answer, confidence
    except Exception as e:
        print(f"LLM generation error: {e}")

    return "Answer generation unavailable. See source documents for relevant information.", 0.5


@app.get("/search")
async def search(
    q: str,
    top_k: int = 5,
    include_restricted: bool = False,
    include_superseded: bool = False,
    generate_answer: bool = True,
    doc_type: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
):
    """
    Hybrid search endpoint. Returns:
    - results: ranked chunks with source review labels
    - answer: LLM-generated answer with citations
    - citations: structured source references
    """
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"))
    query_embedding = model.encode([q], normalize_embeddings=True)[0].tolist()

    filters = {}
    if doc_type:
        filters["doc_type"] = doc_type
    if year:
        filters["year"] = year

    # Parallel retrieval
    vec_results = vector_search(query_embedding, top_k=top_k * 2, include_restricted=include_restricted, filters=filters)
    kw_results = bm25_search(q, top_k=top_k * 2)

    # Fuse results
    merged = reciprocal_rank_fusion(vec_results, kw_results)[:top_k]

    # Build source review labels
    citations = build_citations(merged)

    # Generate LLM answer
    answer, confidence = ("", 0.0)
    if generate_answer and merged:
        answer, confidence = _generate_answer(q, merged)

    return {
        "query": q,
        "answer": answer,
        "confidence": confidence,
        "result_count": len(merged),
        "results": merged,
        "citations": citations,
        "search_types_used": ["semantic", "keyword", "rrf_fusion"],
    }


@app.post("/semantic")
async def semantic_search_endpoint(body: dict):
    """Pure semantic search."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"))
    q = body.get("q", "")
    top_k = body.get("top_k", 5)
    query_embedding = model.encode([q], normalize_embeddings=True)[0].tolist()
    results = vector_search(query_embedding, top_k=top_k, include_restricted=body.get("include_restricted", False))
    return {"query": q, "results": results, "citations": build_citations(results)}


@app.post("/chat")
async def chat(body: ChatRequest):
    """Multi-turn conversational Q&A."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2"))
    query_embedding = model.encode([body.message], normalize_embeddings=True)[0].tolist()
    vec_results = vector_search(query_embedding, top_k=6, include_restricted=body.include_restricted)
    kw_results = bm25_search(body.message, top_k=6)
    merged = reciprocal_rank_fusion(vec_results, kw_results)[:5]
    answer, confidence = _generate_answer(body.message, merged)
    return {
        "message": body.message,
        "response": answer,
        "confidence": confidence,
        "citations": build_citations(merged),
        "sources_used": len(merged),
    }


@app.get("/rebuild-index")
async def rebuild_bm25():
    """Admin endpoint to rebuild the BM25 index (e.g., after new documents are ingested)."""
    build_bm25_index()
    return {"message": "BM25 index rebuilt"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "search"}
