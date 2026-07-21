"""Tests for the view layer (resolved model -> frontend DTOs)."""

import datetime

from yasched.serving.views import build_payload


def test_payload_shape(teacher_db):
    p = build_payload(teacher_db)
    assert set(p) >= {"topics", "tasks", "events", "deadlines", "window"}
    assert len(p["topics"]) == 7
    assert len(p["tasks"]) == 10
    assert p["events"], "expected some event occurrences in the default window"


def test_task_priority_and_status_mapping(teacher_db):
    p = build_payload(teacher_db)
    by_id = {t["id"]: t for t in p["tasks"]}
    # priority is emitted as the raw numeric value (bucketing happens in the UI)
    assert by_id["grade-midterm"]["priority"] == 5
    # status done -> done ; in-progress -> doing
    assert by_id["write-syllabus"]["status"] == "done"
    assert by_id["prepare-math101"]["status"] == "doing"


def test_task_topic_and_deadline(teacher_db):
    p = build_payload(teacher_db)
    by_id = {t["id"]: t for t in p["tasks"]}
    assert by_id["submit-grades"]["topicId"] == "math-101"  # first of multi-topic
    assert by_id["grade-midterm"]["deadline"] == "2026-10-27"


def test_style_shape(teacher_db):
    p = build_payload(teacher_db)
    style = p["topics"][0]["style"]
    assert set(style) == {"backgroundColor", "leftColor", "shape"}
    assert style["leftColor"].startswith("#")
    assert style["backgroundColor"].startswith("rgba(")


def test_deadlines_derived_from_tasks(teacher_db):
    p = build_payload(teacher_db)
    ids = {d["id"] for d in p["deadlines"]}
    assert "grade-midterm::deadline" in ids
    # a task without a deadline attribute produces no deadline entry
    assert "make-slides::deadline" not in ids


def test_recurring_flag(teacher_db):
    p = build_payload(teacher_db)
    lectures = [e for e in p["events"] if e["title"] == "Math 101 Lecture"]
    assert lectures and all(e["recurring"] for e in lectures)


def test_window_query(teacher_db):
    start = datetime.date(2026, 10, 1)
    end = datetime.date(2026, 10, 31)
    p = build_payload(teacher_db, start, end)
    assert p["window"] == {"start": "2026-10-01", "end": "2026-10-31"}
    assert any("midterm-exam" in e["id"] for e in p["events"])
    # events outside the window are excluded
    assert all("2026-10" in e["date"] for e in p["events"])
