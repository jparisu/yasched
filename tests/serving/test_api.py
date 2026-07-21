"""Tests for the FastAPI app via TestClient (fully local, no network)."""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from yasched.serving.api import create_app  # noqa: E402


@pytest.fixture
def client(teacher_path):
    return TestClient(create_app(teacher_path))


def test_health(client, teacher_path):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["exists"] is True
    assert str(teacher_path) in body["agenda"]


def test_agenda_payload(client):
    r = client.get("/api/agenda")
    assert r.status_code == 200
    body = r.json()
    assert len(body["topics"]) == 7
    assert len(body["tasks"]) == 10
    assert body["events"]


def test_topics_tasks_events_endpoints(client):
    assert len(client.get("/api/topics").json()) == 7
    assert len(client.get("/api/tasks").json()) == 10
    assert isinstance(client.get("/api/events").json(), list)


def test_events_window_query(client):
    r = client.get("/api/events", params={"start": "2026-10-01", "end": "2026-10-31"})
    assert r.status_code == 200
    events = r.json()
    assert all(e["date"].startswith("2026-10") for e in events)


def test_invalid_date_query_returns_400(client):
    r = client.get("/api/events", params={"start": "not-a-date"})
    assert r.status_code == 400


def test_reload(client):
    r = client.post("/api/reload")
    assert r.status_code == 200
    assert r.json()["reloaded"] is True


def test_root_served(client):
    # With a built frontend the SPA index is served; without it, a helpful page.
    r = client.get("/")
    assert r.status_code == 200
    assert "html" in r.headers.get("content-type", "")


def test_missing_agenda_yields_empty_payload(tmp_path):
    app = create_app(tmp_path / "nope.yaml")
    client = TestClient(app)
    body = client.get("/api/agenda").json()
    assert body["topics"] == [] and body["tasks"] == [] and body["events"] == []
