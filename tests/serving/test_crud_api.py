"""Tests for the CRUD write API and the read-only guard."""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from yasched.backending.loading.DatabaseLoader import DatabaseLoader  # noqa: E402
from yasched.serving.api import create_app  # noqa: E402


@pytest.fixture
def writable(tmp_path):
    agenda = tmp_path / "agenda.yaml"
    agenda.write_text("topics:\n  - id: work\n    name: Work\n", encoding="utf-8")
    return agenda, TestClient(create_app(agenda))


def test_read_only_agenda_rejects_writes(teacher_path):
    client = TestClient(create_app(teacher_path))  # uses __file__ includes
    assert client.get("/api/health").json()["readOnly"] is True
    assert client.post("/api/tasks", json={"id": "x", "name": "X"}).status_code == 409
    assert client.delete("/api/topics/teaching").status_code == 409


def test_create_update_delete_cycle(writable):
    agenda, client = writable
    assert client.get("/api/health").json()["readOnly"] is False

    # create
    r = client.post(
        "/api/tasks",
        json={"id": "t1", "name": "Task 1", "topic_ids": ["work"], "attributes": {"priority": 5}},
    )
    assert r.status_code == 200
    tasks = client.get("/api/tasks").json()
    assert tasks[0]["id"] == "t1" and tasks[0]["priority"] == 5

    # update (path id authoritative)
    r = client.put("/api/tasks/t1", json={"name": "Renamed", "attributes": {"priority": 1}})
    assert r.status_code == 200
    assert client.get("/api/tasks").json()[0]["title"] == "Renamed"

    # persisted to disk and reloadable
    db = DatabaseLoader.load(agenda)
    assert db.tasks["t1"].name == "Renamed"

    # delete
    assert client.delete("/api/tasks/t1").status_code == 200
    assert client.get("/api/tasks").json() == []


def test_duplicate_create_conflicts(writable):
    _, client = writable
    client.post("/api/tasks", json={"id": "t1", "name": "A"})
    assert client.post("/api/tasks", json={"id": "t1", "name": "B"}).status_code == 409


def test_create_requires_id(writable):
    _, client = writable
    assert client.post("/api/tasks", json={"name": "no id"}).status_code == 400


def test_delete_missing_is_404(writable):
    _, client = writable
    assert client.delete("/api/tasks/ghost").status_code == 404


def test_unknown_kind_is_404(writable):
    _, client = writable
    assert client.post("/api/widgets", json={"id": "x"}).status_code == 404


def test_meta_lists_selectable_refs(writable):
    _, client = writable
    client.post("/api/events", json={"id": "e1", "name": "E"})
    meta = client.get("/api/meta").json()
    assert {"id": "work", "name": "Work"} in meta["topics"]
    assert any(e["id"] == "e1" for e in meta["events"])


def test_create_in_missing_file_creates_it(tmp_path):
    agenda = tmp_path / "sub" / "new.yaml"
    client = TestClient(create_app(agenda))
    assert client.post("/api/topics", json={"id": "home", "name": "Home"}).status_code == 200
    assert agenda.exists()
    assert DatabaseLoader.load(agenda).topics["home"].name == "Home"
