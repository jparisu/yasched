"""Tests for DatabaseParser: raw dict → coring objects."""

from __future__ import annotations

import datetime

import pytest

from yasched.backending.loading.DatabaseLoader import DatabaseParseError
from yasched.backending.loading.DatabaseParser import DatabaseParser
from yasched.coring._shared import TaskStatus, Weekday
from yasched.coring.Layout import Layout
from yasched.coring.MonthlySchedule import MonthlySchedule
from yasched.coring.MultiDaySchedule import MultiDaySchedule
from yasched.coring.SingleDaySchedule import SingleDaySchedule
from yasched.coring.WeeklySchedule import WeeklySchedule
from yasched.coring.YearlySchedule import YearlySchedule

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(raw: dict):
    return DatabaseParser.parse(raw)


# ---------------------------------------------------------------------------
# Top-level structure
# ---------------------------------------------------------------------------


def test_parse_empty_dict_returns_empty_database():
    db = _parse({})
    assert db.layouts == []
    assert db.topics == []
    assert db.events == []
    assert db.tasks == []


def test_parse_unknown_top_key_raises():
    with pytest.raises(DatabaseParseError):
        _parse({"unknown_key": []})


def test_parse_source_path_stored():
    from pathlib import Path

    db = DatabaseParser.parse({}, source_path=Path("/some/file.yaml"))
    assert db.source_path == Path("/some/file.yaml")


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------


def test_parse_topic_minimal():
    db = _parse({"topics": [{"id": "t1", "name": "Topic One"}]})
    assert len(db.topics) == 1
    t = db.topics[0]
    assert t.id == "t1"
    assert t.name == "Topic One"
    assert t.description is None
    assert t.tags == []
    assert t.parent_ids == []
    assert t.layout is None


def test_parse_topic_full():
    db = _parse(
        {
            "topics": [
                {
                    "id": "t1",
                    "name": "Topic One",
                    "description": "desc",
                    "tags": ["a", "b"],
                    "parents": ["p1", "p2"],
                }
            ]
        }
    )
    t = db.topics[0]
    assert t.description == "desc"
    assert t.tags == ["a", "b"]
    assert t.parent_ids == ["p1", "p2"]


def test_parse_topic_layout_string_ref():
    db = _parse({"topics": [{"id": "t1", "name": "N", "layout": "my_theme"}]})
    assert db.topics[0].layout == "my_theme"


def test_parse_topic_layout_inline():
    db = _parse(
        {
            "topics": [
                {
                    "id": "t1",
                    "name": "N",
                    "layout": {"background": {"type": "solid", "color": "blue"}},
                }
            ]
        }
    )
    assert isinstance(db.topics[0].layout, Layout)


def test_parse_multiple_topics():
    db = _parse({"topics": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]})
    assert len(db.topics) == 2


# ---------------------------------------------------------------------------
# Layouts
# ---------------------------------------------------------------------------


def test_parse_layout_named():
    db = _parse({"layouts": [{"id": "blue_theme"}]})
    assert len(db.layouts) == 1
    assert db.layouts[0].id == "blue_theme"


def test_parse_layout_with_background_solid():
    from yasched.coring.Layout import SolidBackground

    db = _parse({"layouts": [{"id": "l1", "background": {"type": "solid", "color": "red"}}]})
    layout = db.layouts[0]
    assert len(layout.backgrounds) == 1
    assert isinstance(layout.backgrounds[0], SolidBackground)
    assert layout.backgrounds[0].color is not None


def test_parse_layout_with_background_gradient_tr():
    from yasched.coring.Layout import GradientTopRightBackground

    db = _parse(
        {
            "layouts": [
                {
                    "id": "l1",
                    "background": {"type": "gradient_tr", "color": "red"},
                }
            ]
        }
    )
    layout = db.layouts[0]
    assert len(layout.backgrounds) == 1
    assert isinstance(layout.backgrounds[0], GradientTopRightBackground)


