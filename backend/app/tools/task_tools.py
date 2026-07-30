"""
LangGraph Google Tasks tools.

Built via build_task_tools(service) -- see gmail_tools.py for why the
service client is closed over rather than exposed as a visible tool arg.
"""
from langchain_core.tools import tool

from app.services import tasks_service as tasks_service_module


def build_task_tools(service):
    @tool
    def list_tasks(show_completed: bool = False, max_results: int = 50):
        """List Google Tasks (to-dos)."""
        return tasks_service_module.list_tasks(service=service, show_completed=show_completed, max_results=max_results)

    @tool
    def create_task(title: str, notes: str | None = None, due: str | None = None):
        """Create a Google Task. `due` is an RFC3339 timestamp, e.g. 2026-08-01T00:00:00.000Z."""
        return tasks_service_module.create_task(service=service, title=title, notes=notes, due=due)

    @tool
    def update_task(task_id: str, updates: dict):
        """
        Update a Google Task. `updates` may include any of: title, notes,
        due, completed (true/false). Only include the keys that should change.
        """
        return tasks_service_module.update_task(service=service, task_id=task_id, updates=updates)

    @tool
    def delete_task(task_id: str):
        """Delete a Google Task by id."""
        tasks_service_module.delete_task(service=service, task_id=task_id)
        return {"success": True, "task_id": task_id}

    return [list_tasks, create_task, update_task, delete_task]