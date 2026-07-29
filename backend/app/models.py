from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    avatar_url: str | None = None

# ---- Calendar ----

class EventCreate(BaseModel):
    summary: str
    start: str                     # RFC3339, e.g. "2026-08-01T09:00:00"
    end: str
    description: str | None = None
    location: str | None = None
    attendees: list[str] | None = None
    timezone: str | None = None    # e.g. "Asia/Karachi"


class EventUpdate(BaseModel):
    summary: str | None = None
    start: str | None = None
    end: str | None = None
    description: str | None = None
    location: str | None = None
    attendees: list[str] | None = None
    timezone: str | None = None


# ---- Tasks ----

class TaskCreate(BaseModel):
    title: str
    notes: str | None = None
    due: str | None = None         # RFC3339 timestamp


class TaskUpdate(BaseModel):
    title: str | None = None
    notes: str | None = None
    due: str | None = None
    completed: bool | None = None


# ---- Email (draft-only) ----

class EmailDraftCreate(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: str | None = None
    in_reply_to_message_id: str | None = None