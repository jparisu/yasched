"""Tests for the validate, timetable, and graph endpoints."""

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from yasched.serving.api import create_app  # noqa: E402


@pytest.fixture
def client(teacher_path):
    return TestClient(create_app(teacher_path))


def test_validate_endpoint(client):
    body = client.get("/api/validate").json()
    assert body["errorCount"] == 0
    assert set(body) == {"issues", "errorCount", "warningCount"}


def test_timetable_only_weekly_events(client):
    entries = client.get("/api/timetable").json()
    assert entries, "expected weekly timetable entries"
    for e in entries:
        assert 0 <= e["weekday"] <= 6
        assert set(e) >= {"eventId", "title", "weekday", "startTime", "endTime", "topicId", "style"}
    # the weekly math101 lecture recurs Mon+Wed -> two entries
    lecture = [e for e in entries if e["eventId"] == "math101-lecture"]
    assert {e["weekday"] for e in lecture} == {0, 2}


def test_graph_structure(client):
    g = client.get("/api/graph").json()
    assert {"topics", "nodes", "edges", "topicEdges"} <= set(g)
    kinds = {n["kind"] for n in g["nodes"]}
    assert kinds == {"task", "event"}
    types = {e["type"] for e in g["edges"]}
    # relations + subtask + event_link all present in the teacher example
    assert {"requires", "needs", "subtask", "event_link"} <= types
    # multi-parent topic edge present (thesis-supervision -> teaching/research)
    assert any(edge["source"] == "thesis-supervision" for edge in g["topicEdges"])


def test_graph_nodes_reference_topics(client):
    g = client.get("/api/graph").json()
    topic_ids = {t["id"] for t in g["topics"]} | {None}
    assert all(n["topicId"] in topic_ids for n in g["nodes"])
