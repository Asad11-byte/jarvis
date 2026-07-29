"""
LangGraph Google Tasks tools.

Thin wrappers around tasks_service.py.
"""

from langchain_core.tools import tool

from app.services import tasks_service


@tool
def list_tasks(
    tasks_service_client,
    show_completed: bool = False,
    max_results: int = 50,
):
    """
    List Google Tasks.
    """

    return tasks_service.list_tasks(
        service=tasks_service_client,
        show_completed=show_completed,
        max_results=max_results,
    )


@tool
def create_task(
    tasks_service_client,
    title: str,
    notes: str | None = None,
    due: str | None = None,
):
    """
    Create a Google Task.
    """

    return tasks_service.create_task(
        service=tasks_service_client,
        title=title,
        notes=notes,
        due=due,
    )


@tool
def update_task(
    tasks_service_client,
    task_id: str,
    updates: dict,
):
    """
    Update a Google Task.
    """

    return tasks_service.update_task(
        service=tasks_service_client,
        task_id=task_id,
        updates=updates,
    )


@tool
def delete_task(
    tasks_service_client,
    task_id: str,
):
    """
    Delete a Google Task.
    """

    tasks_service.delete_task(
        service=tasks_service_client,
        task_id=task_id,
    )

    return {
        "success": True,
        "task_id": task_id,
    }