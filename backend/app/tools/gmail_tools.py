"""
LangGraph Gmail tools.

These tools wrap the existing gmail_service.py.
No Google API logic should be duplicated here.

IMPORTANT

This module NEVER sends email.

Only Gmail drafts are supported.
"""

from langchain_core.tools import tool

from app.services import gmail_service


@tool
def list_recent_emails(
    gmail_service_client,
    max_results: int = 10,
    query: str | None = None,
):
    """
    List recent Gmail messages.
    """

    return gmail_service.list_messages(
        service=gmail_service_client,
        max_results=max_results,
        query=query,
    )


@tool
def get_email(
    gmail_service_client,
    message_id: str,
):
    """
    Read a Gmail message.
    """

    return gmail_service.get_message(
        service=gmail_service_client,
        message_id=message_id,
    )


@tool
def create_email_draft(
    gmail_service_client,
    to: str,
    subject: str,
    body: str,
    thread_id: str | None = None,
    in_reply_to_message_id: str | None = None,
):
    """
    Create a Gmail draft.

    This tool NEVER sends email.
    """

    return gmail_service.draft_email(
        service=gmail_service_client,
        to=to,
        subject=subject,
        body=body,
        thread_id=thread_id,
        in_reply_to_message_id=in_reply_to_message_id,
    )