def test_parse_layout_with_two_gradient_layers():
    from yasched.coring.Layout import GradientBottomLeftBackground, GradientTopRightBackground

    db = _parse(
        {
            "layouts": [
                {
                    "id": "l1",
                    "background": [
                        {"type": "gradient_tr", "color": "red"},
                        {"type": "gradient_bl", "color": "blue"},
                    ],
                }
            ]
        }
    )
    layout = db.layouts[0]
    assert len(layout.backgrounds) == 2
    assert isinstance(layout.backgrounds[0], GradientTopRightBackground)
    assert isinstance(layout.backgrounds[1], GradientBottomLeftBackground)


def test_parse_layout_with_border():
    db = _parse(
        {
            "layouts": [
                {
                    "id": "l1",
                    "border": {"type": "solid", "width": "2px", "color": "black"},
                }
            ]
        }
    )
    assert db.layouts[0].border is not None
    assert db.layouts[0].border.width == "2px"


def test_parse_layout_with_icon_emoji():
    db = _parse({"layouts": [{"id": "l1", "icon": {"type": "emoji", "value": "⚠️"}}]})
    assert db.layouts[0].icon.value == "⚠️"


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


def test_parse_event_minimal_single_day():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "Event One",
                    "schedule": {"day": datetime.date(2026, 1, 15)},
                }
            ]
        }
    )
    assert len(db.events) == 1
    e = db.events[0]
    assert e.id == "e1"
    assert e.topic_id == "t1"
    assert len(e.schedules) == 1
    assert isinstance(e.schedules[0], SingleDaySchedule)


def test_parse_event_full_fields():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "Event One",
                    "description": "desc",
                    "location": "Room 101",
                    "blocking_level": 2,
                    "schedule": {"day": datetime.date(2026, 1, 15)},
                }
            ]
        }
    )
    e = db.events[0]
    assert e.description == "desc"
    assert e.location == "Room 101"
    assert e.blocking_level == 2


def test_parse_event_multi_day_schedule():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "N",
                    "schedule": {
                        "start_day": datetime.date(2026, 1, 1),
                        "end_day": datetime.date(2026, 1, 5),
                    },
                }
            ]
        }
    )
    assert isinstance(db.events[0].schedules[0], MultiDaySchedule)


def test_parse_event_weekly_schedule_shorthand():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "N",
                    "schedule": {
                        "type": "weekly",
                        "week_days": ["monday", "wednesday"],
                        "start_time": "10:00",
                        "duration": "1h",
                    },
                }
            ]
        }
    )
    ws = db.events[0].schedules[0]
    assert isinstance(ws, WeeklySchedule)
    assert len(ws.appointments) == 2
    assert ws.appointments[0].week_day == Weekday.MONDAY
    assert ws.appointments[1].week_day == Weekday.WEDNESDAY


def test_parse_event_weekly_schedule_explicit_appointments():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "N",
                    "schedule": {
                        "type": "weekly",
                        "appointments": [
                            {"week_day": "tuesday", "start_time": "14:00", "duration": "1h"},
                            {"week_day": "thursday", "start_time": "14:00", "end_time": "15:30"},
                        ],
                    },
                }
            ]
        }
    )
    ws = db.events[0].schedules[0]
    assert len(ws.appointments) == 2
    assert ws.appointments[0].week_day == Weekday.TUESDAY
    assert ws.appointments[1].end_time == datetime.time(15, 30)


def test_parse_event_monthly_schedule():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "N",
                    "schedule": {
                        "type": "monthly",
                        "day_of_month": 1,
                        "start_time": "10:00",
                        "duration": "30m",
                    },
                }
            ]
        }
    )
    assert isinstance(db.events[0].schedules[0], MonthlySchedule)
    assert db.events[0].schedules[0].day_of_month == 1


def test_parse_event_yearly_schedule():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "N",
                    "schedule": {"type": "yearly", "month": 12, "day": 25},
                }
            ]
        }
    )
    assert isinstance(db.events[0].schedules[0], YearlySchedule)
    assert db.events[0].schedules[0].month == 12


def test_parse_event_schedule_list():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "N",
                    "schedule": [
                        {"day": datetime.date(2026, 1, 1)},
                        {"day": datetime.date(2026, 2, 1)},
                    ],
                }
            ]
        }
    )
    assert len(db.events[0].schedules) == 2


