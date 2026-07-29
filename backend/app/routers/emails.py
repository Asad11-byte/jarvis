"""
GET  /emails             list recent messages
GET  /emails/{id}        full message detail
POST /emails/draft       create a DRAFT (dev/testing route -- the agent will
                          call gmail_service.draft_email directly in Phase 3;
                          this endpoint exists so you can verify the
                          gmail.compose scope works before the agent exists)
"""
from fastapi import APIRouter, Depends, Query

from app.deps import get_authed_user, AuthedUser
from app.models import EmailDraftCreate
from app.services import gmail_service
from app.services.google_clients import gmail_client

router = APIRouter(tags=["emails"])


@router.get("/emails")
def list_emails(
    max_results: int = Query(20, le=100),
    q: str | None = None,
    authed: AuthedUser = Depends(get_authed_user),
):
    service = gmail_client(authed.credentials)
    return gmail_service.list_messages(service, max_results=max_results, query=q)


@router.get("/emails/{message_id}")
def get_email(message_id: str, authed: AuthedUser = Depends(get_authed_user)):
    service = gmail_client(authed.credentials)
    return gmail_service.get_message(service, message_id)


@router.post("/emails/draft")
def create_email_draft(payload: EmailDraftCreate, authed: AuthedUser = Depends(get_authed_user)):
    service = gmail_client(authed.credentials)
    return gmail_service.draft_email(
        service,
        to=payload.to,
        subject=payload.subject,
        body=payload.body,
        thread_id=payload.thread_id,
        in_reply_to_message_id=payload.in_reply_to_message_id,
    )