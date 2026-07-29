from fastapi import APIRouter, Depends, Query

from app.deps import get_authed_user, AuthedUser
from app.models import TaskCreate, TaskUpdate
from app.services import tasks_service
from app.services.google_clients import tasks_client

router = APIRouter(tags=["todos"])


@router.get("/todos")
def list_todos(
    show_completed: bool = Query(False),
    max_results: int = Query(50, le=100),
    authed: AuthedUser = Depends(get_authed_user),
):
    service = tasks_client(authed.credentials)
    return tasks_service.list_tasks(service, show_completed=show_completed, max_results=max_results)


@router.get("/todos/{task_id}")
def get_todo(task_id: str, authed: AuthedUser = Depends(get_authed_user)):
    service = tasks_client(authed.credentials)
    return tasks_service.get_task(service, task_id)


@router.post("/todos")
def create_todo(payload: TaskCreate, authed: AuthedUser = Depends(get_authed_user)):
    service = tasks_client(authed.credentials)
    return tasks_service.create_task(service, title=payload.title, notes=payload.notes, due=payload.due)


@router.patch("/todos/{task_id}")
def update_todo(task_id: str, payload: TaskUpdate, authed: AuthedUser = Depends(get_authed_user)):
    service = tasks_client(authed.credentials)
    return tasks_service.update_task(service, task_id, payload.model_dump())


@router.delete("/todos/{task_id}")
def delete_todo(task_id: str, authed: AuthedUser = Depends(get_authed_user)):
    service = tasks_client(authed.credentials)
    tasks_service.delete_task(service, task_id)
    return {"ok": True, "deleted_id": task_id}