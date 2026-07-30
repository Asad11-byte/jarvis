"""
LangGraph Gmail tools.

build_gmail_tools(service) closes over an already-authenticated Gmail API
service client for the CURRENT request's user. This keeps the client out
of the tool's JSON schema entirely -- the LLM never sees it, is never
asked to supply it, and can never substitute a different one. That's what
prevents one user's chat turn from ever touching another user's mailbox.

IMPORTANT: this module never sends email. Only Gmail drafts are supported.
"""
from langchain_core.tools import tool

from app.services import gmail_service as gmail_service_module


def build_gmail_tools(service):
    @tool
    def list_recent_emails(max_results: int = 10, query: str | None = None):
        """List recent Gmail messages. Returns id, subject, from, date, snippet, unread."""
        return gmail_service_module.list_messages(service=service, max_results=max_results, query=query)

    @tool
    def get_email(message_id: str):
        """Read the full content (including body) of one Gmail message by its id."""
        return gmail_service_module.get_message(service=service, message_id=message_id)

    @tool
    def create_email_draft(
        to: str,
        subject: str,
        body: str,
        thread_id: str | None = None,
        in_reply_to_message_id: str | None = None,
    ):
        """
        Create a Gmail DRAFT. This tool NEVER sends email -- it only saves
        a draft in the user's mailbox for them to review and send themselves.
        """
        return gmail_service_module.draft_email(
            service=service,
            to=to,
            subject=subject,
            body=body,
            thread_id=thread_id,
            in_reply_to_message_id=in_reply_to_message_id,
        )

    return [list_recent_emails, get_email, create_email_draft]