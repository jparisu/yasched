"""Smoke tests for the FastAPI app (requires fastapi + httpx from dev deps)."""

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")

from yasched.serving.api import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    agenda = tmp_path / "db.yaml"
    agenda.write_text(
        "elements:\n"
        "  - id: AllTopic\n    type: topic\n"
        "  - id: work\n    type: topic\n    directParents: [AllTopic]\n"
        "  - id: t\n    type: task\n    directParents: [work]\n"
        "    attributes: {name: T, priority: 5}\n",
        encoding="utf-8",
    )
    return fastapi_testclient.TestClient(create_app(agenda))


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"


def test_meta_counts(client):
    body = client.get("/api/meta").json()
    assert body["counts"]["tasks"] == 1
    assert body["counts"]["topics"] == 2


def test_elements_payload(client):
    body = client.get("/api/elements").json()
    ids = {e["id"] for e in body["elements"]}
    assert {"t", "work", "AllTopic"} <= ids


def test_crud_and_promotion_cycle(client):
    created = client.post(
        "/api/elements", json={"id": "n", "type": "task", "attributes": {"name": "N"}}
    )
    assert created.status_code == 200
    assert client.post("/api/elements", json={"id": "n", "type": "task"}).status_code == 409

    updated = client.put("/api/elements/n", json={"type": "task", "attributes": {"name": "N2"}})
    assert updated.status_code == 200
    assert client.get("/api/elements/n").json()["attributes"]["name"] == "N2"

    assert client.delete("/api/elements/n").status_code == 200
    assert client.get("/api/elements/n").status_code == 404


def test_validate_endpoint(client):
    assert client.get("/api/validate").json()["errorCount"] == 0
