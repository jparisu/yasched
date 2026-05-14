"""Tests for coring.Event."""

import datetime

import pytest

from yasched.coring.Event import Event
from yasched.coring.Layout import IconStyle, Layout
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring._shared import Weekday, WeeklyAppointment
from yasched.utilizing.timing.Duration import Duration


def _single_day(year: int = 2026, month: int = 6, day: int = 15) -> SingleDaySchedule:
    return SingleDaySchedule(day=datetime.date(year, month, day))


def _weekly_appt() -> WeeklyAppointment:
    return WeeklyAppointment(
        week_day=Weekday.MONDAY,
        start_time=datetime.time(9),
        duration=Duration.from_string("1h"),
    )


# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_event_minimal():
    e = Event(id="e1", topic_id="math", name="Lecture", schedules=[_single_day()])
    assert e.id == "e1"
    assert e.topic_id == "math"
    assert e.name == "Lecture"
    assert e.description is None
    assert e.location is None
    assert e.layout is None
    assert e.blocking_level is None


def test_event_full_fields():
    schedule = _single_day()
    layout = Layout(icon=IconStyle(type="emoji", value="📝"))
    e = Event(
        id="exam",
        topic_id="math",
        name="Final Exam",
        description="End of term",
        location="Room 204",
        schedules=[schedule],
        layout=layout,
        blocking_level=2,
    )
    assert e.description == "End of term"
    assert e.location == "Room 204"
    assert e.blocking_level == 2
    assert isinstance(e.layout, Layout)


def test_event_multiple_schedules():
    s1 = _single_day(2026, 6, 1)
    s2 = _single_day(2026, 6, 8)
    e = Event(id="e", topic_id="t", name="N", schedules=[s1, s2])
    assert len(e.schedules) == 2


def test_event_blocking_level_zero():
    e = Event(id="e", topic_id="t", name="N", schedules=[_single_day()], blocking_level=0)
    assert e.blocking_level == 0


def test_event_is_frozen():
    e = Event(id="e", topic_id="t", name="N", schedules=[_single_day()])
    with pytest.raises((AttributeError, TypeError)):
        e.id = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_event_layout_as_string_reference():
    e = Event(id="e", topic_id="t", name="N", schedules=[_single_day()], layout="primary")
    assert e.layout == "primary"


def test_event_weekly_schedule():
    ws = WeeklySchedule(appointments=[_weekly_appt()])
    e = Event(id="lecture", topic_id="math", name="Weekly Lecture", schedules=[ws])
    assert len(e.schedules) == 1
    assert isinstance(e.schedules[0], WeeklySchedule)


def test_event_blocking_level_high_value():
    e = Event(id="e", topic_id="t", name="N", schedules=[_single_day()], blocking_level=999)
    assert e.blocking_level == 999


# ---------------------------------------------------------------------------
# Construction — failure cases
# ---------------------------------------------------------------------------


def test_event_empty_schedules_raises():
    with pytest.raises(ValueError):
        Event(id="e", topic_id="t", name="N", schedules=[])
