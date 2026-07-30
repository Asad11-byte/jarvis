"""
LangGraph agent factory.

build_agent() is called fresh on every /chat request, not built once at
import time. That's deliberate: the tools it returns must be bound to the
CURRENT request's authenticated Google service clients. A shared/global
agent would risk one user's request reaching another user's mailbox --
this is a multi-tenant safety requirement, not a style choice.

The LLM (_llm) holds no per-user state, so that part is safe to build once.
"""
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from app.services.google_clients import gmail_client, calendar_client, tasks_client
from app.tools.gmail_tools import build_gmail_tools
from app.tools.calendar_tools import build_calendar_tools
from app.tools.task_tools import build_task_tools
from app.agent.prompts import SYSTEM_PROMPT

load_dotenv()

_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


def build_agent(credentials):
    """
    credentials: google.oauth2.credentials.Credentials for the CURRENT
    request's user (AuthedUser.credentials from app/deps.py). Fresh Google
    API service clients -- and therefore a fresh tool list -- are built on
    every call so tools can never leak across users.
    """
    gmail_service = gmail_client(credentials)
    calendar_service = calendar_client(credentials)
    tasks_service = tasks_client(credentials)

    tools = [
        *build_gmail_tools(gmail_service),
        *build_calendar_tools(calendar_service),
        *build_task_tools(tasks_service),
    ]

    return create_react_agent(_llm, tools=tools, prompt=SYSTEM_PROMPT)