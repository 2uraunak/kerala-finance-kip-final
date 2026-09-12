"""
Search Service — Main FastAPI application.
Hybrid search: vector + BM25 + RRF reranking + LLM answer generation.
Includes: lineage-aware filtering, hallucination guard, superseded order interception.
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


def _check_superseded_in_results(chunks: List[dict]) -> dict:
    """
    Scan retrieved chunks for superseded documents and build a lineage warning.
    This is the 'outdated order trap' — prevents officials from citing old GOs.
    Called BEFORE filtering so we can always warn even if docs are removed.
    """
    superseded_docs = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        if meta.get("status") == "superseded" or meta.get("is_superseded"):
            superseded_docs.append({
                "doc_title": meta.get("doc_title", "Unknown"),
                "doc_number": meta.get("doc_number", ""),
                "superseded_by": meta.get("superseded_by_id", ""),
            })

    if superseded_docs:
        names = ", ".join(d["doc_number"] or d["doc_title"] for d in superseded_docs)
        return {
            "has_superseded": True,
            "superseded_documents": superseded_docs,
            "warning": (
                f"⚠️ LINEAGE WARNING: {names} "
                f"{'is' if len(superseded_docs) == 1 else 'are'} SUPERSEDED and NOT authoritative. "
                f"Do not cite {'this order' if len(superseded_docs) == 1 else 'these orders'} in policy notes. "
                f"The platform has intercepted this outdated source and will surface the active version."
            ),
        }
    return {"has_superseded": False, "superseded_documents": [], "warning": None}


def _generate_answer(query: str, chunks: List[dict]) -> tuple[str, float]:
    """
    Use Ollama to generate a grounded answer from retrieved chunks.
    Returns (answer_text, confidence_score).
    Includes explicit hallucination guard — refuses to answer without evidence.
    """
    if not chunks:
        return (
            "⚠️ HALLUCINATION GUARD: I cannot answer this question — no relevant documents "
            "were found in the Finance Department corpus. I will not generate an answer from "
            "general knowledge as that could introduce errors into official policy work.",
            0.0
        )

    context_parts = []
    superseded_warnings = []
    for i, chunk in enumerate(chunks[:5]):
        meta = chunk.get("metadata", {})
        status = meta.get("status", "active")
        is_superseded = status == "superseded" or meta.get("is_superseded", False)
        status_label = " [⚠️ SUPERSEDED — NOT AUTHORITATIVE]" if is_superseded else " [✅ ACTIVE]"
        if is_superseded:
            superseded_warnings.append(meta.get("doc_number") or meta.get("doc_title", "Unknown"))
        context_parts.append(
            f"[Source {i+1}: {meta.get('doc_title', 'Unknown')}{status_label} | "
            f"Page {meta.get('page', '?')} | Status: {status.upper()}]\n"
            f"{chunk.get('chunk_text', '')}"
        )
    context = "\n\n---\n\n".join(context_parts)

    superseded_instruction = ""
    if superseded_warnings:
        superseded_instruction = (
            f"\n\nCRITICAL: The following source(s) are SUPERSEDED and must NOT be treated as "
            f"authoritative: {', '.join(superseded_warnings)}. "
            f"Explicitly warn the user and direct them to the active version."
        )

    prompt = f"""You are an expert policy assistant for the Finance Department, Government of Kerala.

STRICT RULES:
1. Answer ONLY from the provided source documents. Do NOT use general knowledge.
2. Always cite sources using [Source N] notation with the exact GO number and page.
3. If a source is marked SUPERSEDED, explicitly warn the user — do NOT use it as authoritative.
4. If the answer is not in the documents, state: "The answer is not available in the indexed documents."
5. Always mention the exact GO number, date, and relevant provision when citing policy.
{superseded_instruction}

QUESTION: {query}

SOURCE DOCUMENTS:
{context}

ANSWER (with citations and lineage status):"""

    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        answer = llm.invoke(prompt)
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
    - results: ranked chunks with source review labels and lineage status
    - answer: LLM-generated answer grounded strictly in retrieved docs (hallucination guard)
    - citations: structured source references with status
    - lineage_check: superseded order detection + warning before filtering
    """
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    _embed = DefaultEmbeddingFunction()
    query_embedding = _embed([q])[0]

    filters = {}
    if doc_type:
        filters["doc_type"] = doc_type
    if year:
        filters["year"] = year

    # Parallel retrieval
    vec_results = vector_search(query_embedding, top_k=top_k * 2, include_restricted=include_restricted, filters=filters)
    kw_results = bm25_search(q, top_k=top_k * 2)

    # Fuse via RRF
    merged = reciprocal_rank_fusion(vec_results, kw_results)

    # ── Run lineage check BEFORE filtering (so warning is always shown) ──
    lineage_check = _check_superseded_in_results(merged)

    # Filter out superseded documents from results unless explicitly requested
    if not include_superseded:
        filtered = [
            r for r in merged
            if r.get("metadata", {}).get("status") != "superseded"
            and not r.get("metadata", {}).get("is_superseded")
        ]
        # Edge case: if all results are superseded, still show with warning
        if not filtered and merged:
            filtered = merged
            lineage_check["warning"] = (
                "⚠️ ALL retrieved documents are superseded. "
                "The platform cannot find an active version. "
                "Please check if the authoritative order has been indexed."
            )
    else:
        filtered = merged

    filtered = filtered[:top_k]
    citations = build_citations(filtered)

    # Hallucination guard: no docs = explicit refusal, not a fabricated answer
    if not filtered:
        return {
            "query": q,
            "answer": (
                f"⚠️ HALLUCINATION GUARD: No relevant documents found in the Finance Department "
                f"corpus for: '{q}'. I will not generate an answer from general knowledge. "
                f"Please check if the relevant GO/Circular has been indexed."
            ),
            "confidence": 0.0,
            "result_count": 0,
            "results": [],
            "citations": [],
            "lineage_check": lineage_check,
            "search_types_used": ["semantic", "keyword", "rrf_fusion"],
            "no_answer_reason": "no_relevant_documents",
        }

    # Generate LLM answer grounded strictly in retrieved docs
    answer, confidence = ("", 0.0)
    if generate_answer and filtered:
        answer, confidence = _generate_answer(q, filtered)

    return {
        "query": q,
        "answer": answer,
        "confidence": confidence,
        "result_count": len(filtered),
        "results": filtered,
        "citations": citations,
        "lineage_check": lineage_check,
        "search_types_used": ["semantic", "keyword", "rrf_fusion"],
    }


@app.post("/semantic")
async def semantic_search_endpoint(body: dict):
    """Pure semantic search."""
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    _embed = DefaultEmbeddingFunction()
    q = body.get("q", "")
    top_k = body.get("top_k", 5)
    query_embedding = _embed([q])[0]
    results = vector_search(query_embedding, top_k=top_k, include_restricted=body.get("include_restricted", False))
    return {"query": q, "results": results, "citations": build_citations(results)}


@app.post("/chat")
async def chat(body: ChatRequest):
    """Multi-turn conversational Q&A."""
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    _embed = DefaultEmbeddingFunction()
    query_embedding = _embed([body.message])[0]
    vec_results = vector_search(query_embedding, top_k=6, include_restricted=body.include_restricted)
    kw_results = bm25_search(body.message, top_k=6)
    merged = reciprocal_rank_fusion(vec_results, kw_results)[:5]
    lineage_check = _check_superseded_in_results(merged)
    answer, confidence = _generate_answer(body.message, merged)
    return {
        "message": body.message,
        "response": answer,
        "confidence": confidence,
        "citations": build_citations(merged),
        "lineage_check": lineage_check,
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
