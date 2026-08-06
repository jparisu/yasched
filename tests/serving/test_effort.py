"""Tests for the period-scoped effort aggregation."""

import datetime

from yasched.serving.views import build_effort

FALL = (datetime.date(2026, 9, 1), datetime.date(2026, 12, 31))


def test_effort_rolls_task_time_by_deadline(example_db):
    effort = build_effort(example_db, *FALL)["topics"]
    # research tasks in the window: write-paper 6h + intro 4h + experiments 3h30m = 810 min
    assert effort["research"]["ownTasks"] == 6 * 60 + 4 * 60 + 3 * 60 + 30
    assert effort["research"]["rolledTasks"] == effort["research"]["ownTasks"]


def test_effort_counts_event_time_for_teaching(example_db):
    effort = build_effort(example_db, *FALL)["topics"]
    # math-101 lectures + office hours produce many hours of event time under teaching
    assert effort["teaching"]["rolledEvents"] > 0
    assert effort["AllTopic"]["rolledEvents"] >= effort["teaching"]["rolledEvents"]


def test_effort_period_excludes_out_of_range_dates(example_db):
    # A one-day window before any data → nothing counts.
    empty = build_effort(example_db, datetime.date(2000, 1, 1), datetime.date(2000, 1, 2))["topics"]
    assert all(v["rolledEvents"] == 0 and v["rolledTasks"] == 0 for v in empty.values())


def test_effort_defaults_end_to_today(example_db):
    out = build_effort(example_db)
    assert out["window"]["end"] == datetime.date.today().isoformat()
