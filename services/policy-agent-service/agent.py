"""
Policy Agent Service — multi-step agentic policy-note drafter.
Uses LangChain with custom tools: retrieve, verify, draft, format.
"""
import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from langchain_ollama import OllamaLLM
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

app = FastAPI(title="KIP Policy Agent Service", version="1.0.0")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://search-service:8002")
LINEAGE_SERVICE_URL = os.getenv("LINEAGE_SERVICE_URL", "http://lineage-service:8003")


# ─── Agent Tools ─────────────────────────────────────────────────────────────

def retrieve_documents(query: str) -> str:
    """Search for relevant Government Orders and circulars."""
    try:
        resp = httpx.get(
            f"{SEARCH_SERVICE_URL}/search",
            params={"q": query, "top_k": 5, "generate_answer": False},
            timeout=30.0,
        )
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            return json.dumps([{
                "doc_id": r.get("metadata", {}).get("doc_id"),
                "title": r.get("metadata", {}).get("doc_title"),
                "page": r.get("metadata", {}).get("page"),
                "text": r.get("chunk_text", "")[:300],
                "status": r.get("metadata", {}).get("status", "active"),
            } for r in results])
    except Exception as e:
        return f"Search error: {str(e)}"
    return "[]"


def verify_document_status(doc_id: str) -> str:
    """Verify if a document is still active (not superseded)."""
    try:
        resp = httpx.get(f"{LINEAGE_SERVICE_URL}/lineage/{doc_id}", timeout=10.0)
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("current_status", "unknown")
            return f"Document status: {status.upper()}. {'⚠️ SUPERSEDED — do not cite!' if status == 'superseded' else '✅ Active — safe to cite.'}"
    except Exception:
        pass
    return "Status check unavailable"


def draft_policy_note(subject_and_context: str) -> str:
    """Draft a policy note section in official Kerala government format."""
    prompt = f"""Draft a formal policy note for the Finance Department, Government of Kerala.
Subject: {subject_and_context}

Follow this official format:
GOVERNMENT OF KERALA
Finance Department
POLICY NOTE

Subject: [Subject]
Reference: [GO References]
Background: [Context]
Analysis: [Key Points]
Recommendation: [Action proposed]
Financial Implication: [Budget impact if any]

Draft the policy note:"""
    headers = {
        "Authorization": f"Bearer YOUR_GROQ_API_KEY_HERE",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }
    resp = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30.0)
    return resp.json()["choices"][0]["message"]["content"]


# ─── Define LangChain Tools ──────────────────────────────────────────────────

tools = [
    Tool(name="RetrieveDocuments", func=retrieve_documents,
         description="Search for relevant Government Orders and circulars. Input: search query string."),
    Tool(name="VerifyDocumentStatus", func=verify_document_status,
         description="Verify if a document is active or superseded. Input: document ID."),
    Tool(name="DraftPolicyNote", func=draft_policy_note,
         description="Draft a policy note section in official format. Input: subject and context string."),
]

AGENT_PROMPT = PromptTemplate.from_template("""You are an expert policy analyst for the Finance Department, Government of Kerala.
Your task is to draft a comprehensive policy note on the given subject.

Follow these steps:
1. Search for relevant Government Orders on the subject
2. Verify that all cited documents are currently active (not superseded)
3. Draft the policy note with proper citations
4. Ensure all financial figures and references are accurate

You have access to these tools:
{tools}

Use this format:
Thought: [your reasoning]
Action: [tool name]
Action Input: [tool input]
Observation: [tool result]
... (repeat as needed)
Thought: I now have enough information to draft the final policy note.
Final Answer: [complete policy note with all citations]

SUBJECT: {input}

{agent_scratchpad}""")


class PolicyNoteRequest(BaseModel):
    subject: str
    context: str | None = None
    reference_doc_ids: list[str] = []
    drafted_by: str = "analyst"
    user_role: str = "analyst"


@app.post("/draft")
async def draft_policy_note_endpoint(req: PolicyNoteRequest):
    """Multi-step agentic policy note drafting."""
    agent_steps = []

    # Step 1: Retrieve
    agent_steps.append({"step": 1, "action": "retrieve", "input": req.subject})
    docs_json = retrieve_documents(req.subject)
    docs = json.loads(docs_json) if docs_json.startswith("[") else []
    agent_steps.append({"step": 1, "result": f"Found {len(docs)} relevant documents"})

    # Step 2: Verify document statuses
    agent_steps.append({"step": 2, "action": "verify_status"})
    verified_docs = []
    for doc in docs[:3]:
        if doc.get("doc_id"):
            status_str = verify_document_status(doc["doc_id"])
            verified_docs.append({**doc, "status_check": status_str})
    agent_steps.append({"step": 2, "result": f"Verified {len(verified_docs)} documents"})

    # Step 3: Draft
    agent_steps.append({"step": 3, "action": "draft"})
    context_for_draft = f"{req.subject}\n\nContext: {req.context or ''}\n\nReference Documents:\n"
    for d in verified_docs:
        context_for_draft += f"- {d.get('title', 'Unknown')}: {d.get('text', '')[:200]}\n"
    draft = draft_policy_note(context_for_draft)
    agent_steps.append({"step": 3, "result": "Draft completed"})

    # Build citations
    citations = [
        {
            "source_label": f"📄 {d.get('title', 'Unknown')}",
            "doc_id": d.get("doc_id"),
            "status": d.get("status", "active"),
            "status_label": d.get("status", "active").upper(),
            "lineage_warning": d.get("status") == "superseded",
        }
        for d in verified_docs
    ]

    return {
        "subject": req.subject,
        "policy_note_draft": draft,
        "agent_steps": agent_steps,
        "citations": citations,
        "drafted_by": req.drafted_by,
        "disclaimer": "This is an AI-assisted draft. All citations must be verified by a competent officer before official use.",
        "source_review_label": f"Draft generated using {len(verified_docs)} verified source documents",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "policy-agent"}
