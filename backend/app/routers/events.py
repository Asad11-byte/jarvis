from fastapi import APIRouter, Depends, Query

from app.deps import get_authed_user, AuthedUser
from app.models import EventCreate, EventUpdate
from app.services import calendar_service
from app.services.google_clients import calendar_client

router = APIRouter(tags=["calendar"])


@router.get("/events")
def list_events(
    time_min: str | None = Query(None, description="RFC3339 lower bound, e.g. 2026-08-01T00:00:00Z"),
    time_max: str | None = Query(None, description="RFC3339 upper bound"),
    max_results: int = Query(20, le=100),
    authed: AuthedUser = Depends(get_authed_user),
):
    service = calendar_client(authed.credentials)
    return calendar_service.list_events(service, time_min=time_min, time_max=time_max, max_results=max_results)


@router.get("/events/{event_id}")
def get_event(event_id: str, authed: AuthedUser = Depends(get_authed_user)):
    service = calendar_client(authed.credentials)
    return calendar_service.get_event(service, event_id)


@router.post("/events")
def create_event(payload: EventCreate, authed: AuthedUser = Depends(get_authed_user)):
    service = calendar_client(authed.credentials)
    return calendar_service.create_event(
        service,
        summary=payload.summary,
        start=payload.start,
        end=payload.end,
        description=payload.description,
        location=payload.location,
        attendees=payload.attendees,
        timezone=payload.timezone,
    )


@router.patch("/events/{event_id}")
def update_event(event_id: str, payload: EventUpdate, authed: AuthedUser = Depends(get_authed_user)):
    service = calendar_client(authed.credentials)
    return calendar_service.update_event(service, event_id, payload.model_dump())


@router.delete("/events/{event_id}")
def delete_event(event_id: str, authed: AuthedUser = Depends(get_authed_user)):
    service = calendar_client(authed.credentials)
    calendar_service.delete_event(service, event_id)
    return {"ok": True, "deleted_id": event_id}