def test_parse_event_weekly_schedule_with_dates():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t1",
                    "name": "N",
                    "schedule": {
                        "type": "weekly",
                        "week_days": ["friday"],
                        "start_time": "15:00",
                        "duration": "30m",
                        "start_date": datetime.date(2026, 1, 1),
                        "end_date": datetime.date(2026, 6, 30),
                    },
                }
            ]
        }
    )
    ws = db.events[0].schedules[0]
    assert ws.start_date == datetime.date(2026, 1, 1)
    assert ws.end_date == datetime.date(2026, 6, 30)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


def test_parse_task_minimal():
    db = _parse({"tasks": [{"id": "t1", "name": "Task One", "topics": "my_topic"}]})
    task = db.tasks[0]
    assert task.id == "t1"
    assert task.name == "Task One"
    assert task.topic_ids == ["my_topic"]
    assert task.status == TaskStatus.TODO


def test_parse_task_full_fields():
    db = _parse(
        {
            "tasks": [
                {
                    "id": "t1",
                    "name": "Task One",
                    "topics": "tp",
                    "description": "desc",
                    "tags": ["x"],
                    "deadline": datetime.date(2026, 12, 24),
                    "priority": 5,
                    "status": "in_progress",
                    "effort": {"min": "2h", "max": "4h"},
                }
            ]
        }
    )
    task = db.tasks[0]
    assert task.deadline == datetime.date(2026, 12, 24)
    assert task.priority == 5
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.effort is not None
    assert task.effort.min.to_hours() == pytest.approx(2.0)


def test_parse_task_with_parent():
    db = _parse(
        {
            "tasks": [
                {
                    "id": "sub",
                    "name": "Sub",
                    "parent": "parent_task",
                }
            ]
        }
    )
    assert db.tasks[0].parent_id == "parent_task"
    assert db.tasks[0].topic_ids == []


def test_parse_task_event_link_shorthand():
    db = _parse(
        {
            "tasks": [
                {
                    "id": "t1",
                    "name": "N",
                    "topics": "tp",
                    "events": ["event_id"],
                }
            ]
        }
    )
    links = db.tasks[0].event_links
    assert len(links) == 1
    assert links[0].event_id == "event_id"
    assert links[0].use_as_deadline is True
    assert links[0].as_context is True


def test_parse_task_event_link_structured():
    db = _parse(
        {
            "tasks": [
                {
                    "id": "t1",
                    "name": "N",
                    "topics": "tp",
                    "events": [{"id": "ev", "use_as_deadline": False, "as_context": True}],
                }
            ]
        }
    )
    link = db.tasks[0].event_links[0]
    assert link.event_id == "ev"
    assert link.use_as_deadline is False


def test_parse_task_relations():
    from yasched.coring._shared import RelationType

    db = _parse(
        {
            "tasks": [
                {
                    "id": "t1",
                    "name": "N",
                    "topics": "tp",
                    "relations": [
                        {"task": "other_task", "type": "requires", "description": "reason"}
                    ],
                }
            ]
        }
    )
    rels = db.tasks[0].relations
    assert len(rels) == 1
    assert rels[0].task_id == "other_task"
    assert rels[0].type == RelationType.REQUIRES
    assert rels[0].description == "reason"


def test_parse_task_relation_no_description():
    db = _parse(
        {
            "tasks": [
                {
                    "id": "t1",
                    "name": "N",
                    "topics": "tp",
                    "relations": [{"task": "other", "type": "needs"}],
                }
            ]
        }
    )
    assert db.tasks[0].relations[0].description is None


def test_parse_task_relation_shorthand_string():
    from yasched.coring._shared import RelationType

    db = _parse({"tasks": [{"id": "t1", "name": "N", "relations": ["other_task"]}]})
    rel = db.tasks[0].relations[0]
    assert rel.task_id == "other_task"
    assert rel.type == RelationType.CONNECTED


def test_parse_task_multiple_topics():
    db = _parse({"tasks": [{"id": "t1", "name": "N", "topics": ["work", "personal"]}]})
    assert db.tasks[0].topic_ids == ["work", "personal"]


