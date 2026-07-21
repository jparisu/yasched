"""Tests for coring entity + layout + schedule data holders."""

from yasched.coring import (
    Event,
    Layout,
    MonthlySchedule,
    Task,
    Topic,
    Trait,
    WeeklySchedule,
)
from yasched.coring._shared import Weekday
from yasched.coring.Layout import Background
from yasched.utilizing.coloring.Color import Color


def test_topic_defaults():
    t = Topic(id="x", name="X")
    assert t.tags == []
    assert t.parent_ids == []
    assert t.traits == []
    assert t.attributes == {}
    assert t.layout is None


def test_task_and_event_defaults():
    task = Task(id="t", name="T")
    assert task.topic_ids == []
    assert task.schedules == []
    assert task.relations == []
    assert task.event_links == []

    event = Event(id="e", name="E")
    assert event.parent_id is None
    assert event.schedules == []


def test_layout_is_empty():
    assert Layout().is_empty()
    non_empty = Layout(backgrounds=[Background(type="solid", color=Color.from_hex("#fff"))])
    assert not non_empty.is_empty()


def test_trait_holds_bags():
    tr = Trait(name="hard", attributes={"difficulty": "hard"}, layout=Layout())
    assert tr.attributes["difficulty"] == "hard"


def test_schedule_fields():
    ws = WeeklySchedule(week_days=(Weekday.MONDAY, Weekday.FRIDAY))
    assert ws.week_days == (Weekday.MONDAY, Weekday.FRIDAY)
    ms = MonthlySchedule(day=15)
    assert ms.day == 15
