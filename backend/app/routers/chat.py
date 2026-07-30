"""
POST /chat

Builds a fresh agent bound to the current user's Google credentials,
loads prior turns for this conversation from Supabase (if conversation_id
is given), runs the turn, and persists both the user message and the
assistant reply.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from app.agent.graph import build_agent
from app.database import supabase
from app.deps import get_authed_user, AuthedUser

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str


def _load_history(conversation_id: str) -> list:
    rows = (
        supabase.table("messages")
        .select("role, content")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .execute()
    ).data

    history = []
    for row in rows:
        if row["role"] == "user":
            history.append(HumanMessage(content=row["content"]))
        elif row["role"] == "assistant":
            history.append(AIMessage(content=row["content"]))
    return history


def _save_message(conversation_id: str, role: str, content: str):
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
    }).execute()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, authed: AuthedUser = Depends(get_authed_user)):
    conversation_id = payload.conversation_id

    if conversation_id:
        existing = (
            supabase.table("conversations")
            .select("id")
            .eq("id", conversation_id)
            .eq("user_id", authed.user_id)
            .execute()
        )
        if not existing.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        history = _load_history(conversation_id)
    else:
        created = supabase.table("conversations").insert({
            "user_id": authed.user_id,
            "title": payload.message[:60],
        }).execute()
        conversation_id = created.data[0]["id"]
        history = []

    _save_message(conversation_id, "user", payload.message)

    agent = build_agent(authed.credentials)
    result = agent.invoke({"messages": [*history, HumanMessage(content=payload.message)]})
    reply_text = result["messages"][-1].content

    _save_message(conversation_id, "assistant", reply_text)

    return ChatResponse(conversation_id=conversation_id, response=reply_text)