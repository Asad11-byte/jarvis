from fastapi import APIRouter, Depends

from langchain_core.messages import HumanMessage

from app.agent.graph import agent
from app.deps import get_authed_user

router = APIRouter()


@router.post("/chat")
async def chat(
    body: dict,
    authed=Depends(get_authed_user),
):

    credentials = authed.credentials

    question = body["message"]

    response = agent.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ],
            "credentials": credentials,
        }
    )

    return {
        "response": response["messages"][-1].content
    }