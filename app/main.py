from fastapi import FastAPI, HTTPException

from app.exceptions import (
    DuplicateTaskError,
    InvalidTaskError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
)
from app.models import Task
from app.schemas import TaskCreate, TaskRead
from app.services import TaskService


def create_app() -> FastAPI:
    service = TaskService()
    app = FastAPI(title="Task API")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/tasks", response_model=TaskRead, status_code=201)
    def create_task(payload: TaskCreate) -> Task:
        try:
            return service.create(payload.title)
        except InvalidTaskError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except DuplicateTaskError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/tasks", response_model=list[TaskRead])
    def list_tasks(completed: bool | None = None) -> list[Task]:
        return service.list_tasks(completed)

    @app.post("/tasks/{task_id}/complete", response_model=TaskRead)
    def complete_task(task_id: int) -> Task:
        try:
            return service.complete(task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except TaskAlreadyCompletedError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return app


app = create_app()
