"""
GST Agent Service — LangChain-powered GST policy research assistant.
"""
import os
import re
import json
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

app = FastAPI(title="KIP GST Agent Service", version="1.0.0")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://search-service:8002")

# GST-specific knowledge base (hardcoded for POC demonstration)
GST_RATES = {
    "works contract": {"rate": "18%", "hsn": "9954", "notification": "13/2017-CT(R)"},
    "government services": {"rate": "Nil/18%", "hsn": "9997", "notification": "12/2017-CT(R)"},
    "construction": {"rate": "12%/18%", "hsn": "9954", "notification": "11/2017-CT(R)"},
    "consultancy": {"rate": "18%", "hsn": "9983", "notification": "11/2017-CT(R)"},
    "software": {"rate": "18%", "hsn": "9983", "notification": "11/2017-CT(R)"},
    "food": {"rate": "0%/5%/12%", "hsn": "0401-2106", "notification": "1/2017-CT(R)"},
}


class GSTQueryRequest(BaseModel):
    query: str
    context: str | None = None
    user_role: str = "analyst"


def _search_gst_docs(query: str) -> list:
    """Search the vector store for GST-related documents."""
    try:
        resp = httpx.get(
            f"{SEARCH_SERVICE_URL}/search",
            params={"q": f"GST {query}", "top_k": 5, "doc_type": "gst_policy", "generate_answer": False},
            timeout=30.0,
        )
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass
    return []


def _lookup_gst_rate(description: str) -> dict | None:
    """Simple keyword-based GST rate lookup from hardcoded table."""
    desc_lower = description.lower()
    for key, data in GST_RATES.items():
        if key in desc_lower:
            return {**data, "description": key}
    return None


@app.post("/query")
async def gst_query(req: GSTQueryRequest):
    """GST policy Q&A with source citations."""
    # Step 1: Search relevant GST documents
    search_results = _search_gst_docs(req.query)

    # Step 2: Check GST rate lookup
    rate_info = _lookup_gst_rate(req.query)

    # Step 3: Build context for LLM
    context_parts = []
    if rate_info:
        context_parts.append(f"GST Rate Reference: {rate_info['description']} — {rate_info['rate']} (Notification: {rate_info['notification']})")
    for r in search_results[:3]:
        meta = r.get("metadata", {})
        context_parts.append(f"[{meta.get('doc_title', 'GST Document')}] {r.get('chunk_text', '')[:500]}")

    context = "\n\n".join(context_parts) or "No specific documents found."

    prompt = f"""You are a GST expert for the Government of Kerala Finance Department.
Answer the following GST policy question based on the provided context.
Always mention the applicable GST rate, HSN code, and relevant notification number when available.

QUESTION: {req.query}

CONTEXT:
{context}

ANSWER (with specific circular/notification references):"""

    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        answer = llm.invoke(prompt)
    except Exception as e:
        answer = f"LLM unavailable. Based on database: {context}"

    citations = [
        {
            "source_label": f"📄 {r.get('metadata', {}).get('doc_title', 'GST Document')}",
            "page": r.get("metadata", {}).get("page", "?"),
            "relevance_score": r.get("rrf_score", r.get("score", 0)),
            "status_label": "ACTIVE",
        }
        for r in search_results
    ]

    return {
        "query": req.query,
        "answer": answer,
        "gst_rate_info": rate_info,
        "citations": citations,
        "source_count": len(search_results),
        "confidence": "HIGH" if rate_info else ("MEDIUM" if search_results else "LOW"),
    }


@app.get("/rate-lookup")
async def rate_lookup(description: str):
    """GST rate lookup by goods/service description."""
    rate = _lookup_gst_rate(description)
    if rate:
        return {"found": True, "description": description, **rate}
    return {"found": False, "description": description, "message": "Rate not in local database. Please check latest notifications."}


@app.get("/latest-circulars")
async def latest_circulars(topic: str = None, limit: int = 10):
    """Return latest GST circulars from the document store."""
    try:
        resp = httpx.get(
            f"{SEARCH_SERVICE_URL}/search",
            params={"q": f"GST circular {topic or 'notification'}", "top_k": limit, "generate_answer": False},
            timeout=30.0,
        )
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            return {"circulars": results, "count": len(results)}
    except Exception:
        pass
    return {"circulars": [], "count": 0}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gst-agent"}
