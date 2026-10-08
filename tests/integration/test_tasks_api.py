import pytest

pytestmark = pytest.mark.integration


def test_health(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_task(client) -> None:
    created = client.post("/tasks", json={"title": "  market  "})

    assert created.status_code == 201
    assert created.json() == {"id": 1, "title": "market", "completed": False}

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert listed.json() == [{"id": 1, "title": "market", "completed": False}]


def test_create_rejects_blank_title(client) -> None:
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422
    assert response.json()["detail"] == "Başlık boş olamaz"


def test_create_rejects_too_long_title(client) -> None:
    response = client.post("/tasks", json={"title": "a" * 81})

    assert response.status_code == 422


def test_create_rejects_duplicate_title(client) -> None:
    assert client.post("/tasks", json={"title": "Rapor"}).status_code == 201

    response = client.post("/tasks", json={"title": "rapor"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Bu başlıkla bir görev zaten var"


def test_complete_task(client) -> None:
    client.post("/tasks", json={"title": "ödev"})

    response = client.post("/tasks/1/complete")

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_complete_missing_task(client) -> None:
    response = client.post("/tasks/40/complete")

    assert response.status_code == 404
    assert response.json()["detail"] == "Görev bulunamadı"


def test_complete_twice(client) -> None:
    client.post("/tasks", json={"title": "ödev"})
    client.post("/tasks/1/complete")

    response = client.post("/tasks/1/complete")

    assert response.status_code == 409
    assert response.json()["detail"] == "Görev zaten tamamlanmış"


def test_task_lifecycle_filters_open_and_done(client) -> None:
    client.post("/tasks", json={"title": "açık"})
    client.post("/tasks", json={"title": "bitti"})
    client.post("/tasks/2/complete")

    open_tasks = client.get("/tasks", params={"completed": False})
    done_tasks = client.get("/tasks", params={"completed": True})

    assert open_tasks.json() == [{"id": 1, "title": "açık", "completed": False}]
    assert done_tasks.json() == [{"id": 2, "title": "bitti", "completed": True}]
