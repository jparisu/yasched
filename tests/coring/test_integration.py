"""Integration tests for coring: cross-class composition scenarios."""

import datetime

import pytest

from yasched.coring._shared import (
    BlockedBy,
    EffortRange,
    EventLink,
    TaskStatus,
    Weekday,
    WeeklyAppointment,
)
from yasched.coring.Event import Event
from yasched.coring.Layout import BackgroundStyle, BorderStyle, IconStyle, Layout
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.MultiDaySchedule import MultiDaySchedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.Task import Task
from yasched.coring.Topic import Topic
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring.YearlySchedule import YearlySchedule
from yasched.utilizing.coloring.Color import Color
from yasched.utilizing.timing.Duration import Duration

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _color(name: str) -> Color:
    return Color.from_name(name)


def _duration(s: str) -> Duration:
    return Duration.from_string(s)


# ---------------------------------------------------------------------------
# Topic + Layout composition
# ---------------------------------------------------------------------------


def test_topic_with_full_layout():
    bg = BackgroundStyle(type="solid", color=_color("blue"))
    border = BorderStyle(type="solid", width="2px", color=_color("black"))
    icon = IconStyle(type="emoji", value="📚")
    layout = Layout(id="school_theme", background=bg, border=border, icon=icon)
    topic = Topic(
        id="school",
        name="School",
        tags=["education"],
        layout=layout,
    )
    assert isinstance(topic.layout, Layout)
    assert topic.layout.background.type == "solid"  # type: ignore[union-attr]
    assert topic.layout.icon.value == "📚"  # type: ignore[union-attr]


def test_topic_layout_string_reference():
    topic = Topic(id="art", name="Art", layout="creative_theme")
    assert isinstance(topic.layout, str)
    assert topic.layout == "creative_theme"


# ---------------------------------------------------------------------------
# Event + SingleDaySchedule
# ---------------------------------------------------------------------------


def test_event_with_single_day_schedule():
    schedule = SingleDaySchedule(
        day=datetime.date(2026, 6, 15),
        start_time=datetime.time(9, 0),
        duration=_duration("2h"),
    )
    event = Event(
        id="final_exam",
        topic_id="math",
        name="Final Exam",
        schedules=[schedule],
        blocking_level=3,
    )
    assert event.schedules[0].day == datetime.date(2026, 6, 15)
    assert event.blocking_level == 3


def test_event_with_weekly_schedule():
    appt = WeeklyAppointment(
        week_day=Weekday.TUESDAY,
        start_time=datetime.time(10),
        duration=_duration("1h30m"),
    )
    schedule = WeeklySchedule(
        appointments=[appt],
        start_date=datetime.date(2026, 9, 1),
        end_date=datetime.date(2027, 1, 31),
    )
    event = Event(id="lecture", topic_id="physics", name="Physics Lecture", schedules=[schedule])
    ws = event.schedules[0]
    assert isinstance(ws, WeeklySchedule)
    assert ws.appointments[0].week_day == Weekday.TUESDAY


def test_event_with_multi_day_schedule():
    schedule = MultiDaySchedule(
        start_day=datetime.date(2026, 8, 10),
        end_day=datetime.date(2026, 8, 14),
    )
    event = Event(id="conf", topic_id="work", name="Tech Conference", schedules=[schedule])
    ms = event.schedules[0]
    assert isinstance(ms, MultiDaySchedule)
    assert (ms.end_day - ms.start_day).days == 4


# ---------------------------------------------------------------------------
# Task + EventLink + BlockedBy composition
# ---------------------------------------------------------------------------


def test_task_linked_to_event():
    link = EventLink(event_id="final_exam", use_as_deadline=True, as_context=True)
    effort = EffortRange(min=_duration("2h"), max=_duration("4h"))
    task = Task(
        id="study_ch3",
        topic_id="math",
        name="Study Chapter 3",
        deadline=datetime.date(2026, 6, 10),
        priority=3,
        effort=effort,
        event_links=[link],
    )
    assert task.event_links[0].event_id == "final_exam"
    assert task.effort.min == _duration("2h")  # type: ignore[union-attr]


def test_task_dependency_chain():
    bb1 = BlockedBy(task_id="study_ch1")
    bb2 = BlockedBy(task_id="study_ch2", description="Chapter 2 prereq")
    task = Task(
        id="study_ch3",
        name="Study Chapter 3",
        blocked_by=[bb1, bb2],
        status=TaskStatus.BLOCKED,
    )
    assert len(task.blocked_by) == 2
    assert task.blocked_by[1].description == "Chapter 2 prereq"
    assert task.status == TaskStatus.BLOCKED


