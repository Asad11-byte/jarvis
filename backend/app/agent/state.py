"""
LangGraph state definition.

This file defines the data that flows through the graph.
It is intentionally small so additional fields can be added
later (memory, user preferences, retrieval results, etc.).
"""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared graph state.

    messages:
        Conversation history automatically merged by LangGraph.

    conversation_id:
        Existing conversation UUID from Supabase.
        None indicates a new conversation.

    user_id:
        Current authenticated user.

    tool_results:
        Stores tool outputs for logging/debugging/UI.
    """

    messages: Annotated[list[BaseMessage], add_messages]

    conversation_id: str | None

    user_id: str

    tool_results: list[dict]