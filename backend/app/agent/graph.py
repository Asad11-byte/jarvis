from backend.app.routers.events import create_event, list_events
from backend.app.services.gmail_service import draft_email
from backend.app.services.tasks_service import create_task, list_tasks
from backend.app.tools.gmail_tools import read_email
from langgraph.prebuilt import create_react_agent

from langchain_groq import ChatGroq

from app.tools.gmail_tools import *
from app.tools.calendar_tools import *
from app.tools.task_tools import *


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)


agent = create_react_agent(
    llm,
    tools=[
        read_email,
        draft_email,

        list_events,
        create_event,

        list_tasks,
        create_task,
    ],
)