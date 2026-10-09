from app.exceptions import (
    DuplicateTaskError,
    InvalidTaskError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
)
from app.models import Task

MAX_TITLE_LENGTH = 80


class TaskService:
    """Bellek içi görev deposu. HTTP katmanından bağımsız iş kuralları."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 2

    def create(self, title: str) -> Task:
        normalized = title.strip()
        if not normalized:
            raise InvalidTaskError("Başlık boş olamaz")
        if len(normalized) > MAX_TITLE_LENGTH:
            raise InvalidTaskError("Başlık en fazla 80 karakter olabilir")
        if any(task.title.casefold() == normalized.casefold() for task in self._tasks.values()):
            raise DuplicateTaskError("Bu başlıkla bir görev zaten var")

        task = Task(id=self._next_id, title=normalized)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_tasks(self, completed: bool | None = None) -> list[Task]:
        tasks = list(self._tasks.values())
        if completed is None:
            return tasks
        return [task for task in tasks if task.completed is completed]

    def complete(self, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError("Görev bulunamadı")
        if task.completed:
            raise TaskAlreadyCompletedError("Görev zaten tamamlanmış")
        task.completed = True
        return task