def test_parse_task_recurring_schedule():
    db = _parse(
        {
            "tasks": [
                {
                    "id": "t1",
                    "name": "N",
                    "topics": "tp",
                    "schedule": {
                        "type": "weekly",
                        "week_days": ["monday"],
                        "start_time": "09:00",
                        "duration": "1h",
                    },
                }
            ]
        }
    )
    assert len(db.tasks[0].schedules) == 1
    assert isinstance(db.tasks[0].schedules[0], WeeklySchedule)


def test_parse_task_status_done():
    db = _parse({"tasks": [{"id": "t", "name": "N", "topics": "tp", "status": "done"}]})
    assert db.tasks[0].status == TaskStatus.DONE


def test_parse_task_status_cancelled():
    db = _parse({"tasks": [{"id": "t", "name": "N", "topics": "tp", "status": "cancelled"}]})
    assert db.tasks[0].status == TaskStatus.CANCELLED


# ---------------------------------------------------------------------------
# Time parsing from various YAML representations
# ---------------------------------------------------------------------------


def test_parse_time_from_string():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t",
                    "name": "N",
                    "schedule": {
                        "type": "weekly",
                        "week_days": ["monday"],
                        "start_time": "14:30",
                        "duration": "1h",
                    },
                }
            ]
        }
    )
    appt = db.events[0].schedules[0].appointments[0]
    assert appt.start_time == datetime.time(14, 30)


def test_parse_time_from_yaml_sexagesimal():
    # YAML parses 14:30 as int 870 in some loaders
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t",
                    "name": "N",
                    "schedule": {
                        "type": "weekly",
                        "week_days": ["monday"],
                        "start_time": 870,
                        "duration": "1h",
                    },
                }
            ]
        }
    )
    appt = db.events[0].schedules[0].appointments[0]
    assert appt.start_time == datetime.time(14, 30)


def test_parse_time_from_datetime_time():
    db = _parse(
        {
            "events": [
                {
                    "id": "e1",
                    "topic": "t",
                    "name": "N",
                    "schedule": {
                        "type": "weekly",
                        "week_days": ["monday"],
                        "start_time": datetime.time(9, 0),
                        "duration": "1h",
                    },
                }
            ]
        }
    )
    appt = db.events[0].schedules[0].appointments[0]
    assert appt.start_time == datetime.time(9, 0)


# ---------------------------------------------------------------------------
# Color parsing
# ---------------------------------------------------------------------------


def test_parse_color_name():
    from yasched.coring.Layout import SolidBackground

    db = _parse({"layouts": [{"id": "l1", "background": {"type": "solid", "color": "blue"}}]})
    assert isinstance(db.layouts[0].backgrounds[0], SolidBackground)
    assert db.layouts[0].backgrounds[0].color is not None


def test_parse_color_hex():
    from yasched.coring.Layout import SolidBackground

    db = _parse({"layouts": [{"id": "l1", "background": {"type": "solid", "color": "#ff0000"}}]})
    assert isinstance(db.layouts[0].backgrounds[0], SolidBackground)
    assert db.layouts[0].backgrounds[0].color is not None


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_parse_topic_missing_id_raises():
    with pytest.raises(DatabaseParseError):
        _parse({"topics": [{"name": "No ID"}]})


def test_parse_topic_missing_name_raises():
    with pytest.raises(DatabaseParseError):
        _parse({"topics": [{"id": "t1"}]})


def test_parse_event_missing_topic_raises():
    with pytest.raises(DatabaseParseError):
        _parse(
            {"events": [{"id": "e1", "name": "N", "schedule": {"day": datetime.date(2026, 1, 1)}}]}
        )


def test_parse_event_missing_schedule_raises():
    with pytest.raises(DatabaseParseError):
        _parse({"events": [{"id": "e1", "topic": "t", "name": "N"}]})


def test_parse_task_missing_name_raises():
    with pytest.raises(DatabaseParseError):
        _parse({"tasks": [{"id": "t1", "topics": "tp"}]})


def test_parse_unknown_schedule_type_raises():
    with pytest.raises(DatabaseParseError):
        _parse(
            {
                "events": [
                    {
                        "id": "e1",
                        "topic": "t",
                        "name": "N",
                        "schedule": {"type": "unknown_type"},
                    }
                ]
            }
        )
