"""
Extraction Service — clause and financial figure extraction using local LLM.
"""
import os
import json
import re
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="KIP Extraction Service", version="1.0.0")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
MINIO_URL = os.getenv("MINIO_URL", "minio:9000")


def _call_llm(prompt: str, max_tokens: int = 2000) -> str:
    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        return llm.invoke(prompt)
    except Exception as e:
        print(f"Extraction LLM error: {e}")
        return ""


def _get_doc_text(doc_id: str) -> str:
    """Fetch document raw text from the API gateway / database."""
    # In production this would query the DB directly. For POC, fetch from gateway.
    try:
        resp = httpx.get(f"http://api-gateway:8000/api/v1/documents/{doc_id}", timeout=10.0)
        if resp.status_code == 200:
            return resp.json().get("raw_text", "")
    except Exception:
        pass
    return ""


@app.post("/extract/clauses/{doc_id}")
async def extract_clauses(doc_id: str):
    """Extract structured clauses from a document using LLM."""
    text = _get_doc_text(doc_id)
    if not text:
        raise HTTPException(status_code=404, detail="Document text not available")

    prompt = f"""You are an expert legal analyst for the Government of Kerala Finance Department.
Extract all clauses from the following Government Order or circular.
Return a JSON array where each item has:
  - "clause_number": clause or section number (e.g. "1", "2(a)", "Para 3")
  - "clause_type": one of ["operative", "recital", "definition", "condition", "penalty", "directive"]
  - "clause_text": the full text of the clause
  - "page_reference": estimated page number if visible in text
  - "key_entities": list of mentioned officers, positions, or departments
  - "references_go": list of any GO numbers referenced in this clause

DOCUMENT TEXT (first 3000 chars):
{text[:3000]}

Return ONLY valid JSON array, no markdown:"""

    raw = _call_llm(prompt)

    # Try to extract JSON from response
    try:
        # Find JSON array in response
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        clauses = json.loads(match.group()) if match else []
    except Exception:
        clauses = []

    return {
        "doc_id": doc_id,
        "clauses": clauses,
        "clause_count": len(clauses),
        "source_label": f"Extracted from document {doc_id}",
        "model_used": OLLAMA_MODEL,
        "confidence": "MEDIUM" if clauses else "LOW",
    }


@app.post("/extract/figures/{doc_id}")
async def extract_figures(doc_id: str):
    """Extract financial figures, amounts, percentages, and dates."""
    text = _get_doc_text(doc_id)
    if not text:
        raise HTTPException(status_code=404, detail="Document text not available")

    prompt = f"""You are a financial analyst for the Government of Kerala.
Extract all financial figures, monetary amounts, percentages, rates, and key dates from this document.
Return a JSON array where each item has:
  - "figure_type": one of ["amount", "percentage", "rate", "date", "gst_rate", "budget_allocation", "da_rate"]
  - "value": the actual value (e.g. "₹45,000", "12%", "2024-04-01")
  - "description": what this figure represents
  - "context": the sentence where this figure appears
  - "page_reference": page number if visible

DOCUMENT TEXT:
{text[:3000]}

Return ONLY valid JSON array:"""

    raw = _call_llm(prompt)
    try:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        figures = json.loads(match.group()) if match else []
    except Exception:
        figures = []

    return {
        "doc_id": doc_id,
        "figures": figures,
        "figure_count": len(figures),
        "source_label": f"Extracted from document {doc_id}",
        "model_used": OLLAMA_MODEL,
    }


@app.post("/extract/full/{doc_id}")
async def full_extraction(doc_id: str):
    """Full extraction: clauses + figures + named entities + referenced GOs."""
    clauses_resp = await extract_clauses(doc_id)
    figures_resp = await extract_figures(doc_id)
    return {
        "doc_id": doc_id,
        "clauses": clauses_resp["clauses"],
        "figures": figures_resp["figures"],
        "clause_count": clauses_resp["clause_count"],
        "figure_count": figures_resp["figure_count"],
        "source_label": f"Full extraction from document {doc_id}",
    }


@app.get("/extract/tables/{doc_id}")
async def extract_tables(doc_id: str):
    """Return pre-extracted tables stored during ingestion."""
    # Tables are stored as part of the raw metadata during ingestion
    return {"doc_id": doc_id, "tables": [], "message": "Tables extracted during ingestion. Check ingestion result."}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "extraction"}