def test_task_with_recurring_schedule():
    appt = WeeklyAppointment(
        week_day=Weekday.FRIDAY,
        start_time=datetime.time(16),
        duration=_duration("30m"),
    )
    ws = WeeklySchedule(appointments=[appt])
    task = Task(id="weekly_review", topic_id="work", name="Weekly Review", schedules=[ws])
    assert isinstance(task.schedules[0], WeeklySchedule)
    assert task.deadline is None


# ---------------------------------------------------------------------------
# Topic → Event → Task hierarchy (simulated config)
# ---------------------------------------------------------------------------


def test_full_topic_event_task_composition():
    topic = Topic(
        id="math",
        name="Mathematics",
        tags=["school"],
        layout=Layout(icon=IconStyle(type="emoji", value="📐")),
    )

    exam_schedule = SingleDaySchedule(
        day=datetime.date(2026, 6, 15),
        start_time=datetime.time(9),
        duration=_duration("2h"),
    )
    event = Event(
        id="math_exam",
        topic_id=topic.id,
        name="Mathematics Final Exam",
        schedules=[exam_schedule],
        blocking_level=2,
    )

    link = EventLink(event_id=event.id, use_as_deadline=True)
    blocked = BlockedBy(task_id="study_ch2")
    effort = EffortRange(_duration("1h"), _duration("3h"))
    task = Task(
        id="study_ch3",
        topic_id=topic.id,
        name="Study Chapter 3",
        deadline=datetime.date(2026, 6, 10),
        priority=2,
        effort=effort,
        event_links=[link],
        blocked_by=[blocked],
    )

    assert task.topic_id == topic.id
    assert task.event_links[0].event_id == event.id
    assert event.topic_id == topic.id


# ---------------------------------------------------------------------------
# Schedule polymorphism: list[Schedule] accepts all subtypes
# ---------------------------------------------------------------------------


def test_event_accepts_all_schedule_subtypes():
    schedules = [
        SingleDaySchedule(day=datetime.date(2026, 1, 1)),
        MultiDaySchedule(start_day=datetime.date(2026, 2, 1), end_day=datetime.date(2026, 2, 3)),
        WeeklySchedule(
            appointments=[
                WeeklyAppointment(
                    week_day=Weekday.MONDAY,
                    start_time=datetime.time(9),
                    duration=_duration("1h"),
                )
            ]
        ),
        MonthlySchedule(
            day_of_month=15,
            start_time=datetime.time(10),
            duration=_duration("1h"),
        ),
        YearlySchedule(month=12, day=25),
    ]
    event = Event(id="multi", topic_id="t", name="Multi-schedule", schedules=schedules)
    assert len(event.schedules) == 5


# ---------------------------------------------------------------------------
# Immutability across the graph
# ---------------------------------------------------------------------------


def test_event_schedules_list_is_frozen_via_dataclass():
    s = SingleDaySchedule(day=datetime.date(2026, 1, 1))
    e = Event(id="e", topic_id="t", name="N", schedules=[s])
    with pytest.raises((AttributeError, TypeError)):
        e.schedules = []  # type: ignore[misc]


def test_task_event_links_list_is_frozen_via_dataclass():
    t = Task(id="t", name="N", event_links=[EventLink(event_id="e1")])
    with pytest.raises((AttributeError, TypeError)):
        t.event_links = []  # type: ignore[misc]


# ---------------------------------------------------------------------------
# utilizing ↔ coring cross-module integration
# ---------------------------------------------------------------------------


def test_color_used_in_layout_used_in_topic():
    red = Color.from_hex("#ff0000")
    bg = BackgroundStyle(type="solid", color=red)
    layout = Layout(background=bg)
    topic = Topic(id="danger", name="Danger Zone", layout=layout)
    assert isinstance(topic.layout, Layout)
    assert topic.layout.background.color.r == pytest.approx(1.0)  # type: ignore[union-attr]


def test_duration_used_in_effort_used_in_task():
    min_d = Duration.from_string("30m")
    max_d = Duration.from_string("2h")
    effort = EffortRange(min=min_d, max=max_d)
    task = Task(id="t", name="N", effort=effort)
    assert task.effort.max.to_hours() == pytest.approx(2.0)  # type: ignore[union-attr]


def test_duration_used_in_weekly_appointment_in_event():
    appt = WeeklyAppointment(
        week_day=Weekday.WEDNESDAY,
        start_time=datetime.time(14),
        duration=Duration.from_string("45m"),
    )
    ws = WeeklySchedule(appointments=[appt])
    e = Event(id="e", topic_id="t", name="N", schedules=[ws])
    stored_duration = e.schedules[0].appointments[0].duration  # type: ignore[union-attr]
    assert stored_duration == Duration.from_string("45m")
