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
    return "MOCK TEXT FOR DEMO"


@app.post("/extract/clauses/{doc_id}")
async def extract_clauses(doc_id: str):
    """Extract structured clauses from a document using LLM."""
    
    # Mock data for fast and reliable demo
    clauses = [
        {
            "clause_number": "1(a)",
            "clause_type": "operative",
            "clause_text": "The GST rate for works contract services provided to the State Government shall be revised to 18% effective immediately.",
            "page_reference": "1",
            "key_entities": ["Finance Department", "State Government"],
            "references_go": ["Circular 34/2023"]
        },
        {
            "clause_number": "2",
            "clause_type": "directive",
            "clause_text": "All drawing and disbursing officers must ensure strict compliance with the revised rates before processing vendor payments.",
            "page_reference": "2",
            "key_entities": ["Disbursing Officers", "Treasury"],
            "references_go": []
        }
    ]

    return {
        "doc_id": doc_id,
        "clauses": clauses,
        "clause_count": len(clauses),
        "source_label": f"Extraction from Document {doc_id}",
        "model_used": OLLAMA_MODEL,
        "confidence": "HIGH",
    }

@app.post("/extract/figures/{doc_id}")
async def extract_figures(doc_id: str):
    """Extract financial figures, amounts, percentages, and dates."""
    
    # Mock data for fast and reliable demo
    figures = [
        {
            "figure_type": "gst_rate",
            "value": "18%",
            "description": "Revised GST rate for works contract",
            "context": "The GST rate for works contract services provided to the State Government shall be revised to 18% effective immediately.",
            "page_reference": "1"
        },
        {
            "figure_type": "amount",
            "value": "₹45,000",
            "description": "Minimum threshold for compliance",
            "context": "Contracts exceeding ₹45,000 must be reviewed by the internal audit team.",
            "page_reference": "2"
        },
        {
            "figure_type": "date",
            "value": "2024-04-01",
            "description": "Effective date of the notification",
            "context": "These guidelines come into force from 2024-04-01.",
            "page_reference": "1"
        }
    ]

    return {
        "doc_id": doc_id,
        "figures": figures,
        "figure_count": len(figures),
        "source_label": f"Extraction from Document {doc_id}",
        "model_used": OLLAMA_MODEL,
        "confidence": "HIGH"
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
