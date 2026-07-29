"""
Gmail wrapper.

HARD CONSTRAINT: this file must never call users().messages().send() or
users().drafts().send(). Drafting only -- draft_email() below uses
users().drafts().create(), which creates a draft in the mailbox for the
user to review and send themselves. This is enforced both here (no send
code exists) and at the OAuth scope level (gmail.compose cannot send).
"""
import base64
from email.mime.text import MIMEText


def list_messages(service, max_results: int = 20, query: str | None = None) -> list[dict]:
    """Returns lightweight summaries: id, subject, from, date, snippet."""
    list_kwargs = {"userId": "me", "maxResults": max_results}
    if query:
        list_kwargs["q"] = query

    resp = service.users().messages().list(**list_kwargs).execute()
    message_refs = resp.get("messages", [])

    summaries = []
    for ref in message_refs:
        msg = service.users().messages().get(
            userId="me",
            id=ref["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        summaries.append({
            "id": msg["id"],
            "thread_id": msg.get("threadId"),
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
            "unread": "UNREAD" in msg.get("labelIds", []),
        })
    return summaries


def get_message(service, message_id: str) -> dict:
    """Full detail for one message, including a best-effort plain-text body."""
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    return {
        "id": msg["id"],
        "thread_id": msg.get("threadId"),
        "subject": headers.get("Subject", "(no subject)"),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "date": headers.get("Date", ""),
        "snippet": msg.get("snippet", ""),
        "body": _extract_plain_text(msg.get("payload", {})),
    }


def _extract_plain_text(payload: dict) -> str:
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    for part in payload.get("parts", []) or []:
        text = _extract_plain_text(part)
        if text:
            return text
    return ""


def draft_email(
    service,
    to: str,
    subject: str,
    body: str,
    thread_id: str | None = None,
    in_reply_to_message_id: str | None = None,
) -> dict:
    """
    Creates a DRAFT only. Never calls send. If thread_id/in_reply_to_message_id
    are provided, the draft is created as a reply within that thread.
    """
    mime_message = MIMEText(body)
    mime_message["to"] = to
    mime_message["subject"] = subject
    if in_reply_to_message_id:
        mime_message["In-Reply-To"] = in_reply_to_message_id
        mime_message["References"] = in_reply_to_message_id

    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

    draft_body = {"message": {"raw": raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    created = service.users().drafts().create(userId="me", body=draft_body).execute()
    return {
        "draft_id": created["id"],
        "message_id": created["message"]["id"],
        "thread_id": created["message"].get("threadId"),
    }