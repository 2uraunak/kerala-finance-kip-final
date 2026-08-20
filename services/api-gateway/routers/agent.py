"""
Policy Note Agent router — agentic multi-step policy-note drafting.
Streams agent thought steps via WebSocket.
"""
import os
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import httpx

from models.user import User
from middleware.auth import require_analyst_or_admin

router = APIRouter()
POLICY_AGENT_URL = os.getenv("POLICY_AGENT_URL", "http://policy-agent-service:8006")


class PolicyNoteRequest(BaseModel):
    subject: str                   # e.g. "Revision of DA for State Government Employees"
    context: str | None = None     # Any additional context
    reference_doc_ids: list[str] = []  # Pre-selected reference documents


@router.post("/draft-policy-note", summary="Draft a policy note using the AI agent")
async def draft_policy_note(
    payload: PolicyNoteRequest,
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Multi-step agentic workflow to draft a policy note:
    1. Retrieve relevant Government Orders on the subject
    2. Verify none of the cited orders are superseded
    3. Extract relevant clauses and financial figures
    4. Cross-reference with budget allocations
    5. Draft policy note in official Kerala government template
    6. Verify all citations are active and accurate
    Returns the full draft with source audit trail and agent thought chain.
    """
    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{POLICY_AGENT_URL}/draft",
            json={
                "subject": payload.subject,
                "context": payload.context,
                "reference_doc_ids": payload.reference_doc_ids,
                "drafted_by": current_user.username,
                "user_role": current_user.role,
            },
        )
    return resp.json()


@router.websocket("/draft-stream")
async def draft_policy_note_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming policy note generation.
    Client receives agent thought steps in real-time as they occur.
    """
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{POLICY_AGENT_URL}/draft-stream",
                json=data,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        await websocket.send_text(line)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
