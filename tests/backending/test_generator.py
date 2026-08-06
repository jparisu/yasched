"""Tests for the auto-element generator."""

import datetime

from yasched.backending.generating.Generator import Generator
from yasched.backending.loading.ElementLoader import ElementLoader
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType

JAN = (datetime.date(2026, 1, 1), datetime.date(2026, 1, 31))


def _gen(doc, window=JAN):
    db = ElementLoader.from_dict(doc)
    return db, {e.id: e for e in Generator(db).generate(*window)}


def test_weekly_schedule_generates_events():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "lec",
                "type": "schedule",
                "attributes": {
                    "generates": "event",
                    "kind": "weekly",
                    "weekDays": ["mon", "wed"],
                    "startDate": "2026-01-05",
                    "endDate": "2026-01-16",
                    "time": "10:00",
                    "duration": "1h",
                },
            },
        ]
    }
    _, byid = _gen(doc)
    assert set(byid) == {"lec#2026-01-05", "lec#2026-01-07", "lec#2026-01-12", "lec#2026-01-14"}
    one = byid["lec#2026-01-05"]
    assert one.attributes["start"] == "2026-01-05T10:00"
    assert one.virtual is True
    assert one.direct_parents == ["lec"]
    assert one.type is ElementType.EVENT


def test_daily_schedule_all_day():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "d",
                "type": "schedule",
                "attributes": {
                    "generates": "event",
                    "kind": "daily",
                    "startDate": "2026-01-01",
                    "endDate": "2026-01-03",
                },
            },
        ]
    }
    _, byid = _gen(doc)
    assert set(byid) == {"d#2026-01-01", "d#2026-01-02", "d#2026-01-03"}
    assert byid["d#2026-01-01"].attributes["start"] == "2026-01-01"  # no time -> all-day


def test_monthly_clamps_to_month_end():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "r",
                "type": "schedule",
                "attributes": {"generates": "task", "kind": "monthly", "monthDays": [31]},
            },
        ]
    }
    _, byid = _gen(doc, (datetime.date(2026, 2, 1), datetime.date(2026, 2, 28)))
    assert "r#2026-02-28" in byid


def test_yearly_schedule():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "bday",
                "type": "schedule",
                "attributes": {
                    "generates": "event",
                    "kind": "yearly",
                    "yearlyDays": [{"month": 1, "day": 15}],
                },
            },
        ]
    }
    _, byid = _gen(doc)
    assert set(byid) == {"bday#2026-01-15"}


def test_deadline_and_reminder_events():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "g",
                "type": "task",
                "attributes": {"name": "G", "deadline": "2026-01-20", "reminders": ["1d", "2h"]},
            },
        ]
    }
    _, byid = _gen(doc)
    assert byid["g#deadline"].attributes["class"] == "deadline"
    assert byid["g#reminder-1d"].attributes["start"].startswith("2026-01-19")
    assert "g#reminder-2h" in byid


def test_promotion_suppresses_virtual():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "lec",
                "type": "schedule",
                "attributes": {
                    "generates": "event",
                    "kind": "daily",
                    "startDate": "2026-01-01",
                    "endDate": "2026-01-02",
                },
            },
            {
                "id": "lec#2026-01-01",
                "type": "event",
                "directParents": ["lec"],
                "attributes": {"cancelled": True},
            },
        ]
    }
    _, byid = _gen(doc)
    # The real (promoted) element wins; the generator must not re-emit that id.
    assert "lec#2026-01-01" not in byid
    assert "lec#2026-01-02" in byid


def test_window_bounds_are_inclusive_and_limiting():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {"id": "d", "type": "schedule", "attributes": {"generates": "event", "kind": "daily"}},
        ]
    }
    _, byid = _gen(doc, (datetime.date(2026, 1, 10), datetime.date(2026, 1, 11)))
    assert set(byid) == {"d#2026-01-10", "d#2026-01-11"}


def test_deadline_reminder_events_do_not_cascade():
    # A generated deadline/reminder event must not itself spawn more auto-elements.
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {"id": "g", "type": "task", "attributes": {"deadline": "2026-01-20"}},
        ]
    }
    db, byid = _gen(doc)
    # only the single deadline event, nothing like g#deadline#deadline
    assert not any("#deadline#" in i for i in byid)
    assert isinstance(db.element("g"), Element)
