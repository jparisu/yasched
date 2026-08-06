"""Tests for the pure view/DTO layer (no FastAPI)."""

import datetime

from yasched.serving.views import build_payload

WINDOW = (datetime.date(2026, 9, 1), datetime.date(2026, 10, 31))


def test_payload_shape(example_db):
    payload = build_payload(example_db, *WINDOW)
    assert set(payload) == {"window", "definitions", "elements"}
    assert payload["window"]["start"] == "2026-09-01"
    assert any(d["name"] == "effort" and not d["builtin"] for d in payload["definitions"])


def test_payload_includes_virtual_occurrences(example_db):
    payload = build_payload(example_db, *WINDOW)
    ids = {e["id"] for e in payload["elements"]}
    assert any(i.startswith("math-101-lecture#") for i in ids)  # generated lectures present
    virtual = [e for e in payload["elements"] if e["virtual"]]
    assert virtual, "expected generated virtual elements"


def test_connections_surface_on_both_endpoints(example_db):
    payload = build_payload(example_db, *WINDOW)
    by_id = {e["id"]: e for e in payload["elements"]}
    # write-paper --follows--> department-review
    assert {"to": "department-review", "relation": "follows"} in by_id["write-paper"]["connections"]
    assert {"from": "write-paper", "relation": "follows"} in by_id["department-review"]["incoming"]


def test_resolved_layout_included(example_db):
    payload = build_payload(example_db, *WINDOW)
    by_id = {e["id"]: e for e in payload["elements"]}
    # grade-midterm has danger=true -> red border via attribute-layout
    assert by_id["grade-midterm"]["layout"]["border"]["color"] == "#ef4444"
