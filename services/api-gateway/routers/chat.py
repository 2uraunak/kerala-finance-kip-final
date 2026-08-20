"""
Conversational Chat router — multi-turn document Q&A.
"""
import os
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import httpx

from models.user import User
from middleware.auth import require_any_role

router = APIRouter()
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://search-service:8002")


class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []   # Previous turns: [{"role": "user/assistant", "content": "..."}]
    doc_ids: list[str] = []    # Optional: restrict chat to specific documents


@router.post("/", summary="Send a chat message with document context")
async def chat(
    payload: ChatMessage,
    current_user: User = Depends(require_any_role),
):
    """
    Multi-turn conversational Q&A grounded in the document knowledge base.
    Returns:
    - Assistant response
    - Source citations for every claim (document, page, clause)
    - Confidence score
    - Lineage warnings (if citing a superseded document)
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{SEARCH_SERVICE_URL}/chat",
            json={
                "message": payload.message,
                "history": payload.history,
                "doc_ids": payload.doc_ids,
                "user_role": current_user.role,
                "include_restricted": current_user.role == "admin",
            },
        )
    return resp.json()


@router.websocket("/stream")
async def chat_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming chat responses token by token."""
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{SEARCH_SERVICE_URL}/chat-stream", json=data) as resp:
                async for chunk in resp.aiter_text():
                    if chunk:
                        await websocket.send_text(chunk)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
