"""
LangGraph Calendar tools.

Built via build_calendar_tools(service) -- see gmail_tools.py for why the
service client is closed over rather than exposed as a visible tool arg.
"""
from langchain_core.tools import tool

from app.services import calendar_service as calendar_service_module


def build_calendar_tools(service):
    @tool
    def list_events(time_min: str | None = None, time_max: str | None = None, max_results: int = 20):
        """List calendar events. time_min/time_max are RFC3339 timestamps, e.g. 2026-08-01T00:00:00Z."""
        return calendar_service_module.list_events(
            service=service, time_min=time_min, time_max=time_max, max_results=max_results,
        )

    @tool
    def create_event(
        summary: str,
        start: str,
        end: str,
        description: str | None = None,
        location: str | None = None,
        attendees: list[str] | None = None,
        timezone: str | None = None,
    ):
        """Create a calendar event. start/end are RFC3339 timestamps, e.g. 2026-08-01T09:00:00."""
        return calendar_service_module.create_event(
            service=service, summary=summary, start=start, end=end,
            description=description, location=location, attendees=attendees, timezone=timezone,
        )

    @tool
    def update_event(event_id: str, updates: dict):
        """
        Update a calendar event. `updates` may include any of: summary,
        description, location, start, end, timezone, attendees (list of emails).
        Only include the keys that should change.
        """
        return calendar_service_module.update_event(service=service, event_id=event_id, updates=updates)

    @tool
    def delete_event(event_id: str):
        """Delete a calendar event by id."""
        calendar_service_module.delete_event(service=service, event_id=event_id)
        return {"success": True, "event_id": event_id}

    return [list_events, create_event, update_event, delete_event]