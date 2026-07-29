"""
Google Tasks wrapper -- full CRUD. Uses the user's default task list ("@default").
"""

DEFAULT_TASKLIST = "@default"


def list_tasks(service, show_completed: bool = False, max_results: int = 50) -> list[dict]:
    resp = service.tasks().list(
        tasklist=DEFAULT_TASKLIST,
        showCompleted=show_completed,
        maxResults=max_results,
    ).execute()
    return [_shape_task(t) for t in resp.get("items", [])]


def get_task(service, task_id: str) -> dict:
    task = service.tasks().get(tasklist=DEFAULT_TASKLIST, task=task_id).execute()
    return _shape_task(task)


def create_task(service, title: str, notes: str | None = None, due: str | None = None) -> dict:
    body = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = due  # RFC3339 timestamp, e.g. "2026-08-01T00:00:00.000Z"

    created = service.tasks().insert(tasklist=DEFAULT_TASKLIST, body=body).execute()
    return _shape_task(created)


def update_task(service, task_id: str, updates: dict) -> dict:
    body = {}
    if "title" in updates and updates["title"] is not None:
        body["title"] = updates["title"]
    if "notes" in updates and updates["notes"] is not None:
        body["notes"] = updates["notes"]
    if "due" in updates and updates["due"] is not None:
        body["due"] = updates["due"]
    if "completed" in updates and updates["completed"] is not None:
        body["status"] = "completed" if updates["completed"] else "needsAction"

    updated = service.tasks().patch(tasklist=DEFAULT_TASKLIST, task=task_id, body=body).execute()
    return _shape_task(updated)


def delete_task(service, task_id: str) -> None:
    service.tasks().delete(tasklist=DEFAULT_TASKLIST, task=task_id).execute()


def _shape_task(task: dict) -> dict:
    return {
        "id": task.get("id"),
        "title": task.get("title", "(untitled)"),
        "notes": task.get("notes"),
        "due": task.get("due"),
        "completed": task.get("status") == "completed",
        "updated": task.get("updated"),
    }