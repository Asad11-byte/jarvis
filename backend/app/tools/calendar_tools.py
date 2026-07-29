"""
LangGraph Calendar tools.

Thin wrappers around calendar_service.py.
"""

from langchain_core.tools import tool

from app.services import calendar_service


@tool
def list_events(
    calendar_service_client,
    time_min: str | None = None,
    time_max: str | None = None,
    max_results: int = 20,
):
    """
    List calendar events.
    """

    return calendar_service.list_events(
        service=calendar_service_client,
        time_min=time_min,
        time_max=time_max,
        max_results=max_results,
    )


@tool
def create_event(
    calendar_service_client,
    summary: str,
    start: str,
    end: str,
    description: str | None = None,
    location: str | None = None,
    attendees: list[str] | None = None,
    timezone: str | None = None,
):
    """
    Create a calendar event.
    """

    return calendar_service.create_event(
        service=calendar_service_client,
        summary=summary,
        start=start,
        end=end,
        description=description,
        location=location,
        attendees=attendees,
        timezone=timezone,
    )


@tool
def update_event(
    calendar_service_client,
    event_id: str,
    updates: dict,
):
    """
    Update a calendar event.
    """

    return calendar_service.update_event(
        service=calendar_service_client,
        event_id=event_id,
        updates=updates,
    )


@tool
def delete_event(
    calendar_service_client,
    event_id: str,
):
    """
    Delete a calendar event.
    """

    calendar_service.delete_event(
        service=calendar_service_client,
        event_id=event_id,
    )

    return {
        "success": True,
        "event_id": event_id,
    }