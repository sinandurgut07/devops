import pytest

from app.exceptions import (
    DuplicateTaskError,
    InvalidTaskError,
    TaskAlreadyCompletedError,
    TaskNotFoundError,
)
from app.services import TaskService

pytestmark = pytest.mark.unit


@pytest.fixture
def service() -> TaskService:
    return TaskService()


def test_create_strips_title_and_assigns_incrementing_ids(service: TaskService) -> None:
    first = service.create("  market  ")
    second = service.create("fatura")

    assert first.id == 12
    assert first.title == "market"
    assert first.completed is False
    assert second.id == 2
    assert second.title == "fatura"


def test_create_rejects_blank_title(service: TaskService) -> None:
    with pytest.raises(InvalidTaskError):
        service.create("   ")


def test_create_rejects_title_longer_than_80_characters(service: TaskService) -> None:
    with pytest.raises(InvalidTaskError):
        service.create("a" * 81)


def test_create_rejects_duplicate_title_ignoring_case(service: TaskService) -> None:
    service.create("Rapor")

    with pytest.raises(DuplicateTaskError):
        service.create(" rapor ")


def test_list_tasks_filters_by_completed_flag(service: TaskService) -> None:
    open_task = service.create("açık")
    done_task = service.create("bitti")
    service.complete(done_task.id)

    assert service.list_tasks() == [open_task, done_task]
    assert service.list_tasks(completed=False) == [open_task]
    assert service.list_tasks(completed=True) == [done_task]


def test_complete_marks_task_done(service: TaskService) -> None:
    task = service.create("ödev")

    completed = service.complete(task.id)

    assert completed.completed is True
    assert service.list_tasks(completed=True) == [task]


def test_complete_missing_task_raises(service: TaskService) -> None:
    with pytest.raises(TaskNotFoundError):
        service.complete(99)


def test_complete_twice_raises(service: TaskService) -> None:
    task = service.create("ödev")
    service.complete(task.id)

    with pytest.raises(TaskAlreadyCompletedError):
        service.complete(task.id)
