"""
Google Calendar wrapper -- full CRUD, operates on the user's primary calendar.
"""


def list_events(service, time_min: str | None = None, time_max: str | None = None, max_results: int = 20) -> list[dict]:
    kwargs = {
        "calendarId": "primary",
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime",
    }
    if time_min:
        kwargs["timeMin"] = time_min
    if time_max:
        kwargs["timeMax"] = time_max

    resp = service.events().list(**kwargs).execute()
    return [_shape_event(e) for e in resp.get("items", [])]


def get_event(service, event_id: str) -> dict:
    event = service.events().get(calendarId="primary", eventId=event_id).execute()
    return _shape_event(event)


def create_event(
    service,
    summary: str,
    start: str,
    end: str,
    description: str | None = None,
    location: str | None = None,
    attendees: list[str] | None = None,
    timezone: str | None = None,
) -> dict:
    body = {
        "summary": summary,
        "start": {"dateTime": start, **({"timeZone": timezone} if timezone else {})},
        "end": {"dateTime": end, **({"timeZone": timezone} if timezone else {})},
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location
    if attendees:
        body["attendees"] = [{"email": a} for a in attendees]

    created = service.events().insert(calendarId="primary", body=body).execute()
    return _shape_event(created)


def update_event(service, event_id: str, updates: dict) -> dict:
    """Partial update (PATCH semantics). `updates` uses the same keys as create_event."""
    body = {}
    if "summary" in updates and updates["summary"] is not None:
        body["summary"] = updates["summary"]
    if "description" in updates and updates["description"] is not None:
        body["description"] = updates["description"]
    if "location" in updates and updates["location"] is not None:
        body["location"] = updates["location"]
    if "start" in updates and updates["start"] is not None:
        body["start"] = {"dateTime": updates["start"]}
        if updates.get("timezone"):
            body["start"]["timeZone"] = updates["timezone"]
    if "end" in updates and updates["end"] is not None:
        body["end"] = {"dateTime": updates["end"]}
        if updates.get("timezone"):
            body["end"]["timeZone"] = updates["timezone"]
    if "attendees" in updates and updates["attendees"] is not None:
        body["attendees"] = [{"email": a} for a in updates["attendees"]]

    updated = service.events().patch(calendarId="primary", eventId=event_id, body=body).execute()
    return _shape_event(updated)


def delete_event(service, event_id: str) -> None:
    service.events().delete(calendarId="primary", eventId=event_id).execute()


def _shape_event(event: dict) -> dict:
    return {
        "id": event.get("id"),
        "summary": event.get("summary", "(no title)"),
        "description": event.get("description"),
        "location": event.get("location"),
        "start": event.get("start", {}).get("dateTime") or event.get("start", {}).get("date"),
        "end": event.get("end", {}).get("dateTime") or event.get("end", {}).get("date"),
        "attendees": [a.get("email") for a in event.get("attendees", [])],
        "html_link": event.get("htmlLink"),
        "status": event.get("status"),
    }