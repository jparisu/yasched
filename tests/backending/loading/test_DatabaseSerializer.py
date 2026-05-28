"""Tests for DatabaseSerializer: Database → dict / YAML string."""

from __future__ import annotations

import datetime

from yasched.backending.Database import Database
from yasched.backending.loading.DatabaseSerializer import DatabaseSerializer
from yasched.coring._shared import EventLink, TaskStatus
from yasched.coring.Event import Event
from yasched.coring.Layout import BackgroundStyle, Layout
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic


def _empty_db():
    return Database(layouts=[], topics=[], events=[], tasks=[])


# ---------------------------------------------------------------------------
# serialize — structure
# ---------------------------------------------------------------------------


def test_serialize_empty_db():
    result = DatabaseSerializer.serialize(_empty_db())
    assert isinstance(result, dict)
    assert result.get("topics", []) == []
    assert result.get("events", []) == []
    assert result.get("tasks", []) == []
    assert result.get("layouts", []) == []


def test_serialize_topic_minimal():
    db = Database(layouts=[], topics=[Topic(id="t1", name="T1")], events=[], tasks=[])
    result = DatabaseSerializer.serialize(db)
    topics = result["topics"]
    assert len(topics) == 1
    assert topics[0]["id"] == "t1"
    assert topics[0]["name"] == "T1"


def test_serialize_topic_with_parents():
    db = Database(
        layouts=[],
        topics=[Topic(id="child", name="Child", parent_ids=["parent"])],
        events=[],
        tasks=[],
    )
    result = DatabaseSerializer.serialize(db)
    topic = result["topics"][0]
    assert topic["parents"] == ["parent"]


def test_serialize_layout_with_background():
    from yasched.utilizing.coloring.Color import Color

    bg = BackgroundStyle(type="solid", color=Color.from_name("blue"))
    layout = Layout(id="l1", background=bg)
    db = Database(layouts=[layout], topics=[], events=[], tasks=[])
    result = DatabaseSerializer.serialize(db)
    assert len(result["layouts"]) == 1
    assert result["layouts"][0]["id"] == "l1"


def test_serialize_event():
    sched = SingleDaySchedule(day=datetime.date(2026, 1, 15), start_time=datetime.time(9))
    event = Event(id="e1", topic_id="t1", name="Exam", schedules=[sched])
    db = Database(layouts=[], topics=[], events=[event], tasks=[])
    result = DatabaseSerializer.serialize(db)
    ev = result["events"][0]
    assert ev["id"] == "e1"
    assert ev["topic"] == "t1"


def test_serialize_task_status():
    task = Task(id="t1", name="N", topic_id="tp", status=TaskStatus.DONE)
    db = Database(layouts=[], topics=[], events=[], tasks=[task])
    result = DatabaseSerializer.serialize(db)
    assert result["tasks"][0]["status"] == "done"


def test_serialize_event_link_shorthand():
    link = EventLink(event_id="e1", use_as_deadline=True, as_context=True)
    task = Task(id="t1", name="N", topic_id="tp", event_links=[link])
    db = Database(layouts=[], topics=[], events=[], tasks=[task])
    result = DatabaseSerializer.serialize(db)
    ev_links = result["tasks"][0]["events"]
    assert "e1" in ev_links  # shorthand: bare string


def test_to_yaml_returns_string():
    result = DatabaseSerializer.to_yaml(_empty_db())
    assert isinstance(result, str)


def test_to_yaml_is_valid_yaml():
    import yaml

    db = Database(layouts=[], topics=[Topic(id="t1", name="T1")], events=[], tasks=[])
    content = DatabaseSerializer.to_yaml(db)
    parsed = yaml.safe_load(content)
    assert "topics" in parsed
